# Stage28Y public X review package

REVIEW ONLY — NOT AUTHORIZED FOR FLASHING. Source candidate is exact Stage28X
134b295deaebcb93f94beb63f2d46f102a7d6555. App SHA-256 is
`a0cefdbb8ff9915e58b9142841b4c015dd738406c6861ef5f8e4c3f9105cffc4`.

Public package contains one shared app for both app slots, bootloader, partition
table, app0 OTA initializer, empty SPIFFS and erased coredump image. NVS is absent.
Bundled public source/tools/pins enable offline validation and private preparation;
no private credentials, NVS, backups, flasher or automatic installation is included.
Unsigned hashes bind bytes to a reviewed Git checkout; they are not authentication
of a device or a secure-boot signature.

Non-device inspection, from reviewed source checkout root:

```sh
python3 tests/stage28y/package.py extract --archive /path/to/evilduck-stage28y-public.zip --directory /path/to/fresh-extraction
python3 tests/stage28y/host_preflight.py --public /path/to/fresh-extraction
```

Alternatively the extracted validator is at source/tests/stage28y/package.py.
Its trusted pin is source/docs/stage28y-public-manifest.json. Independently compare
the archive/manifest hashes with the reviewed Git report before trusting bundled
code. Safe extractor rejects links, duplicate/absolute/traversal paths, unsupported
members and excessive expansion; use a fresh directory in an owner-controlled parent.
No adversarial concurrent mutation by another local process is within this boundary.

Public validation requires Python3.8+ standard library, no Arduino installation,
Git, compiler, cryptography, USB drivers or device access. If --mkspiffs is supplied,
its pinned geometry/build config is checked and the empty image decoded too.
Otherwise exact known-empty X image identity is checked; this is not a new local
filesystem decode. No download/install occurs. Native mkspiffs execution is a separate
host prerequisite. Linux checks do not establish macOS10.13.6 executable compatibility.

Private finalization requires existing pinned Arduino3.3.0 tool files, verified
ESP-IDF b66b5448 source subset, pinned esp_idf_nvs_partition_gen0.1.9 package source,
a compatible Python cryptography installation and mkspiffs0.2.3 native executable.
Use existing tools/nvs_source_prepare.py and nvs_generator_prepare.py --verify-only
against local paths; preparation downloads are separate explicit environment work.
Do not downgrade core or automatically install anything on the owner computer.

Prepare owner configuration PRIVATELY using local editor outside checkout/public
package, owner-only directory0700 and config file0600. Its exact JSON keys are
ssid, ap_password, web_password, all strings. Both passwords>=12 UTF-8 bytes;
AP<=63 bytes; SSID1..32 UTF-8 bytes; web<4000 bytes; no NUL/CR/LF. Legacy AP password
is rejected. Use strong distinct passwords. Never put credential values in command
arguments, chat, logs, Git or public archives. No default or repair is supplied.

Create an owner-only receipt parent (0700), then use paths only:

```sh
python3 tests/stage28y/private.py prepare --public /path/to/public-package --owner-config /private/path/config.json --private /private/path/new-images --core /path/to/esp32/3.3.0 --sdk /path/to/pinned-sdk-source --generator /path/to/pinned-generator --mkspiffs /path/to/native/mkspiffs --receipt /private/path/new-receipt.json
```

Use `finalize` instead of `prepare` to revalidate existing private images with a NEW
receipt path. Neither operation overwrites an existing receipt or initial directory.
Generation and finalization reproduce/compare the exact typed schema and empty FS,
verify X identity and all public/private ranges together. Successful receipt means
PRIVATE PACKAGE COMPLETE OFFLINE, not physical permission. Keep private data off Git
and never add it to the public ZIP. The original Stage26 manifest cannot accept X
application substitution. This workflow adds a separate Y binding without editing it.

All physical work remains separately authorized: current-device/layout checks;
exact write ranges and intentional fresh NVS/FS replacement; first boot/idle USB
observations; neutral-report prepare/cancel; tiny literal editor output; optional loss.
Delay-only means NO VISIBLE TEXT EXPECTED, not NO HID. Initial neutral synchronization
and clearing can submit reports. Idle/enumeration observations are not absence of USB
traffic. LOCAL_SCHEDULER_DONE and LOCAL_CLEARING_SUBMITTED remain local, not host ACK,
endpoint retirement or host key release. No automatic arming/normal transition exists.

Original firmware: OWNER CONFIRMED: AVAILABLE EXTERNALLY. Availability is not a blocker.
Actual recovery-package compatibility, ROM procedure/connection and target host remain
pending owner review. No stock search or backup access is needed. Stop here; Stage28Z
and hardware operations are not authorized by public or private package completion.
