# Independent DuckyScript preview — offline only

Not included by any Arduino sketch/build profile. NOT FLASH-AUTHORIZED.

core.h/core.cpp contain original fixed-storage parser/evaluator/runtime code. There are no
Arduino, filesystem, USB, HID, network or SDK calls. Program compile/preflight produces
bounded IR; Runtime consumes it cooperatively through a caller-supplied mock event sink.
See docs/stage28b-design.md and docs/stage28a-design.md (current) and docs/stage27b-design.md (historical) for limits and deliberately partial language semantics.

No proprietary compiler code was copied. This is an independent compatibility effort, not
Hak5 firmware, endorsement or complete DuckyScript3.0 compatibility. Stage27A hardware work
remains separate and must retain Stage26 reviewed binaries, hashes and authorization gates.

Stage28A adds cooperative numeric expression function calls in fixed continuations.
The runtime is still mock-only, unlinked and NOT FLASH-AUTHORIZED.

Stage28B adds bounded multiline STRING/STRINGLN via one instruction per block and
compact line records in the existing text arena. STRING strips leading spaces/tabs,
concatenates lines and preserves trailing bytes. STRINGLN strips exactly one leading
tab and emits ENTER per body line; spaces/rest tabs/trailing bytes remain literal.
Empty blocks emit nothing. These formatting edge policies are documented, not
independently established official compiler results. Forward DEFINE substitution
is bounded/nonrecursive; $variable text stays literal. Aliases remain unsupported.
See docs/stage28b-report.md for fresh tests, limits and object-only resource evidence.
No storage/USB/HID adapter, installable firmware or arming path exists in this preview.
