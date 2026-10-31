# Inherited lock-wait acceptance on H1 — prepared, not executed

This sheet is for **ROUTEB-INJECT-VAR-H1-EXPERIMENTAL-v1**, intended application **1,414,080** bytes / SHA-256 `8a48f3f208165466e579f76a35fb7898fbaf1188e746ca3a0d60e99c576b0ecd`, only. It tests the inherited **EvilDuck extension** `$_EVILDUCK_LOCK_TIMEOUT`. This preparation authorizes no hardware access or physical execution. Keep the accepted source/text-v2 rollback **1,413,200** bytes / `cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02` and the existing application packages unchanged.

Do not repeat the four completed H1 checks. These three new groups assess inherited timeout behavior on H1; they do not certify the separate earlier lock-wait application, resolve official Hak5 encoding or change the default firmware baseline. A build-ID string does not prove physical application image bytes. Do not substitute an earlier lock-wait installation receipt for H1 evidence.

## 1. Review offline and prepare the owner setup

From the extracted kit directory, first run the local-only check:

```bash
python3 validate_kit.py --directory .
```

No board access occurs. Only after review and separate physical-use approval: use macOS High Sierra 10.13.6, Python 3.8 stdlib, blank plain-text TextEdit, a known input source/Caps state and the iPhone dashboard. Record the **full** reported build ID, actual assigned request and available boot/session evidence. Label application hashes as package/installer-recorded unless independently read back. Missing identifiers remain unknown.

Confirm execution idle, autorun disabled, EDR1 inactive and no existing quarantine. Keep the existing **STOP / check execution** control accessible on the iPhone and other dashboard clients idle. Do not change lock states during passive trials. Review each complete fixture file before saving it through the existing supported manual path; the kit performs no upload or Start.

## 2. Prepare observation before every deliberate Start

In a dedicated Terminal window, from the kit folder:

```bash
set -o pipefail
WAIT_LOG=$(mktemp "$HOME/Desktop/evilduck-h1-wait-observation.XXXXXX")
printf 'Observation log: %s\n' "$WAIT_LOG"
python3 -u ./observe_wait.py --seconds 45 2>&1 | tee "$WAIT_LOG"
```

Enter the dashboard password **only** at `Dashboard password (not saved):`. Do not put it in arguments, URLs, shell variables, saved logs or screenshots. The helper uses the `X-Duck-Password` header, not Basic auth or `?pw=`. Its default `http://192.168.4.1` is unencrypted; use only the known local AP/network. Redirects are not followed. Logs whitelist execution fields and omit raw response bodies, SSID, script names and credentials. Process-memory clearing is not a secure-erasure guarantee.

Wait for **READY**. This means full H1 build-name verification and idle status preflight succeeded; **no device action was sent and no fixture run is authorized by READY alone**. When separately ready to conduct the reviewed trial:

1. Manually Start the intended fixture **once** through the explicit Route B dashboard path or existing separately approved CDC route.
2. Read the request ID actually assigned by the device. Do not predict the next number.
3. Immediately type that actual number into the observer's waiting `Actual assigned request ID (no prediction):` prompt and press Return.
4. Focus blank TextEdit during the fixture's initial five-second DELAY. For the STOP trial, keep the iPhone STOP control ready throughout.

Prepare the observer, fixture and blank editor **before** Start. The five-second DELAY is an existing focus opportunity, not a guarantee that switching applications and entering the request will fit. Request-entry time is outside the helper's observation window while the device's finite trial window continues. If too late, keep the evidence as inconclusive; do not automatically replay or alter timing.

The helper schedules polls at 250 ms intervals in the 45-second window, with a fixed attempt cap and 32 KiB response-size bound. HTTP uses a 2-second **socket-inactivity** timeout, not a total end-to-end deadline. A peer delivering partial data can hold a call beyond 45 seconds or 45+2 seconds. Responses completing after the observation window are not usable evidence. **Control+C stops observation only; it does not send STOP to EvilDuck.** The owner must use the independent dashboard STOP control if needed. No strict overall network wall-time bound is promised.

Authentication, HTTP409, network, identity, missing/malformed fields or clock/session errors end observation without retrying that failed request or sending any action. A helper error alone is not a firmware failure. Preserve logs; do not automatically replay a payload.

## 3. Trial group 1 — default, assignment, RESET preservation and new-run default

File **wait-settings-reset.txt**:

```ducky
DELAY 5000
IF $_EVILDUCK_LOCK_TIMEOUT == 5000 THEN
STRINGLN 111default
END_IF
$_EVILDUCK_LOCK_TIMEOUT = 10000
IF $_EVILDUCK_LOCK_TIMEOUT == 10000 THEN
STRINGLN 222set
END_IF
RESET
IF $_EVILDUCK_LOCK_TIMEOUT == 10000 THEN
STRINGLN 333reset
END_IF
```

Expect exactly three lines in TextEdit:

```text
111default
222set
333reset
```

Require matching **Completed** for that actual request. Then prepare a new observer invocation and blank TextEdit for one **separate, deliberate** Start of **wait-new-run-default.txt**:

```ducky
DELAY 5000
IF $_EVILDUCK_LOCK_TIMEOUT == 5000 THEN
STRINGLN 444newrun
END_IF
```

