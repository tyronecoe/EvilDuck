# Stage28N limitations and next gates

**GO:** review actual native component observations and the proposed coordinated change table. **NO-GO:** production adapter/integration, installed dependency changes, target/SDK/firmware builds/images, live USB/HID/board access, flash/boot/OTA or automatic Stage28O.

Resolved within this stage's boundary:

- Exact native input bytes:21 official publisher-pinned source/header files, unmodified; independent minimal source retrieval/build reproduced.
- Actual device dispatcher/HID copy/claim/class logic executes; per-case gcov confirms genuine functions, not a replacement model.
- Package/archive/member/config identities independently rechecked; builder DCD selection and archived weak deinit/strong core hooks recorded.
- Concrete behavior established for early completion, partial/oversized shape, refusal/retained claim, duplicate/stale events, buffer reuse, reset/unplug/reopen, finite queue, WAIT_FOREVER entry, protocol, multiple producers and teardown.

Still unresolved, separately:

1. **Source-to-object confidence:** specific header/instruction/callback facts are supported by authenticated shipped artifacts and matching source. Full source working-tree/include/compile equivalence remains unproven. A signed attestation is not mandatory if independently reproducible evidence can settle the specific build question; no unsupported SDK rebuild was attempted.
2. **Authentic identity:** actual event and callback have no C/Q. Native observations demonstrate that bytes/pointers/current mapping cannot manufacture it.
3. **Bounded entry:** actual claim/release invoke WAIT_FOREVER. Our custom OS records it and forced refusal; no real wait/lock latency or ISR synchronization was measured. DCD spin/MMIO loops remain source/static only.
4. **Retirement/quiescence:** reset/deinit/empty queue and success callbacks do not expose a reliable transfer+observer certificate. N20 depends on forced DCD failure and fake OS null guard, not actual malformed-USB robustness.
5. **Ownership/binding/concurrency:** busy exclusion does not provide a producer lease; fixture binding is not the installed board's negotiated binding. CDC/MSC/core concurrency is not run.
6. **Controller/host:** builder DCD runtime N21 and protected Arduino core runtime N22 are BLOCKED/NOT EXECUTED in this native configuration. All physical USB, host, memory/latency/task-stack behavior is NOT TESTED.

Recommended next proposal: review `stage28n-minimal-change-design.md`, then separately authorize a narrowly scoped **native-only opt-in tagged-event and checked try-submit prototype** in isolated source copies. Acceptance should demonstrate old notices cannot clear new endpoint state, early events carry creation-time identity, overflow cannot fabricate retirement, and fixture retirement/observer fences remain explicitly substituted. Keep actual controller retirement and full isolated SDK/core ABI/build verification as independent prerequisites before any production adapter. Do not automatically escalate, patch dependencies, infer host release, start Stage28O or ask for another owner Mac smoke.

Stage28M's K01 correction, conservative E capacity and fixed Planner/Runtime/compiler ceilings remain unchanged. No parser, source subset, INJECT_MOD/RESET guess, USB personality, partition or arming mechanism is added. Stock availability remains owner-confirmed externally; not a search/recovery-file acquisition blocker. Physical deployment authorization remains separate.
