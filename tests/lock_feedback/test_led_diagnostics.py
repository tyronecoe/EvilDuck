"""Sanitized helper diagnostics with synthetic HTTP, clocks and native calls only."""
import contextlib
import errno
import io
import json
import socket
import subprocess
import unittest
import urllib.error
from unittest.mock import patch

from test_led_action_main import Launch, m


SECRET = 'SECRET_DIAGNOSTIC_TEXT'
PRIVATE_URL = 'http://private-user:private-password@192.168.4.1/private-path'
PHASE_REQUESTS = (
    'PREFLIGHT_IDENTITY', 'PREFLIGHT_STATUS', 'PREFLIGHT_CONFIRM',
    'WAIT_INITIAL_IDENTITY', 'WAIT_POLL_STATUS', 'WAIT_POLL_IDENTITY',
    'WAIT_RECHECK_STATUS',
)


def records(output):
    return [json.loads(line) for line in output.splitlines() if line.startswith('{')]


class InstrumentedResponse:
    def __init__(self, launch, response, selected):
        self.launch, self.response, self.selected = launch, response, selected

    def __enter__(self):
        self.launch.observe('HTTP_ENTER')
        if self.selected and self.launch.operation == 'HTTP_ENTER':
            raise self.launch.error
        return self

    def read(self, maximum):
        self.launch.observe('HTTP_READ')
        if self.selected and self.launch.operation == 'HTTP_READ':
            raise self.launch.error
        return self.response.read(maximum)

    def __exit__(self, *args):
        self.launch.observe('HTTP_CLOSE')
        if self.selected and self.launch.close_error is not None:
            raise self.launch.close_error
        return False


class DiagnosticLaunch(Launch):
    def __init__(self, request=0, operation=None, error=None, close_error=None, raw=None):
        super().__init__(entry=12.2)
        self.request, self.operation, self.error = request, operation, error
        self.close_error, self.raw = close_error, raw
        self.http_count, self.markers, self.trace = 0, [], None

    def observe(self, operation):
        marker = (self.trace.phase, self.trace.operation, self.trace.sequence)
        self.markers.append(marker)
        assert marker[0] == PHASE_REQUESTS[self.http_count - 1]
        assert marker[1] == operation
        assert type(marker[2]) is int and 0 < marker[2] <= 4096

    def open(self, request, timeout):
        self.http_count += 1
        self.observe('HTTP_OPEN')
        response = super().open(request, timeout)
        selected = self.http_count == self.request
        if selected and self.operation == 'HTTP_OPEN':
            raise self.error
        if selected and self.raw is not None:
            response.data = self.raw
        return InstrumentedResponse(self, response, selected)

    def run_cli(self):
        self.trace = m.Diagnostics()
        with patch.object(m, 'Diagnostics', return_value=self.trace):
            return self.run(cli=True)


