#!/usr/bin/env python3
"""One explicitly approved LED action. No script Start, STOP, EDR1 or installer API."""
import argparse
import contextlib
import errno
import getpass
import json
import math
import os
import pathlib
import re
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request

BUILD = 'ROUTEB-LOCK-FEEDBACK-20261023-v1'
FOCUS_SECONDS = 3
MAX_WAIT_AGE_MS = 1000  # Reject at this age, leaving nominal device-side margin.
COMMANDS = {
    'WAIT_FOR_NUM_ON': (0, 1, 1), 'WAIT_FOR_NUM_OFF': (1, 1, 0),
    'WAIT_FOR_NUM_CHANGE': (2, 1, None), 'WAIT_FOR_CAPS_ON': (3, 2, 1),
    'WAIT_FOR_CAPS_OFF': (4, 2, 0), 'WAIT_FOR_CAPS_CHANGE': (5, 2, None),
}

# Closed diagnostic vocabulary: never include exception text, URLs, credentials,
# paths, response data, native arguments or dynamically named exception classes.
PHASES = frozenset(('SETUP', 'PREFLIGHT_IDENTITY', 'PREFLIGHT_STATUS',
                    'PREFLIGHT_CONFIRM', 'CONSENT', 'REQUEST_INPUT', 'FOCUS',
                    'WAIT_INITIAL_IDENTITY', 'WAIT_POLL_STATUS', 'WAIT_POLL_IDENTITY',
                    'WAIT_RECHECK_STATUS', 'NATIVE_SUBPROCESS_SPAWN',
                    'NATIVE_SUBPROCESS_RETURN'))
OPERATIONS = frozenset(('CHECK', 'FILE_CHECK', 'CALL', 'HTTP_OPEN', 'HTTP_ENTER', 'HTTP_READ',
                        'HTTP_CLOSE', 'DECODE', 'INPUT', 'SLEEP', 'NATIVE_RUN', 'RETURN'))
POLICY_CODES = frozenset(('INVALID_REQUEST_ID', 'INVALID_IDENTITY_REPLY', 'UNKNOWN_BOOT',
    'BUILD_OR_RECEIVER_NOT_SAFE', 'CURRENT_REQUEST_SNAPSHOT_REQUIRED', 'REQUEST_MISMATCH',
    'REQUEST_ALREADY_TERMINAL', 'WAIT_TIMESTAMPS_REQUIRED', 'WAIT_TOO_LATE_NO_ACTION',
    'INVALID_ACTION', 'WRONG_TARGET', 'PREPARED_SESSION_CHANGED', 'HOST_CLOCK_ERROR',
    'WAIT_CHANGED', 'PRE_ACTION_CHECK_TOO_SLOW', 'NO_MATCHING_WAIT_WITHIN_30_SECONDS',
    'INVALID_IDENTITY', 'NATIVE_MAC_REQUIRED', 'COMPILE_NATIVE_HELPER_FIRST',
    'MISSING_PASSWORD', 'RESPONSE_LIMIT', 'INVALID_JSON_OBJECT',
    'IDLE_BEFORE_PREPARATION_REQUIRED'))


def safe_print(text):
    """Best effort diagnostics only; a broken log must never trigger a retry."""
    try:
        print(text, flush=True)
    except OSError:
        try:
            sys.stderr.write(text + '\n')
            sys.stderr.flush()
        except OSError:
            pass  # No usable diagnostic channel; no subsequent action/replay.


def exception_class(error):
    classes = ((urllib.error.HTTPError, 'HTTPError'), (urllib.error.URLError, 'URLError'),
               (subprocess.TimeoutExpired, 'TimeoutExpired'), (socket.timeout, 'SocketTimeout'),
               (TimeoutError, 'TimeoutError'), (ConnectionRefusedError, 'ConnectionRefusedError'),
               (FileNotFoundError, 'FileNotFoundError'), (PermissionError, 'PermissionError'),
               (BrokenPipeError, 'BrokenPipeError'), (OSError, 'OSError'),
               (json.JSONDecodeError, 'JSONDecodeError'), (ValueError, 'ValueError'),
               (EOFError, 'EOFError'), (KeyboardInterrupt, 'KeyboardInterrupt'))
    for cls, label in classes:
        if type(error) is cls:
            return label
    return 'OtherOSError' if isinstance(error, OSError) else 'OtherException'


