"""Local-only command adapter. No network, no dependency install, no transcript on stdout."""
import os,sys,argparse
from pathlib import Path
os.environ['HF_HUB_OFFLINE']='1'
os.environ['HF_HUB_DISABLE_TELEMETRY']='1'
os.environ['HF_HUB_DISABLE_XET']='1'
os.environ['TOKENIZERS_PARALLELISM']='false'
def no_network(event,args):
    if event in {'socket.connect','socket.getaddrinfo'}:
        raise RuntimeError('Network forbidden in STT inference')
sys.addaudithook(no_network)
from faster_whisper import WhisperModel

def transcribe(audio,language):
    model=WhisperModel('/var/cache/athena-stt/base',device='cpu',compute_type='int8',
                       cpu_threads=2,num_workers=1,local_files_only=True)
    segments,info=model.transcribe(str(audio),language=language,beam_size=5,
                                   vad_filter=True,condition_on_previous_text=False)
    text=' '.join(s.text.strip() for s in segments).strip()
    if not text:raise RuntimeError('No speech recognized')
    return text,info
if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('audio',type=Path)
    p.add_argument('--output-dir',required=True,type=Path)
    p.add_argument('--language',default='ru')
    a=p.parse_args()
    if not a.audio.is_file():raise SystemExit('Input file missing')
    if a.language not in {'ru','en'}:raise SystemExit('Only ru/en accepted by this adapter')
    text,_=transcribe(a.audio,a.language)
    out=a.output_dir
    if not out.is_dir():raise SystemExit('Output directory must already exist')
    (out/'transcript.txt').write_text(text,encoding='utf-8')
