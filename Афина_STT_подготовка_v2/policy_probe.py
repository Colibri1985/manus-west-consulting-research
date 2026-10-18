"""Future read-only docker exec probe. No audio processing/installation. Safe JSON only."""
import os,sys,re,json,hashlib
from pathlib import Path
p=Path('/proc/7');args=(p/'cmdline').read_bytes().split(b'\0')
if not any(b'hermes' in x.lower() or b'gateway' in x.lower() for x in args[1:]):raise SystemExit('PID 7 not confirmed')
status=(p/'status').read_text();identity={}
for k in ['Uid','Gid','Groups']:
 identity[k]=[int(x) for x in re.search(r'^'+k+r':\s*(.*)$',status,re.M).group(1).split()]
env={}
for entry in (p/'environ').read_bytes().split(b'\0'):
 if b'=' in entry:
  k,v=entry.split(b'=',1);env[os.fsdecode(k)]=os.fsdecode(v)
os.environ.clear();os.environ.update(env)
# Match effective process identity for config read. Only drop, never grant new rights.
target_uid=identity['Uid'][1];target_gid=identity['Gid'][1]
if os.geteuid()==0:
 os.setgroups(identity['Groups']);os.setgid(target_gid);os.setuid(target_uid)
if os.geteuid()!=target_uid or os.getegid()!=target_gid:
 raise SystemExit('Cannot run policy probe with effective gateway identity')
from pathlib import Path
original=Path.mkdir
skipped=0;blocked=[]
def mkdir(self,mode=0o777,parents=False,exist_ok=False):
 global skipped
 if exist_ok and self.is_dir():skipped+=1;return None
 return original(self,mode=mode,parents=parents,exist_ok=exist_ok)
Path.mkdir=mkdir
class Denied(RuntimeError):pass
def guard(event,args):
 if event.startswith('socket.') or event in {'subprocess.Popen','os.system','os.exec','os.posix_spawn','os.mkdir','os.remove','os.rename','os.chmod','os.chown','os.utime','os.rmdir','os.truncate','os.link','os.symlink'}:
  blocked.append(event);raise Denied(event)
 if event=='open':
  _,mode,flags=args
  if (isinstance(mode,str) and any(x in mode for x in 'wax+')) or (isinstance(flags,int) and flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND)):
   blocked.append('file write');raise Denied('file write')
sys.addaudithook(guard)
result={'identity':identity,'blocked':blocked,'policy_confirmed':False}
paths=['tools/transcription_tools.py','tools/transcription_local.py','tools/transcription_audio.py','tools/transcription_common.py','tools/environments/local.py','pm/install.py']
result['source_hashes']={rel:hashlib.sha256((Path('/opt/hermes')/rel).read_bytes()).hexdigest() for rel in paths}
try:
 from hermes_cli.config import load_config_readonly,cfg_get,require_readable_config_before_write,get_config_path
 require_readable_config_before_write()
 cfg=load_config_readonly()
 lazy=cfg_get(cfg,'security','allow_lazy_installs',default=True)
 assert isinstance(lazy,bool)
 from pm.install import lazy_installs_allowed
 effective=lazy_installs_allowed()
 result.update({'allow_lazy_installs_config':lazy,'lazy_installs_effectively_allowed':effective,
  'disable_lazy_installs_env':os.environ.get('HERMES_DISABLE_LAZY_INSTALLS','').strip().lower() in {'1','true','yes'},
  'policy_confirmed':not blocked,'config_sha256':hashlib.sha256(Path(get_config_path()).read_bytes()).hexdigest()})
except Exception as e:result['error_type']=type(e).__name__
print('ATHENA_POLICY_RESULT='+json.dumps(result))
