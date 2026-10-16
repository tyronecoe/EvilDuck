# Limited compatibility and documentation pass

Baseline: `79c964d4f32a41f1295f2f96ebce8a42a8061c05` on
stage28y-public-download. Work branch: compatibility-boundaries-and-engine-docs.
The checked source is the developed EvilDuck firmware, not the original Cifertech
upload. No firmware source, evaluator, scheduler, parser, USB interface, deployment
tool, credential, partition or prepared package changes. Only tests/documentation.

## Scope and result

39 PASS /0 final FAIL /712 assertions. Twelve new engine-specific cases (107
assertions),27 selected unchanged regressions (605 assertions). C++ native executions
use actual production modules and named RAM-only HID/storage/clock/task/network/NVS
mocks, ASan/UBSan and leak detection. No device/host input is emitted. Complete per-case
results, commands and development diagnostics are in compatibility-pass-results.json.
No old pass totals are presented as newly executed full-stage suites.

Firmware C++ is byte-identical to baseline. New C++ files are native test drivers,
not target firmware. No new target build/link is needed/performed for this pass.
Existing X ELF/BIN identities and prepared ZIP were checked unchanged; this is
integrity evidence, not a fresh target build, runtime or physical USB validation.
No optional change is made a prerequisite for already-planned firmware testing.

## Coverage audit and additions

| Subject | Existing coverage reused / inspected | New meaningful gap covered |
| --- | --- | --- |
| Variable identifiers | Stage3 identifier/table limits and numeric semantics; Stage7 unknown-name interpolation boundary | Similar *defined* names n/nn/n_1 in assignments and compound IF, on both engines; whole-name interpolation separately on legacy |
| DEFINE | Stage3 forward replacement, single-pass/declaration exemption, duplicates/table bounds | Combined hash-label N/NN and bare WORD/WORDS collisions, declaration order and non-word boundaries on both engines |
| Mixed IF/WHILE | Stage6 return unwinding nested IF/WHILE, caller-control restoration, inactive function calls and condition reevaluation | No duplicate structural suite added; selected existing cases actually rerun |
| Functions/returns | Stage6 explicit/implicit void return, nested numeric calls, unused-body preflight errors and mismatched nested delimiters | Similarly prefixed count/counts/count_1 dispatch, global side-effect count and expression return on both engines |
| Text whitespace | Stage7 STRING leading/trailing preservation, one-tab STRINGLN policy, multiline repeat; Stage8 mixed text/control/functions | Existing observable cases already sufficient; rerun rather than inflate case count |
| Unsupported source | Existing malformed-function/body preflight, W authentication/busy/STOP tests | Four unverified aliases reject on legacy and actual X Route B; Route B inactive unsupported random command, prefix-related undefined variable, and ownership-IR adapter refusal all before lower reports |
| Modifiers/releases | Stage8 existing alias, representative right-side chord, modifier-only, stop/error-release and mixed keyboard cases | No mapping change required; new negative aliases pin deliberate unsupported status |

New shared fixtures are variable-prefixes.duck, define-prefixes.duck and
function-prefixes.duck under tests/compatibility_pass/fixtures. They contain only
finite arithmetic/functions/conditions and harmless literal text for mocks. Text
interpolation is legacy-only; it is not smuggled into Route B. Successful legacy
execution does not count as Route B coverage: Route B cases run through actual
patched X setup/coordinator/FileSource/compiler/adapter/scheduler/backend bodies.
They assert completion/reason or rejection, retained Route B selection and no fallback.

The ownership case intentionally demonstrates a boundary: standalone preview grammar
can represent HOLD/RELEASE, but actual X Adapter's ownershipCommands capability check
rejects before sync/execution. The separate inactive RANDOM_CHAR case is a valid
legacy feature, not a request to implement it in Route B. Unsupported statements are
still validated inside inactive runtime branches; preprocessing exclusion is a
separate legacy feature, not an equivalent policy.

## Reference and expectation provenance

