"""Actual host orchestration with synthetic devices/processes; never IOKit or USB."""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "host_tests/led_return/mac_fixed_message"))
import workflow as w
from test_device import snapshot, newer


class Clock:
    def __init__(self): self.value = 0.0
    def __call__(self): return self.value
    def sleep(self, seconds): self.value += seconds


class Device:
    def __init__(self, num=0, caps=0):
        self.s = snapshot(mask=num | caps << 1, num=bool(num), caps=bool(caps))
        self.starts = self.stops = self.reads = 0
        self.is_busy = self.no_feedback = self.disconnected = False
        self.bad_arm = False
        self.data_value = w.MESSAGE
        self.on_read = self.on_data = None
    def read(self):
        self.reads += 1
        if self.on_read: self.on_read(self)
        if self.disconnected: raise w.DeviceError("USB_NOT_READY")
        return copy.deepcopy(self.s)
    def idle(self): return dict(running=self.is_busy, routeBOwned=False)
    def start(self):
        self.starts += 1
        if not self.bad_arm: self.s.update(state=1, integrity=False)
        return self.read()
    def stop(self): self.stops += 1
    def data(self):
        if self.on_data: self.on_data(self)
        return self.data_value
    def report(self, num, caps):
        if not self.no_feedback: self.s = newer(self.s, num, caps)
    def complete(self):
        self.s = newer(self.s, 0, 0)
        self.s.update(state=2, integrity=True)


class FakeWorker:
    def __init__(self, device, num=0, caps=0):
        self.d, self.num, self.caps = device, num, caps
        self.saved = (num, caps)
        self.commands = []
        self.queue = [dict(event="ready", num=num, caps=caps, reportId=1)]
        self.index = 0
        self.restore_count = 0
        self.bad_step = self.bad_progress = self.native_error = self.cancel = False
    def send(self, command):
        self.commands.append(command)
        if command == "PROBE": self.queue.append(dict(event="probe_ready"))
        if command == "STEP":
            self.index += 1
            if self.index in (1, 3): self.num ^= 1
            else: self.caps ^= 1
            self.d.report(self.num, self.caps)
            self.queue.append(dict(event="probe_step", index=self.index, num=self.num,
                                   caps=self.caps, ok=not self.bad_step))
        if command == "SEND":
            if self.native_error:
                self.queue.append(dict(event="error", code="IO_FAILURE"))
            else:
                self.queue.extend(dict(event="progress", bytes=i, total=25) for i in range(1, 26))
                if self.bad_progress: self.queue[0]["bytes"] = 2
                self.queue.append(dict(event="frame_api_finished", ok=True))
    def event(self, timeout=10):
        if self.cancel and "SEND" in self.commands: raise KeyboardInterrupt()
        item = self.queue.pop(0)
        if item["event"] == "frame_api_finished": self.d.complete()
        return item
    def expect(self, kind, timeout=10):
        item = self.event(timeout)
        if item["event"] != kind: raise w.WorkflowError("WORKER_PROTOCOL")
        return item
    def restore(self):
        self.restore_count += 1
        self.num, self.caps = self.saved
        return dict(attempted=True, caps=True, num=True)


