# Stage28K executed synthetic harness delivery report

**GO: review the executed memory-only D01–D10 harness and its T01–T18 results. NO-GO: Stage26 integration, real HID/USB/OS input, firmware images, flash, boot, OTA or Stage28L.**

Exact starting HEAD/branch: `dce42b8664c2964019cf4b488388d08b2b7fc2d0` / `stage28j-integration-contract-review`, verified clean before changes. Immutable Stage26 baseline `968c8e0aaf459b0b8b652cc57fe88225894ab64b`. New branch: `stage28k-synthetic-report-journal`; no merge, rebase or force push. Owner approved D01–D10 **only** for this milestone. The historical decision cells and all old files stay unchanged.

## Implemented and verified

An isolated C++17 Driver owns Program/CompileSession/Bridge, authoritative counter-delta intent identities, immutable report-phase identities, a fixed non-overwriting acceptance journal, priority cancellation, eight setup requests, fixed diagnostics and a fresh current neutral restart barrier. No new event parser or private API inspection; no equal-byte E inference or queue-as-ack mapping. Delay is journaled as source acceptance with zero report actions. Shared ownership, rollover, transient restoration and source progress remain the unchanged Planner/Bridge behavior.

All 18 formerly specification-only traces have **new actual executions**. There are no blocked/tabletop traces marked passed. Nineteen additional focused groups cover journal/request/counter bounds, stale notices, lifetimes/destructor, source cap/numeric/locale, runtime deadline, first-fault retention, read errors/compile cancellation, source STOP in a function, Delay cancellation, queued setup and Failed/exception decisions. Exact receipts include S/E/R, eight-byte intent/acceptance snapshots, phase, attempt/outcome/receipt state, E admission/ack ticks, counters and diagnostics.

## T01–T18 actual status

Attempts/acceptances below include sync, setup and explicit drain where exercised; source acks include Delay acks. They are not USB transfers or host receipts. T17 runs six failing preflight inputs internally, with no source report attempts; its final empty Driver summary is zero. Per-scenario checks and expected bytes are in `test_journal.cpp`; JSON contains detailed journal rows. No table entry represents an OS test.

| Trace | Status | New assertions | Report attempts | Accepted records | Total source acks / Delay acks |
|---|---|---:|---:|---:|---:|
| T01 | PASS — executed | 40 | 3 | 3 | 2 / 0 |
| T02 | PASS — executed | 44 | 4 | 4 | 2 / 0 |
| T03 | PASS — executed | 26 | 2 | 2 | 1 / 0 |
| T04 | PASS — executed | 42 | 7 | 7 | 0 / 0 |
| T05 | PASS — executed | 55 | 6 | 3 | 1 / 0 |
| T06 | PASS — executed | 69 | 5 | 5 | 3 / 1 |
| T07 | PASS — executed | 37 | 3 | 2 | 0 / 0 |
| T08 | PASS — executed | 37 | 3 | 3 | 0 / 0 |
| T09 | PASS — executed | 38 | 3 | 3 | 0 / 0 |
| T10 | PASS — executed | 43 | 4 | 4 | 0 / 0 |
| T11 | PASS — executed | 33 | 4 | 2 | 0 / 0 |
| T12 | PASS — executed | 42 | 5 | 3 | 1 / 0 |
| T13 | PASS — executed | 1285 | 256 | 0 | 0 / 0 |
| T14 | PASS — executed | 8 | 1 | 0 | 0 / 0 |
| T15 | PASS — executed | 48 | 3 | 3 | 1 / 0 |
| T16 | PASS — executed | 49 | 7 | 4 | 1 / 0 |
| T17 | PASS — executed | 36 | 0 | 0 | 0 / 0 |
| T18 | PASS — executed | 41 | 4 | 4 | 1 / 0 |

**New Stage28K: 37 PASS groups, zero final unexpected FAIL, 10,346 primary C++ assertions.** No XPASS/XFAIL or environment skip substituted for an unexecuted trace. Applicable Linux ASan/UBSan/leak checks passed; exact options/version/commands in `stage28k-test-results.json`. A deliberately failing negative-control build exits 1 (36 PASS/one deliberate FAIL); repeated assertions from it are excluded. The separate healthy allocation probe observes zero C++ new calls and is non-sanitized; neither probe repeats add primary groups/assertions. Runner rejects wrong/missing JSON/cases/receipt associations and nonzero/sanitizer outcomes.

Development history is not hidden: the first run had **32 PASS / one FAIL, 10,181 assertions**, caused by the new lifetime test asking `Runtime::variable("n")` rather than the existing required `"$n"`. Source/API inspection confirmed the mistake; the test call was corrected, not its expected value or the frozen API. The next 33-case run passed 10,197 assertions. Subsequent relevant STOP/Delay/request/Failed checks produce the final 37-case run above. Those development totals are not added to delivered assertions. No production or preview defect was repaired to green the report.

## Separately fresh unchanged regressions