class Diagnostics:
    """Bounded in-memory markers before I/O; emit only on error/native return.

    In particular no extra stdout I/O is inserted after the final freshness check
    and before the native invocation. One retained failure location survives HTTP
    context cleanup. A new cli() call always creates a fresh instance.
    """
    def __init__(self):
        self.phase, self.operation, self.sequence = 'SETUP', 'CHECK', 0
        self.failure = None
        self.failure_error = None

    def mark(self, phase, operation):
        assert phase in PHASES and operation in OPERATIONS
        self.phase, self.operation = phase, operation
        self.sequence = min(self.sequence + 1, 4096)

    @contextlib.contextmanager
    def span(self, phase, operation):
        self.mark(phase, operation)
        try:
            yield
        except BaseException as error:
            if self.failure is None:
                self.failure = (self.phase, self.operation, self.sequence)
                self.failure_error = error
            raise

    def emit_error(self, error):
        phase, operation, sequence = self.failure or (self.phase, self.operation, self.sequence)
        secondary = error if self.failure_error is not None and error is not self.failure_error else None
        error = self.failure_error if self.failure_error is not None else error
        cause = error
        # URLError.reason can be arbitrary text. Inspect only exception objects,
        # with bounded unwrapping; never str()/repr() either the error or reason.
        for _ in range(2):
            if isinstance(cause, urllib.error.URLError) and isinstance(cause.reason, BaseException):
                cause = cause.reason
            else:
                break
        number = getattr(cause, 'errno', None) if isinstance(cause, OSError) else None
        number = number if type(number) is int and 0 <= number <= 4095 else None
        http_status = None
        if isinstance(error, urllib.error.HTTPError):
            category = 'HTTP_ERROR'
            http_status = error.code if type(error.code) is int and 100 <= error.code <= 599 else None
        elif isinstance(error, subprocess.TimeoutExpired):
            category = 'NATIVE_TIMEOUT_RESTORATION_UNVERIFIED'
        elif phase == 'NATIVE_SUBPROCESS_SPAWN' and isinstance(error, OSError):
            category = 'NATIVE_INVOCATION_IO_ERROR'
        elif isinstance(cause, (socket.timeout, TimeoutError)):
            category = 'HTTP_TIMEOUT' if operation.startswith('HTTP_') else 'IO_TIMEOUT'
        elif isinstance(cause, ConnectionRefusedError) or number == errno.ECONNREFUSED:
            category = 'CONNECTION_REFUSED'
        elif isinstance(error, (urllib.error.URLError, OSError)):
            category = 'HTTP_IO_ERROR' if operation.startswith('HTTP_') else 'IO_ERROR'
        elif isinstance(error, (EOFError, KeyboardInterrupt)):
            category = 'CANCELLED'
        elif isinstance(error, json.JSONDecodeError):
            category = 'INVALID_JSON'
        elif isinstance(error, ValueError):
            category = 'POLICY_OR_INPUT'
        else:
            category = 'UNEXPECTED_ERROR'
        record = dict(event='HELPER_ERROR', phase=phase, operation=operation, sequence=sequence,
                      exceptionClass=exception_class(error), causeClass=exception_class(cause),
                      errno=number, category=category)
        if http_status is not None:
            record['httpStatus'] = http_status
        if secondary is not None:
            record['secondaryExceptionClass'] = exception_class(secondary)
        safe_print(json.dumps(record, sort_keys=True))

    def native_return(self, code):
        self.mark('NATIVE_SUBPROCESS_RETURN', 'RETURN')
        safe_print(json.dumps(dict(event='NATIVE_RETURN', phase=self.phase, operation=self.operation,
                                   sequence=self.sequence, helperExit=code), sort_keys=True))


