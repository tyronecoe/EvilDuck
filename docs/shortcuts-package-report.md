# Reviewed shortcut candidate — application-only package

Baseline `5c19f0dacb25960bda36a97f4ff871937a3cc9e7`, branch
`routeb-shortcuts-installation-package`. The owner's supplied code review reported
no blocking correctness defect and recommended concrete package preparation.
This follow-up changes packaging/documentation only. No firmware rebuild,
interpreter change, settings/schema change, core modification or device access.
The original reviewed candidate branch and all prior refs are preserved.

## Deliverable

`downloads/evilduck-shortcuts-5c19f0d-review.zip`

- ZIP bytes: **1,087,506**.
- ZIP SHA-256: **466edeac41cf33182136d5b4d02809a1f641fff5c17ae79e1a8fd3f46b314e0f**.
- Sixteen public flat members; exact inventory in [receipt](shortcuts-package-receipt.json).
- Existing retained application BIN, SHA
  `de241287b972c24e510d3e8d22d888a17f13d1e972142559ba3df19f6195b41d`,
  1,359,808 B. Independently rehashed the actual BIN/ELF/table/bootloader before
  packaging; all match the unchanged reviewed linked receipt.
- Includes source commit/build receipt, reviewed source delta/hash manifest,
  supplied code review, fixture, provenance/docs, expected table INSPECTION file,
  read-only Python3.8+ preflight and exact pinned Espressif partition parser/license.
- No private NVS, credentials, configurations, backup images, owner scripts,
  bootloader/OTA initialization/empty filesystem/coredump image, merged flash
  image or physical writer. The build receipt records the ELF identity; its23MB
  bytes are unnecessary for this application-only review package.

The archive is not a drop-in replacement for the old X full installation package.
Its changed application is bound to its own manifest/commit/build identity.
Existing startup W/X banners are not sufficient to identify this candidate.

## Planned update boundary

Future separately authorized ROM-mode app-only update of BOTH slots, identical
reviewed BIN. No live application writer/OTA, no table migration. Supplied table
must match the same reviewed writable 16MiB geometry. Supplied OTA bytes must
match the known app0 initializer exactly; other states require separate review.
A link-time app0 address alone never selects the update target.

| Role | Offset | Image bytes | End exclusive | Sector erase end exclusive |
|---|---:|---:|---:|---:|
| app0 | 0x10000 | 1,359,808 | 0x15BFC0 | 0x15C000 |
| app1 | 0x750000 | 1,359,808 | 0x89BFC0 | 0x89C000 |

The corresponding sector footprints are 0x14C000 B each, fully within their
0x740000 slots. Nothing selects an erase/write over bootloader, table, NVS,
otadata, SPIFFS or coredump; no full-slot/chip erase exists. Both slots contain
the same proposed bytes, but interrupted installation still needs ROM recovery
and must not be assumed bootable. The plan is NOT execution authorization.
Preservation of settings/files concerns proposed writes; it does not claim the
writable SDK performs immutable NVS reads/recovery at runtime.

See [package README and owner gates](shortcuts-package-readme.md) for the exact
read-only CLI, narrow supported OTA policy, recovery references, safe stopping
conditions and future editor-only trial. No executable flash commands are provided.

## Fresh verification

**25 PASS / 0 FAIL** focused Python package/fault tests;
[full cases](shortcuts-package-results.json). Also executed the actual bundled
CLI without device inputs, and with explicitly synthetic public table/OTA data.
Missing installed state yields no selected ranges; synthetic matching state
selects only the two application ranges and ALWAYS leaves authorization false.
No actual owner metadata/device state was inspected or inferred from those fixtures.

