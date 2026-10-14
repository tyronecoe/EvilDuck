# Stage28L transport completion and execution ownership review

**GO: review this source-backed design. NO-GO: adapter implementation, production integration, live USB/HID, firmware images, flash, boot, OTA or automatic Stage28M.**

Start: exact `4532c9c5d386aa0d4a1c83cd7eeaef495f0c6e8b`, `stage28k-synthetic-report-journal`, clean worktree. Frozen Stage26 `968c8e0aaf459b0b8b652cc57fe88225894ab64b`. Delivery branch `stage28l-transport-ownership-design`, created without modifying prior refs. No unrelated work reset/discarded. Stage28L adds documentation/receipts only.

## Outcome

The recommended **PROPOSED** acceptance observation is genuine current correlated USB IN transfer success, full bound framing/length, **plus safe resource retirement**, not copying, queueing or semaphore notification. For source-bearing R, cancelled E is ineligible; explicit management drain E=0 remains eligible after source cancellation once prior work retires. The unchanged Retry/Accepted/Failed Sink can represent asynchronous polling, but existing **public transport APIs cannot safely supply the required observation**. This is a design ready for review, not an implemented or working adapter.

Fresh byte inspection confirms raw backend calls use a stack-local eight-byte keyboard payload, instance 0 and keyboard ID 1. Actual archive instructions copy payload, add ID framing and return lower endpoint submission bool. The core blocking wrapper can fail after submission and accepts a shared semaphore wake without per-action identity. Actual compiled claim path includes infinite semaphore wait; neither public route is an approved bounded cooperative sender. Existing ELF, independently matched to committed Stage26 SHA, contains strong completion and weak failure hooks. No new firmware was linked.

The pinned headers expose instance, borrowed report buffer and length; failure also exposes report type, but no genuine C/Q submission token or endpoint. Composite callback data includes report-ID framing. The class/DCD source-build relation and reset/retirement guarantees remain critical missing evidence. Cached generic upstream 0.18 C is not certified shipped SDK source and was not substituted. Current code comments and symbols do not establish reliable tokenless correlation or physical delivery.

## Proposed decisions and required proof

| ID | Proposed decision | Evidence / limitation | Next prerequisite |
|---|---|---|---|
| P01 | Accepted = current tagged success + retirement + valid action/epoch/framing | Raw copy/queue and core semaphore cannot prove it; Sink polling is expressible | Separately review a token-bearing nonblocking submit/observe/retire contract |
| P02 | Genuine monotonic C/Q bound to S/E/R; one in-flight/quarantine slot | Tokenless current callback; equal bytes, buffer address, FIFO/current slot insufficient | Exact SDK/DCD source-to-archive provenance and lifecycle/token generation proof; no guessed patch |
| P03 | Binding includes class instance, interface/endpoint, ID/protocol and wire length | Payload 8 versus ID1 frame 9; current constructor/protocol/endpoint source varies | Read-only descriptor/linked initialization evidence and future exact binding getter/service contract before real transport |
| P04 | Loop-task execution owner; copied requests/observations; urgent flags outside normal queue | Main/task/event contexts located; current async Guard can block; callbacks must not wait for executor | Later deterministic race/overflow mocks, then separately scoped RTOS/lock-context verification |
| P05 | Cancel stops source; late current completion retires only; fresh drain gates restart | Source versus transport lifetime distinct; no current public callback fence | Reviewed retirement/observer-quiescence certificate; reconnect/end/empty queue not sufficient |
| P06 | 8 requests / 4 observations; one report poll or Runtime tick per owner step | Design budgets, not implemented; 256 polls may time out before 30 seconds | Preserve strict old budgets; prove bounded sender/shared-lock and fairness behavior separately |
| P07 | No 256-report/128-intent evidence arrays in firmware by default | Prior 14,364 B objects counted once; added operational budget estimate 1536 B | Future actual target layout, full peak/stack ledger including SDK token storage; no device margin claim |
| P08 | Retain conservative E guard; exact progress only via reviewed pre-admission hook | Unchanged API cannot observe next event without private inference | Owner decision on stricter boundary or future bounded event reservation API; no implementation now |
| P09 | Reject start until setup requests/actions disposed (K01) | Stage28K start can cross admitted queue before it executes, then terminal clears requests | Later focused mock regression and separately reviewed fix; historical source/results untouched |

These are not automatically owner-approved by the earlier synthetic D01–D10 approval. Stage28M requires a separate assignment. Source modifier HOLD/RELEASE, INJECT_MOD, RESET owner scope, locale/Unicode and extensions retain previous statuses; no new language capability percentage or parser.

## New checks versus prior tests

**Executed in Stage28L:** exact baseline/parent cleanliness check; actual source-span/file hashing; independently recomputed protected core tree; patch/backend/SDK config/archive/compiler identity; existing Stage26 ELF SHA plus selected symbol/static archive instruction inspection; old Git file/path/mode comparisons; frozen 235-file verification; documentation/JSON/trace consistency; before/after remote refs and new branch identity at publication.

**Not executed:** C++/Python runtime harness, regression suites, sanitizer/leak runs, native Mac tests, target object compilation, sizeof or firmware compilation/link, SDK concurrency/transfer tests, board enumeration/HID/boot/flash/OTA. Stage28K's prior 37 groups / 10,346 assertions and separate 187 groups / 579,622 assertions remain cited prior evidence only. New Stage28L runtime groups/assertions = **0**. All 24 prospective L traces are **NOT EXECUTED**.

