# Stage 19 tests

All inputs synthetic. No device/serial/USB APIs; no owner files, credentials or scripts
are read or executed. Page/PageManager/Storage/Item/HashList are unmodified pinned SDK
source compiled for host with synthetic flash, logging/heap/CRC/BSD adapters. Full SDK
initializer, Xtensa library, locking/ROM/real flash are not executed. Recovery tests PASS
when the expected mutation/failure is observed; those are not preservation/compatibility
passes. Exact flash operation ranges retained in results. Settings tests compile actual
production settings.cpp + setup/loop, mocking NVS APIs and services; SDK recovery tests
separately expose that nominal read-only getters can internally mutate.

Fetch checksum-verified immutable official sources/generator only into fresh external
directories; do not install/rebuild/substitute SDK or alter global core. Generator's
cryptography import is needed for its CLI even though fixtures use plaintext; use the
existing approved Python environment. No generator is needed by owner NVS inspection.

```sh
python3 tools/nvs_source_prepare.py --output /absolute/path/new-idf-test-source
python3 tools/nvs_generator_prepare.py --output /absolute/path/new-generator-source
python3 tests/stage19/run_tests.py --sdk-source /absolute/path/new-idf-test-source \
  --build-dir /absolute/path/new-stage19-tests --results /absolute/path/new-runtime-results.json
python3 tests/stage19/offline_tests.py --sdk-source /absolute/path/new-idf-test-source \
  --generator-dir /absolute/path/new-generator-source --results /absolute/path/new-offline-results.json
```

After clean normal/safe protected builds, run integration_tests.py --help for required
core/build/source paths. It checks mutated-source rejection, actual archive calls,
linked settings guards, accurate owner evidence provenance and unresolved-NVS plan gates.
Current C++ targets use ASan/UBSan. Python structural tests aren't sanitizer targets.

Prior Stage17/18 startup tests now explicitly mock successful settings::ready/loadError,
preserving existing test classifications. New Stage19 tests exercise real settings failures.
Stage9 observations, five historical language XPASS, six original routing XFAIL and earlier
NVS risks remain separate. No test expectation was removed to make results greener.
