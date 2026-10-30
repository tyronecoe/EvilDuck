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
