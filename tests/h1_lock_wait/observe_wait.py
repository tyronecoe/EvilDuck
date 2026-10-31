# H1-only additive observer; historical parent SHA256 3967f44390bf25062dc03d3f355501bebc3b1f9d25745b308fa714524a4780d7
#!/usr/bin/env python3
"""Read-only request-correlated observation; bounded bytes/attempts, socket timeout.

Python 3.8+. urllib timeout is socket inactivity, not a hard response deadline.
A slow peer may outlive the polling window; Ctrl+C interrupts without device STOP.
"""
import argparse
import datetime
import getpass
import json
import math
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import warnings

BUILD = 'ROUTEB-INJECT-VAR-H1-EXPERIMENTAL-v1'
FIELDS = ('routeBRequestId', 'routeBOwned', 'snapshotKind', 'capturedAtMs',
          'routeBWaiting', 'routeBWaitCommand', 'routeBWaitStartedMs',
          'routeBWaitSession', 'routeBPhase', 'routeBReason', 'routeBLine',
          'routeBErrorCode')


class ObservationError(Exception):
    pass


def read_password(prompt):
    # Refuse getpass's echoing fallback before it can read any credential.
    with warnings.catch_warnings():
        warnings.simplefilter('error', getpass.GetPassWarning)
        try:
            return getpass.getpass(prompt)
        except getpass.GetPassWarning:
            raise ObservationError('PASSWORD_TTY_REQUIRED') from None


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class Client:
    def __init__(self, base, password, opener=None):
        u = urllib.parse.urlsplit(base)
        if (u.scheme not in ('http', 'https') or not u.hostname or u.username or
                u.password or u.query or u.fragment or u.path not in ('', '/')):
            raise ObservationError('INVALID_BASE_URL')
        self.base = base.rstrip('/')
        self.password = password
        self.opener = opener or urllib.request.build_opener(NoRedirect)

    def get(self, path):
        if path not in ('/caps-timing', '/status'):
            raise ObservationError('DISALLOWED_PATH')
        req = urllib.request.Request(self.base + path,
                                     headers={'X-Duck-Password': self.password},
                                     method='GET')
        try:
            with self.opener.open(req, timeout=2) as response:
                if response.status != 200:
                    raise ObservationError('HTTP_%d' % response.status)
                data = response.read(32769)
                if len(data) > 32768:
                    raise ObservationError('RESPONSE_TOO_LARGE')
            value = json.loads(data.decode('utf-8'))
        except urllib.error.HTTPError as error:
            raise ObservationError('HTTP_%d' % error.code) from None
        except (urllib.error.URLError, TimeoutError, OSError):
            raise ObservationError('NETWORK_OR_TIMEOUT') from None
        except (UnicodeError, ValueError):
            raise ObservationError('INVALID_JSON') from None
        if not isinstance(value, dict):
            raise ObservationError('INVALID_JSON_OBJECT')
        return value


def request_id(value):
    if not isinstance(value, str) or not re.fullmatch(r'[1-9][0-9]{0,19}', value):
        raise ObservationError('INVALID_REQUEST_ID')
    if int(value) > 18446744073709551615:
        raise ObservationError('INVALID_REQUEST_ID')
    return value


def snapshot(raw):
    try:
        out = {k: raw[k] for k in FIELDS}
    except KeyError:
        raise ObservationError('MISSING_STATUS_FIELD') from None
    request = out['routeBRequestId']
    if request != '0':
        request_id(request)
    if out['snapshotKind'] != 'request-capture':
        raise ObservationError('UNSUPPORTED_SNAPSHOT_KIND')
    for key in ('routeBOwned', 'routeBWaiting'):
        if type(out[key]) is not bool:
            raise ObservationError('INVALID_STATUS_TYPE')
    for key in ('capturedAtMs', 'routeBWaitCommand', 'routeBWaitStartedMs',
                'routeBWaitSession', 'routeBPhase', 'routeBReason',
                'routeBLine', 'routeBErrorCode'):
        if type(out[key]) is not int or not 0 <= out[key] <= 4294967295:
            raise ObservationError('INVALID_STATUS_TYPE')
    if out['routeBPhase'] > 8 or out['routeBReason'] > 9:
        raise ObservationError('UNSUPPORTED_STATUS_ENUM')
    return out


