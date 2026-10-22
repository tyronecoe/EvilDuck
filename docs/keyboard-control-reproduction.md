# Reproduce the isolated keyboard-control candidate

Base source: `cb3a147719850a0dc4a4797b401b606ea14c6571`.
The new source overlay follows the exact historical Caps/STOP composition. Root
firmware, `language_preview` and prior overlays/verifiers are historical inputs,
not files edited in place. Use fresh disposable output paths.

The build uses the existing approved isolated Arduino ESP32 core3.3.0 archive
feedback profile, pinned ESP-IDF5.5 archives, Xtensa compiler, libraries, source
checks and startup decoders. No global core or SDK is modified. ESP32-S3,16MiB,
PSRAM disabled, USB-OTG/TinyUSB, CDC, CPU and flash settings remain unchanged.

Offline build and link-review commands, from the repository root:

```bash
python3 tests/keyboard_control/build_candidate.py --output-dir /workspace/scratch/NEW-keyboard-build --config /workspace/scratch/led-feedback-isolated-core/arduino-cli.json --core /workspace/scratch/led-feedback-isolated-core/data/packages/esp32/hardware/esp32/3.3.0 --arduino-cli /workspace/tooling/arduino/bin/arduino-cli --jobs 4
python3 tests/keyboard_control/verify_link.py --build-root /workspace/scratch/NEW-keyboard-build --output /workspace/scratch/NEW-keyboard-linked.json
python3 tests/keyboard_control/run_tests.py --core /workspace/scratch/led-feedback-isolated-core/data/packages/esp32/hardware/esp32/3.3.0 --build-dir /workspace/scratch/NEW-keyboard-native --results /workspace/scratch/NEW-keyboard-native.json
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests/keyboard_control -p test_host_workflow.py -v
python3 tests/stage28h/verify_freeze.py
```

The first two commands compile/inspect firmware artifacts only. They have no
port, upload or physical-device interface. Do not use a generated merged image as
an installation artifact. The review package uses only application images in the
existing approved OTA geometry and requires separate fresh device/layout checks.

Historical builder/verifier bytes are hash-pinned. The new wrappers record each
explicit in-memory adaptation needed for the keyboard delta, including source
identity and buildId. Dependency, USB, NVS, startup, partition, ELF/BIN and linked
archive checks remain mandatory. The source manifest verifies before/after hashes
and deterministic patch application; a missing or partial layer must fail closed.

Actual executed commands, focused native test selection, sanitizer status,
package-fault tests, firmware hashes and measured compiler resource values are
recorded in `keyboard-control-test-results.json` and `keyboard-control-report.md`.
Compiler stack estimates are not physical stack high-water measurements. Python3.8
grammar/Bash syntax checks are not native High Sierra execution.

The Mac package retains the existing deliberate app-only installer flow, progress
messages, fresh backup and verification requirements. It does not authorize an
installation or automatically reboot, repair storage, reset settings or execute
a payload. Read the package's install and rollback documents before any separately
approved physical action. No new dependency installation is part of this work.

The release is bound to source commit
`c7eb40f20fcdab54670c6bd6dce187faf9250115`. The later publication commit adds only
release evidence, documentation and packaged artifacts; the verified source delta
and build remain unchanged. Package assembly uses the exact linked receipt:

```bash
python3 tests/keyboard_control/package.py --directory /workspace/scratch/NEW-keyboard-package --build-root /workspace/scratch/NEW-keyboard-build --linked-report /workspace/scratch/NEW-keyboard-linked.json --core /workspace/scratch/led-feedback-isolated-core/data/packages/esp32/hardware/esp32/3.3.0 --source-commit c7eb40f20fcdab54670c6bd6dce187faf9250115 --archive /workspace/scratch/NEW-keyboard-package.zip
python3 tests/keyboard_control/test_package.py --directory /workspace/scratch/NEW-keyboard-package --archive /workspace/scratch/NEW-keyboard-package.zip --ota-template /workspace/scratch/led-feedback-isolated-core/data/packages/esp32/hardware/esp32/3.3.0/tools/partitions/boot_app0.bin --results /workspace/scratch/NEW-package-tests.json
python3 tests/keyboard_control/test_bound_installer.py --directory /workspace/scratch/NEW-keyboard-package --ota-template /workspace/scratch/led-feedback-isolated-core/data/packages/esp32/hardware/esp32/3.3.0/tools/partitions/boot_app0.bin --results /workspace/scratch/NEW-installer-tests.json
```

Those two test commands inject device/tool responses; they do not call hardware.
An optional separate LED host kit can be prepared with
`python3 tests/keyboard_control/host_workflow.py --archive /tmp/NEW-keyboard-led-host.zip`.
Its only algorithm-source adaptation is the expected buildId in `device.py`;
the original sources and archive remain intact. It is not an installer or a
requirement to repeat the already accepted LED milestone.
