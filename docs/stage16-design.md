# Stage 16 paired HID routing integration

Baseline: Stage15 `7a8229f9c04d2a5423c179fe8daa42e048554560`. No language,
identity, descriptor, partition, MSC or randomization redesign.

## Reviewed contract and regressions

Adopt the exact two Stage15 proposals together. Nonzero OUTPUT must reach
FeedbackKeyboard::_onOutput; FEATURE must never be treated as keyboard LED evidence.
INPUT/invalid SET_REPORT types are rejected. Legacy type0/ID0 interrupt normalization
and actual report0 devices retain their existing compatibility behavior. Normalized
keyboard ID1 requires exactly one LED byte. IN report ID1 and eight-byte layout remain.

Core-only would retain the misleading FEATURE workaround; companion-only would lose
control OUTPUT feedback. Thus the production backend has a native compile guard and
the build verifies the selected dependency before enabling it. Host mocks are exempt.
The Stage12 direct hook regression now calls OUTPUT, the corrected control delivery
hook; its name and desired LED behavior remain. FEATURE rejection is tested separately.

The upstream patch guards HID instance capacity, null nonempty buffers, empty/null
OUTPUT and ID-prefix extraction before dereference/narrowing. It dispatches by type
and removes unsafe debug-table indexing. Unknown report IDs cannot select a device.
It does not establish arbitrary pointer allocation length, support additional HID
interfaces, or authenticate an incoming packet's USB-session origin. Generic empty
FEATURE is device-defined; EvilDuck inherits a no-op FEATURE hook.

Stock USBHIDKeyboard::_onOutput remains unsafe when directly invoked with invalid
inputs, and retains portMAX_DELAY event posting for valid inputs. The router now
rejects empty/null OUTPUT before that hook; EvilDuck overrides it entirely with a
fixed-copy feedback receiver, no executor lock/event queue/filesystem/log/HID sends.
This bypass is not a global upstream repair. Other USB event callbacks may still
block, and descriptor allocation has not been generally hardened.

## Dependency architecture

`tools/patched_core.py` verifies platform version, the entire source tree fingerprint,
nine Stage15 core/SDK records and patch SHA. It copies the core without hardlinks,
patches only the disposable copy with zero fuzz, checks the patched tree/hash, and
rechecks the original. No download/install is performed. Unexpected source or core
versions fail closed. The tree fingerprint includes every regular file except
Arduino-generated `installed.json` package-index metadata; that catalog is copied
but is not release source. Path/hash pairs are JSON-encoded with compact separators
and SHA256-hashed; this definition is cross-platform for POSIX Linux/macOS layouts.

The independent CLI configuration selects only the copied 3.3.0 core. Installed tool
executables are shared through symlinks and existing user libraries are inputs. They
are not OS write-protected; the wrapper invokes compilation only and never patches,
installs or updates them. Build/cache/download outputs are outside the owner data and
user roots. No write-capable migration helper is invoked. The isolated receipt
records resolved paths and pins. CLI source-tree selection is checked after property
resolution and after the clean build; a mismatch is fatal. An ordinary IDE/native
build fails the firmware guard rather than silently using the old workaround.

The guard macro is a usability safeguard, not authentication against an operator
manually falsifying compiler flags. The supported wrapper additionally checks bytes,
compilation database, object/map and final ELF. It verifies one strong SET_REPORT
symbol, the OUTPUT override, no derived FEATURE override, and linked HID/CDC/MSC
callbacks. The routing translation unit must come from the verified disposable core.
Arduino's exact generated first #line directive is checked separately from backend
bytes. Linked disassembly and object/ELF/application/compiler hashes are retained.

This makes dependency preparation and configuration reproducible; it does not claim
bitwise-identical binaries across build paths/times/hosts. No entire USB stack is
vendored. No additional persistent runtime storage/queue/heap model is introduced.

## Test boundaries

Stage15 historical faults use the exact Git baseline backend in a separate temporary
file, validated byte-for-byte. Original results/reference records are not rewritten.
Stage16 extracts the real patched registry/dispatch/callback bodies and links the
current production modules against RAM/mock USB/storage/clock interfaces. This is
not the full USB controller, descriptor allocator, FreeRTOS scheduler or physical bus.
The actual full firmware is separately compiled and linked against the patched core.
Concurrent snapshot/executor-lock tests exercise the host synchronization model,
not on-device RTOS latency or ThreadSanitizer certification. The source contract
cannot reject a false allocation size supplied by an arbitrary C caller; actual
TinyUSB endpoint storage bounds remain the upstream controller contract.
