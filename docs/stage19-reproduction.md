# Stage 19 reproduction and rollback

Keep Stage18 isolated-core process and exact dependency pin unchanged. Owner installed
Arduino3.3.0/global toolchain is never patched. Fresh disposable copies apply the same
Stage16 HID patch and Stage18 no-auto-erase patch with original/patched file/tree hashes.
No SDK library replacement or source rebuild. Reject failed/partial/hash-mismatched work.

From repository root, with existing pinned libraries/CLI:
```sh
ED_CORE='/absolute/path/to/Arduino/data/packages/esp32/hardware/esp32/3.3.0'
ED_USER='/absolute/path/to/Arduino/user'
ED_CLI='/absolute/path/to/arduino-cli'
ED_NORMAL_ISO='/absolute/path/to/new-stage19-normal-core'
ED_SAFE_ISO='/absolute/path/to/new-stage19-safe-core'
ED_NORMAL_BUILD='/absolute/path/to/new-stage19-normal-build'
ED_SAFE_BUILD='/absolute/path/to/new-stage19-safe-build'
python3 tools/build_s3_patched.py --core-dir "$ED_CORE" --user-dir "$ED_USER" \
  --arduino-cli "$ED_CLI" --isolation-dir "$ED_NORMAL_ISO" --build-dir "$ED_NORMAL_BUILD"
python3 tools/build_s3_patched.py --core-dir "$ED_CORE" --user-dir "$ED_USER" \
  --arduino-cli "$ED_CLI" --isolation-dir "$ED_SAFE_ISO" --build-dir "$ED_SAFE_BUILD" --deployment-safe-start
ED_NORMAL_CORE="$ED_NORMAL_ISO/data/packages/esp32/hardware/esp32/3.3.0"
ED_SAFE_CORE="$ED_SAFE_ISO/data/packages/esp32/hardware/esp32/3.3.0"
```
Both wrappers clean compile and verify actual linked USB/NVS/settings/profile identity,
source/header/flags, ELF->BIN equivalence and reviewed partitions. They never upload.
PSRAMdisabled,USB-OTG TinyUSB/CDC and exact FQBN remain pinned. Local IDE Hardware CDC/
JTAG is not this profile; do not substitute a personality to bypass reproduction failure.
High Sierra native CLI/compiler execution is not newly verified by cloud Linux builds.

Read-only SDK archive evidence:
```sh
python3 tools/nvs_sdk_evidence.py --core-dir "$ED_CORE" \
  --output /absolute/path/to/new-archive-evidence.json
```
No SDK binary execution. Host source source/generator preparation, runtime and offline
checks are in tests/stage19/README.md. Exact official source commit and file hashes are
in stage19-sdk-source-pin.json; generator0.1.9 wheel/files in stage19-generator-pin.json.
Preparation was actually reproduced in fresh external directories and hashes rechecked.
Generator is for synthetic plaintext tests, not migration or owner NVS repair.

```sh
python3 tests/stage19/integration_tests.py --original-core "$ED_CORE" \
  --normal-core "$ED_NORMAL_CORE" --safe-core "$ED_SAFE_CORE" \
  --normal-build "$ED_NORMAL_BUILD" --safe-build "$ED_SAFE_BUILD" \
  --sdk-source /absolute/path/to/verified-idf-test-source \
  --generator-dir /absolute/path/to/verified-generator \
  --results /absolute/path/to/new-integration-results.json
python3 tools/analyze_s3_stack.py --build-dir "$ED_NORMAL_BUILD" \
  --output /absolute/path/to/new-normal-stack.json
python3 tools/analyze_s3_stack.py --build-dir "$ED_SAFE_BUILD" \
  --output /absolute/path/to/new-safe-stack.json
```
Stack objects are disposable; no firmware ELF/core alteration. Estimates include settings,
setup/loop/core startup plus previous modules, not physical task high-water.

Previous test runners remain applicable: Stage2 includes all five Stage1 cases;
Stages3..14 run with --build-dir external; Stage9 observations have --results; Stage15
history needs exact Stage15 backend via --baseline-backend (git show on that prior commit
into an external test file), original core, and separate classifications. Stage16 routing
uses the patched core, build_validation uses original/patched core plus final normal build.
Stage17 uses both current builds and --upstream-core original to retain its original-core
risk observation. Stage18 startup/dependency tests use original/patched core and current
normal build. See each --help/README; old results were not silently reused for verification.

Artifact inventory command (no owner images; no writer):
```sh
python3 tools/deployment_inventory.py --normal-core "$ED_NORMAL_CORE" --normal-build "$ED_NORMAL_BUILD" \
  --safe-core "$ED_SAFE_CORE" --safe-build "$ED_SAFE_BUILD" \
  --output /absolute/path/to/new-provisional-inventory
```
Committed deployment/stage19 adds owner-local evidence annotation/source fingerprint to
that provisional inventory. Actual user files remain absent from package; independent
structural verification pending. Safe app is proposed for both slots only after further
review; normal transition is separate. No padded merged migration image is approved.

Private owner file-only full preflight: stage19-owner-preflight.md. No need to upload
backups or run esptool; it remains read-only and refuses existing output replacement.
Any unresolved NVS classification blocks checked plans, clean subset does not authorize
migration. Existing NVS9000/5000 and SPIFFS file-level safeguards unchanged.

Rollback source/build preparation: keep Stage18 remote untouched; select it separately
when needed and discard only explicitly disposable Stage19 outputs. No global core patch
reversal, uninstallation or physical operation. Source rollback is not device recovery.
Restoring original full flash would overwrite live data and requires separate owner
approval/current backups/exact device/ROM recovery review. No destructive command supplied.
