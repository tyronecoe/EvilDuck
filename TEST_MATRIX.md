# Compatibility and test evidence

Record only actual checks with an identifiable firmware/build, target OS (including version when known), scenario, result, evidence reference, evidence type, and caveat. Reference existing records rather than copying them. Separate physical checks, offline tests, and logs.

## Executed checks with available evidence

No executed historical checks can be indexed from the bounded inspection. No firmware or physical hardware tests were performed for this documentation change.

| Firmware / build identity | macOS / target OS | Scenario | Result | Evidence path/reference | Evidence type (physical/offline/log) | Caveat |
| --- | --- | --- | --- | --- | --- | --- |

## Pending historical reconciliation (not executed-test entries)

| Firmware / build identity | macOS / target OS | Candidate scenario | Reconciliation status | Evidence path/reference | Evidence type | Caveat / exact missing artifact |
| --- | --- | --- | --- | --- | --- | --- |
| Unknown | High Sierra 10.13.6 (requested lead) | G01–G10 objective groups | Pending reconciliation | No exact result artifacts located | Not established | Need original objective definitions and per-group physical results tied to a build; no individual PASS recorded. |
| Unknown | High Sierra 10.13.6 (requested lead; unverified) | DEFINE / INJECT_VAR / DEL | Pending reconciliation | No result artifacts located; script guide is not a result | Physical/offline provenance pending | Need exact scripts, host captures, and separate offline commands/output with revision. |
| Unknown | High Sierra 10.13.6 (requested lead; unverified) | STOP | Pending reconciliation | [README.md](README.md), “Web Interface Features,” advertises stopping a script only | Documentation only | Need physical observation and/or separate offline result with script and build identity. |
| Unknown | High Sierra 10.13.6 (requested lead; unverified) | Caps Lock / keyboard LED return | Pending reconciliation | No HID/host traces located | Not established | Need distinct EvilDuck HID output, macOS state, and Razer LED records. USB queued/completed callbacks do not prove host delivery. |
| Unknown | Not established | USB observer / OS classification | Pending reconciliation | No observer/classification record located | Not established | Historical classification remains inconclusive/unverified; need captures, independent host evidence, and original evidence gate. OS detection is not established as implemented or supported. |
| Unknown | Not established | Build, checksum, rollback, branch/commit, and installed image identities | Pending reconciliation | No firmware identity receipts located | Not established | Need exact build manifests/checksums, rollback IDs and branch/commit records; install evidence must link the tested device to the image. |

Statuses for executed checks:

- **PASS**: evidence supports success for the recorded scenario and environment.
- **FAIL**: evidence supports failure for the recorded scenario and environment.
- **INCONCLUSIVE**: an actual check has evidence that cannot establish an outcome.
- **NOT TESTED**: the specified check is explicitly known not to have been performed; do not infer this from missing evidence.

**Pending reconciliation** is a documentation status, not a test result. Missing repository evidence neither indicates a failed test nor proves that no testing occurred. README features and example scripts alone do not establish compatibility.

## Preserved baseline entry and correction

The original ledger contained: “Historical builds: identity pending | Not recorded | Historical scope pending | INCONCLUSIVE | Evidence pending reconciliation; no supporting results located in the limited documentation inspection.” Its original accompanying caveat stated that this was a documentation gap, not an executed check. It is retained here for provenance and corrected to **pending reconciliation**, outside the executed-check table; no historical outcome has been replaced.

## Evidence sources and inspection boundary

- Baseline: `main` at `edadbdf422db19d4fbb305317913d8fb01973fc5`; repository reference only, not firmware/build/install evidence.
- [PROJECT_STATE.md](PROJECT_STATE.md) and this ledger at that baseline: prior limited-inspection finding and original placeholder.
- [README.md](README.md): advertised S3 capabilities, including STOP; no result records.
- [EvilDuckS3/scripts/README.txt](EvilDuckS3/scripts/README.txt): example categories, upload procedures and paths; no result records.
- One targeted filename search for Markdown/text/log files and receipt, G01/G10, High Sierra, checksum, observer, Caps, and rollback names returned guides and example payloads, with no matching historical result artifacts. Payload contents, firmware source, and broad history were not audited. This is a bounded absence finding, not a claim about all GitHub branches, attachments, or past testing.

## Evidence needed from owner

Supply the original G01–G10 definitions/results; separate physical and offline DEFINE / INJECT_VAR / DEL / STOP records; device-specific Caps Lock/HID and host-delivery traces; observer captures and independent-evidence gate; and exact firmware manifests, checksums, rollback IDs, branch/commit and install receipts. Each result needs its tested build and OS version. See [PROJECT_STATE.md](PROJECT_STATE.md) for the compact request list.
