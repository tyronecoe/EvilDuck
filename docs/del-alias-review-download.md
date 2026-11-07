# DEL alias review download

**PUBLISHED FOR REVIEW - NOT INSTALLED - DEL HARDWARE ACCEPTANCE PENDING**

[Download the existing verified Mac review ZIP](../downloads/evilduck-routeb-del-alias-h1-macos-review-v1.zip?raw=true).
Save it for the Intel Mac running macOS High Sierra 10.13.6. This publication
copies the completed local archive byte-for-byte; no firmware rebuild,
repackaging, installer change or physical operation is involved.

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| ZIP | 2,644,497 | `6dbc548c0e58714511c77f29ef50449f07d3ed94ef4422d09fe755e3f4b0f116` |
| Candidate application | 1,437,888 | `d1571be81619e464ee997d0ba8ebbf7e7b8a8b4252e4debc9d9144b9ebe6b379` |
| Exact older source/text-v2 rollback application | 1,413,200 | `cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02` |

Build ID, read from the actual manifest: `ROUTEB-DEL-ALIAS-H1-v1`.
Implementation and clean-build checkpoint:
`2e3efa295d46aef55b4d39af9cf3a9a40bb70422`.
Package checkpoint: `af579243978006fe4951236452b98719b351868c`.
Local completion/evidence checkpoint:
`c7a9098a43618b0082f652639054f63a32ebe3f1`.
The separate publication commit contains this unchanged ZIP and delivery files;
it does not replace the build's source identity.

The last owner-recorded installed firmware remains
`ROUTEB-PREVIOUS-COMMAND-REPEAT-v1`, source checkpoint
`820a575a45e5a4f644921d663a650110667a6ab2`, application
`13cec88262afdfa641eb0fb4927fe7903abf2863295344ff316418707ba49b7f`.
No DEL installation or physical acceptance is reported by this delivery.

## Review on High Sierra

Keep EvilDuck **unplugged**. Verify the downloaded archive before extraction:

```bash
shasum -a 256 evilduck-routeb-del-alias-h1-macos-review-v1.zip
```

Expect the complete ZIP hash above. Stop on mismatch. Extract into a new folder,
then, from that extracted folder, run only the existing offline checker:

```bash
python3 preflight.py --directory .
```

Expect exit 0, `package_integrity: PASS`, `installed_metadata: NOT_SUPPLIED`,
`plan_ready: false`, `selected_write_ranges: []`, `installation_authorized: false`
and `hardware_access: false`. Python 3.8 standard-library checking does not
contact the device or download dependencies. Preserve the existing High Sierra,
Bash 3.2 and esptool 4.12 instructions inside the ZIP; no new device path or
installation command is introduced here.

Read the [short two-trial owner procedure](del-alias-owner-check.md). Its
[DELETE control](del-alias-owner-fixtures/D01_DELETE_Control.txt) and
[DEL comparison](del-alias-owner-fixtures/D02_DEL_Alias.txt) are standalone,
harmless text fixtures outside the unchanged ZIP. Do not run them as part of
offline review. They replace no historical package file or accepted milestone.

## Evidence and limits

The [completed local delivery report](del-alias-release-delivery.md),
[structured results/source inventory](del-alias-release-results.json),
[grammar contract](del-alias-design.md) and
[primary spelling reference](del-alias-references.json) accompany the source
commits. The ZIP contains the actual build receipt, source attestation, selected
build inputs, native/web test receipts and focused DEL receipt for review.
Their completed run recorded **663 native cases / 28,173 assertions**, **86 web
groups / 1,518 assertions**, clean sanitizers and a clean target build with all
190 inherited release assertions. Package controls also passed. These are
**reused results from the completed implementation/build/package stage**;
delivery does not rerun or relabel them as new tests or physical acceptance.

The recorded measurements support **application size unchanged** and **static
RAM unchanged**; compiler program size increased 12 bytes. The candidate has its
own application hash, so this does not mean its application bytes are unchanged
from REPEAT. The publication does preserve the exact existing DEL ZIP and BIN.

The rollback is an older standalone application without later privacy/dashboard
fixes, not a full flash or filesystem restore. Existing recovery files remain
untouched. The installer retains its documented private full-flash backup before
final confirmation; such a backup can contain credentials, scripts and settings.

[OS_DETECT remains separately investigated and unsupported](os-fingerprinting-compatibility-investigation.md).
The pinned official extension at revision
`4fa639fd06972cd7efd9c48cc73136443f9cffb1` first compile-rejected at physical line
50, code 6, because its 27-byte DEFINE label exceeds the current 23-byte bound.
Other dependencies were identified through source inspection and separately
labelled compile-only fragments. No later whole-file failure is inferred past
that first rejection. Its counter/runtime and device-lifecycle contracts remain
unresolved; no detector, fabricated value, USB identity change or host probe is
included. H1 remains opt-in and experimental, with canonical Hak5 numeric
encoding unresolved.

This task publishes only a dedicated review branch. It does not merge, move tags,
change default/accepted branches, install firmware or perform hardware access,
serial operations, HID execution, flashing or OTA.
