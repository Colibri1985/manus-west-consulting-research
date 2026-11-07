#!/usr/bin/env python3
"""Offline read-only verification. Run from unpacked release; needs PyYAML/jsonschema for schema tests."""
from pathlib import Path
import hashlib, json, sys
root=Path(__file__).resolve().parents[1]
errors=[]
for line in (root/'SHA256SUMS.txt').read_text().splitlines():
    expected,relative=line.split(maxsplit=1)
    p=root/relative
    if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=expected: errors.append(relative)
if errors:
    print(json.dumps({'integrity':'FAIL','files':errors}));sys.exit(1)
try:
    import yaml
    from jsonschema import Draft7Validator,RefResolver
except ImportError:
    print(json.dumps({'integrity':'PASS','schema_tests':'NOT_RUN: install PyYAML and jsonschema'}));sys.exit(2)
a=yaml.safe_load((root/'Voice_API_OpenAPI_v3_3.yaml').read_text())
r=RefResolver.from_schema(a)
for f in json.loads((root/'Reports/Schema_Test_Fixtures.json').read_text()):
    actual=not list(Draft7Validator(a['components']['schemas'][f['schema']],resolver=r).iter_errors(f['data']))
    if actual!=f['expected_valid']: errors.append(f['name'])
print(json.dumps({'integrity':'PASS','targeted_schema_tests':'FAIL' if errors else 'PASS','failed':errors,'runtime':'NOT_RUN'}))
sys.exit(bool(errors))
