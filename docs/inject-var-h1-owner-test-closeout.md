# H1 physical owner-test milestone closeout

**Four scoped owner-reported checks: PASS under the experimental EvilDuck H1 convention.** The owner reported testing the physical EvilDuck with an Intel Mac running **macOS High Sierra 10.13.6** in the October 30, 2026 testing conversation. This later record, prepared October 31, supplements the historical source-stage and package reports; their original no-hardware and pending-test statements remain unchanged.

This is an owner-supplied evidence summary. Codex read the supplied `EvilDuck-H1-Physical-Test-Results-Codex.txt`, not the referenced photographs themselves. They were supplied in the owner's testing conversation but are not embedded in this handoff or attached to this closeout session. Their filenames are retained below for traceability. No physical hardware was accessed by Codex and no screenshot was independently inspected here.

## Scoped results

| Check / reviewed fixture | Classification | Owner-supplied observation and correlation |
|---|---|---|
| Fixed scalars, copy, repeated injection and reassignment — `h1-fixed-copy.txt` | **PASS** — image observations summarized by the owner handoff | Exact `aaA00!!`; dashboard **Request 1: Completed**. References: `IMG_7F2F5CEB-E988-4DFD-949B-F0BFFCF546E2.jpeg`, `IMG_4134.jpeg`. |
| Held Shift, deliberate STOP and manual lowercase recovery — `h1-stop-held-shift.txt` | **PASS** — image observation plus explicit owner confirmation summarized by the handoff | Owner reported an injected `A`; photograph summarized as `Aabc` after instructed manual `abc`, with no visible `999bad`. For that same successful attempt, owner answered **“Yes it says cancelled.”** Successful request ID remains **unknown**. Reference: `IMG_D44D04C7-10E4-415A-A0E0-82442B134F2A.jpeg`. |
| Malformed operand rejected before output — `h1-malformed.txt` | **OWNER-REPORTED PASS** | Owner reported passing after being told to require compile rejection and completely blank TextEdit. No screenshot, request ID, exact diagnostic, physical line or diagnostic code was supplied; all remain **unknown**. |
| Random lowercase value captured, copied and injected twice — `h1-random-copy.txt` | **PASS** — image observations summarized by the owner handoff | Exact `yy`; dashboard **Request 6: Completed**. References: `IMG_377FFE55-D5EF-4308-B755-8FFB3425285A.jpeg`, `IMG_4137.jpeg`. The numeric scalar was **not captured**. |

The earlier STOP attempt, **Request 2: Cancelled with blank TextEdit**, remains **INCONCLUSIVE**. The owner confirmed manually pressing STOP, but its timing did not establish the held-Shift observation. It is not the successful STOP trial and its request ID must not be reassigned to that trial. No ID is inferred from later numbering.

