# Bounded lock waits — implementation and review report

Candidate **ROUTEB-LOCK-WAIT-TIMEOUT-v1** implements configurable cooperative waits as an **EvilDuck extension**, not canonical Hak5 syntax or a remedy for host LED delivery. Offline verification is **PASS**; physical candidate acceptance is **UNVERIFIED**. Implementation/build/package publication is authorized; installation, hardware access, HID execution, flashing and OTA are not.

## Baseline, implementation and preserved behavior

The isolated `routeb-lock-wait-timeout-v1` branch starts at reviewed closeout `993a915bb932bfe50b4e18ea3dedb0a504caaab3`. A remote-ref check found no later relevant release. The accepted installed firmware remains source/text v2:1,413,200bytes / `cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02`. Its four owner-reported High Sierra passes, unknown identifiers and Control+J/port observations remain in [the unchanged closeout](source-text-v2-acceptance-closeout.md). Private backups were not accessed. No new physical evidence is invented.

```ducky
$_EVILDUCK_LOCK_TIMEOUT = 10000
WAIT_FOR_CAPS_ON
```

Read/write1–65535ms, default5000. Existing checked expressions and continuations support reads/assignments without duplicate evaluation. Statically known invalid retained values reject before output, including inactive branches/unused functions; excluded preprocessing remains distinct. Dynamic zero fails at its assignment before accepting the setting or beginning the following wait. Each event captures a timeout once; the adapter requires immutable selector/timeout and preserves its first-entry start time. Expiry is wrap-safe elapsed>=timeout and wins over matching evidence at the boundary. New Start/restart reset the setting, RESET preserves it; cumulative run budgets survive restart. [Detailed contract](lock-wait-timeout-design.md), [compatibility](lock-wait-timeout-compatibility.md).

Five generated source files change: core.cpp/core.h, adapter.cpp/adapter.h and caps_trial.h. Exact hashes/parent pin/patch identity are in [source manifest](../tests/lock_wait_timeout/source-manifest.json); [preparation](../tests/lock_wait_timeout/prepare_sources.py) touches disposable sources only. New enum values are unnecessary: operand/setting IDs and one defaulted in-process Event field are appended. No USB/HTTP wire format, SDK ABI, settings schema, NVS, filesystem or dependency is changed. There is no new allocation buffer, interpreter or Program/source copy. Source equality and actual linked implementation paths are mandatory.

Five-second evidence freshness is independent of the chosen wait duration. Every attempt checks fresh current evidence before CHANGE baseline acquisition or success comparison. Existing baselines survive stale intervals; current fresh evidence plus an advanced same-bit counter can satisfy CHANGE, including away/back transitions. This is not a new timestamp guarantee for individual transitions. Fresh ON/OFF reports after5s can also satisfy a longer wait; stale reports never fabricate OFF. The35newtests demonstrate this distinction with separate clocks. Request/lease ownership, STOP, cleanup, quarantine, all accepted grammar, USB identity, PSRAM policy, authentication and EDR1 remain intact. INJECT_VAR stays blocked; SAVE/RESTORE and new layouts remain deferred.

## Fresh verification

| Executed verification | PASS | Unexpected FAIL | Assertions / boundary |
|---|---:|---:|---|
| New AB01–AB35 composed timeout cases |35|0|352 assertions |
| Existing selected candidate-adapted regressions |457|0|17,612 assertions |
| Total native-v3 |492|0|17,964 assertions; ASan/UBSan/leak clean |
| Read-only observer mocks |24|0|No device or real network |

[Native receipt](lock-wait-timeout-test-results.json), [observer receipt](lock-wait-timeout-observer-tests.json), [build/post-link evidence](lock-wait-timeout-build.json), [reproduction](lock-wait-timeout-reproduction.md). The earlier457-case receipt is not merely reused: those cases were freshly executed on the candidate with the existing adaptations retained. The new generated-only D12 identity-prefix adaptation is recorded explicitly; historical files/expectations remain unchanged. Historical XPASS/XFAIL, risk observations and V14 provenance correction are preserved, not reclassified or counted as new executions of unrelated suites.

Coverage includes all nine waits, defaults/endpoints/invalid values, expressions and suspended functions, bounded RNG sampling/cached retries, after-five-second fresh success versus stale evidence, exact expiry, independent evidence-clock freshness and wait-clock wrap, budgets, event mutations, two settings, Start/restart/RESET lifetimes, held Shift, STOP before/during wait, disconnects, cleanup pressure/quarantine and subsequent runs. Exact mock reports show the setting creates no lock-key actions. Native-only `-fno-access-control` exercises actual private pending-event state without adding production hooks. No such flag reaches firmware.