Source review found K01's setup/start handoff gap and carried forward the conservative E guard without repair. Actual raw/submission blocking/correlation findings are source/compiled-static observations, not measured physical bugs. No test expected outcome or historical approval cell was changed.

## Provenance and scope

Controlled Arduino 3.3.0 tree matches `81c11f59e01c1e6263d387a008d3f3211319d94feb4751ddfa11af35a2a57ed3`; HID source `b1c7130634f385d537184e9f52ec11b3a311ba4a449ae6812015eb04a0d0a0aa`; TinyUSB archive `dece5cdd1d132dabb5e2022d8e3d293592b10f03de5902d9740994d652dd9a18`; existing controlled ELF `ad94738e5625318ea7b6a710496b1ec33ed15b49c8a1fb11563241ebd240bace`. Exact original/patched core, HID companion, NVS patch, compiler and SDK hashes plus source spans are in `stage28l-evidence.json`. All checked from actual bytes, not simply copied prose claims.

Build configuration remains historical pinned USB-OTG/TinyUSB, CDC on boot, ESP32-S3/16 MiB/QIO80/CPU240/PSRAM disabled and approved partition geometry. No new build uses or changes these flags. SDK version header says 5.5.0; package identity `idf-release_v5.5-b66b5448-v1`; TinyUSB headers say 0.18.0. Version string alone does not identify exact controller source; no new upstream release or global toolchain substituted.

All **1,052 old tracked files/path/modes** compare unchanged against exact Stage28K, and **235 Stage26 protected files** pass the existing Git-derived freeze verifier. Only these eight files are added:

- `docs/stage28l-scope-and-review.md`
- `docs/stage28l-usb-source-evidence.md`
- `docs/stage28l-transport-contract.md`
- `docs/stage28l-ownership-and-recovery.md`
- `docs/stage28l-memory-and-capacity.md`
- `docs/stage28l-prospective-traces.md`
- `docs/stage28l-review-report.md`
- `docs/stage28l-evidence.json`

Prepublication receipt snapshots **36 previous remote refs**; final publication must prove every old ref unchanged and only the new branch added at delivered HEAD. The committed receipt is precommit, deliberately not self-referential; exact final SHA/post-push confirmation is supplied at delivery and separately in scratch. Final worktree must be clean.

No code, old docs/tests, Arduino Micro, core/SDK install, settings/schema, partitions, descriptors/identity, boot/storage/OTA configuration or owner files changed. Only existing caches were used, with no public source download, package installation or configuration update. Only Git integrity/publication uses network. No private backups, payloads or credentials read; no physical testing or real host/device input. Setup skill review reused the sufficient environment without changing configuration.

## Reproduction of read-only evidence

Use exact Git baseline/history and the existing controlled core/SDK/cache paths in the evidence JSON. Source anchor verification hashes each complete file and exact inclusive line span (LF-joined with final LF); core tree hashing follows unchanged `tools/patched_core.py:18–20`, excluding `installed.json`. Compare SHA values to `docs/stage18-dependency-pin.json` and Stage26 controlled build provenance. No patch/install/build command is required or authorized.

Safe inspection commands already used:

```sh
git rev-parse HEAD
git status --porcelain
python3 tests/stage28h/verify_freeze.py
```

Existing pinned `xtensa-esp32s3-elf-ar x` extracts only `hid_device.c.obj`, `usbd.c.obj` and `tusb.c.obj` from the current verified TinyUSB archive **into a new scratch directory**. `xtensa-esp32s3-elf-objdump -dr` and `-nm -S/-C` inspect these and the already existing Stage26 ELF; exact commands/tool hashes/selected symbols are in JSON. Do not compile/link, execute extracted objects, replace archives or treat generic tagged source as the shipped revision. If critical cache/provenance is absent, preserve UNKNOWN/BLOCKED rather than fetch a different release.

Old tree/path/mode consistency is checked against `git ls-tree -r -z 4532c9c5d386aa0d4a1c83cd7eeaef495f0c6e8b`, `git show <base>:<path>` and current filesystem/Git diff. New paths must be only `docs/stage28l-*`. Save `git ls-remote --refs origin` before/after, then use unchanged freeze verifier's `--remote-before/--remote-after` and explicit only-new-ref/HEAD comparison. No new checker file is added.

## Next milestone and readiness

The narrow next **proposal** is a separately authorized memory-only transport-state harness exercising L01–L24, truthful tokenless rejection, completion/retirement distinction, queue saturation, cancellation ordering and K01 start barriers. It cannot establish the real SDK supplies genuine tags/fences. In parallel or before any production change, recover exact shipped SDK/DCD source provenance and verify the smallest bounded submit/observer/retirement API change; do not guess a patch or add a strong duplicate callback. No automatic Stage28M.

The design is concrete and reviewable, but **real adapter implementation/integration remains blocked** by missing genuine correlation/quiescence, source lifecycle provenance, bounded-send proof and exclusive producer/thread/metadata requirements. Device recovery/profile/artifact authorization remains independent. Original stock availability is owner-confirmed externally, not a discovery blocker. No executable installation/recovery instructions provided.

**GO: Stage28L design review only. NO-GO: adapter implementation, production integration, live USB/HID, firmware images, flash, boot, OTA or automatic Stage28M.** Stop for owner review.
