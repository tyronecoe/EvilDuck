# Route B transient keyboard shortcuts — implementation report

Prepared October 17, 2026 UTC. Baseline branch `compatibility-boundaries-and-engine-docs`,
commit `6280b1d7b465f5d29800fa230ab60f3b04bf77c4`; new branch
`routeb-transient-keyboard-shortcuts`. Scope follows the owner's supplied
October 16 compatibility audit and first implementation brief.

**Software GO for review. Hardware installation and trials require separate owner
authorization.** No device access, HID output, flashing, OTA, stored owner script
execution or owner-data reads occurred. No additional milestone is started.

## Result

Implemented modifier chords and named keys across the compiler IR, runtime Event,
mock Bridge/Planner and actual composed Route B adapter/scheduler/backend path.
`COMMAND a` now preserves modifier 0x08 and usage 0x04 through report submission;
`SHIFT LEFTARROW` preserves 0x02 and 0x50. Accepted mock input reports use eight
bytes and report ID 1, followed by the intended neutral restoration submission.

This is a separately pinned scratch composition patch, not an edit to installed
firmware or historical production/preview files. Historical X builders and its
public package remain reproducible and unchanged. No Pico GPL implementation was
copied. No language engine replacement or second expression parser was introduced.
See [design and exact syntax](keyboard-shortcuts-design.md),
[source and patch hashes](keyboard-shortcuts-source-manifest.json), and
[reference evidence](keyboard-shortcuts-references.json).

Canonical left modifiers, aliases and space/hyphen combinations are documented
in the design. The key inventory includes navigation/editing/system/lock keys
and F1–F24 with the non-contiguous F12/F13 boundary. F13–F24 are explicitly a
HID-backed extension to the saved Hak5 page's inventory. The apparent official
F0 typo is not implemented. New key names are reserved function identifiers;
existing scripts using those names as functions must rename them for this candidate.
Duplicate modifier bits, missing/multiple operands and unsupported aliases reject
preflight, including unreachable runtime code. DEFINE expands only final key
operands. No standalone modifier, persistent ownership, INJECT_MOD or RESET
capability is enabled in the actual Route B adapter.

## Executed verification

| Final executed scope | PASS | Unexpected FAIL | Assertions |
|---|---:|---:|---:|
| New actual-application shortcut cases K01–K25 | 25 | 0 | 1,660 |
| Unchanged W service/startup/owner cases | 34 | 0 | 380 |
| Selected unchanged T backend cases (T34 excluded below) | 46 | 0 | 460 |
| New mock Bridge/Planner B01–B08 | 8 | 0 | 166 |
| New compiler bounds/diagnostics/no-allocation C01–C03 | 3 | 0 | 126 |
| Selected unchanged Stage27B/28A/28B/28C core cases | 86 | 0 | 395,224 |
| **Total** | **202** | **0** | **398,016** |

The per-group counts/assertions above are backed by the machine receipt;
assertions measure checks, not supported-language features. Full commands, stdout,
stderr and excluded-case reasons are in [results](keyboard-shortcuts-results.json).
No old suite totals are reused as newly executed results. No claim is made that
all historical Stage1–28 suites were rerun; selection covers the changed source
and actual scheduler, backend, ownership, service and parser dependencies.

Coverage: aliases; F1–F24; navigation and lock taps; all 95 US printable character
mapping equivalences; shifted characters; exact report bytes/reserved byte/unused
slots/report IDs; press/restoration identities; DEFINE prefix boundaries; function,
IF and WHILE interaction; malformed/inactive statements; duplicate modifiers;
preflight zero-output; input backpressure; STOP/STOP_PAYLOAD; runtime arithmetic
failure; cancellation before/during a chord; disconnect; ambiguous press/release;
fresh-session modifier isolation; real simulated-task ownership; fixed bounds and
zero C++ new allocations during the focused compiler/runtime chord probe.

Five unchanged old core groups were NOT run because they require CTRL to reject
or use newly reserved F1-style function names. Their expectations/source remain
unchanged. C01/C02 separately validate the original function/call/symbol/nesting
limits with collision-free names, new reservation diagnostics and deferred
unsupported syntax. This is not silently changing historical expected outcomes.

### Separate observations and development failures

- T34, executed unchanged on the full candidate composition, failed its foreign
  owner assertion. Its Linux-thread fixture never assigns a foreign simulated
  RTOS task, whose default is 1. The full V/X task abstraction therefore sees the
  same task. This is retained separately as a harness incompatibility, not a PASS
  or evidence of a production ownership fix. K25 assigns task 2 explicitly and
  proves refusal without a lower call, followed by normal task-1 completion.
  Future runs of the new runner skip T34 with this reason; historical T34 is intact.
- The real modifier-drop negative control changes the compiler Event field to zero
  in a disposable source copy. B01 rejects the incorrect COMMAND report with exit 1.
  It is an expected negative result, outside the 202 PASS count.
- An altered original source hash is rejected before applying the candidate patch;
  recorded separately as an expected fail-closed input check.
