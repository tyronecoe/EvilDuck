# Stage 20 provisional non-owner artifacts

Six files + machine-readable inventory come from clean normal/safe protected builds.
Exact hashes/sizes/proposed offsets/erase ranges, source fingerprint and final ELF/core
provenance are recorded. Both newslots propose safe-app only; normal transition requires
separate review. Bootloader/table/OTAapp0 initializer/new erased coredump match existing
reviewed layout. NVS9000/5000 excluded from every proposed write/erase.

Owner original images/private NVS and supplied destinationSPIFFS are not included.
Owner confirms expected sizes/hashes locally; full structural/NVS review not done here.
External newSPIFFS is listed by expected hash/size only. File-level170000->160000 migration
and capacity/byte roundtrip required; raw relocation prohibited.

Readonly-NVS candidate source tests DO NOT enable a new table/profile. Inventory says
readonly_nvs_policy_enabled=false. Current writable SDK can mutate before setup and during
reads; safe-start is not strict immutability. No padded merged image or physical writer.
Migration, application boot and OTA remain NO-GO pending complete evidence, reviewed
preservation architecture, recovery and individual authorization. No Stage21 work.
