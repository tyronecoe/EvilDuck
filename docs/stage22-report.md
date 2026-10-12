# Stage 22 report: isolated read-only NVS pre-init candidate

**EXPERIMENTAL — REVIEW ONLY — NOT AUTHORIZED FOR FLASHING**

Baseline `516fb642b1126af55db909fcff856943935b7111`; branch
`stage22-readonly-nvs-preinit-gate`. The verified software boundary now rejects unsafe
metadata before the candidate's SDK initializer call. **Complete first-boot NVS
immutability remains unproven. Physical migration, application boot and OTA remain NO-GO.**

## Implemented and independently checked

An additive offline candidate builder prepares an isolated Arduino ESP32 3.3.0 copy
with existing Stage16 HID and Stage18 NVS patches, then applies the separately pinned
Stage22 gate/header pair. No installed core/SDK, production firmware source, partition
CSV, USB identity/descriptor, Arduino Micro source, prior report or deployment artifact
was changed. Both existing production profiles remain independently buildable.

The candidate snapshots existing safe-start source and uses a distinct experimental
CSV. Only NVS flag mask2 changes; all geometry stays exact. The gate checks raw table
bytes, complete canonical descriptor set, exact fields/default main chip, canonical
pointer identity and the installed main OS protection callback's denial. Missing,
writable, wrong, duplicate, conflicting or unsupported configurations fail before
`nvs_flash_init()`; no fallback/repair/erase/retry/settings/service activation exists.
The one-shot gate rejects repeated attempts. Native linked code contains a conditional
branch between gate and initializer; failed gate results store the error and return.
The candidate identifier and error/status accessors are retained in the final ELF.

See [design/contract](stage22-design.md), [startup analysis](stage22-startup-analysis.md),
[reproduction](stage22-reproduction.md), [readiness](stage22-readiness.md) and
[candidate pins](stage22-candidate-pin.json). The advanced callback structure is version-
pinned, **not a stable public SDK API**. Neither a pointer match nor a denial response
authenticates mutable metadata/callbacks.

## Experimental table

| Name | Type/subtype | Offset | Size | Flags |
| --- | --- | --- | --- | --- |
| nvs | data/nvs | 0x9000 | 0x5000 | readonly (2) |
| otadata | data/ota | 0xE000 | 0x2000 | 0 |
| app0 | app/ota_0 | 0x10000 | 0x740000 | 0 |
| app1 | app/ota_1 | 0x750000 | 0x740000 | 0 |
| spiffs | data/spiffs | 0xE90000 | 0x160000 | 0 |
| coredump | data/coredump | 0xFF0000 | 0x10000 | 0 |

Pinned official tooling verifies alignment, overlap, geometry, flag serialization and
MD5 roundtrip. Binary table SHA-256:
`a60cd4a103ec36ea102d964ee16a55980870d23d536b05390e622660c49d78cb`.
The expected3072 bytes are also compiled into the gate. A build match is not a claim
that the table is installed. Runtime checks reject old/writable metadata at the gate;
pre-gate writers are not retroactively protected. Production CSV remains writable and
its existing builders reject this experimental table and core.

## Executed verification

| Suite grouping | Result |
| --- | --- |
| Stage1–21 current suites, freshly rerun | 1220 PASS, zero unexpected FAIL; 637970 assertions |
| Stage22 actual gate/core/app + SDK source probes | 36 PASS, 0 FAIL; 737 assertions |
| Stage22 profile/dependency/final ELF/inventory faults | 22 PASS, 0 FAIL; 22 assertions |
| Current total | **1278 PASS, 0 unexpected FAIL; 638729 assertions** |
| Historical language diagnostics | 5 XPASS, separate; diagnostic sanity assertions included |
| Historical unpatched USB routing | 39 PASS, 6 expected XFAIL, 7 observations, separate |
| Stage9 compatibility observations | 79 matched, zero mismatch, separate |
| Stage21 readonly limitations | 11 observations, retained separately |

Historical Stage16/17/18/20 risks and NVS mutation/bypass observations remain classified
in the complete results. No expected fault was relabeled. All exact names, assertions,
stdout/stderr and classifications are in [stage22-results.json](stage22-results.json)
and the [test index](stage22-test-index.md). These include Stage20 blob follow-ups,
Stage21 SDK recovery/read-time/main-driver/alias cases, full previous runtime/storage/
HID/preprocessing/expression suites and offline migration guards.

