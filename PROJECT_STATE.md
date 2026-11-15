# Project state

Current firmware guidance is in [Recovered Route B lineage](#recovered-route-b-lineage-current-firmware-guidance). Earlier milestone findings retain their original inspection scope and do not override it.

## Baseline and references

- Workflow baseline (before these documents): `bb20cbe8ebd2be3745bb028220f8c6f0d1c354bf`, branch `work`.
- [README.md](README.md): existing project reference for EvilDuck SD and S3 hardware, advertised features, and software requirements. Feature descriptions are not test evidence.
- [Script library guide](EvilDuckS3/scripts/README.txt): existing examples, upload procedures, and device paths; not a record of test outcomes.
- [TEST_MATRIX.md](TEST_MATRIX.md): compatibility and testing evidence ledger.

## Milestone 2 findings (preserved inspection scope)

The following findings describe the earlier bounded inspection. Milestone 3 attachment evidence and the current objective are recorded below; prior absence findings do not describe the new package.

## VERIFIED

- Repository documentation baseline inspected: `main` at `edadbdf422db19d4fbb305317913d8fb01973fc5` (repository identity only, not a firmware build or installed image).
- [README.md](README.md) advertises S3 script execution and stopping a running script. [Script library guide](EvilDuckS3/scripts/README.txt) describes examples and upload paths. These establish documentation content only, not executed tests or host compatibility.
- No supporting firmware result artifacts were located in the bounded inspection. This does not establish that testing never occurred. No firmware or physical hardware tests were performed for this change.

## PENDING REVIEW

- **Evidence pending reconciliation:** High Sierra 10.13.6 G01–G10 objectives and per-group results; DEFINE / INJECT_VAR / DEL and STOP observations; Caps Lock / keyboard LED return; USB observer / OS classification; build checksums and rollback identities. See [TEST_MATRIX.md](TEST_MATRIX.md) for individual gaps.
- Known blockers: missing historical result artifacts prevent verification of these leads. Firmware blockers and detailed compatibility remain unresolved; no specific defect is established by missing evidence.
- Physically installed firmware is **unknown**. A repository commit cannot establish the image installed on a device.

## UNVERIFIED/INCONCLUSIVE

- No individual G01–G10 PASS outcomes or DEFINE / INJECT_VAR / DEL / STOP behavior can be verified from the inspected references. Physical observations, offline tests, and conversational claims must remain separate.
- Caps Lock investigations remain unverified. EvilDuck HID output, macOS system-wide Caps Lock state, and a separate Razer keyboard's LED are distinct observations. Queued/completed USB callbacks alone do not establish host delivery.
- USB observer / OS classification remains inconclusive as a candidate historical finding, not an executed test recorded here. No OS detection implementation or support is established. Classification requires independent host evidence; any original independent-evidence gate must be retained when its record is supplied.
- No evidence-backed experimental state is recorded; example scripts and advertised features do not establish one.

## Evidence needed from owner

- Original G01–G10 objective definitions and per-group High Sierra 10.13.6 result artifacts, with build identity and physical host observations.
- Exact scripts and physical result captures for DEFINE / INJECT_VAR / DEL and STOP; separately, any offline test command, output, and tested revision.
- Caps Lock traces identifying EvilDuck HID output reports, macOS state observations, and the Razer device separately; include host-side delivery evidence and firmware identity.
- USB observer captures, classification notes, and the original independent-evidence gate with independent host identification.
- Build manifests/checksum receipts, exact branch/commit and rollback IDs, plus flash/install records tying an image to the physically tested device. No firmware identity is inferred here.

## Previous objective and next task (Milestone 2 provenance)

- Milestone 2: bounded historical evidence reconciliation, documentation only. The prior workflow objective is complete; its previous “next agreed task: none” is superseded by this milestone.
- Next step: owner supplies the specific missing artifacts above so historical outcomes can be indexed without repeating investigations.

## Milestone 3 owner evidence import

- Started from updated `main` at `970b7ced46f94a90dcbf9dc811dbffc91d74b3db` after PR #2 merged. Scope is the supplied package only; no broader history or compatibility reconciliation was performed.
- Both ZIP uploads are byte-identical (SHA-256 `8c92f205887e7a04eb330b6e749e5f0996266a8c905587ebf4540e1c52e482a3`). All 21 manifest entries match. Exact source filenames, SHA-256 references, build labels, OS limits and evidence types are indexed in [TEST_MATRIX.md](TEST_MATRIX.md#milestone-3-supplied-owner-evidence-bounded-reconciliation). Attachment persistence was pending at Milestone 3; Milestone 4 private preservation is recorded below.
- The duplicate fixed-message receipts count as one evidence item: device feedback reports a verified 17-byte message, with owner-reported iPhone view PASS. This supports a bounded interface LED return finding, not an independently demonstrated iPhone result or general macOS compatibility. The receipt explicitly records `global_caps_restoration_proven=false`.
- Device snapshots carry buildId `CAPS-STOP-TRACE-20261019-v1`; that label does not identify a binary or tested commit. Earlier LED captures show unknown or stale feedback; USB/HID completion counters do not establish host acceptance. Different boot markers and freshness limits are retained in the ledger.
- Supplied host logs record system-wide Caps flags and separate service-filtered input events. High Sierra appears in diagnostic headers, but 10.13.6 is not established by those records. No matching build/boot identity links host logs to device traces. Interface LED feedback, macOS-wide Caps state and a Razer keyboard LED remain separate.
- STOP remains inconclusive: captured terminal detail 1 is not decoded as cancellation, callback correlation is false, and the empty disabled trace cannot prove an outcome. No G01–G10, DEFINE, DEL, INJECT_VAR or OS classification PASS is established. No offline result is supplied.
- Still missing: original group definitions/results; command scripts and physical/offline results; correlated STOP cancellation evidence; Razer LED and global restoration evidence; independent OS/version/classification evidence and original gate; firmware checksums, tested commit/branch, rollback and install receipts. The earlier pending categories remain open, partially supplemented by the supplied logs.

## Previous objective and next task (Milestone 3 provenance)

- Milestone 3: bounded owner evidence import, documentation only. Deliver one PR targeting `main`, leave unmerged, with only PROJECT_STATE.md and TEST_MATRIX.md changed.
- This import supersedes the Milestone 2 next step above. No further task is agreed; missing evidence and attachment persistence remain recorded gaps, not authorization for new investigations.

## Milestone 4 private evidence preservation

- Started from `main` at `2d1f297d0b0ee5ab92e250463e44e6800d5ce4d8`, which includes merged PR #3. Following privacy review, the owner authorized original evidence storage only in the separate private [EvilDuck-Evidence repository](https://github.com/tyronecoe/EvilDuck-Evidence). Private visibility was independently confirmed before upload.
- Permanent directory: [m3-owner-2026-11-13](https://github.com/tyronecoe/EvilDuck-Evidence/tree/e3f81226ac5ce061bff5dcd52f8b0d6e619bdb8c/m3-owner-2026-11-13), commit `e3f81226ac5ce061bff5dcd52f8b0d6e619bdb8c`. It contains all 21 original files, the original checksum manifest, original ZIP and a provenance/limitations README. Original filenames and bytes are preserved.
- On 2026-11-14, retrieved files verified against all 21 supplied SHA-256 entries; the manifest and ZIP matched their previously recorded hashes. E01–E21 and manifest links in TEST_MATRIX.md point to that private commit and require access permission. No originals or redacted derivatives are published here.
- Integrity verification establishes byte preservation, not authenticity, firmware identity, installed image, host acceptance, compatibility or additional PASS outcomes. All earlier findings and missing evidence remain unchanged. No firmware operations or physical testing were performed.

## Previous objective and next task (Milestone 4 provenance)

- Milestone 4: private historical evidence storage verified; public changes are limited to PROJECT_STATE.md and TEST_MATRIX.md. Submit the documentation-only PR against `main` and leave unmerged for owner review.
- Repository owners must maintain private visibility and access controls. Missing behavioral evidence remains pending; no further investigation is authorized.

## Recovered Route B lineage (current firmware guidance)

Recorded 2026-11-14, starting from `main` at `2894a512d4f53987df3f568e513b0645ab7caae0`. Latest main is not the latest recoverable firmware development. The June 6, 2026 S3 source change on main describes the older interpreter only; later Route B development remains on unmerged branches. This correction supersedes the main-only firmware assessment, not the preserved historical evidence.

- **Current development baseline:** branch `routeb-admission-diagnostics-v1`, publication commit `2ad87593bfde79d854c03045a68fe70d2ac49f72`, firmware checkpoint `c9fd36c3e03b2d7ffa318b289398ff7dc1c9fd44`, build `ROUTEB-ADMISSION-DIAGNOSTICS-H1-v1`. Use its hash-pinned composed source/preparer chain; root firmware files or standalone Legacy execution are not substitutes. [Development report](https://github.com/tyronecoe/EvilDuck/blob/2ad87593bfde79d854c03045a68fe70d2ac49f72/docs/admission-diagnostics-report.md).
- **Newest package:** `evilduck-routeb-admission-diagnostics-h1-macos-review-v1.zip`, 5,614,647 bytes, SHA-256 `05fdff0cdb7a0d4336f8dc219c3a501cc7349c9200f95c2f54a36bb9cccffd81`; application 1,450,944 bytes, SHA-256 `fce91bca0774181a1be6bc691a1303d47f61caba49e979e89bfa678ef41f60f1`. Package checkpoint `0c799d9bb72447409c9f6c23b2f78edaaa849a9a`. The preceding lineage investigation independently matched downloaded ZIP/application hashes and ZIP CRC; integrity is not installation or hardware acceptance. Physical installation/acceptance remains **unverified**. [Published artifact reference](https://github.com/tyronecoe/EvilDuck/blob/2ad87593bfde79d854c03045a68fe70d2ac49f72/docs/admission-diagnostics-download.md).
- **Latest owner-accepted working return:** DEFINE package, build `ROUTEB-DEFINE-LABELS-H1-v1`, branch `routeb-define-labels-h1-review-v1`, publication `bdc8cbeea024ebb63f952da7fc4f39ac9e32fe29`, firmware checkpoint `5d9176dd15f722ffe20d219d33684da7461d1754`. Original ZIP 2,691,374 bytes, SHA-256 `b91946bec818616f35a469edd6c2efa525eea01276d238b42ed1b26dea3558ed`; application 1,438,048 bytes, SHA-256 `167cf5013cd4aa7c0823e5c7391ca9f6d400b7b99df6fe0e46085048fde91a30`. Three scoped DEFINE owner-reported passes are documented, not independent device readback or universal compatibility. [Owner evidence](https://github.com/tyronecoe/EvilDuck/blob/2ad87593bfde79d854c03045a68fe70d2ac49f72/docs/define-labels-owner-acceptance.md).
- **Last owner-reported installed image:** `ROUTEB-USB-ENUM-OBSERVER-H1-v2`, branch `routeb-usb-enum-observer-h1-review-v2`, report `10a0aa7685688d41ba474eae37bfa32f1647c86f`, firmware checkpoint `b075e551e07f7b15124bdad3caa564c614f78ba4`; application SHA-256 `b7ac50eebe6fb5e3d69d97f20004e1014c46fb116845e30864f56de5de6d384e`. The later [inconclusive closeout](https://github.com/tyronecoe/EvilDuck/blob/eb4c5d721e30893f7df908ac610d287d7541acf5/docs/usb-os-observer-v2-inconclusive-closeout.md) records owner installation/export evidence. This is not independent confirmation of the current physical installation. Current typing acceptance, installed-byte readback and any subsequent DEFINE return remain unknown.
- **STOP correction:** Route B already implements cooperative single-owner cancellation, prioritized HID cleanup, request-correlated status and quarantine/no replay after ambiguous failure. Withdraw the proposed STOP repair based on the obsolete main interpreter; it must not govern Route B development. Scoped owner STOP/recovery observations are recorded separately from source/software evidence. General host-wide release and precise physical latency remain unproven. The newest admission-diagnostics increment corrects request-owned error reporting; it does not introduce a new STOP implementation. [Composed compatibility and evidence boundaries](https://github.com/tyronecoe/EvilDuck/blob/2ad87593bfde79d854c03045a68fe70d2ac49f72/docs/routeb-current-compatibility.md).
- **Experimental and historical boundaries:** H1 INJECT_VAR is implemented and has scoped owner-reported observations; canonical Hak5 runtime encoding remains unresolved. USB observer v2 is capture-only and OS detection is closed as inconclusive, with no validated classifier. Do not restart it or repeat accepted historical tests. G01–G10 original definitions/results and build/host correlation gaps remain pending; later summaries do not retroactively establish PASS for the Milestone 3 attachments. Preserve all historical evidence and uncertainty in TEST_MATRIX.md.

### Recovery identities and limitations

- The nested original working DEFINE ZIP above is the working-return kit. Its own guarded install action is distinct from the outer package rollback action.
- The separate mandatory older source/text-v2 rollback application remains 1,413,200 bytes, SHA-256 `cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02`. It lacks later privacy/dashboard/editor repairs. Neither application-only recovery restores deleted scripts, historical settings or the entire device; preserve private backups and original packages. Package integrity does not prove physical recovery.
- Historical Caps STOP rollback remains `MAC-CAPS-TIMING-20261019-v1`, 1,397,968 bytes, SHA-256 `5e10009fd3e5a0a862b4f7bed1f7f28ba8464f7bb1066fd8091c6e01b2ed4a59`. Prior package commit `c18fff39e672164121783808e82420557bf9dc36`, ZIP SHA-256 `2f3b398e04f755c751b1ae4aa3602eec133a2e70c44c3fc1e72474d09f2ac77f`. Historical owner confirmation is not a current board readback. [Preserved rollback record](https://github.com/tyronecoe/EvilDuck/blob/0803937b9b552fe4b6e6cb6d1dd60f80f098449c/docs/caps-stop-rollback.md).

## Current objective and next task

- Correct only PROJECT_STATE.md and relevant TEST_MATRIX.md entries; submit one documentation-only PR against main and leave unmerged for owner review. No firmware integration, builds, regression suites, packages or physical operations are part of this correction.
- The Route B baseline above governs future firmware planning. No STOP implementation or further firmware task is authorized by this documentation correction. Maintain private evidence access controls and retain unresolved historical gaps.
