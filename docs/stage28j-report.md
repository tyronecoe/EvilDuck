# Stage28J integration contract decision package — Gate B, REVIEW ONLY

**Stage28J GO: Gate B document/contract review only. NO-GO: adapter implementation, Stage26 integration, real HID, firmware images, flash, boot, OTA.**

Exact starting HEAD `220970bc633d969e76d1d8c91750b5939377df0a`, branch `stage28i-integration-readiness-audit`, was clean before work. New delivery branch `stage28j-integration-contract-review` is created only when checks and deliverables are ready. Stage26 freeze remains `968c8e0aaf459b0b8b652cc57fe88225894ab64b`. No Stage28K has begun. Stage27A physical work remains independent and owner-controlled.

## Concrete outcome

The package turns the 19-seam audit into ten **unapproved proposals** with exact alternatives, hazards, remaining questions, minimum proof and empty owner acceptance fields. Recommend a mutually exclusive opt-in synthetic path with Planner as sole snapshot authority; mock acceptance rather than physical queue/completion claims; unique session/intent/report identity; one serialized stepping owner; a fresh current neutral drain/restart barrier; opaque eight-byte snapshots; unchanged preview bounds and explicit checked arithmetic/US-only subset; a non-double-counted lifetime/memory ledger; and separate startup/deployment authorization.

The proposed contract has a finite-state table and **18 specification-only tabletop traces**, including Retry, ownership conflicts, cancellation at callback return, stale evidence, disconnect uncertainty and small-clock wrap. None are newly executed tests or new APIs. In particular, wrapper IDs and a stricter restart barrier do not exist in current Bridge. Existing behavior is preserved; a future wrapper that cannot express an accepted choice must return a contract revision rather than change preview/production source.

Transport protocol/ID, linked enqueue and correlated completion, RTOS serialization, peak placement and canonical modifier/RESET semantics remain unresolved. Production implementation is not an official Hak5 semantic oracle. No grammar, source modifier, INJECT_MOD, RESET, adapter, report Sink, device driver, firmware or autorun behavior was implemented. Current multi-key settings writes remain non-atomic; no settings schema or policy changed.

## Owner-local evidence update

**Owner screenshot: PASS footer observed; compiler/version and explicit exit-status receipt not supplied.** The authoritative Stage28J assignment records owner local MacBook execution showing:

```text
PASS blocked_preflight cases=4 callbacks=0
PASS host-validation traces=3 blocked_cases=4 assertions=365
PASS runner: host-only mock validation; no hardware or OS input
```

This is **owner-reported** native local PASS evidence, not an independently captured cloud transcript or device test. Exact Apple compiler/version and explicit shell exit remain UNKNOWN. Native macOS/Apple toolchain is unavailable in this Linux cloud (**SKIP_ENVIRONMENT here**), but that does not negate the owner's report. Old Stage28H/I reports retain their historical pending wording; new documents carry this update. No owner rerun is requested for Gate B. No native receipt proves actual USB delivery or host HID behavior.

## Fresh execution evidence

All nine unchanged published runners completed freshly with exit 0. Outputs used new external directories; old result receipts were not reused as test executions.

| Suite | PASS groups | Unexpected FAIL | Assertions |
|---|---:|---:|---:|
| Stage27B | 25 | 0 | 2,543 |
| Stage28A | 23 | 0 | 526 |
| Stage28B | 26 | 0 | 4,733 |
| Stage28C | 17 | 0 | 390,573 |
| Stage28D | 21 | 0 | 14,989 |
| Stage28E | 24 | 0 | 109,591 |
| Stage28F | 20 | 0 | 18,419 |
| Stage28G | 12 | 0 | 37,765 |
| Stage28H | 19 | 0 | 483 |
| Total | **187** | **0** | **579,622** |

Applicable Linux GCC C++ paths used unchanged warnings-as-errors, ASan/UBSan and leak detection; no sanitizer fault occurred. Stage28H intentional negative/environment simulations keep their original classifications, not new compatibility passes. No new runtime suite, XPASS/XFAIL relabeling or assertion inflation. Historical production language XPASS and USB XFAIL remain unchanged and were not rerun by this preview-only scope. The new static checker is integrity evidence, not runtime assertions; proposed tabletop traces count as zero executed tests.

Fresh pinned Xtensa OBJECT-ONLY check passed: four unlinked objects, same exact core/SDK/compiler pins and three module hashes/sizes/sections as Stage28I. Program 6936 B + CompileSession 2408 B + Bridge 5020 B = **14,364 B**, excluding all unknown integration peaks. Bridge already contains Runtime 4872 B and Planner 84 B. Selected frame/section details and provenance are in `stage28j-target-build.json`; no production RAM/headroom/latency/high-water or physical allocation measurement was made. No firmware ELF/BIN/UF2 or deployment artifact was generated.

## Integrity and scope

The unchanged Stage28H Git-derived verifier passes all **235 frozen Stage26 files**. The new read-only checker checks all **1,017 preexisting Stage28I tracked files** against actual Git blobs, exact **47 source spans** (42 repository and five pinned dependency), D01–D10 empty acceptance cells, and 18 specification-only trace records. It rejects new paths outside Stage28J docs/tests. It does not establish a contract's correctness merely by recognizing IDs; the cited source and tables were manually reviewed for acceptance/cancel/ownership contradictions.