def monitor(client, wanted, seconds, emit, clock=time.monotonic, sleep=time.sleep,
            initial_capture=None):
    start = clock()
    previous_capture = initial_capture
    waiting_session = None
    seen_wait = False
    # Hard call bound is independent of clock behavior. No HTTP-error retries.
    for unused in range(int(math.ceil(seconds / 0.25)) + 1):
        if clock() - start >= seconds:
            break
        raw = client.get('/status')
        # urllib's socket timeout is not a total-response deadline. Never promote
        # a response that completed after our polling window to usable evidence.
        if clock() - start >= seconds:
            emit('OBSERVATION_WINDOW_EXCEEDED_DURING_REQUEST',
                 acceptanceDecision='UNVERIFIED', noAutomaticAction=True)
            return 2
        s = snapshot(raw)
        capture = s['capturedAtMs']
        if previous_capture is not None:
            delta = (capture - previous_capture) & 0xffffffff
            if delta == 0:
                emit('DUPLICATE_CAPTURE', current_wait_evidence=False)
                sleep(0.25)
                continue
            if delta >= 0x80000000:
                raise ObservationError('CAPTURE_CLOCK_OR_DEVICE_RESTART')
        previous_capture = capture
        if s['routeBRequestId'] != wanted:
            emit('REQUEST_MISMATCH', matched=False)
            if int(s['routeBRequestId']) > int(wanted):
                raise ObservationError('REQUEST_REPLACED')
            sleep(0.25)
            continue
        # Validate waiting metadata before presenting a matched capture as evidence.
        # Nonwaiting captures legitimately retain old wait metadata.
        if s['routeBWaiting']:
            if (not s['routeBOwned'] or s['routeBPhase'] != 6 or
                    s['routeBWaitCommand'] != 5):
                raise ObservationError('INCONSISTENT_OR_UNEXPECTED_WAIT')
            if ((capture - s['routeBWaitStartedMs']) & 0xffffffff) >= 0x80000000:
                raise ObservationError('WAIT_START_CLOCK_AMBIGUOUS')
            if waiting_session is not None and s['routeBWaitSession'] != waiting_session:
                raise ObservationError('WAIT_SESSION_CHANGED')
        emit('MATCHED_CAPTURE', elapsedObservationSeconds=round(clock()-start, 3),
             status=s, deliveryOrHostStateProven=False)
        if s['routeBWaiting']:
            if (not s['routeBOwned'] or s['routeBPhase'] != 6 or
                    s['routeBWaitCommand'] != 5):
                raise ObservationError('INCONSISTENT_OR_UNEXPECTED_WAIT')
            if waiting_session is not None and s['routeBWaitSession'] != waiting_session:
                raise ObservationError('WAIT_SESSION_CHANGED')
            waiting_session = s['routeBWaitSession']
            if not seen_wait:
                emit('MATCHED_CAPS_CHANGE_WAIT_OBSERVED', requestId=wanted,
                     action='Owner may now use existing STOP control once; observer sends no action')
            seen_wait = True
        if s['routeBPhase'] == 8:
            emit('QUARANTINED_CAPTURE', requestId=wanted,
                 acceptanceDecision='UNVERIFIED', automaticAction=False)
            return 2
        if not s['routeBOwned'] and s['routeBPhase'] == 0:
            emit('TERMINAL_CAPTURE', requestId=wanted,
                 waitingObserved=seen_wait, reason=s['routeBReason'],
                 phase=s['routeBPhase'], errorCode=s['routeBErrorCode'],
                 acceptanceDecision='OWNER_REVIEW_REQUIRED')
            return 0
        sleep(0.25)
    emit('OBSERVATION_WINDOW_ENDED', waitingObserved=seen_wait,
         acceptanceDecision='UNVERIFIED', noAutomaticAction=True)
    return 2


def main(argv=None, client_factory=Client, ask=input, secret=read_password,
         output=None, clock=time.monotonic, sleep=time.sleep):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', default='http://192.168.4.1')
    parser.add_argument('--seconds', type=int, default=45, choices=range(1, 121),
                        metavar='1..120')
    args = parser.parse_args(argv)
    output = output or sys.stdout

    def emit(event, **fields):
        fields.update(event=event, observedUtc=datetime.datetime.now(
            datetime.timezone.utc).isoformat())
        print(json.dumps(fields, sort_keys=True), file=output, flush=True)

    client = None
    try:
        password = secret('Dashboard password (not saved): ')
        if not password:
            raise ObservationError('MISSING_PASSWORD')
        client = client_factory(args.base, password)
        password = ''
        identity = client.get('/caps-timing')
        if identity.get('buildId') != BUILD:
            raise ObservationError('BUILD_ID_MISMATCH')
        initial = snapshot(client.get('/status'))  # Preflight before Start.
        if initial['routeBOwned'] or initial['routeBWaiting'] or initial['routeBPhase'] != 0:
            raise ObservationError('EXECUTION_NOT_IDLE')
        emit('READY', buildId=BUILD,
             instructions='No action sent. Start reviewed fixture manually ONCE, then enter its actual assigned request ID. Keep STOP accessible.')
        wanted = request_id(ask('Actual assigned request ID (no prediction): ').strip())
        if int(wanted) <= int(initial['routeBRequestId']):
            raise ObservationError('REQUEST_NOT_NEWER_THAN_PREFLIGHT')
        return monitor(client, wanted, args.seconds, emit, clock, sleep,
                       initial_capture=initial['capturedAtMs'])
    except ObservationError as error:
        emit('OBSERVER_ERROR', code=str(error), currentSnapshotAvailable=False,
             automaticAction=False, acceptanceDecision='UNVERIFIED')
        return 2
    except (EOFError, KeyboardInterrupt):
        emit('OBSERVER_INTERRUPTED', automaticAction=False,
             acceptanceDecision='UNVERIFIED')
        return 2
    finally:
        if client is not None:
            client.password = ''


if __name__ == '__main__':
    raise SystemExit(main())
