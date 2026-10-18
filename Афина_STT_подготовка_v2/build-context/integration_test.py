"""Run with HERMES Python from the approved image, not the isolated STT Python.
Real Hermes functions perform routing, argument rendering, subprocess and txt reading.
Only configuration input is synthetic; no live config, secret stores or Telegram.
"""
import os,sys,json,hashlib,re,subprocess,importlib.util
from pathlib import Path
sys.path.insert(0,'/opt/hermes');sys.path.insert(0,'/opt/athena-stt')
# Test utilities use stdlib only; version checks belong to direct STT test.
from selftest import identity,require_transcript
who=identity()
contract=json.loads(Path('/opt/athena-stt/contract-hashes.json').read_text())
for rel,want in contract['source_hashes'].items():
    assert hashlib.sha256((Path('/opt/hermes')/rel).read_bytes()).hexdigest()==want,rel
fixture_sha=hashlib.sha256(Path('/fixtures/jfk.flac').read_bytes()).hexdigest()
assert fixture_sha==json.loads(Path('/fixtures/provenance.json').read_text())['sha256']
assert os.environ['HERMES_DISABLE_LAZY_INSTALLS']=='1','No lazy installs allowed in test'
# Deny Python-level network as an extra alarm; Docker --network none is primary boundary.
def network_alarm(event,args):
    if event in {'socket.connect','socket.getaddrinfo'}:raise RuntimeError('Network attempt in offline integration test')
sys.addaudithook(network_alarm)
from tools import transcription_tools as stt
from tools import transcription_local as local
# In-memory fixture config: no modifications to installed code/config files.
cfg={'enabled':True,'provider':'local_command','language':'en','local':{'model':'base','language':'en'}}
stt._load_stt_config=lambda:cfg
command='/opt/athena-stt/venv/bin/python /opt/athena-stt/transcribe.py {input_path} --output-dir {output_dir} --language {language}'
os.environ['HERMES_LOCAL_STT_COMMAND']=command
assert stt._get_provider(cfg)=='local_command'
# Actual public Hermes API -> dispatch -> built-in local_command -> real STT subprocess.
result=stt.transcribe_audio('/fixtures/jfk.flac',source='athena-offline-acceptance')
assert result.get('success') is True,result.get('error','Hermes failed')
assert result.get('provider')=='local_command',result.get('provider')
require_transcript(result.get('transcript',''))
checks=['actual_public_api_routing','real_speech_transcription','actual_txt_output_read']
# Real subprocess failures: no fake transcript accepted from stdout.
script=Path('/tmp/stt-negative.py')
script.write_text('import sys\nprint("stdout is NOT a transcript file")\nsys.exit(0)\n')
os.environ['HERMES_LOCAL_STT_COMMAND']='/opt/hermes/.venv/bin/python /tmp/stt-negative.py {input_path}'
r=stt.transcribe_audio('/fixtures/jfk.flac',source='athena-negative-output')
assert r.get('success') is False and 'did not produce a .txt' in r.get('error','')
checks.append('stdout_without_txt_rejected')
script.write_text('import sys\nsys.exit(7)\n')
r=stt.transcribe_audio('/fixtures/jfk.flac',source='athena-negative-exit')
assert r.get('success') is False and 'Local STT failed' in r.get('error','')
checks.append('nonzero_subprocess_rejected')
os.environ['HERMES_LOCAL_STT_COMMAND']='anything {missing_placeholder}'
r=stt.transcribe_audio('/fixtures/jfk.flac',source='athena-negative-template')
assert r.get('success') is False and 'missing placeholder' in r.get('error','')
checks.append('invalid_placeholder_rejected')
# Inject TimeoutExpired into original helper boundary; do NOT wait 300 seconds.
from unittest.mock import patch
os.environ['HERMES_LOCAL_STT_COMMAND']=command
with patch.object(local,'_run_quiet',side_effect=subprocess.TimeoutExpired(['test'],300)) as call:
    r=stt.transcribe_audio('/fixtures/jfk.flac',source='athena-negative-timeout')
    assert r.get('success') is False and 'Local transcription failed' in r.get('error','')
    assert call.call_args.kwargs['timeout']==300
checks.append('timeout_300_forwarded_and_injected_exception_handled')
print('ATHENA_TEST_RESULT='+json.dumps({'test':'integration','success':True,'identity':who,
      'fixture_sha256':fixture_sha,
      'model_manifest_sha256':hashlib.sha256(Path('/var/cache/athena-stt/model-manifest.json').read_bytes()).hexdigest(),
      'checks':checks,'config':'synthetic in memory; no live profile/Telegram',
      'timeout_test':'injected exception, not elapsed timeout measurement'}))
