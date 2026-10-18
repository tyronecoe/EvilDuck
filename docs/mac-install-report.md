# Mac installation package: new recovery investigation and explicit review gate

**The requested new installation ZIP is still unavailable.** This attempt actively
reproduced the dependency installation, compared complete file inventories, applied
and inspected the exact patches, retried the protected build and prepared/tested
an unbound Mac installer. It did not repeat `d32a60b` as a new firmware release.

Starting source `d32a60bd3fef73e38293f95905f5905eb41b32fd`; new branch
`caps-queue-macos-install`. All original source/profile/verifier files and existing
packages remain byte-identical. No later owner work was overwritten.

## What changed and what was learned this time

1. Exported the **complete 1,683-record inventory** with precisely the historical
   ordering, root installed.json exclusion and compact JSON hashing. Symlinks are
   recorded separately. Permissions and mtimes do not affect this hash.
2. Independently checksum-verified the recorded c8525462 Arduino3.3.0 archive and
   made a fresh extraction. Installed the exact version separately using the real
   ArduinoCLI1.3.1 and publisher checksums. The cloud CLI proxy configuration was
   corrected in an external scratch config; this recovered ordinary downloading
   without touching global/user-owned core sources or changing pins.
3. Compared raw extraction, the preceding manual installation and the new actual
   CLI installation. All **hashed records match exactly**, with **zero added,
   removed or content-changed records**. The CLI's one additional regular file is
   root `installed.json`, excluded by the historical algorithm. No symlinks were
   present. Manual extraction versus CLI installation is **not the explanation**.
4. Traced the pin's creation in accessible history. The fingerprint first appears
   in Stage16 at fcffe4a; no complete historical inventory or generation transcript
   was found. Thirteen paths/variants were recovered from receipts/public package
   bytes, including the byte-identical partition parser. These are partial evidence,
   not a full inventory or proof of whole-tree equivalence.
5. Applied the existing USB patch alone and USB+NVS patches to separate disposable
   copies, with zero fuzz. The latter changes exactly the two expected source files,
   whose outputs match Stage18's exact reviewed hashes. No other source changes.
6. Independently verified **all177 recorded linked SDK archive hashes**, SDK config
   hash, and the exact compiler binary identity against the working STOP/LED build.
   No SDK rebuild or replacement was used.
7. Retried the unchanged protected builder against the **new real CLI installation**.
   It still exits1 `FAIL: Core tree mismatch` **before copying/patching/compiling**.
   This is an observed build blocker, not SKIP_ENVIRONMENT or a successful compile.
8. Prepared a separate, complete [archive-profile proposal](mac-install-build-profile-proposal.md)
   and input guard. Historical pins remain intact. Its successful inspection still
   returns **approved_for_build=false / approved_for_install=false**. This is an
   independent proposed basis, not a claimed historical reconstruction.
9. Prepared a Mac Terminal session engine with default read-only checking, strict
   tool/security/layout gates, unique private backups, explicit owner action,
   two-slot range limits, fresh rechecks and independent comparisons. It is
   deliberately **unbound**, so all CLI actions stop before device access. The
   immediate rollback is pinned to the current **c20dc399** working application,
   not the older shortcut image. No misleading installation ZIP was generated.

[Machine-readable evidence](mac-install-recovery-evidence.json),
[full fresh input inventories](mac-install-core-inventory.json),
[partial historical evidence](mac-install-partial-history.json),
[proposed input pins](mac-install-proposed-profile.json),
[reproduction](mac-install-reproduction.md),
[Mac preparation](mac-install-preparation.md).

## Exact fingerprint comparison

| Stage | Historical expected | Independently reproduced |
|---|---|---|
| Original | `27c2bae8bee6e4f8089417c048f41bfd255d7a80fab5e889bf74fb258112cb51` | `8d9ff37fa810d0338ed89bc87aa26523ea39add6ec8ce947ae59c4abeedeccc8` |
| HID only | `7cf86f7a1912d291ad69f2eab7f5c7fbbcbacbfcba4ed72f21b7fe7d08446499` | `18557597a548be2b70f6683c135de194da7aae8d9067f9c422e68eff58af1671` |
| HID + NVS | `81c11f59e01c1e6263d387a008d3f3211319d94feb4751ddfa11af35a2a57ed3` | `edfa1c99cdb73dca1da7d2f0a9d1153e40a2ce196c7470872c9654f03093f530` |

