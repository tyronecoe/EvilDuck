# Route B keyboard control — short owner acceptance sheet

This sheet is for a future separately authorized installation and supervised test.
The candidate is **review only**. Codex has not installed, booted or physically
tested it. Do not treat a native test or successful build as host key-release proof.

Keep the existing `CAPS-STOP-TRACE-20261019-v1` application and its package available.
Its rollback SHA-256 is
`25e17cadacf3b2ab5eb5ece32fc94f4bf36fb71eb90e91814dca7f7320bd5178`.
If the installed application has changed, stop and reconcile the rollback before
installation. Preserve backups and scripts; this upgrade does not provision NVS,
format storage or change partitions. Installation and physical testing require
separate owner approval.

## Preparation

- Use a harmless TextEdit document on the macOS10.13.6 laptop. Establish Caps Lock
  OFF manually and release all physical modifiers. Account for editor text
  substitutions; the fixtures start with digits to avoid sentence capitalization.
- Use the dashboard's explicit Route B launch path, or `routeb <saved-file>` via
  the existing authenticated/USB CLI path. Ordinary CLI `run` is legacy execution
  and cannot establish Route B acceptance. Save and read back each short fixture.
- Keep the iPhone dashboard STOP control accessible. Use one explicit Start per
  trial; no autorun, automatic replay, host commands or global Caps correction.
- Record buildId, requestId/session diagnostics and host observations. Source files
  and report IDs in this package describe the candidate; they do not prove which
  image is currently installed.

## Trial A — held Shift, selective release and standalone modifier tap

Save this benign script using the implemented candidate grammar:

```text
STRING 111a
HOLD SHIFT
STRING b
RELEASE SHIFT
STRING c222
ENTER
INJECT_MOD SHIFT
STRING 333d444
ENTER
```

Expected text, under the stated host/editor assumptions:

```text
111aBc222
333d444
```

Require local Idle/Completed without a reported fault or quarantine. The modifier
tap has no printable character of its own; lowercase `d` checks for an unintended
sticky Shift after it. Exact modifier/report bytes are primarily verified by the
native mocked tests, not inferred from this text alone. `HOLD SHIFT` is the
documented EvilDuck direct-modifier extension. Bare `INJECT_MOD` is unsupported.

## Trial B — STOP during a held modifier and cooperative delay

```text
STRING 555
HOLD SHIFT
DELAY 10000
STRING 999bad
RELEASE SHIFT
```

Start once, focus TextEdit and use the iPhone **STOP script** control during the
ten-second delay. Require Idle/Cancelled and no later `999bad`. Once cancellation
has been observed, manually type `123abc` into the harmless document: lowercase
letters support release under this tested host condition. Record any delayed or
stuck modifier without automatic corrective keypresses. If STOP arrives after
the delay, label the timing inconclusive; do not describe it as a STOP defect.

This test cannot prove general USB endpoint retirement or delivery under
disconnect. Local clear submission is not a host acknowledgement. A refused or
ambiguous USB submission can quarantine the run; do not replay or continue through
that state. Retain diagnostics and stop for review.

## Evidence and stopping rules

Keep screenshots of the TextEdit results and the relevant terminal/dashboard
status, including final reason and faults. Record whether firmware and timing
stayed unchanged during the trial. Do not include credentials or private scripts.

Classify each trial independently: PASS for the demonstrated tested behavior,
FAIL for an attributable implementation defect, UNVERIFIED for insufficient
evidence, or PLATFORM-LIMITED for an identified host/tooling limitation. An
inconclusive High Sierra observation is not a universal Windows failure. Windows11
testing can add evidence later and is not a prerequisite for recognizing a valid
Mac result.

The fixed EDR1 message milestone is already accepted on this Mac configuration.
Do not repeat the broad Caps/global-flag investigation or require the laptop's LED
to mirror EvilDuck. These fixtures contain no firmware update, protocol change,
arbitrary capture, host shell command or automatic state-restoration loop.
