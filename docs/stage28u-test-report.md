# Stage28U executed verification and reproduction

| Category | PASS | Unexpected FAIL | Assertions |
| --- | ---: | ---: | ---: |
| Final U01–U64 primary | 64 | 0 | 515 |
| Unchanged Stage28T, executed once separately | 47 | 0 | 467 |
| Affected production scheduler/ownership/dispatch regressions | 77 | 0 | 67,371 |
| Final selector-disabled exact comparison, same77 cases | 77 | 0 | 67,371 |
| Existing controlled startup/settings/storage regressions | 30 | 0 | 635 |

Seven preparation controls pass separately. Fourteen actual target source/
metadata units compile successfully, with zero failed object checks. These are
not runtime cases. No SKIP_ENVIRONMENT or unperformed hardware PASS is claimed.
Primary and affected regressions use ASan/UBSan and leak detection. The deliberate
U03 negative assertion exits1; T's negative assertion is retained separately.
Historical language XPASS, upstream USB XFAIL and model/watchdog observations are
unchanged, not rerun or reclassified. No generic controller model or Mac rerun.

## Genuine coverage

- U01–U05: explicit owner/mode, legacy default, real aa/ab report vectors and
  preview functions/loops through actual file/dispatch/com/backend/Runtime.
- U06–U17: exact cap/oversize/empty, partial reads, pre-read Retry, open/seek/EOF,
  growth/equal-size mutation, malformed and inactive unsupported source.
- U18–U29: STOP during queued/capture/compile/verify/run/clear, ambiguity and
  disconnect quarantine, foreign task/reentry, saturated queue priority flags.
- U30–U43: existing transaction exclusion, copied token lifetime/stale completion,
  actual CLI busy/STOP, existing legacy/held/raw/clearing rejection, exhaustion,
  first deadline and fresh reader lifecycle.
- U44–U55: actual mode/layout guards, in-run saturated queue loss, Retry budget,
  retained clear quarantine, restored setters, copied caller path, host contention,
  clock wrap, queued start after old terminal, runtime source line, deferred chunk
  abort and zero-wait service admission.
- U56–U61: exact storage volume without fallback, mocked SD bytes through the
  same capture code, existing diagnostic accessors, default CLI legacy dispatch,
  full idle queue draining and CLI conflict with an active service transaction.
- U62–U64: existing MSC requested/active/preparing states reject capture and
  service admission. Actual attackmode state/getters execute over mocked media.

Coordinator and FileSource reach100% executable-line coverage in the final native
run; dense lines and incomplete branches mean this is not all-path proof.
Actual scheduler44.72%, backend34.74% and preview76.53% line coverage demonstrate
those modules executed. Function/branch summaries are in coverage JSON. Actual
native storage API implementations, USB/Keyboard/MSC/clock and task primitives
are explicit lower mocks. Web handlers/storage writers/loop are object-compiled,
not native-executed in enabled mode. Startup regressions execute their unchanged
production-source harness with the selector off, not native full SDK boot.

## Development findings retained honestly

An initial missing FS include and missing lower SD stub caused compile/link
errors. A regression output filename collided with its source directory; the
helper was corrected before the successful comparison. Target Werror found
uninitialized upstream Stream state copied by unnecessary `file_=File()`;
pinned FS::File::close already releases its pointer, so the redundant assignment
was removed without changing warning flags. Source review added regressions for
queued starts after old terminal state, idle-queue draining, priority polling
before source ticks and deferred retirement of an in-flight transaction chunk.
Runtime and status accessors now retain the proper selected-engine diagnostic.

Some development runs completed all cases but their final fixture guard rejected
concurrent additions/edits to test helpers. They are not final acceptance results.
The final64-case run binds a stable complete fixture snapshot, including both
native executables and the intentional negative control. Earlier passing runs
and default-off rebuilds are superseded, never added to totals.

## Safe reproduction

Use a disconnected development host and fresh external directories. Existing
tools suffice; do not install or patch a global compiler/core. Versions and exact
native commands are in native-results JSON. Warning policy remains
`-Wall -Wextra -Werror -Wno-misleading-indentation`.

```sh
python3 tests/stage28u/run_tests.py --build-dir /tmp/evilduck-u-native --results /tmp/evilduck-u-native.json
python3 tests/stage28u/run_regressions.py --build-dir /tmp/evilduck-u-regressions --results /tmp/evilduck-u-regressions.json
python3 tests/stage28u/check_preparation.py
python3 tests/stage28h/verify_freeze.py
python3 tests/stage28u/verify_scope.py --output /tmp/evilduck-u-scope.json
```

Target compile-only (requires the existing verified build receipt/tool paths;
no install, archive rebuild, linker or firmware output):

```sh
python3 tests/stage28u/target_check.py --baseline-build /workspace/tooling/arduino/build/stage26-final-controlled --output-dir /tmp/evilduck-u-target
```

The tool checks pinned core/SDK/compiler identities before compiling actual
candidate modules with real Arduino/FreeRTOS headers. It emits relocatable `.o`,
dependency/stack text and layout `.raw` only. Undefined platform references are
recorded. It cannot prove a final link or actual startup. Do not point preparation
or output paths at an installed toolchain or protected source directory.

The unchanged Stage28T and controlled-startup runner commands are in their
embedded receipts. The final disabled binary was compared to the already freshly
executed original77 receipt after final dispatch additions, avoiding another
unchanged-original run. Full primary traces, counts, commands, allocation data,
input hashes and receipt digests are machine-readable; no private owner files
are required.
