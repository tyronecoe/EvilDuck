# Stage 22 ordering and protection boundaries

**EXPERIMENTAL — REVIEW ONLY — NOT AUTHORIZED FOR FLASHING**

All three final ELFs have 24 system records and 36 ordinary constructor entries.
`stage22-startup-order.json` resolves the actual pinned record ABI: function pointer32,
cores uint16, stage uint16. Stage21's inventory `cores_mask` stores the whole trailing
32-bit word; it must **not** be interpreted as a pure core mask. Historical inventories
are preserved. The new decoded sequence contains **17 CORE** and **7 SECONDARY** hooks.
Official startup calls CORE hooks in ascending linked order, ordinary constructors in
**reverse** array order on Xtensa, then SECONDARY hooks, then starts the application.
This is source ordering plus native array evidence, not execution of complete startup.

| Path | Ordering / verified finding | Protection classification |
| --- | --- | --- |
| ROM / supplied bootloader | Pre-application table/app loading; previous exact bootloader evidence retained | Unverified transitive/physical; application gate cannot protect it |
| CPU startup / first16 CORE hooks | Before main application flash callback installation; heap/libc/efuse/VFS/timers etc | Unverified transitive/raw writers; no whole-boot guarantee |
| CORE init_flash | Last CORE hook; native root calls default-chip initialization and esp_flash_app_init | Verified direct roots; driver/callee closure conditionally protected, not fully executed |
| esp_flash_app_init | Native disassembly installs ordinary guards and calls esp_flash_app_enable_os_functions(default_chip) | Verified installation path; actual runtime success/unchanged callback remains a condition |
| Partition loading | Supported find() lazily loads/mmap-checks table, MD5, allocates canonical descriptors; source sets readonly bit from entry mask2 | Verified source/target loader evidence; conditional on valid installed table, callback and metadata integrity |
| 36 constructors | After CORE flash hook, before SECONDARY; inventories list every entry in execution order | Selected RAM/settings/USB/network entries inspected; all indirect/transitive effects unverified |
| SECONDARY coredump/security/coexist/etc | Seven hooks after constructors, before Arduino app_main | Ordinary main writes conditionally readonly-protected; complete raw/encryption/closed-source paths unverified |
| USB/CDC start | Arduino app_main starts USB/CDC before initArduino | Not USB-detached; global HID/MSC descriptors can exist. Application safe return does not undo early activity |
| HID feedback callback | Actual production receive path updates bounded RAM feedback under lock, no storage/USB/logging inside guard | Source verified; concurrency/physical transport not executed here |
| OTA verification | Actual initArduino can mark pending app valid or roll back before gate | OTADATA write/reboot, not NVS preservation; gate does not guard it or certify first-boot progression |
| Candidate gate | Reads exact raw table, validates canonical metadata/chip/readonly and policy callback before initializer | Verified source/native conditional call boundary; not retroactive, immutable metadata or callback authenticity |
| NVS C initializer / recovery / reads | Stage21 real source components and Stage22 integrated candidate execute on synthetic flash | Verified software readonly boundary for tested mutation paths; not whole Xtensa SDK/RTOS execution |
| setup/loop | Existing safe profile and failure latches suppress all application services, yield repeatedly | Production-source tests and native profile evidence; not physical USB silence |

New native disassemblies for app_main, initArduino, the gate, esp_flash_app_init,
esp_flash_init_default_chip, callback installation, main_flash_region_protected,
esp_partition_verify and nvs_flash_init are separately recorded. The linked candidate
branches to the initializer only when the gate returns zero; nonzero stores the error
and returns. Actual setup reads the protected startup status before the safe-start
return. Successful gate validation does not establish that no earlier NVS call happened.
No known NVS initializer is identified in the selected pre-gate roots, but a complete
callgraph including indirect and proprietary SDK code has not been proven.

The global readonly scan is installed before constructors and secondary hooks on the
verified direct path. It loads canonical metadata lazily before granting ordinary writes.
Thus those ordinary writes are conditionally protected by the *experimental installed
table*, even before the gate, if its callback is active and its table is correct. On a
writable/missing/wrong installed table, the later gate rejects initialization but cannot
reverse any earlier writer. These cases remain deployment blockers.

The ROM/custom-driver and changed/null callback routes from Stage21 remain excluded.
Readonly handles on writable partitions are still insufficient. SDK recovery success
can coexist with skipped/denied cleanup. Corrupt reads can return original errors.
Production profiles remain writable and multi-key settings saves remain non-atomic.
No SDK library, global installation, production table, USB identity or descriptor was
changed. Coredump and OTA metadata are separate regions, not falsely reported as NVS
writes. No current physical device measurements or owner files were obtained.
