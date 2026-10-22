"""Synthetic diagnostics and loopback HTTP tests; no USB or owner network."""
import copy
import http.client
import http.server
import importlib.util
import json
import pathlib
import threading
import time
import unittest

_PATH = pathlib.Path(__file__).resolve().parents[2] / "host_tests/led_return/mac_fixed_message/device.py"
_SPEC = importlib.util.spec_from_file_location("fixed_device", _PATH)
device = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(device)


def snapshot(**changes):
    s = dict(buildId=device.BUILD, bootMarker="0123456789abcdef", feedbackSession=3,
             reports=1, rejected=0, overflow=0, callbacks=1, rawArrivals=1,
             state=0, mask=0, activeProtocolSample=1, keyboardReportId=1, interfaceProtocol=0,
             integrity=False, observed=True, snapshotSessionCoherent=True, ledEvidenceValid=True,
             usbBusConnectedSample=True, usbConfiguredSample=True, usbSuspendedSample=False,
             hidInReadySample=True, capturedAtUs="1000000", uptimeUs="1000000", lastReportUs="500000",
             num=False, caps=False, scroll=False, lastKnownCaps=False, lastKnownNum=False,
             reportAgeUs="500000", freshnessWindowUs=5000000,
             receiverOutcome=dict(accepted=1, id=0, lengthOrNull=0, padding=0,
                                  notConfigured=0, staleSession=0, suspended=0),
             lifecycle=dict(mount=1, unmount=0, suspend=0, resume=0))
    s.update(changes)
    return s


def newer(s, num=1, caps=0):
    result = copy.deepcopy(s)
    before = int(s["capturedAtUs"])
    result.update(capturedAtUs=str(before + 100000), uptimeUs=str(before + 100000),
                  lastReportUs=str(before + 50000), reportAgeUs="50000", observed=True,
                  ledEvidenceValid=True, mask=num | caps << 1, num=bool(num), caps=bool(caps),
                  lastKnownNum=bool(num), lastKnownCaps=bool(caps))
    for k in ("reports", "callbacks", "rawArrivals"):
        result[k] += 1
    result["receiverOutcome"]["accepted"] += 1
    return result


