# Stage 17 tests — software only

[Commands](../../docs/stage17-reproduction.md). Requires fresh normal and explicitly
safe-start patched-core builds; tests never access ports/devices or execute owner scripts.

Synthetic16MiB flash/sector and old/new SPIFFS fixtures use the exact recorded sizes,
geometry and seven filenames. Hash overrides exist only in Python test API calls and
must be labeled synthetic-test; owner CLI pins are immutable. Tests cover missing/
wrong/truncated evidence, corrupt tables/images, filesystem geometry, raw-size mismatch,
file/content preservation, capacity repack, invalid offsets/NVS/erase ranges, incorrect
OTA/coredump, rehashed bad artifacts, actual patched linked firmware, forged profile,
ELF/BIN mismatch, read-only plan generation, no-overwrite/failure-output and recovery
consistency. Fault injection uses disposable fixture copies, not owner backups or the
published clean artifacts. C++ tests compile the actual setup/loop against service mocks
under ASan/UBSan. Normal regression issues an autorun request to a no-execution stub;
no stored payload is opened/executed. Safe startup runs10000 quiescent loop iterations.

Two retained risks are OBSERVED rather than supported-feature passes: normal automatic
SPIFFS formatting and early Arduino NVS erase. Those observations intentionally remain
unresolved. Python predicates are counted once per acceptance/rejection check; internal
validation guards are not individually inflated into assertion totals. All prior
regression, allocation probes, Stage9 observations and Stage15 faults remain separate.
No physical boot/USB/storage/heap/task-stack behavior is proved by these tests.
