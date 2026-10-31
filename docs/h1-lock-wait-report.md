# H1 inherited lock-wait helper/fixture kit

**GO: review the helper-only kit. Physical inherited lock-wait acceptance remains PENDING OWNER.** No firmware, installer or native LED helper is included; no hardware access, real HID execution, flashing, OTA, settings reset, firmware change or rebuild occurred.

This task starts from the reviewed H1 closeout `29cbfae7974abccf513c6d7ff1b7faa5a3fc58c6`. The four scoped H1 owner passes remain closed, Request 2 remains inconclusive and the successful STOP request ID remains unknown. No repeated H1 trial is requested. This kit tests the inherited configurable lock-wait behavior on H1, not the separate older lock-wait binary; it does not establish canonical Hak5 encoding or change the default baseline.

## Download identity and contents

`evilduck-h1-inherited-lock-wait-high-sierra-v1.zip`: **24,304 bytes**, SHA-256:

```text
faf26f64212fad199e4f34b822f9ea4d684da99540ce2d5c3d50d35932d56211
```

The kit contains 13 flat regular files: README, acceptance sheet, exact H1-bound GET-only observer, mock observer tests, offline validator, source evidence, test receipt, license, manifest and four fixtures. Tools/docs source commit bound in the manifest: `c7531e2792e1f396ba07fc9c69313a21ae9d9949`. [Artifact inventory](h1-lock-wait-artifacts.json) records every member hash. The original H1 application package and its exact rollback remain unchanged; they are not copied into this kit.

Intended full build ID: **ROUTEB-INJECT-VAR-H1-EXPERIMENTAL-v1**; intended app **1,414,080 bytes**, SHA-256 `8a48f3f208165466e579f76a35fb7898fbaf1188e746ca3a0d60e99c576b0ecd`. Mandatory accepted source/text-v2 rollback remains **1,413,200 bytes**, SHA-256 `cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02`. The original public package's application and rollback members were rehashed offline. A build-ID response alone is not image-byte attestation; older installation receipts are not H1 evidence.

## Actual composition and observer changes

Ten inspected generated H1 source files were checked against the unchanged final H1 link receipt's source inventory. [Source evidence](h1-lock-wait-source-evidence.json) records hashes and exact source references. GET `/caps-timing` reports the full build name under authenticated execution synchronization. GET `/status` captures typed Route B status and the device millis timestamp coherently under the same mutex. Its raw response includes private fields, so the observer retains a strict execution-field whitelist and never logs raw response bodies.

The historical `tests/lock_wait_timeout/observe_wait.py` and its tests remain unchanged. The new `tests/h1_lock_wait/observe_wait.py` keeps header authentication, redirect refusal, GET-only path allowlist, size/attempt bounds and fail-closed HTTP/network behavior. It verifies the exact full H1 ID, not a prefix, and adds narrow source-backed safeguards:

- Actual phase range is 0–8; quarantine is **8**, not the historical observer's terminal check for 9. Quarantine ends UNVERIFIED, never as a successful completion.
- Idle preflight must also be nonwaiting. The actual entered request must be greater than the preflight request; no `old+1` prediction is made.
- Capture progression begins at the idle preflight timestamp. Duplicates provide no new waiting evidence; backward/half-range ambiguity fails closed, while normal uint32 wrap is accepted.
- Waiting metadata must be owned/Running6/CAPS_CHANGE5, with a nonfuture modular start. Session change is rejected before a matched capture is emitted. Session zero remains allowed and nonwaiting snapshots may retain old wait metadata, as actual firmware permits.
- If a private password prompt is unavailable, the observer refuses **before** getpass's echoing fallback can read a credential. Interactive Terminal use is documented.

No Start, STOP, upload, setting, LED or HID action exists in this observer. READY is an identity/idle preflight, not permission or automatic arming. Control+C stops observation only. Passwords are prompted privately and sent in `X-Duck-Password`; never in arguments or URLs. Error logs use reviewed generic codes. The known local HTTP AP is unencrypted; no network confidentiality or secure memory erasure is claimed.

