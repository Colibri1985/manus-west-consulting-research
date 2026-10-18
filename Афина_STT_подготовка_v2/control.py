"""Future host orchestration. Default-deny. No phase is run merely by opening/importing this file."""
from pathlib import Path
import os,sys,json,hashlib,subprocess,re,tempfile,stat
ROOT=Path(__file__).resolve().parent
STATE=Path('/srv/hermes-agent/athena-stt-state/v2')
CACHE=Path('/srv/hermes-agent/athena-stt-cache')
LIVE_CONFIG=Path('/srv/hermes-agent/telegram-data/config.yaml')
NAME='hermes-telegram-gateway-1'
BASE='nousresearch/hermes-agent@sha256:9774f4f39a9bb8c2f68ce728ed5e99ddbad282163be56764afacf88ed952b784'
BASE_ID='sha256:373ddd5e6649f525b17993e1c885cdf1352127f8e98fd329140a73237125e52f'
IMAGE='athena-hermes-stt:fw1.2.1-av16.1.0-v2'
COMMON=['-f','/srv/hermes-agent/compose.telegram.yaml','-f','/srv/hermes-agent/compose.telegram.workspace.yaml','-f','/srv/hermes-agent/compose.telegram.executor.yaml']
sha=lambda b:hashlib.sha256(b).hexdigest()
def need(key):
 if os.environ.get(key)!='YES':raise RuntimeError('Separate approval required: '+key)
def run(args,*,data=None,timeout=60):
 r=subprocess.run(args,input=data,capture_output=True,text=True,timeout=timeout)
 if r.returncode:raise RuntimeError('Command failed; exit='+str(r.returncode)+'; raw output withheld')
 return r.stdout
def manifest():
 raw=(ROOT/'MANIFEST.json').read_bytes();m=json.loads(raw)
 actual={str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file() and p.name!='MANIFEST.json'}
 if actual!=set(m['files']):raise RuntimeError('Package file set changed')
 for rel,meta in m['files'].items():
  if sha((ROOT/rel).read_bytes())!=meta['sha256']:raise RuntimeError('Package file changed: '+rel)
 return m,sha(raw)
def build_digest():
 files={str(p.relative_to(ROOT/'build-context')):sha(p.read_bytes()) for p in (ROOT/'build-context').rglob('*') if p.is_file()}
 return sha(json.dumps(files,sort_keys=True,separators=(',',':')).encode())
def inspect_image(name):return json.loads(run(['docker','image','inspect',name]))[0]
def image():
 im=inspect_image(IMAGE)
 if im['Config'].get('Labels',{}).get('org.athena.stt.build-digest')!=build_digest():raise RuntimeError('Image build fingerprint mismatch')
 return im

def write_result(name,value):
 STATE.mkdir(mode=0o700,parents=True,exist_ok=True)
 fd,tmp=tempfile.mkstemp(dir=STATE,prefix='receipt-')
 with os.fdopen(fd,'w') as f:json.dump(value,f,indent=2);f.flush();os.fsync(f.fileno())
 os.replace(tmp,STATE/(name+'.json'))
def facts():
 f=json.loads((STATE/'preflight.json').read_text())
 _,mh=manifest()
 if f['package_manifest_sha256']!=mh:raise RuntimeError('Preflight belongs to a different package')
 if not f['policy']['policy_confirmed'] or f['policy']['blocked']:raise RuntimeError('Policy probe not conclusive')
 return f

def model_hash():
 p=CACHE/'model-manifest.json';raw=p.read_bytes();m=json.loads(raw)
 if m['revision']!='ebe41f70d5b6dfa9166e2c581c45c9c0cfc57b66':raise RuntimeError('Wrong model revision')
 for n,d in m['files'].items():
  if '/' in n or n in {'.','..'}:raise RuntimeError('Invalid model path')
  h=hashlib.sha256()
  with (CACHE/'base'/n).open('rb') as f:
   for b in iter(lambda:f.read(1048576),b''):h.update(b)
  if h.hexdigest()!=d['sha256']:raise RuntimeError('Model file changed: '+n)
 return sha(raw)
def gateway():return json.loads(run(['docker','inspect',NAME]))[0]
def baked_credentials(im):
 names=[]
 for e in im.get('Config',{}).get('Env') or []:
  k,_,v=e.partition('=')
  if v and re.search(r'(^|_)(API_KEY|TOKEN|PASSWORD|SECRET|PRIVATE_KEY)$',k):names.append(k)
 if names:raise RuntimeError('Image has credential-like ENV names: '+','.join(names))

