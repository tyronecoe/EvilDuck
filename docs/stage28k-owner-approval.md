# Stage28K scoped owner approval and native evidence

Exact starting commit: `dce42b8664c2964019cf4b488388d08b2b7fc2d0`, Stage28J. Owner authorization carried by the authoritative Stage28K assignment:

> I approve D01–D10 as proposed for the Stage 28K synthetic-only harness.

This approves a new, isolated, deterministic memory harness only. It does not resolve UNKNOWN/BLOCKED semantics or permit production integration, USB transport, host input, firmware images, flash, boot, OTA, autorun, settings changes or Stage28L. Historical Stage28J acceptance cells and reports remain unchanged.

| Decision | Status in Stage28K | Selected limited implementation |
|---|---|---|
| D01 | OWNER APPROVED — synthetic only | Unchanged Planner owns snapshot union; no production backend access |
| D02 | OWNER APPROVED — synthetic only | Accepted copies current action into fixed memory journal; no delivery claim |
| D03 | OWNER APPROVED — synthetic only | Wrapper S/E/R uint64 counters, checked exhaustion; counter-based E association |
| D04 | OWNER APPROVED — synthetic only | One serialized driver owner, eight bounded setup requests and priority cancel flag |
| D05 | OWNER APPROVED — synthetic only | Fresh current zero drain receipt before new session, including historical-zero cases |
| D06 | OWNER APPROVED — synthetic only | Exactly eight opaque snapshot bytes; report ID/protocol/completion unselected |
| D07 | OWNER APPROVED — synthetic only | All old caps/API behavior retained; stable memory Reader and noncopyable Program |
| D08 | OWNER APPROVED — synthetic only | Checked arithmetic and US-only mapping; canonical modifier/INJECT_MOD/RESET remain blocked |
| D09 | OWNER APPROVED — synthetic only | Persistent member ownership; separate measured fixed journal/queue/control storage |
| D10 | OWNER APPROVED — synthetic only | No firmware boot/live/web/CLI/OTA path, settings, storage or arming mechanism |

## Owner-local evidence, not cloud or device verification

The assignment carries owner-reported/Terminal-screenshot-observed results on macOS High Sierra 10.13.6, Darwin 17G14042, x86_64; Apple LLVM 10.0.0 / Apple clang build 1000.10.44.4; stock Bash 3.2. The cloud has not independently executed or inspected that machine. This new status supersedes the narrower information available when Stage28J was written, without rewriting history.

| Owner-local scope | Reported result |
|---|---|
| Stage28E | 24/24 PASS, 109,591 assertions, zero failures |
| Stage28F | 20/20 PASS, 18,419 assertions, zero failures |
| Stage28G | 12/12 PASS, 37,765 assertions, zero failures |
| Stage28H unchanged portable kit, disconnected | PASS; 365 assertions, 3 traces, 19 exact eight-byte vectors, four blocked preflight cases/zero callbacks; explicit `Runner exit=0` |
| Owner-local E–H total | 166,140 assertions; E–G 165,775 plus H 365 |

E/F/G local compatibility edits removed `-fno-pie`, `-no-pie` and `-Wno-misleading-indentation`; `ASAN_OPTIONS=detect_leaks=0`. ASan/UBSan were retained; **Mac leak detection was not performed**. Those edits are not applied to the repository or cloud runners. Stage28H used the unchanged portable runner and manifest/C++17 probe. Its owner-local 365 assertions and Linux full-suite 483 assertions are different scopes, not additive duplicate execution credits.

No rerun is requested to re-prove that milestone. Stage28K itself has only been executed in Linux here, not on the Mac. Neither native memory-only PASS nor cloud sanitizer PASS establishes USB host delivery, device release state or physical installation safety. Original recovery firmware remains OWNER CONFIRMED AVAILABLE EXTERNALLY; no search, request or download occurred.