- Initial harness development counted setup delays as HID delays, used duplicate
  header paths, omitted the T fixture's esp_random mock, and used an incorrect
  literal byte count in a Bridge test. ASan detected that test's over-read; it was
  corrected to `sizeof(source)-1`, not hidden with an engine change or disabled flag.
- A first target build exposed duplicate physical include identities defeating
  pragma-once for the new shared header. A proper include guard and a single
  scheduler include corrected it. The final clean target build passes.
- An early core-regression adaptation mixed the historical header ABI with the new
  Event header. Final tests copy unchanged historical test sources into an external
  mirror with the candidate header; all final selected core cases pass.
- Bridge failure tests were corrected to drive the documented intermediate Failing
  state to terminal Error before asserting. No production error was suppressed.

Final completed C++ runs use ASan/UBSan and leak detection, with no findings.
Historical language XPASS, upstream USB XFAIL and retirement limitations remain
historical evidence, not renamed or counted in these results. Linux native testing
is not native macOS or physical USB testing.

## Clean composed ESP32-S3 build

Arduino ESP32 3.3.0 protected isolated core, ESP-IDF
`idf-release_v5.5-b66b5448-v1`, Xtensa GCC14.2.0 esp-x32/2411; ESP32-S3, 16 MiB,
PSRAM disabled, USB-OTG/TinyUSB, CDC on boot, CPU240MHz, custom production partitions.
The original HID routing/NVS protections, checked settings, controlled startup,
US-only Route B admission and observational diagnostics are retained.

| Measurement | Installed X baseline | New review candidate | Change |
|---|---:|---:|---:|
| Compiler program bytes | 1,358,083 | 1,359,659 | +1,576 |
| Application BIN bytes | 1,358,224 | 1,359,808 | +1,584 |
| Static RAM | 106,256 | 106,264 | +8 |
| Free per 0x740000 OTA slot | 6,243,952 | 6,242,368 | −1,584 |
| Free OTA percentage | 82.133747% | 82.112911% | −0.020836 pp |

Application SHA-256:
`de241287b972c24e510d3e8d22d888a17f13d1e972142559ba3df19f6195b41d`

ELF SHA-256:
`fe5569b0a6d1819e266c7db3b16f7232929e87051123d7e0a4448fb57cb2f376`

Bootloader remains 20,256 B, SHA
`95b966ad240a05bf8a804cd4519eebac5271b662e51417668da488652b7354bf`.
Partition table remains 3,072 B, SHA
`b79bde9ef4a9544411d97a31a1d326b2028213269ad0dcc643ea921230ce3d5e`.
No merged image, migration package, private NVS image or flashing command was made.

[Full linked receipt](keyboard-shortcuts-build.json) records every source, compiler,
core/SDK archive, profile flag, linker input, artifact hash and stack estimate.
Post-link inspection verifies 177 SDK archives identical to W; 80 compiled source
copies; original HID/NVS guards; same partitions; actual ELF-to-BIN equality; the
four-argument modifier-carrying scheduler key API; owner loop and diagnostics.
There is no silently unpatched-core fallback. These are source/link guarantees,
not proof of physical startup or USB retirement.

Compiler statement frame 352 B (was336); admission96 B (was80); Runtime::tick112 B,
Adapter::receive64 B and owner tick304 B remain unchanged. These are individual
compiler frames, NOT peak task-stack measurements. Host sizeof: Event6 B (was4),
Program6936 B unchanged, Runtime4888 B unchanged, Planner96 B unchanged,
Bridge5064 B (was5056). Bridge already owns Runtime/Planner; do not add them again.
Target's static adapter22536 B (was22528) accounts for the8 B static-RAM growth.
No dynamic modifier collection or report queue was added. Compiler/Runtime hot
path uses fixed storage; lower-layer framework String/USB allocation risks remain.
No new physical heap, stack high-water, timing or latency measurements were taken.

## Remaining limits and review gates

Only the owner's listed X examples have physical evidence. The earlier Functiondone
case discrepancy remains unresolved. Exact new modifier behavior on High Sierra,
editor settings, host key release, disconnect cleanup/endpoint retirement and
other layouts remain untested for this image. Existing local acceptance is not
host delivery. Unchanged legacy web Run does not select Route B automatically.

The editor-only future fixture and owner review gates are in
[keyboard-shortcuts-owner-review.md](keyboard-shortcuts-owner-review.md).
A changed image requires its own artifact binding and separately approved
installation/test review; no automatic reflash, replay, autorun or default change.
Other audit milestones remain deferred. Do not infer a full DS3 compatibility claim.

## Changed file inventory

Only new `docs/keyboard-shortcuts-*` and `tests/keyboard_shortcuts/` files are added.
The exact per-file sizes/hashes and historical-file/mode preservation proof are in
[keyboard-shortcuts-integrity.json](keyboard-shortcuts-integrity.json).
Reproduction and safe inspection commands are in
[keyboard-shortcuts-reproduction.md](keyboard-shortcuts-reproduction.md).