def preflight():
 need('ATHENA_APPROVE_PREFLIGHT');m,mh=manifest();g=gateway();base=inspect_image(BASE)
 if g['Image']!=BASE_ID or base['Id']!=BASE_ID or base.get('Architecture')!='amd64':raise RuntimeError('Wrong base/platform/current image')
 baked_credentials(base)
 output=run(['docker','exec','-i','-w','/opt/hermes',NAME,'/opt/hermes/.venv/bin/python','-B','-'],data=(ROOT/'policy_probe.py').read_text())
 lines=[x for x in output.splitlines() if x.startswith('ATHENA_POLICY_RESULT=')]
 if len(lines)!=1:raise RuntimeError('No unambiguous policy result')
 policy=json.loads(lines[0].split('=',1)[1])
 if not policy.get('policy_confirmed') or policy.get('blocked'):raise RuntimeError('Policy probe incomplete: '+str(policy.get('error_type','blocked')))
 expected=json.loads((ROOT/'build-context/contract-hashes.json').read_text())['source_hashes']
 if policy.get('source_hashes')!=expected:raise RuntimeError('Live selected source files differ from pinned image evidence')
 if policy.get('lazy_installs_effectively_allowed') is not False:raise RuntimeError('Global lazy installs are not confirmed disabled; do not change automatically')
 value={'package_manifest_sha256':mh,'base_image_id':BASE_ID,'container_id':g['Id'],
        'base_runtime_user':base['Config'].get('User') or '0:0','policy':policy,
        'compose_fingerprints':{COMMON[i+1]:sha(Path(COMMON[i+1]).read_bytes()) for i in range(0,len(COMMON),2)}}
 write_result('preflight',value)
 print(json.dumps({'base_image_id':BASE_ID,'identity':policy['identity'],
  'allow_lazy_installs_config':policy['allow_lazy_installs_config'],
  'lazy_installs_effectively_allowed':policy['lazy_installs_effectively_allowed'],'status':'preflight recorded'},indent=2))
def build():
 need('ATHENA_APPROVE_BUILD');f=facts();d=build_digest()
 run(['docker','build','--pull=false','--build-arg','BASE_RUNTIME_USER='+f['base_runtime_user'],
      '--build-arg','ATHENA_BUILD_DIGEST='+d,'-t',IMAGE,str(ROOT/'build-context')],timeout=1800)
 im=image();baked_credentials(im);print('BUILT_IMAGE_ID',im['Id'])
def container_args(f,im,*,offline=True):
 uid=f['policy']['identity']['Uid'][1];gid=f['policy']['identity']['Gid'][1]
 a=['docker','run','--rm','--pull=never','--user',str(uid)+':'+str(gid),'--cap-drop=ALL',
    '--security-opt=no-new-privileges','--read-only','--pids-limit=128','--cpus=2','--memory=2g',
    '--tmpfs','/tmp:rw,nosuid,nodev,size=256m,mode=1777',
    '--env','HOME=/tmp','--env','HERMES_HOME=/tmp/hermes-test',
    '--env','HERMES_DISABLE_LAZY_INSTALLS=1',
    '--env','EXPECTED_UID='+str(uid),'--env','EXPECTED_GID='+str(gid),
    '--env','HF_HUB_DISABLE_TELEMETRY=1','--env','HF_HUB_DISABLE_XET=1']
 # Existing supplementary groups only: preserve them for the test, never invent grants.
 for group in f['policy']['identity']['Groups']:
  if group!=gid:a+=['--group-add',str(group)]
 if offline:a+=['--network=none','--env','HF_HUB_OFFLINE=1']
 return a

def download():
 need('ATHENA_APPROVE_DOWNLOAD');f=facts();im=image();baked_credentials(im)
 if not CACHE.is_dir():raise RuntimeError('Dedicated cache not prepared; no automatic ownership/permission changes')
 output=run(container_args(f,im,offline=False)+['--env','HF_HOME=/var/cache/athena-stt/hf',
  '--mount','type=bind,src='+str(CACHE)+',dst=/var/cache/athena-stt',
  '--entrypoint','/opt/athena-stt/venv/bin/python',im['Id'],'/opt/athena-stt/download_model.py'],timeout=1200)
 print('MODEL_DOWNLOADED_AND_MANIFEST_WRITTEN',model_hash())
def test(which):
 need('ATHENA_APPROVE_TEST');f=facts();im=image();baked_credentials(im);_,mh=manifest()
 # Invalidate any older success before starting a new attempt.
 write_result(which,{'test':which,'success':False,'reason':'new attempt pending'})
 python='/opt/athena-stt/venv/bin/python' if which=='direct' else '/opt/hermes/.venv/bin/python'
 script='selftest.py' if which=='direct' else 'integration_test.py'
 output=run(container_args(f,im)+['--mount','type=bind,src='+str(CACHE)+',dst=/var/cache/athena-stt,readonly',
  '--mount','type=bind,src='+str(ROOT/'fixtures')+',dst=/fixtures,readonly',
  '--entrypoint',python,im['Id'],'/opt/athena-stt/'+script],timeout=700)
 lines=[x for x in output.splitlines() if x.startswith('ATHENA_TEST_RESULT=')]
 if len(lines)!=1:raise RuntimeError('Missing unique test result')
 value=json.loads(lines[0].split('=',1)[1])
 if value.get('test')!=which or value.get('success') is not True:raise RuntimeError('Test failed')
 if value['model_manifest_sha256']!=model_hash():raise RuntimeError('Model changed during test')
 value.update({'image_id':im['Id'],'package_manifest_sha256':mh,'build_digest':build_digest(),
               'network_mode':'none','preflight_sha256':sha((STATE/'preflight.json').read_bytes())})
 write_result(which,value);print(json.dumps(value,indent=2))

