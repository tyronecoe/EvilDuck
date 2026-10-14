# Stage28O test evidence and safe reproduction

46 primary PASS /0 unexpected FAIL /931 assertions. Each case is a fresh native process, not a real transport or language-compatibility pass.

| ID | Executed scenario | Assertions |
|---|---|---:|
| O01 | Full tagged ID1; receipt before/after retirement | 21 |
| O02 | ID0 eight-byte framing | 13 |
| O03 | Invalid instance/ID/null/stale C/oversize before claim | 19 |
| O04 | Lock contention and fake controller busy | 18 |
| O05 | Definite lower refusal, fresh Q retry | 16 |
| O06 | Early full completion before submit return | 11 |
| O07 | Early full callback plus contradictory NotSubmitted | 12 |
| O08 | 100 pending polls, one submission | 212 |
| O09 | Equal frames, distinct Q | 22 |
| O10 | Duplicate before retirement | 11 |
| O11 | Old completed Q while newer endpoint busy | 24 |
| O12 | Queued completion then reset/rebind | 22 |
| O13 | Queued completion then unplug/rebind | 22 |
| O14 | Protocol change invalidates binding | 10 |
| O15 | Wrong C/Q and tokenless event | 14 |
| O16 | Wrong endpoint without current busy clearing | 13 |
| O17 | Wrong instance/ID/protocol shape | 10 |
| O18 | Partial completion | 9 |
| O19 | Oversized completion | 9 |
| O20 | Stable observer snapshot under reentry | 20 |
| O21 | Cancel before submission | 4 |
| O22 | Cancel during controller call | 8 |
| O23 | Late success after pending cancellation | 9 |
| O24 | Retirement without success | 8 |
| O25 | Four-event queue plus fifth loss/sticky fault | 10 |
| O26 | Foreign raw/legacy shared-boundary lease refusal | 17 |
| O27 | Queued/in-progress/pending observer fence refusal | 22 |
| O28 | Lowered Q limit8 without wrap | 78 |
| O29 | Lowered C limit8 without wrap | 20 |
| O30 | Fresh neutral lifetime versus old equal zero | 26 |
| O31 | Ambiguous lower outcome quarantined | 10 |
| O32 | Single active capacity and immutable frame retention | 24 |
| O33 | Wrong retirement identity and first fault retention | 10 |
| O34 | Legacy pre-lease claim and explicit release | 14 |
| O35 | Failed current completion rejected | 8 |
| O36 | Missing fake observer fence denies reclaim | 12 |
| O37 | Queued early completion plus contradictory refusal | 8 |
| O38 | Reconnect does not retire/resume old lease | 22 |
| O39 | Failed unlock quarantines before controller | 9 |
| O40 | No reclaim during submission call | 15 |
| O41 | True UINT64_MAX boundary and old retirement | 18 |
| O42 | Post-fence current event invalidates fence | 17 |
| O43 | Cancellation then fresh neutral drain/lifetime | 20 |
| O44 | Deinit invalidates acceptance, not retirement | 13 |
| O45 | Cancel from admission lock before payload/claim | 6 |
| O46 | Reentry from admission lock cannot unbind/resubmit | 15 |

Separate unchanged baseline20/131 and disabled compatibility20/131. Two original reproductions, the O negative control and the inherited N baseline negative control each intentionally exit1, excluded from primary PASS/assertion totals. Three preparation static utility checks are counted separately. No historical wide-suite/Mac rerun. All46 primary cases have real dcd_event_handler/tud_task_ext/usbd_tagged_bind coverage; all except C-only O29 execute usbd_tagged_try. Cases with a tagged observer execute genuine hidd_xfer_cb/usbd_tagged_observe. O06 receipt order precedes fake controller submit return. Legacy disabled observations match all original data fields. FIFO support compiles without positive FIFO-function coverage.

GCC/gcov14.2.0; C11/O1/-g/-Wall/-Wextra/-Werror, inherited -Wno-misleading-indentation, ASan+UBSan/frame pointers/non-PIE/gcov. ASAN_OPTIONS=detect_leaks=1; UBSAN_OPTIONS=halt_on_error=1. Compiler/config/source/patch hashes, commands and per-case function/line counts are recorded. Fake capacities and serialized reentry do not measure FreeRTOS locks, physical resource use or transport latency.

The primary source corpus is independently exact-hash checked before build. Opt-in disabled compiles the same modified source tree with0 and unchanged Stage28N fixtures, not a handwritten compatibility model. Deliberate negative control checks runner rejection; intended original failures are stale-busy clear and oversize-refusal retained claim. Preparation checks verify fresh exact application, existing-output rejection unchanged, and wrong input hash rejection before output.

## Reproduction: host/native only

Run from repository root using existing GCC/gcov/Python/patch; fresh external paths are required. No installation, target compiler, firmware link, USB enumeration or owner files.

```sh
python3 tests/stage28n/prepare_sources.py --output-dir /tmp/evilduck28o-original-new
python3 tests/stage28n/run_tests.py --source-root /tmp/evilduck28o-original-new --build-dir /tmp/evilduck28o-baseline-new --results /tmp/evilduck28o-baseline-new.json
python3 tests/stage28o/prepare_sources.py --original /tmp/evilduck28o-original-new --output /tmp/evilduck28o-prototype-new
python3 tests/stage28o/run_tests.py --source-root /tmp/evilduck28o-prototype-new --original-root /tmp/evilduck28o-original-new --build-dir /tmp/evilduck28o-native-new --results /tmp/evilduck28o-results-new.json --baseline-results /tmp/evilduck28o-baseline-new.json
python3 tests/stage28o/test_preparation.py --original /tmp/evilduck28o-original-new --scratch /tmp/evilduck28o-preparation-new
python3 tests/stage28o/verify_scope.py --original /tmp/evilduck28o-original-new --prototype /tmp/evilduck28o-prototype-new --output /tmp/evilduck28o-scope-new.json
python3 tests/stage28h/verify_freeze.py
```

Original preparation reads only pinned official full-revision public URLs; exact SHA rejection before use. Native transformation checks all21 inputs, patch digest and four expected outputs; patch --fuzz=0 rejects unexpected hunk/offset. All sources are scratch copies; no deployment script exists. Scope may additionally check the unchanged protected core/package with read-only optional paths. No installed toolchain change or environment configuration was needed.
