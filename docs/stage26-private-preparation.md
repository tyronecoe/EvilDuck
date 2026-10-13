# Stage26 private provisioning and High Sierra workflow

REVIEW ONLY — NOT AUTHORIZED FOR FLASHING

Use the public prebuilt controlled BIN; local firmware compilation on High Sierra is optional.
Keep Python3.8.10 and esptool4.12.0, which previously worked for this owner. Stage26 does not
require esptool5 or a macOS upgrade. No esptool flash/erase/OTA commands are included.
Linux GCC14.2 builds do not prove High Sierra toolchain execution. Native mkspiffs availability
and Python cryptography import must work locally for private generation; these are local-tool
prerequisites, not requests for original firmware or private backups.

## Read-only public checks on macOS

Download the Stage26 repository branch ZIP from GitHub and extract it. From its root:

```sh
cd review/stage26-installation
shasum -a 256 -c SHA256SUMS.txt
wc -c *.bin
cd ../..
python3 --version
python3 -m esptool version
```

Hashes must match the trusted commit's manifest/pin, not an arbitrary edited copy. Public hash
checks require neither Arduino compilation nor owner files. Detailed offline validation uses
an installed Arduino3.3.0 core directory and a compatible mkspiffs0.2.3 executable:

```sh
python3 tools/stage26_installation.py --core-dir "$CORE_3_3_0" \
  --mkspiffs "$MK_SPIFFS" --review-dir review/stage26-installation
```

CORE_3_3_0 is the actual installed core path, not its parent package directory; MK_SPIFFS is
a macOS-compatible executable. The tool checks its compiled SPIFFS format settings. Paths
are owner-local; no Linux binary/tool path is assumed to exist on the Mac.

## Private generation

Use a private directory outside the Git checkout. Create a mode0600 local JSON file with
exactly these three keys: ssid, ap_password, web_password. Supply all values explicitly.
Do not put secrets in command arguments, Git, chat, reports or public test artifacts. No
example password is supplied. AP SSID is1..32 UTF-8 bytes; AP password12..63; web password
12..3999. Both passwords reject NUL/CR/LF; the public legacy AP password is rejected. The
12-byte preparation floor is stricter than Stage25's existing runtime minimums without changing
firmware semantics. Length checks cannot measure entropy: choose distinct strong random
passwords (at least16 ASCII characters recommended), not common/reused phrases.

Use the existing pinned source/generator preparation tools in fresh outside-checkout paths:

```sh
python3 tools/nvs_source_prepare.py --output "$PINNED_SDK_SOURCE"
python3 tools/nvs_generator_prepare.py --output "$PINNED_GENERATOR"
python3 -c 'import cryptography'
```

These download only checksum-pinned official SDK/generator sources, never stock EvilDuck
firmware; --verify-only checks existing copies. They do not patch global Arduino/SDK files.
The generator imports cryptography even for this plaintext mode. If the current Python cannot
import it, stop and review a Python3.8/High-Sierra-compatible isolated dependency; do not
blindly upgrade system Python or use unverified packages. Owner backups remain untouched.

After setting local paths to existing tools, private input and **new** output destinations:

```sh
python3 tools/stage26_private.py prepare --core-dir "$CORE_3_3_0" \
  --sdk-source "$PINNED_SDK_SOURCE" --generator-dir "$PINNED_GENERATOR" \
  --mkspiffs "$MK_SPIFFS" --owner-config "$PRIVATE_CONFIG_JSON" \
  --private-dir "$NEW_PRIVATE_IMAGES" --review-dir review/stage26-installation \
  --summary "$NEW_PRIVATE_RECEIPT"
```

The tool creates fresh-nvs.bin20480B and fresh-spiffs.bin1441792B outside the repository,
rechecks their inventory/structure, independently regenerates and byte-compares the NVS
against the explicit input, and requires its filesystem to equal the pinned empty public
image. The typed duck schema is unchanged: autorun false, script path empty, channel1,
hidden/stealth/LED-disable false, idleRGB0x28 and delay bounds0. Zero files/scripts. No owner
credentials are embedded in published binaries. Temporary plaintext CSV is deleted.
NVS is plaintext and contains secrets: retain it privately, with protected filesystem access.

Use operation verify instead of prepare to check existing outputs with a **new** summary path.
Never reuse an output directory, overwrite a receipt or delete backup files to make a retry work.
Interrupted generation is not accepted; missing inventory fails closed. Exact public pin
mismatch after recompilation requires fresh offline review, not editing hashes to bypass checks.

The private receipt includes fresh NVS size/hash and all eight planned roles/ranges, never
credential values. Share only a privacy-safe success/range/hash summary if desired, not NVS
or the config JSON. No owner credential request is necessary in this conversation. A PASS
is preparation, not authorization to write. Original-data preservation is not required.
