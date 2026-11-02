#!/usr/bin/env python3
"""Офлайн-тесты athena-github-token против поддельного GitHub на 127.0.0.1.
Настоящий GitHub, настоящий ключ и настоящий токен не используются."""
import base64
import contextlib
import importlib.machinery
import importlib.util
import io
import json
import os
import shutil
import subprocess
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
_loader = importlib.machinery.SourceFileLoader("agt", os.path.join(HERE, "athena-github-token"))
_spec = importlib.util.spec_from_loader("agt", _loader)
m = importlib.util.module_from_spec(_spec)
_loader.exec_module(m)

FAKE_TOKEN = "ghs_" + "A1b2C3d4" * 5
GOOD_PERMS = dict(m.READ_PERMISSIONS)


class Fake(BaseHTTPRequestHandler):
    scenario = {}
    log = []
    token_path = ""
    token_present_at_delete = None

    def log_message(self, *a):
        pass

    def _send(self, code, obj=None):
        body = json.dumps(obj).encode() if obj is not None else b""
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _rec(self, body=None):
        Fake.log.append((self.command, self.path, self.headers.get("Authorization", ""), body))

    def do_GET(self):
        self._rec()
        s = Fake.scenario
        if self.path == "/app":
            return self._send(200, {"slug": s["slug"], "id": 5570755})
        if self.path == "/repos/Colibri1985/Athena/installation":
            return self._send(200, {"id": 42, "repository_selection": s["selection"],
                                    "account": {"login": "Colibri1985"}, "suspended_at": None})
        self._send(404, {"message": "not found"})

    def do_POST(self):
        n = int(self.headers.get("Content-Length", "0"))
        body = json.loads(self.rfile.read(n) or b"{}")
        self._rec(body)
        s = Fake.scenario
        if self.path == "/app/installations/42/access_tokens":
            return self._send(201, {
                "token": FAKE_TOKEN, "expires_at": "2026-11-02T00:00:00Z",
                "repository_selection": "selected", "permissions": s["perms"],
                "repositories": [{"name": x} for x in s["repos"]]})
        self._send(404, {"message": "not found"})

    def do_DELETE(self):
        self._rec()
        Fake.token_present_at_delete = os.path.exists(Fake.token_path)
        code = Fake.scenario.get("delete_status", 204)
        if code == 204:
            self._send(204)
        elif code == 401:
            self._send(401, {"message": "Bad credentials"})
        else:
            self._send(code, {"message": "server error"})


def run_main(argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = m.main(argv)
    return code, out.getvalue(), err.getvalue()


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srv = HTTPServer(("127.0.0.1", 0), Fake)
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="agt-test-")
        self.key_dir = os.path.join(self.tmp, "key")
        self.tok_dir = os.path.join(self.tmp, "tok")
        os.mkdir(self.key_dir)
        os.chmod(self.key_dir, 0o700)
        os.mkdir(self.tok_dir)
        os.chmod(self.tok_dir, 0o750)
        self.key = os.path.join(self.key_dir, "k.pem")
        subprocess.run(["openssl", "genrsa", "-out", self.key, "2048"], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        os.chmod(self.key, 0o600)
        m.STRICT = False
        m.KEY_DIR, m.KEY_PATH = self.key_dir, self.key
        m.ALLOWED_TOKEN_DIRS = (self.tok_dir,)
        m.TOKEN_DIR = self.tok_dir
        m.TOKEN_GID = os.getgid()
        m.API_BASE = "http://127.0.0.1:%d" % self.srv.server_address[1]
        Fake.log = []
        Fake.token_path = os.path.join(self.tok_dir, "token")
        Fake.token_present_at_delete = None
        Fake.scenario = {"slug": "athena-colibri1985", "selection": "selected",
                         "repos": ["Athena"], "perms": dict(GOOD_PERMS)}

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)


