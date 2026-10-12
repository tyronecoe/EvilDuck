# Stage 20 offline preservation/persistence tests

All data is synthetic; no owner binary, setting, credential or script is read/executed.
No device/port/USB/flash/OTA operation. C++ ASan/UBSan targets:

- Production settings.cpp typed setter/commit failures use NVS API stand-ins (not SDK
  flash), covering each12-key failure boundary, partial/failed-set effects, invalid/unloaded
  state, explicit reset, NVS-full/I/O/commit errors and busy lock refusal. Immediate map
  updates deliberately model persistence prefixes; they do not model full SDK GC.
- Pinned SDK Page/PageManager/Storage and complete exact supporting target partition API
  bodies execute with synthetic flash/descriptor/CRC/heap adapters. Readonly experiment
  denies lower calls, including attempted read cleanup. Descriptor ABI and precompiled
  SDK binary are not executed. Source corruption->NOT_FOUND is OBSERVED, not a protection
  pass. Abrupt save termination is explicitly a stand-in OBSERVATION, not physical power loss.
- Complete actual CLI module and extracted complete web handler bodies validate checked
  success/failure/busy responses; whole AsyncWebServer/TinyUSB/RTOS is not host-executed.
- Python summary tests enforce whitelist/privacy/classification/identity/overwrite limits.
  Summary inputs are synthetic reports with published expected hashes, not owner evidence.

```sh
# Existing Stage19 source/generator preparation remains hash-pinned and applicable.
python3 tools/partition_source_prepare.py --output /absolute/path/new-partition-reference
python3 tests/stage20/run_tests.py --sdk-source /absolute/path/verified-idf-test-source \
  --partition-source /absolute/path/new-partition-reference/partition_target.c \
  --build-dir /absolute/path/new-stage20-runtime --results /absolute/path/new-runtime-results.json
python3 tests/stage20/ui_tests.py --build-dir /absolute/path/new-stage20-ui \
  --results /absolute/path/new-ui-results.json
python3 tests/stage20/summary_tests.py --results /absolute/path/new-summary-results.json
```
Source preparer only downloads exact recorded immutable official sources into a new
external directory; it verifies hashes and never replaces SDK/library/core sources.
Actual source preparation and these runners were executed in this cloud environment.
Prior Stage19 startup mock adapts its raw setter/commit/open stand-ins for new save
implementation; prior outcomes/classifications retained. Shared CLI mock now provides
checked-save wrappers and a test-only result switch defaulting success. No firmware
behavior is inferred from the mock switch. New production guards use existing TryGuard;
USB feedback behavior is unchanged and prior concurrency/allocation suites rerun.

All Stage1–19 regression runners remain required. Stage9 observations and historical
language XPASS/original USB XFAIL/NVS risks remain separately classified. New readonly
source passes do not mean protection is deployed. See stage20-results.json/report.
