import importlib.util,pathlib,sys,unittest,io,contextlib,stat
from unittest.mock import patch
sys.dont_write_bytecode=True
ROOT=pathlib.Path(__file__).resolve().parents[2];spec=importlib.util.spec_from_file_location('fake_capture',ROOT/'host_tests/capture/capture_linux.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
CODES={v:k for k,v in m.KEYS.items()}
class CaptureTests(unittest.TestCase):
 def test_exact_phrase(self):
  d=m.Detector()
  for c in m.PHRASE:d.key(CODES[c])
  self.assertTrue(d.found);self.assertEqual(d.result(),m.PHRASE)
 def test_other_text_not_retained(self):
  d=m.Detector()
  for code in [18,47,99,100,37,20]:d.key(code)
  self.assertFalse(d.found);self.assertEqual(d.result(),'');self.assertEqual(set(d.__dict__),{'matched','found'})
 def test_partial(self):
  d=m.Detector()
  for c in m.PHRASE[:-1]:d.key(CODES[c])
  self.assertEqual(d.result(),'')
 def test_repeat_release(self):
  d=m.Detector();d.key(18,0);d.key(18,2);self.assertEqual(d.matched,0)
 def test_noise_then_phrase(self):
  d=m.Detector()
  for code in [18,47,999]+[CODES[c] for c in m.PHRASE]:d.key(code)
  self.assertTrue(d.found)
 def test_fixed_result_only(self):
  d=m.Detector()
  for c in m.PHRASE:d.key(CODES[c])
  for code in range(200):d.key(code)
  self.assertEqual(d.result(),m.PHRASE)
 def test_wrong_device_path(self):
  with patch.object(sys,'argv',['test','/tmp/not-a-device']),patch('builtins.input',return_value='START'),patch.object(m.os,'open') as opened,contextlib.redirect_stdout(io.StringIO()):self.assertEqual(m.main(),2);opened.assert_not_called()
 def test_no_start_no_device(self):
  with patch.object(sys,'argv',['test','/dev/input/event0']),patch('builtins.input',return_value='NO'),patch.object(m.os,'open') as opened,contextlib.redirect_stdout(io.StringIO()):self.assertEqual(m.main(),2);opened.assert_not_called()
 def test_permission_denial(self):
  with patch.object(sys,'argv',['test','/dev/input/event0']),patch('builtins.input',return_value='START'),patch.object(m.os,'open',side_effect=PermissionError),contextlib.redirect_stdout(io.StringIO()):self.assertEqual(m.main(),3)
 def test_metadata_failure_closes_fd(self):
  with patch.object(sys,'argv',['test','/dev/input/event0']),patch('builtins.input',return_value='START'),patch.object(m.os,'open',return_value=91),patch.object(m.os,'fstat',side_effect=OSError),patch.object(m.os,'close') as closed,contextlib.redirect_stdout(io.StringIO()):self.assertEqual(m.main(),3);closed.assert_called_once_with(91)
 def test_timeout_closes_mock_fd(self):
  class Info:st_mode=stat.S_IFCHR
  with patch.object(sys,'argv',['test','/dev/input/event0']),patch('builtins.input',return_value='START'),patch.object(m.os,'open',return_value=91),patch.object(m.os,'fstat',return_value=Info()),patch.object(m.os,'close') as closed,patch.object(m.time,'monotonic',side_effect=[0,61]),contextlib.redirect_stdout(io.StringIO()):self.assertEqual(m.main(),4);closed.assert_called_once_with(91)
if __name__=='__main__':unittest.main(verbosity=2)
