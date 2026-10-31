# H1 adaptation of historical observer tests; parent SHA256 657dc8c9248cd9e6db0249f31db59af860889d5bd952b0f40a42d1fc5da9fa2f
#!/usr/bin/env python3
"""Mock-only observer checks. Never contacts a device or network."""
import ast
import importlib.util
import io
import json
from pathlib import Path
import sys
import unittest
import urllib.error
sys.dont_write_bytecode = True
P = Path(__file__).with_name('observe_wait.py')
spec = importlib.util.spec_from_file_location('observe_wait', P)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def status(request='1', capture=100, waiting=False, owned=True, phase=6, reason=0):
    return dict(routeBRequestId=request, routeBOwned=owned, snapshotKind='request-capture',
                capturedAtMs=capture, routeBWaiting=waiting, routeBWaitCommand=5,
                routeBWaitStartedMs=50, routeBWaitSession=9, routeBPhase=phase,
                routeBReason=reason, routeBLine=4, routeBErrorCode=0,
                ssid='PRIVATE_SSID', script='PRIVATE_SCRIPT', lastError='PRIVATE_ERROR')


class FakeClock:
    def __init__(self): self.at = 0
    def __call__(self): return self.at
    def sleep(self, value): self.at += value


class FakeClient:
    def __init__(self, sequence): self.sequence=list(sequence);self.calls=[];self.password='SECRET'
    def get(self, path):
        self.calls.append(path)
        if not self.sequence: raise AssertionError('unexpected request')
        value=self.sequence.pop(0)
        if isinstance(value, BaseException): raise value
        return value


class Response:
    status=200
    def __init__(self, value): self.value=value
    def __enter__(self): return self
    def __exit__(self, *args): pass
    def read(self, count): return self.value[:count]


class Opener:
    def __init__(self, response): self.response=response;self.requests=[]
    def open(self, request, timeout):
        self.requests.append((request, timeout))
        if isinstance(self.response, Exception): raise self.response
        return self.response


