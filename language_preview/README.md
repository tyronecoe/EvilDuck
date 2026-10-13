# Independent DuckyScript preview — offline only

Not included by any Arduino sketch/build profile. NOT FLASH-AUTHORIZED.

core.h/core.cpp contain original fixed-storage parser/evaluator/runtime code. There are no
Arduino, filesystem, USB, HID, network or SDK calls. Program compile/preflight produces
bounded IR; Runtime consumes it cooperatively through a caller-supplied mock event sink.
See docs/stage27b-design.md for limits and deliberately partial language semantics.

No proprietary compiler code was copied. This is an independent compatibility effort, not
Hak5 firmware, endorsement or complete DuckyScript3.0 compatibility. Stage27A hardware work
remains separate and must retain Stage26 reviewed binaries, hashes and authorization gates.