class TestJwt(Base):
    def test_signature_verifies_and_claims(self):
        jwt = m.make_jwt(self.key, now=1_800_000_000)
        h, p, s = jwt.split(".")
        pad = lambda x: x + "=" * (-len(x) % 4)
        payload = json.loads(base64.urlsafe_b64decode(pad(p)))
        self.assertEqual(payload["iss"], 5570755)
        self.assertEqual(payload["exp"] - 1_800_000_000, 540)
        self.assertLessEqual(payload["exp"] - payload["iat"], 600)
        pub = os.path.join(self.tmp, "pub.pem")
        subprocess.run(["openssl", "rsa", "-in", self.key, "-pubout", "-out", pub], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        sig = os.path.join(self.tmp, "sig.bin")
        with open(sig, "wb") as f:
            f.write(base64.urlsafe_b64decode(pad(s)))
        good = subprocess.run(["openssl", "dgst", "-sha256", "-verify", pub, "-signature", sig],
                              input=(h + "." + p).encode(), capture_output=True)
        self.assertEqual(good.returncode, 0)
        bad = subprocess.run(["openssl", "dgst", "-sha256", "-verify", pub, "-signature", sig],
                             input=(h + "." + p + "x").encode(), capture_output=True)
        self.assertNotEqual(bad.returncode, 0)

    def test_dry_run_no_network_no_files(self):
        code, out, err = run_main(["read", "--dry-run", "--test-key", self.key])
        self.assertEqual(code, 0, err)
        self.assertEqual(Fake.log, [])
        self.assertEqual(os.listdir(self.tok_dir), [])

    def test_test_key_requires_dry_run(self):
        code, _, _ = run_main(["read", "--test-key", self.key])
        self.assertEqual(code, 1)
        self.assertEqual(Fake.log, [])


class TestIssue(Base):
    def test_success_files_modes_no_leak(self):
        code, out, err = run_main(["read"])
        self.assertEqual(code, 0, err)
        tp = os.path.join(self.tok_dir, "token")
        self.assertEqual(open(tp).read(), FAKE_TOKEN + "\n")
        self.assertEqual(os.stat(tp).st_mode & 0o777, 0o640)
        status = open(os.path.join(self.tok_dir, "status.json")).read()
        self.assertNotIn(FAKE_TOKEN, status)
        self.assertTrue(json.loads(status)["token_present"])
        keytext = open(self.key).read().splitlines()
        for text in (out, err):
            self.assertNotIn(FAKE_TOKEN, text)
            self.assertNotIn("BEGIN", text)
            for line in keytext[1:-1]:
                self.assertNotIn(line, text)
        post = [x for x in Fake.log if x[0] == "POST"][0]
        self.assertEqual(post[3], {"repositories": ["Athena"], "permissions": GOOD_PERMS})
        self.assertTrue(all(x[2].startswith("Bearer ") for x in Fake.log))
        self.assertEqual([f for f in os.listdir(self.tok_dir) if f.startswith(".")], [])

    def _expect_refused(self, expect_revoke):
        code, out, err = run_main(["read"])
        self.assertEqual(code, 1)
        self.assertFalse(os.path.exists(os.path.join(self.tok_dir, "token")))
        self.assertNotIn(FAKE_TOKEN, out + err)
        revoked = [x for x in Fake.log if x[0] == "DELETE"]
        self.assertEqual(bool(revoked), expect_revoke)
        if revoked:
            self.assertEqual(revoked[0][2], "Bearer " + FAKE_TOKEN)

    def test_extra_repo_refused_and_revoked(self):
        Fake.scenario["repos"] = ["Athena", "Other"]
        self._expect_refused(True)

    def test_write_permission_refused_and_revoked(self):
        Fake.scenario["perms"] = dict(GOOD_PERMS, contents="write")
        self._expect_refused(True)

    def test_extra_permission_refused_and_revoked(self):
        Fake.scenario["perms"] = dict(GOOD_PERMS, workflows="read")
        self._expect_refused(True)

    def test_wrong_slug_refused_before_token(self):
        Fake.scenario["slug"] = "someone-else"
        self._expect_refused(False)
        self.assertFalse([x for x in Fake.log if x[0] == "POST"])

    def test_installation_all_repos_refused_before_token(self):
        Fake.scenario["selection"] = "all"
        self._expect_refused(False)
        self.assertFalse([x for x in Fake.log if x[0] == "POST"])


class TestGuards(Base):
    def test_token_dir_wrong_mode_refused_without_network(self):
        os.chmod(self.tok_dir, 0o755)
        code, _, err = run_main(["read"])
        self.assertEqual(code, 1)
        self.assertEqual(Fake.log, [])

    def test_key_wrong_mode_refused_without_network(self):
        os.chmod(self.key, 0o644)
        code, _, err = run_main(["read"])
        self.assertEqual(code, 1)
        self.assertEqual(Fake.log, [])

    def test_token_dir_not_in_allowlist(self):
        code, _, err = run_main(["read", "--token-dir", "/tmp"])
        self.assertEqual(code, 1)
        self.assertEqual(Fake.log, [])

    def test_key_symlink_refused(self):
        link = os.path.join(self.key_dir, "link.pem")
        os.symlink(self.key, link)
        m.KEY_PATH = link
        code, _, _ = run_main(["read"])
        self.assertEqual(code, 1)
        self.assertEqual(Fake.log, [])


class TestOff(Base):
    def _issue(self):
        self.assertEqual(run_main(["read"])[0], 0)
        self.tp = os.path.join(self.tok_dir, "token")
        self.assertTrue(os.path.exists(self.tp))
        Fake.log = []

    def _status(self):
        return json.load(open(os.path.join(self.tok_dir, "status.json")))

    def test_off_revokes_before_deleting(self):
        self._issue()
        code, out, err = run_main(["off"])
        self.assertEqual(code, 0, err)
        deletes = [x for x in Fake.log if x[0] == "DELETE"]
        self.assertEqual(len(deletes), 1)
        self.assertEqual(deletes[0][2], "Bearer " + FAKE_TOKEN)
        self.assertTrue(Fake.token_present_at_delete)  # файл ещё существовал в момент отзыва
        self.assertFalse(os.path.lexists(self.tp))
        st = self._status()
        self.assertFalse(st["token_present"])
        self.assertEqual(st["revocation"], "revoked")
        self.assertNotIn(FAKE_TOKEN, out + err)

    def test_off_idempotent_without_file(self):
        self._issue()
        self.assertEqual(run_main(["off"])[0], 0)
        Fake.log = []
        code, out, _ = run_main(["off"])
        self.assertEqual(code, 0)
        self.assertIn("не было", out)
        self.assertEqual(Fake.log, [])

    def test_off_already_invalid_token_is_deleted(self):
        self._issue()
        Fake.scenario["delete_status"] = 401
        code, out, _ = run_main(["off"])
        self.assertEqual(code, 0)
        self.assertFalse(os.path.lexists(self.tp))
        self.assertEqual(self._status()["revocation"], "already_invalid")

    def test_off_keeps_file_when_revocation_unconfirmed(self):
        self._issue()
        Fake.scenario["delete_status"] = 500
        code, out, err = run_main(["off"])
        self.assertEqual(code, 1)
        self.assertTrue(os.path.exists(self.tp))
        self.assertNotIn(FAKE_TOKEN, out + err)
        code, out, err = run_main(["off", "--force-delete"])
        self.assertEqual(code, 0, err)
        self.assertFalse(os.path.lexists(self.tp))
        self.assertIn("unconfirmed", self._status()["revocation"])

    def test_off_refuses_non_token_content_without_force(self):
        self._issue()
        with open(self.tp, "w") as f:
            f.write("not a token\n")
        code, _, _ = run_main(["off"])
        self.assertEqual(code, 1)
        self.assertTrue(os.path.exists(self.tp))
        self.assertEqual([x for x in Fake.log if x[0] == "DELETE"], [])


class TestRedact(unittest.TestCase):
    def test_patterns(self):
        for s in (FAKE_TOKEN, "github_pat_" + "x" * 30, "eyJhbGciOiJSUzI1NiJ9.eyJpc3MiOjF9.abcdefgh",
                  "-----BEGIN RSA PRIVATE KEY-----\nAAAA\n-----END RSA PRIVATE KEY-----"):
            r = m.redact("до " + s + " после")
            self.assertIn("[REDACTED]", r)
            self.assertNotIn(s[:20], r)


if __name__ == "__main__":
    unittest.main(verbosity=2)
