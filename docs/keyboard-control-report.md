# Route B keyboard-control candidate v1

## Outcome and review boundary

Implemented actual selected Route B support for inline `INJECT_MOD modifier` and
bounded persistent `HOLD` / `RELEASE`, including local STOP/terminal cleanup.
The clean target build and final linked-image checks pass. This is a review
candidate, not an installed or physically verified keyboard upgrade.

Base: `cb3a147719850a0dc4a4797b401b606ea14c6571`.
Branch: `routeb-keyboard-control-v1`.
New buildId: `ROUTEB-KEYBOARD-CONTROL-20261022-v1`.
The prior installed application is unchanged and remains the exact rollback.

The [compatibility inventory](https://github.com/tyronecoe/EvilDuck/blob/routeb-keyboard-control-v1/docs/keyboard-control-compatibility.md) separates the
installed Route B, legacy and standalone preview implementations. The current
dashboard Run, library Run and Save & Run select Route B explicitly; ordinary
CLI `run` and HTTP without an engine selector still use legacy. Parser recognition
or legacy linkage is not counted as selected Route B support.

The owner-operated fixed-message milestone is already accepted on the tested
High Sierra hardware. Its original receipt and later-repeat iPhone screenshot
remain separate evidence; see [owner acceptance](https://github.com/tyronecoe/EvilDuck/blob/routeb-keyboard-control-v1/docs/keyboard-control-owner-acceptance.md).
It is not a new-keyboard-feature test or a general Caps-state guarantee.

## Exact implemented grammar and behavior

| Form | Candidate behavior and limits |
| --- | --- |
| `INJECT_MOD CONTROL` / `CTRL` | One modifier-only tap; report modifier byte1, no ordinary usages; then restore held state |
| `INJECT_MOD SHIFT` | Modifier byte2 |
| `INJECT_MOD ALT` / `OPTION` | Modifier byte4 |
| `INJECT_MOD GUI` / `WINDOWS` / `COMMAND` | Modifier byte8 |
| `HOLD key`, `RELEASE key` | One existing named physical key, lowercase letter, digit or supported modifier token per statement |
| Direct `HOLD SHIFT`, `RELEASE SHIFT` and other supported modifiers | Explicit EvilDuck extension; no ambiguous bare-prefix semantics inferred |
| Bare `INJECT_MOD`, numeric operands, modifier lists, extra operands | Reject during full preflight, including inactive branches/unused functions |
| `RESET`, `RESTART_PAYLOAD`, packed `INJECT_VAR` | Remain unsupported on Route B; no board reset or speculative encoding |

The modifier vocabulary is the existing Route B **left-side** set above. Internal
storage has eight modifier bits, but that does not add right-side source aliases.
Physical nonmodifier ownership retains the existing lowercase/digit domain and
named-key vocabulary, including F1–F24 and navigation/editing names. Uppercase
single-character ownership is not silently treated as shifted text. No new
punctuation, Unicode, locale or chord grammar is invented.

Repeated HOLD and release of an unheld key are logically idempotent but receive a
fresh, correlated report submission for their current operation. Aliases share a
physical usage. Six distinct ordinary keys is the maximum; an offending seventh
key fails before it is submitted or partially added. Runtime failure then invokes
the existing bounded neutral cleanup.

Held modifiers merge by OR with transient text/chord modifiers. Transient release
restores the held report. A transient tap of an already-held physical usage,
including a modifier-only tap of that held modifier, rejects instead of faking a
release/repress edge. Other modifiers in a real key chord may overlap intentionally.
Holds survive cooperative delays, conditionals, loops and function returns.
Completion, STOP_PAYLOAD, external STOP and runtime errors clear script ownership.

## Production integration and safety

The eight-file additive composition layer follows the exact preserved Caps/STOP
candidate. The existing compiler/runtime already represented Hold/Release events;
this change provides the real adapter and scheduler/backend implementation before
removing their former capability refusal. Inline taps use a modifier-only KeyTap
event, not a legacy command-string fallback.

The backend reuses its fixed modifier byte and six usage bytes. New admissions
and ownership calls require the current lease, task, operation and permission
scope. Legacy hold/release entry points remain denied during a Route B lease.
No new worker, report queue, dynamic ownership table or USB descriptor is added.

HOLD commits only after positive local submission. RELEASE drops logical ownership
and keeps the current operation's bounded target ahead of later ordinary output.
NoCall/readiness backpressure can retry that pending operation; an ambiguous
CalledFalse or transport loss retains the existing quarantine and prevents replay.
Cancellation clears intent and performs the existing priority neutral cleanup.

Local submission, scheduler completion and cleanup are not USB host acknowledgement,
physical key-release proof or restoration of latched Caps Lock. A disconnected or
quarantined transport cannot be described as having released host keys. Existing
permanent ambiguity handling is preserved rather than bypassed for convenience.

The opt-in500ms ordinary CAPSLOCK profile, default5ms behavior, HTTP authentication,
bounded status locking, request correlation, single owner, storage/deletion guards,
settings/NVS protections and application startup remain in the inherited composition.
The EDR1 ingress/decoder,17-byte restriction,CRC, RAM bounds and explicit arming are
unchanged; native receiver regressions and concurrent held-key/receiver coverage
pass. No broad Caps/global-flag investigation was restarted.

## Executed verification

| Suite | PASS | Unexpected FAIL | Assertions |
| --- | ---: | ---: | ---: |
| New composed keyboard-control Q01–Q37 | 37 | 0 | 1,049 |
| Selected inherited production-source regressions | 82 | 0 | 5,243 |
| Version-bound host-workflow checks | 5 | 0 | not instrumented |
| Existing host workflow/package regressions | 56 | 0 | not instrumented |
| Actual unchanged dashboard view/download functions | 15 | 0 | 195 |
| Package corruption, bounds and metadata checks | 39 | 0 | not instrumented |
| Bound installer with simulated device/tool results | 38 | 0 | not instrumented |

The119 C++ cases pass ASan, UBSan and leak detection. They exercise exact eight-byte
reports/reportID1, alias/dedup behavior, overflow atomicity, fresh operation
acknowledgements, held/transient restoration, STOP during delay/admission/release,
permission failures, disconnect/ambiguity, no cross-run replay, functions/control
flow and fixed-message receiver operation. They run actual composed modules with
mock USB, storage, clocks and task identities, not the full RTOS or physical USB.
Missing and zero candidate selectors fail compilation as intentional negative
controls. The Python host checks are not sanitizer tests.

Historical capability-refusal fixtures E18/K23 are explicitly replaced by feature
tests, not relabeled as previously supported. An initial selected W34 fixture
failed on **both unchanged baseline and candidate**: it expects401 during auth
contention, while the recorded bounded-lock contract returns409. Its obsolete
expectation was already superseded in `http-snapshot-report.md:90–97`. That
observation is retained separately; current H09/H10/H18 auth/busy tests and other
selected HTTP progress regressions pass. No production change was made to satisfy
W34, and no historical source or classification was rewritten.

The final focused selection comprises272 passing cases/groups and zero unexpected
failures, with6,487 instrumented C++/Node assertions; Python assertions are not
instrumented. Package and installer tests use actual assembled release images and
helpers with disposable public copies and simulated device/tool responses. No
esptool hardware dispatcher or serial port is opened. Their separate receipts
record actual execution. After incorporating these results in the review package,
the package checks are repeated against the final archive without counting them
twice or rerunning the unchanged target build.

## Clean build and resources

Approved isolated Arduino ESP32 core3.3.0 archive-feedback profile; pinned ESP-IDF5.5,
Xtensa GCC14.2.0; ESP32-S3/16MiB custom geometry; PSRAM disabled; existing
USB-OTG/TinyUSB/CDC and CPU/flash settings. Global toolchains are untouched.

| Measurement | Prior application | New candidate | Change |
| --- | ---: | ---: | ---: |
| Compiler program bytes | 1,404,495 | 1,405,867 | +1,372 |
| Actual application BIN | 1,404,640 | 1,406,016 | +1,376 |
| Static RAM | 111,992 | 111,992 | 0 |
| Free bytes per OTA slot | 6,197,536 | 6,196,160 | −1,376 |
| Free OTA percentage | 81.523185% | 81.505085% | −0.018100 points |

Existing compiler stack-frame estimates remain com::update80B, Adapter::step144B
and route_u::tick368B. New ownership backend64B, ownership admission80B and modifier
admission48B estimates are not summed into a measured task high-water value. The
loop stack selection remains8192B. No new persistent ownership allocation or
unbounded queue is introduced; physical heap, latency and stack measurements are
unavailable for this candidate.

- Application SHA-256: `de0d34d577cbaebb31bdeff825bd264d527f6c894103d6e0ed66140022016cf3`
- ELF SHA-256: `b99c9223e2d6a7e2a3c9eec4a092a146bbf5704b188cbaa97393aaed9d5a4bf8`
- Source patch SHA-256: `000d87359ff5ecc7448763448fb0e79eb320cb4e925f0f5ef6019a634e2fbcb5`
- Partition BIN SHA-256: `b79bde9ef4a9544411d97a31a1d326b2028213269ad0dcc643ea921230ce3d5e`

Final closure checks cover284 linked inputs,177 unchanged SDK archives, three
response files and13 linker scripts. They verify exact before/after source hashes,
compiled copies, mandatory selector, real adapter calls into modifier/ownership
admission, ownership permission/submission calls, inherited USB/NVS/startup guards,
and ELF-to-BIN integrity. New hash-pinned wrappers document their exact source-ID
adaptations; the historical verifiers and dependency predicates remain intact.
Full hashes and commands are in `keyboard-control-build.json` and native receipts.

## Package, rollback and remaining gates

The review package contains only application update/rollback images and public
support files. The intended future application locations are0x10000 and0x750000,
each inside its0x740000 slot. Candidate sector-rounded ranges are
`[0x10000,0x168000)` and `[0x750000,0x8A8000)`. Bootloader, table,NVS,OTA,SPIFFS
and coredump are excluded. Expected partition bytes are a read-only template,
not a planned table write. The installer retains fresh metadata/security/chip
checks, a new private backup, explicit confirmation, independent comparisons,
numbered progress and no automatic retry/reboot. Narrow supported OTA metadata
checks remain; unexpected metadata stops for review rather than being repaired.

Rollback is the exact current known1,404,640-byte application,
SHA-256 `25e17cadacf3b2ab5eb5ece32fc94f4bf36fb71eb90e91814dca7f7320bd5178`.
Reconfirm identity before a future installation if the board has changed.

The original host kit intentionally pins the old firmware buildId. It remains
unchanged. An optional separately bound host kit changes only the expected buildId
for this candidate; protocol, pacing, authentication and validation are byte-
identical. This avoids weakening the identity check and does not require an
automatic repeat of the already accepted LED milestone.

**GO:** source/package review and offline verification.
**NO-GO:** installation, boot, OTA or real HID testing without separate owner
authorization. Native High Sierra installer execution and new keyboard behavior
remain physically unverified. The short [owner sheet](https://github.com/tyronecoe/EvilDuck/blob/routeb-keyboard-control-v1/docs/keyboard-control-owner-check.md)
is the proposed acceptance, not an executed test. Windows11 remains unverified;
its temporary unavailability does not invalidate the earlier Mac milestone.

Next useful release: interface-specific lock variables/reply indication and bounded
cooperative waits with explicit unknown/stale/session semantics. Save/restore,
RESET/restart, random/jitter and USB/storage changes stay distinct reviewed groups.
Do not implement the next group automatically.

All1,805 baseline tracked files,235 frozen Stage26 files, the old composed sources
and current rollback remain unchanged. Publication must add only this branch and
new artifacts, with all65 previous remote refs compared before/after. No hardware,
flash/erase/OTA, real payload, owner-file modification, filesystem formatting or
dependency installation occurred in this software work.
