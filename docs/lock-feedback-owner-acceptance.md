# Prior physical keyboard-control acceptance — scoped evidence

Host: owner's MacBook, macOS 10.13.6. Owner-observed build:
`ROUTEB-KEYBOARD-CONTROL-20261022-v1`, source baseline
`bbc83640a264c6398d396fdca564804f62ece117`.
The rollback artifact is 1,406,016 bytes, SHA-256
`de0d34d577cbaebb31bdeff825bd264d527f6c894103d6e0ed66140022016cf3`.
This identifies the known public build, not a new flash readback.

Trial A supplied text: `111aBc222` then `333d444`. **PASS for exact host
text**, supporting selected HOLD SHIFT, RELEASE SHIFT and inline INJECT_MOD SHIFT.
The owner separately confirmed the contemporaneous completion/status record is
saved. That record has not been supplied for inspection here: **full status
criterion UNVERIFIED pending review of the saved record**. No rerun is requested.

Trial B supplied text: `555` then owner-manually typed `123abc`. Owner reports
`999bad` absent. Supplied iPhone screenshot shows `RouteB_Keyboard_Test_B` and
`Request 2: Cancelled [Caps 500ms captured]`. **PASS for this cancellation trial**:
STOP interrupted the held-Shift delay, forbidden text was absent, and subsequent
manual lowercase worked. Source dashboard terminal classification requires Idle
and relinquished ownership. This is observed application/host behavior, not a
USB wire capture or proof of release during disconnect or ambiguous transport.
The 500ms label is the captured ordinary CAPSLOCK setting; neither trial issued
CAPSLOCK.

The supplied A/B text files and screenshot remain owner evidence; no private
settings, backups or credentials are required. Existing published evidence and
packages are unchanged. The prior fixed-message EDR1 physical acceptance remains
a distinct milestone. Its 408-report receipt and later 820-report screenshot
must not be combined into one run.

These physical results do not validate the new lock-feedback candidate. No new
hardware activity has occurred during this implementation.
