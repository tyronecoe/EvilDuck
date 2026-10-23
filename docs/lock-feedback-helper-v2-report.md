# LED-action helper v2 correction — host only

Baseline: `e306108377a10ae3205a6db1d40cd0abe3d91b3a`.
Branch: `routeb-lock-led-helper-v2`. No firmware source, overlay, image, protocol,
partition, descriptor, native C source or installer was changed or rebuilt.
No board, owner's Mac, HID interface or physical device was accessed.

## Proven defect and correction

The actual retained published v1 ZIP is 6,947 bytes, SHA-256
`3135e2cd8d65f2dbefdeefcf0a8f5f02edf117568de4a59f6cab7e4e729f931d`.
Its `led_action.py` is byte-identical to the baseline repository file and contains
`token=base64.b64encode(...)` without importing base64. `token` has no consumer;
real authentication uses `X-Duck-Password`. A controlled execution of v1's actual
packaged `main()` reproduces the expected NameError before networking/native calls.
That defect is not counted as a working v1 capability.

V2 removes the dead calculation entirely. Existing authenticated endpoints
`/status` and `/led-test` and the password header remain unchanged. No Basic-auth
fallback or new interface is introduced. Full-main tests now exercise startup,
password acquisition, authenticated reads, confirmation, manual request entry and
the native subprocess boundary, all using injected mocks.

## Ready before Start and timing

Interactive `--request` is now optional. With it omitted, the helper first checks
the compiled native executable, obtains the password privately, verifies the
expected build/USB/receiver and idle execution, binds boot/session identity, and
obtains explicit APPLY ONCE consent. Only then does it print READY and prompt
for the actual assigned request ID after the owner manually starts the fixture.
No script Start or receiver arming is automated. The compatibility option
`--request N` accepts only an already assigned owned request, not a predicted ID.

A new 3s host focus countdown after ID entry lets the owner switch from Terminal
to TextEdit before the fixture can type. It does not alter firmware DELAY or WAIT
semantics. The script remains DELAY 15000 / WAIT_FOR_CAPS_ON / STRING 111 / ENTER.
All slow setup occurs before Start; only reading/entering the ID and focusing the
editor remain within the preparation window. Aim for ID entry within about 10s.

The helper requires the exact owned Running request/command/session twice, retains
the preparation boot/session, and rejects captured wait ages >=1000ms using
uint32 device timestamps. Final identity/status verification taking >=1s is
refused. These conservative host checks leave nominal margin within the unchanged
5000ms device wait; they are not a real-time transport guarantee. HTTP samples,
process launch and IOKit are not atomic with STOP. An unobserved STOP can still
race the final check/action; observed terminal/stopping state is refused.

Synthetic full-main tests cover ID entry at 0, 2, 10, 12.2 and 12.999s plus the
3s focus countdown: one native invocation during the first active-wait second.
Entries at 13, 15, 17 and 21s are refused without invocation in that model. This
establishes the software schedule, not measured operator or physical Mac latency.
The former procedure could not justify fitting launch/password/consent into 15s;
v2 removes those tasks from the window. No unconditional human-timing claim is
made. Missed windows are preserved as refusals, never automatically replayed.

## Focused verification and evidence

The source tests execute **35 current-helper checks, zero failures**, plus one
separately classified expected-v1-NameError control. They cover the complete
interactive and explicit-request paths, exact password-header/no-Basic auth,
missing executable/password, HTTP401/409 without retry, idle and receiver guards,
manual ID validation, boot/session changes, terminal/wrong request, observed STOP,
wait-age boundaries/wrap, slow/invalid clocks, EOF/Ctrl-C, native refusal/timeout
and exactly one attempted native action. Python3.8 grammar and documented Bash
syntax are checked. No tests invoke real HTTP or the real native helper.