def gate():
 f=facts();im=image();_,mh=manifest();model=model_hash()
 for which in ['direct','integration']:
  value=json.loads((STATE/(which+'.json')).read_text())
  for k,want in {'test':which,'success':True,'image_id':im['Id'],'package_manifest_sha256':mh,
                 'build_digest':build_digest(),'network_mode':'none','model_manifest_sha256':model,
                 'preflight_sha256':sha((STATE/'preflight.json').read_bytes())}.items():
   if value.get(k)!=want:raise RuntimeError('Acceptance receipt mismatch: '+which+'.'+k)
  if value['identity']['uid']!=f['policy']['identity']['Uid'][1] or value['identity']['gid']!=f['policy']['identity']['Gid'][1]:raise RuntimeError('Test identity mismatch')
 for name,want in f['compose_fingerprints'].items():
  if sha(Path(name).read_bytes())!=want:raise RuntimeError('Original Compose changed')
 cfg=LIVE_CONFIG
 if sha(cfg.read_bytes())!=f['policy']['config_sha256']:raise RuntimeError('Live config changed since preflight')
 current=gateway()
 if current['Image']!=BASE_ID:raise RuntimeError('Current gateway no longer matches approved base')
 if current['Id']!=f['container_id']:raise RuntimeError('Gateway container was recreated after preflight')
 return im['Id']

def switch():
 need('ATHENA_APPROVE_SWITCH');image_id=gate()
 # A fourth file must become the persistent invocation, not an occasional manual override.
 if os.environ.get('ATHENA_FOURTH_COMPOSE_REVIEWED')!='YES':raise RuntimeError('Persistent launch procedure with fourth Compose file not reviewed')
 backup=Path(os.environ['BACKUP_DIR'])
 run(['docker','compose',*COMMON,'-f',str(ROOT/'compose.telegram.stt.yaml'),'config','--quiet'])
 # Bind the actual Compose image reference to the immutable tested ID, not a mutable tag.
 # Write a transaction-only override identical to reviewed one except immutable image.
 override=(ROOT/'compose.telegram.stt.yaml').read_text().replace('athena-hermes-stt:fw1.2.1-av16.1.0-v2',image_id)
 # Do not create backup here: config_transaction.py requires a fresh directory.
 env=dict(os.environ);env['ATHENA_APPROVE_SWITCH']='YES'
 subprocess.run([sys.executable,str(ROOT/'config_transaction.py'),'apply','--backup',str(backup)],check=True,env=env)
 (backup/'compose.tested-image.yaml').write_text(override)
 try:
  run(['docker','compose',*COMMON,'-f',str(backup/'compose.tested-image.yaml'),
    'up','-d','--no-deps','--no-build','--pull','never','--force-recreate','gateway'],timeout=180)
 except Exception:
  raise RuntimeError('Switch failed AFTER config apply. MANUAL rollback required; no automatic rollback performed.')
 if gateway()['Image']!=image_id:raise RuntimeError('Gateway image mismatch; MANUAL rollback required')
 print('SWITCHED_IMAGE',image_id,'VOICE_ACCEPTANCE_STILL_REQUIRED')
 print('PERSISTENT_FOURTH_COMPOSE_FILE',backup/'compose.tested-image.yaml')
def rollback():
 need('ATHENA_APPROVE_SWITCH');backup=Path(os.environ['BACKUP_DIR'])
 subprocess.run([sys.executable,str(ROOT/'config_transaction.py'),'restore','--backup',str(backup)],check=True)
 run(['docker','compose',*COMMON,'up','-d','--no-deps','--no-build','--pull','never','--force-recreate','gateway'],timeout=180)
 if gateway()['Image']!=BASE_ID:raise RuntimeError('Original image not restored')
 print('ROLLBACK_IMAGE_CONFIRMED',BASE_ID,'No data/model/image deletion')

if __name__=='__main__':
 try:
  action=sys.argv[1]
  if action=='preflight':preflight()
  elif action=='build':build()
  elif action=='download':download()
  elif action in ['direct','integration']:test(action)
  elif action=='gate':print('GATE_PASSED_IMAGE',gate())
  elif action=='switch':switch()
  elif action=='rollback':rollback()
  else:raise RuntimeError('Unknown action')
 except Exception as e:
  print('STOP:',type(e).__name__,str(e));sys.exit(1)
