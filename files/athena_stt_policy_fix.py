"""Scoped preparation-package correction. No Docker, install or live config calls.
Default is check only. --apply changes control.py, README.md and MANIFEST.json only.
Creates a sibling backup of those three files; never overwrites an existing backup.
"""
import argparse,ast,hashlib,json,os,tempfile
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--root',type=Path,default=Path('/srv/hermes-agent/athena-stt-prep-v2_1'))
p.add_argument('--apply',action='store_true')
a=p.parse_args();root=a.root.resolve()
sha=lambda b:hashlib.sha256(b).hexdigest()
manifest_path=root/'MANIFEST.json'
old_manifest=manifest_path.read_bytes()
if sha(old_manifest)!='080275cc7219f13a60bec7c8ed32218bee441b2035dded4a0ec4c3a456e7d99a':
 raise SystemExit('STOP: unexpected package manifest; no changes made')
m=json.loads(old_manifest)
actual={str(x.relative_to(root)) for x in root.rglob('*') if x.is_file() and x.name!='MANIFEST.json'}
if actual!=set(m['files']):raise SystemExit('STOP: package file set changed')
for name,meta in m['files'].items():
 q=root/name
 if q.is_symlink() or sha(q.read_bytes())!=meta['sha256']:raise SystemExit('STOP: package file changed: '+name)
old_line=" if policy.get('lazy_installs_effectively_allowed') is not False:raise RuntimeError('Global lazy installs are not confirmed disabled; do not change automatically')"
new_line=" if type(policy.get('lazy_installs_effectively_allowed')) is not bool:raise RuntimeError('Effective lazy-install policy was not established')"
old_note='Если глобальная автоустановка НЕ подтверждена отключённой, дальнейшие этапы блокируются;\nскрипт сам её не отключает и не включает. Важна политика, а не произвольный bool.'
new_note='Глобальная политика автоустановки фиксируется как наблюдаемый bool, но не меняется.\nДля local_command её глобальное отключение не требуется. Неизвестное значение блокирует\nпродолжение. Изолированные тестовые контейнеры по-прежнему явно получают\nHERMES_DISABLE_LAZY_INSTALLS=1; рабочая конфигурация и права не меняются.'
control=(root/'control.py').read_text();readme=(root/'README.md').read_text()
if control.count(old_line)!=1 or readme.count(old_note)!=1:
 raise SystemExit('STOP: expected correction targets not unique')
new_control=control.replace(old_line,new_line)
ast.parse(new_control,filename='control.py')
# Explicitly preserve the local test/container restriction and immutable-image gates.
for marker in ["'--env','HERMES_DISABLE_LAZY_INSTALLS=1'",'def validate_base_identity(',"for which in ['direct','integration']:"]:
 if marker not in new_control:raise SystemExit('STOP: expected safety guard missing')
updates={'control.py':new_control.encode(),'README.md':readme.replace(old_note,new_note).encode()}
for name,data in updates.items():m['files'][name]={'sha256':sha(data),'size_bytes':len(data)}
m['policy_correction']='Record global lazy-install bool without changing it; isolated containers retain explicit disable flag; no test/gate bypass.'
updates['MANIFEST.json']=(json.dumps(m,ensure_ascii=False,indent=2)+'\n').encode()
print('CHECK_OK: original v2.1 files verified; correction limited to control.py, README.md, MANIFEST.json')
if not a.apply:
 print('CHECK_ONLY: no files changed; use --apply after reviewing scope')
 raise SystemExit(0)
backup=root.with_name(root.name+'.before-policy-fix')
backup.mkdir(mode=0o700)
for name in updates:
 q=backup/name
 fd=os.open(q,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
 with os.fdopen(fd,'wb') as f:f.write((root/name).read_bytes())
def atomic_write(path,data):
 fd,temp=tempfile.mkstemp(prefix='.policy-fix-',dir=path.parent)
 try:
  os.fchmod(fd,path.stat().st_mode & 0o777)
  with os.fdopen(fd,'wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
  os.replace(temp,path)
 finally:
  if os.path.exists(temp):os.unlink(temp)
try:
 for name,data in updates.items():atomic_write(root/name,data)
 for name,data in updates.items():
  if (root/name).read_bytes()!=data:raise RuntimeError('read-back mismatch: '+name)
except Exception:
 print('STOP: incomplete correction; do not run preflight; originals available at',backup)
 raise
print('APPLIED_AND_VERIFIED: only preparation package updated')
print('BACKUP:',backup)
print('MANIFEST_SHA256:',sha(updates['MANIFEST.json']))
print('Production config, Docker, permissions, install policy and services were NOT changed')