class ObserverTests(unittest.TestCase):
    def run_main(self, extra, build=m.BUILD, password='SECRET', request='1', seconds=2):
        # New helper binds freshness to preflight. Model a strictly earlier idle
        # capture, including the wrap test, instead of reusing the first timestamp.
        first=next((v['capturedAtMs'] for v in extra if isinstance(v,dict) and 'capturedAtMs' in v),100)
        initial=status(request='0',capture=(first-1)&0xffffffff,owned=False,phase=0)
        client=FakeClient([{'buildId':build}, initial] + extra)
        out=io.StringIO();clock=FakeClock()
        code=m.main(['--seconds',str(seconds)], client_factory=lambda *args:client,
                    ask=lambda prompt:request, secret=lambda prompt:password,
                    output=out, clock=clock, sleep=clock.sleep)
        return code,out.getvalue(),client

    def test_wait_then_cancel(self):
        code,out,client=self.run_main([status(waiting=True),status(capture=200,owned=False,phase=0,reason=2)])
        self.assertEqual(code,0);self.assertIn('MATCHED_CAPS_CHANGE_WAIT_OBSERVED',out)
        self.assertIn('OWNER_REVIEW_REQUIRED',out);self.assertNotIn('PRIVATE_',out)
        self.assertEqual(client.password,'');self.assertNotIn('SECRET',out)
        self.assertTrue(all(p in ('/caps-timing','/status') for p in client.calls))

    def test_preflight_requires_idle(self):
        client=FakeClient([{'buildId':m.BUILD},status(waiting=True)])
        out=io.StringIO()
        code=m.main([],client_factory=lambda *args:client,secret=lambda p:'SECRET',
                    ask=lambda p:self.fail('prompt must not be reached'),output=out)
        self.assertEqual(code,2);self.assertIn('EXECUTION_NOT_IDLE',out.getvalue())
        self.assertNotIn('READY',out.getvalue())

    def test_missing_password(self):
        code,out,client=self.run_main([],password='');self.assertEqual(code,2)
        self.assertIn('MISSING_PASSWORD',out);self.assertEqual(client.calls,[])

    def test_build_mismatch(self):
        code,out,client=self.run_main([],build='wrong');self.assertEqual(code,2)
        self.assertIn('BUILD_ID_MISMATCH',out);self.assertEqual(client.calls,['/caps-timing'])

    def test_wrong_older_request_is_not_wait_evidence(self):
        code,out,_=self.run_main([status(request='1',waiting=True),status(request='2',capture=200,owned=False,phase=0,reason=1)],request='2')
        self.assertEqual(code,0);self.assertIn('REQUEST_MISMATCH',out)
        self.assertNotIn('MATCHED_CAPS_CHANGE_WAIT_OBSERVED',out);self.assertIn('"waitingObserved": false',out)

    def test_newer_request_stops(self):
        code,out,_=self.run_main([status(request='2',waiting=True)])
        self.assertEqual(code,2);self.assertIn('REQUEST_REPLACED',out)

    def test_expiry_is_observation_not_failure(self):
        end=status(owned=False,phase=0,reason=9);end['routeBErrorCode']=26
        code,out,_=self.run_main([end]);self.assertEqual(code,0)
        self.assertIn('"reason": 9',out);self.assertNotIn('"acceptanceDecision": "PASS"',out)

    def test_no_stale_snapshot_after_409(self):
        code,out,client=self.run_main([status(waiting=True),m.ObservationError('HTTP_409')])
        self.assertEqual(code,2);self.assertEqual(out.count('MATCHED_CAPTURE'),1)
        self.assertIn('"currentSnapshotAvailable": false',out)
        self.assertEqual(len(client.calls),4)

    def test_duplicate_capture_cannot_satisfy_wait(self):
        code,out,_=self.run_main([status(),status(waiting=True),status(capture=200,owned=False,phase=0)])
        self.assertEqual(code,0);self.assertIn('DUPLICATE_CAPTURE',out)
        self.assertNotIn('MATCHED_CAPS_CHANGE_WAIT_OBSERVED',out)

    def test_capture_wrap(self):
        wrapped=status(capture=10,waiting=True);wrapped['routeBWaitStartedMs']=0xffffffe0
        code,out,_=self.run_main([status(capture=0xfffffff0),wrapped,status(capture=20,owned=False,phase=0)])
        self.assertEqual(code,0);self.assertIn('MATCHED_CAPS_CHANGE_WAIT_OBSERVED',out)

    def test_backward_capture(self):
        code,out,_=self.run_main([status(capture=100),status(capture=99)])
        self.assertEqual(code,2);self.assertIn('CAPTURE_CLOCK_OR_DEVICE_RESTART',out)

    def test_session_change(self):
        newer=status(capture=200,waiting=True);newer['routeBWaitSession']=10
        code,out,_=self.run_main([status(waiting=True),newer])
        self.assertEqual(code,2);self.assertIn('WAIT_SESSION_CHANGED',out)

    def test_unexpected_wait(self):
        s=status(waiting=True);s['routeBWaitCommand']=3
        code,out,_=self.run_main([s]);self.assertEqual(code,2)
        self.assertIn('INCONSISTENT_OR_UNEXPECTED_WAIT',out)

    def test_missing_field(self):
        s=status();del s['capturedAtMs'];code,out,_=self.run_main([s])
        self.assertEqual(code,2);self.assertIn('MISSING_STATUS_FIELD',out)

    def test_bad_types(self):
        s=status();s['routeBWaiting']=1;code,out,_=self.run_main([s])
        self.assertEqual(code,2);self.assertIn('INVALID_STATUS_TYPE',out)

    def test_invalid_assigned_ids(self):
        for value in ('0','-1','1SECRET','18446744073709551616','١'):
            code,out,client=self.run_main([],request=value)
            self.assertEqual(code,2);self.assertIn('INVALID_REQUEST_ID',out)
            self.assertEqual(len(client.calls),2)

    def test_window_bounded(self):
        code,out,client=self.run_main([status(capture=n) for n in range(100,120)],seconds=1)
        self.assertEqual(code,2);self.assertIn('OBSERVATION_WINDOW_ENDED',out)
        self.assertLessEqual(len(client.calls),7)

    def test_slow_response_past_window_is_not_evidence(self):
        clock=FakeClock();events=[]
        class SlowClient:
            def get(self, path):
                clock.at += 5
                return status(waiting=True)
        code=m.monitor(SlowClient(),'1',1,lambda event,**fields:events.append((event,fields)),
                       clock=clock,sleep=clock.sleep)
        self.assertEqual(code,2)
        self.assertEqual(events[0][0],'OBSERVATION_WINDOW_EXCEEDED_DURING_REQUEST')
        self.assertFalse(any(event=='MATCHED_CAPTURE' for event,fields in events))
        self.assertFalse(any(event=='MATCHED_CAPS_CHANGE_WAIT_OBSERVED' for event,fields in events))

    def test_http_errors_sanitized(self):
        for code in (401,409,302):
            error=urllib.error.HTTPError('http://SECRET/',code,'SECRET',{},None)
            opener=Opener(error);client=m.Client('http://192.168.4.1','SECRET',opener)
            with self.assertRaisesRegex(m.ObservationError,'HTTP_%d'%code): client.get('/status')
            self.assertEqual(len(opener.requests),1)

    def test_timeout_sanitized(self):
        client=m.Client('http://192.168.4.1','SECRET',Opener(TimeoutError('SECRET')))
        with self.assertRaisesRegex(m.ObservationError,'NETWORK_OR_TIMEOUT'):client.get('/status')

    def test_bad_json_and_response_bound(self):
        for data,code in ((b'{SECRET','INVALID_JSON'),(b'[]','INVALID_JSON_OBJECT'),(b'x'*32769,'RESPONSE_TOO_LARGE')):
            with self.assertRaisesRegex(m.ObservationError,code):m.Client('http://192.168.4.1','SECRET',Opener(Response(data))).get('/status')

    def test_only_get_and_header_auth(self):
        opener=Opener(Response(b'{}'));m.Client('http://192.168.4.1','SECRET',opener).get('/status')
        request,timeout=opener.requests[0];self.assertEqual(request.get_method(),'GET')
        self.assertEqual(request.full_url,'http://192.168.4.1/status');self.assertEqual(timeout,2)
        self.assertEqual(request.get_header('X-duck-password'),'SECRET')
        with self.assertRaisesRegex(m.ObservationError,'DISALLOWED_PATH'):m.Client('http://192.168.4.1','SECRET').get('/stop')

    def test_redirect_refused_and_bad_urls(self):
        self.assertIsNone(m.NoRedirect().redirect_request(None,None,302,'m',{},'http://evil/'))
        for url in ('http://user:SECRET@192.168.4.1','http://192.168.4.1?pw=SECRET','http://192.168.4.1/a','file:///tmp/SECRET'):
            with self.assertRaisesRegex(m.ObservationError,'INVALID_BASE_URL'):m.Client(url,'SECRET')

    def test_python38_syntax(self):
        ast.parse(P.read_text(),feature_version=(3,8))




