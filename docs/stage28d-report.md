# Stage28D mock keyboard ownership/report planning report

**GO isolated offline review only. NOT FLASH-AUTHORIZED.**
**NO-GO Stage26 integration, Stage27A changes, flashing/boot/OTA, real HID or production adapters.**

Exact baseline: aff427ab6346433729487e5359d101ea764e5357.
Branch: stage28d-mock-keyboard-report-planning. Only this new branch is published; no next stage.
Stage27A remains independent with frozen Stage26 968c8e0aaf459b0b8b652cc57fe88225894ab64b.

## Implemented internal API, not DuckyScript syntax

New independent language_preview/keyboard.h/.cpp namespace ds_keyboard plans synthetic8-byte
snapshots: modifier mask, reserved zero and six ascending distinct keyboard/keypad page07 usages.
There is no USB descriptor/report ID/backend, OS injection, hardware driver or Runtime adapter.
Core compiler/runtime/header remain byte-identical to Stage28C. No HOLD/RELEASE/INJECT_MOD or
other commands are added; unsupported preview syntax remains unsupported. Character/KeyTap/Delay
ABI, cooperative compilation, expression continuations and multiline semantics remain unchanged.

Planner supports four persistent owners, each with six keys/eight modifier bits, and one transient
action. hold/release are idempotent. Owners sharing a usage retain it until the last owner releases.
Snapshot union must fit six; seventh-key and invalid owner/usage proposals reject without mutation.
Sorted reports are deterministic independent of acquisition order. Duplicate union snapshots
avoid extra reports while independent owner records still change. Left/right modifiers remain
separate E0..E7 bits. Raw ordinary usages04..73 are model selectors, not a host capability claim.

Transient tap/character merges persistent ownership and restores that exact union after accepted
press. Tap of an already-held usage rejects HeldTap rather than fabricating an edge by releasing
another owner. Repeated taps when unheld produce separate press/restoration pairs. All256 modifier
combinations, shared ownership, rollover recovery, named usage boundaries and exact byte vectors
are tested. No counted acquisitions/ref-counter wrap, unbounded queue or implicit cross-session hold.
Modifier masks are accepted as16-bit API inputs and reject values>255 before narrowing.

US mapping implements printable ASCII32..126 and TAB9/LF10->ENTER. Letters, digits, punctuation
and shifted symbols have explicit mapping, not a cast from text bytes to usages. Other controls,
Unicode bytes/scalars, locale/dead-key/lock-state compensation reject or are absent. This fixed
US model is deliberately narrow compared with international keyboards. Persistent SHIFT remains
active while lowercase characters are planned: resulting reports may be interpreted as uppercase;
no literal-text guarantee with held modifiers or host locks is claimed. No actual text transcription.

## Acceptance, failure, cancellation and neutral evidence

Desired logical owners, pending snapshot, last Accepted snapshot and known/uncertain-neutral
status are independent. Valid persistent transitions commit desired state upon admission; sink
Accepted alone commits acknowledged state. Ready after a tap requires accepted press AND accepted
restoration, which can still contain persistent holds. neutralConfirmed is a separate global-zero
query, and releaseRequired is its negation. Initial zero bytes are unknown, not confirmed neutral.

A new session explicitly synchronizes a neutral report. One step attempts at most one report;
Retry preserves bytes/phase and does not advance acceptance. Press acceptance queues restoration
for a later step. No real dwell/sleep, typematic or delivery guarantee. Actions share a256-attempt
and30000ms maximum, optionally narrowed; press acceptance does not reset that action budget.
Timers wrap uint32 safely and apply to pending actions, not idle persistent holds.

Failed/throwing callbacks and budget failures clear internal owners, stop ordinary actions and
conservatively mark release uncertainty. Failed phase and attempted report remain inspectable;
terminal failure diagnostics survive rejected ordinary calls. Cancel/stop clears internal owners
and pending action eligibility, never retroactively undoing an accepted press. Explicit drain
may only publish neutral under its own bounded Retry/error budget. Restart is refused until mock
neutral is confirmed, then resynchronizes; no stale owners leak. No automatic destructor cleanup.

Reentrant step/start/drain/ownership mutation reject; callback cancel is allowed. If it then returns
Accepted, that actual attempted report is still recorded, even though normal output stops. A Retry
keeps previous evidence; exception produces uncertainty. Double cancellation preserves diagnostic
phase. API is single-threaded, not cross-thread locking or ownership authentication. Callback/context
must stay valid through any future drain and return promptly; self-destruction/blocking callbacks
are outside contract. Explicit repeated recovery requests are owner actions, not internal infinite retry.

The optional Runtime adapter is NOT implemented. DELAY remains external synthetic scheduling;
a future mock bridge must complete a tap before acknowledging/consuming its following delay.
No real HID, modifier ownership or release is claimed for current Runtime events.

## References and compatibility policy

Saved Hak5 holding/keystroke/payload-control/quick-reference snapshots were hash-rechecked, and
USB HUT1.5 keyboard page07 cache reviewed/fingerprinted. References, URLs, exact hashes and
limits are in reference-evidence.json. No fresh latest-reference or official compiler/runtime
oracle claim. Four-owner idempotence, sorted six-key union, held-tap rejection, admission timing,
initial sync/drain and retry/time budgets are explicit engineering policies. Official HOLD/RELEASE
concepts informed research; their parser syntax is not silently implemented here. No proprietary
compiler copied. No complete DuckyScript3.0, international-layout, host or USB hardware parity claim.

