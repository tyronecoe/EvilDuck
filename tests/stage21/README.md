# Stage 21 production-source NVS and startup investigation

`run_tests.py` compiles complete pinned plaintext C API, lookup, partition manager,
handle, NVSPartition, Storage/PageManager/Page sources with synthetic flash/descriptors,
ROM CRC and actual Linux no-op lock branch. Five exact supporting target partition API
bodies are extracted with recorded hashes; write/raw/erase attempt recording wraps
symbol names only. Exact canonical region scan/main OS callback bodies are executed
with an iterator/driver-dispatch adapter; the complete SPI driver is not executed.
No installed source/library is modified. Native headers/config and
compiled archives are inspected independently; this is not executing Xtensa/RTOS/ROM.

Normal/safe integration targets additionally execute the exact patched `initArduino()`
body and real production settings.cpp/setup/loop. OTA/BT/USB tasks/global constructors
and other application services are not simulated end-to-end; their calls are spies.
Synthetic autorun is only a spy request, with no script source or HID execution.

Protection PASS checks assert full20KiB equality, no lower synthetic mutation and
original failure statuses where specified. The OBSERVED cases document successful
init with skipped/denied recovery, read cleanup despite read-only handles on writable partitions,
missing-callback/changed-canonical-metadata mutations and normal-profile service
activation despite readonly NVS. These are not supported compatibility claims.
Ordinary main direct/alias/pointer writes are rejected by the global region guard;
permissive adapter drafts did not demonstrate a default-main-driver bypass.
Preparation writes occur before snapshots and never touch owner files.

`integration_tests.py` validates transient flag-table serialization/production rejection,
source version/hashes and tamper refusal, native descriptor ABI/loader/getter/guard
evidence, bootloader entry identity, both final ELF profiles, constructor/system-init
array inventory, original owner-evidence boundaries and NO-GO status. It does not create
an experimental firmware or authorized partition artifact.

All outputs must be new external paths. Reproduction commands are in
`docs/stage21-reproduction.md`. ASan/UBSan applies to native source tests; Python/archive
inspection is not a sanitizer target. Historical diagnostic classifications remain in
separate baseline result groups. All individual names/assertions/outcomes are recorded
in `docs/stage21-results.json`. No physical USB/flash/filesystem access is performed.
