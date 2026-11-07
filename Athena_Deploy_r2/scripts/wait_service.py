#!/usr/bin/env python3
import argparse,json,subprocess as sp,time
from preflight import dc
p=argparse.ArgumentParser();p.add_argument('stage',choices=['core','honcho','data','team']);p.add_argument('service');p.add_argument('--timeout',type=int,default=300);a=p.parse_args()
end=time.monotonic()+a.timeout
while time.monotonic()<end:
    q=sp.run(dc(a.stage,'ps','-q',a.service),capture_output=True,text=True)
    ids=q.stdout.split()
    if q.returncode or len(ids)!=1: time.sleep(2);continue
    s=json.loads(sp.check_output(['docker','inspect',ids[0]],text=True))[0]['State']
    if s.get('Status') in ['exited','dead']: raise SystemExit('BLOCKED: process exited')
    h=s.get('Health',{}).get('Status')
    if h=='healthy': print('PASS container health only');raise SystemExit(0)
    if h is None: raise SystemExit('BLOCKED: service has no native healthcheck; use functional gate, not fake HTTP')
    time.sleep(2)
raise SystemExit('BLOCKED: health timeout')
