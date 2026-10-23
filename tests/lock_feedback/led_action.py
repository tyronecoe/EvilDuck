#!/usr/bin/env python3
"""One explicitly approved LED action. No script Start, STOP, EDR1 or installer API."""
import argparse
import getpass
import json
import math
import os
import pathlib
import re
import subprocess
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
        clock=time.monotonic, sleep=time.sleep, prepared=None):
    if (type(request) is not int or not 0 < request < (1 << 64)
            or command not in COMMANDS or type(value) is not int or value not in (0, 1)):
        raise ValueError('INVALID_ACTION')
    if COMMANDS[command][2] is not None and value != COMMANDS[command][2]:
        raise ValueError('WRONG_TARGET')
    initial = identity()
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
        s = status()
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
            i = identity()
            if validate_identity(i) != baseline or i['feedbackSession'] != s['routeBWaitSession']:
                raise ValueError('BUILD_OR_RECEIVER_NOT_SAFE')
            again = status()
            if not check_status(again, request, command) or again['routeBWaitSession'] != s['routeBWaitSession']:
                raise ValueError('WAIT_CHANGED')
            fresh_wait(again)
            end = clock()
            if not math.isfinite(end) or end < check_at:
                raise ValueError('HOST_CLOCK_ERROR')
            if end - check_at >= 1 or end - started >= 30:
                raise ValueError('PRE_ACTION_CHECK_TOO_SLOW')
            return invoke(COMMANDS[command][1], value)  # Exactly once; never replay.
        sleep(.1)
    raise ValueError('NO_MATCHING_WAIT_WITHIN_30_SECONDS')


def main():
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
    if os.uname().sysname != 'Darwin':
        raise ValueError('NATIVE_MAC_REQUIRED')
    helper = pathlib.Path(__file__).with_name('led-action-native')
    if not helper.is_file() or helper.is_symlink() or not os.access(str(helper), os.X_OK):
        raise ValueError('COMPILE_NATIVE_HELPER_FIRST')
    password = getpass.getpass('Dashboard password (not saved): ')
    if not password:
        raise ValueError('MISSING_PASSWORD')
    # Existing password-header contract. No Basic-auth token or unused encoding.
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

    def read(path):
        req = urllib.request.Request('http://' + a.host + path,
                                     headers={'X-Duck-Password': password, 'Cache-Control': 'no-cache'})
        with opener.open(req, timeout=.5) as response:
            data = response.read(65537)
        if len(data) > 65536:
            raise ValueError('RESPONSE_LIMIT')
        result = json.loads(data)
        if not isinstance(result, dict):
            raise ValueError('INVALID_JSON_OBJECT')
        return result

    prepared = read('/led-test')
    validate_identity(prepared)
    s = read('/status')
    if a.request is None:
        if (s.get('snapshotKind') != 'request-capture' or s.get('routeBOwned') is not False
                or type(s.get('routeBPhase')) is not int or s['routeBPhase'] != 0
                or s.get('running') is not False):
            raise ValueError('IDLE_BEFORE_PREPARATION_REQUIRED')
    else:
        # Compatibility mode: only an actually assigned owned request, never a
        # prediction of the next ID. Interactive preparation is recommended.
        validate_request_snapshot(s, a.request)
    confirm = read('/led-test')
    if validate_identity(confirm) != validate_identity(prepared):
        raise ValueError('PREPARED_SESSION_CHANGED')
    if input('Separate physical approval required. Type APPLY ONCE: ') != 'APPLY ONCE':
        return 2
    if a.request is None:
        print('READY: authentication and native-file checks complete. No LED action sent.', flush=True)
        print('Now manually start the reviewed fixture ONCE. Enter its actual assigned request ID.', flush=True)
        selected = request_id(input('Assigned request ID (no prediction): '))
    else:
        selected = a.request

    print('Switch to TextEdit now: %d-second focus countdown; no LED action yet.' % FOCUS_SECONDS, flush=True)
    time.sleep(FOCUS_SECONDS)

    def invoke(usage, value):
        return subprocess.run([str(helper), '--one-approved-action', a.serial, str(usage), str(value)],
                              timeout=5, check=False).returncode

    result = act(lambda: read('/status'), lambda: read('/led-test'), invoke,
                 selected, a.command, a.value, prepared=prepared)
    print('helperExit=%d; API acceptance is not device completion or host restoration proof.' % result,
          flush=True)
    return result


def cli():
    try:
        return main()
    except (EOFError, KeyboardInterrupt):
        print('CANCELLED; no automatic retry. If native action began, restoration is UNVERIFIED.')
    except urllib.error.HTTPError as error:
        print('HTTP_%d; no action retry.' % error.code)
    except (urllib.error.URLError, OSError):
        print('IO_UNAVAILABLE; no automatic retry.')
    except subprocess.TimeoutExpired:
        print('NATIVE_TIMEOUT_RESTORATION_UNVERIFIED; no retry.')
    except json.JSONDecodeError:
        print('INVALID_JSON; no action.')
    except ValueError as error:
        # Only our fixed diagnostic strings are printed; never echo supplied
        # credentials or urllib's potentially sensitive header-error contents.
        code = str(error)
        print(code if re.fullmatch('[A-Z0-9_]{1,64}', code) else 'INVALID_INPUT_NO_RETRY')
    return 1


if __name__ == '__main__':
    raise SystemExit(cli())
