# LED-action helper v3 — failure-boundary diagnostics

Baseline: `ed9971a4b00cb3cf267d52f5e6e32304347b0db1`.
Branch: `routeb-lock-led-helper-diagnostics-v3`.
This is a host-only update. No firmware, native C, LED protocol, timing policy,
installer, Arduino/SDK dependency, partition or USB identity was changed or built.
No owner's Mac, board, real HTTP endpoint or HID interface was accessed in testing.

## Evidence and correction

The owner's handoff reports READY followed by `IO_UNAVAILABLE` or
`REQUEST_ALREADY_TERMINAL`, six successful authenticated read-only HTTP probes,
and request 7 expiring at WAIT line 2/code 26. Those are owner-reported results,
not reproduced physical observations here. They establish neither a successful
native invocation nor LED delivery. Mach-O x86_64 establishes architecture only.
No specific network, IOKit or firmware cause can yet be selected from that evidence.

V3 distinguishes fixed phases for preflight identity/status/confirmation, initial
post-countdown identity, wait poll, final identity/status recheck, native invocation
and native return. HTTP open, context entry, read and cleanup are distinct
operations. Markers are bounded in memory; successful poll markers are not logged.
No additional console I/O occurs between the final freshness check and invocation.

On errors, JSON emits only a fixed phase/operation/category, bounded sequence,
allowlisted exception/cause class and numeric errno or null. HTTP status is numeric.
URLError reasons are inspected only as exception objects, with bounded unwrapping;
raw strings, URLs, headers, credentials, response content, paths, subprocess
arguments and dynamic class names are never included. Policy messages use a closed
set of literal codes. A first read failure remains primary even if closing the
response also fails; only a sanitized secondary class is added. Broken diagnostic
stdout gets one best-effort stderr fallback, with no new action or replay.

Socket timeout, connection refusal, HTTP error, native invocation OS error, native
timeout and returned `helperExit=N` have distinct evidence. A spawn exception does
not establish IOKit behavior or prove that no child briefly existed. A returned
code 3 is not relabeled as an HTTP/launch failure. Native return 0 continues to
mean API acceptance/restoration attempt, not device completion or global Caps proof.

## Preserved policy and timing

The exact password-header authentication, APPLY ONCE consent, real assigned ID,
expected build, boot/session binding, receiver safety and owned Running request
checks remain. Observed STOP/terminal/stopping/session changes refuse action.
The captured wait must be under 1000ms; final checks must take under 1s. HTTP
timeout remains 0.5s, native subprocess timeout 5s, poll interval 0.1s, bounded
polling 30s/301 iterations, and focus countdown 3s. There is at most one native
invocation, no automatic script Start, no action retries and no automatic replay.

The existing fixture remains DELAY 15000 / WAIT_FOR_CAPS_ON / STRING 111 / ENTER;
the active firmware wait remains 5s. Prepared mode places password/consent/setup
before the owner starts the fixture. Aim to enter the actual ID within about 10s.
The existing synthetic timing boundary tests still pass, including safe refusal
of late entries. Neither a human timing guarantee nor measured Mac latency is
claimed. HTTP checking is not atomic with STOP or subsequent USB state changes.

## Verification and classification

Executed suite: `python3 -m unittest discover -s tests/lock_feedback -p 'test_led_*.py' -v`.
**50 current-helper checks PASS, zero FAIL**, plus **one separate expected
historical v1 undefined-base64 negative control**; 51 unittest methods total.
Repeated source, extracted-package and downloaded-package runs are the same
checks, not additional distinct passes. No assertion-count inflation is claimed.

The 15 new diagnostic methods include 56 phase/open-or-read/error-type subcases
(seven semantic phases × two operations × four injected failures); each asserts
zero native attempts and no retry. Additional checks cover HTTP401/409, context
entry/close and double failures, malformed JSON, sanitization, unknown exception
classes, bounded errno excluding Boolean values, native launch faults/timeout/
return 3, per-launch trace reset, bounded markers, post-action-only logging and
broken stdout before action. The original 35 current-helper checks are unchanged.
All networking, native calls, Darwin checks, clocks and manual ID entry are mocked.

