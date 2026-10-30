# Bounded lock-wait acceptance — review candidate only

Candidate **ROUTEB-LOCK-WAIT-TIMEOUT-v1** adds `$_EVILDUCK_LOCK_TIMEOUT`, an **EvilDuck extension**. This sheet authorizes no installation or physical trial. The currently accepted source/text v2 does not implement this property. Keep its exact application and rollback available; no EDR1, Caps timing, keyboard layout or settings change is needed.

After separate installation and physical-test approval, use macOS High Sierra10.13.6, Python3.8, blank TextEdit, a known input source/Caps state and the iPhone dashboard. Record build ID, actual assigned request, available boot/session evidence and observed output; leave unavailable identifiers unknown. Keep STOP accessible, autorun disabled, EDR1 inactive and other dashboard clients idle. One deliberate Start per fixture, no automatic replay. Do not deliberately change any lock state for the passive wait trials.

## Prepare observation before Start

The package's **`observe_wait.py`** is read-only: it authenticates and checks build ID through GET `/caps-timing`, preflights GET `/status`, then asks for the actual assigned request. It never starts, stops or retries a payload, changes a lock key, sends LED output or saves settings. No additional Python modules, native executable, pySerial or compiler are required. Run it from the unpacked package folder in a dedicated Terminal window:

```bash
set -o pipefail
WAIT_LOG=$(mktemp "$HOME/Desktop/evilduck-wait-observation.XXXXXX")
printf 'Observation log: %s\n' "$WAIT_LOG"
python3 -u ./observe_wait.py --seconds 45 2>&1 | tee "$WAIT_LOG"
```

Enter the dashboard password only at **`Dashboard password (not saved):`**. Do not put it in the command, URL, shell variable, screenshot or notes. The helper uses `X-Duck-Password`, not `?pw=` or Basic auth. Default base is the known local `http://192.168.4.1`; this is unencrypted HTTP, so use only the known local AP/network. No redirect is followed. Logs include only whitelisted execution fields, not SSID, script names, raw HTTP bodies or credentials. Keeping a password in process memory is not a secure-erasure guarantee.

Wait for **READY** before starting the fixture. READY confirms only authentication, expected build ID, an idle execution preflight and the response structure; no action has been sent. Manually Start the reviewed fixture once using the existing explicit Route B dashboard path, read its **actual** assigned request ID, and immediately enter that number into the waiting Terminal prompt. Do not predict the next number. Request-entry time is outside the helper's observation window but still consumes the device fixture's finite timing window; if too late, preserve the result as inconclusive and do not automatically restart.

The helper schedules polls at250ms intervals within a45second observation window, with a fixed attempt cap and a32KiB response-size bound. Each HTTP operation uses a2second **socket-inactivity timeout**, not a hard end-to-end deadline: a slow peer delivering partial data may keep an in-flight call alive beyond45seconds or45+2seconds. The helper rejects a response that returns after the observation window as evidence. If it remains blocked, **Control + C** interrupts the observer; that does **not** send device STOP. Keep the independent dashboard STOP control ready. No strict physical wall-time bound for urllib/network I/O is claimed. Authentication, HTTP409, network, malformed-response or identity errors end observation without retrying the failed request. This never sends STOP; the owner remains responsible for the existing STOP control. A helper error is missing evidence, not proof of a firmware fault.

Each `MATCHED_CAPTURE` must show the intended **`routeBRequestId`**, not a previous request. For the STOP fixture, require **`routeBWaiting=true`**, **`routeBOwned=true`**, **`routeBPhase=6`**, **`routeBWaitCommand=5`** (CAPS_CHANGE), with recorded **`routeBWaitStartedMs`** and **`routeBWaitSession`**. On the first such capture it prints **MATCHED_CAPS_CHANGE_WAIT_OBSERVED**. The existing visible dashboard has no special waiting label. These fields come from an individually coherent request-capture snapshot, not a live promise extending beyond capture. Duplicate device capture timestamps do not establish new waiting evidence; backward/ambiguous device-clock jumps and wait-session changes stop observation. Normal uint32 timestamp wrap is handled.

