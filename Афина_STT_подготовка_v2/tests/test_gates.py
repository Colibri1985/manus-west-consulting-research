"""Only artificial receipts/files in TemporaryDirectory. NO Docker or gateway calls.
These tests are NOT direct/integration ASR acceptance receipts.
"""
import unittest,tempfile,json,hashlib,importlib.util,sys
from pathlib import Path
from unittest.mock import patch
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('stt_control_under_test',ROOT/'control.py')
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
sha=lambda b:hashlib.sha256(b).hexdigest()

class GateTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
  root=Path(self.temp.name)/'package';root.mkdir();state=Path(self.temp.name)/'state';state.mkdir()
  (root/'build-context').mkdir();(root/'build-context/Dockerfile').write_text('synthetic build input\n')
  (root/'fixtures').mkdir();(root/'fixtures/jfk.flac').write_bytes(b'SYNTHETIC NOT AUDIO')
  manifest={'files':{}}
  for p in root.rglob('*'):
   if p.is_file():manifest['files'][str(p.relative_to(root))]={'sha256':sha(p.read_bytes())}
  (root/'MANIFEST.json').write_text(json.dumps(manifest))
  (state/'preflight.json').write_text('{"unit_test_fixture":true}')
  self.root=root;self.state=state;self.image={'Id':'sha256:SYNTHETIC_IMAGE'}
  config=Path(self.temp.name)/'synthetic-live-config.yaml';config.write_text('synthetic config')
  self.f={'container_id':'SYNTHETIC_CONTAINER','policy':{'identity':{'Uid':[100,100,100,100],'Gid':[200,200,200,200]},'config_sha256':sha(config.read_bytes())},'compose_fingerprints':{}}
  self.patches=patch.multiple(c,ROOT=root,STATE=state,LIVE_CONFIG=config)
  self.patches.start();self.addCleanup(self.patches.stop)
  self.mockfacts=patch.object(c,'facts',return_value=self.f);self.mockfacts.start();self.addCleanup(self.mockfacts.stop)
  self.mockimage=patch.object(c,'image',side_effect=lambda:self.image);self.mockimage.start();self.addCleanup(self.mockimage.stop)
  self.mockmodel=patch.object(c,'model_hash',return_value='SYNTHETIC_MODEL_HASH');self.mockmodel.start();self.addCleanup(self.mockmodel.stop)
  self.mockgateway=patch.object(c,'gateway',return_value={'Image':c.BASE_ID,'Id':'SYNTHETIC_CONTAINER'});self.mockgateway.start();self.addCleanup(self.mockgateway.stop)
  self.mockrun=patch.object(c,'run',side_effect=AssertionError('No process execution permitted in unit tests'));self.mockrun.start();self.addCleanup(self.mockrun.stop)
 def receipts(self):
  _,mh=c.manifest()
  for which in ['direct','integration']:
   d={'test':which,'success':True,'image_id':self.image['Id'],'package_manifest_sha256':mh,
      'build_digest':c.build_digest(),'network_mode':'none','model_manifest_sha256':'SYNTHETIC_MODEL_HASH',
      'preflight_sha256':sha((self.state/'preflight.json').read_bytes()),'identity':{'uid':100,'gid':200}}
   (self.state/(which+'.json')).write_text(json.dumps(d))
 def test_absent_receipts_refused(self):
  with self.assertRaises(FileNotFoundError):c.gate()
 def test_switch_missing_receipts_cannot_modify(self):
  with patch.dict(c.os.environ,{'ATHENA_APPROVE_SWITCH':'YES'}):
   with self.assertRaises(FileNotFoundError):c.switch()
 def test_complete_synthetic_receipts_allowed(self):
  self.receipts();self.assertEqual(c.gate(),self.image['Id'])
 def test_failed_integration_refused(self):
  self.receipts();p=self.state/'integration.json';d=json.loads(p.read_text());d['success']=False;p.write_text(json.dumps(d))
  with self.assertRaises(RuntimeError):c.gate()
 def test_changed_image_refused(self):
  self.receipts();self.image={'Id':'sha256:DIFFERENT_SYNTHETIC_IMAGE'}
  with self.assertRaises(RuntimeError):c.gate()
 def test_changed_build_file_refused(self):
  self.receipts();(self.root/'build-context/Dockerfile').write_text('changed')
  with self.assertRaises(RuntimeError):c.gate()
 def test_changed_model_refused(self):
  self.receipts()
  with patch.object(c,'model_hash',return_value='CHANGED_SYNTHETIC_MODEL'):
   with self.assertRaises(RuntimeError):c.gate()
 def test_changed_preflight_refused(self):
  self.receipts();(self.state/'preflight.json').write_text('changed')
  with self.assertRaises(RuntimeError):c.gate()
 def test_wrong_uid_refused(self):
  self.receipts();self.f['policy']['identity']['Uid'][1]=999
  with self.assertRaises(RuntimeError):c.gate()
 def test_changed_live_config_refused(self):
  self.receipts();c.LIVE_CONFIG.write_text('later edit')
  with self.assertRaises(RuntimeError):c.gate()
 def test_changed_compose_refused(self):
  self.receipts();f=Path(self.temp.name)/'original-compose.yaml';f.write_text('original')
  self.f['compose_fingerprints'][str(f)]='wrong-hash'
  with self.assertRaises(RuntimeError):c.gate()
 def test_model_content_rehashed(self):
  with tempfile.TemporaryDirectory() as tmp:
   cache=Path(tmp);(cache/'base').mkdir();(cache/'base/model.bin').write_bytes(b'SYNTHETIC WEIGHTS')
   d={'revision':'ebe41f70d5b6dfa9166e2c581c45c9c0cfc57b66','files':{'model.bin':{'sha256':sha(b'SYNTHETIC WEIGHTS')}}}
   (cache/'model-manifest.json').write_text(json.dumps(d))
   original=importlib.util.spec_from_file_location('model_hash_original',ROOT/'control.py')
   mod=importlib.util.module_from_spec(original);original.loader.exec_module(mod);mod.CACHE=cache
   self.assertTrue(mod.model_hash())
   (cache/'base/model.bin').write_bytes(b'changed')
   with self.assertRaises(RuntimeError):mod.model_hash()
if __name__=='__main__':unittest.main(verbosity=2)
