# Stage28I gated roadmap — proposals, not implementation authorization

Immediate recommendation: complete disconnected owner-native Stage28H smoke and review the
ownership/acknowledgement matrix. Do not write a production adapter or replace the interpreter.
The two paths are independent: Stage27A physical work stays owner-controlled and untouched.

| Gate | Current status | Evidence required for review GO | NO-GO / stopping condition | Review/rollback boundary |
|---|---|---|---|---|
| A Native High Sierra smoke | **PENDING OWNER / NOT TESTED**; cloud SKIP_ENVIRONMENT | Owner macOS10.13.6 + native compiler/version + exit0; existing Stage28H365-assertion/3-trace/19-vector/4-negative footer, sanitized relevant diagnostics | Missing compiler/probe=SKIP, not pass; true build/trace failure=FAIL for review; another OS/compiler result doesn't prove High Sierra | Board unplugged, existing source kit only; runner removes unique temp; retain transcript locally, no files uploaded |
| B Peer review of matrix | **PENDING REVIEW** | Reviewer signs explicit choices: one report/ownership authority; ack level; protocol/callback identity; single-thread request scheduling; retained subset, numeric policy, capacity/locale/extensions; memory/lifetime plan | Any mismatch waved away as a one-line API wiring, report call treated as delivery, unknown memory/semantics silently assumed | Docs-only review; frozen Stage26 and preview unchanged. Findings reversible by documentation change on later reviewed branch |
| C Separate mock adapter contract proposal/harness | **NOT AUTHORIZED** | Separate owner-approved scope after A/B; mocked endpoint state/admitted/queued/completed/refused/stale sessions with exact bytes and error taxonomy; all Stage28H/regressions preserved | Requires real USB/files/network or firmware change; missing transaction identity/cancel/timeout/capacity policy; no current code authorization | New isolated non-device branch, no production link/transport; fail closed and stop on discrepancy; review proposed interface before implementation |
| D Minimal integration design + independent physical plan | **NOT AUTHORIZED** | Explicit separate owner approval and reviewed C results; opt-in isolation, profile/autorun/cancellation protections, evidence for pinned protocol/concurrency/peak resources; owner-approved recovery/artifact gates | Native/mock PASS alone, unsafe profile, raw callback assumptions, unreviewed table/core/USB identity change, concurrent live/OTA paths, unapproved arming | Design and read-only plan first; Stage26 untouched here. Any physical execution needs another distinct owner authorization; no automatic switch/deployment |

## Concrete future C acceptance proposal (not executed)

Define a synthetic report Sink contract before writing it. Choose whether Accepted binds queue
acceptance or correlated completion; distinguish those from host delivery. One current action,
immutable Retry bytes, no duplicate source ack, independent error cause; all four owner claims
and fresh idempotent acknowledgements preserved. Model boot/report ID selection as data, not a
real descriptor or transport. Simulate callback accepted-after-cancel, stale completion, refused
neutral, disconnect, current-zero drain and restart barriers. Do not introduce another global
TinyUSB callback, pass complete snapshots through merging beginReport, or call blocking helpers.

Specify File-reader/compile ownership separately: raw bounded bytes, stable source/context and
error/seek/EOF mapping, but no actual storage API. Existing precise
source bound is8192B, line256,128IR,4096 arena; retain exact caps until a reviewed change. Choose
which256KiB production files intentionally remain outside preview scope. Numeric wrap-vs-error
policy, US-only mapping and lost production extensions need conscious owner review, not a bridge
that silently changes language behavior. No new grammar or speculative modifier/RESET semantics.

Memory acceptance: Program+CompileSession+Bridge14364B excludes source/reader/UI/old executor.
Bridge contains Runtime and Planner: do not add them twice. Require an allocation/stack ownership
ledger and object-placement rationale before any integration build. Future full-linked/stack/
heap evidence cannot be substituted with unlinked section numbers. No predicted OTA percentage.

## Owner gate A — existing command, unchanged

From unpacked Stage28H/Stage28I repository root, EvilDuck UNPLUGGED:

```sh
bash tests/stage28h/run_host_smoke.sh
```

Existing instructions: stage28h-macos-validation.md. Optional unique local transcript there;
owner reports ONLY platform/compiler version, exit, PASS/FAIL/SKIP and sanitized relevant lines.
No passwords/tokens/paths/private images requested. Source ZIP needs no Git/Python/Arduino for
smoke, but lacks historical objects for freeze verifier. No automatic tool installs or upload.
Owner output has NOT been supplied; no inferred PASS from Linux. No Codex action on MacBook.

## Next milestone selection

Stage28J is not started. Recommended next decision is review of A/B outcomes, then (only if
explicitly approved) a precise mock report-contract milestone C. Do not leap from the preview
bridge's software correctness to replacing com/hid_backend, or bootstrap physical firmware.
Stock recovery availability remains OWNER CONFIRMED EXTERNALLY, not a search/request blocker;
physical recovery and artifact/provisioning authorization belong to the separate deployment lane.
