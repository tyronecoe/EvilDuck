# Stage 23 early-writer and callback audit

The three application ELFs retain17 CORE hooks,36 reverse-order ordinary constructors
and7 SECONDARY hooks. New bounded call inspection visits400 functions per application
(maxdepth3; cap reached), and108 in the supplied QIO80 bootloader. Unresolved indirect/
ROM calls remain; this is explicitly not complete transitive coverage. Selected exact
linked roots, source URLs/hashes and ELF identities are recorded. No target code ran.

Some Xtensa property metadata makes objdump print genuine function bytes as words.
Inspection-only copies remove `.xt.prop` after verifying every allocated runtime byte
and address is unchanged. Original ELFs are untouched. Such copies are temporary,
not deployment artifacts; changed load metadata makes them inappropriate for loading.
Original raw views and labeled inspection views are kept separately. ROM symbol aliases
and unresolved callbacks are not treated as definitive call identities or absent writes.

| Path | Classification | Evidence and protection boundary |
| --- | --- | --- |
| ROM / non-OS bootloader writes | Unsupported/unverified for NVS preservation | Nominal bootloader NON_OS source routes write/erase to ROM, outside application descriptor/callback protection. Actual bootloader has write/sector-erase routes; ROM/complete callers not executed |
| Bootloader factory data reset | Unsupported/unverified as a general route; no active matching helper identified in this supplied ELF | Source helper can erase named data including NVS, ignoring application readonly policy. `bootloader_common_erase_part_type_data` is absent from supplied bootloader symbols; not proof every erase path is absent |
| Bootloader OTA selection/rollback | Conditionally protected by correct metadata/range, not by application readonly gate | Native bootloader selection roots and official OTA source; expected writes are OTADATA at0xE000/0x2000. Wrong metadata/raw operations remain outside gate |
| Early default flash chip | Verified callback-absence interval; NVS-writing callers unverified | Actual initial no-OS configuration has region_protected=NULL; default-chip setup precedes esp_flash_app_enable_os_functions. Not a demonstrated automatic NVS write |
| CORE hooks preceding init_flash | Unsupported/unverified transitive | Heap/libc/efuse/VFS/etc roots inventoried; no complete callee/ROM audit. Later gate cannot protect earlier operations |
| init_flash → esp_flash_app_init | Conditionally protected | Actual linked roots install guard/OS callback. Pinned nominal source reports initialization errors; runtime success/stability not measured |
| Canonical partition loading | Conditionally protected | Exact loader source/unchanged native member sets mask2 readonly; mmap/MD5/allocates, no ordinary write identified in this loader. Metadata integrity and OOM behavior remain conditions |
| Ordinary main write/erase after installation | Verified protected within tested source/adapter boundary, conditional beyond it | Actual CHECK_WRITE_ADDRESS/callback/scanner; validated table and successful scan deny readonly NVS. Corrected scanner releases ownership. Full bus/driver/physical execution excluded |
| Scanner allocation/load failure | Verified permission-policy risk | Native exact iterator/scanner/callback bodies with injected failure return writable/ESP_OK for the synthetic safe NVS range. Not a claim physical flash accepted a write |
| Missing/replaced callback or changed canonical flag | Verified synthetic mutation risks; actual spontaneous occurrence unverified | Historical Stage21 fault cases; advanced exposed fields can be replaced, metadata is RAM. One-shot query does not guarantee later state |
| Constructors / secondary hooks | Conditionally protected for ordinary APIs; other paths unverified | All roots retained; partial bounded traversal. Mutable metadata, raw/ROM routes, dynamic callbacks and proprietary callees not certified |
| Coredump boot check | Conditionally protected; expected region is separate from NVS | Decoded native init finds coredump subtype3, records its range and calls image check. Nominal source read/check routines target coredump; panic/erase APIs can write its assigned0xFF0000/0x10000. Full panic/raw behavior not executed |
| USB CDC/TinyUSB before initArduino | Unsupported/unverified complete transport closure | Actual app_main starts CDC/USB before Arduino gate. Application HID/MSC backing remains uninitialized in safe candidate; descriptor registration and early tasks can exist |
| Arduino OTA verification before gate | Conditionally protected for correct OTADATA, not covered by gate | Native initArduino may mark valid or rollback/reboot before gate; no assumption these are NVS writes or that gate always runs |
| Stage22 gate and subsequent SDK initialization | Verified tested call boundary | Corrected candidate rejects unsafe metadata before NVS initializer; source integration preserves all36 gate cases. SDK successful recovery may skip/ignore denied repair; not health certification |
| Normal writable operation | Intentionally writable, with existing error/settings safeguards | Original SDK/archive/profile retained. Owner no longer requires old-data immutability; ordinary writes and non-atomic multi-key saves remain unchanged |

Main callback installation assigns the default main-chip hooks/context with no_protect
false. The readonly scan runs before the dangerous-write exemption; disabling dangerous
write protection does not remove that scan. Secondary-chip hooks may have null callbacks.
Exposed hook fields are advanced non-stable API, not authenticated metadata. No callback
replacement, canonical flag clearing or generic flash interception is installed here.

The source's ESP-TEE/ESP32-C6 read workaround includes a ROM dummy write, but its branch
is not the ESP32-S3 configuration. Status/QIO register writes during flash initialization
must not be confused with writes to NVS bytes. No assertion is made that every underlying
chip-driver operation is read-only. Application bootloader-named helper APIs can use the
ordinary guarded app driver; NON_OS bootloader implementations use ROM instead.

Under the owner addendum, exact legacy NVS/firmware/filesystem preservation is no longer
a mandatory future criterion. These findings still matter for reliable boot, bounded
resources, controlled approved write ranges and recoverability. No new authorization
or deployment command follows from that policy change. Physical migration/boot/OTA NO-GO.
