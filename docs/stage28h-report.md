# Stage28H — offline High Sierra validation kit and trace audit

**GO: isolated offline review only.**
**NO-GO: Stage26 integration, real HID, flashing, boot, OTA or production deployment.**

Base7d391c0900eb4c5eba730abc3143008dcdeb1ae1 (Stage28G), verified HEAD and clean worktree
before any edits. New branch stage28h-host-validation-kit only. No earlier ref moved.
No Stage28I started. Stage27A remains a separate owner-controlled hardware lane.

## Delivered one-command kit

In a reviewed source checkout or unpacked source ZIP root, EvilDuck unplugged:

```sh
bash tests/stage28h/run_host_smoke.sh
```

New Bash3.2-compatible runner uses POSIX/BSD essential utilities, quoted paths, existing clang++
or c++ (optional CXX single executable). It checks root/source fixtures; shows sanitized compiler
path/version and platform/build; probes C++17 compile/link/run; compiles only core.cpp/keyboard.cpp/
bridge.cpp plus new inert fixture; compares compiled JSON manifest byte-for-byte; executes tests.
No Python/Git/Arduino/SDK/network/device/installation dependency for owner smoke. No automatically
written project receipt. One unique normalized local mktemp directory, constrained EXIT/INT/TERM
cleanup, no deletion of other files. relative TMPDIR from another working directory also tested.

Common -std=c++17 -Wall -Wextra -Werror only on clang path. Existing misleading-indent suppression
is added for non-clang/GCC path; no Linux -no-pie/-fno-pie or assumed Apple sanitizer flags in the
portable runner. Cloud sanitizer wrappers and target compilers are distinct from the owner recipe.
Bash3.2 syntax reviewed but actually executed only on Linux Bash5.2.37; native Apple remains unrun.

PASS0 means exact fixtures matched. Environment/compiler/version/C++17/SDK/probe/temp insufficiency
is SKIP_ENVIRONMENT77. Missing root/fixture FAIL2; real build/program failures propagate original
nonzero status; damaged compiled manifest or missing receipt FAIL1. No unexplained source failure
is silently relabeled SKIP. Child-tool diagnostics captured before redaction. Project/home/temp
prefixes and custom compiler parent paths hidden in shareable text. Known-prefix redaction does
not guarantee anonymity of arbitrary malicious compiler output; owner should review transcript.

## Distinct fixed-buffer traces and manifest

New fixture is NOT a copied Stage28G8-report smoke. Reports stored in fixed16 accepted slots plus
one retry snapshot; callback count capped32; each scenario bounded500 virtual steps. Readonly
constexpr sources/vectors/retry masks/specs, no writable globals or dynamic report queue. Actual
existing compiler/Runtime/Planner/Bridge used, no alternate interpreter. Values are synthetic
8-byte snapshots, without USB descriptors/report IDs or physical transport claims.

| Trace | Exact accepted vectors | Callback attempts | Admissions / acks / Delay | Verified behavior |
|---|---:|---:|---|---|
| repeated_transient_delay_retry |7|10|3/3/1|Neutral sync, two distinct a press/restoration pairs,2ms virtual delay after ack, then b; Retry at0-based1,2,4|
| shared_owner_selective_release_drain |9|13|4/4/1|Prepared owner0 a + owner1 SHIFT; source HOLD/RELEASE/repeated RELEASE a require fresh same-union acceptance; b/restoration; explicit zero drain; Retry3,4,10,11|
| stale_zero_current_drain |3|5|1/1/0|Prior accepted zero cannot complete current drain; Retry2,3 before fresh zero acceptance|
| blocked_preflight |0 callbacks|0|No execution|INJECT_MOD/HOLD CONTROL, HOLD SHIFT, RESET, RELEASE_ALL reject before sink invocation|

All traces end Completed with exact current expected union/neutral evidence. Fixture checks one
report attempt per driver step, no source ack on report turns, no duplicate admission on Retry,
Delay no report/no advancement before prior action ack, retry-mask exact identity, counters, and
current-drain terminal/evidence. Reports printed with trace name/index/eight hex bytes, mismatch
shows expected/actual; bounded state/counter faults include trace/line/condition. No sleep/timer.

expected-traces.json matches compiled --manifest output byte-for-byte, including retry positions,
counts, terminal assertions and callback policy. Compact JSON is intentional for POSIX cmp without
Python/jq on High Sierra; readable trace descriptions above. Fixture assertions365, each negative
source has0 callbacks. Identical ownership reports have distinct acknowledgements. Prepared SHIFT
is prior internal API, not new source modifier support. All blocked semantics remain blocked.

## Fault diagnostics and honest development results

Independent Python cloud audit uses disposable synthetic projects/compiler wrappers only. Tests
real compile/run with ASan/UBSan/leak, paths with spaces, relative TMPDIR outside project, missing/
nonexecutable compilers, failing version/C++17 probes, compile exit42, warning exit43, program exit7,
zero-exit missing receipt, wrong root, missing/damaged JSON, compiled expectation mismatch, TERM
interrupt cleanup143, direct byte mismatch diagnostic and untouched user-sentinel/source hashes.

New runner defect found: its first draft printed custom compiler absolute parent paths. Initial
audited16 groups8 PASS/8 FAIL, all failures from the shared path-leak check. Minimal reproduction:
select a synthetic compiler outside project/home/temp-prefix mappings; runner displayed its full
parent path. Fixed by redacting custom parent, sanitizing captured logs, and verifying it across
success/failure paths. All mandatory tests freshly rerun. Relative temp-parent normalization also
added/tested to keep cleanup valid after root cd. No true preview-engine defect found or fixed.
Negative mismatch macro exists only in test fixture, never enabled by owner runner. Mock failures
are deliberate fault inputs, not relabeled engine successes or supported-language claims.

