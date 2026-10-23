"""Full packaged-helper launch paths. HTTP, Darwin and native execution are mocks."""
import contextlib
import importlib.util
import io
import json
import os
import pathlib
import sys
import types
import unittest
import urllib.error
import zipfile
from unittest.mock import patch

HERE = pathlib.Path(os.environ.get('EVILDUCK_TEST_HELPER_DIR', str(pathlib.Path(__file__).parent)))
spec = importlib.util.spec_from_file_location('helper_full_main', HERE/'led_action.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class Clock:
    def __init__(self): self.t = 0.0
    def now(self): return self.t
    def sleep(self, value): self.t += value


class Response:
    def __init__(self, value): self.data = json.dumps(value).encode()
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def read(self, maximum): return self.data[:maximum]


class Launch:
    """A manually started synthetic 15s delay / 5s wait, no real device."""
    def __init__(self, entry=2.0):
        self.clock, self.entry = Clock(), entry
        self.events, self.calls = [], []
        self.started, self.inputs = False, 0
        self.failure, self.exit_code, self.cancel_last = None, 0, False
        self.status_reads = 0
        self.fixture_password = 'x' * 23  # Mock only; never an owner credential.

    def identity(self):
        return dict(buildId=m.BUILD, state=0, bootMarker='1122334455667788',
                    feedbackSession=42, snapshotSessionCoherent=True,
                    usbConfiguredSample=True, usbSuspendedSample=False)

    def status(self):
        self.status_reads += 1
        active = self.started and self.clock.t < 20
        waiting = active and self.clock.t >= 15
        s = dict(snapshotKind='request-capture', routeBRequestId='7' if self.started else '6',
                 routeBOwned=active, running=active, routeBPhase=6 if active else 0,
                 routeBWaiting=waiting, routeBWaitCommand=3, routeBWaitSession=42,
                 capturedAtMs=int(round(self.clock.t*1000)) & 0xffffffff,
                 routeBWaitStartedMs=15000)
        if self.cancel_last and self.status_reads >= 3:
            s.update(routeBWaiting=False, routeBOwned=False, running=False, routeBPhase=0)
        return s

    def open(self, request, timeout):
        path = request.full_url.split('192.168.4.1', 1)[1]
        self.events.append(('HTTP', path))
        assert path in ('/led-test', '/status') and timeout == .5
        assert request.get_header('X-duck-password') == self.fixture_password
        assert request.get_header('Authorization') is None
        assert request.get_header('Cache-control') == 'no-cache'
        if self.failure: raise self.failure
        return Response(self.identity() if path == '/led-test' else self.status())

    def password(self, prompt):
        self.events.append(('PASSWORD',))
        return self.fixture_password

    def input(self, prompt):
        self.inputs += 1
        if self.inputs == 1:
            assert prompt.endswith('APPLY ONCE: ')
            assert not self.started
            self.events.append(('CONSENT',))
            return 'APPLY ONCE'
        assert self.inputs == 2 and 'Assigned request ID' in prompt
        self.events.append(('MANUAL_START_AND_ID',))
        self.started = True
        self.clock.t = self.entry
        return '7'

    def native(self, args, timeout, check):
        assert args[1:] == ['--one-approved-action', 'SYNTHETIC', '2', '1']
        assert timeout == 5 and check is False
        self.events.append(('NATIVE', self.clock.t))
        self.calls.append(args)
        return types.SimpleNamespace(returncode=self.exit_code)

    def run(self, arguments=None, file_present=True, password=None, input_fn=None, cli=False):
        stdout = io.StringIO()
        # Explicit injection into the real act(), not a replacement act() test.
        actual_act = m.act
        def controlled_act(*args, **kwargs):
            return actual_act(*args, **kwargs, clock=self.clock.now, sleep=self.clock.sleep)
        argv = ['led_action.py', '--serial', 'SYNTHETIC', '--command', 'WAIT_FOR_CAPS_ON', '--value', '1']
        if arguments: argv += arguments
        with contextlib.ExitStack() as stack:
            stack.enter_context(patch.object(sys, 'argv', argv))
            stack.enter_context(patch.object(m.os, 'uname', return_value=types.SimpleNamespace(sysname='Darwin')))
            stack.enter_context(patch.object(m.pathlib.Path, 'is_file', return_value=file_present))
            stack.enter_context(patch.object(m.pathlib.Path, 'is_symlink', return_value=False))
            stack.enter_context(patch.object(m.os, 'access', return_value=True))
            stack.enter_context(patch.object(m.getpass, 'getpass', side_effect=password or self.password))
            stack.enter_context(patch.object(m.urllib.request, 'build_opener', return_value=self))
            stack.enter_context(patch('builtins.input', side_effect=input_fn or self.input))
            stack.enter_context(patch.object(m.subprocess, 'run', side_effect=self.native))
            stack.enter_context(patch.object(m, 'act', side_effect=controlled_act))
            stack.enter_context(patch.object(m.time, 'sleep', side_effect=self.clock.sleep))
            stack.enter_context(contextlib.redirect_stdout(stdout))
            result = m.cli() if cli else m.main()
        return result, stdout.getvalue()


class Tests(unittest.TestCase):
    def test_interactive_main_reaches_native_without_base64(self):
        x = Launch(); result, output = x.run()
        self.assertEqual(result, 0)
        self.assertEqual(len(x.calls), 1)
        self.assertIn('READY:', output)
        self.assertNotIn(x.fixture_password, output)
        self.assertLess(x.events.index(('CONSENT',)), x.events.index(('MANUAL_START_AND_ID',)))
        self.assertEqual(x.events[0], ('PASSWORD',))
        self.assertEqual(x.events[1:4], [('HTTP','/led-test'),('HTTP','/status'),('HTTP','/led-test')])
        self.assertGreaterEqual(x.events[-1][1], 15)
        self.assertLess(x.events[-1][1], 16)

    def test_simulated_id_entry_times(self):
        for t in (0.0, 2.0, 10.0, 12.2, 12.999):
            with self.subTest(entry=t):
                x = Launch(t); self.assertEqual(x.run()[0], 0); self.assertEqual(len(x.calls), 1)
        for t in (13.0, 15.0, 17.0, 21.0):
            with self.subTest(entry=t):
                x = Launch(t)
                with self.assertRaises(ValueError): x.run()
                self.assertFalse(x.calls)

    def test_missing_native_before_password_or_network(self):
        x = Launch()
        with self.assertRaisesRegex(ValueError, 'COMPILE_NATIVE'): x.run(file_present=False)
        self.assertEqual(x.events, [])

    def test_missing_password(self):
        x = Launch()
        with self.assertRaisesRegex(ValueError,'MISSING_PASSWORD'): x.run(password=lambda _: '')
        self.assertFalse(x.calls); self.assertEqual(x.inputs, 0)

    def test_http_401_and_409_not_retried(self):
        for code in (401,409):
            x=Launch(); x.failure=urllib.error.HTTPError('http://192.168.4.1/led-test',code,'blocked',None,None)
            result,output=x.run(cli=True)
            self.assertEqual(result,1);self.assertIn('HTTP_%d'%code,output)
            self.assertFalse(x.calls);self.assertEqual(sum(e[0]=='HTTP' for e in x.events),1)

    def test_consent_refusal_no_id_or_action(self):
        x=Launch(); result,_=x.run(input_fn=lambda _: 'NO')
        self.assertEqual(result,2);self.assertFalse(x.calls);self.assertFalse(x.started)

    def test_invalid_id_once_no_action(self):
        for bad in ('', '0', '-1', '7x', str(1<<64)):
            x=Launch(); answers=iter(['APPLY ONCE',bad])
            with self.assertRaisesRegex(ValueError,'INVALID_REQUEST_ID'):x.run(input_fn=lambda _:next(answers))
            self.assertFalse(x.calls)

    def test_eof_and_interrupt(self):
        for error in (EOFError(),KeyboardInterrupt()):
            x=Launch()
            def stop(_):raise error
            result,output=x.run(input_fn=stop,cli=True)
            self.assertEqual(result,1);self.assertIn('CANCELLED',output);self.assertFalse(x.calls)

    def test_stopping_last_capture_refuses_native(self):
        x=Launch(12.1);x.cancel_last=True
        with self.assertRaisesRegex(ValueError,'WAIT_CHANGED'):x.run()
        self.assertFalse(x.calls)

    def test_boot_change_while_entering_id(self):
        x=Launch(); original=x.identity
        def identity():
            s=original()
            if x.started:s['bootMarker']='8877665544332211'
            return s
        x.identity=identity
        with self.assertRaisesRegex(ValueError,'PREPARED_SESSION_CHANGED'):x.run()
        self.assertFalse(x.calls)

    def test_wrong_manual_id_not_searched(self):
        x=Launch(); original=x.input
        def answer(prompt):
            v=original(prompt)
            return '8' if x.inputs==2 else v
        with self.assertRaisesRegex(ValueError,'REQUEST_MISMATCH'):x.run(input_fn=answer)
        self.assertFalse(x.calls)

    def test_native_error_one_attempt(self):
        x=Launch();x.exit_code=3
        result,output=x.run()
        self.assertEqual(result,3);self.assertEqual(len(x.calls),1)
        self.assertIn('not device completion',output)

    def test_explicit_request_retained(self):
        x=Launch();x.started=True;x.clock.t=2.0
        result,output=x.run(arguments=['--request','7'],input_fn=lambda _:'APPLY ONCE')
        self.assertEqual(result,0);self.assertEqual(len(x.calls),1);self.assertNotIn('READY:',output)

    def test_native_timeout_no_retry(self):
        x=Launch()
        def timeout(args, **kwargs):
            x.calls.append(args)
            raise m.subprocess.TimeoutExpired(args, 5)
        x.native=timeout
        result,output=x.run(cli=True)
        self.assertEqual(result,1);self.assertEqual(len(x.calls),1)
        self.assertIn('NATIVE_TIMEOUT_RESTORATION_UNVERIFIED',output)

    def test_receiver_active_before_ready(self):
        x=Launch();original=x.identity
        def identity():
            s=original();s['state']=1;return s
        x.identity=identity
        with self.assertRaisesRegex(ValueError,'BUILD_OR_RECEIVER_NOT_SAFE'):x.run()
        self.assertFalse(x.calls);self.assertEqual(x.inputs,0)

    def test_existing_execution_not_prepared(self):
        x=Launch();x.started=True
        with self.assertRaisesRegex(ValueError,'IDLE_BEFORE_PREPARATION_REQUIRED'):x.run()
        self.assertFalse(x.calls);self.assertEqual(x.inputs,0)

    def test_old_published_main_reproduces_undefined_base64(self):
        # Historical evidence only; it must not become a new release pass claim.
        archive=pathlib.Path(__file__).resolve().parents[2]/'downloads/evilduck-routeb-lock-led-action-v1.zip'
        with zipfile.ZipFile(archive)as z:source=z.read('led_action.py')
        old=types.ModuleType('old_packaged_helper');old.__file__='old/led_action.py';exec(compile(source,old.__file__,'exec'),old.__dict__)
        with patch.object(sys,'argv',['old','--serial','SYNTHETIC','--request','7','--command','WAIT_FOR_CAPS_ON','--value','1']), patch.object(old.os,'uname',return_value=types.SimpleNamespace(sysname='Darwin')),patch.object(old.getpass,'getpass',return_value='x'*23),patch.object(old.urllib.request,'build_opener')as network,patch.object(old.subprocess,'run')as native:
            with self.assertRaisesRegex(NameError,'base64'):old.main()
            network.assert_not_called();native.assert_not_called()

if __name__=='__main__':unittest.main(verbosity=2)
