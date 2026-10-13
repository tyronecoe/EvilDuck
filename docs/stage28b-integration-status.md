# Stage28B integration boundary

GO: isolated offline preview review only. NOT FLASH-AUTHORIZED.
NO-GO: Stage26 integration, flashing, boot, OTA or real HID in this assignment.

Stage27A remains a separate owner-controlled hardware track using frozen Stage26 commit
968c8e0aaf459b0b8b652cc57fe88225894ab64b. All235 protected files remain identical.
No production hook, interpreter dispatch, HID/USB/storage/network adapter, startup/arming path,
ATTACKMODE implementation, firmware ELF/BIN or installation profile is added. Original firmware
is OWNER CONFIRMED — AVAILABLE EXTERNALLY. No owner files/backups/private data requested or read.

This compiler accepts a bounded caller-memory source, retains expanded text in its arena, and
runs output cooperatively via mock events. It is not SD/SPIFFS streaming or a cooperative file
compiler. Source8192/text4096 caps remain. Program+Runtime now totals11804 target bytes; stack,
source ownership, task admission, runtime isolation and adapters need review before integration.

Recommended next separate milestone: bounded cooperative source/preflight compilation and
source-reader interfaces exercised entirely with mocks, including cancellation/read/seek faults
and compile-stack reduction. Do not lift caps or connect hardware automatically. Text aliases,
variable string interpolation, persistent modifiers, locale/Unicode, hardware status, random/jitter,
parameterized functions and advanced commands remain inventory gaps. No next milestone started.