class H1Tests(unittest.TestCase):
    run_main = ObserverTests.run_main


def add_test(name):
    def register(fn):
        setattr(H1Tests, 'test_'+name, fn)
        return fn
    return register

@add_test('exact_h1_build_required_no_prefix_or_other_release')
def _(self):
    for value in ('ROUTEB-INJECT-VAR-H1-EXPERIMENTAL-', m.BUILD[:-1], m.BUILD+'x',
                  'ROUTEB-LOCK-WAIT-TIMEOUT-v1', None, 3, True, ''):
        code,out,client=self.run_main([],build=value)
        self.assertEqual(code,2);self.assertIn('BUILD_ID_MISMATCH',out)
        self.assertEqual(client.calls,['/caps-timing'])

@add_test('preflight_waiting_idle_inconsistency_refused')
def _(self):
    client=FakeClient([{'buildId':m.BUILD},status(request='0',owned=False,phase=0,waiting=True)])
    out=io.StringIO()
    code=m.main([],client_factory=lambda *a:client,secret=lambda p:'SECRET',
                ask=lambda p:self.fail('must not ask'),output=out)
    self.assertEqual(code,2);self.assertNotIn('READY',out.getvalue())

@add_test('old_or_same_request_not_accepted_after_ready')
def _(self):
    for wanted in ('1','5'):
        client=FakeClient([{'buildId':m.BUILD},status(request='5',owned=False,phase=0)])
        out=io.StringIO()
        code=m.main([],client_factory=lambda *a:client,secret=lambda p:'SECRET',ask=lambda p:wanted,output=out)
        self.assertEqual(code,2);self.assertIn('REQUEST_NOT_NEWER_THAN_PREFLIGHT',out.getvalue())
        self.assertEqual(len(client.calls),2)

