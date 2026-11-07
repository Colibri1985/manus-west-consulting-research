#!/usr/bin/env python3
"""Read-only aggregate checks; never starts containers or prints rendered secrets."""
import argparse, json, os, pathlib, re, stat, subprocess as sp, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
FILES = {'core':'compose.core.yaml', 'honcho':'compose.honcho.yaml', 'data':'compose.data.planned.yaml', 'team':'compose.team.planned.yaml'}
NETWORKS = ['athena_memory_api', 'athena_team_api', 'athena_catalog_api']
def run(args):
    p = sp.run(args, cwd=ROOT, text=True, capture_output=True)
    if p.returncode:
        raise RuntimeError('Command failed: ' + ' '.join(args[:3]) + '; inspect locally without publishing env/output')
    return p.stdout

def protected(p, root_owned=False):
    p = pathlib.Path(p)
    if p.is_symlink() or not p.is_file(): raise RuntimeError('Missing/non-regular protected file: '+str(p))
    st = p.stat()
    if st.st_mode & 0o077: raise RuntimeError('Protected file must have no group/other access: '+str(p))
    if root_owned and st.st_uid != 0: raise RuntimeError('Root ownership required: '+str(p))
    return p

def settings():
    p = protected(ROOT/'settings.env')
    values = {}
    for line in p.read_text().splitlines():
        line=line.strip()
        if not line or line.startswith('#'): continue
        k,v=line.split('=',1)
        if k in values: raise RuntimeError('Duplicate setting: '+k)
        values[k]=v
    return values

def safe_path(value):
    p=pathlib.Path(value)
    if not p.is_absolute() or '..' in p.parts or not p.is_relative_to('/srv/athena') or p==pathlib.Path('/srv/athena'):
        raise RuntimeError('Path outside approved subtree')
    if any(q.is_symlink() for q in [p,*p.parents]): raise RuntimeError('Symlinks forbidden for managed storage')
    return p

def validate_mount(e):
    p=safe_path(e['HONCHO_DATA_ROOT'])
    expected=e['HONCHO_DATA_UUID']
    if not expected or 'REPLACE' in expected: raise RuntimeError('Expected UUID not configured')
    actual=run(['findmnt','-rn','--mountpoint',str(p),'-o','UUID']).strip()
    if actual != expected: raise RuntimeError('Dedicated filesystem UUID mismatch/missing')

def dc(stage,*args):
    return ['docker','compose','--env-file',str(ROOT/'settings.env'),'-f',str(ROOT/FILES[stage]),*args]

def size(value):
    m=re.fullmatch(r'(\d+(?:\.\d+)?)([bkmg]?)',str(value).lower())
    if not m: raise RuntimeError('Unsupported memory units')
    return int(float(m[1])*{'':1,'b':1,'k':1024,'m':1024**2,'g':1024**3}[m[2]])

def gate(stage, config):
    p=protected(ROOT/'release-gates'/f'{stage}.json',True)
    g=json.loads(p.read_text())
    own='catalog' if stage=='data' else 'team-control'
    if g.get('implemented_and_verified') is not True or g.get('image_digest')!=config['services'][own]['image']:
        raise RuntimeError('Own implementation not accepted for this digest')
    if not g.get('evidence_refs') or not g.get('owner_acceptance_ref'):
        raise RuntimeError('Acceptance evidence missing')

