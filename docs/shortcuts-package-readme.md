# EvilDuck transient-shortcut candidate — REVIEW ONLY

NOT AUTHORIZED FOR INSTALLATION, BOOT OR PHYSICAL TRIAL.
Source: 5c19f0dacb25960bda36a97f4ff871937a3cc9e7.
Application: 1,359,808 bytes, SHA-256
`de241287b972c24e510d3e8d22d888a17f13d1e972142559ba3df19f6195b41d`.
This is the retained reviewed build, not a rebuild. The supplied code review found
no blocker; independently reran 11 cases/292 assertions under ASan/UBSan but could
not independently establish leak-check results in its environment. The original
202-case software report and its separate T34 observation remain unchanged.

## Intended update method and gates

Proposal only: stop the application by owner-controlled ROM download mode, then
update ONLY app0 and app1 with the identical application BIN. No OTA workflow or
application-running write is provided. Both slots eliminate reliance on the
link-time app0 address as the only boot target. Before selecting even those ranges,
verify the actual installed partition table and OTA records through a separate
owner-authorized read-only procedure. This ZIP contains no device tool, serial
interface, flasher, credentials or executable flash commands.

The supported offline path is deliberately narrow: installed table must match
`expected-partitions.bin`, and installed OTA data must exactly match the pinned
Arduino app0 initializer (SHA in manifest). Other valid OTA states may exist;
this preflight does not decode or authorize them. A mismatch blocks this path for
review; it does not justify overwriting OTA metadata, migrating partitions or
resetting settings. The old pre-migration 0x140000 slots are incompatible.

After extracting into a trusted local directory on the Mac, the read-only check is:

```
python3 preflight.py --directory .
```

This verifies package bytes and reports installed metadata NOT_SUPPLIED, with NO
selected write ranges. Python3.8.10 is sufficient; no Arduino, pySerial, network,
compiler installation or Git is required. Native High Sierra execution of this
new helper has NOT been performed by Codex.

Once separate read-only acquisition is authorized and completed by the owner,
use the actual newly captured table sector and OTA metadata files locally:

```
python3 preflight.py --directory . --installed-table /path/to/current-table.bin --installed-otadata /path/to/current-otadata.bin
```

Do not use the included expected table as proof of the installed state. Input
files are not authenticated device reads and cannot establish freshness, device
identity, ROM accessibility or power/cable reliability. Output always retains
installation_authorized=false. No full backups, private NVS, settings, passwords
or scripts are required by this helper. Do not upload private evidence.

## Exact proposed application ranges

Both rows use application.bin, 1,359,808 bytes, with the application SHA above:

| Role | Start | Byte end (exclusive) | Sector erase end (exclusive) | Slot end |
|---|---:|---:|---:|---:|
| app0 | 0x10000 | 0x15BFC0 | 0x15C000 | 0x750000 |
| app1 | 0x750000 | 0x89BFC0 | 0x89C000 | 0xE90000 |

Sector size4096. Only the listed image footprints, NOT full slots or the chip.
The final64 B in each rounded sector are within the approved application region.
All non-application partitions and the bootloader/table are excluded. No SPIFFS
format/repack or NVS provisioning is part of this package. Existing private settings
and script files remain in place. This write-plan property is NOT runtime NVS
immutability: ordinary SDK NVS recovery/read/save side effects remain those of
the existing writable normal firmware, with prior no-auto-erase protections intact.

## Required separate owner review

Before physical authorization: confirm this downloaded archive hash against its
commit-pinned publication receipt; package preflight; exact device/chip/security
and16MiB state; current layout/OTA evidence; owner-controlled ROM recovery access;
compatible recovery/rollback files and offsets; stable power/cable; current settings
still valid and autorun disabled; no live script or writable MSC operation; review
an interruption/recovery plan. Stock firmware availability is OWNER CONFIRMED
externally, not a download/search blocker. Physical recovery is not newly verified.

ROM-mode interruption between application writes requires returning to ROM recovery;
do not assume a half-completed update is bootable. Preserve the working X package,
existing backup files and private settings unchanged. Never use a full initial
migration plan merely to replace this application. No automatic arming, replay,
startup payload, defaults change or transition from a read-only profile is added.

Only after separately approved installation and trial: use editor-only.duck once
in a NEW EMPTY disposable plain-text editor document, with explicit Route B selection
and review of editor capitalization/substitution settings. Intended text:

```
abZ
done
```

COMMAND a selects existing contents; never target an existing document. Local
clearSubmitted is not proof of host key release. The old X physical examples do
not validate this changed image. The earlier Functiondone/functiondone discrepancy
remains unresolved. Ordinary web Run still selects legacy unless Route B is explicit.

## Rollback reference

Existing X public ZIP (unchanged):
https://raw.githubusercontent.com/tyronecoe/EvilDuck/79c964d4f32a41f1295f2f96ebce8a42a8061c05/downloads/evilduck-stage28y-public.zip

4,837,000 B; SHA-256
`6cfe4b33bda853004f6af4672b553700e1756a6feeda9bd4579dd27cbf3a705f`.
X application SHA:
`a0cefdbb8ff9915e58b9142841b4c015dd738406c6861ef5f8e4c3f9105cffc4`.
This is a rollback artifact reference, not permission to replay that package's
original full migration or replace private NVS/filesystem. A rollback must receive
its own app-only range and state review. Do not substitute this BIN into its old manifest.

## Package identity and limitations

manifest.json binds public members, exact source commit, original linked receipt,
patch/source hashes, review, fixture and proposed ranges. expected-partitions.bin
is inspection evidence only, never a planned write. No bootloader, OTA, NVS,
filesystem, coredump initialization or merged flash image is included. ELF identity
is recorded, but the23MB ELF is not needed for this app-only review package.
Integrity hashes are not signatures: verify the externally published ZIP hash
before executing an extracted helper. Do not run a helper from an untrusted ZIP.
No claim of complete DuckyScript3.0 compatibility or physical release/USB-retirement
safety is made. No next language-development milestone is started.