## Fresh suites and environment status

| Suite | PASS groups | Final FAIL | Assertions |
|---|---:|---:|---:|
| Stage27B |25|0|2543|
| Stage28A |23|0|526|
| Stage28B |26|0|4733|
| Stage28C |17|0|390573|
| Stage28D |21|0|14989|
| Stage28E |24|0|109591|
| Stage28F |20|0|18419|
| Stage28G |12|0|37765|
| Stage28H |19|0|483|
| TOTAL |187|0|579622|

All9 suites actually built/executed, old runners unchanged, fresh external outputs, warnings-as-
errors/ASan/UBSan/leak clean for executed C++ paths. Stage28H483=365 C++ assertions counted once
plus118 Python checks; repeat runner smoke invocations are not counted as extra C++ assertions.
Its19 groups include one trace-audit group, not a compatibility percentage. Exact names/status/
assertions/stdout and compiler commands are in test-results.md/.json; paths redacted there.
No preview XPASS/XFAIL or skipped mandatory runtime suite. Historical production diagnostics
remain immutable and unrerun by this preview-only task. Expected simulator failure classifications
are recorded as verified runner checks, separate from actual feature support.

Direct portable one-command Linux runner also freshly passed with real /usr/bin/c++ DebianGCC14.2,
exit0,19 vectors and365 assertions. Cloud Bash5.2.37/kernel6.18.44. Native macOS10.13.6/Apple clang/
stock Bash3.2 SKIP_ENVIRONMENT, not available/run here; no owner result supplied. Syntax review and
Linux tests do not prove native compatibility. Manual disconnected recipe/troubleshooting and
unique local sanitized-transcript capture are in macos-validation.md. ZIP lacks Git history for
frozen Git verifier, which is not a requirement of the one-command smoke.

## Object-only resources and immutability

Fresh pinned Arduino3.3.0 / ESP-IDF5.5 / Xtensa GCC14.2 original/protected core, compiler/archive/
config/source checks pass;16MiB/QIO80/CPU240/PSRAM-disabled/TinyUSB/USB-OTG/CDC unchanged. Compile
unlinked core/keyboard/bridge/metadata objects only. All3 actual module objects byte-identical to
Stage28G. No firmware ELF/BIN/UF2 or deployment artifact, no production flash/RAM/OTA claim.
Exact pins/source/objects/sections/frame hashes in target-build.json, published project paths masked.

| Target sizeof | Stage28G B | Stage28H B | Delta |
|---|---:|---:|---:|
| Program |6936|6936|0|
| Runtime |4872|4872|0|
| CompileSession |2408|2408|0|
| Planner |84|84|0|
| Bridge (includes Runtime+Planner) |5020|5020|0|
| Event / Instruction |4/12|4/12|0|

No enum/opcode/Sink ABI change. Event/Instruction additionally static-asserted in fixture.
Entire language_preview tree independently byte-identical to base, as are all historical docs/
tests. No new global writable mock state or dynamic per-event buffer. Test harness stdio/compiler/
Python allocations outside engine; no unmeasured zero-malloc claim. Existing allocation probes
freshly pass. Host fixture constants/stack buffers are not firmware resource growth.

Selected core text/literal/rodata13292/1892/1838, planner2181/168/47, bridge1586/180/0, data/BSS0/0,
all unchanged. Frames unchanged: Bridge step/receive/report32, start48, planner ownership96,
Runtime tick112, expression preparation144B; full object metadata retained. Prior selected runtime
stack estimate about1.5KiB before caller/libc remains only an estimate. No physical heap/latency/
task-stack high-water or USB measurements. Frozen Stage26 firmware not rebuilt/integrated.

All235 protected files compared directly with immutable Git baseline
968c8e0aaf459b0b8b652cc57fe88225894ab64b plus inventory/hash checks. Current remote snapshot32 refs
(including Stage28G) compared before publication; verify all after pushing only this new branch.
No prior ref merge/rebase/force; final exact SHA/ref check recorded externally and at delivery.
No hardware/private backups/owner scripts/credentials read, no telemetry/network test or installs.
Only required Git publication checks/push use network, never the offline kit or fixtures.

## Files and review boundary

Created only tests/stage28h/{run_host_smoke.sh,test_host_validation.cpp,expected-traces.json,
run_tests.py,target_check.py,verify_freeze.py,test-results.md,test-results.json};
docs/stage28h-{macos-validation,reproduction,report}.md and reproduction.json,
source-hashes.json,target-build.json,stage26-freeze.json,preview-identity.json,publication.json.
No preexisting source or docs/test modifications. Reproduction/source/publication receipts are
stage-scoped; raw cloud logs externally retained, not huge owner transcripts in repository.

BLOCKED unchanged: INJECT_MOD lifecycle, source modifier HOLD/RELEASE, RESET independent owner
scope/release-all. Also ALL real HID/USB, Stage26 integration, flash, boot, OTA and deployment.
Next proposal only: owner may run disconnected native kit and review sanitized results. Any
real engine defect should stop its fix for separate review. No automatic next implementation.

**GO: isolated offline review only.**
**NO-GO: Stage26 integration, real HID, flashing, boot, OTA or production deployment.**
