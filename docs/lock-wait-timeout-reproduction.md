# Offline reproduction

Run from repository root with fresh disposable output directories; never supply a device port. The source manifest pins all five generated changes and exact parent/patch hashes. Historical dependency/core/SDK installations are read-only inputs; the build copies/patches isolated sources only.

```bash
python3 tests/lock_wait_timeout/run_tests.py --core /workspace/scratch/led-feedback-isolated-core/data/packages/esp32/hardware/esp32/3.3.0 --build-dir /workspace/scratch/lock-wait-timeout/native-v3 --results /workspace/scratch/lock-wait-timeout/native-v3.json
python3 tests/lock_wait_timeout/test_observe_wait.py
python3 tests/lock_wait_timeout/build_candidate.py --output-dir /workspace/scratch/lock-wait-timeout/build-v1 --config /workspace/scratch/led-feedback-isolated-core/arduino-cli.json --core /workspace/scratch/led-feedback-isolated-core/data/packages/esp32/hardware/esp32/3.3.0 --arduino-cli /workspace/tooling/arduino/bin/arduino-cli --jobs 4
python3 tests/lock_wait_timeout/verify_link.py --build-root /workspace/scratch/lock-wait-timeout/build-v1 --output /workspace/scratch/lock-wait-timeout/linked-final.json
python3 tests/stage28h/verify_freeze.py
```

Actual fresh results, environment, commands, source inventory, source-to-compiled/linked proof and artifact identities accompany this report. Existing classifications and historical receipts remain unchanged; older passes are not reused as fresh results. Native-only `-fno-access-control` allows the tests to mutate pending event fields without production hooks; this flag is not used in firmware. Mock HID is not real host delivery.

Final package/check commands (choose fresh output/result paths to reproduce):

```bash
python3 tests/lock_wait_timeout/package.py --directory /workspace/outputs/evilduck-routeb-lock-wait-timeout-macos-v1-final --build-root /workspace/scratch/lock-wait-timeout/build-v1 --linked-report /workspace/scratch/lock-wait-timeout/linked-final.json --core /workspace/scratch/led-feedback-isolated-core/data/packages/esp32/hardware/esp32/3.3.0 --archive /workspace/outputs/evilduck-routeb-lock-wait-timeout-macos-v1-final.zip --source-commit a1e521325cb6a41e6424227cdf4023ed0e52a9a8
python3 tests/lock_wait_timeout/test_package.py --directory /workspace/outputs/evilduck-routeb-lock-wait-timeout-macos-v1-final --archive /workspace/outputs/evilduck-routeb-lock-wait-timeout-macos-v1-final.zip --ota-template /workspace/scratch/led-feedback-isolated-core/data/packages/esp32/hardware/esp32/3.3.0/tools/partitions/boot_app0.bin --results /workspace/scratch/lock-wait-timeout/package-tests-final.json
python3 tests/lock_wait_timeout/test_bound_installer.py --directory /workspace/outputs/evilduck-routeb-lock-wait-timeout-macos-v1-final --ota-template /workspace/scratch/led-feedback-isolated-core/data/packages/esp32/hardware/esp32/3.3.0/tools/partitions/boot_app0.bin --results /workspace/scratch/lock-wait-timeout/installer-tests-final.json
```

The external `-final` suffix preserves the initial failed-guide archive as development evidence. The single published filename is `evilduck-routeb-lock-wait-timeout-macos-v1.zip`; renaming does not change ZIP bytes. No failed package is published. The bundled report is its source-commit snapshot; later repository artifact/publication receipts supply final package checks and download verification without rebuilding firmware or rewriting the archive.