An exit status0 means only that a matching terminal snapshot was observed. It is **not a trial PASS**: review its reason/error, prior waiting correlation and independent TextEdit/manual evidence. Exit2 means observation was incomplete or refused. Preserve the Terminal output and available dashboard/TextEdit screenshots before rebooting or starting another trial.

## Trial 1 — setting, RESET preservation and next-run default

Save and review this exact harmless fixture. Start once, focus blank TextEdit during DELAY:

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

Expect three lines, exactly `111default`, `222set`, `333reset`, and matching **Completed**. Then perform one separate deliberately started default-check fixture:

```ducky
DELAY 5000
IF $_EVILDUCK_LOCK_TIMEOUT == 5000 THEN
STRINGLN 444newrun
END_IF
```

Expect exactly `444newrun` and Completed for that new request. This is a second execution within trial group1, not an automatic replay. Restart-default and exhaustive numeric boundaries remain automated checks.

## Trial 2 — expected passive wait expiry

Prepare the observer first. Run this fixture once, focus blank TextEdit during DELAY and enter its assigned ID promptly:

```ducky
DELAY 5000
$_EVILDUCK_LOCK_TIMEOUT = 1000
WAIT_FOR_CAPS_CHANGE
STRINGLN 999bad
```

With no qualifying bit transition, expect blank TextEdit, the matching request's terminal **Deadline reason9**, **Timeout error26**, physical **line3**, and no quarantine. A matched waiting capture is useful, but the one-second window may be missed; record whether it was observed. This expected wait timeout is a **successful timeout-policy observation**, not an implementation failure. The helper observation interval is not precise execution or USB timing.

Distinguish competing outcomes: whole-request elapsed budget gives **Runtime reason6 / Timeout26**; tick/step exhaustion has its own diagnostics; disconnect/loss/backend or cleanup trouble is not the intended lock-timeout result. If unexpected lock transition lets the fixture type `999bad`, or another failure intervenes, classify this timeout trial **inconclusive**, preserve evidence and do not replay automatically. This passive trial does not prove LED delivery or host-global state.

## Trial 3 — STOP during a held-Shift wait

Prepare the observer first, then Start this fixture once and enter its actual request ID promptly:

```ducky
DELAY 5000
$_EVILDUCK_LOCK_TIMEOUT = 10000
HOLD SHIFT
WAIT_FOR_CAPS_CHANGE
STRINGLN 999bad
```

Keep the iPhone STOP control ready. After **MATCHED_CAPS_CHANGE_WAIT_OBSERVED** for that request, press the existing dashboard STOP **once** while that execution is still active. Expect the same request to become Idle/Cancelled (**reason2**), no `999bad`, no quarantine, and normal harmless manual lowercase typing afterward. Preserve waiting and terminal captures plus TextEdit/manual observations. Local cleanup or manual lowercase recovery is scoped evidence, not universal host key-release proof.

If the wait completed, expired or disconnected before STOP, waiting correlation was absent, or the assigned request differs, the intended STOP window was not established. Classify it **UNVERIFIED/inconclusive**, retain the evidence and do not automatically replay. Do not change host lock state just to make this sheet pass.

## GNU Screen / connection reminders

For an existing separately authorized USB CDC connection, rediscover and verify the current port using `ls /dev/cu.usbmodem*` after every reconnect/reset; never copy an old numeric suffix. Use the known Screen procedure at **115200 baud** and explicit `routeb <actual-stored-fixture-name>` selection. On the tested High Sierra/GNU Screen setup, **Control + J once** submits where Return appeared ineffective; this is the observed workaround, not a universal requirement or proven console defect. A template is `screen /dev/cu.usbmodemCURRENT 115200`; replace the placeholder with the verified current port. Submit each fixture only once.

## Classification

**PASS** requires the expected scoped output/status and evidence for the specified trial. **FAIL** requires demonstrated incorrect implementation under the tested conditions. Missing correlation, helper error or competing transition/failure is **UNVERIFIED**; an identified host/tooling constraint is **PLATFORM-LIMITED**. No broad Caps investigation or Windows prerequisite is introduced. Preserve exact release bytes and partial evidence; do not reflash, alter EDR1, clear results, reset settings or automatically run another payload in response to an inconclusive observation.
