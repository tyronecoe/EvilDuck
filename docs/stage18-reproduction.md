# Stage 18 reproducible protected-core builds

Use existing verified Arduino3.3.0, libraries and CLI; never patch the owner's installed
core. Stage16 HID patch/companion hashes and Stage17 profiles are unchanged. The new
[pin](stage18-dependency-pin.json) extends the original tree with exactly the HID routing
and NVS patches; original/core/SDK/NVS archive/config hashes are verified before/after.
Zero-fuzz patch application occurs only inside new disposable copies. HID-only, mutated,
wrong-version and partial trees fail closed. The additional native compile guard and
strong core status symbol prevent accidentally linking an unprotected core. Full link
verification checks actual initArduino disassembly/no erase call, getter/latch and
normal/safe flags in addition to Stage16/17 routing and ELF→BIN checks.

```sh
ED_CORE='/absolute/path/Arduino/data/packages/esp32/hardware/esp32/3.3.0'
ED_USER='/absolute/path/Arduino/user'
ED_CLI='/absolute/path/arduino-cli'
ED_NORMAL_CORE='/absolute/path/new-stage18-normal-isolation'
ED_NORMAL_BUILD='/absolute/path/new-stage18-normal-build'
ED_SAFE_CORE='/absolute/path/new-stage18-safe-isolation'
ED_SAFE_BUILD='/absolute/path/new-stage18-safe-build'
python3 tools/build_s3_patched.py --core-dir "$ED_CORE" --user-dir "$ED_USER" \
  --arduino-cli "$ED_CLI" --isolation-dir "$ED_NORMAL_CORE" --build-dir "$ED_NORMAL_BUILD"
python3 tools/build_s3_patched.py --core-dir "$ED_CORE" --user-dir "$ED_USER" \
  --arduino-cli "$ED_CLI" --isolation-dir "$ED_SAFE_CORE" --build-dir "$ED_SAFE_BUILD" --deployment-safe-start
ED_NORMAL_PATCHED="$ED_NORMAL_CORE/data/packages/esp32/hardware/esp32/3.3.0"
ED_SAFE_PATCHED="$ED_SAFE_CORE/data/packages/esp32/hardware/esp32/3.3.0"
python3 tests/stage18/run_tests.py --original-core "$ED_CORE" --patched-core "$ED_NORMAL_PATCHED" \
  --build-dir /absolute/path/new-nvs-tests --results /absolute/path/new-nvs-results.json
python3 tests/stage18/dependency_tests.py --original-core "$ED_CORE" --patched-core "$ED_NORMAL_PATCHED" \
  --build-dir "$ED_NORMAL_BUILD" --results /absolute/path/new-dependency-results.json
```

Existing suites remain applicable. On this branch Stage17 runner additionally requires
--upstream-core "$ED_CORE" to retain its historical original-core erase observation,
rather than falsely treating patched source as the old behavior. Its startup mock uses
an explicit successful core status; new Stage18 tests exercise the actual status hook.
Stage15 retains its exact baseline backend via --baseline-backend. Stage9 observations
remain separate. Run all original runners with RAM endpoints, not physical devices.

CPU240MHz/QIO80MHz/16MiB/custom dual740000 slots/PSRAMoff/USB-OTG TinyUSB/CDC and existing
MSC/DFU boot flags remain pinned. Macro EVILDUCK_VERIFIED_NVS_PRESERVATION=1 is supplied
only after dependency validation. Owner esptool4.12.0/Python3.8.10 remain appropriate
for separately authorized ROM reads; build-local esptool5.0 ELF conversion is not a
requirement to replace that owner environment. High Sierra CLI/compiler execution
is still unverified. Do not downgrade the core or change USB identity to bypass it.

New provisional non-owner binaries are in deployment/stage18. Stage17 artifacts remain
historical and unchanged. Neither owner original flash/sector backup nor external new
SPIFFS image is included. Manifests distinguish fixed Arduino auto-erase from remaining
SDK mutation risk. No padded merged image or physical writer is published.

Owner-file verification and checked-plan tools retain their known sizes/hashes, exact
NVS9000/5000 protection, old SPIFFS290000/170000→newE90000/160000 file-level safeguards,
app0 OTA initialization and both new application slots. A software-safe policy or
checked offline plan does not authorize migration; no owner files were supplied here.

Rollback: use the untouched Stage17 checkout in a separate worktree; discard only the
new explicitly disposable build/isolation directories when appropriate. No global
patch reversal/uninstall is required. Repository rollback is not physical recovery.
An original raw-image restore would overwrite current data and requires independent
owner authorization and backup review. No destructive commands are supplied here.
