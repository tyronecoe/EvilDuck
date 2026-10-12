# Stage 18 production-source startup tests

[Commands](../../docs/stage18-reproduction.md). The exact original/patched initArduino
bodies and patched status storage/getter are extracted from hash-verified source.
They compile with the actual EvilDuck setup/loop and mock SDK/serial/application
services under ASan/UBSan. No actual SDK NVS implementation, real flash or owner script
is run. Synthetic20KiB byte pattern is not invented owner NVS content or a page emulator.
Erase/write APIs instrument calls and compare every protected byte. Success, documented
error codes, unexpected signs/bounds, repeated explicit attempts, later retry latch and
both profiles are tested. Preserved autorun=true reaches only a no-execution stub on
healthy normal startup, never on failure or safe profile. Ten-thousand loop iterations
exercise bounded quiescence, no service activation or implicit retry.

Three original-core erase/error observations and two SDK-side-effect injection
observations are separate from passes. They do not certify real SDK execution.
Dependency tests reject HID-only/modified sources, absent native guard/status hook and
verify final linked policy. Source order test uses actual main.cpp. All prior suites,
allocation probes and historical routing faults remain separately accounted.

NVS header/error codes match the installed SDK definitions; corrupted metadata/flash
errors are injected return codes, not an independently executed page-corruption model.
This proves the Arduino layer and application gate. SDK-internal recovery, partition
boot failures, diagnostic transport, timing/heap/task-stack and physical data retention
remain untested. No destructive recovery or automatic arming command is provided.
