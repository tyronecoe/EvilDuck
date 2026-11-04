# Static-response repair — owner review delivery

**REVIEW ONLY — NOT INSTALLED — NOT OWNER-HARDWARE-VERIFIED.**

Branch: `routeb-static-response-repair-review-v1`.
Build ID: **`ROUTEB-STATIC-RESPONSE-REPAIR-v1`**.

[Download the commit-pinned Mac review ZIP](https://raw.githubusercontent.com/tyronecoe/EvilDuck/d8f608005da34ebe0d3e871322922dc35f3788e8/downloads/evilduck-static-response-repair-h1-macos-review-v1.zip).
Artifact publication commit: `d8f608005da34ebe0d3e871322922dc35f3788e8`.
The [publication receipt](static-response-repair-publication.json) records the
HTTP 200 download, exact byte comparison, extracted image hashes and successful
offline preflight from the downloaded archive. All 91 previous remote refs remain
unchanged; only the new isolated review branch was added.

The normal build selects the streaming static-response repair by default. It
preserves the reviewed editor, Privacy Fix 1, dashboard organization and inherited
Route B safeguards. The previously owner-installed e825 application remains
faulty historical evidence, not a known-good recovery image.

## Final archive and artifacts

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `evilduck-static-response-repair-h1-macos-review-v1.zip` | 2,596,654 | `2109f0560103bdebab427978ad33b83f344eea34c8dadb68d039e98b31c4a1f3` |
| Application | 1,437,696 | `d5fe0932fe915443a5e53030969c6792409f719d427681304a7102355b2d7946` |
| ELF, provenance only | 23,642,852 | `4f530f7e0eb330585faaed3311de7b6b4227514b2517f6d6c36615da128e9c44` |
| Exact older source/text-v2 rollback | 1,413,200 | `cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02` |

The rollback lacks Privacy Fix 1 and subsequent dashboard/editor/response repairs.
It is standalone application code, not complete flash or filesystem recovery.
It cannot restore deleted scripts or past settings. No existing private backup,
including the owner's backup ending `w7uhm8z7`, was read or published.

Compiler program is **1,437,547 bytes** (-8); application BIN size remains
**1,437,696 bytes**; static RAM remains **113,896 bytes**. Free space remains
**6,164,480 bytes** per slot. These are build measurements, not measured heap.

## Provenance and verification

- Actual clean compilation C: `68f7fb2de5af2988a3136eb9222fb8c3e7dee8f5`.
- Host verifier correction D: `89d499fdb4dde13782cb09c7882ab55cc604a4dd`.
- Verification-only completion helper E: `520716462ffd66858a686e6c3a06eae037b3c5d4`.
- Final packaging sources: `1d4f2402f778e926894ed0111e3916003b3a8291`.

One clean target compile/link produced this image. A host decoder correction
recognized Xtensa signed `MOVI`/`ADDMI` length formation. Original compilation
inputs, all 201 firmware source entries, ELF and application remained unchanged.
The completion trace permits only one pinned compiler linker-location query;
no firmware recompile/link or device operation occurred. The correction and
initial failures are explicitly preserved in the reports, not hidden by a rebuild.

Actual compiled and linked dispatcher/factory/fill paths are verified, along with
all ten compiled pointer/length call witnesses and all nine wire resources. All
five complete dashboard/settings resources occur once in actual ELF and BIN.
All six inherited release layers and 190 verifier Assert nodes are retained.

Fresh software results:

| Suite | PASS | FAIL |
|---|---:|---:|
| Response/native/browser/source groups | 43 (1,034 assertions) | 0 |
| Affected privacy native cases | 28 (736 assertions) | 0 |
| Existing composed native regressions | 558 (23,901 assertions) | 0 |
| Inherited inert dashboard browser groups | 9 (207 assertions) | 0 |
| Target integration controls | 8 | 0 |
| Decoder/provenance controls | 11 | 0 |
| Completion policy controls | 6 | 0 |
| Final response-package checks | 41 | 0 |
| Final inherited package/archive checks | 83 | 0 |
| Final mock-installer checks | 38 | 0 |
| Final package-source policy groups | 6 | 0 |

Native ASan, UBSan and leak checks are clean. Repeated independent invocations
are not counted as extra unique cases. The prior 64-group editor result is
historical reuse bound to the identical header, not freshly counted.

The first unpublished package prototype failed one guide check: installation
instructions omitted a reference to the owner acceptance sheet. The final
packager adds that reference. The final 83-case suite passes unchanged; no image,
installer-code or validation guard was altered to satisfy the guide check.
Prototype evidence remains outside published downloads.

The final 37-member ZIP passed fresh extraction and its actual offline preflight.
Installer and launcher construction are unchanged apart from release-binding
values. Python 3.8 grammar/API checks and mocked security/range/backup/refusal
paths pass; actual native execution of this new kit remains pending. The existing
installer's backup-folder prefix is historical and does not identify the image.

All 91 prior remote refs were unchanged before publication. All historical
packages are preserved. The only pre-existing tracked path intentionally updated
on this branch is the requested normal build entry; the other 2,436 historical
files/modes remain unchanged. Old commits/refs retain their original contents.
The publication receipt records the final ref and downloaded-byte checks.

## First offline step

With EvilDuck **unplugged**, from the extracted folder:

```bash
python3 preflight.py --directory .
```

Expect exit 0, `package_integrity: PASS`, `plan_ready: false`, no selected write
ranges and `hardware_access: false`. Stop before installation. Download/package
integrity does not authorize hardware operation or establish runtime success.

Use [the short acceptance sheet](static-response-repair-acceptance.md) only after
a separately authorized owner installation. Correlate the new image identity with
a fresh full-page load, nonempty script, password-handler availability and normal
authenticated status. Keep Mac and iPhone observations separate; matching an
isolated GET is insufficient. No payload or accepted keyboard/lock-wait/privacy
milestone needs repeating.

[Full engineering report](static-response-repair-report.md) ·
[Build/source artifacts](static-response-repair-artifacts.json) ·
[Package checks](static-response-repair-package-verification.json) ·
[Reproduction](static-response-repair-reproduction.md) ·
[Platform limits](static-response-repair-platforms.md).

No hardware access, installation, flashing, OTA, owner-script execution, storage
mutation, credential reset or private-backup access occurred. H1 remains opt-in
and experimental; canonical Hak5 encoding remains unresolved.
