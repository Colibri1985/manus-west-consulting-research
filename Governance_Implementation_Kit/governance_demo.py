"""Local governance demonstrator; not a security sandbox."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def compile_rules(baseline, overlay, project, role):
    effective = {}
    selected = []
    for rules, layer in ((baseline, "global"), (overlay, "project")):
        for rule in rules:
            required = {"id", "revision", "status", "effect", "operation", "resource", "text"}
            if not required <= rule.keys():
                raise ValueError("Missing required fields")
            if rule["status"] != "approved":
                raise ValueError("Only approved rules may enter a bundle")
            if rule["effect"] not in {"allow", "deny", "require"}:
                raise ValueError("Unknown effect")
            if layer == "project" and rule.get("project") != project:
                raise ValueError("Wrong project")
            if rule.get("roles") and role not in rule["roles"]:
                continue
            key = (rule["operation"], rule["resource"])
            old = effective.get(key)
            if old and old["effect"] == "deny" and rule["effect"] != "deny":
                raise ValueError("Cannot weaken an existing deny")
            if old and old["effect"] == "require" and rule["effect"] != "require":
                raise ValueError("Requirement conflict requires review")
            effective[key] = rule
            selected.append(dict(rule, layer=layer))
    return {"schema_version": "1.0", "project": project, "role": role, "rules": selected}


def publish_bundle(root, bundle):
    payload = canonical(bundle)
    digest = hashlib.sha256(payload).hexdigest()
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    target = root / digest
    if target.exists():
        if (target / "manifest.json").read_bytes() != payload:
            raise ValueError("Existing bundle differs")
        return target
    with tempfile.TemporaryDirectory(dir=root) as tmp:
        staging = Path(tmp)
        (staging / "manifest.json").write_bytes(payload)
        text = "# Effective rules\n\n" + "\n".join(
            f"- [{r['id']} r{r['revision']}] {r['text']}" for r in bundle["rules"]
        )
        (staging / "rules.md").write_text(text, encoding="utf-8")
        config = {"$schema": "https://opencode.ai/config.json", "instructions": ["rules.md"]}
        (staging / "opencode.json").write_text(json.dumps(config, indent=2), encoding="utf-8")
        staging.rename(target)
    return target


def rule(**changes):
    value = {"id": "GLOBAL.NO_DELETE", "revision": 1, "status": "approved",
             "effect": "deny", "operation": "delete", "resource": "workspace",
             "text": "Не удалять workspace без отдельного решения."}
    value.update(changes)
    return value


class GovernanceTests(unittest.TestCase):
    def test_rejects_proposed(self):
        with self.assertRaises(ValueError):
            compile_rules([rule()], [rule(id="P1", project="p", status="proposed")], "p", "developer")

    def test_rejects_weakened_deny(self):
        with self.assertRaises(ValueError):
            compile_rules([rule()], [rule(id="P2", project="p", effect="allow")], "p", "developer")

    def test_rejects_wrong_project(self):
        with self.assertRaises(ValueError):
            compile_rules([rule()], [rule(project="other")], "p", "developer")

    def test_role_filter(self):
        bundle = compile_rules([rule(roles=["qa"])], [], "p", "developer")
        self.assertEqual(bundle["rules"], [])

    def test_deterministic_publish(self):
        bundle = compile_rules([rule()], [], "p", "developer")
        with tempfile.TemporaryDirectory() as root:
            a = publish_bundle(root, bundle)
            b = publish_bundle(root, bundle)
            self.assertEqual(a, b)
            self.assertIn("GLOBAL.NO_DELETE", (a / "rules.md").read_text())

    def test_new_revision_has_new_bundle(self):
        with tempfile.TemporaryDirectory() as root:
            a = publish_bundle(root, compile_rules([rule()], [], "p", "developer"))
            b = publish_bundle(root, compile_rules([rule(revision=2)], [], "p", "developer"))
            self.assertNotEqual(a, b)
            self.assertTrue(a.exists())


if __name__ == "__main__":
    unittest.main()