def traced(trace, phase, callback):
    if trace is None:
        return callback()
    with trace.span(phase, 'CALL'):
        return callback()


def native_executable():
    # Resolve the script, not the executable: preserve the sibling symlink refusal.
    # A bare argv[0] otherwise searches PATH rather than the checked local file.
    helper = pathlib.Path(__file__).resolve(strict=True).with_name('led-action-native')
    if not helper.is_file() or helper.is_symlink() or not os.access(str(helper), os.X_OK):
        raise ValueError('COMPILE_NATIVE_HELPER_FIRST')
    return helper


def uint(value, bits):
    return type(value) is int and 0 <= value < (1 << bits)


def request_id(value):
    text = str(value).strip()
    if not re.fullmatch(r'[0-9]{1,20}', text) or not 0 < int(text) < (1 << 64):
        raise ValueError('INVALID_REQUEST_ID')
    return int(text)


def validate_identity(i):
    if not isinstance(i, dict):
        raise ValueError('INVALID_IDENTITY_REPLY')
    boot = i.get('bootMarker')
    if not isinstance(boot, str) or not re.fullmatch('[0-9a-fA-F]{16}', boot):
        raise ValueError('UNKNOWN_BOOT')
    if (i.get('buildId') != BUILD or not uint(i.get('state'), 8) or i['state'] == 1
            or not uint(i.get('feedbackSession'), 32) or i['feedbackSession'] == 0
            or i.get('snapshotSessionCoherent') is not True
            or i.get('usbConfiguredSample') is not True
            or i.get('usbSuspendedSample') is not False):
        raise ValueError('BUILD_OR_RECEIVER_NOT_SAFE')
    return boot, i['feedbackSession']


def validate_request_snapshot(s, request):
    if not isinstance(s, dict) or s.get('snapshotKind') != 'request-capture':
        raise ValueError('CURRENT_REQUEST_SNAPSHOT_REQUIRED')
    if s.get('routeBRequestId') != str(request):
        raise ValueError('REQUEST_MISMATCH')
    if s.get('routeBOwned') is not True:
        raise ValueError('REQUEST_ALREADY_TERMINAL')


def check_status(s, request, command):
    return (isinstance(s, dict) and s.get('snapshotKind') == 'request-capture'
            and s.get('routeBRequestId') == str(request) and s.get('routeBOwned') is True
            and s.get('routeBWaiting') is True and type(s.get('routeBPhase')) is int
            and s['routeBPhase'] == 6  # Existing coordinator Running, not Stopping.
            and type(s.get('routeBWaitCommand')) is int
            and s['routeBWaitCommand'] == COMMANDS[command][0]
            and uint(s.get('routeBWaitSession'), 32) and s['routeBWaitSession'] != 0)


def fresh_wait(s):
    captured, started = s.get('capturedAtMs'), s.get('routeBWaitStartedMs')
    if not uint(captured, 32) or not uint(started, 32):
        raise ValueError('WAIT_TIMESTAMPS_REQUIRED')
    # Both timestamps are from the device. Normal uint32 millis wrap is supported.
    if ((captured - started) & 0xffffffff) >= MAX_WAIT_AGE_MS:
        raise ValueError('WAIT_TOO_LATE_NO_ACTION')