Pico-Ducky e087a69da9d9c474a18a35ad26ba790cd71a11ab was an idea source only. No GPL
code was copied/translated or executed, and its output is not an oracle. Current
Hak5 HTML requests returned403 on2026-10-16. Six saved official Markdown snapshots
were independently SHA-256-checked against docs/stage9-reference-sources.json;
URLs, saved names and hashes are in compatibility-pass-references.json.

* [Variables — naming/global scope](https://documentation.hak5.org/hak5-usb-rubber-ducky/attack-modes-constants-and-variables/variables.md): n/nn/n_1 are distinct valid global numeric identifiers. Canonical IF and arithmetic establish the shared fixture's visible marker. Legacy STRING interpolation is a documented EvilDuck extension, not inferred canonical DS3.
* [Constants — string replacement and label forms](https://documentation.hak5.org/hak5-usb-rubber-ducky/attack-modes-constants-and-variables/constants.md): hash labels can replace within text; bare labels are delimited words; DEFINE declarations are exempt. Overlapping-label longest-match selection, duplicate rejection, nonrecursive expansion and table bounds are explicitly tested EvilDuck contracts where reference detail is insufficient.
* [Conditional statements — IF/ELSE and nesting](https://documentation.hak5.org/hak5-usb-rubber-ducky/operators-conditions-loops-and-functions/conditional-statements.md) and [loops — condition reevaluation](https://documentation.hak5.org/hak5-usb-rubber-ducky/operators-conditions-loops-and-functions/loops.md): selected branches, global assignment and reevaluation establish shared success markers and existing mixed-control fixtures. Preflight of all runtime branches and bounded nesting/progress are deliberate project safety contracts.
* [Functions — declaration/invocation/RETURN](https://documentation.hak5.org/hak5-usb-rubber-ducky/operators-conditions-loops-and-functions/functions.md): named no-argument functions and returned numeric expressions. Shared fixture's global counter verifies exactly-once execution. Identifier-prefix isolation follows distinct identifiers; void-value rejection, key-name collisions and depth/call budgets are project contracts, not new standard claims.
* [Keystroke injection — STRING/STRINGLN blocks, Basic Modifier Keys](https://documentation.hak5.org/hak5-usb-rubber-ducky/ducky-script-basics/keystroke-injection.md): leading-whitespace STRING versus one-leading-tab STRINGLN policies and modifier families. Exact formatting edges remain the existing Stage7 contract, not independently observed official-compiler output. Report bits follow USB HID Usage Tables keyboard page0x07 (right Alt usage0xE6, right GUI0xE7); extra spellings are not inferred from HID usages.

No official compiler/device oracle was run. These tests do not establish all DS3
precedence/evaluation edges or full compatibility; existing documented uncertainties
and limits remain unchanged.

## Modifier alias decision

Actual source is EvilDuckS3/duck_keys.cpp:isModifierName; case-normalized lookup is
shared by legacy chords and ownership validation. Existing RIGHTGUI/RIGHTWINDOWS
map to0x80 and RIGHTALT/RALT to0x40. Existing GUI/WINDOWS/COMMAND left-GUI and
ALT/OPTION left-Alt functionality remains. RGUI, RWINDOWS, RCOMMAND and ROPTION are
absent; no verified official spelling requirement was established. They would be
optional EvilDuck aliases/extensions, not canonical additions. This pass leaves
all four unsupported rather than adds spelling-only compatibility without a stated
reference need. No alias implementation, key enum, descriptor or report changes.

Selected Stage8 tests actually compare eight-byte accepted mock reports and report
ID1. RIGHTWINDOWS A produces modifier0x80/key usage0x04, followed by neutral bytes;
RALT A produces0x40/key0x04. The representative RIGHTCTRL-RIGHTSHIFT-RIGHTALT-RIGHTGUI
F13 chord has0xF0/key0x68 followed by neutral. Stop/error and modifier-only cleanup
regressions pass. These are local mocked-report outcomes, not host delivery/release.
Route B does not acquire modifier/chord support through this audit; its four alias
negative cases compile/fail through its own path with no legacy retry.

## Two engines and preserved safety

The concise current comparison now lives in language_preview/README.md, with its
old stage notes explicitly historical. Source anchors verified during this pass:

* EvilDuckS3/duckscript.cpp run/update and script_parser.cpp Validator: developed
  legacy global variables/control/functions/preflight, storage-backed execution.
* language_preview/core.h/core.cpp: fixed Program/CompileSession/Runtime, limits,
  no arbitrary eval, explicit error/sink contracts.
* tests/stage28v/adapter.cpp:74: reject ownership IR; adapter receives only supported
  Character/KeyTap/Delay events; exact X instrumentation.patch does not broaden it.
* tests/stage28u/portable.patch and stage28w boundary composition: ordinary CLI
  run or authenticated /run?s=... stays legacy. Explicit `routeb <script>` or
  authenticated `/run?engine=routeb&s=<script>` selects Route B only in builds with
  EVILDUCK_PORTABLE_ROUTE_B. Invalid engine/busy/compile/capability errors refuse,
  never silently retry legacy. X boot binds owner, not engine selection/arming.

W11/W15/W18–20/W33–34 regressions rerun on actual X instrumentation bodies cover
owner progress under serial pressure, STOP backlog, explicit HTTP selection/status,
authentication, busy-no-fallback and synchronized settings/auth snapshots. No change
to publication, lease/transaction lifetime, backpressure, first fault, permanent
loss/ambiguity quarantine or local cleanup is introduced. W restrictions on mutating
WebSocket CLI, filesystem-backed async responses and upload/update/restart remain.

LOCAL_SCHEDULER_DONE / LOCAL_CLEARING_SUBMITTED are local observations. USB/host
receipt, key release, endpoint retirement, actual FreeRTOS/AsyncTCP behavior and
physical media/heap/stack still need separately authorized validation. Physical
checks were NOT PERFORMED. No new hardware/deployment stage is authorized here.

## Execution, diagnostics and reproduction

From repository root, use fresh external paths:

```sh
python3 tests/compatibility_pass/run_tests.py --build-dir /tmp/evilduck-compatibility-pass --results /tmp/evilduck-compatibility-results.json
python3 tests/stage28h/verify_freeze.py
```

Python3.12.14 / Debian g++14.2.0-19 on Linux; existing compile_target and X command/
source-preparation helpers reused unchanged. Source copies are disposable, SDK and
installed core untouched. Existing Stage6 fixture emits its preexisting misleading-
indentation compiler warning; it is recorded, not hidden by new suppression flags.
ASan/UBSan halt-on-error and detect_leaks=1 were set for completed native processes.

Initial development had two test-input mistakes: F() conflicts with an existing
legacy physical key name, so the shared test was changed to count()/counts()/count_1();
and an existing STRINGLN case name was misspelled. Actual corrected cases were rerun,
three additional existing mixed-control cases ran from the same newly built binary,
and successful cases were not rebuilt/repeated unnecessarily. Full initial errors
are retained under development_diagnostics; no historical XFAIL/XPASS was relabelled.
No firmware defect was demonstrated; key-name rejection is a deliberate documented
limit. No larger source follow-up was hidden or added to the prepared-image gates.

Consumer Control/media, PRINT, locales, buttons, IMPORT and restart semantics remain
out of scope. Optional future alias adoption would need an explicit extension or
verified canonical contract and a new source/build identity; it is not a prerequisite
for testing existing X/Y bytes. Published ZIP remains4837000B / SHA256
6cfe4b33bda853004f6af4672b553700e1756a6feeda9bd4579dd27cbf3a705f.

## Changed files

* language_preview/README.md — current comparison and historical-note clarification.
* docs/compatibility-pass.md — audit, reference decisions and reproduction/report.
* docs/compatibility-pass-results.json — actual native results/development diagnostics.
* docs/compatibility-pass-references.json — verified official snapshot provenance.
* docs/compatibility-pass-integrity.json — baseline/source/package/ref inventory.
* tests/compatibility_pass/run_tests.py — reuses existing compilers/mock harnesses.
* tests/compatibility_pass/legacy.cpp and route_b.cpp — narrow native test drivers.
* tests/compatibility_pass/fixtures/{variable-prefixes,define-prefixes,function-prefixes}.duck — three shared harmless fixtures.
