"""Actual transaction code, but hardcoded live path replaced by an artificial temp file."""
import os,sys,tempfile,unittest,contextlib,io
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]

class TransactionTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  self.config=Path(self.tmp.name)/'config.yaml';self.backup=Path(self.tmp.name)/'backup'
  self.original=b'project: synthetic\nsecurity:\n  allow_lazy_installs: false\nstt:\n  enabled: true\nweb:\n  backend: openai-native\n'
  self.config.write_bytes(self.original)
  self.source=(ROOT/'config_transaction.py').read_text().replace("Path('/srv/hermes-agent/telegram-data/config.yaml')",'Path('+repr(str(self.config))+')')
 def action(self,name):
  with patch.dict(os.environ,{'ATHENA_APPROVE_SWITCH':'YES'}),patch.object(sys,'argv',['test',name,'--backup',str(self.backup)]),contextlib.redirect_stdout(io.StringIO()):
   exec(compile(self.source,'<isolated actual transaction code>','exec'),{'__name__':'__main__','__file__':str(ROOT/'config_transaction.py')})
 def test_apply_restore_exact_bytes(self):
  self.action('apply');new=self.config.read_bytes()
  self.assertIn(b'provider: local_command',new)
  self.assertIn(b'allow_lazy_installs: false',new)
  self.assertTrue(new.endswith(b'web:\n  backend: openai-native\n'))
  self.action('restore');self.assertEqual(self.config.read_bytes(),self.original)
 def test_restore_refuses_later_edits(self):
  self.action('apply');changed=self.config.read_bytes()+b'later: preserved\n';self.config.write_bytes(changed)
  with self.assertRaises(SystemExit):self.action('restore')
  self.assertEqual(self.config.read_bytes(),changed)
 def test_repeat_restore_after_partial_rollback(self):
  self.action('apply');self.action('restore')
  with self.assertRaises(SystemExit) as e:self.action('restore')
  self.assertEqual(e.exception.code,0);self.assertEqual(self.config.read_bytes(),self.original)
if __name__=='__main__':unittest.main(verbosity=2)
