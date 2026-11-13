# Compatibility and test evidence

Record only actual checks with an identifiable firmware/build, target OS (including version when known), scenario, result, evidence reference, evidence type, and caveat. Reference existing records rather than copying them. Separate physical checks, offline tests, and logs.

## Executed checks with available evidence

At the Milestone 2 inspection, no executed historical checks could be indexed from that bounded inspection. The supplied Milestone 3 records are indexed separately below. No firmware or physical hardware tests were performed for this documentation change.

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

## Milestone 3: supplied owner evidence (bounded reconciliation)

Baseline: updated `main` at `970b7ced46f94a90dcbf9dc811dbffc91d74b3db`, merge of PR #2. Earlier entries and pending categories above retain their original inspection provenance; “no artifacts located” describes that earlier inspection, not the newly supplied attachments.

Both uploaded `EvilDuck_M3_Evidence.zip` copies have SHA-256 `8c92f205887e7a04eb330b6e749e5f0996266a8c905587ebf4540e1c52e482a3`. All 21 file entries were checked against the supplied manifest. Hash matching establishes attachment integrity, not authenticity, firmware binary identity, or independent reproduction. No firmware tests, builds or physical checks were performed for this import; no offline test result is supplied.

References below point to owner attachments only. **Attachment persistence is pending**: no durable repository URL is available, and raw records are not committed. Source `buildId` values are self-reported diagnostic labels, not image checksums or install receipts. No OS is inherited between separate records merely from filenames or nearby dates.

| Firmware / build identity | Target OS | Scenario | Bounded result | Evidence references | Evidence type | Caveat |
| --- | --- | --- | --- | --- | --- | --- |
| `CAPS-STOP-TRACE-20261019-v1` | Not established; filename says mac, receipt has no OS/version | Fixed-message LED return, `EVILDUCK TEST 123` (17 bytes) | Device reports VERIFIED; owner reports iPhone view PASS | E01, E02 | Device snapshots + owner-reported observation | One receipt under two names, not two successes. Boot `74f39b50638bee97`, session 3; probe masks 1/3/2/0; final message snapshot has 408 accepted reports, integrity=true and ledEvidenceValid=true. Scope is this interface. `global_caps_restoration_proven=false`; restoration attempted is not restoration proven. No independent iPhone capture or OS identity. |
| `CAPS-STOP-TRACE-20261019-v1` | Not established | 10/21 LED before/end | INCONCLUSIVE for current LED/global Caps | E10, E11 | Device snapshots | Boot `9f7e374e4ddb478a`, session 3: 0 to 1 accepted report, last-known mask 2; end is stale and ledEvidenceValid=false. Caps down/up queued/completed each 1; completion is not host acceptance. |
| `CAPS-STOP-TRACE-20261019-v1` | Not established | A/B and burst LED snapshots | INCONCLUSIVE for current LED/global Caps | E13, E14, E15, E16, E17, E18 | Device snapshots | Boot `049cf0fd820dc14c`, session 3: A and B-before have no accepted report; B-end and both bursts retain one stale mask-2 report, ledEvidenceValid=false. Later repeated snapshots are not new LED arrivals; Caps queued/completed counts are 1 each. |
| `CAPS-STOP-TRACE-20261019-v1` | Not established | Bounded HID/STOP trace | INCONCLUSIVE for STOP cancellation/host delivery | E12, E19 | Device snapshots/trace + supplied explanatory note | Boot `049cf0fd820dc14c`, session 3. Trace seq 1–26 includes backend report-accepted, input-completed, led-accepted detail 2, and terminal detail 1; no decoded cancellation outcome or STOP request correlation is established. callbackRunCorrelation=false; callback run/op=0. Disabled empty trace is absence of captured events only. HTTP202 means requested, not terminal cancellation. |
| Not recorded | High Sierra (log header); 10.13.6 not established | System-wide Caps diagnostic | Observed host state changes; restoration INCONCLUSIVE | E03, E04, E08, E06 | Host logs | HID and COMBINED flags match in recorded samples; these are system-wide flags, not per-device LED states. First log records USB absent then Caps OFF; disconnect-named log records only USB present. No firmware build, causal restoration proof, or independent OS classification result. |
| Not recorded | Not independently established in these captures | Passive service-filtered Caps/modifier observation | Host input observations present; broader acceptance INCONCLUSIVE | E07, E09, E05 | Host logs | Diagnosis5 and observer record Caps usage 39 down/up for evilduck-303a:1001, separately from builtin-05ac:0259. hid.log contains built-in modifier observations; silence for EvilDuck is not proof of no USB events. No build/boot correlation to device traces; no Razer LED or OS classification proof. |
| Not recorded | Not established | Route B text captures | INCONCLUSIVE | E20, E21 | Owner-supplied text observation | A contains 111aBc222 / 333d444; B contains 555 / 123abc. No script, capture method, host/build attribution or explicit success criteria; cannot establish DEFINE, DEL, INJECT_VAR or a group PASS. |

