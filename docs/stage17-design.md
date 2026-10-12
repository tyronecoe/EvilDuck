# Stage 17 deployment preflight and first-boot contract

Baseline Stage16 fcffe4a1bb01d72a3a0176a2d8e738f3641db34f. This stage is offline
preparation, not authorization to modify the device. No new language/USB identity,
GPIO/button, storage personality or migration-layout behavior is introduced.

## Established evidence and source risks

Recorded installed table: NVS9000/5000, OTAE000/2000, app010000/140000,
app1150000/140000, SPIFFS290000/170000; no coredump. Approved proposed table:
NVS9000/5000, OTAE000/2000, app010000/740000, app1750000/740000,
SPIFFSE90000/160000, coredumpFF0000/10000. Neither16MiB physical capacity nor a
successful build means the proposed table is installed. Actual device checks remain
separate; owner-recorded backups have not been supplied here.

Normal setup actually initializes HID/locale/attackmode, calls storage::begin(),
installs examples, loads preserved `duck` NVS settings, starts CLI/web and, if enabled,
delays then requests the stored autorun script. Mount failure is ignored by setup;
SPIFFS.begin(true) may format an unmountable filesystem. Source selection can include
SD. script_library installation can write missing examples/marker. ATTACKMODE startup
resets requested storage off; USBMSC constructor still registers the class descriptor
with media_present=false. A host-visible descriptor is not a writable backing medium.
Normal CLI `autorun off` changes settings through the existing save path, but using it
is owner intervention and writes NVS; it is not a read-only check or action run here.

Core3.3.0 `cores/esp32/esp32-hal-misc.c` initArduino initializes NVS before setup.
On ESP_ERR_NVS_NO_FREE_PAGES / ESP_ERR_NVS_NEW_VERSION_FOUND it erases the NVS partition
and retries. This proven upstream behavior is **not fixed** by the application profile.
Do not infer runtime NVS preservation from a region-safe manifest. Original backups,
compatibility/error-policy review and recovery remain gates before any application boot.

## Explicit deployment-safe build

`--deployment-safe-start` on the isolated build wrapper enables exactly
EVILDUCK_DEPLOYMENT_SAFE_START=1. Header defaults0 and rejects values other than0/1.
Normal setup/loop behavior is unchanged when disabled; compiler removes the false
branch. The opt-in profile returns from setup after diagnostic initialization/logging,
then loop only yields. It never invokes application settings loading, filesystem/SD
mounting, example installation, HID initialization, ATTACKMODE activation, web/CLI
startup, script execution or execution schedulers. This prevents those EvilDuck paths
from formatting SPIFFS, running preserved autorun, writing storage or injecting keys.
No source script, button or live command can arm this quiescent profile.

USB/SDK and C++ global constructors still run. Arduino CDC-on-boot and the unchanged
HID/MSC descriptors may enumerate; this is **not** a new CDC-only personality, USB
detachment, physical bus safety proof or complete pre-setup side-effect prohibition.
USBMSC defaults media absent and the application never activates its backing image.
Existing callback/core limits remain. No PID/VID/descriptors are changed. Early core
NVS initialization remains a risk even here.

Arming requires a separately reviewed owner-controlled change to a normal-operation
firmware image after all deployment gates, including autorun policy, are satisfied.
There is intentionally no automatic OTA/web/button arm path in this profile. It cannot
serve as a file manager or normal keyboard interpreter. Preserve the original firmware
and recovery image; no normal-operation behavior is silently disabled in default builds.

## Read-only evidence and artifact checks

`deployment_preflight.py` requires exact owner filenames/sizes/hashes. It checks sector
consistency and original layout using Espressif's MD5/partition tool, original S3 image
segments/XOR checksums/appended SHA, valid recovery apps/bootloader, old/new SPIFFS
geometry and seven-file inventory, byte-for-byte contents, successful destination
repack/decode including metadata overhead, and unchanged source hashes afterward.
One unused erased original application slot is allowed; no valid recovery app is rejected.
Valid image serialization is not proof it boots. NVS bytes are hashed, not semantically
decoded or declared healthy. Geometry is4096block/256page, tested mkspiffs0.2.3 with
32-byte names/4-byte metadata/magic settings. No raw170000→160000 relocation.

The CLI never accepts arbitrary owner hash overrides. Synthetic test injection is
explicitly labeled, cannot claim owner evidence, and is not a hardware observation.
It never prints file contents, executes stored scripts or overwrites backup files.
Temporary offline extraction/repack is disposable and does not replace the approved
owner-supplied new filesystem image. Individual content hashes are derived from the
hash-bound original full backup because the owner's seven individual hashes were not
provided in this conversation.

Final firmware verification now also validates build headers/layout, actual startup
compiler flag, current startup body/policy copy, linked flash-rodata safe-start marker,
and exact ELF→BIN regeneration using pinned Arduino esptool elf2image settings. It uses
only local files, no serial APIs. objcopy dumps to explicit temporary output, never the
original ELF. Normal and safe artifacts are distinguished by actual compiled/linked
behavior, not an editable JSON boolean. Stage16 core/SDK hashes, guard, object/map and
single strong callback checks remain enforced. Successful compilation is software only.

## Plan validation and limits

`deployment_inventory.py` stages non-owner artifacts and a **provisional** seven-region
inventory; owner filesystem stays external. `deployment_plan.py` requires actual pinned
owner files and verified safe-start firmware before staging a complete REVIEW-ONLY plan.
It uses the separately verified approved new SPIFFS bytes, never raw old data or a guessed
replacement. `deployment_preflight.py` can independently reverify the complete plan.

Offsets, types, exact metadata/data sizes, both identical app images, CRC-valid app0
OTA initializer, newly erased coredump, bootloader/table hashes, owner filesystem hash,
file inventory, NVS protection and sector-rounded erase bounds are recomputed. Stored
misaligned/overlapping erase declarations are rejected rather than silently corrected.
No generic-address/full-chip writer exists. All output directories/files must be new.
Existing lower-assurance s3_write_plan remains REVIEW-ONLY and now uses stage-neutral
artifact names; Stage17 verification is required before using its output for review.

A checked plan remains migration_authorized=false and hardware_execution_supported=false.
NVS preservation in its result means planned regions only; nvs_runtime_guaranteed=false
records the separate early-core risk. It never changes the installed device, approves
migration, resets OTA metadata on hardware or confirms ROM recovery.
