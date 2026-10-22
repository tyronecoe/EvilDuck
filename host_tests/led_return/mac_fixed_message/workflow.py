#!/usr/bin/env python3
"""Foreground fixed-data workflow. No input observation, serial ports or firmware writes."""
import argparse
import getpass
import hashlib
import json
import os
import re
import selectors
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from device import (DeviceClient, DeviceError, validate_session, validate_probe,
                    validate_armed, validate_complete)

MESSAGE = b"EVILDUCK TEST 123"
WORKFLOW_SECONDS = 600


class WorkflowError(Exception):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


class Receipt:
    def __init__(self, clock=time.monotonic):
        self.clock = clock
        self.started = clock()
        self.events = []
        self.result = "NOT_STARTED"
        self.iphone = "PENDING_OWNER"
        self.receiver_may_be_armed = False

    def add(self, event, **values):
        if len(self.events) >= 1000:
            raise WorkflowError("RECEIPT_LIMIT")
        self.events.append(dict(event=event, elapsed_s=round(self.clock()-self.started, 6), **values))

    def save(self, directory):
        data = dict(format="evilduck-fixed-message-v1", result=self.result,
                    iphone_view=self.iphone, evidence_origin="LOCAL_WORKFLOW",
                    message_ascii=MESSAGE.decode("ascii"), payload_bytes=len(MESSAGE),
                    global_caps_restoration_proven=False, events=self.events)
        path = Path(directory) / "receipt.json"
        fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=2, allow_nan=False)
            f.write("\n")
        return path


class Worker:
    """One retained non-seizing native device handle; bounded JSON-line transport."""
    def __init__(self, executable, serial, deadline, clock=time.monotonic):
        self.clock, self.deadline = clock, deadline
        self.process = subprocess.Popen([str(executable), "--worker", serial],
                                        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        stderr=subprocess.DEVNULL)
        self.selector = selectors.DefaultSelector()
        self.selector.register(self.process.stdout, selectors.EVENT_READ)
        self.buffer = b""
        self.restoration = None
        self.dirty = False
        self.closed = False
        self.sending = False
        self.restore_requested = False
        self.cleanup_error = None
        self.abort_sent = False

    def send(self, command):
        if command not in ("PROBE", "STEP", "RESTORE", "SEND", "QUIT"):
            raise WorkflowError("WORKER_COMMAND")
        if command in ("STEP", "SEND"):
            self.dirty = True
            self.restoration = None
            self.restore_requested = False
        if command == "SEND":
            self.sending = True
        if command == "RESTORE":
            self.restore_requested = True
        try:
            self.process.stdin.write((command+"\n").encode("ascii"))
            self.process.stdin.flush()
        except (OSError, ValueError):
            raise WorkflowError("NATIVE_EXIT") from None

    def event(self, timeout=10, cleanup=False):
        until = self.clock()+timeout
        if not cleanup:
            until = min(until, self.deadline)
        while True:
            if b"\n" in self.buffer:
                line, self.buffer = self.buffer.split(b"\n", 1)
                if len(line) > 4096:
                    raise WorkflowError("WORKER_PROTOCOL")
                try:
                    item = json.loads(line.decode("ascii"))
                except (ValueError, UnicodeError):
                    raise WorkflowError("WORKER_PROTOCOL") from None
                if not isinstance(item, dict) or not isinstance(item.get("event"), str):
                    raise WorkflowError("WORKER_PROTOCOL")
                if item["event"] == "restored":
                    if any(type(item.get(k)) is not bool for k in ("caps", "num", "attempted")):
                        raise WorkflowError("WORKER_PROTOCOL")
                    self.restoration = {k:item[k] for k in ("caps", "num", "attempted")}
                    if item["caps"] and item["num"]:
                        self.dirty = False
                    self.sending = False
                if item["event"] == "frame_api_finished":
                    self.sending = False
                return item
            remaining = until-self.clock()
            if remaining <= 0:
                raise WorkflowError("WORKER_TIMEOUT")
            if not self.selector.select(min(remaining, 0.25)):
                continue
            chunk = os.read(self.process.stdout.fileno(), 4096)
            if not chunk:
                code = self.process.poll()
                raise WorkflowError("NATIVE_WATCHDOG" if code == 124 else "NATIVE_EXIT")
            self.buffer += chunk
            if len(self.buffer) > 8192:
                raise WorkflowError("WORKER_PROTOCOL")

    def expect(self, kind, timeout=10):
        event = self.event(timeout)
        if event["event"] == "error":
            code = event.get("code", "NATIVE_ERROR")
            if not isinstance(code, str) or not re.fullmatch(r"[A-Z0-9_]{1,64}", code):
                code = "NATIVE_ERROR"
            raise WorkflowError(code)
        if event["event"] != kind:
            raise WorkflowError("WORKER_PROTOCOL")
        return event

    def restore(self):
        self.send("RESTORE")
        item = self.expect("restored", 5)
        if not item["caps"] or not item["num"]:
            raise WorkflowError("RESTORATION_UNCONFIRMED")
        return self.restoration

    def interrupt_send(self):
        if self.sending and not self.abort_sent and self.process.poll() is None:
            try:
                self.process.terminate()
                self.abort_sent = True
            except OSError:
                self.cleanup_error = "NATIVE_CLEANUP_UNCONFIRMED"

    def cleanup(self):
        if self.closed:
            return self.restoration
        self.closed = True
        try:
            if self.dirty:
                # SEND is synchronous in the child. Interrupt it immediately on an
                # orchestration failure, rather than queue RESTORE behind a frame.
                if self.sending and self.process.poll() is None:
                    self.interrupt_send()
                elif not self.restore_requested and self.process.poll() is None:
                    try:
                        self.send("RESTORE")
                    except WorkflowError:
                        pass
                end = self.clock()+5
                while self.clock() < end:
                    try:
                        item = self.event(end-self.clock(), cleanup=True)
                    except WorkflowError:
                        break
                    if item["event"] == "restored":
                        break
            if self.process.poll() is None:
                try:
                    self.send("QUIT")
                except WorkflowError:
                    pass
            try:
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.terminate()
                try:
                    self.process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    self.process.kill()
                    self.process.wait(timeout=2)
            if self.process.returncode:
                self.cleanup_error = "NATIVE_WATCHDOG" if self.process.returncode == 124 else "NATIVE_EXIT"
        except (OSError, ValueError, subprocess.SubprocessError):
            self.cleanup_error = "NATIVE_CLEANUP_UNCONFIRMED"
        finally:
            for resource in (self.selector, self.process.stdin, self.process.stdout):
                try:
                    resource.close()
                except (OSError, ValueError):
                    self.cleanup_error = "NATIVE_CLEANUP_UNCONFIRMED"
        return self.restoration


