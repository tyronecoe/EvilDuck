# Stage 23 report — iterator cleanup and early-writer audit

Baseline `89006f886fa30058a965e8e1883fb743d1683b70`; branch
`stage23-nvs-iterator-early-writer-audit`.

**The iterator ownership loss is confirmed and corrected in the isolated experimental
candidate. Physical migration, application boot and OTA remain NO-GO.**

The owner's addendum is incorporated: exact old firmware/NVS/settings/scripts
preservation is no longer mandatory for future deployment. Backups remain optional,
untouched recovery resources. Compatible verified recovery, correct geometry and image
identity, controlled write ranges, ROM access and explicit physical authorization remain
mandatory. See [owner policy](stage23-owner-policy.md) and [readiness](stage23-readiness.md).
No old preservation report or safeguard is rewritten or silently bypassed.

## Implementation and proof

The SDK scanner owns an allocated iterator but does not release it on either readonly
matching exit. Pinned source execution with real malloc/free proves accumulation;
shipped Xtensa code and20-byte target DWARF structure independently corroborate it.
The object has borrowed descriptor/label pointers and no retained lock/refcount.

For128 denied native scans:128 allocations,0 releases,128 retained objects (4096 host
payload bytes). With the correction:128 allocations,128 releases,0 retained. Four
immutable-table threads performing512 denials likewise balance after correction.
Host sizeof32 differs from target20; physical heap overhead, latency and high-water were
not measured. A separate historical LSan probe detects leaks; conservative roots can
make its unreachable count smaller than the independently recorded retained count.

The patch adds release immediately before the two false returns. No permission decision,
allocation, lock, loop, flash operation or SDK error is changed. Full analysis and exact
counts are in [iterator analysis](stage23-iterator-analysis.md) and the test results.

A compatible one-object SDK rebuild is independently established before adoption:

- Hash-verified unchanged target source reproduces all33 allocated runtime sections,
  normalized relocations, public symbols and target ABI of the shipped object.
- Corrected output differs only in scanner text/literals/relocations, required release
  reference and scanner size. The other archive member is byte-identical.
- Two fresh directories and a final guarded acceptance rebuild produce identical archive
  hashes. Prefix mapping normalizes assertion/debug paths; debug bytes need not match the
  shipped SDK. This is component runtime equivalence, not a complete SDK source rebuild.
- The experimental wrapper copies the SDK independently, changes only that archive,
  checks exact whole-SDK/core/pin identity, and verifies the final ELF/bin/map.
- Actual linked scanner calls SDK iterator release; actual gate/conditional branch still
  precedes NVS initialization. Stage16 HID routing, Stage18 original-error/no-auto-erase,
  Stage19–20 settings checks and Stage22 safe-start/gate/table are retained.

Both production profiles keep the original SDK/archive and behavior. Original Stage22
builder intentionally rejects the corrected dependency; a new explicit experimental
selector is required. No installed SDK/core, production source/table, USB identity,
settings schema, Arduino Micro code or previous artifact/report is modified. The
candidate retains Stage22's compiled quiescent identifier and has additional Stage23
SDK-cleanup provenance. No auto-arming or writable transition exists.

Key hashes:

| Item | SHA-256 |
| --- | --- |
| Original target source | 5917caadeb7a4a405c72eecbee939fdd153f50c32d9340699623da172f0f58d6 |
| Corrected target source | 99acce5481a72547beebb1063b3b6dedacc22378159d3c32dc6fb89604aea40d |
| Cleanup patch | 5c18697e62248153ec4cf443384f24086c7a216ad063e9e284d6a32882ccdd48 |
| Original partition archive | dd56cec7a28fb58246381dafddff33fcd9b46f56c9a863bdb8fb3441288d991d |
| Corrected partition archive | 5d1f3620100058b4a7b800dc4550af87ce4fd360a9cae3b1312712f7ef75c502 |
| Corrected SDK tree | cac0ba8fcd3bbebb42a19cf354aadd7206b622af7ef0ae0cf2a6e6a8f450ec07 |

Exact compiler/config/core/object/SDK hashes and commands are in stage23-sdk-pin.json,
the rebuild receipts and three profile provenance files. [Reproduction](stage23-reproduction.md)
never modifies global dependencies or invokes physical APIs. No compiled SDK archive,
private backup or device-specific image is committed.

## Executed tests

| Group | Results |
| --- | --- |
| Stage1–22, freshly rerun | 1278 current PASS,0 unexpected FAIL;638729 assertions |
| Stage23 allocator/scanner source | 15 PASS,18 observations,1 historical expected LSan XFAIL;1178 assertions |
| Corrected SDK protection/startup sources | 40 PASS,11 retained readonly observations;972 assertions |
| Corrected candidate pre-init gate | 36 PASS,0 FAIL;737 assertions |
| SDK/object/profile/ELF/startup integration | 19 PASS,0 FAIL;19 assertions |
| Current total | **1388 PASS,0 unexpected FAIL;641635 assertions** |

Historical language5 XPASS, upstream USB39 PASS/6 expected XFAIL/7 observations, Stage9
79 matched observations and previous NVS/bypass risks remain separate. The new allocator
suite's unpatched retained-resource observations and leak XFAIL are not compatibility
passes. Current/proposal C++ tests pass ASan/UBSan/LSan; expected historical unpatched
USB/leak sanitizer failures remain recorded, not relabeled. Exact names, statuses,
assertions, stdout/stderr and allocation counts are in [stage23-results.json](stage23-results.json).

