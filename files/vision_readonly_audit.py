#!/usr/bin/env python3
"""Read-only vision inventory. Run on the Docker host, not the SSH executor.
No config edits, restarts, installs, API/model calls, auth reads or image uploads.
Only allowlisted metadata is printed. Raw Docker inspect and errors stay private.
"""
import argparse
import datetime
import json
import re
import shutil
import subprocess

GATEWAY = 'hermes-telegram-gateway-1'
CHILD = r'''
import ast, hashlib, json, os, re
from pathlib import Path

def identifier(value):
    if not isinstance(value, str): return None
    if value.lower().startswith(('sk-', 'bearer ', 'token', 'password')): return '<omitted>'
    return value if re.fullmatch(r'[A-Za-z0-9_.:/@+ -]{1,120}', value) and '://' not in value else '<omitted>'

def ids(value):
    return [identifier(x) for x in value] if isinstance(value, list) else None

def summarize_config(cfg):
    def mapping(value): return value if isinstance(value, dict) else {}
    agent = mapping(cfg.get('agent'))
    auxiliary = mapping(mapping(cfg.get('auxiliary')).get('vision'))
    model = cfg.get('model')
    model_info = {k: identifier(model.get(k)) for k in ('default', 'name', 'provider') if k in model} if isinstance(model, dict) else {'name': identifier(model)}
    return {
        'telegram_toolsets_explicit': ids(mapping(cfg.get('platform_toolsets')).get('telegram')),
        'global_toolsets_explicit': ids(cfg.get('toolsets')),
        'disabled_toolsets_explicit': ids(agent.get('disabled_toolsets')),
        'image_input_mode_explicit': identifier(agent.get('image_input_mode')),
        'model_explicit': model_info,
        'auxiliary_vision': {
            'section_present': bool(auxiliary),
            'provider': identifier(auxiliary.get('provider')),
            'model': identifier(auxiliary.get('model')),
            'base_url_present': bool(auxiliary.get('base_url')),
            'api_key_present': bool(auxiliary.get('api_key')),
        },
    }

def read_static_toolsets(path):
    out = {'source_exists': path.is_file(), 'method': 'AST only; toolset code not executed'}
    if not path.is_file(): return out
    raw = path.read_bytes(); tree = ast.parse(raw.decode())
    out['sha256'] = hashlib.sha256(raw).hexdigest()
    definitions = {}
    for node in tree.body:
        targets = node.targets if isinstance(node, ast.Assign) else [node.target] if isinstance(node, ast.AnnAssign) else []
        if not any(isinstance(t, ast.Name) and t.id == 'TOOLSETS' for t in targets): continue
        if not isinstance(node.value, ast.Dict): continue
        for key, value in zip(node.value.keys, node.value.values):
            if not isinstance(key, ast.Constant) or not isinstance(key.value, str) or not isinstance(value, ast.Dict): continue
            fields = {}
            for field, expr in zip(value.keys, value.values):
                if not isinstance(field, ast.Constant) or field.value not in ('tools', 'includes'): continue
                try: fields[field.value] = ids(ast.literal_eval(expr))
                except (ValueError, TypeError): fields[field.value] = None
            definitions[key.value] = fields
    out['definitions_found'] = bool(definitions)
    out['vision_and_bundles'] = {k: definitions.get(k) for k in ('vision', 'no_mcp', 'hermes', 'all', 'safe', 'debugging')}
    out['warning'] = 'Static entries do not prove live tool availability; dynamic registry and check functions not executed.'
    return out

def collect():
    from hermes_constants import get_hermes_home
    import hermes_yaml
    home = get_hermes_home()
    cfg = hermes_yaml.safe_load((home / 'config.yaml').read_text()) or {}
    if not isinstance(cfg, dict): raise TypeError('Unexpected configuration')
    root = Path('/opt/hermes')
    result = {
        'home': str(home), 'uid': os.getuid(), 'gid': os.getgid(),
        'configuration': summarize_config(cfg),
        'static_toolsets': read_static_toolsets(root / 'toolsets.py'),
        'credential_environment_presence_only': {name: bool(os.environ.get(name)) for name in (
            'OPENROUTER_API_KEY', 'GOOGLE_API_KEY', 'OPENAI_API_KEY', 'ANTHROPIC_API_KEY')},
        'vision_source_metadata': [],
        'not_tested': ['live-session schema', 'effective managed/env/runtime overrides', 'credential validity',
                       'native image support of current endpoint', 'auxiliary model calls', 'actual image recognition'],
    }
    # Do not read .env/auth.json or call tool availability checks: those can resolve credentials.
    tools = root / 'tools'
    for path in sorted(tools.glob('*vision*.py')) if tools.is_dir() else []:
        raw = path.read_bytes(); tree = ast.parse(raw.decode())
        names = [n.name for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        result['vision_source_metadata'].append({'path': str(path), 'sha256': hashlib.sha256(raw).hexdigest(),
            'functions': [identifier(name) for name in names], 'source_imported_or_executed': False})
    return result

if __name__ == '__main__':
    try: result = collect()
    except Exception as exc: result = {'inspection_error_type': type(exc).__name__}
    print('VISION_AUDIT_JSON:' + json.dumps(result, ensure_ascii=False))
'''


def run_host():
    result = {'mode': 'read_only', 'observed_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'config_changed': False, 'services_restarted': False, 'model_calls_made': False}
    if not shutil.which('docker'):
        result['blocker'] = 'Docker CLI unavailable here; run on the Docker host.'
        return result, 2
    try:
        p = subprocess.run(['docker', 'inspect', GATEWAY], capture_output=True, text=True, timeout=20)
        if p.returncode:
            result['blocker'] = 'Container inspect failed; raw output withheld.'
            return result, 2
        data = json.loads(p.stdout)[0]
        result['gateway'] = {'name': GATEWAY, 'running': data.get('State', {}).get('Running'),
                             'image_id': data.get('Image'), 'container_id': data.get('Id')}
        if result['gateway']['running'] is not True:
            result['blocker'] = 'Gateway is not running; no start or restart attempted.'
            return result, 2
        p = subprocess.run(['docker', 'exec', '-i', GATEWAY, 'python', '-B', '-'],
                           input=CHILD, capture_output=True, text=True, timeout=60)
        prefix = 'VISION_AUDIT_JSON:'
        records = [line[len(prefix):] for line in p.stdout.splitlines() if line.startswith(prefix)]
        if p.returncode or len(records) != 1:
            result['blocker'] = 'Read-only child failed; raw output withheld.'
            return result, 2
        result['gateway_readonly_audit'] = json.loads(records[0])
        return result, 2 if 'inspection_error_type' in result['gateway_readonly_audit'] else 0
    except Exception as exc:
        result['inspection_error_type'] = type(exc).__name__
        return result, 2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    result, status = run_host()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(status)


if __name__ == '__main__':
    main()
