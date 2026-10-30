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
        if isinstance(value, Exception): raise value
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
        client=FakeClient([{'buildId':build}, status(request='0', owned=False, phase=0)] + extra)
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
        code,out,_=self.run_main([status(capture=0xfffffff0),status(capture=10,waiting=True),status(capture=20,owned=False,phase=0)])
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


if __name__ == '__main__': unittest.main(verbosity=2)