The reviewed fixtures are preserved in [the package acceptance sheet](inject-var-h1-package-acceptance.md) and [the exact fixture directory at the published package commit](https://github.com/tyronecoe/EvilDuck/tree/6299e19a41925ff1048655bb52751899cc0ee6ea/tests/inject_var_h1_package/fixtures). The malformed fixture contains `STRINGLN 999bad` followed by `INJECT_VAR 0x0004`; rejecting it before the first output is the scoped owner-reported observation, not a newly executed compiler test.

The owner was instructed to select Route B, blank plain-text TextEdit, US input, Caps off and no held physical keys. Independent host-setting records and exact source-readback hashes were not supplied. Exact per-run timestamps and complete boot/session correlation remain unknown. Detailed quarantine/transport diagnostics were not supplied, so this record does **not** assert independently proven absence of faults or quarantine. Missing identifiers do not trigger a request to repeat these completed checks.

## Installation and artifact identity boundaries

Intended build: **ROUTEB-INJECT-VAR-H1-EXPERIMENTAL-v1**. Source-stage review: `a15b8e218935b2c6a69b71eeac3aaf378c3c0c03`. Published package/report: `6299e19a41925ff1048655bb52751899cc0ee6ea`; ZIP-containing commit: `0982baec1d2beda44b1db31aacd373b3f45c1121`.

The handoff records owner-supplied **READ_ONLY_CHECK_PASS**, zero writes and both planned application entries referencing the candidate hash. A read-only plan is not an installation-comparison receipt. The owner subsequently reported completing installation; the handoff summarizes a running dashboard screenshot with the H1 experimental build-name prefix, USB configured and HID input ready. The build-ID ending was clipped. **No final H1 installation-comparison receipt or independent full application readback was supplied.** An earlier lock-wait installation receipt is not H1 evidence.

| Preserved artifact | Bytes | SHA-256 |
|---|---:|---|
| `evilduck-routeb-inject-var-h1-experimental-macos-v1.zip` | 2,450,845 | `229da835898e6739e31e4a6c08dd1ee9b5d74ded0458c7a0d850c899f5d2c639` |
| H1 `application.bin` | 1,414,080 | `8a48f3f208165466e579f76a35fb7898fbaf1188e746ca3a0d60e99c576b0ecd` |
| Required accepted source/text-v2 `rollback-application.bin` | 1,413,200 | `cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02` |

These package/image identities can be independently rehashed offline and are recorded in [artifact evidence](inject-var-h1-package-artifacts.json); they must not be relabeled as independent device readbacks. The exact **source/text-v2 rollback requirement remains unchanged**. Original packages, historical refs, default profiles and canonical compatibility inventories are not replaced or promoted by this milestone.

## What is now accepted, and what remains unresolved

Accepted here: **physical owner validation of the four tested EvilDuck H1 behaviors on High Sierra**, including the scoped STOP/manual-lowercase recovery observation and owner-only malformed-source report. This does not make H1 the default firmware or expand its checked US-printable subset.

**Genuine Hak5 runtime encoding and canonical INJECT_VAR compatibility remain unresolved.** H1-generated values working with H1's decoder cannot distinguish H1 from H2/swapped-byte or another genuine runtime representation. No calibrated genuine DS3 scalar capture was performed. The two equal letters are evidence of the observed generation/copy/reuse behavior for this run, not a numeric representation observation or randomness-quality study.

Other layouts, exhaustive physical printable coverage, arbitrary scancodes/modifiers, statistical quality, general recovery, host-global key release and USB endpoint retirement are outside this milestone. The inherited configurable lock-wait timeout change is not physically certified by these four fixtures. The existing bounded H1 policy and official-runtime unknowns remain in the [experimental design](inject-var-experimental-design.md); no new research sweep is needed for this closeout.

## Closeout verification and preserved history

Only documentation changes are made. The H1 package overview receives a dated link to this later owner-results record; the original overview text is retained as a prefix and the published ZIP remains byte-identical. Firmware, tests/fixtures, dependency guards, installation tools, source-stage reports, canonical inventories and recovery artifacts remain unchanged.

Existing [native/source-stage evidence](inject-var-experimental-test-results.json) and [package evidence](inject-var-h1-package-tests.json) are reused: **522 native passes / 23,124 assertions** with the recorded source-stage sanitizer results, and **75 final package / 38 final mock-installer passes**. None was rerun or reclassified for this documentation closeout. Earlier package documentation-check failures remain in their original receipts.

[Structured owner record](inject-var-h1-owner-test-closeout.json) retains unknown values as JSON null, distinguishes the inconclusive attempt and records the supplied handoff's hash. [Fresh closeout verification](inject-var-h1-owner-test-verification.json) records artifact, link, scope and preservation checks. Publication/ref comparisons are recorded separately after push. No new installer, firmware build, physical repetition, payload execution, flashing, OTA or settings action is requested or performed.

**GO:** close the four-check experimental H1 owner-test milestone. **UNRESOLVED:** canonical Hak5 runtime representation and the wider untested guarantees above. This closeout grants no new deployment or execution authorization.
