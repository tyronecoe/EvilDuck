# DEFINE labels: verified review candidate

**BUILT — PACKAGED — NOT INSTALLED — DEFINE HARDWARE ACCEPTANCE PENDING.**

`ROUTEB-DEFINE-LABELS-H1-v1` accepts DEFINE labels up to **31 bytes excluding
NUL, including optional `#`**, through constant collection, storage, expansion
and conditional-flag lookup. This is a bounded EvilDuck capacity policy, not an
asserted official DS3 maximum. Ordinary variable/function limits remain 23
bytes. The sixteen-slot constant limit and all existing grammar, expansion,
source/line/IR/text and execution limits remain unchanged.

The only functional delta is three constant-specific edits in composed
core.cpp. The separate build-ID literal also changes; **199 other composed
sources remain byte-identical to DEL**. No runtime/HID, descriptor, USB mode,
storage, authentication, dependency, partition or dashboard implementation was
changed. [Exact source patch](../tests/define_labels/application.patch) and
[grammar/design contract](define-labels-design.md).

## Identity and review files

Development branch: `routeb-define-labels-h1-v1`, based on DEL publication
`6bcfb605c8249b63be2be9f79a00e4e81863fbf6`.
Implementation/clean-build checkpoint:
`5d9176dd15f722ffe20d219d33684da7461d1754`.
Package checkpoint: `2f8567a2547d133f54de7aa122aff05fe71629d7`.
Publication is a later dedicated review commit; it does not replace the build
checkpoint or imply installation.

[Mac review ZIP](/workspace/scratch/define-labels-release/evilduck-routeb-define-labels-h1-macos-review-v1.zip)
— **2,691,374 bytes, 50 members**, SHA-256:

```text
b91946bec818616f35a469edd6c2efa525eea01276d238b42ed1b26dea3558ed
```

Application: **1,438,048 bytes**, SHA-256:

```text
167cf5013cd4aa7c0823e5c7391ca9f6d400b7b99df6fe0e46085048fde91a30
```

ELF: **23,643,744 bytes**, SHA-256
`1ad99339ef0770eff96665f969149e636373f44fffeda2b76508e3e1d07de062`.

[Full results, changed-file inventory and 201-source inventory](define-labels-release-results.json),
[three-check owner sheet](define-labels-owner-check.md), and the
[DEL owner closeout](del-alias-owner-closeout.md) accompany the release.

## Measurements, not estimates

| Measurement | DEL parent | DEFINE candidate |
| --- | ---: | ---: |
| Host Compiler size/alignment | 3,856 / 8 bytes | 3,984 / 8 bytes |
| Host workspace/headroom | 4,096 / 240 bytes | 4,096 / 112 bytes |
| ESP32 Compiler size/alignment | 3,800 / 8 bytes | 3,928 / 8 bytes |
| ESP32 workspace/headroom | 4,096 / 296 bytes | 4,096 / 168 bytes |
| ESP32 Constant name/value cells | 24 / 64 bytes | 32 / 64 bytes |
| ESP32 Constant structure | 88 bytes | 96 bytes |
| Application image | 1,437,888 bytes | 1,438,048 bytes (+160) |
| Compiler program | 1,437,747 bytes | 1,437,907 bytes (+160) |
| Static RAM | 113,896 bytes | 113,896 bytes (0) |

All sixteen name cells grow inside the existing placement-construction
workspace. Its 4,096-byte size and original size/alignment static assertions are
retained. No heap allocation, workspace increase or production measurement
global was added. Host CompileSession stays 4,144 bytes with workspace alignment
16; target CompileSession stays 4,136 bytes/alignment 8. Target Program remains
6,936 bytes and Runtime 4,920 bytes; host Runtime is separately 4,952 bytes.

Actual core-object DWARF and linked ELF sizes agree. Two separately cached,
unlinked Xtensa measurement objects use the approved compiler arguments to
measure sizeof/alignment; neither is linked into the application nor executed.
Their input/compiler/response/object hashes are recorded and subsequent checks
reuse the verified cache instead of recompiling them.

All **72 compiler-reported core stack frames** match the parent. Cooperative
Compiler statementImpl/textLine/line/expr/step frames remain
336/304/240/144/144 bytes. The separate convenience Program::compile() frame
remains 4,224 bytes. These are emitted per-function frame measurements, not
physical stack high-water or whole task/call-chain peak measurements. Target
heap use and precise host timing were not measured.

## Verification completed

