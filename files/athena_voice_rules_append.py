"""Append the approved voice-transcript rules to the approved live SOUL.md only.
Default: read-only check. --apply: backup, in-place append, verification.
No config/STT/model/permission/container state changes or service restarts.
"""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import tempfile

TARGET = Path('/srv/hermes-agent/telegram-data/SOUL.md')
EXPECTED = '5daafcd4d6bd62d781612c6a1049e8f97e0766748bf265ed53a51654e8755d61'
CONTAINER = 'hermes-telegram-gateway-1'
DESTINATION = '/var/lib/hermes/SOUL.md'
SECTION = '''## Обработка голосовых сообщений и расшифровок

Поступившая расшифровка может содержать ошибки распознавания.
Я не считаю её гарантированно дословной записью голоса Андрея.

Перед ответом я проверяю расшифровку на непонятные слова,
противоречия и неоднозначности. Если сомнение влияет на смысл
ответа или предполагаемое действие, задаю короткий конкретный
уточняющий вопрос.

Я не заменяю сомнительные слова молча. Показываю исходный
фрагмент и предлагаю исправление только как предположение:
«В расшифровке “редкрытые”; ты имел в виду “открытые”?»

Перед значимым действием по голосовому поручению я повторяю
существенные параметры: действие, объект, сумму и валюту,
дату и время, адресата или направление — в зависимости
от задачи. Получаю подтверждение конкретного действия
с этими параметрами.

Подтверждение правильности расшифровки не считаю
автоматическим разрешением на покупку, отправку сообщения,
изменение данных или другое значимое действие.

Если Андрей просит дословную расшифровку, я воспроизвожу
поступивший текст без смыслового редактирования.
Сомнительные фрагменты и возможные исправления указываю
отдельно, не подменяя ими исходный текст.

Я ясно различаю работу с расшифровкой и проверку аудио.
Не утверждаю, что прослушала запись или сверилась с аудио,
если работала только с текстом. В таком случае дословность
означает точное воспроизведение полученной расшифровки,
а не подтверждённое совпадение с исходной речью.

В обычной беседе без существенных неоднозначностей
я не требую подтверждения каждого сообщения.

Исправления Андрея учитываю в текущей задаче.
Не заявляю, что эти исправления переобучили распознаватель
или изменили его настройки, если такого изменения
в действительности не выполнялось.
'''
TITLE = SECTION.splitlines()[0]

PROBE = r'''
import hashlib,json,os
from pathlib import Path
try:
    proc=Path('/proc/7')
    args=(proc/'cmdline').read_bytes().split(b'\0')
    if not any(b'gateway' in arg for arg in args[1:]):
        raise RuntimeError('PID not confirmed')
    env={}
    for item in (proc/'environ').read_bytes().split(b'\0'):
        if b'=' in item:
            key,value=item.split(b'=',1)
            env[os.fsdecode(key)]=os.fsdecode(value)
    if env.get('HERMES_HOME')!='/var/lib/hermes':
        raise RuntimeError('Home not confirmed')
    profile=env.get('HERMES_PROFILE', 'default')
    if profile not in ('', 'default'):
        raise RuntimeError('Non-default profile')
    data=Path('/var/lib/hermes/SOUL.md').read_bytes()
    print(json.dumps({'home':'/var/lib/hermes','profile':profile or 'default',
        'sha256':hashlib.sha256(data).hexdigest()}))
except Exception as exc:
    print(json.dumps({'error_type':type(exc).__name__}))
'''

def digest(data):
    return hashlib.sha256(data).hexdigest()

def docker_read(args):
    result = subprocess.run(['docker', *args], capture_output=True, timeout=60)
    if result.returncode:
        raise RuntimeError('Docker read failed; raw output withheld')
    return result.stdout

def verify_gateway(expected_hash):
    info = json.loads(docker_read(['inspect', CONTAINER]))[0]
    if not info.get('State', {}).get('Running'):
        raise RuntimeError('Gateway is not running')
    mounts = [m for m in info.get('Mounts', []) if m.get('Destination') == DESTINATION]
    if len(mounts) != 1:
        raise RuntimeError('Exact SOUL mount not confirmed')
    m = mounts[0]
    if m.get('Type') != 'bind' or m.get('Source') != str(TARGET) or m.get('RW') is not False:
        raise RuntimeError('Approved read-only SOUL bind mount not confirmed')
    report = json.loads(docker_read(['exec', '-w', '/opt/hermes', CONTAINER,
        '/opt/hermes/.venv/bin/python', '-B', '-c', PROBE]))
    if report.get('home') != '/var/lib/hermes' or report.get('profile') != 'default':
        raise RuntimeError('Active gateway home/default profile not confirmed')
    if report.get('sha256') != expected_hash:
        raise RuntimeError('Host/container SOUL bytes differ')
    return info['Id']

