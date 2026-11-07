# Standalone REPEAT v1 — local implementation and offline results

**SOURCE IMPLEMENTED — TARGET FIRMWARE UNBUILT — UNFLASHED.**

Branch: `routeb-previous-command-repeat-v1`. HEAD remains
`fcba0385ce21662c7a504e0c9b6fba0dfa2c4f8d`; changes are local and uncommitted.
The required starting HEAD and clean worktree were checked before creating the
branch. No commit, push, target build, installer, package, hardware access, real
HID output, flashing or OTA occurred.

The compiler-only fix admits a preceding eligible leaf followed by literal
`REPEAT 1` through `REPEAT 128`, meaning that many **additional** executions.
Existing inline REPEAT remains **2–128 total** executions. Both consume the same
128-instruction budget. [Exact grammar, policies, owner evidence and later
acceptance sheet](previous-command-repeat-design.md) document the bounded subset;
this is not blanket Hak5 DS3 certification.

## Root cause and source boundary

The complete static-response parent uses an inline-only parser. Its missing-body
check rejects standalone `REPEAT 3` with Syntax/code 15 at physical line 4 of the
supplied Request 11 fixture. Whole-source compilation precedes execution, so
TextEdit remains blank. The old-core causal control freshly reproduced that
exact diagnostic. The new core accepts the four-x fixture while retaining
three-x inline semantics and consecutive inline forms.

The hash-pinned [source patch](../tests/previous_command_repeat/application.patch)
changes only composed `core.cpp`. **200 of 201 source files remain identical**.
The normal source entry applies the delta after the entire H1/right-modifier,
lock-wait, privacy, editor, dashboard and static-response composition. Its
201-file final inventory and omission/tamper controls pass.

| Core | SHA-256 |
|---|---|
| Exact parent | `2876056adb42347f53ff8efdcf9cdbbce8ca04db4dc670bd1c4fdb2dc49befa5` |
| New compiler | `01fda98ee58d34cd523241cfdd1da37b6992e037b889ce964ce3e32c899b0c4b` |

The shared inline whitelist was extracted without widening it. One compiler
index selects an immutable preceding leaf; existing cooperative shared-operand
cloning performs the expansion. Copies use REPEAT's physical line for errors.
No opcode, runtime history, HID backend or storage interface is added. The
Program/runtime tail of `core.cpp` remains byte-identical, as do `core.h` and all
backend/adapter/authentication/web resources.

## Fresh verification

All results below were newly executed against the new composition or exact
old/new causal source controls. Historical receipts are not substituted for
fresh passes. Native tests use RAM-only transport, storage/NVS, clocks and random
inputs. Browser checks use intercepted inert requests in Linux Chromium, not a
physical High Sierra/iPhone browser.

| Group | PASS | FAIL | Assertions/checks |
|---|---:|---:|---:|
| New standalone/inline REPEAT cases | 50 | 0 | 2,739 assertions |
| Privacy native cases | 28 | 0 | 736 assertions |
| Existing composed keyboard/H1/lock/preprocessing/EDR1 regressions | 558 | 0 | 23,901 assertions |
| Static-response native | 33 | 0 | 976 assertions |
| Streamed-resource browser | 3 | 0 | 26 assertions |
| Dashboard browser | 9 | 0 | 207 assertions |
| Editor browser | 41 | 0 | 309 assertions |
| Source composition/normal-entry controls | 9 | 0 | 47 assertions |
| Separate old/new compiler causal controls | 2 | 0 | 8 checks |
| Inherited core edge probe | 1 | 0 | 2 checks |
| Required-profile refusal controls | 12 | 0 | 12 expected rejections |

Distinct composed native total: **636 PASS, zero FAIL, 27,376 assertions**.
Web/component total: **86 PASS, zero FAIL, 1,518 assertions**. The native wrapper
also executed the identical nine dashboard browser groups; they are not counted
again as unique groups. Expected negative-control compiler exits are refusals,
not test failures.

Native ASan, UBSan and leak checks passed, with empty final runtime stderr.
Compilation of native mock executables is distinct from a target firmware build.

The broad successful run executed PR01–46 and all 586 inherited cases. Four
additional cases then closed specific gaps without repeating the broad suite:
nested function/WHILE/IF repetition, ELSE IF boundary handling, once-only function
operand evaluation through retries, and continued rejection of inline INJECT_VAR.
The focused receipt proves that all first 46 case bodies remain byte-identical
to the frozen successful driver. The maintained runner now selects all 50 plus
the inherited cases for future reproduction.