All previous suites, Stage20 blob follow-ups and Stage22 original gate/profile checks
were executed. Those original Stage22 dependency tests use the retained unmodified
Stage22 fixture; corrected-source gate/protection probes and actual full corrected
firmware are independently checked. No old counts are reused as new execution evidence.
Source probes execute selected pinned SDK components, not the full Xtensa/RTOS/ROM.
Iterator loader/bus/transport/service and Linux lock adapters remain explicit. Protection
probes record blocked attempts/zero lower operations/unchanged synthetic flash; real
allocator ownership is tested in its separate source harness.

During development, the first runner had a local variable shadowing the os module;
fixing it enabled execution. A subsequent expected LSan exit preceded buffered stdout,
so explicit flushing corrected evidence capture. An absent bootloader init array required
handling missing entries in the audit. Final reruns have no unexpected failures; these
intermediate harness failures are not presented as successful verification.

## Builds and memory

All three clean builds use pinned Arduino ESP32 3.3.0, ESP-IDF5.5/GCC14.2, 16MiB custom
partitions, PSRAM disabled, existing QIO80/240MHz/USB-OTG/TinyUSB/CDC configuration.
Production flags remain writable; candidate NVS remains0x9000/0x5000, readonly mask2.
Experimental table SHA remains
`a60cd4a103ec36ea102d964ee16a55980870d23d536b05390e622660c49d78cb`.

| Measurement | Normal | Production-safe | Corrected experimental |
| --- | ---: | ---: | ---: |
| Compiler program bytes | 1329491 | 1065971 | 1069971 |
| Application binary bytes | 1329632 | 1066112 | 1070112 |
| Static RAM bytes | 82248 | 78280 | 78288 |
| Free OTA bytes per0x740000 slot | 6272544 | 6536064 | 6532064 |
| Free OTA percentage | 82.50985% | 85.97623% | 85.92361% |

Against Stage22: normal/safe measurements unchanged; candidate +4 compiler program bytes,
**0 binary growth and0 static-RAM growth**. All455 normal/safe and458 candidate normalized
application/core per-function estimates remain identical. Gate96B/initArduino48B;
corrected scanner compiler estimate32B, excluding callees/heap internals and runtime
high-water. Patch adds no allocation and removes matching-exit ownership loss. No
physical heap, latency, task-stack or stability measurement occurred.

Application hashes:

- Normal: `1668c499544e39f8b16b5b899c938bba6fbe9cc692c50253039a4e74bd1f630e`
- Production-safe: `806ad9a5391b48d5addf82ddce05f9cc5e9d52079201f94c4ea58d0e9e911ff6`
- Corrected experimental: `15e58e1f2fbe03673b66e0878638e30d46a71cd1c0b7db16fce97b6bc312c2b3`

The review-only inventory records exact ELF/BIN/bootloader/table sizes/hashes. It is
not an authorized migration package or physical write plan.

## Early writers and remaining blockers

[Startup/callback audit](stage23-startup-analysis.md) distinguishes protected, conditional,
risk and unverified routes. Bounded inspection covers400 functions per application and
108 supplied bootloader functions, with unresolved indirect/ROM calls and truncated
application traversal. Original ELFs stay intact; optional disassembler inspection copies
have verified unchanged runtime bytes/addresses and are not loadable artifacts.

Two important remaining facts:

1. The scanner still returns writable on allocation/lookup failure. Actual source tests
   reproduce an allowing policy result with otherwise readonly synthetic metadata.
   Cleanup does not introduce this risk or silently change its semantics.
2. The initial no-OS default chip has no region callback before app OS installation.
   Bootloader/ROM/raw writers do not gain protection from a later gate. Full early
   call closure, callback stability, mutable canonical metadata and physical behavior
   remain unverified.

Correct metadata distinguishes OTADATA0xE000/0x2000 and coredump0xFF0000/0x10000 from
NVS. Actual coredump init/check roots and bootloader selection routes are inspected;
absence of a named factory helper is not proof every raw erase path is absent.
No ordinary unexpected lower write is admitted by corrected successful-scan tests.
No claim of whole-device read-only or complete DuckyScript compatibility is made.

Under the revised owner priorities, exact old-data preservation is not a deployment
blocker. Verified recovery firmware/ROM readiness, correct images/geometry/approved write
ranges, safe first-boot/provisioning policy and explicit authorization still are.
Owner-reported backups/preflight/zero NVS findings remain owner evidence, not Codex files.
Existing non-atomic settings saves, current fresh-namespace failure latches and SPIFFS
format behavior need deliberate provisioning review, not automatic repair.

**GO:** offline software/artifact/recovery-build review. **NO-GO:** physical migration,
application boot or OTA. Recommend a separately reviewed Stage24 recovery-first image/
provisioning contract plus scanner failure-open and early callback investigation.
Stage24 has not started. No hardware access, flash/erase/format/OTA, real HID or stored
owner payload execution occurred. Backups and prior branches/artifacts are preserved.

## File inventory

[Every created file](stage23-files.md) is listed explicitly; all changes are additive.
