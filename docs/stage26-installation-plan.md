# Stage26 non-executable installation and recovery plan

REVIEW ONLY — NOT AUTHORIZED FOR FLASHING

**Original firmware: OWNER CONFIRMED — AVAILABLE EXTERNALLY.** Do not search for or
request it. Exact original firmware, settings, scripts and filesystem preservation is not
required. Leave existing backup files untouched. Physical recovery verification is separate.

The exact public files/ranges/hashes are in stage26-compatibility.md and the machine-readable
review/stage26-installation/manifest.json. Private NVS is the only missing initial image.
The full private receipt adds NVS at0x9000/0x5000 to those seven roles and checks all footprints.
This fresh replacement is an explicit future review item, not permission to bypass existing
preserved-NVS migration tools. No writer is implemented. No full-chip erase, padded merged
image or old-size SPIFFS relocation is part of this plan.

## Dependencies and conceptual ordering

1. Review the trusted branch/commit and artifact hashes, and create/verify private fresh NVS
   locally. Review every region, including the deliberate fresh NVS replacement. Select
   controlled-normal-start, not legacy normal or experimental readonly. Confirm owner
   authorization specifies the exact image set and allows first application boot.
2. Under a separately authorized physical session, enter ROM download mode and confirm the
   intended board/port, chip/revision,16MiB quad/3.3V flash, security state, cable/power and
   working recovery access before modifying anything. Previously supplied physical evidence
   remains historical evidence; it is not needlessly requested again in this offline stage.
3. Remain in ROM mode throughout the complete installation. Conceptually place bootloader,
   partition table, fresh NVS, OTA metadata, both identical controlled applications, empty
   SPIFFS and erased coredump state at their reviewed offsets. Do not boot a partial set.
   Individual transport writes may erase their rounded sectors; the manifest defines maximum
   allowed footprints. Any extra erase operation requires an explicit reviewed range.
4. Read back and verify every written image at its destination before leaving ROM mode.
   Verify the table sector, including expected FF padding beyond its3072-byte table if that
   padding is part of the approved operation. Check both app slots and deterministic app0
   metadata. No mismatched hash, incomplete image or interrupted session may be called complete.
5. First boot is a separate controlled acceptance step: no payloads, no stored autorun and no
   example installation. Confirm settings and filesystem mount succeeded, then test AP/web
   authentication without injecting keys. No automatic switch from readonly/safe to controlled
   exists. Later USB/TextEdit/SD checks need specific harmless physical-test authorization.

Allowed **planned byte ranges and sector footprints** are exactly those in the manifest,
plus fresh NVS [0x9000,0xE000) only after explicit approval. Untouched gaps include
[0x5000,0x8000), application-slot tails after the rounded application bytes and any other
unlisted region. Stop on wrong chip/size, unsupported security state, missing files/private
receipt, bad hash, wrong table/profile, changed offsets, out-of-range erases, unstable power,
ROM communication errors, failed readback or a critical startup diagnostic. Do not compensate
with a full-chip erase, automatic format, defaults or guessed images.

## Recovery choices

The newly built deployment-safe profile is verified offline against the same proposed table
and patched core. It skips application settings/services/HID/storage and has no auto-arming.
It is useful as a quiescent fallback, but has not demonstrated physical recovery or completely
flash-immutable SDK boot. Any future substitution into app0/app1 needs a separately reviewed
manifest and valid OTA selection; it is not silently interchangeable with the controlled image.

The owner already has stock firmware externally. Stock recovery is acceptable after its chosen
image set, matching table/offsets and boot compatibility are reviewed by the owner. No original
resource is requested here. Reverting to a stock layout may replace newly created settings/files;
that loss is acceptable. Original backups are optional, unmodified recovery resources.

ROM recovery requires access to the board's proven download mechanism, correct serial port,
data cable, stable power and usable esptool. Previously reported ROM access is valuable evidence;
physical recovery of this new candidate has not been executed. On interrupted installation,
remain/re-enter ROM and stop for a reviewed complete image set. On startup failure, preserve
error evidence and use ROM recovery under separate authorization. Do not rely on web/OTA or
Wi-Fi when configuration/storage failed. Successful build, offline format checks and possession
of stock files do not prove a newly installed board will boot.