def act(status, identity, invoke, request, command, value,
        clock=time.monotonic, sleep=time.sleep, prepared=None, trace=None):
    if (type(request) is not int or not 0 < request < (1 << 64)
            or command not in COMMANDS or type(value) is not int or value not in (0, 1)):
        raise ValueError('INVALID_ACTION')
    if COMMANDS[command][2] is not None and value != COMMANDS[command][2]:
        raise ValueError('WRONG_TARGET')
    initial = traced(trace, 'WAIT_INITIAL_IDENTITY', identity)
    baseline = validate_identity(initial)
    if prepared is not None and validate_identity(prepared) != baseline:
        raise ValueError('PREPARED_SESSION_CHANGED')
    started = last = clock()
    for _ in range(301):
        now = clock()
        if not math.isfinite(now) or not math.isfinite(started) or now < last:
            raise ValueError('HOST_CLOCK_ERROR')
        last = now
        if now - started >= 30:
            break
        s = traced(trace, 'WAIT_POLL_STATUS', status)
        validate_request_snapshot(s, request)
        if s.get('routeBWaiting') is True:
            if not check_status(s, request, command):
                raise ValueError('WAIT_CHANGED')
            fresh_wait(s)
            check_at = clock()
            if not math.isfinite(check_at) or check_at < last:
                raise ValueError('HOST_CLOCK_ERROR')
            # Bind identity then obtain the last matching request capture. No action
            # can be atomic with device STOP; observed cancellation must be refused.
            i = traced(trace, 'WAIT_POLL_IDENTITY', identity)
            if validate_identity(i) != baseline or i['feedbackSession'] != s['routeBWaitSession']:
                raise ValueError('BUILD_OR_RECEIVER_NOT_SAFE')
            again = traced(trace, 'WAIT_RECHECK_STATUS', status)
            if not check_status(again, request, command) or again['routeBWaitSession'] != s['routeBWaitSession']:
                raise ValueError('WAIT_CHANGED')
            fresh_wait(again)
            end = clock()
            if not math.isfinite(end) or end < check_at:
                raise ValueError('HOST_CLOCK_ERROR')
            if end - check_at >= 1 or end - started >= 30:
                raise ValueError('PRE_ACTION_CHECK_TOO_SLOW')
            # Exactly once; markers are memory-only before invoking the helper.
            result = traced(trace, 'NATIVE_SUBPROCESS_SPAWN',
                            lambda: invoke(COMMANDS[command][1], value))
            if trace is not None:
                trace.native_return(result)
            return result
        sleep(.1)
    raise ValueError('NO_MATCHING_WAIT_WITHIN_30_SECONDS')


