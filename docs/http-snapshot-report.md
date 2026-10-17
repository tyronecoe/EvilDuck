# HTTP execution-busy investigation and reviewed candidate

**Software verification: PASS. Physical installation/testing: NOT AUTHORIZED or performed.**
The original immediate-fail contention mechanism is reproduced. A bounded correction
passes focused regressions and a clean, independently checked ESP32-S3 link. This
does not establish that the owner's observed physical collisions have disappeared.

## Baseline and cause

Installed source named by the owner: `5c19f0dacb25960bda36a97f4ff871937a3cc9e7`.
Repository starting point: package commit `fb1c43c5de28cc9887368f9bd016be0b3fd04763`.
New branch: `routeb-http-snapshot-contention`. Original X, shortcut sources, their
packages and builders remain unchanged. The new isolated builder composes their
exact pinned sources and then applies `tests/http_snapshot/contention.patch`.
It is not a build of the frozen Stage26 tree alone.

The two old endpoints try the shared execution mutex with zero wait. Idle
`duckscript::update`, `com::update` and diagnostic backend reads still acquire it.
Closing browsers does not remove these owners. Other synchronous services can hold
it longer. The CLI does not hold it throughout idle serial polling. Original JSON
formatting and response submission also extended the locked regions. HTTP STOP's
standalone authentication could misleadingly report401 on lock contention.

[Detailed ownership and synchronization analysis](http-snapshot-analysis.md) and
[actual composed source hashes/line anchors](http-snapshot-source-evidence.json)
trace these paths. Source/native evidence explains a mechanism, not the exact
physical holder behind the owner's ten successes/two busy responses. Advancing
ticks and the owner's separate63-second idle/three-fixture successes do not prove
a lock leak, deadlock or physical timing guarantee. No such attribution is made.

## Exact implementation

Seven composed files change, pinned before/after in the [source manifest](http-snapshot-source-manifest.json):

- `execution_guard.h`: named outermost ownership and fixed telemetry; new bounded
  HTTP guard tries immediately, then waits once for5ms rounded up to RTOS ticks.
  This pinned1000Hz SDK means five ticks. Existing Guard/TryGuard policies remain.
- `duckscript.cpp`, `com.cpp`: label their existing outer update guards.
- `webserver.cpp`: bounded snapshot/STOP-auth acquisition; live auth and owned state
  copies under synchronization; JSON formatting, responses and authenticated
  Route B STOP publication outside the capture lock. Persistent contention still
  returns409. Invalid credentials still return401; failed STOP admission is not
  falsely acknowledged. Existing Route B single-owner and priority STOP remain.
- `diagnostics.h/.cpp`: copy a coherent published structure, format outside locks;
  explicit capture/observation/resource timestamps and age, completed-turn count.
  Backend sampling guard is separately labeled and narrowly scoped.
- `cli.cpp`: diagnostic record buffer1024→1536 for the expanded bounded schema.

A single copied Route B status drives running/phase/reason/script/line/error,
including a tested concurrent completion immediately after capture. Settings and
legacy state remain execution-locked. JSON string escaping handles quotes,
backslashes and control bytes. There is no cached fallback, removed mutex,
authentication bypass, retry loop, new worker task or new script syntax.

Five ticks limits the mutex wait, not wall-clock HTTP latency or capture duration.
Long owner work, scheduling, allocations and network backpressure remain possible.
The fields `executionContentions`, `executionTimeouts`, `lastContendedOwner` and
`maxExecutionHoldUs` are independent observations, with saturating counters.
Owner classes/recursion/race and clock-wrap limitations are documented in the
analysis. Statistics use a separate tiny static critical section; no SDK call,
allocation or execution wait occurs inside it. Existing String capture/response
allocation remains. No claim of allocation-free HTTP or physical latency is made.

`/status` says `snapshotKind=request-capture`; it is not a guarantee that the
response is still current on arrival. `/routeb/diagnostics` says
`published-observation` with `observationKnown` and ages: owner-phase/backend are
last completed-turn evidence, resource fields are last sampled evidence, and
admission/STOP/tick counters can be newer. This preserves coherent published
copies without representing asynchronous fields as simultaneous hardware state.

