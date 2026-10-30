# H1 High Sierra acceptance — prepared, not executed

**EXPERIMENTAL — REVIEW ONLY — NOT AUTHORIZED FOR FLASHING OR EXECUTION.** This short sheet applies only after separate installation, boot and physical-test approval. It tests EvilDuck H1 behavior, **not proven Hak5 compatibility**. Accepted v2 intentionally rejects this experimental syntax. Preserve the accepted rollback image and all partial evidence.

## Setup and evidence

Use the physical **macOS High Sierra 10.13.6** Mac, **US input source**, Caps off, no held keys and a blank TextEdit document. Confirm the exact dashboard build ID **ROUTEB-INJECT-VAR-H1-EXPERIMENTAL-v1**. Record the installer-recorded app SHA-256 `8a48f3f208165466e579f76a35fb7898fbaf1188e746ca3a0d60e99c576b0ecd` as installer-recorded unless independently read back. Confirm autorun disabled, EDR1 inactive, execution idle and no quarantine. Keep the iPhone dashboard’s existing **STOP / check execution** control accessible. No special helper or lock-LED action is needed.

The four `.txt` files are review fixtures, not automatically uploaded, installed as examples or run. Review each complete file before using the already supported manual upload/save path. Start through the **explicit Route B** path once, or an existing separately approved CDC connection with `routeb <actual-stored-fixture-name>`. Ordinary legacy Run does not establish use of this engine. Do not predict request IDs: record the actual assigned request, boot/session if available, terminal status and observed TextEdit text for each trial. Unknown identifiers stay unknown.

For an existing approved GNU Screen session, rediscover and verify `/dev/cu.usbmodem*` after reconnect and use 115200 baud. The owner previously found **Control + J once** submitted a command when Return appeared ineffective; this is an observed workaround, not a universal rule or diagnosed root cause. Never compensate by repeatedly submitting Start. Each fixture’s initial 5-second DELAY is only a focus opportunity, not a guarantee that manual setup will fit; prepare before Start and preserve a missed window as inconclusive.

## Trial 1 — fixed scalar, copy, repeated injection, reassignment

File: **h1-fixed-copy.txt**

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

Focus TextEdit during the initial delay. Expect exactly **`aaA00!!`** and the matching request **Completed**, without fault/quarantine. Preserve the output and matching dashboard result. The literals are experimental H1 values, not official runtime reference vectors. They are not instructions for a genuine Hak5 device. No decimal printing or variable mutation is intended.

## Trial 2 — held Shift and one deliberate STOP

File: **h1-stop-held-shift.txt**

```ducky
DELAY 5000
VAR $K = 0x0004
HOLD SHIFT
INJECT_VAR $K
DELAY 5000
STRINGLN 999bad
RELEASE SHIFT
```

Expect one **`A`**. While the same request remains active during its second DELAY, press the existing dashboard STOP **once**. Expect that request to become **Cancelled**, no `999bad`, no quarantine, and harmless manual lowercase typing afterward. Preserve request/status and TextEdit evidence. If STOP misses the intended active window, completion is ambiguous or another error intervenes, preserve the result as **UNVERIFIED** rather than automatically replaying. Local cleanup submission and manual lowercase are scoped recovery observations, not general host-key-release or endpoint-retirement proof.

## Trial 3 — malformed retained operand rejects before output

File: **h1-malformed.txt**

```ducky
STRINGLN 999bad
INJECT_VAR 0x0004
```

Expect compile rejection and **blank TextEdit**. Record the actual request, physical line and diagnostic code; no expected identifier/code is invented here. A variable operand is required, so the earlier text must not be emitted. Do not “fix” the fixture by supplying a numeric literal through another command. Exhaustive invalid runtime values remain offline tests, not a physical keycode sweep.

## Optional Trial 4 — generated value captured and copied once

File: **h1-random-copy.txt**

```ducky
DELAY 5000
VAR $K = $_RANDOM_LOWER_LETTER_KEYCODE
VAR $COPY = $K
INJECT_VAR $COPY
INJECT_VAR $COPY
```

Start only as a separate deliberate trial. Expect **two identical lowercase letters** and matching **Completed**, whichever one finite draw selected. Repeated results across runs are valid. This shows practical EvilDuck capture/copy/reuse only; it does not establish statistical quality, all layouts or genuine DS3 encoding.

## Classification and preservation

**PASS** means the expected scoped output and matching request result are evidenced for that trial. **FAIL** requires demonstrated incorrect behavior attributable to this implementation under the tested setup. Missing correlation, missed STOP window or ambiguous output is **UNVERIFIED**. An identified High Sierra/tooling/host limit is **PLATFORM-LIMITED**, not universal incompatibility. Preserve screenshots, installer/Terminal output and a short host/firmware/trial note before rebooting or another trial; never include passwords, private settings or backups in shared evidence.

No automatic retry, Caps normalization, LED-protocol change, host shell, arbitrary payload, keystroke collection or private-file access is part of these fixtures. A practical H1 pass cannot settle the official runtime numeric contract. The next decisive canonical reference remains a separately authorized, calibrated genuine DS3 capture that correlates a generated scalar, copy and repeated injection; the existing reference kit remains distinct and unexecuted.