## Fresh executed verification

| Suite | PASS groups | FAIL | Assertions |
|---|---:|---:|---:|
| Stage27B complete regression | 25 | 0 | 2543 |
| Stage28A complete continuation suite | 23 | 0 | 526 |
| Stage28B complete multiline suite | 26 | 0 | 4733 |
| Stage28C complete source/preflight suite | 17 | 0 | 390573 |
| Stage28D new planner suite | 21 | 0 | 14989 |
| Total | 112 | 0 | 413364 |

All five freshly executed suites pass ASan/UBSan and leak detection. Exact names/assertions,
stdout and commands are in test-results.md/.json. Prior runners/tests are unchanged; the new
runner links both actual core and planner. Historical production XPASS/XFAIL/observations remain
unchanged, not reused as fresh passes. Unsupported-rejection tests prove rejection, not feature
support. Group counts are not inflated per seed or per assertion.

New tests cover every modifier mask, shared key/modifier owners, six/seventh occupancy, duplicates/
invalid inputs, exact press/restore/zero bytes, all95 printable model characters with independent
literal punctuation/letter vectors, ENTER/TAB, persistent SHIFT conflicts, ordinary key boundaries
including F13/F24, retries on both press/restoration, all cancellation phases including sync/drain,
callback cancel Accepted/Retry/throw, failures/uncertainty, bounded drain, full stop/restart, reentry,
queue admission, stuck/wrapped clocks, narrowed budgets,500 seeded ownership operations and zero
C++new on the tested planner path. Previous500+400+150 source mutations and compiler EOF/cancel/
seek/borrow/preflight tests freshly pass. External sink vectors/exception machinery are outside
zero-allocation claim; no physical heap, latency or task-stack measurements.

Initial build-only issue: C++ token spelling0x1e+c/0x1e+i needed whitespace to avoid preprocessing
number interpretation. Corrected source spelling; no test expectation, cap, sanitizer or pin relaxed.
Final21 new cases include strengthened independent mapping and hostile callback tests. No remaining
unexpected failure or missing required verification tool.

## Pinned target objects and resources

Exact Arduino3.3.0/ESP-IDF5.5 original/protected core, SDK/config and Xtensa compiler/flags checks
PASS, retaining16MiB/QIO80/CPU240, PSRAM disabled, TinyUSB/USB-OTG/CDC. Compile only core.o,
keyboard.o and unlinked sizes.o;64-byte readonly sizeof dump includes16 types. No firmware ELF/BIN,
USB metadata, descriptors, installable profile or deployable firmware. Provenance/source/object/
SDK hashes and exact commands are in target-build.json/source-hashes.json.

| Target object size | Stage28C B | Stage28D B | Change |
|---|---:|---:|---:|
| Program | 6936 | 6936 | 0 |
| Runtime | 4872 | 4872 | 0 |
| CompileSession | 2408 | 2408 | 0 |
| Existing three-object total | 14216 | 14216 | 0 |
| Planner | absent | 84 | new fixed storage |
| Report | absent | 8 | three buffers inside Planner |
| Owner / OwnerTable | absent | 7 / 28 | four owners inside Planner |
| Existing objects + Planner | 14216 | 14300 | +84 |

Queue capacity is one action with press/restoration phases, not a FIFO or full text buffer. All
reports/owners are included in84B; do not count them again. No adapter type. Core sections remain
text13007/literal1856/rodata1838; additional planner sections are text2021/literal160/rodata47,
data/BSS0. These are selected module sections, not final firmware flash/RAM/OTA growth. Undefined
planner symbols are libc/exception support only, no Arduino/USB/OS/storage calls.

Planner compiler frames: step64B, ownership96B, start/tap/mapUS/character48B, snapshot32B.
No recursive report processing or large temporary; proposal28B and attempted report8B are fixed.
Conservative selected ownership chain is roughly200B plus callers/libc; sink callback and exception
handling add unmeasured cost. Existing compiler/parser stack risks remain Stage28C's measured
boundary; no physical stack high-water/latency/host operation demonstrated.

## Freeze and delivery

All235 protected Stage26 files independently compare byte-identical against frozen Git baseline.
No production source, Arduino Micro, partition, startup/arming, USB identity, storage/migration/
recovery safeguard or global core/SDK changes. Only new preview module/tests/docs and README change.
All earlier stage docs/tests remain intact.28 existing remote heads were captured and checked
before/after pushing only Stage28D; the actual count includes Stage28C joining27 previous heads.
No prior remote ref is moved or rewritten. Review exact files in stage28d-files.md.

Stage27A stays separate; original firmware is OWNER CONFIRMED — AVAILABLE EXTERNALLY. No owner
backup/private-data request/access, hardware discovery/operation, real HID or stored payload execution.

Recommended next separate milestone: mock Runtime-to-planner acknowledgement bridge with bounded
Delay/backpressure/cancel/drain behavior. Nothing in that next scope is started. Still no transport,
locale/Unicode/dead-key, lock-state, descriptor/report-ID or physical-release evidence.
**GO offline review only; NO-GO integration/flashing/boot/OTA/real HID/automatic execution.**
