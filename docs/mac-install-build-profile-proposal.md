# Review decision: an additive archive-based core profile

**PROPOSAL ONLY. Not an approved build/deployment baseline. No installation ZIP.**
This is a new concrete review proposal from the investigation after `d32a60b`;
it does not change or replace the Stage16–18 historical verifier or pins.

## Evidence established in this attempt

The original core pin was first committed at
`fcffe4a1bb01d72a3a0176a2d8e738f3641db34f` against an installed Arduino3.3.0
source tree. Accessible history contains the hash values and `tree_hash` algorithm,
but no complete original path/hash inventory or pin-generation transcript. Repeated
later receipts carry those values forward; that is not an independent reconstruction.

The exact recorded release archive was obtained and its SHA-256 checked:
`c8525462e47b37b726c211b71afada0fca5859ba748963e4d967131355716ba2`.
A separate clean ArduinoCLI1.3.1 installation used the publisher package index and
checksum-verified tools. Raw ZIP extraction, the previous manually installed input,
and the clean CLI installation all produce the **same 1,683 hashed file records**:

`8d9ff37fa810d0338ed89bc87aa26523ea39add6ec8ce947ae59c4abeedeccc8`.

The clean CLI installation adds `installed.json` only; the historical algorithm
explicitly excludes that root file. No source records were added, removed or
changed, and no symlinks were found in those core trees or the release ZIP. File
permissions and mtimes are not hash inputs. Therefore manual extraction vs CLI
installation, catalog metadata, permission bits and mtimes do **not** explain the
observed fingerprint disagreement. No corruption or malicious modification is
inferred. A generated-cache hypothesis did not reproduce the historical hash and
is not treated as evidence that such a cache existed historically.

[Complete fresh inventories and patch diff](mac-install-core-inventory.json) use
exact historical ordering and compact JSON path/SHA semantics. [Investigation
receipt](mac-install-recovery-evidence.json) records expected/actual fingerprints.
[Partial historical evidence](mac-install-partial-history.json) has only13 recovered
paths/variants, including the old public package's byte-identical partition parser;
it is **not** a full historical inventory. Historical added/removed/changed file
lists remain UNKNOWN. Comparing two fresh trees does not fill that gap.

## Proposed separate profile

Retain historical original `27c2bae8…`, HID-only `7cf86f7a…` and USB/NVS patched
`81c11f59…` exactly as they are. Do not make them accept another tree.

For a separately selected, explicitly reviewed **archive-based profile**:

| Input stage | Independently reproduced fingerprint |
|---|---|
| Exact release extraction | `8d9ff37fa810d0338ed89bc87aa26523ea39add6ec8ce947ae59c4abeedeccc8` |
| Same extraction + existing HID patch | `18557597a548be2b70f6683c135de194da7aae8d9067f9c422e68eff58af1671` |
| Same extraction + existing HID and NVS patches | `edfa1c99cdb73dca1da7d2f0a9d1153e40a2ce196c7470872c9654f03093f530` |

Patches apply with zero fuzz and change **exactly two files**:
`libraries/USB/src/USBHID.cpp` and `cores/esp32/esp32-hal-misc.c`. Both resulting
file hashes exactly match Stage18's already reviewed patched source hashes.
The two patch bytes/hashes are unchanged. The compiler is bit-identical to the
working build, SHA `d968578945d9f62c2769e03a786d8853eb0ba226cfff1e8ee6588550927941a3`.
All **177** SDK archive identities consumed by the working STOP/LED link and its
SDK configuration hash match the newly installed SDK. No SDK library is rebuilt,
patched or substituted. Framework library trees were already independently matched
in the preceding attempt and remain unchanged.

[Proposed input identity receipt](mac-install-proposed-profile.json) includes all177
archive hashes and patch identities. `tests/mac_install/proposed_profile.py`
independently checks these inputs and returns **approved_for_build=false** and
**approved_for_install=false** even on success. It has no build/upload API.
This is not a disguised edit of `tools/patched_core.py` or a historical reproduction.

## Smallest remaining decision or artifact

Either:

1. Supply/recover a **matching historical core tree**, or a complete original
   per-file inventory plus provenance sufficient to reproduce it. No private NVS,
   credentials, firmware backups or Mac-side firmware compilation is needed.
2. **Review and explicitly approve introducing the separate archive-based build
   profile described here**, while keeping all historical profiles/verifiers intact.
   This approves a software dependency/build basis only, not hardware installation.

Review should consider that official release provenance, exact patches and unchanged
compiler/SDK establish a strong independent basis, but cannot prove byte equivalence
to the unavailable original measured tree. The unaccounted historical records must
not be described as metadata, harmless or equivalent without evidence.

After that review, implement/select the additive build/post-link identity path,
clean-build `tests/caps_queue` composition, rerun its final linked checks and bind
the actual new application into the prepared Mac installer. The full new BIN/ELF
and consumed source/object/archive evidence must pass before generating an install
ZIP. Review its new hash and app-only plan before physical use. None of that is
silently enabled by this proposal.

The requested exact historical build was actively retried against the clean CLI
installation and still fails **before compilation** with `Core tree mismatch`.
No verified new BIN exists, so packaging an old image as this release or inventing
an application hash would be wrong. Installation remains unavailable, with a
specific software review gate rather than a request for owner hardware experiments.