Polling includes a 250 ms pause between attempts; request duration adds to that interval. Each GET has a two-second **socket-inactivity** timeout, not a hard total deadline. A slow partial response can outlive the observation window; a late completed response is rejected. Fixed call bounds remain, but no hard wall-time guarantee is invented. Capture/clock checks do not authenticate complete boot continuity or prove host-global state. Matching terminal exit0 still means OWNER_REVIEW_REQUIRED, not an automatic physical PASS.

## Fresh focused checks

| Executed final group | PASS | FAIL |
|---|---:|---:|
| Mock observer tests | 46 | 0 |
| Package/manifest/integrity checks | 31 | 0 |

These **77 final checks** cover exact/clipped/wrong build identity, authentication/contention/network errors, private-field omission, old/wrong/replaced request IDs, duplicate/stale/ambiguous/wrapped captures, missing/malformed fields, session changes, future wait starts, late responses, quarantine and other terminal reasons, Ctrl+C/no actions, echo-fallback refusal, fixture identity, tampering, exact ZIP inventory, Python 3.8 grammar, Bash syntax and deterministic repackaging. All HTTP/device responses are mocks; no real firmware/device dispatcher was executed.

The initial observer run was **44 PASS / 1 error**: its fake client treated KeyboardInterrupt as response data. Correcting that test double produced 45 passes; then the added no-echo privacy guard/test produced 46. Initial and intermediate results are retained in [the test receipt](h1-lock-wait-test-results.json), separate from final totals. No firmware workaround or weakened expectation was introduced. The original lock-wait tests are reused in the new helper's targeted suite; chronology fixtures were aligned to the newly enforced preflight baseline and valid wrap semantics.

Checks ran on Linux with the versions in the receipt. Python 3.8 grammar and Bash syntax checks support the intended **High Sierra 10.13.6 / Bash 3.2 / Python 3.8 stdlib** interfaces. This kit does not require pySerial, esptool, a compiler or a native LED executable. Native High Sierra use and the new physical trials remain pending. ASan/UBSan are not applicable to this Python-only work; no historical firmware test/sanitizer count is presented as freshly rerun.

An independent final review extracted the ZIP, checked all member identities, ran the offline validator successfully, checked Python 3.8 grammar and verified all four fixtures against the original contract. This is software evidence only.

## Owner review and next step

After externally verifying the ZIP SHA-256 and unpacking into a new folder, the first fully offline command is:

```bash
python3 validate_kit.py --directory .
```

Expect kit integrity PASS, `hardware_access=false`, `physical_use_authorized=false` and physical acceptance PENDING_OWNER. Read [the acceptance sheet](h1-lock-wait-acceptance.md) before any later owner-operated use. It prepares the observer before Start, asks for the actual assigned ID, preserves Screen 115200/Control+J guidance and requires port rediscovery after reconnect.

Four unchanged fixtures form three groups: default/readback10000/RESET preservation plus a separately started new-run5000 check; passive1000ms CAPS_CHANGE expiry with correlated **Deadline9 / Timeout26 / line3**, distinct from whole-budget Runtime6; and held Shift /10000ms CAPS_CHANGE wait, matched waiting evidence, one deliberate owner STOP, Cancelled2, absent unwanted marker and manual lowercase recovery. The existing five-second preparation DELAY is a focus opportunity, not a guarantee of manual timing. No automatic Start, retry or replay occurs. Missing correlation, unexpected lock transitions or competing outcomes are inconclusive, not automatic firmware failures.

[Preservation evidence](h1-lock-wait-preservation.json) records unchanged historical bytes/modes and the pre-publication ref snapshot. Publication/download verification is recorded separately after push. Changes are confined to new helper/test/fixture files, new documentation/receipts and this one ZIP. Existing firmware, profiles, packages, observers, inventories, rollback and refs are preserved.
