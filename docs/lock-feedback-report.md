# Route B lock feedback and cooperative waits — review candidate

Implemented on isolated branch `routeb-lock-feedback-v1` from
`bbc83640a264c6398d396fdca564804f62ece117`. Existing published firmware and
historical profiles are preserved. New buildId:
`ROUTEB-LOCK-FEEDBACK-20261023-v1`. **No hardware access, installation, flashing,
OTA, actual host LED actions or HID output occurred.** New physical behavior is
UNVERIFIED; preparation is not installation authorization.

## Prior physical evidence

[Owner acceptance](lock-feedback-owner-acceptance.md) records Trial A exact text
PASS, with full completion/status evidence UNVERIFIED pending inspection of the
owner's saved record. Trial B PASS is limited to the supplied Cancelled request
2 screenshot, absence of forbidden output and successful manual lowercase after
STOP on macOS 10.13.6. These are not wire/retirement guarantees. The EDR1 physical
milestone remains separate and is neither reopened nor combined across runs.

## Implementation and decisions

[Compatibility](lock-feedback-compatibility.md) specifies exact variables,
commands, freshness, eager expression evaluation, timeout and failure semantics.
Five fixed read-only internal operands integrate with the existing evaluator;
no new expression parser, symbol expansion, language fallback or dynamic registry
was added. Nine no-argument ON/OFF/CHANGE commands use a separate cooperative
5000ms wait state, never the existing 1000ms transport-pending state.

Source is an exact additive ten-file composed overlay in
`tests/lock_feedback/application.patch`; before/after identities are in its
`source-manifest.json`. Root production sources and historical preview/tests
are unchanged. The actual selected production call paths are:

- `core.cpp` Expression::next/parse recognizes fixed internal names and emits
  `ExprKind::Internal`; Runtime::evaluationStep resolves exactly once through
  Adapter::internalRead into hid_backend::lockEvidence.
- Compiler emits Op::LockWait; Runtime::completeInstruction delivers the retained
  EventType::LockWait to Adapter::receive/Adapter::wait. Sink Retry yields.
- hid_backend::receiveLockReport updates the new fixed evidence only after the
  existing registered keyboard/report/type/length/session validation, under the
  existing FeedbackGuard. Boot/session/report/time/mask/transitions are copied
  coherently. No independently locked diagnostics are joined as device truth.
- invalidateLockState resets evidence for lifecycle changes. Report/transition
  overflow, session wrap or backward evidence time latch unavailable until boot.
  Legacy LockState's historical semantics and counters remain unchanged.
- Existing Adapter::finish, route_b cancellation, backend lease and priority
  clearing own every terminal path. Waiting does not yield the execution lease.
  STOP polling, owner scheduling, HTTP and independent EDR1 servicing remain
  cooperative. No automatic lock toggles, repair, SAVE/RESTORE or arming exist.
- coordinator publishes bounded wait command/start/session fields into its
  existing coherent request status; authenticated handleStatus serializes them
  with request ID and capture timestamp. Neither stale cached state nor local
  cleanup is relabelled host evidence.

The compact observation guard contains fixed copies/counter work and one
existing ESP Timer timestamp sample. It introduces no new queue, lock ordering
against diagnostics, storage calls or unbounded retries. Target disassembly and
native tests cover the newly linked path; real critical-section latency remains
unmeasured.

## Fresh offline verification

| Suite | PASS | Unexpected FAIL | Assertions |
|---|---:|---:|---:|
| New N01–N44 production-source cases | 44 | 0 | 1,349 |
| Unchanged selected regressions (including Q01–Q37) | 140 | 0 | 6,559 |
| Separate Python host-action policy tests | 11 | 0 | not counted as C++ assertions |

Native total: **184 PASS, 0 unexpected FAIL, 7,908 assertions**. ASan, UBSan and
leak detection passed. Four missing/zero profile-selector controls were correctly
rejected, separately from pass counts. New coverage includes all wait families,
unknown/stale/duplicate/rapid transitions, nonselected bits, entry deadlines,
uint32 time wrap, saturation, boot/session changes, malformed source, function
continuations, STOP and cleanup backpressure, concurrent callback publication,
EDR1 coexistence, authentication and zero-allocation evidence reads.

M27 still expects the previous absence of Route B lock support. Its unchanged
old binary passed (8 assertions), and its unchanged fixture rejected this new
capability (original FAIL retained in
`lock-feedback-historical-observation.json`). It is superseded by explicit new
success/refusal tests, not silently relabelled PASS. The first broad new run
recorded 181 PASS plus that one historical mismatch; the final selected run
excludes it and retains the separate observation. Earlier E18/K23 ownership
refusals and W34's obsolete auth-contention expectation remain documented
history. Historical language XPASS, USB XFAIL and Stage 9 observations are
unchanged; this focused stage does not claim to have rerun every historical
suite.

