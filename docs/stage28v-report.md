# Stage28V service ownership and controlled candidate review

**Source/mock work delivered; complete integration/link gate remains BLOCKED.**
GO for review of the isolated candidate. NO-GO for claiming complete service
integration, target firmware link, physical deployment or Stage28W. No firmware
image was produced and no hardware/real HID action occurred.

Exact clean starting commit: `967596476dfe0dde5e824c8f6d1b2ba543502443`.
New branch: `stage28v-service-ownership-controlled-candidate`.
All1,254 prior tracked paths/bytes/modes and235 frozen Stage26 files are preserved.
The46 previous remote refs are snapshotted; publication verification compares
all of them and permits only this new branch. No old report/source/expectation,
installed dependency, USB identity, partition, profile or owner file is changed.

Implemented in new V files and a56-hunk scratch-only patch:

* Fixed synchronous service admission spanning actual settings, filesystem,
  SD/SPIFFS, MSC, LED, library and network-lifecycle bodies. Bounded nesting,
  task/chunk ownership, deferred abort and reentrant Start exclusion.
* Explicit copied CLI/HTTP Route B selection, typed status and STOP, no legacy
  fallback while busy, no boot selection or arming. Ordinary run stays legacy.
* Open writable stream exclusion before capture; actual FileSource uses precise
  volume selection, bounded capture and second byte verification.
* File/firmware uploads, their completion callbacks and restart return503 in the
  enabled candidate, even on repeated chunks or completion without data.
* Complete actual webserver native TU execution over simulated lower interfaces;
  actual typed settings, storage, SPIFFS, SD, MSC, NeoPixel, scheduler/backend and
  unchanged preview compiler/Runtime. No generic token model substitutes for a
  real handler PASS. The language subset and local-only semantics are unchanged.

Fresh tests: V56 PASS/566 assertions; unchanged U64/515; unchanged T47/467;
affected original production77/67,371; controlled startup30/635. Separate exact
selector-off comparisons pass77/67,371 and30/635 without adding coverage.
Preparation controls7 PASS; actual pinned target objects20 enabled /15 selector-off PASS. Zero unexpected
failures in final completed runs. ASan/UBSan/leaks clean; deliberate negative
controls and superseded fixture diagnostics are separately recorded. See the
test report and machine-readable results for every command/result.

The link acceptance gate is not satisfied: wrapper guards do not attest complete
SDK/VFS/USB/framework producer exclusion or asynchronous lifetime. V48 proves raw
VFS is outside wrapper admission, not an escaped enabled handler. Existing WS
application authentication and actual callback/request cancellation require review;
the existing serial-drain loop is not a hard bounded work claim. All inventoried
repository writers are guarded within the tested boundary, but missing lower
proof cannot be replaced by object or mock success. No controlled full link was
attempted, so there is no linked map, application size, final RAM, OTA headroom or
credible physical task-stack measurement. Strict Route A remains unresolved.

Selected target static payload grows16 bytes from23,374 to23,390; Adapter remains
22,528, Publication568, FileSource44. This is not final firmware RAM. Coordinator
frame304 and requestStart64 bytes remain unchanged; new admission helpers each32.
All dependencies, including the protected HID/NVS core patches, match U's pins.
The full resource ledger separates nested objects, probe limits and unknowns.

Answered: synchronous admission before real mutations, explicit frontend copying,
local owner/transaction behavior, enabled fail-closed callbacks, default-off
production/startup behavior and actual target declaration compatibility.
Blocked: complete lower producer closure, real framework/task/callback lifetime,
final link/resources and physical USB/media/host behavior. No SDK rebuild,
installed-package edit or external support message was used to bypass those gates.

Review documents: service-contract, handler-matrix, integration-review,
resource-ledger, test-report, reproduction, source-manifest, coverage,
native-results, target-object-results and integrity receipts. The complete changed
file inventory is appended below and hashed in the integrity receipt. Rollback is
leave Route B disabled and discard external scratch outputs. Recovery/physical
installation still requires separate owner review and authorization; original
firmware availability is OWNER CONFIRMED: AVAILABLE EXTERNALLY, and exact old data
preservation remains optional. Backups were untouched and not inspected.

Stage28W was not started. No hardware access, USB/serial traffic, real HID output,
stored owner payload execution, flash, erase, formatting, boot, OTA, SDK rebuild,
production merge or historical-ref rewrite occurred.

## New files only

- `docs/stage28v-coverage.json`
- `docs/stage28v-handler-matrix.md`
- `docs/stage28v-integration-review.md`
- `docs/stage28v-integrity.json`
- `docs/stage28v-native-results.json`
- `docs/stage28v-report.md`
- `docs/stage28v-reproduction.md`
- `docs/stage28v-resource-ledger.md`
- `docs/stage28v-service-contract.md`
- `docs/stage28v-source-manifest.json`
- `docs/stage28v-target-object-results.json`
- `docs/stage28v-test-report.md`
- `tests/stage28v/adapter.cpp`
- `tests/stage28v/adapter.h`
- `tests/stage28v/allocations.cpp`
- `tests/stage28v/allocations.h`
- `tests/stage28v/backend_lease.h`
- `tests/stage28v/backend_lease.inc`
- `tests/stage28v/check_preparation.py`
- `tests/stage28v/collect_results.py`
- `tests/stage28v/coordinator.cpp`
- `tests/stage28v/coordinator.h`
- `tests/stage28v/file_source.cpp`
- `tests/stage28v/file_source.h`
- `tests/stage28v/lower.cpp`
- `tests/stage28v/lower.h`
- `tests/stage28v/mocks/Adafruit_NeoPixel.h`
- `tests/stage28v/mocks/Arduino.h`
- `tests/stage28v/mocks/ESPAsyncWebServer.h`
- `tests/stage28v/mocks/FS.h`
- `tests/stage28v/mocks/SD.h`
- `tests/stage28v/mocks/SPI.h`
- `tests/stage28v/mocks/SPIFFS.h`
- `tests/stage28v/mocks/USBHID.h`
- `tests/stage28v/mocks/USBHIDKeyboard.h`
- `tests/stage28v/mocks/USBMSC.h`
- `tests/stage28v/mocks/Update.h`
- `tests/stage28v/mocks/WiFi.h`
- `tests/stage28v/mocks/host.h`
- `tests/stage28v/mocks/network.h`
- `tests/stage28v/mutation_guard.h`
- `tests/stage28v/nvs_fixture.cpp`
- `tests/stage28v/prepare_sources.py`
- `tests/stage28v/run_regressions.py`
- `tests/stage28v/run_startup.py`
- `tests/stage28v/run_tests.py`
- `tests/stage28v/scheduler_seam.h`
- `tests/stage28v/seam.inc`
- `tests/stage28v/services.patch`
- `tests/stage28v/target_check.py`
- `tests/stage28v/task_platform.h`
- `tests/stage28v/test_main.cpp`
- `tests/stage28v/verify_scope.py`
