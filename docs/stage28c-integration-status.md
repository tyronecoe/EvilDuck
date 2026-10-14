# Stage28C integration boundary

GO: isolated offline review only. NOT FLASH-AUTHORIZED.
NO-GO: Stage26 integration, production adapters, flashing, boot, OTA or real HID.

Stage27A remains independently owner-controlled with frozen Stage26
968c8e0aaf459b0b8b652cc57fe88225894ab64b. All235 protected files remain identical.
No sketch/source/HID/storage/USB/network/startup/arming/partition/migration/Arduino Micro changes.
Original firmware stays OWNER CONFIRMED — AVAILABLE EXTERNALLY; no private backups/data requested.

CompileSession is a RAM-only bounded two-pass compiler, not an SD/SPIFFS adapter. Its exact-size,
stable-source, callback lifetime and prompt-return contracts must be reviewed before any adapter.
Program/Runtime still operate only through synthetic mock events. Source8192/text4096 remain caps.
Target Program+Runtime11808B plus an active CompileSession2408B totals14216B, excluding external
reader/source/sink storage. These are software object measurements, not embedded heap/task-stack.

Recommended next separate milestone: reference-backed mock-only keyboard/modifier ownership and
report planning, including merge/rollover/release/cancellation tests, before any real HID adapter.
No next milestone is started. Compile-stack/work-latency/admission and immutable-reader contracts
also need integration review; a passing object compile is not hardware or production readiness.