| Suite | PASS groups | FAIL | Assertions |
|---|---:|---:|---:|
| Stage27B | 25 | 0 | 2543 |
| Stage28A | 23 | 0 | 526 |
| Stage28B | 26 | 0 | 4733 |
| Stage28C | 17 | 0 | 390573 |
| Stage28D | 21 | 0 | 14989 |
| Stage28E | 24 | 0 | 109591 |
| Stage28F | 20 | 0 | 18419 |
| Stage28G | 12 | 0 | 37765 |
| Stage28H | 19 | 0 | 483 |
| Separate legacy total | **187** | **0** | **579622** |

All nine runners completed with exit 0, freshly built/executed into new external outputs. Original flags and expectations are unchanged. Their negative/environment simulations keep original classifications; no historical production XPASS/XFAIL is relabeled or claimed rerun by this preview-only assignment. Owner Mac E–H results are separately recorded as 166,140 reported assertions, not new cloud assertions. Native H's 365 and full Linux H's 483 scopes remain distinct. Mac E–G leak detection was disabled; Linux applicable leak checks are enabled. No new Mac rerun is requested or performed.

## Size, lifetime and scope findings

Fresh pinned preview OBJECT-ONLY checks pass and produce unchanged module hashes/type sizes compared with Stage28J. A separate metadata-only object measures Driver 34,032 B target / 34,128 B host. New record/intent/request arrays occupy 19,488 B; complete added storage beyond Program/CompileSession/Bridge is 19,668 B target / 19,720 B host. Bridge contains Runtime/Planner and CompileSession contains Compiler; no double counting. This is a deliberately bounded evidence harness, not production heap/headroom or a recommendation for a firmware journal. No new wrapper target runtime/stack measurements, firmware linkage, physical heap/latency/task high-water or OTA usage claim.

The source-intent counter association is feasible through unchanged public counters/phases. There is one explicit conservative boundary: when the next E ID/slot cannot be reserved, the wrapper can stop before a non-event tick because the next source event is not exposed. ID uniqueness is per Driver lifetime; rebuilding with retained callbacks is prohibited. Completion notices never generate receipts, even current matching ones; correlation remains unselected. Journal capacity failure can prevent drain/restart; no history is overwritten to recover. These constraints are documented for review, not disguised as full integration success.

## Integrity and publication

All **235 protected Stage26 files** match frozen Git content. All **1,030 preexisting Stage28J tracked files** remain byte-identical; old tracked modes/paths are checked too. Forty-seven original source spans are rechecked against actual repository and pinned dependency bytes. New files are restricted to `tests/stage28k/` and `docs/stage28k-*`; no code/core/SDK/toolchain installation or globally patched dependency. The immutable baseline was independently checked before work, not inferred only from a prior receipt.

The prepublication snapshot has **35 previous remote refs**. Final publication must add only the new Stage28K ref at exact delivered HEAD and prove every old ref unchanged. Receipt is deliberately precommit (no self-referential SHA); final exact head/clean-worktree/post-push confirmation is supplied at delivery and in an external receipt. No prior reports, owner approval cells, firmware branch or frozen artifacts were modified.

Added files only:

- Harness/checks: `tests/stage28k/journal_driver.h`, `journal_driver.cpp`, `test_journal.cpp`, `allocation_probe.cpp`, `object_layout.cpp`, `run_tests.py`, `verify_scope.py`.
- Documentation: `docs/stage28k-owner-approval.md`, `stage28k-contract-implementation.md`, `stage28k-test-report.md`, `stage28k-memory-ledger.md`, `stage28k-reproduction.md`, `stage28k-limitations-and-next-gates.md`.
- Receipts: `docs/stage28k-test-results.json`, `stage28k-legacy-results.json`, `stage28k-source-evidence.json`, `stage28k-target-build.json`, `stage28k-object-layout.json`, `stage28k-stage26-freeze.json`, `stage28k-static-audit.json`, `stage28k-source-hashes.json`, `stage28k-publication.json`.

Cloud environment already supports the work: no setup/configuration changes, installs, services or tool downloads were needed. Only Git integrity/publication uses network. No owner/private source, backups, NVS values or credentials were read. No real device, USB enumeration, actual HID endpoint, OS keystrokes, payload-launched file/network/shell action, firmware ELF/BIN/UF2, flash/boot/OTA or physical testing occurred.

## Review handoff

See `stage28k-contract-implementation.md` for actual counter/phase mechanics; `stage28k-memory-ledger.md` for measured cost; `stage28k-reproduction.md` for exact safe commands; `stage28k-limitations-and-next-gates.md` for unresolved transport/thread/profile/language requirements. Review the executed harness and conservative lifetime/capacity boundaries before any future proposal. Original stock availability remains owner-confirmed externally, not a development blocker.

**Synthetic-only GO for review. NO-GO for production/Stage26 integration, real HID/USB, firmware images, flash, boot, OTA or automatic Stage28L.** Stop and await owner review.
