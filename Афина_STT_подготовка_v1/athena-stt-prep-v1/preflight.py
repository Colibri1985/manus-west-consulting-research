"""Host-only READ-ONLY preflight. stdout contains safe facts only; no files created."""
import subprocess,json,re
from pathlib import Path
NAME='hermes-telegram-gateway-1'
BASE='nousresearch/hermes-agent@sha256:9774f4f39a9bb8c2f68ce728ed5e99ddbad282163be56764afacf88ed952b784'
def run(args,**kw):
 r=subprocess.run(args,capture_output=True,text=True,timeout=30,**kw)
 if r.returncode:raise SystemExit('Preflight subprocess failed; exit='+str(r.returncode)+'; raw output withheld')
 return r.stdout
c=json.loads(run(['docker','inspect',NAME]))[0]
b=json.loads(run(['docker','image','inspect',BASE]))[0]
assert c['Image']==b['Id'],'Running image does not match approved base'
# Print names only if credentials were baked into the parent image; never their values.
baked=[]
for entry in b.get('Config',{}).get('Env') or []:
 name,_,value=entry.partition('=')
 if value and re.search(r'(^|_)(API_KEY|TOKEN|PASSWORD|SECRET|PRIVATE_KEY)$',name):baked.append(name)
print('BASE_IMAGE_CREDENTIAL_VARIABLE_NAMES:',baked)
assert not baked,'Test containers must not inherit baked credentials'
print('BASE_RUNTIME_USER:',b.get('Config',{}).get('User') or '0:0')
probe=r"""
import os,json,re,ast,hashlib
from pathlib import Path
p=Path('/proc/7')
a=(p/'cmdline').read_bytes().split(b'\0')
assert any(b'hermes' in x.lower() or b'gateway' in x.lower() for x in a[1:]),'PID 7 not identified'
s=(p/'status').read_text()
facts={}
for key in ['Uid','Gid','Groups']:
 m=re.search(r'^'+key+r':\s*(.*)$',s,re.M);facts[key]=[int(x) for x in m.group(1).split()]
print('GATEWAY_PROCESS_IDENTITY:',json.dumps(facts))
print('CONFIGURED_IMAGE_USER_IS_NOT_A_SUBSTITUTE_FOR_PROCESS_IDENTITY')
p=Path('/var/lib/hermes/config.yaml');text=p.read_text()
inside=False;v=[]
for line in text.splitlines():
 if line and not line[0].isspace() and not line.lstrip().startswith('#'):inside=bool(re.fullmatch(r'security:\s*(?:#.*)?',line))
 if inside:
  m=re.fullmatch(r' {2}allow_lazy_installs:\s*(true|false)\s*(?:#.*)?',line,re.I)
  if m:v.append(m.group(1).lower())
print('ALLOW_LAZY_INSTALLS_EXPLICIT_RAW:',v[0] if len(v)==1 else 'NOT_ESTABLISHED; no boolean parsed or duplicates')
print('ALLOW_LAZY_INSTALLS_EFFECTIVE: not inferred from absence; do not enable it')
for name in ['transcription_local.py','transcription_tools.py']:
 p=Path('/opt/hermes/tools')/name;t=p.read_text();print('INSTALLED_SOURCE_SHA256',name,hashlib.sha256(p.read_bytes()).hexdigest())
 tree=ast.parse(t)
 for n in tree.body:
  if isinstance(n,ast.FunctionDef) and n.name in ['_transcribe_local_command','_resolve_explicit_provider','_get_provider','_resolve_local_command']:
   print('INSTALLED_FUNCTION',n.name);print(ast.get_source_segment(t,n))
"""
print(run(['docker','exec','-i','-w','/opt/hermes',NAME,'/opt/hermes/.venv/bin/python','-B','-'],input=probe))
print('PASS: read-only facts gathered; runtime/build/download NOT executed')