Expect exactly `444newrun` and matching Completed for its new actual request. This is a second execution within group 1, not an automatic repeat. RESET here is the keyboard-state command, not a device reboot or settings reset. Exhaustive bounds and restart-default behavior remain prior software checks.

## 4. Trial group 2 — expected passive 1000 ms CAPS_CHANGE expiry

Prepare observation first. File **wait-passive-expiry.txt**:

```ducky
DELAY 5000
$_EVILDUCK_LOCK_TIMEOUT = 1000
WAIT_FOR_CAPS_CHANGE
STRINGLN 999bad
```

Do not deliberately change any lock state. Expect **blank TextEdit** and the actual request's correlated terminal **Deadline reason 9**, **Timeout error 26**, physical **line 3**. This is an expected timeout-policy observation, not an implementation failure. Require no quarantine using available device diagnostics; if those diagnostics are unavailable, leave the field unknown and preserve the limitation.

A matched waiting capture is useful, but its one-second window may be missed. Record whether one was observed; the scoped terminal diagnostic must still identify the requested wait expiry. Whole-request elapsed budget instead yields **Runtime reason 6 / Timeout 26** and is a competing outcome, not this pass. Tick/step exhaustion, disconnect, backend/loss or cleanup errors likewise do not establish the intended timeout behavior. If an unexpected lock transition types `999bad`, or a competing outcome prevents interpretation, classify **UNVERIFIED/inconclusive**, preserve the evidence and do not replay automatically. Polling elapsed time is not precise script-execution, USB or LED timing.

## 5. Trial group 3 — held Shift and one STOP during correlated waiting

Prepare observation first. File **wait-held-shift-stop.txt**:

```ducky
DELAY 5000
$_EVILDUCK_LOCK_TIMEOUT = 10000
HOLD SHIFT
WAIT_FOR_CAPS_CHANGE
STRINGLN 999bad
```

Require a **MATCHED_CAPTURE** for the actual assigned request with:

- `routeBRequestId`: the exact actual request string.
- `routeBWaiting=true`, `routeBOwned=true`.
- `routeBPhase=6`, `routeBWaitCommand=5` (CAPS_CHANGE).
- Recorded `routeBWaitStartedMs`, `routeBWaitSession`, `capturedAtMs` and `snapshotKind=request-capture`.

After **MATCHED_CAPS_CHANGE_WAIT_OBSERVED**, use the existing iPhone dashboard STOP **once** while that same execution is still active. Expect matching Idle/Cancelled (**reason 2**), no unwanted marker, no quarantine in available device diagnostics and ordinary harmless **manual lowercase** typing afterward. Because Shift is held, the unwanted marker could appear uppercase; require no injected marker in either case. Preserve waiting and terminal captures, TextEdit/manual observations and the actual request correlation.

The entered request must be newer than the idle preflight request; the helper compares actual IDs rather than predicting the next ID. Capture-clock checks begin with that idle snapshot, and future or ambiguous wait-start timestamps are rejected. Quarantined phase8 is not treated as a successful terminal completion; observation ends UNVERIFIED. A restart or inconsistent clock is missing correlation, not grounds to bypass the checks.

Each accepted capture is individually coherent at its capture time; it is not a continuing live promise. Duplicate capture timestamps are not new waiting evidence. Normal uint32 clock wrap is handled; backward/ambiguous jumps and changed wait session stop observation. Local cleanup submission/manual lowercase recovery is scoped evidence, not general host-key-release or USB endpoint-retirement proof.

If waiting correlation is absent, the request differs, or the wait completed, expired or disconnected before STOP, the intended test window was not established. Classify **UNVERIFIED/inconclusive** and preserve evidence; do not automatically restart or toggle a host lock key to force a pass.

## 6. Interpret the observer and preserve evidence

Exit0 means only a matching terminal capture was observed. It does **not** mean trial PASS: review its reason/error/line, waiting correlation where required and independent TextEdit/manual evidence. Exit2 means incomplete/refused observation. The observer sends no Start, STOP, upload, settings or LED/HID action; it cannot stop the payload when it exits.

Save the Terminal log, screenshots, relevant request/status fields and a short host/build/trial note before rebooting or starting another trial. Record unknown metadata as unknown. Do not share passwords, raw private status bodies, backups or configuration. Preserve working firmware, original receipts and partial results unchanged.

**PASS** is the expected scoped behavior with the specified correlation/evidence. **FAIL** requires demonstrated incorrect implementation under the tested conditions. Missing correlation, helper error or competing transition is **UNVERIFIED**; an identified host/tooling constraint is **PLATFORM-LIMITED**. No broad Caps investigation or Windows prerequisite is introduced.

## Existing GNU Screen reminders

For a separately approved existing USB CDC connection, rediscover the port after every reconnect/reset:

```bash
ls /dev/cu.usbmodem*
```

Verify the current port before opening Screen; never reuse an old numeric suffix. The existing template is:

```bash
screen /dev/cu.usbmodemCURRENT 115200
```

Replace the placeholder with the verified current port. Use explicit `routeb <actual-stored-fixture-name>` once. The observed High Sierra/GNU Screen workaround is **Control+J once** when Return appeared ineffective; it is not a universal requirement or diagnosed defect. Do not compensate with repeated submissions. No pySerial, compiler or native LED helper is needed.
