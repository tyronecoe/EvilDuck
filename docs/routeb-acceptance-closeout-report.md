# Route B acceptance closeout and next compatibility recommendation

## Result

**ROUTEB-TEXT-KEYBOARD-v1 is the latest owner-accepted baseline.** Its 1,412,400-byte application SHA-256 is `53acc374ef38be652b6847d4b84f2dc7d42fa73a3dd54ea62d5208be4cbc0167`. [Acceptance and exact future rollback requirement](routeb-accepted-baseline.md), [machine-readable record](routeb-accepted-baseline.json).

The five planned physical trials passed as owner-reported on High Sierra 10.13.6. The last was Request 5, line 3, diagnostic 16, blank TextEdit/no unexpected output. Missing dates, receipts and boot/session identifiers remain unknown. Codex did not independently perform these physical checks. No full language, USB delivery, host-global key release or universal layout certification is inferred.

The [consolidated current inventory](routeb-accepted-compatibility.md) separates actual composed behavior, scoped physical observations, software-only edges, restrictions, legacy-only capabilities and blocked reference contracts. It leaves older reports untouched. Main/legacy/standalone preview symbols are not evidence of composed support. ELSE IF, randomization, preprocessing, inline INJECT_MOD, HOLD/RELEASE, RESET and inline REPEAT are already implemented; none is proposed for reimplementation.

## Recommended next work

The three ranked work groups are bounded restart, source-file portability and explicit keyboard layouts. The recommended cohesive next release is **argument-free RESTART_PAYLOAD** with owner-matched neutral submission, same request/lease and unchanged whole-request budgets. Full [proposal, exact syntax, source seams, risk/effort ranking, regression matrix and short High Sierra sheet](routeb-next-compatibility-release.md).

The key implementation hazard identified is using `Runtime::start()` to restart: it resets the deadline, counters and borrow state. The proposal instead requires a private state rewind after the existing reset barrier. This is a design finding, not a demonstrated defect in the current firmware, which has no restart command. No significant existing safety defect was established by the targeted review. The already documented compiler-versus-adapter BOM mismatch remains a separate portability limitation.

Official restart-from-beginning intent is supported by the existing primary-source capture. State lifetimes and finite request budgets are explicitly proposed EvilDuck policies, not independently verified Hak5 runtime behavior. INJECT_VAR remains blocked pending new independent runtime evidence; completed research and unresolved fields are unchanged. No broad searches, compiler reference reruns, Caps investigation or Windows dependency were introduced.

## Fresh checks versus historical evidence

Fresh read-only integrity checks are recorded in [the closeout receipt](routeb-acceptance-closeout-checks.json):

- All **2,053 accepted-baseline files and executable modes** unchanged, including previous packages, historical evidence and firmware/dependency tools.
- All **201 composed source files** and **five existing build artifacts** rehashed against the existing linked receipt; no build was performed.
- Existing public ZIP: **2,336,378 bytes**, SHA-256 `9a60e91e142fea74b746bef352d16139cccaf9fd45ca5e5a10549c91b846dc9e`; CRC and 20 support bindings checked. Its `application.bin` matches the new accepted rollback target exactly.
- Existing Stage26 freeze check rerun: **235 protected files byte-identical**.
- New changes restricted to acceptance/inventory/design/report records and one read-only audit utility. No implementation or installation artifact added.

The earlier **371 PASS / 14,907 assertions**, **43 package checks** and **38 mock-installer checks** remain historical receipts, inspected but **not rerun**. No new firmware behavior, sanitizer result, target resource measurement or physical test is claimed. Existing sanitizer results remain historical. There is no reason to rebuild or repeat the full suites for an additive documentation closeout.

Relevant historical coverage already exercises RESET fresh-neutral ordering, ownership, retries, STOP, disconnect/quarantine and continued execution (V25–V40); bounded compile/repetition (V13–V24/V37–V38); and keyboard/feedback/preprocessing/randomization/EDR1 regressions. Actual **missing restart-specific coverage** is budget preservation across rewind, immutable Program lifetime, abandoned nested-expression/call state, same-request diagnostics and clearing completion races. Those tests must be new when implementation is separately approved. Existing RESET tests do not establish restart correctness.

## Reproduction and review boundary

From repository root, using the preserved existing build directory:

```bash
python3 tests/acceptance_closeout/verify.py --build-root /workspace/scratch/text-keyboard/build-v1
```

The utility only reads public repository/build evidence and runs local Git/freeze checks. It performs no compilation, network, serial, installer, payload or hardware operation. Missing/changed source or artifacts is an error; the utility does not regenerate or repair them. A reviewer without that saved build must recreate it only under a separately appropriate build authorization; this assignment does not silently build it. Python execution environment and exact hash/inventory results are in the receipt. Native macOS execution is not claimed.

Only the isolated documentation branch is published; old branches/tags and all historical release bytes remain untouched. [Publication/ref receipt](routeb-acceptance-closeout-publication.json) records the checks. The final branch tip and clean worktree are verified after publishing the receipt.

**GO:** review the consolidated inventory and proposed bounded restart contract. **Not authorized here:** firmware implementation, new installation package, hardware access, HID execution, flashing or OTA. Future packages must roll back to the accepted text/keyboard application, while retaining older versions as optional recovery resources. No original firmware search, private backup access, settings reset, format or EDR1 change occurred.