## Fresh executed verification

Exact commands, per-case stdout/stderr, assertion counts and exclusions are in
[results](http-snapshot-results.json) and [reproduction](http-snapshot-reproduction.md).

| Executed suite | PASS | Unexpected FAIL | Assertions |
|---|---:|---:|---:|
| New H01–H18 + unchanged K01–K25 and W01–W33 | 76 | 0 | 2,682 |
| Related unchanged T cases46 + X cases17 | 63 | 0 | 2,650 |
| Total positive regression cases | **139** | **0** | **5,332** |

ASan/UBSan and leak detection are enabled and clean for these completed C++ cases.
These are relevant composed production regressions, not a claim to rerun every
historical stage. No historical XPASS/XFAIL classification is changed. The whitespace checker reports
only11 mandatory blank-context spaces inside the pinned unified patch; no source
line trailing whitespace was introduced.

Coverage: short and prolonged contention on both endpoints,401 handling, exact
409 preservation, response submission outside execution lock, STOP retry and
cancellation without output, idle and running progress, exact mock reports,
single-owner execution, age/wrap arithmetic, bounded numeric formatting, JSON
escaping and forced status-publication races. Existing keyboard, controlled
startup/services, backend ownership/USB and diagnostic regressions run unchanged.
T34's Linux-thread identity fixture is not run with this RTOS-identity composition
(K25 covers the latter). X13/X15 assume the former1024-byte diagnostic schema;
H15 explicitly checks the new1536-byte bound/truncation. W34's former false401
STOP-auth contention expectation is superseded by H09/H10/H18, not relabeled PASS.

Negative evidence is separate:

- A disposable copy reverting only the bounded guard to zero-wait reproduces real
  handler H01's409 instead of200 (expected exit1, three assertions at rejection).
- Two disposable ELF symbol negative controls demonstrate that the original
  settings-ready and NVS-call predicates still reject missing evidence. They are
  verifier controls, not additional language/HTTP passing cases.

Development failures were corrected, not classified as environment skips: early
native harness overlay/include integration failed closed; intermediate H13/H14
clock fixtures had an extra helper tick and H16's newline SSID was correctly
rejected by existing settings validation. Final fixtures exercise valid inputs.
An initial target lock-free-atomic assumption failed its assertion and was replaced
with explicit short critical sections, not a weaker assertion or dependency patch.

## Clean build and linked provenance

The clean Arduino compile succeeded. Initial post-build verification exposed
Xtensa disassembly alignment/property metadata issues, not missing startup safety
calls. `startup_decode.py` pins the original verifier SHA and changes only its two
disassembly inputs: bounded reachable setup decoding and a disposable NVS
inspection copy stripped of non-loadable Xtensa property metadata. Allocated
section bytes/addresses/flags and symbols must match the original ELF. All original
safety predicates remain intact. The ELF itself is never rewritten.

Verification resumed against the existing successful clean compile rather than
unnecessarily rebuilding it. Expanded build properties match except the two
Arduino time properties; the stored original properties are retained. Actual
source/compile flags, ELF-to-BIN regeneration, startup profile, checked settings,
no format/examples/autorun, Stage16 HID and Stage18 NVS protection are verified.
Two negative controls also pass the ELF-to-image check before reaching and failing
their intended safety predicate. A first control correctly failed earlier because
ELF SHA embedded in the application changed; controls now regenerate their own
disposable images and hashes rather than bypassing that check.

[Full build/link receipt](http-snapshot-build.json):280 linked inputs, three link
response files,13 scripts;177 SDK archives identical to the prior verified SDK.
Host-only test hooks are absent from the target ELF; actual linked recursive-mutex
arguments are verified as immediate0 and one5-tick wait, after releasing the
telemetry critical section. Bounded guard/telemetry are
linked. Arduino3.3.0, ESP-IDF5.5 package `b66b5448-v1`, pinned Xtensa14.2.0,
16MiB, PSRAM disabled,240MHz, existing USB-OTG/TinyUSB/CDC and partitions unchanged.
No global dependency source or installed toolchain was modified.