def metadata(s):
    return s.st_dev, s.st_ino, s.st_uid, s.st_gid, stat.S_IMODE(s.st_mode)

def apply(approved=False):
    if TARGET.is_symlink():
        raise RuntimeError('SOUL is a symlink; separate review needed')
    flags = (os.O_RDWR if approved else os.O_RDONLY) | os.O_NOFOLLOW
    fd = os.open(TARGET, flags)
    with os.fdopen(fd, 'r+b' if approved else 'rb') as stream:
        fcntl.flock(stream, fcntl.LOCK_EX if approved else fcntl.LOCK_SH)
        before_stat = os.fstat(stream.fileno())
        if not stat.S_ISREG(before_stat.st_mode):
            raise RuntimeError('SOUL is not a regular file')
        old = stream.read()
        if digest(old) != EXPECTED:
            raise RuntimeError('SOUL changed since content review; no append permitted')
        if TITLE in old.decode('utf-8'):
            raise RuntimeError('Voice section already exists; separate review needed')
        original_meta = metadata(before_stat)
        container_id = verify_gateway(EXPECTED)
        print('CHECK_OK: approved source hash, bind mount and active default home confirmed')
        if not approved:
            print('READ_ONLY: no files changed')
            return
        backup_fd, backup_name = tempfile.mkstemp(
            prefix='SOUL.md.before-voice-rules.', suffix='.bak', dir=TARGET.parent)
        with os.fdopen(backup_fd, 'wb') as backup:
            backup.write(old)
            backup.flush()
            os.fsync(backup.fileno())
        if Path(backup_name).read_bytes() != old:
            raise RuntimeError('Backup verification failed; SOUL not changed')
        if metadata(TARGET.stat()) != original_meta:
            raise RuntimeError('SOUL identity/metadata changed before append')
        stream.seek(0)
        if stream.read() != old:
            raise RuntimeError('SOUL bytes changed before append')
        new = old + b'\n\n' + SECTION.encode('utf-8')
        try:
            stream.seek(0, os.SEEK_END)
            stream.write(new[len(old):])
            stream.flush()
            os.fsync(stream.fileno())
            stream.seek(0)
            actual = stream.read()
            if actual != new or not actual.startswith(old):
                raise RuntimeError('Content preservation check failed')
            if metadata(os.fstat(stream.fileno())) != original_meta or metadata(TARGET.stat()) != original_meta:
                raise RuntimeError('File metadata changed')
            if verify_gateway(digest(new)) != container_id:
                raise RuntimeError('Gateway container changed during edit')
        except Exception:
            # Revert only our append, and only if no concurrent change is observed.
            stream.seek(0)
            current = stream.read()
            if current == new:
                stream.seek(0)
                stream.truncate(len(old))
                stream.flush()
                os.fsync(stream.fileno())
                stream.seek(0)
                if stream.read() == old:
                    print('OWN_APPEND_REVERTED: original bytes restored; gateway unchanged by script')
            print('BACKUP:', backup_name)
            raise
        print('SAVED_PATH:', TARGET)
        print('BACKUP:', backup_name)
        print('SECTION_PRESENT_EXACTLY_ONCE:', actual.decode('utf-8').count(TITLE) == 1)
        print('ORIGINAL_BYTES_PRESERVED:', actual[:len(old)] == old)
        print('INODE_OWNER_MODE_UNCHANGED:', metadata(os.fstat(stream.fileno())) == original_meta)
        print('CONTAINER_SEES_UPDATED_FILE: True')
        print('ORIGINAL_SHA256:', EXPECTED)
        print('NEW_SHA256:', digest(actual))
        print('NEW_SESSION_REQUIRED_FOR_ACCEPTANCE: no restart performed')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    try:
        apply(args.apply)
    except Exception as exc:
        print('STOP:', type(exc).__name__, str(exc) if isinstance(exc, RuntimeError) else 'details withheld')
        raise SystemExit(1)