The file-by-file difference **against the historical measured tree remains UNKNOWN**:
its full records/bytes are unavailable. The zero differences above compare actual
fresh inputs, not an invented historical tree. Metadata, corruption, generated
bytecode and malicious changes are not asserted as causes. An exploratory generated
cache hypothesis did not reproduce the historical fingerprint and was not adopted.
No unknown files were added/deleted to force acceptance, no broad ignore rules were
introduced and no expected historical checksum was changed.

## Fresh verification (executed this attempt)

| Check | Result | Boundary |
|---|---|---|
| Input/inventory/profile cases | **21 PASS, 0 FAIL** | Real archive/core/SDK/patch/compiler inputs; invalid versions/files/tamper; unchanged historical guards still reject |
| Installer engine | **42 PASS, 0 FAIL** | Injected tool/checker faults and temporary fixtures; exact rejection reasons; cancellation, backups, ranges, verification failures, rollback identity and action override |
| esptool4.12.0 argument parser | **9 PASS, 0 FAIL** | Exact source AST truncated after argument parsing; no connection/operation dispatcher executed |
| Composed C++ regressions | **125 PASS, 0 FAIL, 6,574 assertions** | Freshly compiled actual selected application bodies with mocks; ASan/UBSan/leak detection |
| Embedded UI regressions | **18 PASS groups, 0 FAIL, 31 assertions** | Actual newly composed JavaScript in Node VM; no physical browser/HID claim |
| Stage26 freeze | **235 files byte-identical** | Repository evidence only |
| Protected firmware build | **BLOCKED, exit1** | Same historical tree guard; compilation did not start |
| Native High Sierra / physical installation | **NOT TESTED** | Owner-recorded environment only; no device access |

No broad historical totals were reused as fresh results. Python fault-case counts,
C++ assertions and JS group counts are kept distinct. Python/CLI preparation does
not acquire a sanitizer claim; the fresh C++ runner enables ASan/UBSan/leak checks.
Initial installer-engine tests found a version-regex newline bug; it was corrected
and negative tests now require the precise expected rejection code so an earlier
wrong gate cannot manufacture a pass. A temporary harness syntax error was also
corrected before the final completed run. No historical tests were weakened.

The installer tests use a synthetic **non-firmware** application and an injected
package checker. They prove session gating, not an actual new image/manifest's
integrity. Release binding, final ESP image checks and new package publication
cannot be completed honestly before the target build passes. The Python sources
use3.8-compatible grammar; Bash launchers are tested with spaced paths and0644
permissions. They do not install compilers, tools, drivers or bypass OS controls.

## Firmware and resource status

No new target ELF/BIN, application SHA/size, compiler program bytes, static RAM,
OTA headroom or target stack estimates are available. No proposed alternative was
silently promoted to the historical profile. No new application was repackaged from
an old BIN. Existing working application remains1,376,576 bytes, SHA
`c20dc3991a72b3411c506c107300e57ea96156d3ca233caa682f6a0c6a7a07d4`.
That identity is **rollback input only**, not a new release identity.

Caps Lock remains diagnostics-first: usage0x39 follows the selected transient path,
press/release progress acknowledges local API behavior rather than host acceptance;
Route B still rejects HOLD/RELEASE. No minimum Caps dwell/transport completion
contract was independently established, so no guessed timing change or forced
uppercase was introduced. Raw LED callbacks and the17-byte roundtrip remain
physically unresolved. Current owner Mac version/port were not newly observed.

## Specific next decision

**GO:** review the complete additive archive-profile proposal and the tested Mac
preparation. **NO-GO:** publish/install a new application or claim a successful
build while the accepted dependency basis is unresolved.

The smallest concrete path forward is **explicit review/approval to introduce the
separate archive-based profile** pinned to8d9ff37… / edfa1c99…, with historical
verifiers retained unchanged. That is cloud software-build approval, not physical
flashing approval. Alternatively recover the matching historical core or its full
inventory/provenance so the old verifier can pass naturally. No owner firmware
backup, NVS values, credentials, stock-firmware download or Mac compilation is
needed for that review.

After that gate: select the separately reviewed dependency profile, clean-build
and post-link-check the exact caps_queue composition, bind its actual image and
c20 rollback into the prepared installer, test the real package, then publish and
download-verify a NEW commit-pinned ZIP. Only then can a genuine first download/
check/extract command and installation instructions be supplied. This task has not
created a nonexistent link or reoffered the installed ZIP as containing the new fixes.

All existing firmware, profiles, historical refs and backups remain preserved.
No hardware access, real HID, flashing, erasing, formatting, OTA, owner payload
execution or host LED sender launch occurred.
