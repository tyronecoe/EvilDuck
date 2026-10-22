"""Bounded local diagnostics for the fixed-message test; never uploads data.

This module makes no requests when imported. The only password-bearing operation
is an explicitly constructed client's direct local HTTP request. No environment
proxy, redirect, retry, report write or arbitrary-message endpoint is used.
"""
import http.client
import io
import ipaddress
import json
import re
import socket
import time
import urllib.parse

BUILD = "CAPS-STOP-TRACE-20261019-v1"
MESSAGE = b"EVILDUCK TEST 123"
MAX_BODY = 8192
MAX_WIRE = 16384
UINT32 = (1 << 32) - 1
UINT64 = (1 << 64) - 1
_NETWORKS = tuple(ipaddress.IPv4Network(n) for n in
                  ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16", "169.254.0.0/16"))
_RECEIVER = ("accepted", "id", "lengthOrNull", "padding", "notConfigured", "staleSession", "suspended")
_LIFECYCLE = ("mount", "unmount", "suspend", "resume")


class DeviceError(Exception):
    """A safe stable code: no server body, endpoint or password in the message."""
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def _fail(code="INVALID_DIAGNOSTICS"):
    raise DeviceError(code)


def _uint(value, maximum=UINT32):
    if type(value) is not int or not 0 <= value <= maximum:
        _fail()
    return value


def _boolean(value):
    if type(value) is not bool:
        _fail()
    return value


def _decimal(value):
    if not isinstance(value, str) or not re.fullmatch(r"0|[1-9][0-9]{0,19}", value):
        _fail()
    if int(value) > UINT64:
        _fail()
    return value


def _object(value):
    if type(value) is not dict:
        _fail()
    return value


def validate_snapshot(value):
    """Validate required installed-build fields and discard unneeded text."""
    try:
        value = _object(value)
        if value["buildId"] != BUILD:
            _fail("BUILD_MISMATCH")
        boot = value["bootMarker"]
        if not isinstance(boot, str) or not re.fullmatch(r"[0-9a-f]{16}", boot) or int(boot, 16) == 0:
            _fail()
        out = {"buildId": BUILD, "bootMarker": boot}
        for key in ("feedbackSession", "reports", "rejected", "overflow", "callbacks", "rawArrivals"):
            out[key] = _uint(value[key])
        for key, maximum in (("state", 8), ("mask", 7), ("activeProtocolSample", 1),
                             ("keyboardReportId", 255), ("interfaceProtocol", 2)):
            out[key] = _uint(value[key], maximum)
        for key in ("integrity", "observed", "snapshotSessionCoherent", "ledEvidenceValid",
                    "usbBusConnectedSample", "usbConfiguredSample", "usbSuspendedSample", "hidInReadySample"):
            out[key] = _boolean(value[key])
        for key in ("capturedAtUs", "uptimeUs", "lastReportUs"):
            out[key] = _decimal(value[key])
        for key in ("num", "caps", "scroll", "lastKnownCaps", "lastKnownNum"):
            v = value[key]
            out[key] = None if v is None else _boolean(v)
        age = value["reportAgeUs"]
        out["reportAgeUs"] = None if age is None else _decimal(age)
        out["freshnessWindowUs"] = _uint(value["freshnessWindowUs"])
        if out["freshnessWindowUs"] != 5000000:
            _fail("FRESHNESS_POLICY_MISMATCH")
        out["receiverOutcome"] = {k: _uint(_object(value["receiverOutcome"])[k]) for k in _RECEIVER}
        out["lifecycle"] = {k: _uint(_object(value["lifecycle"])[k]) for k in _LIFECYCLE}
        # A saturated baseline cannot reveal another event or error, so reject
        # it before the workflow performs its first probe write.
        if (any(out[k] == UINT32 for k in ("reports", "callbacks", "rawArrivals", "rejected", "overflow")) or
                any(n == UINT32 for n in out["receiverOutcome"].values()) or
                any(n == UINT32 for n in out["lifecycle"].values())):
            _fail("COUNTER_INVALID")
        if not out["snapshotSessionCoherent"]:
            _fail("SESSION_INCOHERENT")
        if not out["usbBusConnectedSample"] or not out["usbConfiguredSample"] or out["usbSuspendedSample"]:
            _fail("USB_NOT_READY")
        if out["activeProtocolSample"] != 1 or out["keyboardReportId"] != 1:
            _fail("UNSUPPORTED_PROTOCOL")
        captured, last = int(out["capturedAtUs"]), int(out["lastReportUs"])
        if captured != int(out["uptimeUs"]):
            _fail("DEVICE_CLOCK_INVALID")
        # Receiver and metadata use distinct locks. A concurrent callback may
        # postdate the request's sampled capture time; it must remain stale,
        # never be promoted to fresh evidence by this validator.
        if last > captured and (out["reportAgeUs"] is not None or out["ledEvidenceValid"]):
            _fail("DEVICE_CLOCK_INVALID")
        if out["reportAgeUs"] is not None and int(out["reportAgeUs"]) != captured - last:
            _fail("DEVICE_CLOCK_INVALID")
        if out["integrity"] and out["state"] != 2:
            _fail("RECEIVER_STATE_INVALID")
        return out
    except (KeyError, TypeError, ValueError):
        _fail()


def identity(snapshot):
    s = validate_snapshot(snapshot)
    return s["buildId"], s["bootMarker"], s["feedbackSession"], s["activeProtocolSample"], s["keyboardReportId"]


def validate_session(previous, current):
    """Reject discontinuities, new errors, saturation and backwards counters."""
    before, after = validate_snapshot(previous), validate_snapshot(current)
    if identity(before) != identity(after) or before["lifecycle"] != after["lifecycle"]:
        _fail("SESSION_CHANGED")
    if int(after["capturedAtUs"]) < int(before["capturedAtUs"]):
        _fail("DEVICE_CLOCK_INVALID")
    for key in ("reports", "callbacks", "rawArrivals"):
        if after[key] < before[key] or after[key] == UINT32:
            _fail("COUNTER_INVALID")
    for key in ("rejected", "overflow"):
        if after[key] != before[key] or after[key] == UINT32:
            _fail("NEW_RECEIVER_ERROR")
    for key in _RECEIVER:
        old, new = before["receiverOutcome"][key], after["receiverOutcome"][key]
        if new < old or new == UINT32:
            _fail("COUNTER_INVALID")
        if key != "accepted" and old != new:
            _fail("NEW_RECEIVER_ERROR")
    return after


def _new_report(before, after):
    if (after["reports"] <= before["reports"] or
            after["receiverOutcome"]["accepted"] <= before["receiverOutcome"]["accepted"] or
            int(after["lastReportUs"]) <= int(before["capturedAtUs"])):
        _fail("NO_NEW_DEVICE_REPORT")


def validate_probe(before, after, num, caps):
    """A successful API call is not enough: require new expected LED evidence."""
    if type(num) is not int or num not in (0, 1) or type(caps) is not int or caps not in (0, 1):
        _fail("INVALID_EXPECTATION")
    old = validate_snapshot(before)
    s = validate_session(old, after)
    if old["state"] == 1 or s["state"] == 1:
        _fail("RECEIVER_ALREADY_ARMED")
    if old["state"] != s["state"] or old["integrity"] != s["integrity"]:
        _fail("RECEIVER_CHANGED_DURING_PROBE")
    _new_report(old, s)
    if not s["observed"] or not s["ledEvidenceValid"] or s["reportAgeUs"] is None:
        _fail("LED_EVIDENCE_NOT_FRESH")
    if int(s["reportAgeUs"]) > s["freshnessWindowUs"]:
        _fail("LED_EVIDENCE_NOT_FRESH")
    if s["mask"] & 3 != (num | (caps << 1)) or s["num"] is not bool(num) or s["caps"] is not bool(caps):
        _fail("LED_STATE_MISMATCH")
    return s


def validate_armed(previous, armed):
    """The authenticated fresh start receipt clears previous message success."""
    before = validate_snapshot(previous)
    if before["state"] == 1:
        _fail("RECEIVER_ALREADY_ARMED")
    s = validate_session(before, armed)
    if s["state"] != 1 or s["integrity"]:
        _fail("FRESH_ARM_NOT_CONFIRMED")
    return s


def validate_complete(armed, current):
    before = validate_snapshot(armed)
    if before["state"] != 1 or before["integrity"]:
        _fail("FRESH_ARM_NOT_CONFIRMED")
    s = validate_session(before, current)
    if s["state"] != 2 or not s["integrity"]:
        _fail("MESSAGE_NOT_COMPLETE")
    _new_report(before, s)
    # A verified result persists in RAM. LED freshness is not message freshness.
    return s


def _pairs(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            _fail("INVALID_JSON")
        out[key] = value
    return out


def _json(data):
    try:
        return json.loads(data.decode("utf-8"), object_pairs_hook=_pairs,
                          parse_constant=lambda _: _fail("INVALID_JSON"))
    except (ValueError, UnicodeError, RecursionError):
        _fail("INVALID_JSON")


def _address(url):
    try:
        if not isinstance(url, str) or url != url.strip() or any(ord(c) < 33 for c in url):
            _fail("INVALID_LOCAL_ADDRESS")
        p = urllib.parse.urlsplit(url)
        if (p.scheme != "http" or p.username is not None or p.password is not None or
                p.path not in ("", "/") or p.query or p.fragment):
            _fail("INVALID_LOCAL_ADDRESS")
        ip = ipaddress.IPv4Address(p.hostname)
        if str(ip) != p.hostname or not any(ip in n for n in _NETWORKS):
            _fail("INVALID_LOCAL_ADDRESS")
        port = 80 if p.port is None else p.port
        if not 1 <= port <= 65535:
            _fail("INVALID_LOCAL_ADDRESS")
        canonical = str(ip) if p.port is None else "%s:%d" % (ip, port)
        if p.netloc != canonical or "?" in url or "#" in url:
            _fail("INVALID_LOCAL_ADDRESS")
        return str(ip), port
    except (ValueError, TypeError):
        _fail("INVALID_LOCAL_ADDRESS")


class _Reader(io.RawIOBase):
    """One absolute deadline includes trickled response headers and body."""
    def __init__(self, sock, deadline):
        super().__init__()
        self.sock, self.deadline, self.total = sock, deadline, 0
        # Keep the socket's makefile reference alive when HTTPConnection closes
        # its own reference after an HTTP/1.0 or Connection:close response.
        self._raw = sock.makefile("rb", buffering=0)

    def readable(self):
        return True

    def readinto(self, data):
        left = self.deadline - time.monotonic()
        if left <= 0:
            raise TimeoutError()
        self.sock.settimeout(left)
        size = min(len(data), MAX_WIRE + 1 - self.total)
        if size <= 0:
            _fail("RESPONSE_TOO_LARGE")
        count = self._raw.readinto(memoryview(data)[:size])
        self.total += count
        if self.total > MAX_WIRE:
            _fail("RESPONSE_TOO_LARGE")
        return count

    def close(self):
        if not self.closed:
            self._raw.close()
        super().close()


class _Socket:
    def __init__(self, sock, deadline):
        self.sock, self.deadline = sock, deadline

    def __getattr__(self, key):
        return getattr(self.sock, key)

    def makefile(self, mode):
        if mode != "rb":
            _fail("HTTP_PROTOCOL_ERROR")
        return io.BufferedReader(_Reader(self.sock, self.deadline))

    def sendall(self, data):
        left = self.deadline - time.monotonic()
        if left <= 0:
            raise TimeoutError()
        self.sock.settimeout(left)
        self.sock.sendall(data)


class DeviceClient:
    """Direct, single-attempt local HTTP; `_connection_factory` is test injection."""
    def __init__(self, base_url, password, timeout=2.0, *, _connection_factory=None):
        self.host, self.port = _address(base_url)
        if not isinstance(password, str) or not password or len(password) > 256:
            _fail("AUTH_FORMAT")
        try:
            password.encode("latin-1")
        except UnicodeError:
            _fail("AUTH_FORMAT")
        if any(ord(c) < 32 or ord(c) == 127 for c in password):
            _fail("AUTH_FORMAT")
        if isinstance(timeout, bool) or not isinstance(timeout, (float, int)) or not 0 < timeout <= 2:
            _fail("INVALID_TIMEOUT")
        self._password, self.timeout = password, float(timeout)
        self._factory = _connection_factory or http.client.HTTPConnection

    def _request(self, path, method="GET", text=False):
        allowed = {("GET", "/led-test"), ("GET", "/caps-timing"), ("GET", "/status"), ("GET", "/led-test/data"),
                   ("POST", "/led-test/start"), ("POST", "/led-test/stop")}
        if (method, path) not in allowed:
            _fail("ENDPOINT_NOT_ALLOWED")
        connection = None
        response = None
        try:
            end = time.monotonic() + self.timeout
            connection = self._factory(self.host, self.port, timeout=self.timeout)
            connection.connect()
            connection.sock = _Socket(connection.sock, end)
            connection.request(method, path, body=None, headers={
                "X-Duck-Password": self._password,
                "Accept": "text/plain" if text else "application/json",
                "Connection": "close", "Cache-Control": "no-cache"})
            response = connection.getresponse()
            if response.status != 200:
                if 300 <= response.status < 400:
                    _fail("REDIRECT_REFUSED")
                if response.status == 401:
                    _fail("AUTH_REFUSED")
                if response.status == 409:
                    _fail("DEVICE_BUSY")
                _fail("HTTP_STATUS_ERROR")
            if response.headers.get_all("Transfer-Encoding"):
                _fail("HTTP_PROTOCOL_ERROR")
            lengths = response.headers.get_all("Content-Length") or []
            if len(lengths) > 1:
                _fail("HTTP_PROTOCOL_ERROR")
            expected = None
            if lengths:
                if not re.fullmatch(r"0|[1-9][0-9]{0,7}", lengths[0]):
                    _fail("HTTP_PROTOCOL_ERROR")
                expected = int(lengths[0])
                if expected > MAX_BODY:
                    _fail("RESPONSE_TOO_LARGE")
            content_types = response.headers.get_all("Content-Type") or []
            wanted = "text/plain" if text else "application/json"
            if len(content_types) != 1 or content_types[0].split(";", 1)[0].strip().lower() != wanted:
                _fail("CONTENT_TYPE_MISMATCH")
            data = response.read(MAX_BODY + 1)
            if len(data) > MAX_BODY:
                _fail("RESPONSE_TOO_LARGE")
            if expected is not None and len(data) != expected:
                _fail("HTTP_TRUNCATED")
            if time.monotonic() > end:
                _fail("HTTP_TIMEOUT")
            if text:
                if data != MESSAGE:
                    _fail("FIXED_MESSAGE_MISMATCH")
                return data
            return _json(data)
        except DeviceError:
            raise
        except (socket.timeout, TimeoutError):
            _fail("HTTP_TIMEOUT")
        except (http.client.IncompleteRead, http.client.RemoteDisconnected):
            _fail("HTTP_TRUNCATED")
        except (OSError, http.client.HTTPException, ValueError, UnicodeError):
            _fail("HTTP_CONNECTION_ERROR")
        finally:
            if response is not None:
                response.close()
            if connection is not None:
                connection.close()

    def read(self):
        return validate_snapshot(self._request("/led-test"))

    def start(self):
        return validate_snapshot(self._request("/led-test/start", "POST"))

    def stop(self):
        return validate_snapshot(self._request("/led-test/stop", "POST"))

    def data(self):
        return self._request("/led-test/data", text=True)

    def idle(self):
        value = self._request("/status")
        try:
            if _object(value)["snapshotKind"] != "request-capture":
                _fail("EXECUTION_SNAPSHOT_UNCONFIRMED")
            return {"snapshotKind": "request-capture",
                    "running": _boolean(value["running"]),
                    "routeBOwned": _boolean(value["routeBOwned"]),
                    "hid": _boolean(value["hid"])}
        except (KeyError, TypeError, ValueError):
            _fail("INVALID_EXECUTION_DIAGNOSTICS")

    def timing(self):
        value = self._request("/caps-timing")
        try:
            if _object(value)["buildId"] != BUILD:
                _fail("BUILD_MISMATCH")
            selected = _uint(value["selectedMs"], 500)
            if selected not in (5, 500) or value["snapshotKind"] != "request-capture":
                _fail()
            return {"buildId": BUILD, "selectedMs": selected,
                    "requestCapsMs": _uint(value["requestCapsMs"], 500),
                    "requestId": _decimal(value["requestId"]),
                    "owned": _boolean(value["owned"]), "snapshotKind": "request-capture"}
        except (KeyError, TypeError, ValueError):
            _fail()
