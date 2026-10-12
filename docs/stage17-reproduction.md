# Reproduce Stage 17 offline checks

Run from this branch. All build/output directories below must be new and external;
never use owner backup paths as output. No serial/flash/OTA commands are present.
Set existing verified paths; no global core install or patch is performed:

```sh
ED_CORE='/absolute/path/Arduino/data/packages/esp32/hardware/esp32/3.3.0'
ED_USER='/absolute/path/Arduino/user'
ED_CLI='/absolute/path/arduino-cli'
ED_NORMAL_CORE='/absolute/path/new-normal-isolation'
ED_NORMAL_BUILD='/absolute/path/new-normal-build'
ED_SAFE_CORE='/absolute/path/new-safe-isolation'
ED_SAFE_BUILD='/absolute/path/new-safe-build'
python3 tools/build_s3_patched.py --core-dir "$ED_CORE" --user-dir "$ED_USER" \
  --arduino-cli "$ED_CLI" --isolation-dir "$ED_NORMAL_CORE" --build-dir "$ED_NORMAL_BUILD"
python3 tools/build_s3_patched.py --core-dir "$ED_CORE" --user-dir "$ED_USER" \
  --arduino-cli "$ED_CLI" --isolation-dir "$ED_SAFE_CORE" --build-dir "$ED_SAFE_BUILD" \
  --deployment-safe-start
ED_NORMAL_PATCHED="$ED_NORMAL_CORE/data/packages/esp32/hardware/esp32/3.3.0"
ED_SAFE_PATCHED="$ED_SAFE_CORE/data/packages/esp32/hardware/esp32/3.3.0"
ED_MKSPIFFS="$ED_CORE/../../../tools/mkspiffs/0.2.3/mkspiffs"
python3 tests/stage17/run_tests.py --core-dir "$ED_SAFE_PATCHED" --normal-core "$ED_NORMAL_PATCHED" \
  --normal-build "$ED_NORMAL_BUILD" --safe-build "$ED_SAFE_BUILD" --results /tmp/stage17-results.json
```

Normal is the unchanged operating profile; safe is explicitly quiescent. Build reports,
flags, header/policy source, linked marker, ELF regeneration and hashes distinguish
both. Stage16 original/patched source pins and guards remain required. Actual source
bytes can be rebuilt from this branch; binary equality across build times/paths/OS is
not promised. Existing Stage1–16 runners remain applicable; Stage2 includes the five
Stage1 tests and historical language diagnostics, Stage2.5 requires an actual completed
build, Stage9 reports observations separately, Stage15 requires its exact baseline
backend via --baseline-backend for historical diagnostics, Stage16 uses the normal
patched core/build. See prior runner READMEs. All C++ targets use mocked endpoints.

## Owner local backups — verification, not physical access

```sh
ED_BACKUPS='/absolute/path/to/owner-backups'
wc -c "$ED_BACKUPS/evilduck-16m-backup.bin" "$ED_BACKUPS/partition-table-backup.bin" "$ED_BACKUPS/new-spiffs-0x160000.bin"
shasum -a 256 "$ED_BACKUPS/evilduck-16m-backup.bin" "$ED_BACKUPS/partition-table-backup.bin" "$ED_BACKUPS/new-spiffs-0x160000.bin"
python3 tools/deployment_preflight.py --core-dir "$ED_CORE" --backup-dir "$ED_BACKUPS" \
  --mkspiffs "$ED_MKSPIFFS" --output /absolute/path/new-owner-evidence.json
```

This checks known owner hashes, exact layouts, ESP images/checksums/digests, SPIFFS
geometry/listing/extraction, every filename/byte and capacity repack. It cannot establish
physical flash/security, NVS health or ROM recovery. Owner input files are never
modified. Source file contents are not printed or executed. No new SPIFFS replacement
is fabricated; temporary repacks are only capacity/content checks.

## Non-owner artifact inventory and checked plan

```sh
python3 tools/deployment_inventory.py --normal-core "$ED_NORMAL_PATCHED" --normal-build "$ED_NORMAL_BUILD" \
  --safe-core "$ED_SAFE_PATCHED" --safe-build "$ED_SAFE_BUILD" --output /absolute/path/new-provisional-artifacts
# Only after actual owner evidence passes; still REVIEW-ONLY, never authorization:
python3 tools/deployment_plan.py --core-dir "$ED_SAFE_PATCHED" --build-dir "$ED_SAFE_BUILD" \
  --backup-dir "$ED_BACKUPS" --mkspiffs "$ED_MKSPIFFS" --output /absolute/path/new-reviewed-plan
python3 tools/deployment_preflight.py --core-dir "$ED_SAFE_PATCHED" --backup-dir "$ED_BACKUPS" \
  --mkspiffs "$ED_MKSPIFFS" --plan-dir /absolute/path/new-reviewed-plan --build-dir "$ED_SAFE_BUILD" \
  --output /absolute/path/new-plan-verification.json
```

The provisional inventory explicitly lists missing owner evidence and external approved
SPIFFS. It is not a complete migration package. The checked-plan path fails before
output when owner evidence is missing/changed and copies the independently supplied
approved destination filesystem only after content validation. The underlying
s3_write_plan now uses evilduck-app.bin instead of the outdated stage4-app.bin label;
existing lower-assurance manifests still require Stage17 independent verification.

No helper executes physical writes or produces a full-chip writer/erase command.
NVS-range preservation is distinguished from unresolved pre-setup NVS runtime erase.
Normal application is not in the initial safe-profile write set. All first-boot and
recovery gates in [owner checklist](stage17-owner-checklist.md) remain mandatory.

## Artifact delivery and rollback

`deployment/stage17/` contains six generated, non-owner binary files and the provisional
inventory. These bytes/hashes are the reported cloud builds, not owner backup files.
It contains neither old full-flash data nor the external new SPIFFS image, no padded
merged image, and no physical writer. Source, build wrappers, tests and reports in this
branch support review/reproduction. Full ELF/object compilation evidence is recorded
by hash and was checked in the clean build; independent rerun needs a complete build,
not only this minimal binary directory. High Sierra CLI/compiler execution is unverified.

Rollback of repository preparation: keep the untouched Stage16 checkout/branch and
select it in a separate worktree; discard only explicitly created disposable build/
isolation directories when no longer needed. Do not modify/uninstall the global core.
Switching branches cannot roll back a physical device. Actual raw-flash recovery is a
separate destructive owner-reviewed operation described without executable commands
in the [checklist](stage17-owner-checklist.md). No Stage18 work is included.
