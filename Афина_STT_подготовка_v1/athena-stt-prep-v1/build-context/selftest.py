import os,sys,json,hashlib,re,subprocess,importlib.metadata,time
from pathlib import Path
expected_uid=int(os.environ['EXPECTED_UID']);expected_gid=int(os.environ['EXPECTED_GID'])
assert os.getuid()==expected_uid and os.getgid()==expected_gid,'Wrong runtime identity'
print('IDENTITY',json.dumps({'uid':os.getuid(),'gid':os.getgid(),'groups':os.getgroups()}))
versions=json.loads(Path('/opt/athena-stt/versions.json').read_text())
for name,wanted in versions.items():assert importlib.metadata.version(name)==wanted,(name,'version mismatch')
fixture=Path('/fixtures/jfk.flac');provenance=json.loads(Path('/fixtures/provenance.json').read_text())
assert hashlib.sha256(fixture.read_bytes()).hexdigest()==provenance['sha256'],'Wrong test fixture'
manifest=json.loads(Path('/var/cache/athena-stt/model-manifest.json').read_text())
for name,meta in manifest['files'].items():
 p=Path('/var/cache/athena-stt/base')/name
 assert p.is_file() and os.access(p,os.R_OK),'Model not readable'
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(1048576),b''):h.update(block)
 assert h.hexdigest()==meta['sha256'],'Model checksum mismatch'
# No Telegram entrypoint or secrets. --network none is REQUIRED by test.sh.
start=time.monotonic()
subprocess.run([sys.executable,'/opt/athena-stt/transcribe.py',str(fixture),
 '--output-dir','/tmp','--language','en'],check=True,timeout=180)
text=Path('/tmp/transcript.txt').read_text()
normal=re.sub(r'[^a-z ]',' ',text.lower());normal=' '.join(normal.split())
for phrase in provenance['expected_substrings']:assert phrase in normal,('Unexpected transcript',text)
print('RECOGNITION_TEXT_PUBLIC_FIXTURE:',text)
print('OFFLINE_RECOGNITION_PASS elapsed_seconds=',round(time.monotonic()-start,2))
# Second pass proves repeated access to existing readonly model cache.
subprocess.run([sys.executable,'/opt/athena-stt/transcribe.py',str(fixture),
 '--output-dir','/tmp','--language','en'],check=True,timeout=180)
assert Path('/tmp/transcript.txt').read_text().strip()
print('SECOND_OFFLINE_RECOGNITION_PASS')