def preflight(stages):
    e=settings()
    if 'honcho' in stages: validate_mount(e)
    manifests={}
    total=0
    for stage in stages:
        env=protected(ROOT/'env'/({'core':'hermes','honcho':'honcho','data':'catalog','team':'team'}[stage]+'.env'))
        active='\n'.join(x for x in env.read_text().splitlines() if not x.lstrip().startswith('#'))
        if 'REPLACE' in active: raise RuntimeError('Unfilled runtime environment: '+stage)
        c=json.loads(run(dc(stage,'config','--format','json')))
        manifests[stage]=c
        if stage in ['data','team']: gate(stage,c)
        for name,s in c['services'].items():
            if not re.fullmatch(r'[^\s]+@sha256:[a-f0-9]{64}',s.get('image','')):
                raise RuntimeError('Image digest missing: '+stage+'/'+name)
            if s.get('privileged') or s.get('network_mode')=='host' or s.get('devices'):
                raise RuntimeError('Forbidden privilege/device/network mode')
            if not s.get('mem_limit') or not s.get('pids_limit') or not s.get('cpus'):
                raise RuntimeError('Missing resource cap')
            total+=size(s['mem_limit'])
            for port in s.get('ports',[]):
                if port.get('host_ip') not in ['127.0.0.1','::1']: raise RuntimeError('Non-loopback port')
            for v in s.get('volumes',[]):
                if 'docker.sock' in v.get('source',''): raise RuntimeError('Docker socket forbidden')
                if v['type']=='bind':
                    p=pathlib.Path(v['source'])
                    if not p.exists() or p.is_symlink(): raise RuntimeError('Missing/unsafe bind path')
                    if v.get('bind',{}).get('create_host_path') is not False: raise RuntimeError('Auto-created bind forbidden')
            for sec in s.get('secrets',[]):
                p=pathlib.Path(c['secrets'][sec['source']]['file'])
                protected(p)
                v=p.read_text().strip()
                if not v or 'REPLACE' in v: raise RuntimeError('Empty/unfilled secret')
        for v in c.get('volumes',{}).values():
            if not v.get('external'): continue
            n=json.loads(run(['docker','volume','inspect',v['name']]))[0]
            expected={'athena_honcho_pgdata':e['HONCHO_DATA_ROOT']+'/postgres','athena_honcho_redisdata':e['HONCHO_DATA_ROOT']+'/redis','athena_team_pgdata':e['TEAM_PGDATA']}[v['name']]
            if n.get('Driver')!='local' or n.get('Options')!={'type':'none','o':'bind','device':expected}:
                raise RuntimeError('External volume driver/options mismatch')
    if 'core' in stages:
        p=pathlib.Path(e['HERMES_HOME_HOST'])/'config.yaml'
        if not p.is_file() or 'REPLACE' in p.read_text(): raise RuntimeError('Native Hermes config not prepared')
    for name in NETWORKS:
        n=json.loads(run(['docker','network','inspect',name]))[0]
        if n.get('Driver')!='bridge' or n.get('Internal') is not True: raise RuntimeError('API network not internal bridge')
    selected_projects={c['name'] for c in manifests.values()}
    ids=run(['docker','ps','-q']).split()
    if ids:
        running=json.loads(run(['docker','inspect',*ids]))
        for c in running:
            project=(c['Config'].get('Labels') or {}).get('com.docker.compose.project','')
            if project.startswith('athena-') and project not in selected_projects:
                raise RuntimeError('Include every active Athena project in the aggregate preflight')
    reserve=float(e['HOST_RESERVE_GIB'])
    other=float(e['OTHER_WORKLOAD_GIB'])
    if reserve<2 or other<0: raise RuntimeError('Invalid host/other-workload reserve')
    physical=int(next(x.split()[1] for x in pathlib.Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemTotal:')))*1024
    required=total+(reserve+other)*1024**3
    if required>physical: raise RuntimeError('Aggregate caps + host + other workloads exceed physical RAM')
    print(json.dumps({'stages':stages,'container_caps_GiB':total/1024**3,'required_GiB':required/1024**3,'status':'STATIC_PASS','not_proven':['compatibility','auth','isolation','migrations','restore','business readiness']}))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stages',nargs='+',choices=list(FILES));a=p.parse_args()
    try: preflight(list(dict.fromkeys(a.stages)))
    except Exception as exc: print('BLOCKED: '+str(exc),file=sys.stderr);sys.exit(1)