Python 3.8 grammar, README Bash syntax, archive members/CRC/source hashes and
unchanged native C are checked. Linux execution uses Python 3.12.14 and Bash 5.2.37;
this is not native High Sierra/Python 3.8 execution. Native Apple SDK compilation,
IOKit behavior and physical LED/WAIT success remain **UNVERIFIED**. ASan/UBSan are
not applicable to the Python-only change; C and firmware were not rebuilt.

The ZIP verifier accepts an explicit v3 guide identity, retaining the v2 default
and its historical test selection. Final package and publication receipts record
the actual archive hash, exact committed source and successful downloaded-byte
verification, only after those operations execute.

## Changes and preservation

Only existing `tests/lock_feedback/led_action.py` and
`tests/lock_feedback/verify_host_package.py` change. Added files are the diagnostic
test module, this report, the v3 owner guide, v3 preservation/test/artifact/
publication receipts and the new source-only v3 ZIP. Prior docs, tests, packages,
working firmware and rollback remain unchanged. The separate preservation receipt
checks baseline bytes and modes; Stage26 freeze checks all 235 protected files.
Remote refs are independently snapshotted and compared before/after publication.

Native C SHA-256 remains
`bf1691e838b16818eb7e7fb6d038a715ad6b90c8855f2cb066ecdd656b37f640`.
Working firmware ZIP remains
`97e64ecd165be2b05bd0610953651a923e44f74635a100baf427b84f3bf2655d`;
its application artifact remains
`ae079c5a1b0c10849bdf79c12a40e5f0f3a01fb50996e4499f5352b91b1c9a5d`.
Keyboard-control rollback remains
`de0d34d577cbaebb31bdeff825bd264d527f6c894103d6e0ed66140022016cf3`.
No private backup, settings, credentials or owner scripts enter this package.

## Owner review and next evidence

[Exact High Sierra preparation and one manual retest](lock-feedback-helper-v3.md)
retain the existing clang command, private password input, actual request ID,
focus countdown, dashboard Run/STOP and evidence requirements. Only separately
approved owner operation may perform that physical test; nothing is run remotely.

**GO:** review/download the host-only diagnostic package. For a separately approved
single manual trial, preserve the complete sanitized terminal log, helper exit,
same request's final dashboard status and TextEdit output. A scoped success needs
both native evidence and same-request Completed/expected `111` output. Deadline
alone remains wait expiry, not HID delivery. Missing evidence is UNVERIFIED;
identified host constraints are PLATFORM-LIMITED. There is no basis for claiming
this update fixed the physical problem before collecting the new diagnostics.

No firmware changes, reflashing, altered timing, EDR1 changes, automatic retry or
broad Caps investigation are needed or authorized by this host-only correction.

## Final source-only package verification

ZIP: `evilduck-routeb-lock-led-action-v3.zip`, **12,096 bytes**.
SHA-256: `2e67ca6e2f924793e7b2633c32d4fd0e9599942a4691939fe217df1d086a4ecd`.
Source commit: `a3e8019c988eeac373109e5fa8ffb349294d7745`.
The actual extracted ZIP source passed all 50 current checks and the separate
historical v1 control. Its four members are README, Python, unchanged C and a
source/hash manifest; there is no executable or firmware. A repeat package build
produced identical bytes. The v2 default verifier was also rerun on the unchanged
v2 ZIP and retains its 35 current checks plus historical control, zero failures.
See `lock-feedback-helper-v3-tests.json` and `lock-feedback-helper-v3-artifact.json`.

The preservation check independently confirmed **1,881 baseline files/modes
unchanged**, excluding only the two explicitly modified host-helper/verifier files,
and 235 frozen Stage26 files unchanged. These are not hardware measurements.

Reproduce the v3 archive check without any device access (results path must not
already exist):

```bash
python3 tests/lock_feedback/verify_host_package.py --archive downloads/evilduck-routeb-lock-led-action-v3.zip --guide docs/lock-feedback-helper-v3.md --results /tmp/NEW-led-helper-v3-results.json
```

GitHub download verification and previous-remote-ref comparison are recorded in
the publication receipt after successful publication; assembly alone is not
substituted for checking downloaded bytes.
