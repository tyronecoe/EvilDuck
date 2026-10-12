# Stage 21 readiness: NO-GO for physical migration, application boot and OTA

| Gate | Current evidence / remaining requirement |
| --- | --- |
| Owner original backups | Owner locally reports expected three sizes/hashes matched; original app/partition checks PASS; no binary supplied/inspected by Codex |
| Owner NVS structure | Owner reports updated Stage20 compatible-within-verified-checks, zero findings; limited offline subset, not live SDK preservation |
| SPIFFS | Owner reports file-level roundtrip PASS; original290000/170000 differs from proposedE90000/160000; no raw relocation allowed |
| Arduino erase path | Stage18 patch retained, exact isolated source and final ELF verified; no whole-NVS erase/retry |
| SDK canonical readonly boundary | Source C API/partition/manager plus exact target guard bodies tested; target loader/getter/guard evidence supports mechanism |
| SDK logical recovery | May skip repair/ignore denial and return success; offline subset cannot certify every logical setting or future physical fault |
| SDK lower/alias paths | Exact main-flash global readonly callback rejects ordinary direct writes/erases and descriptor/pointer aliases; callback-disabled/changed-metadata observations remain separate; no whole-boot guarantee |
| Earlier startup | All36 ordinary constructors and24 system-init records inventoried per ELF; selected source/entry disassembly reviewed; full transitive/ROM/closed-source audit not established |
| Existing safe-start | Application quiescence retained and tested; SDK uses writable approved CSV before setup; not read-only first-boot protection |
| Experimental candidate | Design/test-only; transient flag table roundtrips with official tooling, production guards reject it; no third image/table published for deployment |
| Candidate early precondition | Future exact core/profile must reject missing/writable/wrong-range descriptor before calling initializer; not implemented here |
| Settings | Actual production load + real source API tested; checked saves retained, normal healthy operation unchanged; multi-key saves still non-atomic |
| Fresh artifact identity | Two clean builds with exact pinned patches/SDK/headers/config/compiler and ELF-to-bin checks; source/partition bytes identical to baseline |
| Installed physical table | Original owner-recorded table remains distinct; proposed layout/readonly flag must not be assumed installed |
| Current physical data/security/ROM recovery | Previous owner evidence retained; current freshness/cable/power/port/chip/table/recovery needs separate authorized checks |
| macOS10.13.6 | Owner offline tools successfully ran; new firmware toolchain and real USB/storage/timing behavior not validated here |
| Owner authorization | None for hardware operations in this stage; clean software evidence cannot grant it |

**GO:** review the preservation contract, dependency/ELF evidence and privacy-safe owner
findings. A separately approved next development milestone may design/test the explicit
pre-init gate and isolated candidate tooling, while continuing the early-writer audit.

**NO-GO:** physical migration, application boot or OTA. No physical commands, first-boot
arming mechanism, deployment package, or transition to writable operation is provided.

Before any later deployment review, preserve independently retained original16MiB and
4096-byte table backups, verify their exact identities and fresh private structural
evidence, retain the verified destinationSPIFFS image, establish ROM recovery, and
review exact bootloader/table/OTA/app0+app1/filesystem/coredump artifacts with NVS-excluded
erase/write ranges. No full-chip erase or padded merged normal migration image. The
current approved NVS range stays `0x9000..0xDFFF`.

The latest owner report concerns saved backups, not newly measured current device NVS.
Do not require public uploads of private flash/NVS/settings or substitute synthetic
fixtures as owner evidence. Original settings/autorun semantics need private review
before normal writable operation. Radio/calibration and storage writers remain disabled
in a quiescent candidate, but existing USB global registration/CDC startup can precede
application guards. Real High Sierra TextEdit, reconnect/lock feedback, storage integrity,
heap/task high-water and failure behavior remain future, separately authorized physical
acceptance cases. Stage22 has not begun.