| Verification | Result |
| --- | --- |
| New focused actual-module cases | 28 PASS / 374 assertions |
| Fresh existing native regressions | 663 PASS / 28,173 assertions |
| Fresh native total | 691 PASS / 28,547 assertions |
| Unchanged web groups | 86 PASS / 1,518 assertions reused from completed DEL run |
| Source composition/refusal controls | 7 PASS / 34 assertions |
| Actual-candidate release controls | 30 PASS, no failures/skips |
| Package policies | 7 PASS |
| Package negative controls | 73 PASS |
| Archive/layout controls | 83 PASS |
| Actual bound-installer mocks | 38 PASS |
| Fresh extraction/offline preflight | PASS, no write ranges or hardware authorization |

ASan, UBSan and leak checks passed with empty native compile/runtime stderr.
The original 663 case bodies, expectations and sanitizer flags remain intact.
Focused cases cover short/23/24/27/31/32-byte labels, bare and prefixed forms,
full numeric/text substitution, long-prefix collisions, duplicates/slots,
declaration order, boundaries/nonrecursive expansion, long Boolean flags,
exclusions versus retained errors, physical diagnostics, variable/function and
internal-variable restrictions, retries, cancellation, isolation and no C++ heap
allocation. Original web results are explicitly reused; unchanged sources/tests
and fifteen SDK/mock input hashes support that decision.

The canonical entry executed its original committed-source guards, binding
**85 Git inputs**, then a clean isolated Arduino ESP32 **3.3.0** target build.
All **190 inherited release assertions** remain and pass, together with DEL
mapping, REPEAT, ownership, source/ELF, complete streaming resources, USB/NVS,
startup, SDK and dependency proofs. The first clean build passed; no rejected
image or post-compilation source/verifier delta was substituted. Three prebuild
candidate-dependent controls were initially pending; all thirty passed once the
actual image existed. No successful suite was repeatedly rerun without cause.

## Actual OS-extension progress and remaining blockers

The exact unchanged pinned OS_DETECTION v1.1 source was compiled against old and
new actual composed cores without starting Runtime. Parent: line **50/code 6**.
Candidate: line **54/code 18**, at the unsupported enumeration-counter reset.
The 27-byte DEFINE now passes; the whole extension still rejects. No detector,
counter, USB hook, OS constant/result, indicator, lock restoration or identity
change was implemented. Unknown lock state remains unknown. H1 remains opt-in
and experimental, with canonical numeric encoding unresolved.

[Detailed old/new observations and next Plan-mode contract questions](define-labels-os-progress.md)
preserve the earlier report and distinguish actual whole-file progress from
source-inspected or isolated dependencies. Remaining source/IR/runtime capacity
and host accuracy are unestablished. No OS probe or broad new research occurred.

## Review, owner observations and recovery

The owner reports DEL package integrity PASS, installer
BOTH_APPLICATION_COMPARISONS_PASS and both DELETE/DEL TextEdit checks working;
the handoff describes a photo with `ab` twice. This is scoped installation,
boot/input evidence. Missing full dashboard ID, request IDs and Completed
statuses remain unknown. The latest owner-installed record is DEL; no repeat
tests are requested because metadata is missing. New DEFINE physical acceptance
remains pending.

With EvilDuck unplugged, extract the new ZIP to a fresh folder and run only:

```bash
python3 preflight.py --directory .
```

The [short owner sheet](define-labels-owner-check.md) and matching fixtures are
also inside the ZIP. Later owner checks expect DEFINE27OK/newline,
DEFINE31OK/newline, and an exact 32-byte-label rejection at line 1/code 6 with
blank TextEdit. They use only constant substitution, not a shell or OS probe.
High Sierra 10.13.6, Bash 3.2, Python 3.8 and esptool 4.12 support and the guarded
application-only install/rollback procedure remain.

Exact rollback: **1,413,200 bytes**, SHA-256:

```text
cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02
```

The rollback is byte-identical to the published DEL kit's copy. It is older
standalone source/text-v2 application recovery without later privacy/dashboard
repairs, not a full-device/filesystem restore. Existing published packages and
recovery artifacts remain untouched. The installer retains its guarded chip,
security, partition/OTA checks and documented new private full-flash backup
before final confirmation; it performs no automatic reboot or script execution.

Only the canonical selector and consolidated inventory modify pre-existing
repository paths. All **2,549 other historical files/modes** remain unchanged.
The dedicated review publication preserves all earlier remote refs, accepted
branches and tags. No merge or force-push is permitted.

**No hardware access, serial/device operation, real HID output, flashing, OTA,
formatting, settings reset, credential/input collection or automatic owner test
occurred.** Publication is review delivery only; it does not claim installation
or physical acceptance of this candidate.