def require_idle(client):
    state = client.idle()
    if state["running"] or state["routeBOwned"]:
        raise WorkflowError("EXECUTION_BUSY")


def confirm_token(prompt, token, ask=input):
    if ask(prompt).strip() != token:
        raise WorkflowError("OWNER_CANCELLED")


def run_flow(client, worker, receipt, confirm, clock=time.monotonic, sleep=time.sleep,
             output=print):
    """No hardware-specific shortcuts: tests inject the same orchestrated interfaces."""
    ready = worker.expect("ready")
    if any(type(ready.get(k)) is not int or ready[k] not in (0, 1) for k in ("num", "caps")):
        raise WorkflowError("WORKER_PROTOCOL")
    if type(ready.get("reportId")) is not int or ready["reportId"] != 1:
        raise WorkflowError("WORKER_PROTOCOL")
    saved_num, saved_caps = ready["num"], ready["caps"]
    before = client.read()
    require_idle(client)
    if before["state"] == 1:
        raise WorkflowError("RECEIVER_BUSY")
    receipt.add("initial", snapshot=before)
    confirm("Type PROBE to perform four direct Num/Caps LED writes: ", "PROBE")
    # Recheck after the owner prompt; no state captured before a long pause is current.
    current = client.read()
    validate_session(before, current)
    before = current
    require_idle(client)
    if before["state"] == 1:
        raise WorkflowError("RECEIVER_BUSY")
    worker.send("PROBE")
    worker.expect("probe_ready")
    expected = [(saved_num ^ 1, saved_caps), (saved_num ^ 1, saved_caps ^ 1),
                (saved_num, saved_caps ^ 1), (saved_num, saved_caps)]
    for index, (num, caps) in enumerate(expected, 1):
        require_idle(client)
        current = client.read()
        validate_session(before, current)
        if current["state"] == 1:
            raise WorkflowError("RECEIVER_ARMED_DURING_PROBE")
        if (current["state"], current["integrity"]) != (before["state"], before["integrity"]):
            raise WorkflowError("RECEIVER_CHANGED_DURING_PROBE")
        before = current
        worker.send("STEP")
        ack = worker.expect("probe_step")
        if (ack.get("ok") is not True or type(ack.get("index")) is not int or
                ack["index"] != index or type(ack.get("num")) is not int or
                type(ack.get("caps")) is not int or (ack["num"], ack["caps"]) != (num, caps)):
            raise WorkflowError("PROBE_WRITE_FAILED")
        until = clock()+4
        while True:
            if clock() >= until:
                raise WorkflowError("CAPABILITY_NOT_CONFIRMED")
            observed = client.read()
            if clock() > until:
                raise WorkflowError("CAPABILITY_NOT_CONFIRMED")
            validate_session(before, observed)
            if observed["state"] == 1:
                raise WorkflowError("RECEIVER_ARMED_DURING_PROBE")
            try:
                validate_probe(before, observed, num, caps)
                break
            except DeviceError as e:
                # Poll only not-yet-arrived evidence; never repeat the write or an HTTP error.
                if e.code not in ("NO_NEW_DEVICE_REPORT", "LED_EVIDENCE_NOT_FRESH", "LED_STATE_MISMATCH"):
                    raise
                if clock() >= until:
                    raise WorkflowError("CAPABILITY_NOT_CONFIRMED") from None
                sleep(0.1)
        receipt.add("probe_step", index=index, num=num, caps=caps, snapshot=observed)
        output("Probe {}/4: device observed Num={} Caps={}.".format(index, num, caps))
        before = observed
    receipt.add("probe_restoration", **worker.restore())
    receipt.add("capability", result="CONFIRMED_BY_DEVICE_FEEDBACK")
    output("Caps and Num output capability confirmed on this device/session.")
    confirm("Type SEND to arm a NEW receiver and send EVILDUCK TEST 123 once: ", "SEND")
    current = client.read()
    validate_session(before, current)
    require_idle(client)
    if current["state"] == 1:
        raise WorkflowError("RECEIVER_BUSY")
    # Set before POST: an HTTP failure can leave arming outcome unknown, so cleanup still stops it.
    receipt.receiver_may_be_armed = True
    armed = validate_armed(current, client.start())
    receipt.add("new_receiver", snapshot=armed)
    require_idle(client)
    worker.send("SEND")
    progress = 0
    send_deadline = clock()+95
    while True:
        remaining = send_deadline-clock()
        if remaining <= 0:
            raise WorkflowError("SEND_TIMEOUT")
        event = worker.event(remaining)
        if event["event"] == "error":
            raise WorkflowError("NATIVE_SEND_FAILED")
        if event["event"] == "frame_api_finished":
            if event.get("ok") is not True or progress != 25:
                raise WorkflowError("WORKER_PROTOCOL")
            break
        if (event["event"] != "progress" or type(event.get("bytes")) is not int or
                event["bytes"] != progress+1 or type(event.get("total")) is not int or event["total"] != 25):
            raise WorkflowError("WORKER_PROTOCOL")
        progress += 1
        output("Fixed frame: {}/25 bytes submitted through the host API.".format(progress))
        check = client.read()
        validate_session(armed, check)
        if check["state"] not in (1, 2) or (check["state"] == 2 and not check["integrity"]):
            raise WorkflowError("RECEIVER_FAILED")
        require_idle(client)
    until = clock()+5
    while True:
        final = client.read()
        if clock() > until:
            raise WorkflowError("RECEIVE_NOT_CONFIRMED")
        validate_session(armed, final)
        if final["state"] == 2:
            validate_complete(armed, final)
            break
        if final["state"] != 1:
            raise WorkflowError("RECEIVER_FAILED")
        if clock() >= until:
            raise WorkflowError("RECEIVE_NOT_CONFIRMED")
        sleep(0.1)
    if client.data() != MESSAGE:
        raise WorkflowError("FIXED_MESSAGE_MISMATCH")
    after_data = validate_complete(armed, client.read())
    validate_session(final, after_data)
    receipt.add("device_message", result="VERIFIED", snapshot=after_data,
                bytes=len(MESSAGE), payload_sha256=hashlib.sha256(MESSAGE).hexdigest())
    receipt.receiver_may_be_armed = False
    receipt.add("send_restoration", **worker.restore())
    receipt.result = "DEVICE_MESSAGE_VERIFIED_IPHONE_PENDING"
    output("Fresh device result and authenticated 17-byte download verified.")