def main(trace=None):
    trace = trace if trace is not None else Diagnostics()
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--serial', required=True)
    p.add_argument('--request', type=request_id,
                   help='Already assigned request ID; omit for prepared interactive flow')
    p.add_argument('--command', choices=sorted(COMMANDS), required=True)
    p.add_argument('--value', type=int, choices=[0, 1], required=True)
    p.add_argument('--host', default='192.168.4.1')
    a = p.parse_args()
    if not re.fullmatch('[A-Za-z0-9]{1,128}', a.serial) or not re.fullmatch('[0-9.]{7,15}', a.host):
        raise ValueError('INVALID_IDENTITY')
    if COMMANDS[a.command][2] is not None and a.value != COMMANDS[a.command][2]:
        raise ValueError('WRONG_TARGET')
    with trace.span('SETUP', 'FILE_CHECK'):
        if os.uname().sysname != 'Darwin':
            raise ValueError('NATIVE_MAC_REQUIRED')
        helper = native_executable()
    with trace.span('SETUP', 'INPUT'):
        password = getpass.getpass('Dashboard password (not saved): ')
    if not password:
        raise ValueError('MISSING_PASSWORD')
    # Existing password-header contract. No Basic-auth token or unused encoding.
    with trace.span('SETUP', 'CALL'):
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

    def read(path):
        phase = trace.phase
        req = urllib.request.Request('http://' + a.host + path,
                                     headers={'X-Duck-Password': password, 'Cache-Control': 'no-cache'})
        with trace.span(phase, 'HTTP_OPEN'):
            response = opener.open(req, timeout=.5)
        with trace.span(phase, 'HTTP_ENTER'):
            with response as stream:
                try:
                    with trace.span(phase, 'HTTP_READ'):
                        data = stream.read(65537)
                finally:
                    trace.mark(phase, 'HTTP_CLOSE')
        trace.mark(phase, 'DECODE')
        if len(data) > 65536:
            raise ValueError('RESPONSE_LIMIT')
        result = json.loads(data)
        if not isinstance(result, dict):
            raise ValueError('INVALID_JSON_OBJECT')
        return result

    prepared = traced(trace, 'PREFLIGHT_IDENTITY', lambda: read('/led-test'))
    validate_identity(prepared)
    s = traced(trace, 'PREFLIGHT_STATUS', lambda: read('/status'))
    if a.request is None:
        if (s.get('snapshotKind') != 'request-capture' or s.get('routeBOwned') is not False
                or type(s.get('routeBPhase')) is not int or s['routeBPhase'] != 0
                or s.get('running') is not False):
            raise ValueError('IDLE_BEFORE_PREPARATION_REQUIRED')
    else:
        # Compatibility mode: only an actually assigned owned request, never a
        # prediction of the next ID. Interactive preparation is recommended.
        validate_request_snapshot(s, a.request)
    confirm = traced(trace, 'PREFLIGHT_CONFIRM', lambda: read('/led-test'))
    if validate_identity(confirm) != validate_identity(prepared):
        raise ValueError('PREPARED_SESSION_CHANGED')
    with trace.span('CONSENT', 'INPUT'):
        if input('Separate physical approval required. Type APPLY ONCE: ') != 'APPLY ONCE':
            return 2
    if a.request is None:
        print('READY: authentication and native-file checks complete. No LED action sent.', flush=True)
        print('Now manually start the reviewed fixture ONCE. Enter its actual assigned request ID.', flush=True)
        with trace.span('REQUEST_INPUT', 'INPUT'):
            selected = request_id(input('Assigned request ID (no prediction): '))
    else:
        selected = a.request

    print('Switch to TextEdit now: %d-second focus countdown; no LED action yet.' % FOCUS_SECONDS, flush=True)
    with trace.span('FOCUS', 'SLEEP'):
        time.sleep(FOCUS_SECONDS)

    def invoke(usage, value):
        trace.mark('NATIVE_SUBPROCESS_SPAWN', 'NATIVE_RUN')
        return subprocess.run([str(helper), '--one-approved-action', a.serial, str(usage), str(value)],
                              timeout=5, check=False).returncode

    result = act(lambda: read('/status'), lambda: read('/led-test'), invoke,
                 selected, a.command, a.value, prepared=prepared, trace=trace)
    print('helperExit=%d; API acceptance is not device completion or host restoration proof.' % result,
          flush=True)
    return result


def cli():
    trace = Diagnostics()
    try:
        return main(trace=trace)
    except (EOFError, KeyboardInterrupt) as error:
        trace.emit_error(error)
        safe_print('CANCELLED; no automatic retry. If native action began, restoration is UNVERIFIED.')
    except urllib.error.HTTPError as error:
        trace.emit_error(error)
        code = error.code if type(error.code) is int and 100 <= error.code <= 599 else 0
        safe_print('HTTP_%d; no action retry.' % code)
    except (urllib.error.URLError, OSError) as error:
        trace.emit_error(error)
        safe_print('IO_UNAVAILABLE; no automatic retry. See sanitized phase diagnostic.')
    except subprocess.TimeoutExpired as error:
        trace.emit_error(error)
        safe_print('NATIVE_TIMEOUT_RESTORATION_UNVERIFIED; no retry.')
    except json.JSONDecodeError as error:
        trace.emit_error(error)
        safe_print('INVALID_JSON; no action.')
    except ValueError as error:
        trace.emit_error(error)
        code = error.args[0] if error.args and type(error.args[0]) is str else None
        safe_print(code if code in POLICY_CODES else 'INVALID_INPUT_NO_RETRY')
    except Exception as error:
        trace.emit_error(error)
        safe_print('UNEXPECTED_ERROR_NO_RETRY')
    return 1


if __name__ == '__main__':
    raise SystemExit(cli())
