# Stage 21 native startup-path analysis

Baseline `7c4559132251340b03bcb68a3d66d04d1659e503`. Production source and installed
toolchain are unchanged. Exact dependencies are in Stage 18's pin and the new normal/safe
provenance records. New immutable source references are hash-pinned in
`stage21-reference-pin.json`; they are downloaded only as external reference files.
They do not replace any SDK library.

## Sequence and evidence levels

| Phase | Findings | Evidence / remaining gap |
| --- | --- | --- |
| ESP32-S3 ROM | Selects/loads bootloader; owner previously reported ROM download support | Owner report; ROM execution and every ROM flash operation not tested here |
| Supplied bootloader | Partition/app selection, image checks and configured OTA rollback precede application | Exact supplied QIO80 ELF hash/entry disassembly inspected, nominal official bootloader sources reviewed; not executed or a complete transitive audit |
| CPU/system startup | Flash, heap, libc and system initialization precede global constructors | Official `startup.c` ordering, actual linked arrays and archive entries; no native RTOS execution |
| System init hooks | Both ELFs contain 24 system-init records, including flash, security, coredump, coexistence, console/USJ and timer hooks | Every array address resolved/inventoried; transitive and closed-source callees are not fully audited |
| C/C++ constructors | Both ELFs contain 36 ordinary init-array entries; strings, filesystem wrappers, settings RAM, USB/HID/MSC, network and runtime objects initialize | Actual arrays and entry disassembly recorded; executing all constructors on Xtensa/physical device remains unverified |
| Arduino `app_main()` | TinyUSB CDC/USB startup occurs before `initArduino()`, followed by loop-task creation | Exact hash-verified core source ordering; actual final ELF/callback linkage verified; USB tasks/races not simulated by sequential startup tests |
| `initArduino()` | OTA verification can update OTA metadata before NVS; then patched NVS initializer captures original error, without erase/retry | Exact patched source and final linked disassembly; real source C NVS API integrated in native tests, while OTA/BT/RTOS branches remain outside that host probe |
| Partition lookup / NVS init | Table flag reaches descriptor before `NVSPartition` scanning; real C API invokes lookup/manager/storage | Source execution plus native loader/getter/partition-guard evidence; actual installed table must be checked separately |
| EvilDuck `setup()` | NVS error disables application. Safe-start returns before settings load and services. Normal validates settings before HID/filesystem/MSC/web/CLI/autorun | Actual production setup/loop and settings.cpp integrated with real C NVS API; application transports/services are spies |
| Safe loop / failures | Repeated loop calls remain quiescent, with no arming path; failure latch persists | Production-source tests and linked profile verification; not physical transport validation |

The linked inventories are `stage21-normal-startup-inventory.json` and
`stage21-safe-startup-inventory.json`. They enumerate addresses and direct named calls,
not a proof that every indirect/callee/ROM path is flash-write-free. The separate priority
constructor array is inventoried too. Its presence/absence is recorded rather than guessed.
An initialization symbol relating to PSRAM is not proof that PSRAM is enabled: the
unchanged, verified build profile explicitly disables PSRAM.

## Globals and USB quiescence

Production settings globals initialize RAM strings; NVS opens occur in `settings::load()`
or explicit saves, not those constructors. Inspected WiFiGeneric/NetworkManager
constructors are empty; radio/NVS-calibration behavior during later Wi-Fi startup is
outside the quiescent application path and is not claimed write-free.

Global `USBHIDKeyboard` construction registers the keyboard descriptor and initializes
the empty report. Global `USBMSC` construction registers MSC with media absent,
block count/size zero and null backing read/write callbacks. Its SDK writable boolean
initially defaults true. Thus **safe-start does not promise absent HID/MSC descriptors**
or no USB activity before `setup()`. It prevents EvilDuck HID initialization/injection
and backing-image activation; it is not proof of host-visible USB silence. Existing
Stage 16 output routing remains unchanged. No real reports were emitted in this work.

TinyUSB/CDC starts before the Arduino NVS check. Device-level feedback callbacks and
USB task concurrency therefore require separate verification; a downstream application
return cannot retroactively protect earlier tasks. No descriptor/VID/PID changes were
made to conceal these facts.

## Other early writes and NVS risk

`CONFIG_BOOTLOADER_APP_ROLLBACK_ENABLE` is enabled, as is its Arduino alias. The core's
weak `verifyRollbackLater()` returns false, so pending-verify OTA metadata may be marked
valid before NVS initialization. Official OTA source uses the OTA data partition; this
is **not** NVS activity. Bootloader rollback can also update OTA data. No real OTA action
was performed. Physical region correctness still depends on the actual table.

The pinned config enables flash coredump and boot checking. A linked system-init hook
calls coredump initialization before application startup. Its assigned proposed region
is `0xFF0000/0x10000`; this must not be confused with `0x9000/0x5000` NVS. The current
original device table has no coredump partition. Complete coredump/flash-driver transitive
behavior was not executed/certified; absence of an inspected NVS-specific system-init
name does not establish absence of a hidden NVS writer.

Flash encryption/security setup and bootloader flash writes are distinct from NVS
recovery. Owner reports encryption/secure boot disabled; no new hardware recheck occurred.
Nominal source, configuration and actual binary identities are recorded separately.
Source/binary byte equivalence for a complete SDK rebuild is not established.

## Candidate gate

The approved proposed table and currently installed original table have writable NVS.
The existing safe-start binary therefore does not stop SDK recovery writes before
setup. Changing only a firmware label or checking the flag after initialization is
insufficient. A future isolated candidate needs an early, fail-closed expected-descriptor
check plus an explicitly reviewed read-only table, and remaining early/raw-writer audit.
No such candidate is enabled here. Full first-boot byte immutability and physical
behavior remain unproven; migration/application boot/OTA remain NO-GO.
