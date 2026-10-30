# INJECT_VAR reference investigation and reversible H1 prototype

**Practical result:** an isolated, opt-in EvilDuck H1 implementation passes composed software tests and a clean pinned target build. **Reference result:** genuine Hak5 runtime encoding remains unresolved. The experiment does not convert that uncertainty into a canonical compatibility claim. No installer or deployable image is published; no hardware, real HID, flashing, OTA, settings reset, private backup or stored owner payload was accessed/executed.

## Starting point and failure classification

Work starts at `51583dd9008c98699f1eb082c42103bbff6c755a` on new branch `routeb-inject-var-experimental-v1`. Initial worktree was clean; remote refs were recorded and no subsequent release found. The starting lock-wait candidate is software-tested, not newly owner-accepted. The latest accepted High Sierra baseline remains source/text v2,1413200bytes / `cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02`. Its exact published application bytes are verified available. The handoff's older combined1411088byte application is also verified as `2e1d8345417c6f23a5df3d884db42dd2a0f9f305120ee494c56a58048e677496`; its four scoped owner passes remain history. UppercaseZIP `f3aa611d…`, combinedZIP `a25e703d…` and application hashes remain distinct. [Preservation/rollback evidence](inject-var-experimental-preservation.json).

No original physical INJECT_VAR failure transcript was supplied. Existing documented examples do not demonstrate an observed wrong output or mutation. On the unchanged current composition, a random-keycode initializer fails because its internal getter is absent; separately, a declared numeric variable followed by INJECT_VAR reaches explicit Unsupported. Both are pre-output admission failures. This prototype adds a feature, rather than claiming to repair a proven numeric-decoding bug. [Evidence and newly labeled minimal reproducers](inject-var-experimental-evidence.md).

## What changed in the investigation

The preserved focused report/19function identities/25checks were read first and remain unchanged. They were not rerun as this task's main result. A fresh public PayloadStudio capture matched SHA256 `18efc91b48d8ada4e7aaaaebe0218e9bbc360360eb81ac182a63c4db9c10eee7`, encoder `5b4c1b5-271b6b-1690371896-STABLE`. New selected-handler checks trace previously untested assignment/copy/EXFIL seams:

| Step | Observed compiler bytes | What is established |
|---|---|---|
| `$ORIGINAL = $_RANDOM_LOWER_LETTER_KEYCODE` | `e8010001fa420000` | Runtime assignment references destination and property; not a selected scalar |
| `$COPY = $ORIGINAL` | `e801000200010000` | Runtime copy references source/destination; JS placeholders remain0000 |
| Inject copy twice | `e9e90002e9e90002` | Same register referenced twice; no runtime decoding/release execution |
| EXFIL original/copy | `f6e90001f6e90002` | Runtime output references; framing and byte order remain unobserved |
| Initializer0x0204 | Separate constant pool entry `0402` | Serialized constant, not the meaning of a generated key |

Distinct ASCII/keycode selector families reinforce the semantic distinction, but do not establish how the VM returns or transforms a keycode. `generateLangPack` forces Shift into each entry, so lowercaseLANG_a0402 cannot be adopted as a lowercase scalar. Compiler placeholder/storage-copy observations are not official runtime variable mutation results.

[Full evidence/URLs/function lines](inject-var-experimental-evidence.md), [machine-readable provenance and hypothesis table](inject-var-experimental-reference-evidence.json), [actual new compiler receipt](inject-var-experimental-compiler-trace.json). Targeted current docs.hak5 and USBPDF requests returned403; no verified current canonical redirect or fresh specification reading is invented. Earlier saved official statements remain the documentary basis. No proprietary binary was reverse-engineered and no emulator was used as a Hak5 oracle.

## Hypotheses: tested predictions, no invented winner

H1 predicts `(modifier << 8) | usage`; H2 swaps those bytes. For A their predictions are0204 and0402; for a they are0004 and0400. ASCII-like, layout-index/tagged values and runtime case transformations remain possible without a defined scalar specification. The new comparison code distinguishes numerical predictions and a synthetic H2counterexample, while leaving every official runtime value null. It never chooses a winner merely because our whitelist accepts H1. The strongest supported statement is that H1 is a simple, useful experimental convention consistent with currently inspected evidence, **not that Hak5 implements it**.

