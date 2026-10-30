# Experimental H1 owner checks — prepared, not executed

This is a future review sheet for **ROUTEB-INJECT-VAR-H1-EXPERIMENTAL-v1** only. Existing accepted releases intentionally reject INJECT_VAR. No installation package or physical execution is authorized by this document. Keep the owner-accepted source/text v2 application unchanged: **1,413,200 bytes**, SHA256 `cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02`. Its exact bytes exist as `application.bin` in the published v2 ZIP; do not rebuild a rollback substitute. The newer lock-wait release is software-tested but no new physical acceptance was supplied. Original packages, rollback resources and private backups remain untouched.

A later independently approved installation/recovery plan would have to verify chip/security, installed partition/OTA state and exact application identities before any app-only operation. No executable flashing/rollback commands are supplied here and no bootloader/table/NVS/SPIFFS/OTA metadata change is proposed.

## Setup and evidence boundary

Only after separate prototype installation and test approval, use the physical High Sierra10.13.6 Mac, US input source, Caps off, no held keys and blank TextEdit. Confirm the exact experimental dashboard build ID and preserve its installer-recorded app hash without calling that a physical readback. Keep iPhone STOP accessible and autorun disabled. Use explicit Route B selection and one deliberate Start per reviewed fixture; no automatic replay. Record actual request/session/boot identifiers when available, leaving unavailable evidence unknown.

For a separately authorized GNU Screen connection, rediscover and verify the current `/dev/cu.usbmodem*` port after reconnect/reset. Use115200 baud and explicit `routeb <actual-fixture-name>`. On the owner's tested High Sierra/Screen setup, **Control + J once** submitted commands when Return appeared ineffective; this remains an observed workaround, not a root-cause diagnosis. Never send repeated submissions to compensate for missing output.

## 1. Fixed H1 scalars, copy, repeated injection and reassignment

```ducky
DELAY 5000
VAR $K = 0x0004
VAR $COPY = $K
INJECT_VAR $COPY
INJECT_VAR $COPY
$K = 0x0204
INJECT_VAR $K
$COPY = 0x0027
INJECT_VAR $COPY
INJECT_VAR $COPY
$K = 0x021E
INJECT_VAR $K
INJECT_VAR $K
```

After focusing TextEdit during DELAY, H1's chosen policy predicts exactly **`aaA00!!`**, followed by matching Completed. These numeric literals are **experimental EvilDuck H1 values**, not official Hak5 runtime observations. Do not transfer guessed literals to a genuine reference device. A mismatch is scoped prototype/host evidence to preserve and reduce, not proof of universal incompatibility or a reason to restart Caps diagnostics. No decimal printing or variable mutation is intended. Exhaustive report/copy invariants remain offline tests.

## 2. STOP during a held-state interval

```ducky
DELAY 5000
VAR $K = 0x0004
HOLD SHIFT
INJECT_VAR $K
DELAY 5000
STRINGLN 999bad
RELEASE SHIFT
```

H1 plus the existing persistent modifier merge predicts one **`A`**. While the same request remains active during the second DELAY, issue the existing dashboard STOP once. Expect scoped Cancelled, no `999bad`, no quarantine and harmless manual lowercase afterward. Capture request/status and TextEdit evidence. If STOP missed the intended window or a competing error occurred, mark the trial inconclusive and do not automatically replay. Local clear submission/manual lowercase is not general host-key-release or endpoint-retirement proof.

## 3. Retained malformed operand rejects before output

```ducky
STRINGLN 999bad
INJECT_VAR 0x0004
```

The prototype accepts an ordinary variable operand, not a direct numeric literal. Expect compile rejection and blank TextEdit; record the actual request, physical line and diagnostic rather than manufacture identifiers. Inactive retained branches and unused functions are also preflighted; excluded preprocessing has its established separate policy. Runtime invalid-scalar cleanup and all numeric boundaries are automated, not a blind physical keycode sweep.

## Optional random capture check, separately deliberate

```ducky
DELAY 5000
VAR $K = $_RANDOM_LOWER_LETTER_KEYCODE
VAR $COPY = $K
INJECT_VAR $COPY
INJECT_VAR $COPY
```

H1 predicts two equal lowercase letters with US/Caps-off context, whatever one finite draw selected. Repeats across runs are valid. This would demonstrate practical EvilDuck capture/copy/injection only; it cannot establish genuine DS3 encoding, statistical randomness or all layouts. Do not expand the physical suite without documenting it.

No EXFIL, host shell, credential access, keystroke collection, networking, LED protocol change or arbitrary owner payload is involved. Missing evidence is UNVERIFIED; isolated High Sierra/tooling limits are PLATFORM-LIMITED. The genuine-DS3 reference kit is separate from this prototype sheet. Neither kit has been physically executed by Codex.
