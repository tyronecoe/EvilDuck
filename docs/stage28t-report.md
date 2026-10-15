# Stage28T — native Route B through the actual HID backend

**GO: review the native proof and default-off patch proposal. NO-GO: production
integration/deployment, firmware builds, live USB/HID or physical operations.**

Parent `5355b4dd76fe57884fb9036348f218dd28634958` was verified clean before work.
Branch: `stage28t-native-real-backend-route-b`. Changes are exclusively new
`tests/stage28t/*` and `docs/stage28t-*` files. No historical firmware, preview,
test, patch, partition, installed dependency or global toolchain was changed.

## Answer to the assignment

The selected conservative local contract is implementable in the native boundary
using actual com and hid_backend state, without Stage28S's fake backend outcome
guarantees or a core/DCD change. Scratch queueRaw now observes whether the lower
API was called and its Boolean return. Known precall refusal may be polled;
called-false or transport loss causes real backend quarantine with first-fault
identity retained. Even fail/end/cancel/update cannot issue another lower report
under that quarantined lease. Both fixture false cases receive the same policy.

An explicit session/operation/thread-scoped lease guards actual backend ingress
as well as com. Callback reentry, another host thread, stale operation IDs, raw
helpers, foreign persistent ownership and pending clearing are rejected. A
source-backed legacy gap was found: raw Keyboard software ownership is separate
from Owned. Native acquisition now conservatively refuses it until explicit
legacy software release followed by fresh synchronization. This is not a claim
that the host received a release.

Runtime, grammar, limits and S's whitelist remain unchanged. Actual scheduler
press/dwell/restoration is required before matching local acknowledgement; Delay
belongs to Runtime. Native a/a and a/b verify every report byte, ID1 and instance0.
Actual backend merging/validation, clearing, errors and loss processing execute.
Lower USB/core/RTOS/platform services are mocked; no real USB stack executes.

## Fresh verification

| Category | PASS | Unexpected FAIL | Assertions |
| --- | ---: | ---: | ---: |
| Stage28T primary | 47 | 0 | 467 |
| Unchanged Stage28S, separately run once | 56 | 0 | 512 |
| Affected actual production regression cases | 77 | 0 | 67,371 |
| Same77 cases with final prototype disabled, exact comparison | 77 | 0 | 67,371 |

Six static preparation/fault controls pass separately. Primary and regressions
use ASan/UBSan and leak detection with no unexpected diagnostics. Intentional
negative assertion exits1 and is separately classified. Development failures
and fixes are disclosed in the test report; final results supersede them without
changing assertions. Historical language XPASS, USB XFAIL and model observations
were not relabeled or added to these counts. No generic model or owner Mac rerun.

gcov records actual queueRaw9,445, beginReport162, releaseReport144, update11,130
and cancelReport130 calls. Partial source line coverage: scheduler47.07%,
backend45.61%, preview84.51%, scheduler seam98.28%, lease100%; no complete branch,
USB/core or physical behavior claim. Full per-case traces and function counts are
in the JSON receipts.

## Resources and lifetime

Native Adapter22,592B includes Program6,936B, CompileSession2,416B,
Runtime4,888B and source8,193B; no Bridge/Planner or duplicate accounting.
Adapter is static, not on the simulated loop-task stack. Scheduler owner80B,
backend lease136B and per-thread permission24B are fixed storage. Allocation
measurements include platform/fixtures: a/a9 ordinary C++ allocations/309B,
ASCII sweep31/11,119B. No target allocation, stack high-water, firmware RAM/flash
or OTA measurement was performed. Full limitations and placement proposal are
in the lifetime ledger.

## Remaining integration blockers

- Real task ownership/affinity, callback scheduling, mutex wait and lifecycle
  exclusion have not been established by host-thread tests.
- Direct core/DCD calls and actual web/settings/file/OTA/storage transactions
  can sit outside the prototype lease. Production entry points must be reviewed
  as a whole; com busy is not a complete service isolation mechanism.
- File dispatch, source diagnostics/UI stop/running state and target ABI/resources
  need a separately authorized integration design. The native patch uses host
  thread identity and is not ready to enable on target.
- No physical readiness, report protocol/layout negotiation, host delivery,
  neutral receipt or endpoint retirement is demonstrated. Strict A remains
  UNRESOLVED and the support draft remains UNSENT.

The smallest useful next proposal is a review of concrete task/service ownership
and explicit file/dispatch integration, retaining this local contract. Do not
automatically begin Stage28U or require a new generic retirement model to accept
these native results. Physical migration remains unauthorized.

## Artifacts and integrity

The source/patch manifest records exact original inputs, intermediate S outputs,
final scratch outputs, both patch hashes, include hashes, native executable
identities and read-only protected-core/SDK source verification. This dependency
check is source evidence, not a target build. Native executables and full vendor
trees are not committed. The combined production-review-only patch was applied
only to fresh external originals and checked against all four final hashes.

The integrity receipt is **PRECOMMIT**, with its own hash excluded. Final commit
and publication confirmation are external to avoid self-referential evidence.
All44 prior refs must match after publication, with only this new branch added.
All1,186 parent files/paths/modes and235 frozen Stage26 files remain unchanged.
Unified diff blank context has its mandatory single-space format; only that
exact format is excluded from Git's trailing-whitespace check.

### New file inventory

Documentation:

- `docs/stage28t-owner-scope.md`
- `docs/stage28t-backend-outcome-contract.md`
- `docs/stage28t-producer-inventory.md`
- `docs/stage28t-source-and-patch-manifest.json`
- `docs/stage28t-resource-and-lifetime-ledger.md`
- `docs/stage28t-test-report.md`
- `docs/stage28t-test-results.json`
- `docs/stage28t-coverage.json`
- `docs/stage28t-production-integration-proposal.md`
- `docs/stage28t-report.md`
- `docs/stage28t-integrity.json`

Native fixture and review patches:

- `tests/stage28t/adapter.cpp`, `adapter.h`
- `tests/stage28t/allocations.cpp`, `allocations.h`
- `tests/stage28t/backend_lease.h`, `backend_lease.inc`
- `tests/stage28t/candidate.patch`, `production-review-only.patch`
- `tests/stage28t/lower.cpp`, `lower.h`, `mocks/USBHID.h`
- `tests/stage28t/prepare_sources.py`, `check_preparation.py`
- `tests/stage28t/resource_probe.cpp`
- `tests/stage28t/run_tests.py`, `run_regressions.py`
- `tests/stage28t/scheduler_seam.h`, `seam.inc`
- `tests/stage28t/test_main.cpp`, `verify_scope.py`

No hardware access, firmware generation, real HID output, owner payload execution,
backup access, support communication or Stage28U work occurred.