The smallest missing evidence is a calibrated correlated genuine runtime capture with compiler/layout/device context: capture once, copy, inject the same copy twice and observe original/copy before and after **each** injection. [Prepared reference kit](inject-var-experimental-reference-trial.md) supports a six-byte calibration gate and a narrow60byteframe with two marker blocks and four12bytegroups. It refuses unknown framing, incomplete captures and missing metadata; synthetic parser passes do not authenticate a device. Only generated constants/keys are involved, never ordinary files, credentials or unrelated loot. This kit was prepared, not physically executed.

## Experimental architecture and grammar

Build **ROUTEB-INJECT-VAR-H1-EXPERIMENTAL-v1** requires explicit `EVILDUCK_EXPERIMENTAL_INJECT_VAR_H1=1`. Existing/default profiles never apply its patch; missing/zero selection refuses the candidate build. Only three disposable generated files change: core.cpp/core.h/caps_trial.h. Backend, adapter, descriptors, partitions, SDK, settings and EDR1 are unchanged. [Exact source/patch hashes](../tests/inject_var_experimental/source-manifest.json), [design](inject-var-experimental-design.md).

Exact `INJECT_VAR $ordinaryVariable` uses existing checked numeric evaluation, validates a sparse whitelist of95USprintable mapping pairs with modifiers0orleftShift2, then emits the existing cached KeyTap. No numeric/direct-getter/expression/DEFINE-generated operand or inlineREPEAT is added. Six read-only stored-keycode getters reuse existing alphabets and bounded sampler. Each reference selects once; scalar assignment/copy remains ordinary uint16 storage, and repeated injection does not mutate the values. Ordinary numeric variables have no provenance tags: an integer can coincidentally equal a valid H1pair, but numeric randomization is not decimal printing or guaranteed keycode generation.

The pure decoder and event path preserve held-key merging/restoration, collision/rollover refusals, jitter/dwell, request/lease ownership, budgets, STOP/error/disconnect cleanup and ambiguity/quarantine. Lowercase stored data under a heldShift still follows existing modifier merging; no Caps normalization or host-global release guarantee is introduced. AltGr/dead keys, extra layouts, arbitrary masks/usages and special/modifier-only keys are rejected by this experiment; these refusals are not claimed Hak5 error behavior. Canonical INJECT_VAR remains blocked in accepted inventories; this branch is an explicitly different evidence level.

## Fresh verification

| Executed checks | PASS | Unexpected FAIL | Scope |
|---|---:|---:|---|
| New AC01–AC30 |30|0|5168 assertions; H1policy/actual composed modules |
| Candidate-adapted regressions |492|0|17956 assertions |
| Full native-v2 |522|0|23124 assertions; ASan/UBSan/leak clean |
| Separate actual-core edge probes |2|0|Uninitialized rejection/noevent; cachedoperand despite synthetic mutation |
| Unchanged default refusal smoke |3|0|44assertions; prior binary freshly executed, not rebuilt firmware |
| New selected compiler checks |18|0|Assignment/copy/EXFIL/compiler bookkeeping only |
| Separate hypothesis comparisons |5|0|Synthetic/algorithmic, no authentic scalar observation |
| Reference-parser checks |18|0|Manufactured calibration/mutation/error captures only |

[Native and development receipt](inject-var-experimental-test-results.json), [default refusal identity](inject-var-experimental-default-refusals.json), [parser receipt](inject-var-experimental-reference-parser-tests.json), [reproduction](inject-var-experimental-reproduction.md).

Independent hard-coded USusage/modifier/report expectations cover every supported printable and all six getter alphabets, not only encode/decode round trips. Cases cover scalar capture/copy/reassignment/repetition, invalid and uninitialized inputs, malformed retained source, exclusions, function suspension, random sampling exhaustion, cached retries, held states, collisions/rollover, STOP/error/disconnect cleanup/quarantine, jitter and subsequent runs. The extra core probe changes the original variable during a pending retry and confirms the accepted event retains its earlier key. No additional production hooks or target access-control overrides are introduced; native-only fault injection is explicitly recorded.

The existing R06/U06 generated copies remove two superseded refusal expectations for newly supported forms. Their8assertions are not silently counted in the new regression total; positive getters and new invalid-value/grammar cases replace coverage. Historical sources/receipts and XPASS/XFAIL/risk observations remain unchanged. This is not a rerun claim for every unrelated historical suite.

