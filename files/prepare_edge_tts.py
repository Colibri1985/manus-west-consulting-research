#!/usr/bin/env python3
"""Prepare and test a separate Edge TTS image. Never switches the gateway."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import urllib.request

ROOT = Path('/srv/hermes-agent/athena-tts')
CONTAINER = 'hermes-telegram-gateway-1'
EXPECTED = 'sha256:b05b50fde9b4cb15d41e4e9c395b340e6b234977c7dde0cdaf94e4ce6f697579'
BASE = 'athena-tts-base:voice-test-001'
IMAGE = 'athena-tts-edge:voice-test-001'
PHRASE = 'Проверка голоса. Я Афина, твой помощник.'

INSTALL = r'''import importlib.metadata as md
import os
from pathlib import Path
import re
import subprocess
import sys

before = {d.metadata['Name']: d.version for d in md.distributions() if d.metadata['Name']}
constraints = []
for name, version in before.items():
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*', name) or not re.fullmatch(r'[A-Za-z0-9.!+_-]+', version):
        raise SystemExit('Unsupported installed-package identifier; installation stopped.')
    constraints.append(f'{name}=={version}')
Path('/tmp/athena-constraints.txt').write_text('\n'.join(sorted(constraints)) + '\n')
env = {k: v for k, v in os.environ.items() if not k.startswith(('PIP_', 'UV_'))}
env.update(PYTHONPATH='/tmp/athena-pip.whl', PIP_CONFIG_FILE='/dev/null', PYTHONDONTWRITEBYTECODE='1')
subprocess.run([sys.executable, '-B', '-m', 'pip', '--isolated', '--disable-pip-version-check',
    'install', '--index-url', 'https://pypi.org/simple', '--no-cache-dir',
    '--constraint', '/tmp/athena-constraints.txt', '--report', '/opt/athena-tts/install-report.json',
    'edge-tts==__EDGE_VERSION__'], env=env, check=True)
after = {d.metadata['Name']: d.version for d in md.distributions() if d.metadata['Name']}
if any(after.get(k) != v for k, v in before.items()):
    raise SystemExit('Existing package versions changed; image rejected.')
import edge_tts
print('EDGE_IMPORT_OK; existing package versions preserved')
'''

TEST = r'''import asyncio
import json
from pathlib import Path
import subprocess
import edge_tts

async def main():
    voices = await edge_tts.list_voices()
    preferred = 'ru-RU-SvetlanaNeural'
    names = {v['ShortName'] for v in voices if v.get('Locale') == 'ru-RU' and v.get('Gender') == 'Female'}
    if preferred not in names:
        raise RuntimeError('Selected Russian female voice is unavailable; no automatic substitution.')
    await edge_tts.Communicate(__PHRASE__, preferred).save('/tmp/athena-voice-test.mp3')
    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', '/tmp/athena-voice-test.mp3',
                    '-c:a', 'libopus', '/tmp/athena-voice-test.ogg'], check=True,
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                        '-of', 'json', '/tmp/athena-voice-test.ogg'], capture_output=True, text=True, check=True)
    duration = float(json.loads(r.stdout)['format']['duration'])
    if duration <= 0 or Path('/tmp/athena-voice-test.ogg').stat().st_size < 100:
        raise RuntimeError('Invalid generated audio.')
    print('EDGE_AUDIO_OK', json.dumps({'voice': preferred, 'duration_seconds': duration,
          'bytes': Path('/tmp/athena-voice-test.ogg').stat().st_size}))

try:
    asyncio.run(asyncio.wait_for(main(), timeout=120))
except Exception as exc:
    print('EDGE_AUDIO_FAILED:', type(exc).__name__)
    raise SystemExit(1)
'''

def execute(args, capture=False, timeout=900):
    p = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    if p.returncode:
        raise RuntimeError('Command failed: ' + args[0] + ' (exit ' + str(p.returncode) + '). Details kept local; do not send raw logs.')
    return p.stdout if capture else ''

def fetch(url):
    with urllib.request.urlopen(url, timeout=60) as r:
        return r.read()

def inspect_container():
    return json.loads(execute(['docker', 'inspect', CONTAINER], True))[0]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true', help='Create files, build and test; never switch the gateway')
    args = parser.parse_args()
    if not args.apply:
        print('No changes. Run with sudo python3 prepare_edge_tts.py --apply on Beget.')
        return
    if os.geteuid() != 0:
        raise SystemExit('Run through sudo on Beget.')
    original = inspect_container()
    if original['Image'] != EXPECTED or original['Config'].get('User') != '10000:10000':
        raise SystemExit('Gateway image/user differs from the approved baseline. No changes.')
    if not original['State']['Running']:
        raise SystemExit('Gateway is not running. No changes.')
    if ROOT.exists():
        raise SystemExit('Target directory already exists. Refusing to overwrite. Review it first.')
    for tag in (BASE, IMAGE):
        p = subprocess.run(['docker', 'image', 'inspect', tag], capture_output=True)
        if p.returncode == 0:
            raise SystemExit('A target image tag already exists. Refusing to overwrite.')
    # Fetch public installation materials before making host changes.
    edge = json.loads(fetch('https://pypi.org/pypi/edge-tts/json'))
    pip = json.loads(fetch('https://pypi.org/pypi/pip/json'))
    version = edge['info']['version']
    if not re.fullmatch(r'[0-9]+(?:\.[0-9]+)+(?:[a-z0-9.]*)?', version):
        raise SystemExit('Unexpected Edge version; stop for review.')
    wheel = next(x for x in pip['urls'] if x['filename'].endswith('-py3-none-any.whl'))
    if not wheel['url'].startswith('https://files.pythonhosted.org/'):
        raise SystemExit('Unexpected pip download host.')
    data = fetch(wheel['url'])
    if hashlib.sha256(data).hexdigest() != wheel['digests']['sha256']:
        raise SystemExit('pip wheel checksum mismatch.')
    ROOT.mkdir(mode=0o700)
    context = ROOT / 'build'
    context.mkdir(mode=0o700)
    (context / 'pip.whl').write_bytes(data)
    (context / 'install.py').write_text(INSTALL.replace('__EDGE_VERSION__', version))
    (context / 'test.py').write_text(TEST.replace('__PHRASE__', repr(PHRASE)))
    (context / 'Dockerfile').write_text(
        f'FROM {BASE}\nUSER 0:0\n'
        'COPY pip.whl /tmp/athena-pip.whl\n'
        'COPY install.py /tmp/athena-install.py\n'
        'COPY test.py /opt/athena-tts/test.py\n'
        'RUN /opt/hermes/.venv/bin/python -B /tmp/athena-install.py '
        '&& rm /tmp/athena-pip.whl /tmp/athena-install.py /tmp/athena-constraints.txt\n'
        'USER 10000:10000\n')
    record = {'base_image': EXPECTED, 'new_image': IMAGE, 'edge_version': version,
              'pip_version': pip['info']['version'], 'pip_wheel_sha256': wheel['digests']['sha256'],
              'gateway_before': {'id': original['Id'], 'started_at': original['State']['StartedAt']}}
    (ROOT / 'preparation.json').write_text(json.dumps(record, indent=2) + '\n')
    execute(['docker', 'image', 'tag', EXPECTED, BASE])
    print('Building separate image. Gateway is not being switched.', flush=True)
    build = subprocess.run(['docker', 'build', '--pull=false', '-t', IMAGE, str(context)],
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=1200)
    (ROOT / 'build.log').write_bytes(build.stdout)
    if build.returncode:
        raise RuntimeError('Build failed. Log stays in ' + str(ROOT / 'build.log') + '; do not send it unfiltered.')
    img = json.loads(execute(['docker', 'image', 'inspect', IMAGE], True))[0]
    if img['Config'].get('User') != '10000:10000':
        raise RuntimeError('New image user check failed.')
    # Cover inherited VOLUME destinations with empty temporary filesystems.
    mounts = {'/tmp': 'rw,nosuid,nodev,size=64m,mode=1777'}
    for dest in img['Config'].get('Volumes') or {}:
        if dest != '/opt/data':
            raise RuntimeError('Unexpected image VOLUME; stop for isolation review.')
        mounts[dest] = 'rw,nosuid,nodev,noexec,size=32m,mode=0700,uid=10000,gid=10000'
    args = ['docker', 'create', '--read-only',
        '--cap-drop=ALL', '--security-opt=no-new-privileges', '--pids-limit', '128',
        '--memory', '512m', '--cpus', '1', '--user', '10000:10000']
    for dest, options in mounts.items():
        args += ['--tmpfs', dest + ':' + options]
    # Do not inherit credentials, proxies or service configuration from image ENV.
    for item in img['Config'].get('Env') or []:
        key = item.split('=', 1)[0]
        if key not in {'PATH', 'LANG', 'LC_ALL'}:
            args += ['-e', key + '=']
    args += ['-e', 'HOME=/tmp', '-e', 'PYTHONDONTWRITEBYTECODE=1',
             '--entrypoint', '/opt/hermes/.venv/bin/python', IMAGE,
             '-B', '/opt/athena-tts/test.py']
    test_id = execute(args, True).strip()
    try:
        isolated = json.loads(execute(['docker', 'inspect', test_id], True))[0]
        if any(m.get('Type') != 'tmpfs' for m in isolated.get('Mounts', [])):
            raise RuntimeError('Unexpected test mount; no synthesis started.')
        if isolated['HostConfig'].get('Binds'):
            raise RuntimeError('Unexpected bind mount; no synthesis started.')
        print('Testing neutral text only; no host directories, secrets or gateway environment passed.', flush=True)
        result = subprocess.run(['docker', 'start', '-a', test_id],
                                capture_output=True, text=True, timeout=180)
        (ROOT / 'test.log').write_text(result.stdout + '\n' + result.stderr)
        for line in result.stdout.splitlines():
            if line.startswith(('EDGE_AUDIO_OK ', 'EDGE_AUDIO_FAILED:')):
                print(line)
        if result.returncode or 'EDGE_AUDIO_OK ' not in result.stdout:
            raise RuntimeError('Audio test failed. Raw diagnostic log stays on Beget.')
    finally:
        subprocess.run(['docker', 'rm', '-f', '-v', test_id], capture_output=True, timeout=30)
    current = inspect_container()
    if current['Id'] != original['Id'] or current['State']['StartedAt'] != original['State']['StartedAt'] or not current['State']['Running']:
        raise RuntimeError('Gateway state differs from the starting state; investigate.')
    record.update(test='passed', gateway_unchanged=True, image_id=img['Id'])
    (ROOT / 'preparation.json').write_text(json.dumps(record, indent=2) + '\n')
    print('PREPARATION_OK: audio generated and decoded; gateway unchanged; no Compose/config changes.')

if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        if isinstance(exc, (RuntimeError, SystemExit)):
            raise
        print('Stopped:', type(exc).__name__, '(details not printed to protect local data)', file=sys.stderr)
        sys.exit(1)