Development findings are preserved: exploratory source-object compilation initially omitted an inherited shortcut selector and correctly hit its guard; corrected selectors compiled. Native-v1 stopped on an unused test parameter under unchanged -Werror. Native-v2's sole D12 failure expected the historical generic build prefix; a generated-copy identity correction fixed it. Native-v3 above is the final complete run; earlier results are not combined with it. Repetitive tick invariance is aggregated, not reported as100,000 separate assertions.

## Clean build and resources

Approved isolated Arduino ESP32 **3.3.0**, ESP32-S3,16MiB custom partitions, PSRAM disabled, unchanged USB-OTG/TinyUSB/CDC and CPU/flash configuration. All **177** SDK archive identities and existing HID/NVS/startup/dependency guards pass. The final verifier requires new profile flags, exact five-file delta and source/compiled equality; disassembly binds compiler/runtime/adapter wait dispatch and preserves inherited clear/rewind/ownership paths. ELF-to-BIN regeneration and table constraints remain mandatory.

| Measurement | Accepted v2 | Candidate | Change |
|---|---:|---:|---:|
| Compiler program bytes |1,413,055|1,413,375|+320|
| Application BIN bytes |1,413,200|1,413,520|+320|
| Static RAM bytes |113,888|113,896|+8|
| OTA slot bytes |7,602,176|7,602,176|0|
| Free bytes per slot |6,188,976|6,188,656|−320|

Application SHA256: `319df438aa4fb7cabec4247f9fcb2b666de27213cbd1611d8041b55cf5aa129f`.

ELF SHA256: `5ae7e7ff7ada8e385c6b98117191cb190eb2991499739d65e455eb3f615582dc`.

Table SHA256: `b79bde9ef4a9544411d97a31a1d326b2028213269ad0dcc643ea921230ce3d5e` (unchanged).

Compiler frame estimates: Compiler::expr changes112→144bytes (+32) with its new validation parameter; statement368, Adapter::wait96, Runtime::evaluationStep144, Runtime::tick112, Adapter::step144 and coordinator tick384 remain unchanged. These are compiler frames, not measured task-stack/heap/high-water or latency. [Full resource/provenance comparison](lock-wait-timeout-resources.json). Build-wrapper provenance fields and an explicit parent-source pin assertion were finalized after clean compilation; production sources/options remained unchanged, and final post-link verification independently rechecked compiled identity. No weakened predicate or silently substituted SDK is involved.

## Package, owner check and limitations

One distinct Mac app-only review ZIP includes the candidate plus exact accepted v2 application rollback, reused from published bytes. The v2 ZIP and its older included restart rollback remain unchanged. Existing app-only region, chip/security/image/table/OTA checks remain fail closed. No installation, formatting, automatic repair or automatic payload execution is authorized. [Install review](lock-wait-timeout-install.md), [rollback](lock-wait-timeout-rollback.md), [three-trial acceptance sheet](lock-wait-timeout-acceptance.md).

The bound `observe_wait.py` is Python3.8 stdlib, GET-only, authenticates with a private header prompt, checks candidate build identity, preflights idle state, requires the actual assigned request and logs whitelisted status fields. Prepare it before Start. It cannot start/STOP a script or emit LED/HID actions. HTTP errors stop observation; no failed-request replay, stale-current substitution or automatic acceptance. The2s timeout is socket inactivity, not a hard total-response deadline; a slow peer can exceed the polling window. Late responses cannot establish waiting evidence. Ctrl+C ends observation but does not STOP firmware.

A passive timeout is an expected policy outcome, distinct from whole-run budget, disconnect or cleanup failure. STOP requires correlated routeBWaiting/request evidence, not an invented UI label. Missing correlation/competing transition is inconclusive; no broad Caps investigation or Windows prerequisite is introduced. Longer waits do not prove host-global locks, actual USB delivery or endpoint retirement.

Package size/hash, source/artifact commits, package/mock-installer checks and the commit-pinned download are recorded in the subsequent [artifact receipt](lock-wait-timeout-artifact.json) and [publication receipt](lock-wait-timeout-publication.json). This report is included in the ZIP as its source-commit snapshot; later publication receipts supplement it without regenerating the archive. [Historical preservation check](lock-wait-timeout-preservation.json).

**GO: review the software candidate and plan separately authorized acceptance. Physical candidate behavior remains UNVERIFIED; installation, hardware access, real HID, flashing and OTA remain unauthorized.**
