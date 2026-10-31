# Right-side modifier acceptance — High Sierra review sheet

**EXPERIMENTAL — REVIEW ONLY — NOT AUTHORIZED FOR INSTALLATION OR EXECUTION.** These are future owner-operated checks for **ROUTEB-RIGHT-MODIFIERS-H1-EXPERIMENTAL-v1** only, after separate installation/test approval. No physical right-modifier test was performed by Codex. The prior H1 and **3/3 planned inherited lock-wait PASS** milestones are closed and need no repetition.

## Prepare once, record each actual request

Read INSTALL-MAC.md and ROLLBACK-MAC.md. Confirm the exact candidate build ID and record the installer-recorded application hash as such, unless independently read back. Keep exact accepted source/text-v2 rollback `cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02` available. Use the known **macOS High Sierra 10.13.6**, a blank plain-text TextEdit document, **US input**, Caps off and no physically held keys. Confirm autorun disabled, EDR1 inactive, execution idle and no existing quarantine. Keep the iPhone **STOP / check execution** control accessible.

Review and save each complete fixture through the existing supported manual path, then use **explicit Route B** and one deliberate Start. Never infer a request ID: record the assigned ID, terminal result and TextEdit observation. The five-second initial delay is a focus opportunity, not a guarantee of manual setup time. Missing correlation or a missed STOP window is inconclusive; no automatic retry. No special LED helper is needed, and the old exact-build lock-wait observer intentionally targets another build and must not be bypassed.

## 1. Right Shift, mixed sides and restored text — `rm-shift.txt`

```ducky
DELAY 5000
HOLD RSHIFT
STRING a
RELEASE RSHIFT
STRING b
SHIFT-RSHIFT c
RSHIFT d
INJECT_MOD RSHIFT
STRING e
ENTER
```

Expect one line **`AbCDe`** followed by Enter, and that request **Completed**. This combines persistent right Shift, left/right transient combination, right-side chord and a right-Shift-only tap, with ordinary lowercase restored. Caps/input state matters; preserve a mismatch rather than speculate about global lock state.

## 2. Other modifier-only taps — `rm-modifier-taps.txt`

```ducky
DELAY 5000
INJECT_MOD RCTRL
INJECT_MOD RALT
INJECT_MOD RGUI
STRINGLN 222taps
```

Expect exactly **`222taps`** and matching **Completed**, with no latched modifier or unintended application action in this tested Mac setup. Do not add shell/launcher shortcuts. Visible markers alone **do not prove host-level left/right bit distinction**; exact report-byte assertions establish that within the offline software boundary. If this host reacts unexpectedly to a modifier-only tap, preserve the scoped observation and stop; do not claim universal incompatibility or automatically replay.

## 3. STOP under held right Shift — `rm-stop.txt`

```ducky
DELAY 5000
HOLD RSHIFT
STRING a
DELAY 10000
STRINGLN 999bad
```

Expect one **`A`**. While the same request is still active in the ten-second delay, press the existing dashboard STOP **once**. Expect that request **Cancelled**, no injected `999bad`/`999BAD`, and harmless manual **`abc`** afterward appearing normally in lowercase. Record the request, timing/terminal observation and TextEdit evidence. If STOP misses the active interval, preserve the result as inconclusive instead of replaying. Local cleanup/manual lowercase is scoped recovery evidence, not a general USB retirement or host-key-release guarantee.

## 4. Duplicate right-modifier rejection — `rm-malformed.txt`

```ducky
STRINGLN 999bad
RSHIFT-RSHIFT a
```

Expect compile rejection **before output**, with blank TextEdit. Record the actual assigned request, diagnostic code and physical line as supplied; do not manufacture unavailable identifiers. Retained inactive branches and unused functions retain full-preflight validation; exhaustive rejection/boundary coverage remains automated.

## Preserve results and limits

A scoped PASS requires expected text, the matching request result and adequate correlation for that trial. A demonstrated implementation error is FAIL for that configuration. Missing evidence, missed STOP window or competing event is UNVERIFIED/inconclusive; an identified legacy-host/tooling limitation is PLATFORM-LIMITED. Preserve logs/screenshots and a short host/build/input/trial note before reboot or another trial, excluding credentials/private settings. Do not expand the suite or change Caps timing/EDR1 to force a result.

For an existing separately approved CDC/Screen connection, rediscover and verify `/dev/cu.usbmodem*` after reconnect; never reuse an old suffix. Use **115200 baud** and explicit `routeb <actual-stored-fixture-name>`. The observed High Sierra/GNU Screen workaround is **Control + J once** when Return appears ineffective; do not compensate with repeated submissions. No pySerial, compiler or native helper is required for these acceptance fixtures. Future installation tooling still uses the documented Python 3.8/esptool 4.12 interfaces.

Right-side names remain EvilDuck extensions; this sheet does not establish canonical Hak5 numeric encoding, AltGr/dead-key behavior, other host/layout compatibility or full DuckyScript 3.0 certification. A separate instruction is required before physical execution.
