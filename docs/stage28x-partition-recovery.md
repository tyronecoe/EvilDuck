# Stage28X partition, provisioning and recovery decision sheet

REVIEW ONLY — NO PHYSICAL OPERATION AUTHORIZED. Machine-readable artifact/range
inventory is stage28x-artifact-plan.json. This is an offline proposal, not a writer
or an approved installation package. No stock firmware search/download occurred.
**Original firmware availability: OWNER CONFIRMED: AVAILABLE EXTERNALLY.** Actual
restorable package compatibility and physical recovery remain separate pending checks.
Exact old firmware/settings/NVS/scripts/filesystem preservation is not required;
existing backups remain untouched and optional. Do not request private backup data.

| Region | Historical original offset/size | Proposed unchanged offset/size |
| --- | --- | --- |
| NVS |0x9000 /0x5000|0x9000 /0x5000|
| otadata |0xE000 /0x2000|0xE000 /0x2000|
| app0 |0x10000 /0x140000|0x10000 /0x740000|
| app1 |0x150000 /0x140000|0x750000 /0x740000|
| SPIFFS |0x290000 /0x170000|0xE90000 /0x160000|
| coredump |absent|0xFF0000 /0x10000|

The owner historically verified16MiB quad3.3V flash, ESP32-S3v0.2, security disabled
and ROM access. These are recorded owner facts, not new reads. Current installed
table/boot identity and future session ROM access need confirmation at an authorized
session; do not assume proposed geometry is installed. W/X application cannot fit
0x140000 original slots. Never recommend it there. App-only OTA cannot move a table,
SPIFFS, app1 or safely provision credentials. No in-place original-slot OTA is proposed.

Future complete-set decision: matching S3 bootloader at0, approved table at0x8000,
explicit fresh private NVS at0x9000, deterministic app0 otadata at0xE000, identical
reviewed X apps at0x10000/0x750000, verified empty new-size SPIFFS at0xE90000 and
new erased coredump region0xFF0000. Byte lengths/hashes/sector footprints are in the
plan. Application write footprints cover only rounded image bytes, not complete
slots. No footprint crosses a partition boundary; no unlisted gap is authorized.
NVS replacement is deliberate fresh provisioning, not SDK automatic recovery.
No normal migration path raw-copies0x170000 filesystem into0x160000. Old file
preservation is optional; any optional transfer must be file-level with capacity
and roundtrip checks. Public empty filesystem initially contains zero scripts.

Use existing `tools/stage26_private.py` privately/offline for explicit schema and
credential provisioning; it wraps reviewed Stage24/25 generators. Stage26 preparation
requires explicit SSID/AP/web credentials, passwords>=12 UTF-8 bytes, legacy AP
password rejected, autorun false/path empty, exact typed schema and empty filesystem
byte checks. Keep owner config, generated NVS and private receipts outside Git/logs.
No values were supplied or generated here. Its public manifest trust pin still
names Stage26 apps: **do not substitute X bytes into that pinned manifest**. A future
reviewed X package must regenerate/pin the complete artifact set and validate the
private NVS against it before an authorized install. This missing final package is
an explicit next-review item, not a reason to search for original firmware.

Controlled startup retains early NVS no-auto-erase, exact writable proposed-layout
check, typed settings/credential validation, autorun rejection, SPIFFS.begin(false),
no examples, required mount/AP success before operational readiness. SDK writable
NVS/Wi-Fi can still write valid fresh settings; this is not read-only firmware.
Deployment-safe and experimental readonly candidates remain distinct; neither arms
normal operation automatically. X boot does not select Route B. Expected initial
logs include CONTROLLED NORMAL START, W explicit-selection marker and X observational
marker only in instrumented build. Failure disables dependent services; it does not
repair or format storage. No successful boot is asserted from the ELF.

Recovery prerequisites: owner selects a verified compatible stock/recovery image set
(or reviewed reproducible build), its table/bootloader/offsets/flash mode+frequency,
exact hashes and security compatibility; confirms appropriate host tool execution,
ROM entry, data cable, power and port in a separately authorized session. Available
externally is not the same as a newly verified restorable package. The public
Stage26 quiescent fallback is an offline format-verified option with its own hash,
not physical recovery evidence. A stock table may differ and replace new user data;
loss is acceptable but must be explicitly included in the approved recovery plan.
Do not rely on failed web/AP/OTA to recover. Unexpected layout/image/security, failed
readback or partial operation =>stop and review a complete ROM-compatible set.
No full-chip erase, auto-format, guessed offsets or automatic fallback is prescribed.
No physical write/erase/restore commands are executed or embedded in these tools.

Owner choices/facts before next review: target host/OS/layout; recovery package and
its exact layout/offset validation (not its availability); current installed layout
confirmation plan; privately provisioned fresh credentials; exact approved X package
and complete initial write ranges; safe first-boot observation channel; telemetry
limits and separately scoped installation/boot/HID/loss permissions. macOS High
Sierra tool/runtime compatibility needs an actual local run; Linux compilation is
not proof the target compiler or browser/USB works on10.13.6.