def discover(executable):
    try:
        proc = subprocess.run([str(executable), "--check"], stdout=subprocess.PIPE,
                              stderr=subprocess.DEVNULL, timeout=95, check=False)
    except subprocess.TimeoutExpired:
        raise WorkflowError("DISCOVERY_TIMEOUT") from None
    if proc.returncode or len(proc.stdout) > 32768:
        raise WorkflowError("DISCOVERY_FAILED")
    try:
        rows = json.loads(proc.stdout.decode("utf-8"))["devices"]
    except (ValueError, UnicodeError, KeyError, TypeError):
        raise WorkflowError("DISCOVERY_PROTOCOL") from None
    if not isinstance(rows, list) or len(rows) > 16:
        raise WorkflowError("DISCOVERY_PROTOCOL")
    for row in rows:
        if (not isinstance(row, dict) or not isinstance(row.get("serial"), str) or
                len(row["serial"].encode("utf-8")) > 255 or any(not c.isprintable() for c in row["serial"]) or
                type(row.get("usable")) is not bool):
            raise WorkflowError("DISCOVERY_PROTOCOL")
        if not isinstance(row.get("reason"), str) or not re.fullmatch(r"[A-Z0-9_]{1,64}", row["reason"]):
            raise WorkflowError("DISCOVERY_PROTOCOL")
    return rows