The current core/SDK are reused and never patched or installed. Original source evidence was independently rechecked before new files; additional direct anchors include the exact Bridge API, startup profile, partition CSV and saved reference contracts. Source/span hashes are in `stage28j-source-evidence.json`; the freeze inventory and new-file/source hash receipts are separate. Cloud setup skill review found no installation, services or reusable configuration changes necessary; no configuration draft was saved.

Before publication, 34 remote refs are snapshotted. Publication uses only a new branch, with no merge, rebase or force push. Post-push verification must prove every previous ref identical and only the new ref added at the delivered commit. The committed publication receipt is deliberately prepublication to avoid self-referential commit hashes; final exact SHA/post-push checks are supplied at delivery and in an external receipt.

Only these 13 files are added:

- `docs/stage28j-owner-decisions.md`
- `docs/stage28j-report-contract.md`
- `docs/stage28j-dependencies.md`
- `docs/stage28j-next-gates.md`
- `docs/stage28j-report.md`
- `docs/stage28j-source-evidence.json`
- `docs/stage28j-test-results.json`
- `docs/stage28j-target-build.json`
- `docs/stage28j-stage26-freeze.json`
- `docs/stage28j-static-audit.json`
- `docs/stage28j-source-hashes.json`
- `docs/stage28j-publication.json`
- `tests/stage28j/verify_audit.py`

No existing source/test/report, preview, firmware, Arduino Micro, partition, USB identity/descriptor, startup, storage, OTA or protected dependency changed. No owner backup, payload, credential or NVS value was read. Git ref/publication operations are the only required network work; scripts never launch filesystem/network/OS actions from DuckyScript. No physical access, enumeration, real HID, host injection, flashing, boot or OTA took place.

## Exact safe reproduction

Observed cloud tools: Python 3.12.14, GNU Bash 5.2.37, Debian g++ 14.2.0-19. Target pins: Arduino ESP32 3.3.0 / ESP-IDF 5.5 / Xtensa GCC 14.2, 16 MiB QIO 80 MHz, CPU 240 MHz, PSRAM disabled, existing USB-OTG/TinyUSB/CDC. These identify unlinked checks, not a newly linked firmware. No setup changes or automatic downloads required.

From repository root, use fresh external outputs:

```sh
stage28j_results="$(mktemp -d /tmp/evilduck28j-tests.XXXXXX)"
for stage28j_suite in stage27b stage28a stage28b stage28c stage28d stage28e stage28f stage28g stage28h; do
  python3 "tests/$stage28j_suite/run_tests.py" \
    --build-dir "$stage28j_results/$stage28j_suite-build" \
    --results "$stage28j_results/$stage28j_suite.json" || exit 1
done
python3 tests/stage28h/verify_freeze.py
```

Actual fresh cloud invocation for each suite used `/workspace/tooling/stage28j-<suite>` and `/workspace/tooling/stage28j-<suite>.json`; exact commands, counts, diagnostic stdout and sanitizer flags are in `stage28j-test-results.json`. Independent suites were run with three concurrent processes; no expectations were weakened.

Existing target check (output directory must not exist):

```sh
python3 tests/stage28h/target_check.py \
  --baseline-build /workspace/tooling/arduino/build/stage26-final-controlled \
  --original-core /workspace/tooling/arduino/data/packages/esp32/hardware/esp32/3.3.0 \
  --output-dir /tmp/evilduck28j-target-new
```

Static receipt checker (Python 3.12 cloud; Git history and existing source pins required, not a Mac prerequisite):

```sh
python3 tests/stage28j/verify_audit.py \
  --protected-core /workspace/tooling/stage26-final-controlled-core/data/packages/esp32/hardware/esp32/3.3.0 \
  --sdk /workspace/tooling/arduino/data/packages/esp32/tools/esp32-arduino-libs/idf-release_v5.5-b66b5448-v1/esp32s3 \
  --results /tmp/evilduck28j-static-new.json
```

The checker refuses an existing result or output inside the checkout. It only reads baseline/source/docs/Git and writes the fresh external receipt; no patch, compiler, adapter, runtime or network call. A source ZIP lacks historical Git objects and cannot run the freeze checker. The owner memory-only kit remains `bash tests/stage28h/run_host_smoke.sh`, unchanged, disconnected and optional; **no rerun requested now**.

For publication, save `git ls-remote --refs origin` before and after and use unchanged `tests/stage28h/verify_freeze.py --remote-before <before> --remote-after <after>`, plus an exact added-ref/commit check. Never force push or update prior refs.

## Review result and next decision

The ten recommendations and eighteen traces are now concrete enough for owner/peer review. They are not approved. Minimum next action is owner acceptance or specific alternatives for D01–D10; only a separate assignment could authorize Stage28K's isolated synthetic harness. Linked driver/USB protocol, production concurrency and memory, canonical blocked language semantics, physical recovery/profile and operation authorization remain later gates. Original stock recovery availability is OWNER CONFIRMED EXTERNALLY, not a search/request blocker.

**Stage28J GO: Gate B document/contract review only. NO-GO: adapter implementation, Stage26 integration, real HID, firmware images, flash, boot, OTA.** Stop for owner decisions. No Stage28K begun.