class DiagnosticsTests(unittest.TestCase):
    def error_record(self, output):
        found = records(output)
        self.assertEqual(len(found), 1)
        record = found[0]
        self.assertEqual(record['event'], 'HELPER_ERROR')
        self.assertIn(record['phase'], m.PHASES)
        self.assertIn(record['operation'], m.OPERATIONS)
        self.assertIs(type(record['sequence']), int)
        self.assertTrue(0 <= record['sequence'] <= 4096)
        self.assertLessEqual(set(record), {
            'event', 'phase', 'operation', 'sequence', 'exceptionClass',
            'causeClass', 'errno', 'category', 'httpStatus', 'secondaryExceptionClass',
        })
        for private in (SECRET, PRIVATE_URL, 'private-user', 'private-password',
                        'private-path', 'X-Duck-Password', '--private-argument', 'x' * 23):
            self.assertNotIn(private, output)
        return record

    def assert_no_native_or_retry(self, launch, request):
        self.assertFalse(launch.calls)
        self.assertEqual(launch.http_count, request)
        self.assertEqual(sum(event[0] == 'HTTP' for event in launch.events), request)

    def test_open_and_read_failures_have_each_semantic_phase(self):
        for request, phase in enumerate(PHASE_REQUESTS, 1):
            for operation in ('HTTP_OPEN', 'HTTP_READ'):
                errors = (
                    (OSError(errno.EIO, SECRET), 'HTTP_IO_ERROR', errno.EIO),
                    (socket.timeout(SECRET), 'HTTP_TIMEOUT', None),
                    (urllib.error.URLError(TimeoutError(errno.ETIMEDOUT, SECRET)),
                     'HTTP_TIMEOUT', errno.ETIMEDOUT),
                    (urllib.error.URLError(ConnectionRefusedError(errno.ECONNREFUSED, SECRET)),
                     'CONNECTION_REFUSED', errno.ECONNREFUSED),
                )
                for error, category, number in errors:
                    with self.subTest(phase=phase, operation=operation, category=category,
                                      wrapped=isinstance(error, urllib.error.URLError)):
                        x = DiagnosticLaunch(request, operation, error)
                        result, output = x.run_cli()
                        self.assertEqual(result, 1)
                        record = self.error_record(output)
                        self.assertEqual((record['phase'], record['operation']), (phase, operation))
                        self.assertEqual(record['category'], category)
                        self.assertEqual(record['errno'], number)
                        self.assert_no_native_or_retry(x, request)

    def test_timeout_and_connection_refused_unwrap_only_exception_reasons(self):
        errors = (
            (socket.timeout(SECRET), 'HTTP_TIMEOUT', None),
            (urllib.error.URLError(TimeoutError(errno.ETIMEDOUT, SECRET)),
             'HTTP_TIMEOUT', errno.ETIMEDOUT),
            (urllib.error.URLError(urllib.error.URLError(
                ConnectionRefusedError(errno.ECONNREFUSED, SECRET))),
             'CONNECTION_REFUSED', errno.ECONNREFUSED),
            (urllib.error.URLError(SECRET + PRIVATE_URL), 'HTTP_IO_ERROR', None),
        )
        for error, category, number in errors:
            with self.subTest(category=category, error_type=type(error).__name__):
                x = DiagnosticLaunch(1, 'HTTP_OPEN', error)
                result, output = x.run_cli()
                self.assertEqual(result, 1)
                record = self.error_record(output)
                self.assertEqual(record['category'], category)
                self.assertEqual(record['errno'], number)
                self.assert_no_native_or_retry(x, 1)

    def test_http_401_and_409_are_sanitized_without_retry(self):
        for status in (401, 409):
            with self.subTest(status=status):
                error = urllib.error.HTTPError(PRIVATE_URL, status, SECRET,
                                               {'X-Duck-Password': SECRET}, None)
                x = DiagnosticLaunch(1, 'HTTP_OPEN', error)
                result, output = x.run_cli()
                self.assertEqual(result, 1)
                record = self.error_record(output)
                self.assertEqual(record['category'], 'HTTP_ERROR')
                self.assertEqual(record['httpStatus'], status)
                self.assertEqual(record['exceptionClass'], 'HTTPError')
                self.assert_no_native_or_retry(x, 1)

    def test_invalid_json_has_decode_location_without_response_text(self):
        x = DiagnosticLaunch(7, raw=(SECRET + PRIVATE_URL).encode())
        result, output = x.run_cli()
        self.assertEqual(result, 1)
        record = self.error_record(output)
        self.assertEqual((record['phase'], record['operation']),
                         ('WAIT_RECHECK_STATUS', 'DECODE'))
        self.assertEqual(record['category'], 'INVALID_JSON')
        self.assertEqual(record['exceptionClass'], 'JSONDecodeError')
        self.assert_no_native_or_retry(x, 7)

    def test_context_enter_and_close_failures_have_io_locations(self):
        cases = (
            ('HTTP_ENTER', OSError(errno.EIO, SECRET), None),
            ('HTTP_CLOSE', None, OSError(errno.EIO, SECRET)),
        )
        for operation, error, close_error in cases:
            with self.subTest(operation=operation):
                x = DiagnosticLaunch(7, operation, error, close_error)
                result, output = x.run_cli()
                self.assertEqual(result, 1)
                record = self.error_record(output)
                self.assertEqual((record['phase'], record['operation']),
                                 ('WAIT_RECHECK_STATUS', operation))
                self.assertEqual(record['category'], 'HTTP_IO_ERROR')
                self.assert_no_native_or_retry(x, 7)

    def test_primary_read_failure_survives_secondary_close_failure(self):
        primary = TimeoutError(errno.ETIMEDOUT, SECRET)
        secondary = PermissionError(errno.EACCES, PRIVATE_URL)
        x = DiagnosticLaunch(7, 'HTTP_READ', primary, secondary)
        result, output = x.run_cli()
        self.assertEqual(result, 1)
        record = self.error_record(output)
        self.assertEqual((record['phase'], record['operation']),
                         ('WAIT_RECHECK_STATUS', 'HTTP_READ'))
        self.assertEqual(record['category'], 'HTTP_TIMEOUT')
        self.assertEqual(record['errno'], errno.ETIMEDOUT)
        self.assertEqual(record['exceptionClass'], m.exception_class(primary))
        self.assertEqual(record['causeClass'], m.exception_class(primary))
        self.assertEqual(record['secondaryExceptionClass'], 'PermissionError')
        self.assert_no_native_or_retry(x, 7)

    def test_errno_is_bounded_integer_and_excludes_boolean(self):
        for number, expected in ((True, None), (False, None), (-1, None),
                                 (4096, None), ('13', None), (13, 13)):
            with self.subTest(number=number):
                error = OSError(errno.EIO, SECRET)
                error.errno = number
                x = DiagnosticLaunch(1, 'HTTP_OPEN', error)
                _, output = x.run_cli()
                self.assertEqual(self.error_record(output)['errno'], expected)
                self.assert_no_native_or_retry(x, 1)

    def test_arbitrary_exception_class_and_arguments_are_not_emitted(self):
        private_type = type('SECRET_PRIVATE_EXCEPTION_CLASS', (OSError,), {})
        error = private_type(errno.EIO, SECRET, PRIVATE_URL)
        x = DiagnosticLaunch(1, 'HTTP_OPEN', error)
        _, output = x.run_cli()
        record = self.error_record(output)
        self.assertEqual(record['exceptionClass'], 'OtherOSError')
        self.assertEqual(record['causeClass'], 'OtherOSError')
        self.assertNotIn('SECRET_PRIVATE_EXCEPTION_CLASS', output)
        self.assert_no_native_or_retry(x, 1)

    def test_unknown_non_oserror_text_and_class_are_not_emitted(self):
        private_type = type('SECRET_PRIVATE_EXCEPTION_CLASS', (RuntimeError,), {})
        x = DiagnosticLaunch(1, 'HTTP_OPEN', private_type(SECRET, PRIVATE_URL))
        result, output = x.run_cli()
        self.assertEqual(result, 1)
        record = self.error_record(output)
        self.assertEqual(record['exceptionClass'], 'OtherException')
        self.assertEqual(record['category'], 'UNEXPECTED_ERROR')
        self.assertNotIn('SECRET_PRIVATE_EXCEPTION_CLASS', output)
        self.assert_no_native_or_retry(x, 1)

    def test_native_oserrors_are_single_invocation_failures(self):
        for error in (FileNotFoundError(errno.ENOENT, SECRET, PRIVATE_URL),
                      PermissionError(errno.EACCES, SECRET, PRIVATE_URL),
                      OSError(errno.EIO, SECRET, PRIVATE_URL)):
            with self.subTest(error_type=type(error).__name__):
                x = DiagnosticLaunch()
                native = x.native
                def fail(args, timeout, check):
                    native(args, timeout=timeout, check=check)
                    raise error
                x.native = fail
                result, output = x.run_cli()
                self.assertEqual(result, 1)
                record = self.error_record(output)
                self.assertEqual((record['phase'], record['operation']),
                                 ('NATIVE_SUBPROCESS_SPAWN', 'NATIVE_RUN'))
                self.assertEqual(record['category'], 'NATIVE_INVOCATION_IO_ERROR')
                self.assertEqual(record['exceptionClass'], type(error).__name__)
                self.assertEqual(record['errno'], error.errno)
                self.assertEqual(len(x.calls), 1)
                self.assertEqual(x.http_count, 7)

    def test_native_timeout_has_distinct_single_attempt_diagnostic(self):
        x = DiagnosticLaunch()
        native = x.native
        def timeout(args, timeout, check):
            native(args, timeout=timeout, check=check)
            raise subprocess.TimeoutExpired([SECRET, '--private-argument', PRIVATE_URL],
                                            timeout, output=SECRET, stderr=PRIVATE_URL)
        x.native = timeout
        result, output = x.run_cli()
        self.assertEqual(result, 1)
        record = self.error_record(output)
        self.assertEqual((record['phase'], record['operation']),
                         ('NATIVE_SUBPROCESS_SPAWN', 'NATIVE_RUN'))
        self.assertEqual(record['category'], 'NATIVE_TIMEOUT_RESTORATION_UNVERIFIED')
        self.assertEqual(record['exceptionClass'], 'TimeoutExpired')
        self.assertEqual(len(x.calls), 1)
        self.assertEqual(x.http_count, 7)

    def test_native_return_is_emitted_after_one_invocation_and_never_before(self):
        for code in (0, 3):
            with self.subTest(code=code):
                x = DiagnosticLaunch()
                x.exit_code = code
                emit = m.safe_print
                def observe_emit(text):
                    self.assertEqual(len(x.calls), 1)
                    x.events.append(('DIAGNOSTIC', json.loads(text)['event']))
                    emit(text)
                with patch.object(m, 'safe_print', side_effect=observe_emit):
                    result, output = x.run_cli()
                self.assertEqual(result, code)
                self.assertEqual(len(x.calls), 1)
                self.assertEqual(x.http_count, 7)
                emitted = records(output)
                self.assertEqual(len(emitted), 1)
                self.assertEqual(emitted[0]['event'], 'NATIVE_RETURN')
                self.assertEqual(emitted[0]['helperExit'], code)
                self.assertEqual((emitted[0]['phase'], emitted[0]['operation']),
                                 ('NATIVE_SUBPROCESS_RETURN', 'RETURN'))
                self.assertLess(next(i for i, event in enumerate(x.events)
                                     if event[0] == 'NATIVE'),
                                x.events.index(('DIAGNOSTIC', 'NATIVE_RETURN')))

    def test_each_cli_invocation_resets_diagnostic_state(self):
        original_diagnostics = m.Diagnostics
        traces = []
        launches = (
            DiagnosticLaunch(1, 'HTTP_OPEN', OSError(errno.EIO, SECRET)),
            DiagnosticLaunch(7, 'HTTP_READ', OSError(errno.EIO, SECRET)),
            DiagnosticLaunch(),
        )
        for x in launches:
            def fresh():
                trace = original_diagnostics()
                traces.append(trace)
                x.trace = trace
                return trace
            with patch.object(m, 'Diagnostics', side_effect=fresh):
                result, output = x.run(cli=True)
            record = records(output)[0]
            expected = ('PREFLIGHT_IDENTITY' if x.request == 1 else
                        'WAIT_RECHECK_STATUS' if x.request == 7 else
                        'NATIVE_SUBPROCESS_RETURN')
            self.assertEqual(record['phase'], expected)
            self.assertEqual(result, 1 if x.request else 0)
        self.assertEqual(len({id(trace) for trace in traces}), 3)
        self.assertIsNone(traces[-1].failure)

    def test_diagnostic_markers_are_bounded_and_memory_only(self):
        trace = m.Diagnostics()
        with patch.object(m, 'safe_print') as emit:
            for _ in range(5000):
                trace.mark('WAIT_RECHECK_STATUS', 'HTTP_READ')
        emit.assert_not_called()
        self.assertEqual(trace.sequence, 4096)
        self.assertEqual((trace.phase, trace.operation), ('WAIT_RECHECK_STATUS', 'HTTP_READ'))

    def test_broken_stdout_before_action_still_refuses_native(self):
        class BrokenStdout(io.StringIO):
            def write(self, text):
                raise BrokenPipeError(errno.EPIPE, SECRET)
        sink, fallback = BrokenStdout(), io.StringIO()
        x = DiagnosticLaunch()
        with contextlib.redirect_stderr(fallback):
            with patch('test_led_action_main.io.StringIO', return_value=sink):
                result, output = x.run_cli()
        self.assertEqual(result, 1)
        self.assertEqual(output, '')
        record = self.error_record(fallback.getvalue())
        self.assertEqual(record['exceptionClass'], 'BrokenPipeError')
        self.assert_no_native_or_retry(x, 3)


if __name__ == '__main__':
    unittest.main(verbosity=2)
