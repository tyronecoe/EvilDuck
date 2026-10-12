# Reproducing the Stage 16 isolated patched-core build

Compilation and local file verification only. Never add a port/upload command.
Retain pinned Arduino ESP32 3.3.0, libraries and the Stage2.5 16MiB profile.
No core downgrade, global patch, firmware upload or hardware discovery is required.

Set existing verified local paths (placeholders below are not new installs):

```sh
ED_CORE='/absolute/path/to/Arduino/data/packages/esp32/hardware/esp32/3.3.0'
ED_USER='/absolute/path/to/Arduino/user'
ED_CLI='/absolute/path/to/arduino-cli'
ED_ISOLATION='/absolute/path/to/new-stage16-core-copy'
ED_BUILD='/absolute/path/to/new-stage16-build'
python3 tools/build_s3_patched.py --core-dir "$ED_CORE" --user-dir "$ED_USER" \
  --isolation-dir "$ED_ISOLATION" --build-dir "$ED_BUILD" --arduino-cli "$ED_CLI"
```

Isolation must not already exist or overlap the repository/installed Arduino data/user
roots; build output must be external and empty. The script never downloads a core.
It verifies [pins](stage16-dependency-pin.json) and the nine
[original sources](stage15-upstream-sources.json), copies/patches only core source,
then runs the original clean 16MiB build checks and final link verifier. The source
fingerprint intentionally excludes generated installed.json catalog metadata. An
unexpected tree fails: do not adjust pins merely to make a different install pass.
Investigate against the verified Espressif release first. The release archive recorded
by Arduino is SHA256 `c8525462e47b37b726c211b71afada0fca5859ba748963e4d967131355716ba2`;
Stage16 uses already installed verified sources, not a new unverified replacement.

FQBN:

```text
esp32:esp32:esp32s3:USBMode=default,CDCOnBoot=cdc,FlashSize=16M,PartitionScheme=custom,FlashMode=qio,PSRAM=disabled,CPUFreq=240,MSCOnBoot=default,DFUOnBoot=default
```

240MHz; QIO80MHz boot, application image DIO as required by the existing Arduino
recipe; USB-OTG/TinyUSB, CDC enabled, boot MSC/DFU disabled, PSRAM disabled.
Custom CSV and dual0x740000 slots unchanged. `compiler.cpp.extra_flags` enables
EVILDUCK_VERIFIED_HID_ROUTING only after the resolved core passes verification.
Do not compile this companion in the ordinary unpatched IDE profile. The owner IDE
Hardware CDC/JTAG setting is different from this pinned application USB-OTG profile;
ROM Serial/JTAG recovery remains independent. No identity/descriptor edits are needed.

Outputs include s3-build-report.json/properties/log, compile_commands.json, ELF,
application/bootloader/partition binaries and stage16-link-provenance.json plus linked
routing disassembly. Arduino also generates a padded merged image; it is never used
for normal migration. Hash/configuration verification is not permission to upload.

High Sierra10.13.6/Darwin compiler execution remains unverified. Python3.8-compatible
helpers and local core installation do not prove the compiler/CLI minimum macOS
version. A separately performed offline smoke build is required; Linux-produced
artifacts remain reviewable without pretending Mac toolchain compatibility.

## Rollback without changing the owner's toolchain

Discard only the newly created external isolation/build directories after reviewing
that they contain no owner data, then select the untouched Stage15 branch in a separate
checkout. No uninstall, global core patch reversal or owner toolchain alteration is
needed. Existing main/Stage4–15 refs are preserved. This source rollback is not a
hardware restore procedure; no hardware migration has occurred in this task.

For the full mock-suite commands and results see [report](stage16-report.md) and
[tests](../tests/stage16/README.md). To reproduce Stage15 history on this branch,
extract the exact baseline backend with `git show` to a new temporary file and pass
`--baseline-backend`; the runner validates it against the baseline Git object.
