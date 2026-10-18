"""Execute exact pinned function AST with isolated helper doubles.
Contract unit tests only; NOT real Hermes import/inference or ASR acceptance.
"""
import ast,sys,os,types,shlex,tempfile,subprocess,logging,unittest
from pathlib import Path
from typing import Optional,Dict,Any
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
text=(ROOT/'evidence/base-image/tools/transcription_local.py').read_text()
node=next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef) and n.name=='_transcribe_local_command')
function_module=ast.Module(body=[node],type_ignores=[])

class ContractTests(unittest.TestCase):
 def setUp(self):
  modules={name:types.ModuleType(name) for name in ['tools','tools.transcription_tools','tools.environments','tools.environments.local']}
  modules['tools.transcription_tools']._resolve_stt_language=lambda name:'en'
  modules['tools.environments.local'].hermes_subprocess_env=lambda **kw:{'SYNTHETIC_ENV':'no credentials'}
  self.p=patch.dict(sys.modules,modules);self.p.start();self.addCleanup(self.p.stop)
  self.env=patch.dict(os.environ,{'HERMES_LOCAL_STT_COMMAND':'python {input_path} {output_dir} {language} {model}'})
  self.env.start();self.addCleanup(self.env.stop)
  self.calls=[]
  self.ns={'Optional':Optional,'Dict':Dict,'Any':Any,'os':os,'shlex':shlex,'tempfile':tempfile,
      'Path':Path,'subprocess':subprocess,'logger':logging.getLogger('contract-unit'),
      'LOCAL_STT_COMMAND_ENV':'HERMES_LOCAL_STT_COMMAND','DEFAULT_LOCAL_STT_LANGUAGE':'en',
      '_get_local_command_template':lambda:os.environ['HERMES_LOCAL_STT_COMMAND'],
      '_normalize_local_stt_language':lambda x:x,'_normalize_local_model':lambda x:x,
      '_log_prompt_unsupported':lambda *a:None,'_prepare_local_audio':lambda a,b:(a,None),
      '_error_result':lambda message:{'success':False,'error':message},
      '_ok_result':lambda text,provider:{'success':True,'transcript':text,'provider':provider},
      '_process_error_detail':lambda e:'injected exit '+str(e.returncode)}
  exec(compile(function_module,'<exact pinned local_command AST>','exec'),self.ns)
 def invoke(self,runner):
  self.ns['_run_quiet']=runner
  return self.ns['_transcribe_local_command']('/tmp/name with spaces.wav','base')
 def test_placeholders_txt_and_timeout_argument(self):
  def runner(args,**kw):
   self.calls.append((args,kw));self.assertEqual(args[1],'/tmp/name with spaces.wav')
   self.assertEqual(args[3:],[ 'en','base']);self.assertEqual(kw['timeout'],300)
   (Path(args[2])/'z.txt').write_text('second')
   (Path(args[2])/'a.txt').write_text('\ufeff first transcript \n',encoding='utf-8')
  r=self.invoke(runner);self.assertTrue(r['success']);self.assertEqual(r['transcript'],'first transcript')
  self.assertEqual(r['provider'],'local_command')
 def test_stdout_without_txt_is_not_accepted(self):
  r=self.invoke(lambda *a,**k:subprocess.CompletedProcess(a[0],0,stdout='not a txt file'))
  self.assertFalse(r['success']);self.assertIn('did not produce a .txt',r['error'])
 def test_exit_error(self):
  def runner(*a,**kw):raise subprocess.CalledProcessError(7,a[0])
  r=self.invoke(runner);self.assertFalse(r['success']);self.assertIn('Local STT failed',r['error'])
 def test_timeout_error(self):
  def runner(*a,**kw):raise subprocess.TimeoutExpired(a[0],300)
  r=self.invoke(runner);self.assertFalse(r['success']);self.assertIn('Local transcription failed',r['error'])
 def test_bad_placeholder(self):
  os.environ['HERMES_LOCAL_STT_COMMAND']='python {unknown}'
  r=self.invoke(lambda *a,**k:self.fail('Should not execute'))
  self.assertFalse(r['success']);self.assertIn('missing placeholder',r['error'])
if __name__=='__main__':unittest.main(verbosity=2)
