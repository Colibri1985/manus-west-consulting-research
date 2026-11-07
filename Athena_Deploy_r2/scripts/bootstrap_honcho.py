#!/usr/bin/env python3
import os, pathlib, sys
from urllib.parse import quote

def read(name):
    value = pathlib.Path('/run/secrets', name).read_text().strip()
    if not value or 'REPLACE' in value:
        raise SystemExit('Unconfigured secret: ' + name)
    return value

def main():
    os.environ['DB_CONNECTION_URI'] = 'postgresql+psycopg://honcho:' + quote(read('honcho_db_password'), safe='') + '@database:5432/honcho'
    os.environ['CACHE_URL'] = 'redis://redis:6379/0?suppress=true'
    os.environ['AUTH_JWT_SECRET'] = read('honcho_jwt_secret')
    os.environ['LLM_OPENAI_API_KEY'] = read('honcho_openrouter_key')
    os.environ['PYTHON_DOTENV_DISABLED'] = '1'
    os.environ['HONCHO_CONFIG_TOML_DISABLED'] = '1'
    os.chdir('/app')
    mode = sys.argv[1] if len(sys.argv) == 2 else ''
    if mode == 'api':
        os.execvp('sh', ['sh', 'docker/entrypoint.sh'])
    if mode == 'deriver':
        os.execv('/app/.venv/bin/python', ['/app/.venv/bin/python', '-m', 'src.deriver'])
    raise SystemExit('Use api or deriver')

if __name__ == '__main__':
    main()
