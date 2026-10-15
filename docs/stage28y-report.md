# Stage28Y verified public X package and private workflow

**PUBLIC PACKAGE INTEGRITY: PASS offline. PRIVATE PROVISIONING WORKFLOW: PASS using
synthetic inputs. OWNER PRIVATE FINALIZATION: PENDING. RUNTIME/PHYSICAL DEPLOYMENT:
NOT AUTHORIZED / NOT EXECUTED.** No Stage28Z is started.

Clean exact starting base134b295deaebcb93f94beb63f2d46f102a7d6555; new branch
stage28y-verified-artifact-package.1379 historical paths/bytes/modes,235 frozen
Stage26 files and49 previous remote refs are independently checked and preserved.
All additions are new Y docs/tests. No firmware semantics, source, old pin, dependency,
partition, USB identity, profile, stored script or owner data changed.

## Public package

Filename: `evilduck-stage28y-public.zip`

Size: **4,837,000 bytes**

SHA-256: `6cfe4b33bda853004f6af4672b553700e1756a6feeda9bd4579dd27cbf3a705f`

Local location: `/workspace/outputs/evilduck-stage28y-public.zip`.
The current tool set has no attachment-upload/persistent file-publishing API. This
local file is NOT a confirmed downloadable ChatGPT attachment. No invented URL or
GitHub release is provided. Exact creation/retrieval alternatives are in reproduction:
export the retained bytes through an environment file-export facility if available,
or reproduce using reviewed branch/pinned X inputs on a compatible build host.

Package ID: `evilduck-stage28y-x134b295-public-v1`.
Versioned manifest/pin: stage28y-public-manifest.json. Includes six distinct images
for seven public roles, README, pinned partition generator source, public firmware/
tools/historical documentation/pins and three Y scripts. Full byte inventories are
in the manifest; no private NVS, binding/config/receipt or owner backups are included.
Extracted-copy validation and the extracted bundled validator both executed PASS.
ZIP is deterministic for tested Python/zlib inputs; two fresh copies matched exactly.
Unsigned integrity/checkout pins are not device authenticity or secure boot.

| Role | Offset | Bytes | Sector footprint [start,end) |
| --- | --- | ---: | --- |
| bootloader |0x0|20,256|0x0..0x5000|
| partitions |0x8000|3,072|0x8000..0x9000|
| otadata |0xE000|8,192|0xE000..0x10000|
| X app0 |0x10000|1,358,224|0x10000..0x15C000|
| identical X app1 |0x750000|1,358,224|0x750000..0x89C000|
| empty SPIFFS |0xE90000|1,441,792|0xE90000..0xFF0000|
| erased coredump |0xFF0000|65,536|0xFF0000..0x1000000|

All exact SHA-256 values are in the public manifest (root and bundled trusted copy).
The sole absent initial role is private fresh NVS0x9000/0x5000, deliberate replacement
requiring explicit later approval. No public range overlaps NVS; no whole-slot or
unlisted-gap erase is authorized. The actual proposed writable table, flags, subtypes,
canonical MD5, S3 images/segment checksums/appended hashes, DIO-safe80MHz/16MiB headers,
entry points, deterministic app0 metadata, empty SPIFFS and FF coredump were validated.
Actual bootloader/table are from exact X retained build, not guessed board defaults.

X app SHA `a0cefdbb8ff9915e58b9142841b4c015dd738406c6861ef5f8e4c3f9105cffc4`
and ELF SHA `9dd8a8ed952d1c62cbb7fb16447748cfd0628bf22d96f5aa856404c0df8ec54b`
match retained artifacts. No new target build was necessary or counted. Retained X
measurements remain program1,358,083B/BIN1,358,224B/RAM106,256B; free6,243,952B
(82.13374697%) per proposed0x740000 slot. No new runtime measurement. Image exceeds
historical0x140000 slots by47,504B; app-only OTA cannot migrate the old layout.

## Private workflow

