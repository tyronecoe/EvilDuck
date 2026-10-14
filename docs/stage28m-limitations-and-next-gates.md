# Stage28M limitations and next gates

**GO:** review the executed memory-only transport-state harness and isolated K01 correction.

**NO-GO:** production adapter integration, live HID/USB, firmware images, board access, flash/boot/OTA or automatic Stage28N. No source parser, unsupported grammar, descriptors, partitions or deployment profiles changed. Stage27A/owner hardware work remains independent and owner-controlled.

Real readiness blockers, individually:

1. **Source-to-object attestation:** release package/member identities, recorded builder/TinyUSB revisions, selected DCD source, five identical headers and static evidence are established. A clean exact source working tree/full compile recipe or equivalent independent source-to-object verification is still missing. No SDK rebuild was attempted.
2. **Authentic correlation:** shipped DCD event/class/core APIs lack C/Q. Snapshot equality, FIFO, callback-time slot tagging and buffer addresses are not identities. Mock Q carries through scheduled notices by construction only.
3. **Bounded sender:** infinite claim/release mutex waits, DCD spinlocks and hardware-dependent loops exist. Strict bounded refusal/ownership behavior is unproven; existing raw/core APIs cannot just be renamed NotSubmitted/Submitted.
4. **Retirement and quiescence:** completion, unplug/reset, queue empty, begin/end and reconnect do not provide the mock's separate transfer/observer certificate. Controller/FIFO/buffer and callback lifetime require a dedicated exact-stack investigation.
5. **Ownership/concurrency/binding:** all raw/legacy producers must be excluded by a real reviewed lease; task/ISR ordering, descriptor/protocol binding and CDC/MSC contention remain unresolved. Deterministic interleavings are not RTOS race tests.
6. **Host/device acceptance:** no physical USB behavior, OS release, host layout, latency, runtime heap/task-stack or installed profile was measured. No successful mock drain proves TextEdit/macOS state.

The memory model explicitly retains a conservative E-capacity guard. L20's exact final Delay/non-event pre-admission variant is BLOCKED/UNSELECTED, not executed or counted as a compatibility pass. Current unsupported source modifiers, INJECT_MOD/RESET and locale/Unicode features retain earlier classifications.

Recommended narrowest next **proposal for separate review**: inspect/pin the publisher's exact build recipe and select one stack-level token/retirement design, then authorize an isolated native component harness for the actual DCD→event→class lifecycle, with bounded submission and no production integration. Review the Stage28M contract/K01 fix first. Do not jump from a mock PASS to an application adapter, install a patched dependency, rerun the owner's Mac smoke or flash anything automatically. If exact lifecycle evidence remains unavailable, document the blocker rather than guess a patch.

Original stock firmware availability remains owner-confirmed external; not a search/availability blocker. Backups and recovery resources remain untouched. Any future deployment needs its own artifacts/recovery/authorization review; this stage supplies none of those authorizations.