Development findings are retained: native-v1 had521PASS/1FAIL because AC30 reused a callback expecting Character/A; the actual new KeyTap caused its assertion/exception allocation. Correcting the callback preserved the no-allocation assertion and required the final run above; no production workaround was applied. The first link verifier saw both a real Runtime::evaluationStep function and its new read-only local groups table under the same prefix. The additive verifier now requires executable symbol types and still rejects multiple matching functions. A four-site ASToverride initially matched one historical marker twice; restricting it to the actual replacement preserved exact anchors. Final post-link checks passed; earlier logs remain development evidence.

## Clean build, resources and artifact boundary

Pinned isolated ArduinoESP32 3.3.0 archive profile, ESP32-S3/16MiB/custom geometry/PSRAMdisabled, existing USB-OTG/TinyUSB/CDC and CPU/flash settings. All177SDKarchive identities and inherited source/startup/USB/NVS/ownership/timeout/ELF-to-BIN guards pass. Final link proof binds the real H1decoder to Runtime::completeInstruction and the unchanged Adapter→route_b::key transport. No globally installed core/SDK is modified.

| Resource | Accepted v2 | Starting lock-wait | H1prototype |
|---|---:|---:|---:|
| Compiler program bytes |1413055|1413375|1413931|
| Application BIN bytes |1413200|1413520|1414080|
| Static RAM bytes |113888|113896|113896|
| Free OTA slot bytes |6188976|6188656|6188096|

The OTA slot remains7602176bytes. H1adds556program/560BINbytes and zero staticRAM over its software starting point; versus acceptedv2 the total is876program/880BINbytes and8staticRAM. Compiler frames: decoder48bytes, completeInstruction48, evaluationStep144; statement352(vs368starting). These are compiler estimates, not physical stack high-water, heap or latency measurements. No new heap buffer/state allocation is introduced; relevant native allocation/sanitizer checks pass. [Resources](inject-var-experimental-resources.json), [complete build/link receipt](inject-var-experimental-build.json).

Local experimental application SHA256 `8a48f3f208165466e579f76a35fb7898fbaf1188e746ca3a0d60e99c576b0ecd`; ELF SHA256 `c33c612cfa704b15d6b9c7908d37b8dc17767384270c8a52893f650bfc0763c0`. Partition table SHA remains `b79bde9ef4a9544411d97a31a1d326b2028213269ad0dcc643ea921230ce3d5e`. The images remain local scratch research outputs, not published deployment artifacts. No installation ZIP, merged image or installer is produced.

## Owner review, rollback and decision

[Future harmless High Sierra checks](inject-var-experimental-owner-check.md) specify fixed H1scalar/copy output `aaA00!!`, STOP/heldShift recovery, malformedoperand rejection and an optional captured random pair. They require separate installation/test approval and must not be run on accepted firmware. The genuine reference procedure is different: it never injects guessed numeric constants. No broad Caps investigation or Windows prerequisite is introduced.

Exact known-good recovery bytes exist: accepted source/textv2 application.bin in its original public ZIP, verified1413200bytes/cf42…ba81f02, not a rebuild or the older included restart rollback member. This is an application image, not a full-flash recovery set. Physical restoration still needs separately verified chip/security/installed geometry/OTA/recovery access and owner authorization. No physical readback or rollback test occurred. Original stock firmware remains OWNER CONFIRMED: AVAILABLE EXTERNALLY; it was not searched for or downloaded. Existing backups remain untouched.

| Decision area | Status |
|---|---|
| Compiler analysis | CONFIRMED within selected-function/static evidence scope |
| Genuine DS3runtime encoding/copy/release semantics | UNRESOLVED; no authenticated runtime observation |
| EvilDuck H1implementation | VERIFIED experimental software behavior; not canonical compatibility |
| Physical EvilDuck/HighSierra behavior | NOT TESTED; separate authorization required |

**GO:** review the reversible source experiment and prepared reference kit. **NO-GO:** canonical Hak5 compatibility claim, default-profile promotion, installation or physical execution. The final branch/publication identity and unchanged historical refs are recorded in [publication receipt](inject-var-experimental-publication.json); [changed-file inventory](inject-var-experimental-file-inventory.json) lists additions.

**PROMISING, BUT FURTHER VERIFICATION REQUIRED.** H1has a working software prototype under its chosen policy; the smallest next evidence for Hak5compatibility remains a calibrated genuine runtime sample or authoritative runtime specification, not more self-consistent emulator assertions.