New Y workflow preserves Stage24/25/26 typed schema, minimum12-byte password policy,
legacy AP rejection, autorun=false/empty path and empty filesystem. It binds private
NVS to the exact X public manifest hash, regenerates/compares the entire schema,
checks all public/private ranges together, and never changes Stage26's historical
pin. Swapping X into a Stage26 manifest is actually rejected in tests.

Credentials are local0600 config only, no argument values. Output0700/files0600,
private receipt0600 under owner-only parent, all outside repository/public package.
Errors suppress values/paths/tracebacks/subprocess output. Existing outputs/receipts
are never overwritten. No owner credentials were supplied or requested. Successful
synthetic finalization is not the owner's package or installation approval.

## Fresh focused verification

**41 PASS /0 FAIL /41 assertions**, named positive and expected-rejection cases in
results. Tests execute real artifact parsers, exact partition tool, real pinned NVS
generator and native mkspiffs. Coverage includes byte tamper, missing/wrong/mixed
image/profile/table, ranges/overlap/whole-slot footprint, readonly table, wrong chip,
invalid OTA/coredump, safe extraction/traversal/absolute/backslash/symlink rejection,
archive reproducibility, extracted validator, configuration types/lengths/legacy,
actual wrong-type/missing-key/autorun/path NVS generated with valid format, NVS size,
nonempty FS, X binding, private modes, public/private separation and sanitized CLI
errors. Public archive excludes synthetic private credentials/files.

Initial40-case development run passed; private/public containment guard and regression
were added, final41-case run supersedes it. No runtime suite inflation or old X pass
count reused. ASan/UBSan are NOT APPLICABLE to Python packaging; X native evidence
remains unchanged, not rerun. Native mkspiffs/generator calls are host utilities, not
physical storage/USB tests. Current Linux public/tool checks pass; High Sierra native
execution and device behavior are PENDING, not failed or presumed safe.

## Owner decisions and remaining gates

See owner-checklist and packaged README for exact offline host/private commands and
short recovery sheet. Remaining concrete items: selected host/OS/layout and local
non-device run; private fresh finalization; compatible specific recovery image/table/
offsets review; current-device/layout/security/ROM check plan; complete exact image/
range approval; first boot/idle authorization; explicitly authorized neutral-report
prepare/cancel; separately authorized tiny literal editor output and optional loss.

Original firmware availability is OWNER CONFIRMED: AVAILABLE EXTERNALLY, not a blocker.
No search/request/download or private-backup requirement was reintroduced. Specific
recovery compatibility and current ROM ability remain separate unperformed checks.

Y corrects X's ambiguous Delay-only preparation heading: NO VISIBLE TEXT EXPECTED
is not NO HID OUTPUT; synchronization/clearing can submit neutral reports. Idle USB
observations can include enumeration/traffic. No permission is inferred from package
completion. W/X controlled startup, explicit Route B selection/legacy default,
disabled upload/restart/WS mutation/async FS responses and permanent quarantine remain.
LOCAL_SCHEDULER_DONE/LOCAL_CLEARING_SUBMITTED are local, not delivery/retirement/host
release. Strict Route A and physical task/heap/stack/media/USB behavior remain unresolved.

No hardware connection/interrogation/serial/USB traffic, flash/erase/format/boot/OTA,
real HID, owner payload, release publication or installed dependency modification
occurred. Package readiness is not deployment authorization. Stop for owner review.

## Complete new-file inventory

- `docs/stage28y-integrity.json`
- `docs/stage28y-owner-checklist.md`
- `docs/stage28y-package-readme.md`
- `docs/stage28y-protected-refs.json`
- `docs/stage28y-public-manifest.json`
- `docs/stage28y-report.md`
- `docs/stage28y-reproduction.md`
- `docs/stage28y-results.json`
- `tests/stage28y/audit.py`
- `tests/stage28y/host_preflight.py`
- `tests/stage28y/package.py`
- `tests/stage28y/private.py`
- `tests/stage28y/run_tests.py`
