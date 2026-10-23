import ast,copy,importlib.util,os,pathlib,unittest
p=pathlib.Path(os.environ.get('EVILDUCK_TEST_HELPER_DIR',str(pathlib.Path(__file__).parent)))/'led_action.py';spec=importlib.util.spec_from_file_location('fixture',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class Tests(unittest.TestCase):
 def setUp(self):
  self.s=dict(snapshotKind='request-capture',routeBRequestId='7',routeBOwned=True,routeBWaiting=True,routeBWaitCommand=3,routeBWaitSession=42,routeBPhase=6,capturedAtMs=100,routeBWaitStartedMs=100)
  self.i=dict(buildId=m.BUILD,state=0,bootMarker="1122334455667788",snapshotSessionCoherent=True,feedbackSession=42,usbConfiguredSample=True,usbSuspendedSample=False)
  self.calls=[]
 def run_action(self,s=None,i=None,command='WAIT_FOR_CAPS_ON',value=1):
  return m.act(lambda:s or self.s,lambda:i or self.i,lambda *a:self.calls.append(a) or 0,7,command,value)
 def test_one_action(self):self.assertEqual(self.run_action(),0);self.assertEqual(self.calls,[(2,1)])
 def test_guards(self):
  for key,value in [('snapshotKind','cached'),('routeBRequestId','8'),('routeBOwned',False),('routeBWaiting',False),('routeBWaitCommand',0),('routeBWaitCommand',True),('routeBWaitSession','42')]:
   s=copy.deepcopy(self.s);s[key]=value;self.assertFalse(m.check_status(s,7,'WAIT_FOR_CAPS_ON'))
 def test_identity_guards(self):
  for key,value in [('buildId','old'),('state',1),('state',None),('snapshotSessionCoherent',False),('feedbackSession',43),('usbConfiguredSample',False),('usbSuspendedSample',True)]:
   i=copy.deepcopy(self.i);i[key]=value
   with self.assertRaises(ValueError):self.run_action(i=i)
  self.assertFalse(self.calls)
 def test_no_replay(self):
  with self.assertRaises(ValueError):self.run_action(s=dict(self.s,routeBOwned=False))
  self.assertFalse(self.calls)
 def test_changed_wait(self):
  states=iter([self.s,dict(self.s,routeBWaitSession=43)])
  with self.assertRaises(ValueError):m.act(lambda:next(states),lambda:self.i,lambda *a:self.calls.append(a),7,'WAIT_FOR_CAPS_ON',1)
  self.assertFalse(self.calls)
 def test_boot_change(self):
  identities=iter([self.i,dict(self.i,bootMarker='8877665544332211')])
  with self.assertRaises(ValueError):m.act(lambda:self.s,lambda:next(identities),lambda *a:self.calls.append(a),7,'WAIT_FOR_CAPS_ON',1)
  self.assertFalse(self.calls)
 def test_wrong_action(self):
  for cmd,value in [('WAIT_FOR_CAPS_ON',0),('WAIT_FOR_SCROLL_ON',1),('WAIT_FOR_CAPS_CHANGE',3),('WAIT_FOR_CAPS_CHANGE',True)]:
   with self.assertRaises(ValueError):self.run_action(command=cmd,value=value)
  self.assertFalse(self.calls)
 def test_timeout_no_action(self):
  now=[0]
  def sleep(t):now[0]+=t
  with self.assertRaisesRegex(ValueError,'NO_MATCHING'):m.act(lambda:dict(self.s,routeBWaiting=False),lambda:self.i,lambda *a:self.calls.append(a),7,'WAIT_FOR_CAPS_ON',1,lambda:now[0],sleep)
  self.assertFalse(self.calls)
 def test_failed_submission_not_retried(self):
  calls=[];self.assertEqual(m.act(lambda:self.s,lambda:self.i,lambda *a:calls.append(a) or 3,7,'WAIT_FOR_CAPS_ON',1),3);self.assertEqual(len(calls),1)
 def test_request_mismatch_not_searched(self):
  with self.assertRaisesRegex(ValueError,'REQUEST_MISMATCH'):self.run_action(s=dict(self.s,routeBRequestId='8'))
  self.assertFalse(self.calls)
 def test_wait_age_boundaries(self):
  self.assertEqual(self.run_action(s=dict(self.s,capturedAtMs=1099)),0)
  self.calls.clear()
  for t in (1100,5100,0):
   with self.assertRaisesRegex(ValueError,'WAIT_TOO_LATE'):self.run_action(s=dict(self.s,capturedAtMs=t))
  self.assertFalse(self.calls)
 def test_wait_age_wrap(self):
  self.assertEqual(self.run_action(s=dict(self.s,routeBWaitStartedMs=0xfffffff0,capturedAtMs=16)),0)
 def test_missing_wait_time_fails_closed(self):
  for k in ('capturedAtMs','routeBWaitStartedMs'):
   s=dict(self.s);s.pop(k)
   with self.assertRaisesRegex(ValueError,'WAIT_TIMESTAMPS'):self.run_action(s=s)
  self.assertFalse(self.calls)
 def test_cancel_observed_before_action(self):
  states=iter([self.s,dict(self.s,routeBWaiting=False,routeBPhase=7)])
  with self.assertRaisesRegex(ValueError,'WAIT_CHANGED'):m.act(lambda:next(states),lambda:self.i,lambda *a:self.calls.append(a),7,'WAIT_FOR_CAPS_ON',1)
  self.assertFalse(self.calls)
 def test_prepared_identity_retained(self):
  prepared=dict(self.i,bootMarker='8877665544332211')
  with self.assertRaisesRegex(ValueError,'PREPARED_SESSION_CHANGED'):m.act(lambda:self.s,lambda:self.i,lambda *a:self.calls.append(a),7,'WAIT_FOR_CAPS_ON',1,prepared=prepared)
  self.assertFalse(self.calls)
 def test_slow_pre_action_samples_refused(self):
  times=iter([0,0,0,1.0])
  with self.assertRaisesRegex(ValueError,'PRE_ACTION_CHECK_TOO_SLOW'):m.act(lambda:self.s,lambda:self.i,lambda *a:self.calls.append(a),7,'WAIT_FOR_CAPS_ON',1,clock=lambda:next(times))
  self.assertFalse(self.calls)
 def test_invalid_host_clock(self):
  for moments in ([0,-1],[0,0,float('nan')],[0,0,0,float('inf')]):
   times=iter(moments)
   with self.assertRaisesRegex(ValueError,'HOST_CLOCK_ERROR'):m.act(lambda:self.s,lambda:self.i,lambda *a:self.calls.append(a),7,'WAIT_FOR_CAPS_ON',1,clock=lambda:next(times))
  self.assertFalse(self.calls)
 def test_python38(self):ast.parse(p.read_text(),feature_version=(3,8))
 def test_no_start_write_endpoint(self):
  s=p.read_text();self.assertNotIn("read('/run",s);self.assertNotIn('/led-test/start',s);self.assertNotIn('write_flash',s)
if __name__=='__main__':unittest.main(verbosity=2)