Intermediate harness builds exposed a namespace/main-name collision, one missing
allocation header and an enum-switch diagnostic. All were corrected; the final
strict compilation and sanitizer run pass. The superseded first target build is
not packaged. The final candidate was cleanly rebuilt. No failure is hidden by
reducing compiler flags or changing historical test source expectations.

## Build, resource and provenance

| Measurement | Working keyboard build | New candidate | Delta |
|---|---:|---:|---:|
| Compiler program bytes | 1,405,867 | 1,407,859 | +1,992 |
| Application BIN bytes | 1,406,016 | 1,408,000 | +1,984 |
| Static RAM | 111,992 | 112,120 | +128 |
| Free bytes in each 7,602,176-byte OTA slot | 6,196,160 | 6,194,176 | −1,984 |

Free OTA: **81.478987%**. Application SHA-256:
`ae079c5a1b0c10849bdf79c12a40e5f0f3a01fb50996e4499f5352b91b1c9a5d`.
ELF SHA-256:
`f1f3f83aa461dd2bd35658d558434fd020de30b29aca4122cf8aa33acfdff780`.
Unchanged table SHA-256:
`b79bde9ef4a9544411d97a31a1d326b2028213269ad0dcc643ea921230ce3d5e`.

Clean Arduino ESP32 3.3.0 / pinned SDK archive build uses ESP32-S3, 16MiB custom
partitions, PSRAM disabled, existing USB-OTG/CDC/CPU/flash settings and the approved
isolated USB/NVS patches. Final post-link evidence verifies 177 unchanged SDK
archives, 284 inputs, 13 linker scripts, three response files, exact final source
pins, profile flags, linked ownership and feedback/wait call edges, startup and
ELF-to-BIN identity. Test-only injection is absent from the target. Global core
and SDK installations were not modified.

Compiler frame estimates: new wait 96B and evidence snapshot 32B; existing
Runtime evaluation 144B, Adapter step 144B and receive 64B unchanged; owner tick
384B versus 368B; status handler 432B versus 400B. These are individual compiler
frames, not measured call-chain high-water. Native 64-bit sizes are separately
reported in `lock-feedback-resources.json`; Adapter owns Runtime/Program/compiler
and must not be double-counted. Physical heap, stack high-water and latency were
not measured. Fixed static growth is modest; existing HTTP String allocation and
bounded cleanup/quarantine limitations remain.

## Package, rollback and next review

The app-only Mac review ZIP binds this image, exact source pin and rollback to
`ROUTEB-KEYBOARD-CONTROL-20261022-v1`, 1,406,016 bytes, SHA-256
`de0d34d577cbaebb31bdeff825bd264d527f6c894103d6e0ed66140022016cf3`.
The rollback is the retained public artifact corresponding to the owner's working
build, not a new device readback. Old packages and backups remain untouched.
Public-package fault injection passed 39 cases and the actual bound installer
passed 38 mocked cases, both with zero failures. These executed no physical
operations. Package and mocked-installer results are published separately;
see `lock-feedback-package-tests.json`, `lock-feedback-installer-tests.json` and
`lock-feedback-artifacts.json`. The app-only installer still requires separate
owner approval, a fresh private backup, exact identity/security/table/OTA checks,
typed confirmation, bounded slot writes and independent verification. It cannot
perform partition migration, auto-repair, OTA or automatic reboot.

The separate one-action LED helper is a future Num/Caps IOKit fixture, not an EDR1
sender or a key injector. Its Python policy is mock-tested; native Apple compilation
and hardware delivery are **UNVERIFIED**. It has an explicit target request,
action and serial, bounded polling, duplicate status/session checks, no automatic
Start/replay and best-effort selected-element restoration. A STOP can still race
the last host-side check; neither watchdog exit nor API acceptance proves
restoration or receipt. The old EDR1 host kits' strict identity/idle safeguards
remain unchanged. See [owner check](lock-feedback-owner-check.md).

**GO:** source/package review and planning a separately authorized short
High Sierra acceptance. **No hardware installation or test is authorized here.**
Unresolved: new physical lock feedback/waits, Scroll capability, delayed packet
attribution across reconnect, native Apple helper verification, global lock-state
meaning, and host release under loss/ambiguous transport. A platform limitation
must not be treated as universal failure. Windows validation can follow later.
Do not implement SAVE/RESTORE or another feature group before review.
