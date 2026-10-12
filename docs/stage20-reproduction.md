# Stage 20 reproduction and rollback

Stage19 reproduction's isolated build commands remain applicable; use fresh Stage20
normal/safe isolation and build paths. Arduino3.3.0/SDK/Stage16 HID/Stage18 NVS whole-tree
pins unchanged; never modify global core. Both firmware profiles clean-built with existing
16MiB table,PSRAMoff,USB-OTG/TinyUSB/CDC,CPU240/QIO80; no SDK rebuild or readonly flag.
Wrapper verifies compiled source/header/caller identity, checked persistence symbols in
normal ELF, early NVS guard/HID companion/profile, exact ELF->BIN and partition bounds.

```sh
ED_CORE='/absolute/path/to/Arduino/data/packages/esp32/hardware/esp32/3.3.0'
ED_USER='/absolute/path/to/Arduino/user'
ED_CLI='/absolute/path/to/arduino-cli'
ED_NORMAL_ISO='/absolute/path/new-stage20-normal-core'
ED_SAFE_ISO='/absolute/path/new-stage20-safe-core'
ED_NORMAL_BUILD='/absolute/path/new-stage20-normal-build'
ED_SAFE_BUILD='/absolute/path/new-stage20-safe-build'
python3 tools/build_s3_patched.py --core-dir "$ED_CORE" --user-dir "$ED_USER" \
 --arduino-cli "$ED_CLI" --isolation-dir "$ED_NORMAL_ISO" --build-dir "$ED_NORMAL_BUILD"
python3 tools/build_s3_patched.py --core-dir "$ED_CORE" --user-dir "$ED_USER" \
 --arduino-cli "$ED_CLI" --isolation-dir "$ED_SAFE_ISO" --build-dir "$ED_SAFE_BUILD" --deployment-safe-start
ED_NORMAL_CORE="$ED_NORMAL_ISO/data/packages/esp32/hardware/esp32/3.3.0"
ED_SAFE_CORE="$ED_SAFE_ISO/data/packages/esp32/hardware/esp32/3.3.0"
```
No upload/discovery/port access. Existing CLI/library/tool dependencies retained. Normal
and safe binaries are not interchangeable first-boot profiles; no automatic arming.
Readiness is not inferred from compiling. High Sierra actual tool execution unverified.

New test runners/source preparation: tests/stage20/README.md. Stage19 source/generator
pins remain unchanged; partition reference preparer fetches only immutable official
sources into a new external directory and checks exact SHA, never installs SDK replacements.
Descriptor offset check compiles actual installed S3 header; archive candidate guards
are inspected, not executed. SDK source tests use synthetic adapters. No owner files.

```sh
python3 tests/stage20/integration_tests.py --original-core "$ED_CORE" \
 --normal-core "$ED_NORMAL_CORE" --safe-core "$ED_SAFE_CORE" \
 --normal-build "$ED_NORMAL_BUILD" --safe-build "$ED_SAFE_BUILD" \
 --results /absolute/path/new-stage20-integration.json
python3 tools/analyze_s3_stack.py --build-dir "$ED_NORMAL_BUILD" --output /absolute/path/new-normal-stack.json
python3 tools/analyze_s3_stack.py --build-dir "$ED_SAFE_BUILD" --output /absolute/path/new-safe-stack.json
```
Compiler frame scope additionally includes cli.cpp/webserver.cpp; temporary objects don't
replace firmware/core. Per-function frame estimates don't measure runtime stack/heap.

All previous Stage1–19 runners executed: Stage2 contains five Stage1 regressions;
Stage3–14 actual mock runtimes, Stage9 observations separately; Stage2.5 requires actual
completed build + tested mkspiffs; Stage15 original-core diagnostics use exact original
Stage15 backend via --baseline-backend; Stage16 routing/dependency tests use protected
core/current normal ELF; Stage17 both profiles plus --upstream-core original preserve old
risk observations; Stage18 initialization/dependency guards; Stage19 source/settings,
structural/private and link tests. --help/READMEs specify each runner's external paths.
No old outcomes relabeled; Stage19 raw API stand-in adapts new setters/commit, shared CLI
mock checked-save switch defaults success; new tests inject errors explicitly.

Provisional non-owner inventory:
```sh
python3 tools/deployment_inventory.py --normal-core "$ED_NORMAL_CORE" --normal-build "$ED_NORMAL_BUILD" \
 --safe-core "$ED_SAFE_CORE" --safe-build "$ED_SAFE_BUILD" --output /absolute/path/new-stage20-inventory
```
Committed inventory adds owner-local evidence annotation/source fingerprint and explicit
readonly_nvs_policy_enabled=false. No actual owner backups/destinationSPIFFS supplied;
private local preflight/summary instructions in stage20-owner-inspection.md. Summary does
not reauthenticate input report or authorize migration. No flash writer/merged package.

Rollback of source preparation: keep Stage19 remote unchanged; select it separately and
discard only explicitly disposable Stage20 build/isolation/test outputs. Original global
core requires no undo. Source rollback does not restore physical flash. Future original
raw-image recovery overwrites live data and requires separate owner review/authorization,
correct device/security/ROM route and original-image verification; no destructive command
is supplied/executed. Physical migration/boot/OTA remain NO-GO; Stage21 not started.
