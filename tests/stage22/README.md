# Stage 22 tests

EXPERIMENTAL — REVIEW ONLY — NOT AUTHORIZED FOR FLASHING

run_tests.py executes the actual candidate gate/header and extracted patched
initArduino body with actual pinned plaintext ESP-IDF NVS source components and
production setup/loop/settings source. Partition descriptors, iterator/canonical
lookup, flash bus, USB/RTOS and services remain adapters. The SDK C initializer is
counted at the actual call boundary: unsafe metadata must have zero calls. Every case
checks byte-for-byte synthetic NVS preservation and no lower write/erase, plus 10,000
quiescent loop calls and one-shot repeat rejection. This is not complete target startup.

integration_tests.py verifies actual clean final ELF/binary/table/core provenance,
production/candidate rejection, original core identity and review-inventory fault
handling. Wrong profile, authorization, dependency pin, offset, hash, size and ELF
identity must fail. No physical API or owner backup is opened. Stage21 retains the
broader recovery/bypass cases and observations; they are rerun without relabeling.

Final exact results/names/assertions/stdout/stderr are in ../../docs/stage22-results.json.
ASan/UBSan applies to native probes; Python/ELF file checks are not sanitizer targets.
