"""Host root, future approved switch ONLY. Never prints config or secrets."""
import argparse,os,json,re,hashlib,tempfile,stat
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('action',choices=['apply','restore']);p.add_argument('--backup',required=True,type=Path);a=p.parse_args()
if os.environ.get('ATHENA_APPROVE_SWITCH')!='YES':raise SystemExit('STOP: separate switch/rollback approval required')
config=Path('/srv/hermes-agent/telegram-data/config.yaml');backup=a.backup
sha=lambda b:hashlib.sha256(b).hexdigest()
def atomic(data):
 s=config.stat();fd,tmp=tempfile.mkstemp(prefix='.athena-stt-',dir=config.parent)
 try:
  os.fchmod(fd,stat.S_IMODE(s.st_mode));os.fchown(fd,s.st_uid,s.st_gid)
  with os.fdopen(fd,'wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
  os.replace(tmp,config)
 finally:
  if os.path.exists(tmp):os.unlink(tmp)
if a.action=='apply':
 if backup.exists():raise SystemExit('STOP: backup directory already exists')
 raw=config.read_bytes();text=raw.decode('utf-8');lines=text.splitlines(keepends=True)
 if '\r' in text or '\t' in text:raise SystemExit('STOP: unusual YAML whitespace requires review')
 # Deliberately restricted editor: fail rather than alter ambiguous/multi-document YAML.
 if re.search(r'(?m)^\s*(---|\.\.\.)\s*$',text):raise SystemExit('STOP: YAML documents require review')
 starts=[i for i,l in enumerate(lines) if re.match(r'^stt\s*:',l)]
 if len(starts)>1:raise SystemExit('STOP: duplicate STT sections')
 if starts:
  start=starts[0]
  if not re.fullmatch(r'stt:\s*(?:#.*)?\n?',lines[start]):raise SystemExit('STOP: inline/anchored STT requires review')
  end=start+1
  while end<len(lines):
   l=lines[end]
   if l.strip() and not l[0].isspace() and not l.lstrip().startswith('#'):break
   end+=1
  if re.search(r'[&*]|<<\s*:', ''.join(lines[start:end])):raise SystemExit('STOP: STT aliases require review')
 else:start=end=len(lines)
 target=(Path(__file__).parent/'stt-target.yaml').read_text()
 new=''.join(lines[:start])+('' if start==0 or lines[start-1].endswith('\n') else '\n')+target+''.join(lines[end:])
 new=new.encode('utf-8')
 backup.mkdir(mode=0o700,parents=False)
 fd=os.open(backup/'config.before.yaml',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
 with os.fdopen(fd,'wb') as f:f.write(raw)
 metadata={'original_sha256':sha(raw),'applied_sha256':sha(new),'note':'Whole-config backup is secret-bearing; never send it to chat or build context'}
 fd=os.open(backup/'transaction.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
 with os.fdopen(fd,'w') as f:json.dump(metadata,f)
 atomic(new)
 print('APPLIED_STT_ONLY original_sha256='+sha(raw)+' new_sha256='+sha(new))
else:
 meta=json.loads((backup/'transaction.json').read_text());raw=config.read_bytes()
 if sha(raw)==meta['original_sha256']:
  print('CONFIG_ALREADY_RESTORED sha256='+sha(raw));raise SystemExit(0)
 if sha(raw)!=meta['applied_sha256']:raise SystemExit('STOP: config changed after switch; selective rollback needs review')
 original=(backup/'config.before.yaml').read_bytes()
 if sha(original)!=meta['original_sha256']:raise SystemExit('STOP: backup integrity failed')
 atomic(original);assert config.read_bytes()==original
 print('RESTORED_CONFIG_EXACTLY sha256='+sha(original))