Representative exact terminal output:

```text
DIAGNOSTIC old Request11 line=4 code=15
DIAGNOSTIC line=1 code=14 message=Recognized feature not supported in this preview
DIAGNOSTIC line=1 code=15 message=Malformed statement or expression
DIAGNOSTIC line=2 code=4 message=Instruction limit exceeded
```

Physical-line checks also cover CRLF, missing final newline, BOM input, barriers,
retained inactive source and a sampling error in a copied operation. Tests cover
the exact limit, every eligible leaf category, all fourteen aliases, DEFINE,
release reports, held right Shift, dwell/jitter, cached retries, STOP during
compile/delay/pending delivery, disconnect/quarantine, restart and new requests.

### Preserved development failures

An initial new-runner hook assertion occurred before compilation or test
execution; only adapter composition order was corrected. The first native
attempt then recorded **630 PASS and two new-test failures**. Both were test
oracle errors, independently reviewed:

- PR33 measured STOP after the no-replay observer deliberately advanced 1,000
  ticks. The strict `<500 ms` measurement now occurs before that observer;
  cancelled status, ownership release, held-state clearing and no-replay checks
  remain.
- PR46 incorrectly expected code 14 for the unrelated unsupported REPLAY command.
  Its unchanged baseline diagnostic is UnknownStatement/code 13. The function-call
  predecessor barrier still requires code 14.

No production patch changes were needed. The failed receipt is preserved at
`/workspace/scratch/previous-command-repeat/native-v1.json`; setup and correction
details are retained in the successful native receipt and results summary.

## Evidence, resource measurements and changed files

[Results and exact source/input inventory](previous-command-repeat-results.json)
bind the raw receipts and all 201 final source hashes:

| Receipt | SHA-256 |
|---|---|
| `/workspace/scratch/previous-command-repeat/native-v2.json` | `7d9e77d004335a6e6b50be99612698058291d33f14beae1ca8bda28ef5d76b24` |
| `/workspace/scratch/previous-command-repeat/focused-v1.json` | `721f7e1c42e5122086c84e56e9428dfff29ac25f66cb5410f2626d58aea1f296` |
| `/workspace/scratch/previous-command-repeat/web-v1.json` | `d27ec20d835c11750087a0edab61d7c5a2a4f8e85e8d4e7ca1b3ac2259408a82` |

Host old/new measurements are identical: compiler **3,856 bytes** within its
4,096-byte workspace, Program **6,936**, Runtime **4,952**. The index fits existing
padding on this host. These are not ESP32 flash/static-RAM measurements; target
resource changes remain unmeasured.

One existing tracked path changes: `tools/build_routeb_candidate.py`. All other
**2,489 tracked historical paths** remain unchanged. Eight new implementation/test
files are under `tests/previous_command_repeat/`:

- `application.patch`, `source-manifest.json`, `prepare_sources.py`
- `build_candidate.py`, `test_main.cpp`, `run_tests.py`
- `test_scope.py`, `test_web_regressions.py`

Three new documents are this report, `previous-command-repeat-design.md` and
`previous-command-repeat-results.json`. No historical overlay, test, evidence,
published package or recovery image was edited.

## Explicit build boundary and next stage

The normal entry now selects the new source overlay in `--compose-only` mode.
Target builds **fail closed**: inherited release verifiers pin the old core and
must not silently accept a changed compiler or emit the old image without this
fix. Source tests exercise the real entry and refusal controls without invoking
any target compiler. Fresh composition uses the exact verified full parent;
raw target-scaffold reconstruction and the target release chain remain deferred.

This is the implementation-stage boundary, not a claim of build/package
readiness. A separately authorized next stage should integrate the new compiler
inventory into the complete release-verifier chain, preserve all inherited
guards, assign a unique build identity, clean-build using the approved isolated
Arduino ESP32 3.3.0 profile, measure resources and prepare a verified High Sierra
review ZIP. Installation and the short acceptance sheet remain separate
owner-operated steps.

Mandatory rollback was freshly verified unchanged: **1,413,200 bytes**, SHA-256
`cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02`.
The prior static-response application still hashes to
`d5fe0932fe915443a5e53030969c6792409f719d427681304a7102355b2d7946`.
Neither image was rebuilt, modified or published in this stage.

H1 remains opt-in/experimental with unresolved canonical Hak5 numeric encoding.
Previously accepted owner milestones remain scoped observations; no repeated
hardware test, broad Caps investigation or new physical success is claimed.
