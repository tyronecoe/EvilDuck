# Project state

## Baseline and references

- Workflow baseline (before these documents): `bb20cbe8ebd2be3745bb028220f8c6f0d1c354bf`, branch `work`.
- [README.md](README.md): existing project reference for EvilDuck SD and S3 hardware, advertised features, and software requirements. Feature descriptions are not test evidence.
- [Script library guide](EvilDuckS3/scripts/README.txt): existing examples, upload procedures, and device paths; not a record of test outcomes.
- [TEST_MATRIX.md](TEST_MATRIX.md): compatibility and testing evidence ledger.

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

## Current objective and next task

- Milestone 2: bounded historical evidence reconciliation, documentation only. The prior workflow objective is complete; its previous “next agreed task: none” is superseded by this milestone.
- Next step: owner supplies the specific missing artifacts above so historical outcomes can be indexed without repeating investigations.
