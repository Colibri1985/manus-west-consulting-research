#!/usr/bin/env python3
import argparse, json, os, subprocess as sp
from preflight import settings, validate_mount, safe_path, run, NETWORKS

def main():
    p=argparse.ArgumentParser();p.add_argument('--apply',action='store_true');p.add_argument('--independent-backup-confirmed',action='store_true');a=p.parse_args()
    if not (a.apply and a.independent_backup_confirmed and os.geteuid()==0):
        raise SystemExit('BLOCKED: approved root operation with both explicit flags required')
    e=settings();validate_mount(e)
    keys=['HERMES_HOME_HOST','EXECUTOR_INPUTS','EXECUTOR_WORK','EXECUTOR_HOME','WAREHOUSE_ROOT','CATALOG_STATE','TEAM_STATE','TEAM_WORK','TEAM_PGDATA','GOVERNANCE_ROOT']
    for key in keys: safe_path(e[key]).mkdir(parents=True,exist_ok=True)
    for suffix in ['postgres','redis']: safe_path(e['HONCHO_DATA_ROOT']+'/'+suffix).mkdir(exist_ok=True)
    for name in NETWORKS:
        probe=sp.run(['docker','network','inspect',name],text=True,capture_output=True)
        if probe.returncode==0:
            n=json.loads(probe.stdout)[0]
            if n.get('Driver')!='bridge' or n.get('Internal') is not True: raise SystemExit('BLOCKED: network policy mismatch')
        else: run(['docker','network','create','--internal','--label','athena.managed=true',name])
    targets={'athena_honcho_pgdata':e['HONCHO_DATA_ROOT']+'/postgres','athena_honcho_redisdata':e['HONCHO_DATA_ROOT']+'/redis','athena_team_pgdata':e['TEAM_PGDATA']}
    for name,path in targets.items():
        expected={'type':'none','o':'bind','device':path}
        probe=sp.run(['docker','volume','inspect',name],text=True,capture_output=True)
        if probe.returncode==0:
            n=json.loads(probe.stdout)[0]
            if n.get('Driver')!='local' or n.get('Options')!=expected: raise SystemExit('BLOCKED: manual volume migration required')
        else: run(['docker','volume','create','--driver','local','--opt','type=none','--opt','o=bind','--opt','device='+path,name])
    print('PREPARED; no services started, no ownership rewritten, no disk formatted')
if __name__=='__main__': main()