Tests include mutated/truncated BIN, wrong chip bytes, legacy/changed/truncated
partition table, read-only flag, unexpected trailer, missing/unreviewed/CRC-invalid
OTA records, altered source identity, authorization flag, NVS/oversize
range substitutions, full-slot erase, missing second slot, path injection,
unexpected private member, fixture integrity, ZIP CRC/member/byte equality and
read-only input-file identity. Exact-image hashes reject changed bytes before
parsing; these negative cases are not independent mutation coverage of every
parser branch. Actual pinned image/partition formats are checked on the positive
reviewed bytes; no new ESP parser compatibility claim is made.

Repeat packaging was byte-identical in this environment. Package builder verifies
the original protected-core tree against the reviewed receipt before copying
its partition parser. No global/toolchain files were changed. First preparation
attempt stopped at an unavailable SDK license-file path; the complete standard
Apache-2.0 license from the system common-license directory is included instead,
with the tool's original SPDX/copyright header intact. No failed verification was
bypassed. Python3.8 syntax compatibility checked; actual High Sierra native run
of this new helper remains unperformed. C++ sanitizers are not applicable to this
Python-only follow-up; the prior implementation and independent review outcomes
remain separate, unchanged historical evidence. No need to repeat firmware suites
or builds whose sources/dependencies are unchanged.

## PASS / BLOCKED / FAIL

**PASS — independently verified offline:** actual retained artifact hashes;
new package integrity; pinned parser/core identity; image/header/checksum/digest;
range bounds/data exclusion; fault tests; repeat archive equality; bundled CLI.
Source remains the reviewed5c19f0d build, not a new feature image.

**BLOCKED — not performed or not authorized:** actual installed table/OTA freshness
and device identity; supported active-slot evidence; present ROM recovery/power/
cable readiness; new-candidate installation and editor trial; host key-release and
USB-retirement proof. Existing owner X physical evidence remains qualified X-only
evidence. Stock firmware is OWNER CONFIRMED AVAILABLE EXTERNALLY; obtaining it is
not a blocker. Its selected recovery compatibility and physical recovery procedure
still need separate owner review. No private files are requested for public upload.

**FAIL:** no final package technical failure demonstrated. Unsafe fault fixtures
are correctly rejected; unsupported real-world OTA metadata would block this
narrow procedure for review rather than imply firmware/device failure.

**GO:** download, offline integrity checking and owner review of the concrete package.
**NO-GO:** installation/boot/OTA/new physical trial without separate authorization.
No HID output, flash/erase/format/OTA, installed-device change, automatic payload,
autorun/default change or next language milestone occurred.

## Reproduction and publication

Existing source/build receipts are inputs, not regenerated historical results:

```
python3 tests/shortcuts_package/package.py --directory /tmp/shortcut-public --build /workspace/tooling/shortcuts-dev/linked-verified/build --core /workspace/tooling/stage26-final-controlled-core/data/packages/esp32/hardware/esp32/3.3.0 --review /path/to/supplied-public-code-review.md --archive /tmp/evilduck-shortcuts-5c19f0d-review.zip
python3 tests/shortcuts_package/run_tests.py --directory /tmp/shortcut-public --archive /tmp/evilduck-shortcuts-5c19f0d-review.zip --ota-template review/stage26-installation/ota-app0.bin --results /tmp/shortcut-package-tests.json
python3 /tmp/shortcut-public/preflight.py --directory /tmp/shortcut-public
```

The builder uses the standard `/usr/share/common-licenses/Apache-2.0` license file
in this Linux environment; the extracted owner preflight has no such dependency.
Fresh output paths only. Actual package is `/workspace/tooling/shortcuts-package/public-release`;
reproduction archive `release-repeat.zip`; no owner inputs used.
Development environment Python3.12.14; package/preflight syntax compatible with3.8.
Download publication uses a new Git branch and actual ZIP bytes (not Git LFS),
never a release/tag or prior-branch overwrite. Final download verification and
remote-ref comparison are external publication receipts because a commit cannot
contain its own final hash. All pre-existing file bytes/modes are preserved;
the new source/archive inventory is in [integrity](shortcuts-package-integrity.json).