### Attachment reference index

- **E01** — owner attachment: receipt.json; SHA-256 a06ed227c3e8aa2300df9ae66d1fd5f218ed7664a0c371ed6ee8fde5baf05ffd
- **E02** — owner attachment: evilduck_s3_mac_led_return_success_2026-10-21.json; SHA-256 a06ed227c3e8aa2300df9ae66d1fd5f218ed7664a0c371ed6ee8fde5baf05ffd
- **E03** — owner attachment: evilduck_caps_v4.log; SHA-256 dbd7695d5c597e0b13906a8b31b2e3e710403c60bd894fbb55529dcbff41d63e
- **E04** — owner attachment: v4.log; SHA-256 809118c73e849db2a667973197344dcbc5e8af164cfc866472592f706129f539
- **E05** — owner attachment: hid.log; SHA-256 7e7ddda5247ceb7bb4f620935aa8daa64684442283f92c21bdedbb86f1a62894
- **E06** — owner attachment: v4_disconnect.log; SHA-256 362f5ab231a1c2851a6af45b9691926cd3d87d82e8ce06f2f2def2a151ed05b9
- **E07** — owner attachment: evilduck_hid_diagnosis5.log; SHA-256 e4b4e5ef2d1ef4b994929d985ffa14b7045a9dd33cac04db3d68a060376ccd7d
- **E08** — owner attachment: evilduck_v4_diagnosis5.log; SHA-256 c9975d8f511f1a3b17f387c0d9602b1536e935ca21fcc52b191c6c839268c14c
- **E09** — owner attachment: evilduck_hid_observer.log; SHA-256 b2c5dccb80746092f93c8163ec593ad500061f96ccc34be583a80a7205402e23
- **E10** — owner attachment: 10:21 LED Report Begins.txt; SHA-256 401eb3e9372064b3e911df069fcb92e16871a876e978c958d5b053e0ab3f50e2
- **E11** — owner attachment: 10:21 LED Report Ends.txt; SHA-256 f08022498ad40804100e06d09d295735000355764b7e8e46ac721ecc34d878ab
- **E12** — owner attachment: Bounded HID:STOP trace(1).txt; SHA-256 f5f2339d7c35b48fa7eb4b759ce25864930d4dea83926975d8c9ed076777677a
- **E13** — owner attachment: A00_before_LED(1).txt; SHA-256 cab0874b925bfbbd136a4809b1805e490b0ea5198b26b27afa7bfcd6366a7896
- **E14** — owner attachment: A01_end_LED(1).txt; SHA-256 8494556bde599254951064e065268d53fa1f6c8fa98244deb7bb5d155954fb96
- **E15** — owner attachment: B00_before_LED(1).txt; SHA-256 6c98967062f51ac445ca449ccf0d7ccb48be1e9d256b496abc749652b0c619f4
- **E16** — owner attachment: B03_end_LED(1).txt; SHA-256 aebcadceea7ece2cfa9239c2dda9944c5122a3437099919ba93c651b648d6111
- **E17** — owner attachment: C_burst01_Led(1).txt; SHA-256 d499a04b3ff0a0f68d2635d5704676eb0f11b5323a3e135327e03a2ebb123527
- **E18** — owner attachment: C_burst02_LED(1).txt; SHA-256 596f166fe0927a4424a7eda64645519cbb239f3a9a800e2e47b8117e8e35df1c
- **E19** — owner attachment: Trace not observed(1).txt; SHA-256 0a6f6b40398e3453a4d38b225f3121dfe52c38139af5782c48f5fe690a29dc73
- **E20** — owner attachment: RouteB_Keyboard_Test_A.txt; SHA-256 b1e9819b0ed28aab609af6cdbfde6cf99a44c26fb32c44b0c83981964925bbbd
- **E21** — owner attachment: RouteB_Keyboard_Test_B.txt; SHA-256 3a393de6248f75c47d5cd7850a2140e3d94bd99ea74ae2490e9633fe10c48bde
- Manifest — owner attachment: MANIFEST_SHA256.txt; SHA-256 1f9c7baeefab3ea0f09b07304eb75b628054342a98511877f61e35a361743f91

### Remaining evidence gaps

G01–G10 definitions and original per-group results, DEFINE / DEL / INJECT_VAR scripts and results, decoded/correlated STOP cancellation evidence, separate offline commands/output/revision, Razer LED captures, global Caps restoration proof, independent OS/version evidence and the original classification gate remain pending. Host logs partially supply the requested observations but do not tie them to a firmware image. Binary checksums, exact tested commit/branch, rollback identities and flash/install receipts remain missing. No G01–G10, DEFINE, DEL, INJECT_VAR or OS classification PASS is added.
