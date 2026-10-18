# Executes ONLY in a separately approved download container without any audio mount.
import os,json,hashlib
from pathlib import Path
os.environ['HF_HUB_DISABLE_TELEMETRY']='1'
os.environ['HF_HUB_DISABLE_XET']='1'
from huggingface_hub import snapshot_download
root=Path('/var/cache/athena-stt')
model=root/'base'
path=snapshot_download('Systran/faster-whisper-base',revision='ebe41f70d5b6dfa9166e2c581c45c9c0cfc57b66',
    local_dir=str(model),allow_patterns=['config.json','model.bin','tokenizer.json','vocabulary.txt'])
files={}
for name in ['config.json','model.bin','tokenizer.json','vocabulary.txt']:
    p=model/name
    if not p.is_file():raise RuntimeError('Required model file missing: '+name)
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(1048576),b''):h.update(chunk)
    files[name]={'bytes':p.stat().st_size,'sha256':h.hexdigest()}
manifest={'repo':'Systran/faster-whisper-base','revision':'ebe41f70d5b6dfa9166e2c581c45c9c0cfc57b66', 'files':files,
          'uid':os.getuid(),'gid':os.getgid()}
(root/'model-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps(manifest,indent=2))