The final archive verifier reruns those tests against **the Python file extracted
from the ZIP**, checks CRC/exact members/manifest/source-commit hashes, rejects
any remaining base64/token AST reference, and checks that native C is unchanged.
See the versioned package-test receipt after assembly for the actual ZIP hash
and executed results. Source-only test results are not substituted for packaged
source verification. Native Apple SDK compilation and physical High Sierra
behavior remain UNVERIFIED. ASan/UBSan are not applicable to these Python-only
changes; the unchanged native C and firmware were not rebuilt.

Preservation audit: 1,871 baseline files/modes unchanged, with only the three
explicit host helper/packager/test files modified; all other changes are new
host-only docs/tests/archive. Frozen Stage26 verification passes for 235 files.
The original application ZIP remains SHA-256
`97e64ecd165be2b05bd0610953651a923e44f74635a100baf427b84f3bf2655d`.
Its application remains
`ae079c5a1b0c10849bdf79c12a40e5f0f3a01fb50996e4499f5352b91b1c9a5d`;
rollback remains
`de0d34d577cbaebb31bdeff825bd264d527f6c894103d6e0ed66140022016cf3`.
Native C SHA-256 remains
`bf1691e838b16818eb7e7fb6d038a715ad6b90c8855f2cb066ecdd656b37f640`.
Historical branches, packages, evidence and backups are preserved.

## Delivery and owner procedure

Use only the new `evilduck-routeb-lock-led-action-v2.zip`, not v1. No replacement
firmware package is needed. The archive contains Python, unchanged C, README and
manifest, with no credentials, private values or executable firmware. Packaging
binds committed source; publication must be verified by downloading the genuine
commit-pinned GitHub asset and comparing exact size/SHA-256. The publication
receipt records this only after successful retrieval.

[Exact High Sierra setup and trial instructions](lock-feedback-helper-v2.md)
cover SHA verification, a new extraction directory, the existing clang/IOKit
build command, private password input, explicit consent, actual request ID,
focus countdown, manual iPhone Run/STOP and evidence preservation. No compiler
installation, credential disclosure or automatic replay is requested. If the
expected firmware is not already installed, stop; this correction does not
authorize installing it. Native API acceptance/restoration is not device WAIT
completion, global Caps restoration or host key-release proof.

GO: review the corrected host package and use the controlled procedure only
under the owner's separate physical-test approval. No installation, reflashing,
EDR1 changes or broad Caps investigation is required or authorized by this fix.


## Final packaged-source verification

The actual v2 ZIP is **9,758 bytes**, SHA-256
`2522b09650d400e2f01eab43613525581a3d3b0f36df6bae3f7dbe16dc2c7d98`.
Source commit: `e274a34c8213e98b6996f2679cbd009e7bc07e3d`.
`verify_host_package.py` extracted this archive and executed 35 current-helper
checks plus the expected historical v1 NameError control, all with zero unexpected
failures. CRC, exact four-member inventory, committed source hashes, README Bash
syntax and Python3.8 AST checks passed. A repeat build produced identical bytes.
See `lock-feedback-helper-v2-tests.json`. The old invalid commit argument used in
an initial packaging invocation was rejected before any archive was created;
only the exact verified Git HEAD was used for this package.

Reproduce the final archive check without hardware:

```bash
python3 tests/lock_feedback/verify_host_package.py --archive downloads/evilduck-routeb-lock-led-action-v2.zip --results /tmp/NEW-led-helper-v2-results.json
```

The result path must not exist. This runs only mocked launch tests, never a
physical helper or firmware builder. The GitHub publication receipt is added only
after downloading and checking the genuine commit-pinned ZIP.


Published ZIP download verification: **PASS**, exact size/SHA-256 and source
inspection. The downloaded Python source also passed the 35 current checks and
expected v1 control. These repeated runs validate the artifact, not extra distinct
features or physical behavior. All 67 pre-existing remote refs remain unchanged.
See `lock-feedback-helper-v2-publication.json` for the genuine immutable URL.