@add_test('new_request_need_not_be_preflight_plus_one')
def _(self):
    code,out,_=self.run_main([status(request='12',owned=False,phase=0,reason=1)],request='12')
    self.assertEqual(code,0);self.assertIn('TERMINAL_CAPTURE',out)

@add_test('stale_first_capture_not_promoted')
def _(self):
    initial=status(request='0',capture=100,owned=False,phase=0)
    client=FakeClient([{'buildId':m.BUILD},initial,status(waiting=True,capture=100),status(capture=110,owned=False,phase=0,reason=1)])
    out=io.StringIO();clock=FakeClock()
    code=m.main(['--seconds','2'],client_factory=lambda *a:client,secret=lambda p:'SECRET',ask=lambda p:'1',output=out,clock=clock,sleep=clock.sleep)
    self.assertEqual(code,0);self.assertIn('DUPLICATE_CAPTURE',out.getvalue())
    self.assertNotIn('MATCHED_CAPS_CHANGE_WAIT_OBSERVED',out.getvalue())

@add_test('every_required_field_missing_fails_closed')
def _(self):
    for key in m.FIELDS:
        value=status();del value[key];code,out,_=self.run_main([value])
        self.assertEqual(code,2);self.assertNotIn('MATCHED_CAPTURE',out)

@add_test('numeric_field_types_bounds_and_booleans_refused')
def _(self):
    keys=('capturedAtMs','routeBWaitCommand','routeBWaitStartedMs','routeBWaitSession',
          'routeBPhase','routeBReason','routeBLine','routeBErrorCode')
    for key in keys:
        for v in (None,'1',True,-1,4294967296):
            raw=status();raw[key]=v
            with self.assertRaises(m.ObservationError):m.snapshot(raw)

@add_test('wrong_kind_ids_and_boolean_fields_refused')
def _(self):
    for key,val in [('snapshotKind','live'),('routeBRequestId',1),('routeBRequestId','00'),
                    ('routeBOwned',0),('routeBWaiting','false')]:
        raw=status();raw[key]=val
        with self.assertRaises(m.ObservationError):m.snapshot(raw)

@add_test('unsupported_phase_9_refused_actual_quarantine_8')
def _(self):
    raw=status(phase=9);code,out,_=self.run_main([raw])
    self.assertEqual(code,2);self.assertIn('UNSUPPORTED_STATUS_ENUM',out)
    raw=status(phase=8);code,out,_=self.run_main([raw])
    self.assertEqual(code,2);self.assertIn('QUARANTINED_CAPTURE',out)
    self.assertNotIn('TERMINAL_CAPTURE',out)

@add_test('future_and_ambiguous_wait_start_rejected_before_match')
def _(self):
    for started in (101,(100+0x80000000)&0xffffffff):
        raw=status(waiting=True);raw['routeBWaitStartedMs']=started
        code,out,_=self.run_main([raw]);self.assertEqual(code,2)
        self.assertIn('WAIT_START_CLOCK_AMBIGUOUS',out);self.assertNotIn('MATCHED_CAPTURE',out)

@add_test('zero_wait_session_and_equal_start_are_supported')
def _(self):
    raw=status(waiting=True);raw['routeBWaitSession']=0;raw['routeBWaitStartedMs']=100
    code,out,_=self.run_main([raw,status(capture=110,owned=False,phase=0,reason=2)])
    self.assertEqual(code,0);self.assertIn('MATCHED_CAPS_CHANGE_WAIT_OBSERVED',out)

@add_test('half_range_capture_ambiguity_refused')
def _(self):
    raw=status(capture=(100+0x80000000)&0xffffffff)
    code,out,_=self.run_main([status(capture=100),raw])
    self.assertEqual(code,2);self.assertIn('CAPTURE_CLOCK_OR_DEVICE_RESTART',out)

@add_test('waiting_inconsistent_ownership_phase_or_selector_refused')
def _(self):
    for key,value in [('routeBOwned',False),('routeBPhase',7),('routeBWaitCommand',3)]:
        raw=status(waiting=True);raw[key]=value;code,out,_=self.run_main([raw])
        self.assertEqual(code,2);self.assertNotIn('MATCHED_CAPTURE',out)

