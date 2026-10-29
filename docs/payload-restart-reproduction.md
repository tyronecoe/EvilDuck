# Offline reproduction — composed payload restart

Use fresh disposable outputs. These commands do not open a board, emit real HID, run a host payload, upload firmware or invoke an installer. Historical overlays and installed dependencies stay unchanged; the new layer must validate exact source/patch identities and its explicit selector.

The successful final native execution used:

```bash
python3 tests/payload_restart/run_tests.py --core /workspace/scratch/led-feedback-isolated-core/data/packages/esp32/hardware/esp32/3.3.0 --build-dir /workspace/scratch/payload-restart/native-v3 --results /workspace/scratch/payload-restart/native-v3.json
```

The clean build and linked verification also completed successfully using:

```bash
python3 tests/payload_restart/build_candidate.py --output-dir /workspace/scratch/payload-restart/build-v1 --config /workspace/scratch/led-feedback-isolated-core/arduino-cli.json --core /workspace/scratch/led-feedback-isolated-core/data/packages/esp32/hardware/esp32/3.3.0 --arduino-cli /workspace/tooling/arduino/bin/arduino-cli --jobs 4
python3 tests/payload_restart/verify_link.py --build-root /workspace/scratch/payload-restart/build-v1 --output /workspace/scratch/payload-restart/linked-v1.json
python3 tests/stage28h/verify_freeze.py
```

Do not reuse these occupied native/build/output paths. Choose fresh disposable names when reproducing; tools refuse existing outputs. Full target commands, exact flags, linked call evidence and source/artifact hashes are in `payload-restart-build.json`; resource comparisons are in `payload-restart-resources.json`.

Tests exercise actual composed compiler/runtime/adapter/backend modules with mocked transport, storage, clocks and randomness. Final native-v3 results: **403 PASS/0 FAIL,15,211 assertions** (32 new/278;371 selected earlier/14,933), with ASan/UBSan/leak detection clean. Exact C++ command and test-input identities are in `payload-restart-test-results.json`. Intentional selector rejections and historical dispositions remain separately recorded.

The historical V14 receipt had53 assertions, while its unchanged source now executes79:26 additional held-key/jitter assertions. The old executable omitted the late branch despite a later timestamp, so the earlier `final_driver_used` inference was incorrect. Historical artifacts remain untouched and the missing coverage is not retroactively declared passed. The26 assertions are counted in this fresh run only. Native-v1's missing test include and native-v2's two incorrect fixture assumptions are retained as development diagnostics; corrected native-v3 totals are not combined with earlier runs.

The build preserves the approved isolated Arduino ESP32 core3.3.0 archive profile, all177 SDK archive identities, USB/NVS/startup/ownership guards, exact compiler options, source selectors, linked restart/neutral-clear edges and ELF-to-BIN verification. No global Arduino core or SDK is patched. Compiler frame/static/object measurements do not establish hardware heap, stack high-water, latency or USB delivery.

Executed native environment: Linux, Python3.12.14, Debian g++14.2.0 (`14.2.0-19`), GNU Bash5.2.37, C++17 and address/undefined sanitizers with leak detection. Host package interfaces remain High Sierra10.13.6, Bash3.2, Python3.8 and esptool4.12; native High Sierra execution of the new candidate remains pending.

After all source/native/build/link checks pass, inspect `python3 tests/payload_restart/package.py --help`. Commit source before binding its package revision. Package and bound-installer tests use disposable public copies and synthetic tool responses only. Bind exact accepted text/keyboard rollback. Publish only the isolated new branch/archive, download the commit-pinned ZIP, compare size/hash/member identities, and verify all previous remote refs unchanged. No LED helper or second installation package is needed.
