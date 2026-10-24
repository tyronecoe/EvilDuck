# Host helper v4 — absolute sibling native path

Baseline source: `32e22650f98faec03ebdce71446e9f48e8d39fe5`.
This is a host-only fix; it does not rebuild firmware or change the native C,
EDR1 protocol, authentication or LED action/restoration behavior.

## Proven path defect and correction

V3 used `Path(__file__).with_name('led-action-native')`. With a relative script
path, the file checks can find a local executable while subprocess receives the
bare `led-action-native` string. That string is looked up through PATH rather
than automatically selecting the checked file in the current directory. The
owner's absolute-script invocation workaround succeeded on High Sierra.

V4 resolves the script's location strictly, then constructs an absolute sibling
path. It retains regular-file/executable checks and checks `is_symlink()` on the
unresolved sibling leaf; it does not resolve away the symlink before refusing it.
The selected absolute path is passed as one subprocess argument, preserving spaces.
No directory is added to PATH and no shell is introduced. No new path override or
command-line capability is added. Selection remains subject to ordinary filesystem
TOCTOU limitations; the file is not cryptographically authenticated at execution.

All existing consent, private password-header authentication, exact assigned
request, boot/session, receiver, STOP, fresh-wait and final-recheck conditions
remain unchanged. Timeouts, polling, focus countdown, one native invocation and
no-retry/no-replay behavior are unchanged. Diagnostic privacy remains unchanged.

## Focused verification

`python3 -m unittest discover -s tests/lock_feedback -p 'test_*led*.py' -v`
executes **55 current-helper checks, zero failures**, plus one separately
classified expected historical v1 undefined-base64 control: 56 unittest methods.
The five new methods exercise relative and absolute script paths, a different
working directory, spaces, missing/nonexecutable native files, native symlink
refusal, and script-symlink resolution to the real script's sibling. Full-main
path cases assert the exact absolute subprocess argument and exactly one mock
invocation. All HTTP/native calls and timing are mocked; synthetic path fixtures
are created only in temporary directories and are never executed.

The package verifier retains v2 and v3 guide identities/test patterns; v4 includes
the added path tests. The final archive receipt must verify exact source commit,
four source-only members, checksums, README shell syntax and Python 3.8 grammar,
then rerun the tests on extracted source. Publication requires a separately
downloaded, byte/hash-checked ZIP. Those receipts do not prove a new physical run.

Native Apple compilation/execution of v4 remains unverified. Linux tests use mocks
and do not establish macOS 10.13.6 IOKit behavior, host-global Caps restoration or
wire delivery. ASan/UBSan are not applicable to this Python-only change; native C
and firmware are not rebuilt for this fix.

## Supplied physical observations

The owner reports that absolute invocation worked on macOS 10.13.6 using the
existing `ROUTEB-LOCK-FEEDBACK-20261023-v1` firmware. Record observations separately,
not as a merged fictitious session:

| Observation | Native API evidence | TextEdit evidence | Dashboard evidence | Boot/session | Classification |
|---|---|---|---|---|---|
| Request 8 | Screenshot: apiAccepted=true, restoreApiAccepted=true; native return/helperExit=0, sequence 507 | Owner reports expected `111`; screenshot contains two `111` lines but does not encode their request IDs | No Request 8 completion screenshot supplied | Unknown | Native API return evidenced; exact same-request completion unverified |
| Request 9 | Screenshot stops at assigned-ID prompt | No independently attributable result | Not supplied | Unknown | Unverified |
| Request 1, later absolute invocation | Owner-supplied terminal screenshot: API acceptance/restoration true, global restoration false; helperExit=0, sequence 537 | Expected `111` visible, owner attributes it to trial | Separate owner-supplied iPhone screenshot: Request 1 Completed | Unknown | Request-ID-level corroboration of scoped WAIT/typing completion; boot/session correlation unverified |
| Separate HTTP401 attempt | Preflight identity / HTTP_OPEN; no action authorized by that failed preflight | Not applicable | Not applicable | Unknown | Authentication refusal, not native/HID failure |

Request numbers can repeat after reboot. No boot marker or feedback-session value
is visible in these screenshots, so matching request numbers alone cannot prove
same-boot/session identity. Preserve the owner-reported attribution and the limits.
Screenshots do not constitute a firmware readback. The installed artifact identity
remains owner-reported build `ROUTEB-LOCK-FEEDBACK-20261023-v1`, application SHA-256
`ae079c5a1b0c10849bdf79c12a40e5f0f3a01fb50996e4499f5352b91b1c9a5d`.

No broad Caps investigation or repeat physical trial is required to establish this
path correction. If a separately approved targeted trial is chosen, use the
[exact High Sierra setup and bounded procedure](lock-feedback-helper-v4.md), keep
the working firmware installed, and preserve actual request/boot/session evidence
where available. Native API acceptance, TextEdit output and correlated dashboard
completion remain separate observations. Neither local restoration API success
nor WAIT completion proves host-global lock state or host key release.

## Delivery boundaries

The v4 host ZIP contains Python, unchanged C, README and manifest only. It remains
bound to the current lock-feedback build; it is not a helper authorization for a
different future firmware build. Keep the working firmware, rollback, prior ZIPs,
backups and physical evidence. No hardware access, reflash, automatic execution,
EDR1 changes or unrelated capabilities are part of this fix.

## Final packaged-source verification

Source commit: `dbd6fe3fed98115e55f6c1c9e78ae0eeb153ee2d`.
ZIP: `evilduck-routeb-lock-led-action-v4.zip`, **12,422 bytes**.
SHA-256: `a76f2074247f4aaf702e91a73431abffb1e9f8dc353a4147602848d693abb726`.
The actual extracted ZIP source passed all 55 current checks and the separately
classified historical v1 control. CRC, exact four-member inventory, committed
source hashes, unchanged native C, README Bash syntax and Python 3.8 AST checks
passed. A second package build produced byte-identical output. See
`lock-feedback-helper-v4-artifact.json` and `lock-feedback-helper-v4-tests.json`.
Publication/download verification must be recorded separately after retrieval of
the genuine commit-pinned ZIP; these local checks do not assert publication.

Published v4 download verified: the genuine commit-pinned ZIP at
https://raw.githubusercontent.com/tyronecoe/EvilDuck/069652b65e631f0f56f3d689afd2d38f49d98d24/downloads/evilduck-routeb-lock-led-action-v4.zip
was downloaded and its exact12,422byte size, SHA-256 and extracted source were checked. The downloaded source passed55currentchecks plus the separate historicalv1control. This repeats artifact verification, not additional distinct tests or a physical Mac trial. See lock-feedback-helper-v4-publication.json. Existing hardware evidence describes v3 with the owner's absolute-path workaround; it does not establish that v4 itself has physically run.
