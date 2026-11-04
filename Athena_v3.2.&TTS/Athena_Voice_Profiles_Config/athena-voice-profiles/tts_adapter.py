#!/usr/bin/env python3
"""Minimal whole-file TTS adapter; stdlib only. No automatic retries or streaming.
Reads explicitly passed-through secrets. Never prints request text/error body/token.
"""
import argparse, json, os, pathlib, sys, tempfile, urllib.request, urllib.error

FISH_MODELS={"s1","s2-pro","s2.1-pro","s2.1-pro-free","drama-3"}
OPENROUTER_MODELS={"elevenlabs/eleven-v4-turbo"}
MAX_AUDIO=32*1024*1024
class SafeError(RuntimeError): pass

def validate(backend,model,voice,text,env):
    if env.get("ATHENA_PAID_TTS_ENABLED","").lower()!="true":
        raise SafeError("PAID_TTS_DISABLED")
    if not voice.strip() or "REPLACE" in voice: raise SafeError("VOICE_NOT_CONFIGURED")
    allowed=OPENROUTER_MODELS if backend=="openrouter" else FISH_MODELS
    if model not in allowed: raise SafeError("MODEL_NOT_APPROVED")
    try: cap=int(env.get("ATHENA_TTS_MAX_INPUT_CHARS","4000"))
    except ValueError: raise SafeError("INVALID_TEXT_CAP")
    if cap<1 or cap>4000: raise SafeError("INVALID_TEXT_CAP")
    if not text.strip(): raise SafeError("EMPTY_TEXT")
    if len(text)>cap: raise SafeError("TEXT_TOO_LONG")
    key=env.get("OPENROUTER_TTS_API_KEY" if backend=="openrouter" else "FISH_TTS_API_KEY","")
    if not key.strip(): raise SafeError("KEY_NOT_CONFIGURED")
    return key

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        raise SafeError("PROVIDER_REDIRECT_REJECTED")

def synthesize(backend,model,voice,text,output,env):
    key=validate(backend,model,voice,text,env)
    headers={"Authorization":"Bearer "+key,"Content-Type":"application/json","Accept":"audio/mpeg"}
    if backend=="openrouter":
        url="https://openrouter.ai/api/v1/audio/speech"
        body={"model":model,"input":text,"voice":voice,"response_format":"mp3"}
    else:
        url="https://api.fish.audio/v1/tts"
        headers["model"]=model
        body={"text":text,"reference_id":voice,"format":"mp3"}
    req=urllib.request.Request(url,data=json.dumps(body,ensure_ascii=False).encode(),headers=headers)
    target=pathlib.Path(output)
    if not target.parent.is_dir(): raise SafeError("OUTPUT_DIRECTORY_MISSING")
    temp=None
    try:
        opener=urllib.request.build_opener(NoRedirect())
        try:
            response=opener.open(req,timeout=60)
        except urllib.error.HTTPError as exc:
            raise SafeError("PROVIDER_HTTP_"+str(exc.code)) from None
        except (urllib.error.URLError,TimeoutError):
            raise SafeError("PROVIDER_NETWORK_OR_TIMEOUT_UNKNOWN_CHARGE") from None
        with response:
            if response.status!=200: raise SafeError("UNEXPECTED_HTTP_STATUS")
            mime=response.headers.get_content_type()
            if mime not in {"audio/mpeg","audio/mp3","application/octet-stream"}:
                raise SafeError("UNEXPECTED_CONTENT_TYPE")
            with tempfile.NamedTemporaryFile(dir=target.parent,prefix=".athena-tts-",suffix=".partial",delete=False) as fp:
                temp=pathlib.Path(fp.name);total=0
                while True:
                    chunk=response.read(65536)
                    if not chunk: break
                    total+=len(chunk)
                    if total>MAX_AUDIO: raise SafeError("AUDIO_LIMIT_EXCEEDED")
                    fp.write(chunk)
                fp.flush();os.fsync(fp.fileno())
        if total==0: raise SafeError("EMPTY_AUDIO")
        # Codec/container validity is an integration/ffprobe gate, not inferred from extension.
        os.replace(temp,target);temp=None
    finally:
        if temp is not None:
            try:temp.unlink()
            except FileNotFoundError:pass
    return str(target)

def main():
    p=argparse.ArgumentParser();p.add_argument("--backend",choices=["openrouter","fish"],required=True)
    p.add_argument("--input",required=True);p.add_argument("--output",required=True)
    p.add_argument("--model",required=True);p.add_argument("--voice",required=True);a=p.parse_args()
    input_file=pathlib.Path(a.input)
    if input_file.stat().st_size>20000: raise SafeError("INPUT_BYTES_EXCEEDED")
    text=input_file.read_text(encoding="utf-8")
    print(synthesize(a.backend,a.model,a.voice,text,a.output,os.environ))
if __name__=="__main__":
    os.umask(0o077)
    try:main()
    except SafeError as exc:print("TTS_ERROR:"+str(exc),file=sys.stderr);sys.exit(1)
    except Exception:print("TTS_ERROR:LOCAL_OR_RESPONSE_FAILURE",file=sys.stderr);sys.exit(1)