Current native C++ tests used ASan/UBSan and completed cleanly. Historical malformed
upstream USB fault cases retain expected sanitizer failures. Python/ELF inspection is
not a sanitizer target. The gate probes execute actual selected plaintext SDK sources,
not the complete native Xtensa/RTOS/ROM implementation. Iterator/canonical lookup/bus/
service adapters and sequential Linux locks remain explicitly simulated. OOM/missing
iteration is a fault-injected API result, not a measured target allocator failure.
No actual owner backup, owner script, device storage or HID endpoint was used.

Two initial candidate attempts compiled but failed final verification because the
unused reason accessor was discarded. The corrected accessor/status linkage passed a
fresh clean build and final tests; these development verification failures are not
counted as passing builds or hidden in the final executed results.

## Clean build and resources

All builds use Arduino3.3.0, pinned SDK5.5/GCC14.2, 16MiB, two0x740000 slots, PSRAM
disabled, existing QIO80/240MHz/TinyUSB OTG/CDC profile. Actual compiler/ELF/bin/source,
core/SDK/table hashes are in the three resource/provenance records. Original core tree
and all prior dependency patches remain verified unchanged.

| Measurement | Normal | Production safe | Experimental readonly |
| --- | ---: | ---: | ---: |
| Compiler program bytes | 1329491 | 1065971 | 1069967 |
| Application binary bytes | 1329632 | 1066112 | 1070112 |
| Static RAM bytes | 82248 | 78280 | 78288 |
| Free bytes per OTA slot | 6272544 | 6536064 | 6532064 |
| Free percent per slot | 82.50985% | 85.97623% | 85.92361% |

Normal and production-safe measurements are unchanged from Stage21. Candidate versus
production-safe: +3996 program bytes, +4000 application bytes, +8 static RAM bytes.
Both existing profiles retain all455 normalized per-function compiler stack estimates.
Candidate gate estimate96B, initArduino48B, status/reason32B each; these exclude callees,
interrupts, SDK stacks and runtime high-water. Largest application estimate remains
1184B CLI command handler. Hardware heap/stack/timing measurements are unavailable.
The gate allocates no heap directly, but SDK loading/iteration allocate. Its one policy
query inherits the pinned scanner's potential one-iterator retention; repeated gate
calls cannot repeat it. Arbitrary subsequent SDK denied operations are not fixed.

Application SHA-256:

- Normal: `56cd4a12be80b2a33e600888ed79ab486c7d3209e095d1a4ec879df7c96e92aa`
- Production-safe: `44539ee93dfe4129a88e9cd6a74abaf6e37fe995e591a6b0843af89ea70ac4de`
- Experimental: `e8f3637dd8914bb5e6e3f85e87108f272df8dab25d214cb6cc43361a7fd56851`

Candidate core tree: `32aefca062d69b9f500bc2766a1901e493fd9d6c7ab3583b89e10f6ee3515e11`.
Candidate patch: `b7c0b29321edcb2a5098c8df584e0d47cae87a230d92b2ca805c76c1d255ce63`.
Exact original/patched headers, SDK archives/config, compiler and ELF identities are
recorded, not inferred from version labels. Three relevant installed SDK headers also
matched immutable official commit source byte-for-byte; this does not establish whole-
SDK source/binary equivalence.

## Artifacts and remaining blockers

The separately labeled review inventory records app/bin/ELF/bootloader/experimental
partition bytes, sizes and hashes. It is **not** a physical migration plan or authorized
package. No owner-specific backup or fabricated filesystem image is included. Normal
and safe production artifacts and earlier deployment directories are unchanged.

All three ELFs retain36 constructors and24 system records. Newly decoded ordering is
17 CORE, reverse36 constructors, 7 SECONDARY, then application. The installed main
callback direct path precedes constructors/secondary hooks, but full pre-callback,
transitive/closed-source, ROM and raw-driver coverage is not established. USB/CDC and
OTA hooks can precede the gate. OTADATA/coredump writes must not be confused with NVS.
Changing canonical metadata/callbacks after validation remains outside the guarantee.

Owner-reported private preflight/zero NVS findings/SPIFFS roundtrip are preserved as
owner evidence, not Codex binary inspection. No current live table, physical transport,
flash preservation, recovery or High Sierra firmware behavior was newly validated.
Normal writable operation and non-atomic multi-key saves remain unchanged. There is
no candidate transition/arming path.

**GO:** offline software/artifact/contract review. **NO-GO:** physical migration,
application boot and OTA. Recommend a separately reviewed Stage23 scanner ownership
fix investigation plus extended early-writer/callback audit. Stage23 was not started.
No hardware access, flash/erase/format/OTA, real HID or owner payload execution occurred.

## File inventory

[Every created file](stage22-files.md) is listed explicitly. No baseline tracked file is modified.
