#!/usr/bin/env python3
import argparse,json,pathlib,urllib.request,urllib.error
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs): return None
p=argparse.ArgumentParser();p.add_argument('--base-url',required=True);p.add_argument('--token-file',required=True);p.add_argument('--kind',choices=['hermes','honcho'],required=True);a=p.parse_args()
u=urllib.parse.urlsplit(a.base_url)
if u.scheme!='http' or u.hostname not in ['127.0.0.1','localhost','::1'] or u.username or u.password or u.query or u.fragment:
    raise SystemExit('Only local HTTP via trusted SSH tunnel is accepted')
token=pathlib.Path(a.token_file).read_text().strip()
if not token or '\n' in token: raise SystemExit('Invalid token file')
opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),NoRedirect())
def get(path,auth=True):
    req=urllib.request.Request(a.base_url.rstrip('/')+path,headers={'Authorization':'Bearer '+token} if auth else {})
    try:
        with opener.open(req,timeout=10) as r:
            data=r.read(1024*1024+1)
            if len(data)>1024*1024: raise SystemExit('Response too large')
            return r.status,data
    except urllib.error.HTTPError as e: return e.code,b''
def expect(path,statuses,auth=True,as_json=False):
    status,body=get(path,auth)
    if status not in statuses: raise SystemExit('BLOCKED: unexpected status for '+path+': '+str(status))
    return json.loads(body) if as_json else None
expect('/health',[200],False)
if a.kind=='hermes':
    expect('/v1/capabilities',[401,403],False)
    expect('/v1/capabilities',[200],True,True)
    result=expect('/health/detailed',[200],True,True)
    if result.get('status') not in ['ok','healthy','ready']: raise SystemExit('BLOCKED: unknown detailed-health schema/status')
else:
    expect('/v3/workspaces',[401,403],False)
    expect('/v3/workspaces',[200],True,True)
print('PASS passive HTTP only; pin schemas and run functional gates separately')