class EvidenceTests(unittest.TestCase):
    def rejected(self, code, function, *args):
        with self.assertRaises(device.DeviceError) as caught:
            function(*args)
        self.assertEqual(caught.exception.code, code)
        self.assertEqual(str(caught.exception), code)

    def test_valid_snapshot_discards_private_unknown_fields(self):
        s = snapshot(ssid="synthetic-private", arbitrary="not retained")
        result = device.validate_snapshot(s)
        self.assertNotIn("ssid", result)
        self.assertNotIn("arbitrary", result)
        self.assertEqual(device.identity(result), (device.BUILD, "0123456789abcdef", 3, 1, 1))

    def test_required_fields_and_exact_types(self):
        for key in ("reports", "capturedAtUs", "integrity", "receiverOutcome", "lifecycle"):
            s = snapshot()
            del s[key]
            self.rejected("INVALID_DIAGNOSTICS", device.validate_snapshot, s)
        for key, bad in (("reports", True), ("state", False), ("feedbackSession", -1),
                         ("integrity", 1), ("mask", 8), ("uptimeUs", 1000000),
                         ("capturedAtUs", "01"), ("lastReportUs", str(1 << 64))):
            self.rejected("INVALID_DIAGNOSTICS", device.validate_snapshot, snapshot(**{key: bad}))

    def test_build_and_boot_identity(self):
        self.rejected("BUILD_MISMATCH", device.validate_snapshot, snapshot(buildId="old-build"))
        for boot in ("", "0" * 16, "bad", "0123456789abcdef0", 123):
            self.rejected("INVALID_DIAGNOSTICS", device.validate_snapshot, snapshot(bootMarker=boot))

    def test_link_protocol_and_coherence_fail_closed(self):
        for changes, code in (({"usbConfiguredSample": False}, "USB_NOT_READY"),
                              ({"usbBusConnectedSample": False}, "USB_NOT_READY"),
                              ({"usbSuspendedSample": True}, "USB_NOT_READY"),
                              ({"activeProtocolSample": 0}, "UNSUPPORTED_PROTOCOL"),
                              ({"keyboardReportId": 2}, "UNSUPPORTED_PROTOCOL"),
                              ({"snapshotSessionCoherent": False}, "SESSION_INCOHERENT")):
            self.rejected(code, device.validate_snapshot, snapshot(**changes))

    def test_device_clock_consistency(self):
        self.rejected("DEVICE_CLOCK_INVALID", device.validate_snapshot, snapshot(uptimeUs="999999"))
        self.rejected("DEVICE_CLOCK_INVALID", device.validate_snapshot, snapshot(reportAgeUs="1"))
        self.rejected("DEVICE_CLOCK_INVALID", device.validate_snapshot, snapshot(lastReportUs="1000001"))

    def test_concurrent_future_report_is_stale_not_corruption(self):
        s = snapshot(lastReportUs="1000010", reportAgeUs=None, ledEvidenceValid=False, num=None, caps=None)
        self.assertFalse(device.validate_snapshot(s)["ledEvidenceValid"])
        before = snapshot(capturedAtUs="900000", uptimeUs="900000", reportAgeUs="400000")
        s["reports"] += 1
        s["receiverOutcome"]["accepted"] += 1
        self.rejected("LED_EVIDENCE_NOT_FRESH", device.validate_probe, before, s, 0, 0)

    def test_session_and_lifecycle_discontinuity(self):
        before = snapshot()
        for change in ({"feedbackSession": 4}, {"bootMarker": "fedcba9876543210"}):
            self.rejected("SESSION_CHANGED", device.validate_session, before, newer(snapshot(**change)))
        after = newer(before)
        after["lifecycle"]["suspend"] += 1
        self.rejected("SESSION_CHANGED", device.validate_session, before, after)

    def test_gray_probe_uses_new_reports_for_each_expected_state(self):
        before = snapshot()
        for num, caps in ((1, 0), (1, 1), (0, 1), (0, 0)):
            after = newer(before, num, caps)
            self.assertEqual(device.validate_probe(before, after, num, caps)["mask"], num | caps << 1)
            before = after

    def test_api_success_without_new_report_is_not_capability(self):
        self.rejected("NO_NEW_DEVICE_REPORT", device.validate_probe, snapshot(), snapshot(), 0, 0)
        after = newer(snapshot())
        after["receiverOutcome"]["accepted"] = 1
        self.rejected("NO_NEW_DEVICE_REPORT", device.validate_probe, snapshot(), after, 1, 0)

    def test_probe_rejects_stale_or_wrong_mask(self):
        before = snapshot()
        self.rejected("LED_STATE_MISMATCH", device.validate_probe, before, newer(before), 0, 1)
        self.rejected("INVALID_EXPECTATION", device.validate_probe, before, newer(before), True, 0)
        after = newer(before)
        after["ledEvidenceValid"] = False
        self.rejected("LED_EVIDENCE_NOT_FRESH", device.validate_probe, before, after, 1, 0)
        after = newer(before)
        after.update(capturedAtUs="8000000", uptimeUs="8000000", reportAgeUs="6950000")
        self.rejected("LED_EVIDENCE_NOT_FRESH", device.validate_probe, before, after, 1, 0)

    def test_receiver_arming_or_reset_during_probe_is_not_success(self):
        before = snapshot()
        after = newer(before)
        after["state"] = 1
        self.rejected("RECEIVER_ALREADY_ARMED", device.validate_probe, before, after, 1, 0)
        self.rejected("RECEIVER_ALREADY_ARMED", device.validate_probe, snapshot(state=1), after, 1, 0)
        after = newer(before)
        after["state"] = 3
        self.rejected("RECEIVER_CHANGED_DURING_PROBE", device.validate_probe, before, after, 1, 0)

    def test_receiver_errors_and_counter_saturation(self):
        before = snapshot()
        for key in ("rejected", "overflow"):
            after = newer(before)
            after[key] += 1
            self.rejected("NEW_RECEIVER_ERROR", device.validate_session, before, after)
        for key in ("id", "lengthOrNull", "padding", "notConfigured", "staleSession", "suspended"):
            after = newer(before)
            after["receiverOutcome"][key] += 1
            self.rejected("NEW_RECEIVER_ERROR", device.validate_session, before, after)
        for value in (0, device.UINT32):
            after = newer(before)
            after["reports"] = value
            self.rejected("COUNTER_INVALID", device.validate_session, before, after)

    def test_saturated_baseline_is_rejected_before_any_probe(self):
        for key in ("reports", "callbacks", "rawArrivals", "rejected", "overflow"):
            self.rejected("COUNTER_INVALID", device.validate_snapshot, snapshot(**{key: device.UINT32}))
        for group, key in (("receiverOutcome", "accepted"), ("receiverOutcome", "id"), ("lifecycle", "mount")):
            s = snapshot()
            s[group][key] = device.UINT32
            self.rejected("COUNTER_INVALID", device.validate_snapshot, s)

    def test_normal_prefixed_id_fallback_is_not_receiver_error(self):
        before = snapshot(routeReject={"missingRoute": 0})
        after = newer(before)
        after["routeReject"] = {"missingRoute": 1}
        self.assertEqual(device.validate_probe(before, after, 1, 0)["reports"], 2)

    def test_new_arm_clears_historical_success(self):
        before = snapshot(state=2, integrity=True)
        armed = copy.deepcopy(before)
        armed.update(state=1, integrity=False, capturedAtUs="1100000", uptimeUs="1100000", reportAgeUs="600000")
        self.assertEqual(device.validate_armed(before, armed)["state"], 1)
        self.rejected("FRESH_ARM_NOT_CONFIRMED", device.validate_armed, before, before)
        self.rejected("RECEIVER_ALREADY_ARMED", device.validate_armed, armed, armed)

    def test_completed_message_may_outlive_led_freshness(self):
        armed = snapshot(state=1)
        complete = newer(armed)
        complete.update(state=2, integrity=True, ledEvidenceValid=False, num=None, caps=None,
                        capturedAtUs="9000000", uptimeUs="9000000", reportAgeUs="7950000")
        self.assertTrue(device.validate_complete(armed, complete)["integrity"])

    def test_old_result_missing_reports_and_wrong_terminal_cannot_pass(self):
        armed = snapshot(state=1)
        self.rejected("MESSAGE_NOT_COMPLETE", device.validate_complete, armed, armed)
        historical = snapshot(state=2, integrity=True)
        self.rejected("NO_NEW_DEVICE_REPORT", device.validate_complete, armed, historical)
        self.rejected("FRESH_ARM_NOT_CONFIRMED", device.validate_complete, historical, historical)
        after = newer(armed)
        after["state"] = 5
        self.rejected("MESSAGE_NOT_COMPLETE", device.validate_complete, armed, after)


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        self.handle_reply()

    def do_POST(self):
        self.handle_reply()

    def handle_reply(self):
        self.server.requests.append((self.command, self.path, self.headers.get("X-Duck-Password")))
        status, headers, body, delay = self.server.reply
        try:
            header_delay = getattr(self.server, "header_delay", 0)
            if header_delay:
                raw = b"HTTP/1.0 200 OK\r\nContent-Type: application/json\r\nContent-Length: 2\r\n\r\n{}"
                for byte in raw:
                    self.wfile.write(bytes([byte]))
                    self.wfile.flush()
                    time.sleep(header_delay)
                return
            self.send_response(status)
            for name, value in headers:
                self.send_header(name, value)
            self.end_headers()
            if delay:
                for byte in body:
                    self.wfile.write(bytes([byte]))
                    self.wfile.flush()
                    time.sleep(delay)
            else:
                self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass
        self.close_connection = True


class HttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.server.daemon_threads = True
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(2)

    def setUp(self):
        self.server.requests = []
        self.server.header_delay = 0
        self.reply(json.dumps(snapshot()).encode())
        factory = lambda host, port, timeout: http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=timeout)
        self.client = device.DeviceClient("http://192.168.4.1", "SYNTHETIC_ONLY", _connection_factory=factory)

    def reply(self, body, kind="application/json", status=200, extra=(), delay=0):
        self.server.reply = status, [("Content-Type", kind), ("Content-Length", str(len(body)))] + list(extra), body, delay

    def rejected(self, code, action):
        with self.assertRaises(device.DeviceError) as caught:
            action()
        self.assertEqual(caught.exception.code, code)
        self.assertNotIn("SYNTHETIC_ONLY", str(caught.exception))

    def test_read_only_identification_and_explicit_receiver_methods(self):
        self.assertEqual(self.client.read()["buildId"], device.BUILD)
        self.client.start()
        self.client.stop()
        self.assertEqual([r[:2] for r in self.server.requests],
                         [("GET", "/led-test"), ("POST", "/led-test/start"), ("POST", "/led-test/stop")])
        self.assertTrue(all(r[2] == "SYNTHETIC_ONLY" for r in self.server.requests))
        self.rejected("ENDPOINT_NOT_ALLOWED", lambda: self.client._request("/upload", "POST"))

    def test_timing_and_idle_discard_settings_and_script_names(self):
        self.reply(json.dumps(dict(buildId=device.BUILD, selectedMs=500, requestCapsMs=500,
                                  requestId="1", owned=False, snapshotKind="request-capture", secret="omit")).encode())
        self.assertFalse(self.client.timing()["owned"])
        self.reply(json.dumps(dict(snapshotKind="request-capture", running=False, routeBOwned=False,
                                  hid=True, ssid="omit", script="omit", lastError="omit")).encode())
        self.assertEqual(self.client.idle(), {"snapshotKind": "request-capture", "running": False, "routeBOwned": False, "hid": True})

    def test_exact_fixed_message_and_content_type(self):
        self.reply(device.MESSAGE, "text/plain; charset=utf-8")
        self.assertEqual(self.client.data(), device.MESSAGE)
        for bad in (device.MESSAGE + b"\n", b"\xef\xbb\xbf" + device.MESSAGE, device.MESSAGE + b"\x00", b"SHORT", b"X" * 17):
            self.reply(bad, "text/plain")
            self.rejected("FIXED_MESSAGE_MISMATCH", self.client.data)
        self.reply(device.MESSAGE, "text/html")
        self.rejected("CONTENT_TYPE_MISMATCH", self.client.data)

    def test_status_and_redirect_never_retry_or_follow(self):
        for status, code in ((401, "AUTH_REFUSED"), (409, "DEVICE_BUSY"), (500, "HTTP_STATUS_ERROR"), (302, "REDIRECT_REFUSED")):
            self.reply(b"private body must not be logged", status=status, extra=[("Location", "http://203.0.113.1/")])
            before = len(self.server.requests)
            self.rejected(code, self.client.read)
            self.assertEqual(len(self.server.requests), before + 1)

    def test_invalid_json_duplicate_keys_and_wrong_content_type(self):
        for body in (b"{", b"[]", b'{"buildId":"a","buildId":"b"}', b'{"x":NaN}', b"\xff"):
            self.reply(body)
            code = "INVALID_DIAGNOSTICS" if body == b"[]" else "INVALID_JSON"
            self.rejected(code, self.client.read)
        self.reply(b"<html>not diagnostics</html>", "text/html")
        self.rejected("CONTENT_TYPE_MISMATCH", self.client.read)

    def test_oversized_truncated_and_duplicate_length(self):
        self.reply(b"x" * (device.MAX_BODY + 1))
        self.rejected("RESPONSE_TOO_LARGE", self.client.read)
        self.server.reply = 200, [("Content-Type", "application/json"), ("Content-Length", "100")], b"{}", 0
        self.rejected("HTTP_TRUNCATED", self.client.read)
        self.reply(b"{}", extra=[("Content-Length", "2")])
        self.rejected("HTTP_PROTOCOL_ERROR", self.client.read)
        self.reply(b"{}", extra=[("Transfer-Encoding", "chunked")])
        self.rejected("HTTP_PROTOCOL_ERROR", self.client.read)

    def test_absolute_deadline_stops_trickled_body(self):
        self.reply(json.dumps(snapshot()).encode(), delay=.025)
        self.client.timeout = .12
        start = time.monotonic()
        self.rejected("HTTP_TIMEOUT", self.client.read)
        self.assertLess(time.monotonic() - start, .8)

    def test_absolute_deadline_includes_trickled_headers(self):
        self.server.header_delay = .025
        self.client.timeout = .12
        start = time.monotonic()
        self.rejected("HTTP_TIMEOUT", self.client.read)
        self.assertLess(time.monotonic() - start, .8)

    def test_header_resource_bound_and_duplicate_type(self):
        self.reply(b"{}", extra=[("X-Oversize", "x" * (device.MAX_WIRE + 1))])
        self.rejected("RESPONSE_TOO_LARGE", self.client.read)
        self.reply(b"{}", extra=[("Content-Type", "application/json")])
        self.rejected("CONTENT_TYPE_MISMATCH", self.client.read)

    def test_url_and_credentials_rejected_before_network(self):
        bad = ["http://127.0.0.1", "http://8.8.8.8", "http://192.0.2.1", "http://example.com",
               "http://user:pass@192.168.4.1", "http://192.168.4.1/?pw=x", "http://192.168.4.1/#x",
               "https://192.168.4.1", "http://[::1]", "http://192.168.4.1/path", "http://192.168.4.1:65536",
               "http://192.168.4.1:0", "http://192.168.4.1:", "http://192.168.4.1:00080",
               " http://192.168.4.1", "http://192.168.4.1\n"]
        for url in bad:
            self.rejected("INVALID_LOCAL_ADDRESS", lambda: device.DeviceClient(url, "synthetic"))
        for password in ("", "x\r\ny", "x\x00y", "x" * 257, "\u2603"):
            self.rejected("AUTH_FORMAT", lambda: device.DeviceClient("http://192.168.4.1", password))
        self.assertEqual(self.server.requests, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