def main(argv=None):
    parser = argparse.ArgumentParser(description="One visible, fixed-message LED workflow; no firmware update")
    parser.add_argument("--native", required=True, type=Path)
    args = parser.parse_args(argv)
    receipt = Receipt()
    worker = client = None
    receipt.receiver_may_be_armed = False
    receipt_dir = tempfile.mkdtemp(prefix="evilduck-fixed-message-", dir=str(Path.home()/"Desktop"))
    old_handler = signal.getsignal(signal.SIGALRM)
    def expired(_signum, _frame):
        raise WorkflowError("WORKFLOW_TIMEOUT")
    signal.signal(signal.SIGALRM, expired)
    signal.alarm(WORKFLOW_SECONDS)
    try:
        print("VISIBLE FIXED MESSAGE ONLY. No input capture, keystroke injection, driver, installer or firmware update.")
        print("Direct LED output may change visible interface LEDs. Cleanup is best effort, not global Caps restoration.")
        rows = discover(args.native)
        for row in rows:
            print("USB 303A:1001 serial={} usable={} reason={}".format(
                row["serial"] or "<missing>", row["usable"], row["reason"]))
        serial = input("Enter the exact serial of your unique usable EvilDuck interface: ").strip()
        matches = [row for row in rows if row["serial"] == serial]
        if not serial or len(matches) != 1 or not matches[0]["usable"]:
            raise WorkflowError("TARGET_MISSING_OR_AMBIGUOUS")
        address = input("Existing local dashboard address (no password in URL): ").strip()
        password = getpass.getpass("Existing Web UI password (not saved): ")
        client = DeviceClient(address, password)
        password = None
        worker = Worker(args.native, serial, receipt.started+WORKFLOW_SECONDS)
        run_flow(client, worker, receipt, confirm_token)
        print("On iPhone: Observe LEDs / refresh, then View test data. Confirm EVILDUCK TEST 123 exactly.")
        try:
            confirm_token("Type VIEWED only after checking that new iPhone result (Enter leaves pending): ", "VIEWED")
            receipt.iphone = "OWNER_REPORTED_PASS"
            receipt.result = "DEVICE_VERIFIED_AND_OWNER_IPHONE_CONFIRMED"
        except WorkflowError as e:
            if e.code != "OWNER_CANCELLED":
                raise
        return_code = 0
    except (WorkflowError, DeviceError) as e:
        receipt.result = e.code
        receipt.add("stopped", code=e.code)
        print("STOPPED: {}. No automatic retry or message replay.".format(e.code))
        return_code = 2
    except (KeyboardInterrupt, EOFError):
        receipt.result = "OWNER_CANCELLED"
        receipt.add("stopped", code="OWNER_CANCELLED")
        print("Cancelled. Attempting bounded receiver stop and independent output restoration.")
        return_code = 130
    except (OSError, ValueError, subprocess.SubprocessError):
        receipt.result = "LOCAL_TOOL_ERROR"
        receipt.add("stopped", code="LOCAL_TOOL_ERROR")
        print("STOPPED: LOCAL_TOOL_ERROR. No automatic retry.")
        return_code = 2
    finally:
        signal.alarm(0)
        # A second Ctrl-C cannot strand the child midway through this finite cleanup.
        previous_int = signal.signal(signal.SIGINT, signal.SIG_IGN)
        try:
            if worker:
                worker.interrupt_send()
            if client and receipt.receiver_may_be_armed:
                try:
                    client.stop()
                    receipt.add("receiver_stop", result="REQUEST_ACCEPTED_NOT_HOST_RELEASE_PROOF")
                except (DeviceError, OSError):
                    receipt.add("receiver_stop", result="UNCONFIRMED")
            if worker:
                status = worker.cleanup()
                receipt.add("final_restoration", result=status or "UNCONFIRMED_OR_NOT_ATTEMPTED")
                if worker.dirty or worker.cleanup_error:
                    receipt.add("cleanup_status", code=worker.cleanup_error or "RESTORATION_UNCONFIRMED")
                    receipt.result = "RESTORATION_UNCONFIRMED" if worker.dirty else worker.cleanup_error
                    return_code = 2
            path = receipt.save(receipt_dir)
            print("Sanitized local receipt: {}".format(path))
            print("Result: {}; iPhone: {}".format(receipt.result, receipt.iphone))
        finally:
            signal.signal(signal.SIGINT, previous_int)
            signal.signal(signal.SIGALRM, old_handler)
    return return_code


if __name__ == "__main__":
    sys.exit(main())
