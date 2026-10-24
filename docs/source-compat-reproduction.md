# Offline reproduction — composed preprocessing candidate

No command below opens a board, emits real HID output or invokes an installer. Use new disposable output directories; dependencies and historical overlays remain read-only. The new overlay uses exact before/after hashes and fails on missing/wrong candidate selectors. Existing parent runner/source hashes are mandatory.

```bash
python3 tests/source_compat/run_tests.py --core /workspace/scratch/led-feedback-isolated-core/data/packages/esp32/hardware/esp32/3.3.0 --build-dir /workspace/scratch/NEW-source-native --results /workspace/scratch/NEW-source-native.json
python3 tests/source_compat/build_candidate.py --output-dir /workspace/scratch/NEW-source-build --config /workspace/scratch/led-feedback-isolated-core/arduino-cli.json --core /workspace/scratch/led-feedback-isolated-core/data/packages/esp32/hardware/esp32/3.3.0 --arduino-cli /workspace/tooling/arduino/bin/arduino-cli --jobs 4
python3 tests/source_compat/verify_link.py --build-root /workspace/scratch/NEW-source-build --output /workspace/scratch/NEW-source-linked.json
python3 tests/stage28h/verify_freeze.py
```

Native runner adds preprocessing cases to all 44 lock-feedback cases and the same selected keyboard/control/`STOP`/HID/receiver/HTTP regressions. Each case executes actual composed modules in its own process with mocked USB/storage/time and ASan/UBSan/leak detection. Historical refusal cases/obsolete status expectations stay separately classified rather than relabeled. Missing/zero source-profile selectors are intentional compile rejection controls.

Build retains the existing approved separately pinned archive-feedback profile; no SDK archive is rebuilt/replaced. All 177 archive identities, startup/no-auto-erase/USB guards, compiled-source hashes, linked call edges and ELF-to-BIN regeneration remain mandatory. Additional compiler-source/selector checks identify the new overlay. Resource/compiler-frame numbers come from clean artifacts, never physical high-water measurements.

After committing source and successful post-link verification, use `python3 tests/source_compat/package.py --help` to review the required output, source, core and receipt arguments before packaging. The `tests/source_compat/test_package.py` and `test_bound_installer.py` tests operate on disposable public copies/mock esptool only. New rollback must be the current `ae079…` application. Publish only committed verified public ZIPs and independently re-download and verify SHA-256/size. Helper v4 ZIP has its own source commit/manifest/test receipt; do not combine helper and firmware identity.