class FlowTests(unittest.TestCase):
    def setup_flow(self, num=0, caps=0):
        self.clock = Clock()
        self.device = Device(num, caps)
        self.worker = FakeWorker(self.device, num, caps)
        self.receipt = w.Receipt(self.clock)
    def run_flow(self, confirm=lambda *_: None):
        w.run_flow(self.device, self.worker, self.receipt, confirm, self.clock,
                   self.clock.sleep, lambda _: None)
    def fails(self, code, confirm=lambda *_: None):
        with self.assertRaises((w.WorkflowError, w.DeviceError)) as caught:
            self.run_flow(confirm)
        self.assertEqual(caught.exception.code, code)
    def setUp(self): self.setup_flow()
    def test_all_initial_led_states_one_probe_and_one_frame(self):
        for num, caps in ((0, 0), (0, 1), (1, 0), (1, 1)):
            self.setup_flow(num, caps)
            self.run_flow()
            self.assertEqual(self.worker.commands, ["PROBE"] + ["STEP"] * 4 + ["SEND"])
            self.assertEqual(self.worker.restore_count, 2)
            self.assertEqual(self.device.starts, 1)
            self.assertFalse(self.receipt.receiver_may_be_armed)
            self.assertEqual(self.receipt.result, "DEVICE_MESSAGE_VERIFIED_IPHONE_PENDING")
    def test_api_success_without_device_feedback_never_arms_or_sends(self):
        self.device.no_feedback = True
        self.fails("CAPABILITY_NOT_CONFIRMED")
        self.assertNotIn("SEND", self.worker.commands)
        self.assertEqual(self.worker.index, 1)
        self.assertEqual(self.device.starts, 0)
        self.assertLessEqual(self.clock(), 4.2)
    def test_busy_execution_before_probe(self):
        self.device.is_busy = True
        self.fails("EXECUTION_BUSY")
        self.assertEqual(self.worker.commands, [])
    def test_armed_receiver_before_probe(self):
        self.device.s["state"] = 1
        self.fails("RECEIVER_BUSY")
        self.assertEqual(self.worker.commands, [])
    def test_refuse_incorrect_report_id_before_writes(self):
        self.worker.queue[0]["reportId"] = 0
        self.fails("WORKER_PROTOCOL")
        self.assertEqual(self.worker.commands, [])
    def test_decline_probe_changes_nothing(self):
        def decline(*_): raise w.WorkflowError("OWNER_CANCELLED")
        self.fails("OWNER_CANCELLED", decline)
        self.assertEqual(self.worker.commands, [])
        self.assertEqual(self.device.starts, 0)
    def test_decline_send_keeps_only_probe(self):
        def decline(_prompt, token):
            if token == "SEND": raise w.WorkflowError("OWNER_CANCELLED")
        self.fails("OWNER_CANCELLED", decline)
        self.assertEqual(self.worker.index, 4)
        self.assertEqual(self.worker.restore_count, 1)
        self.assertEqual(self.device.starts, 0)
        self.assertNotIn("SEND", self.worker.commands)
    def test_receiver_arming_between_probe_steps_prevents_next_write(self):
        def arm(d):
            if self.worker.index == 1 and d.reads == 5: d.s["state"] = 1
        self.device.on_read = arm
        self.fails("RECEIVER_ARMED_DURING_PROBE")
        self.assertEqual(self.worker.index, 1)
    def test_bad_step_ack_stops_probe(self):
        self.worker.bad_step = True
        self.fails("PROBE_WRITE_FAILED")
        self.assertEqual(self.worker.index, 1)
        self.assertEqual(self.device.starts, 0)
    def test_external_clear_between_steps_refuses_next_write(self):
        self.device.s.update(state=2, integrity=True)
        def clear(d):
            if self.worker.index == 1 and d.reads == 5:
                d.s.update(state=0, integrity=False)
        self.device.on_read = clear
        self.fails("RECEIVER_CHANGED_DURING_PROBE")
        self.assertEqual(self.worker.index, 1)
    def test_historical_complete_is_not_fresh_arm(self):
        self.device.s.update(state=2, integrity=True)
        self.device.bad_arm = True
        self.fails("FRESH_ARM_NOT_CONFIRMED")
        self.assertTrue(self.receipt.receiver_may_be_armed)
        self.assertEqual(self.device.starts, 1)
        self.assertNotIn("SEND", self.worker.commands)
    def test_unknown_post_outcome_keeps_cleanup_stop_required(self):
        def failed_start():
            self.device.starts += 1
            raise w.DeviceError("HTTP_IO_ERROR")
        self.device.start = failed_start
        self.fails("HTTP_IO_ERROR")
        self.assertTrue(self.receipt.receiver_may_be_armed)
        self.assertNotIn("SEND", self.worker.commands)
    def test_disconnect_after_data_never_claims_message(self):
        self.device.on_data = lambda d: setattr(d, "disconnected", True)
        self.fails("USB_NOT_READY")
        self.assertEqual(self.receipt.result, "NOT_STARTED")
        self.assertTrue(self.receipt.receiver_may_be_armed)
    def test_wrong_payload_no_device_success(self):
        self.device.data_value = w.MESSAGE + b"\n"
        self.fails("FIXED_MESSAGE_MISMATCH")
        self.assertEqual(self.receipt.result, "NOT_STARTED")
    def test_invalid_progress_not_silently_accepted(self):
        self.worker.bad_progress = True
        self.fails("WORKER_PROTOCOL")
        self.assertEqual(self.worker.commands.count("SEND"), 1)
    def test_native_error_never_replays_frame(self):
        self.worker.native_error = True
        self.fails("NATIVE_SEND_FAILED")
        self.assertEqual(self.worker.commands.count("SEND"), 1)
    def test_cancel_during_frame_propagates_to_cleanup(self):
        self.worker.cancel = True
        with self.assertRaises(KeyboardInterrupt): self.run_flow()
        self.assertTrue(self.receipt.receiver_may_be_armed)
        self.assertEqual(self.worker.commands.count("SEND"), 1)
    def test_new_receiver_error_during_send_fails_closed(self):
        def error(d):
            if "SEND" in self.worker.commands: d.s["receiverOutcome"]["padding"] = 1
        self.device.on_read = error
        self.fails("NEW_RECEIVER_ERROR")
    def test_session_changes_during_owner_prompt_no_write(self):
        def changed(*_): self.device.s["feedbackSession"] += 1
        self.fails("SESSION_CHANGED", changed)
        self.assertEqual(self.worker.commands, [])
    def test_receipt_private_permissions_and_no_overwrite(self):
        self.run_flow()
        with tempfile.TemporaryDirectory() as directory:
            path = self.receipt.save(directory)
            data = json.loads(path.read_text())
            self.assertEqual(os.stat(path).st_mode & 0o777, 0o600)
            self.assertNotIn("password", path.read_text().lower())
            self.assertFalse(data["global_caps_restoration_proven"])
            with self.assertRaises(FileExistsError): self.receipt.save(directory)


class ProcessTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
    def worker(self, source):
        path = Path(self.tmp.name) / "synthetic-worker"
        path.write_text("#!" + sys.executable + "\n" + source)
        path.chmod(0o700)
        worker = w.Worker(path, "SYNTHETIC-NOT-USB", time.monotonic()+10)
        self.addCleanup(worker.cleanup)
        return worker
    def test_partial_json_line_and_clean_exit(self):
        p = self.worker('import sys,time\nsys.stdout.write(\'{"event":"rea\');sys.stdout.flush()\ntime.sleep(.02)\nprint(\'dy"}\',flush=True)\nsys.stdin.readline()\n')
        self.assertEqual(p.expect("ready"), dict(event="ready"))
        self.assertIsNone(p.cleanup())
        self.assertIsNone(p.cleanup_error)
    def test_oversized_line_rejected(self):
        p = self.worker('print("x"*5000,flush=True)\n')
        with self.assertRaises(w.WorkflowError) as caught: p.event()
        self.assertEqual(caught.exception.code, "WORKER_PROTOCOL")
    def test_error_payload_sanitized(self):
        p = self.worker('print(\'{"event":"error","code":"secret\\\\nraw"}\',flush=True)\n')
        with self.assertRaises(w.WorkflowError) as caught: p.expect("ready")
        self.assertEqual(caught.exception.code, "NATIVE_ERROR")
    def test_cleanup_interrupts_active_sender_immediately(self):
        p = self.worker('import sys,signal,time\ndef stop(*_):\n print(\'{"event":"restored","caps":true,"num":true,"attempted":true}\',flush=True)\n sys.exit(0)\nsignal.signal(signal.SIGTERM,stop)\nprint(\'{"event":"ready"}\',flush=True)\nsys.stdin.readline()\ntime.sleep(60)\n')
        p.expect("ready")
        p.send("SEND")
        began = time.monotonic()
        status = p.cleanup()
        self.assertLess(time.monotonic()-began, 2)
        self.assertTrue(status["caps"] and status["num"])
        self.assertFalse(p.dirty)
    def test_cleanup_errors_are_bounded_and_do_not_raise(self):
        p = self.worker('import sys\nprint(\'{"event":"ready"}\',flush=True)\nsys.stdin.readline()\n')
        p.expect("ready")
        with mock.patch.object(p.process, "wait", side_effect=subprocess.TimeoutExpired("mock", 2)):
            p.cleanup()
        self.assertEqual(p.cleanup_error, "NATIVE_CLEANUP_UNCONFIRMED")
        p.process.wait(timeout=2)
    def test_watcher_nonzero_is_not_clean_success(self):
        p = self.worker('import sys\nsys.exit(124)\n')
        with self.assertRaises(w.WorkflowError): p.event()
        p.cleanup()
        self.assertEqual(p.cleanup_error, "NATIVE_WATCHDOG")


if __name__ == "__main__": unittest.main(verbosity=2)
