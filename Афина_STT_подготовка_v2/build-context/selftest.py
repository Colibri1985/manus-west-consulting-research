import os,sys,json,hashlib,re,subprocess,importlib.metadata,time
from pathlib import Path

def identity():
    uid=int(os.environ['EXPECTED_UID']);gid=int(os.environ['EXPECTED_GID'])
    assert os.getuid()==uid and os.getgid()==gid,'Wrong effective gateway identity'
    assert os.access('/opt/athena-stt/venv/bin/python',os.X_OK),'STT interpreter not executable'
    assert os.access('/opt/athena-stt/transcribe.py',os.R_OK),'Runner not readable'
    return {'uid':os.getuid(),'gid':os.getgid(),'groups':os.getgroups()}
def validate_files():
    for name,want in json.loads(Path('/opt/athena-stt/versions.json').read_text()).items():
        assert importlib.metadata.version(name)==want,(name,'dependency version mismatch')
    contract=json.loads(Path('/opt/athena-stt/contract-hashes.json').read_text())
    for rel,want in contract['source_hashes'].items():
        assert hashlib.sha256((Path('/opt/hermes')/rel).read_bytes()).hexdigest()==want,rel
    provenance=json.loads(Path('/fixtures/provenance.json').read_text())
    assert hashlib.sha256(Path('/fixtures/jfk.flac').read_bytes()).hexdigest()==provenance['sha256']
    manifest=Path('/var/cache/athena-stt/model-manifest.json')
    m=json.loads(manifest.read_text())
    assert m['revision']=='ebe41f70d5b6dfa9166e2c581c45c9c0cfc57b66'
    for name,meta in m['files'].items():
        assert '/' not in name and name not in {'.','..'}
        p=Path('/var/cache/athena-stt/base')/name
        assert p.is_file() and os.access(p,os.R_OK),'Model not readable as gateway user'
        h=hashlib.sha256()
        with p.open('rb') as f:
            for block in iter(lambda:f.read(1048576),b''):h.update(block)
        assert h.hexdigest()==meta['sha256'],'Model checksum mismatch'
    return {'fixture_sha256':provenance['sha256'],
            'model_manifest_sha256':hashlib.sha256(manifest.read_bytes()).hexdigest()}
def require_transcript(text):
    normal=' '.join(re.sub(r'[^a-z ]',' ',text.lower()).split())
    expected=json.loads(Path('/fixtures/provenance.json').read_text())['expected_substrings']
    for phrase in expected:assert phrase in normal,'Public fixture recognition mismatch'

if __name__=='__main__':
    who=identity();fingerprints=validate_files();elapsed=[]
    for i in range(2):
        start=time.monotonic()
        subprocess.run([sys.executable,'/opt/athena-stt/transcribe.py','/fixtures/jfk.flac',
                        '--output-dir','/tmp','--language','en'],check=True,timeout=180)
        require_transcript(Path('/tmp/transcript.txt').read_text())
        elapsed.append(round(time.monotonic()-start,3))
    print('ATHENA_TEST_RESULT='+json.dumps({'test':'direct','success':True,
          'identity':who,**fingerprints,'passes':2,'cold_process_seconds':elapsed,
          'note':'Each invocation creates a process and loads the model. Second pass is NOT a warm model run.'}))