| Resource | Shortcut baseline | HTTP candidate | Change |
|---|---:|---:|---:|
| Compiler program bytes | 1,359,659 | 1,366,703 | +7,044 |
| Application BIN bytes | 1,359,808 | 1,366,848 | +7,040 |
| Static RAM bytes | 106,264 | 106,328 | +64 |
| Free bytes per0x740000 OTA slot | 6,242,368 | 6,235,328 | −7,040 |
| Free percentage per OTA slot | 82.112911% | 82.020306% | −0.092605pp |

Compiler frame estimates: status144→368B, diagnostics1088→1888B, CLI parse1216→1728B,
STOP64B unchanged, loop32B unchanged. Diagnostic owner endTurn240→224B.
These are per-function compile estimates, not aggregate stack depth or high-water.
AsyncTCP's pinned default task stack is16384B; loop allocation remains8192B.
Increased local diagnostic buffers deserve separate physical stack observation.
Fixed telemetry adds no additional RTOS mutex; dynamic String work is not eliminated.
No hardware heap, stack, HTTP409 rate or latency was measured.

Review-only application: [evilduck-http-snapshot-review.bin](../downloads/evilduck-http-snapshot-review.bin)

- Bytes:1,366,848
- SHA-256:`706d215f5cc8e7c318bd7677dc3758c1fd95603061d71ada1dbe440e450c2d4b`
- ELF SHA-256:`173a1da746bfa3ed71f722833b1ef86817e2ea4b57497b5dcb717beeb0551537`
- Original verifier SHA-256:`d8b1ea90ea3528ecc0f6639f6d5b6c8d22dccf763532fb05726a2d45d96a00ac`
- New decoder/adapter SHA-256:`41a7ff490b3cb62feae5c85749685f82d5b0055ff961abbeb3732241b3a33cf8`

This application is not an approved installation package. Do not substitute it into
the existing shortcut package's pinned preflight. Existing bootloader/table hashes,
partition geometry, NVS/filesystem safeguards and USB identity remain unchanged;
no merged migration image is used or published.

## Preservation and next review

[Integrity receipt](http-snapshot-integrity.json) checks every historical Git file
byte/mode,235 frozen Stage26 files and both original public ZIPs. Publication
receipt separately records previous remote refs before/after the new branch push.
No previous branch/tag is rewritten. No owner files/configuration/backups are read
or modified. The installed working shortcut package remains available unchanged.

**GO:** review this isolated source delta, evidence and review-only build.
**PENDING:** separately authorized owner observation of idle/progress/STOP and
remaining contention with the new timestamps/owner counters. The earlier physical
results apply only to the installed previous candidate. No automatic retry/replay,
stored payload execution, change to defaults or new stage is authorized here.
**NO-GO:** flashing/installation as part of this investigation. No hardware access,
real HID, OTA, formatting or physical write occurred.

## Complete added-file inventory

- `docs/http-snapshot-analysis.md`
- `docs/http-snapshot-build.json`
- `docs/http-snapshot-integrity.json`
- `docs/http-snapshot-report.md`
- `docs/http-snapshot-reproduction.md`
- `docs/http-snapshot-results.json`
- `docs/http-snapshot-source-evidence.json`
- `docs/http-snapshot-source-manifest.json`
- `downloads/evilduck-http-snapshot-review.bin`
- `tests/http_snapshot/build_candidate.py`
- `tests/http_snapshot/contention.patch`
- `tests/http_snapshot/execution_guard.h`
- `tests/http_snapshot/mocks/ESPAsyncWebServer.h`
- `tests/http_snapshot/mocks/Update.h`
- `tests/http_snapshot/mocks/WiFi.h`
- `tests/http_snapshot/mocks/network.h`
- `tests/http_snapshot/prepare_sources.py`
- `tests/http_snapshot/run_negative.py`
- `tests/http_snapshot/run_related.py`
- `tests/http_snapshot/run_tests.py`
- `tests/http_snapshot/startup_decode.py`
- `tests/http_snapshot/test_main.cpp`
- `tests/http_snapshot/test_verifier_controls.py`
- `tests/http_snapshot/verify_link.py`