@add_test('terminal_reasons_never_automatically_pass_trial')
def _(self):
    for reason,error in ((1,0),(2,0),(9,26),(6,26),(8,0),(7,0),(4,16)):
        raw=status(owned=False,phase=0,reason=reason);raw['routeBErrorCode']=error
        code,out,_=self.run_main([raw]);self.assertEqual(code,0)
        self.assertIn('OWNER_REVIEW_REQUIRED',out)
        self.assertNotIn('"acceptanceDecision": "PASS"',out)

@add_test('get_auth_contention_network_errors_no_retry')
def _(self):
    for error in ('HTTP_401','HTTP_403','HTTP_409','NETWORK_OR_TIMEOUT','INVALID_JSON'):
        code,out,client=self.run_main([m.ObservationError(error)])
        self.assertEqual(code,2);self.assertEqual(len(client.calls),3)
        self.assertNotIn('MATCHED_CAPTURE',out)

@add_test('no_mutation_path_is_accepted')
def _(self):
    opener=Opener(Response(b'{}'));client=m.Client('http://192.168.4.1','SECRET',opener)
    for path in ('/stop','/run','/routeb','/settings','/upload','/caps-timing?pw=SECRET','/status?pw=SECRET'):
        with self.assertRaisesRegex(m.ObservationError,'DISALLOWED_PATH'):client.get(path)
    self.assertEqual(opener.requests,[])

@add_test('selected_logs_drop_all_private_response_fields')
def _(self):
    code,out,_=self.run_main([status(owned=False,phase=0,reason=1)])
    self.assertEqual(code,0)
    for word in ('PRIVATE_', 'SECRET', 'ssid', 'lastError', 'autorunScript'):
        self.assertNotIn(word,out)
    events=[json.loads(line) for line in out.splitlines()]
    captures=[v['status'] for v in events if v['event']=='MATCHED_CAPTURE']
    self.assertTrue(captures);self.assertEqual(set(captures[0]),set(m.FIELDS))

@add_test('ctrl_c_stops_observer_without_stop_action')
def _(self):
    code,out,client=self.run_main([KeyboardInterrupt()]);self.assertEqual(code,2)
    self.assertIn('OBSERVER_INTERRUPTED',out);self.assertEqual(client.password,'')
    self.assertTrue(all(p in ('/caps-timing','/status') for p in client.calls))

@add_test('frozen_clock_still_has_attempt_cap')
def _(self):
    client=FakeClient([status(capture=100+n) for n in range(6)]);events=[]
    code=m.monitor(client,'1',1,lambda *a,**kw:events.append((a,kw)),clock=lambda:0,sleep=lambda _:None)
    self.assertEqual(code,2);self.assertEqual(len(client.calls),5)

@add_test('invalid_preflight_capture_not_ready')
def _(self):
    raw=status(request='0',owned=False,phase=0);raw['capturedAtMs']='100'
    client=FakeClient([{'buildId':m.BUILD},raw]);out=io.StringIO()
    code=m.main([],client_factory=lambda *a:client,secret=lambda p:'SECRET',output=out,
                ask=lambda p:self.fail('must not ask'))
    self.assertEqual(code,2);self.assertNotIn('READY',out.getvalue())

@add_test('wait_session_change_stops_without_replacement_evidence')
def _(self):
    raw=status(waiting=True,capture=200);raw['routeBWaitSession']=10
    code,out,_=self.run_main([status(waiting=True),raw])
    self.assertEqual(code,2);self.assertIn('WAIT_SESSION_CHANGED',out)
    self.assertEqual(out.count('MATCHED_CAPTURE'),1)


def main():
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--results',type=Path)
    args=parser.parse_args()
    if args.results:
        path=args.results.resolve()
        if path.parent==P.parent.resolve() or P.parent.resolve() in path.parents:
            parser.error('Save results outside the checksum-bound kit directory')
        if path.exists():parser.error('Results path already exists; preserve it')
    suite=unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromTestCase(c) for c in (ObserverTests,H1Tests)])
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    report=dict(tests=result.testsRun,PASS=result.testsRun-len(result.failures)-len(result.errors)-len(result.skipped),
                FAIL=len(result.failures)+len(result.errors),SKIP=len(result.skipped),hardware=False,
                network=False,scope='Mock-only observer tests; no esptool or real HTTP operation',
                native_high_sierra_tested=False)
    print(json.dumps(report,sort_keys=True))
    if args.results:args.results.write_text(json.dumps(report,indent=2)+'\n')
    return 0 if result.wasSuccessful() else 1

if __name__=='__main__':raise SystemExit(main())
