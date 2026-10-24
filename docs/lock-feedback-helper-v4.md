# Mac LED-action helper v4 — diagnostic-only update and one manual trial

This source-only ZIP fixes the native executable path while retaining the existing sanitized diagnostics.
It contains no firmware or installer. **Do not reflash, change EDR1, or change
Caps timing.** Keep the working firmware, rollback and previous evidence.
Physical testing remains owner-operated and requires separate approval.

Expected installed build: `ROUTEB-LOCK-FEEDBACK-20261023-v1`; application artifact
SHA-256 `ae079c5a1b0c10849bdf79c12a40e5f0f3a01fb50996e4499f5352b91b1c9a5d`.
That is an installer/artifact identity, not a new readback of the board. Stop if
the installed build differs. This helper does not authorize installing firmware.

## 1. Prepare on High Sierra before starting any script

Use existing Python 3.8.10 and Apple command-line tools on macOS 10.13.6. Download
`evilduck-routeb-lock-led-action-v4.zip` using the commit-pinned link in the
publication receipt. Check against that receipt's SHA-256 and byte size:

```bash
cd "$HOME/Downloads"
wc -c evilduck-routeb-lock-led-action-v4.zip
shasum -a 256 evilduck-routeb-lock-led-action-v4.zip
```

Stop on a mismatch. Use a fresh directory, preserving all old files:

```bash
LED_WORK=$(mktemp -d "$HOME/Desktop/evilduck-led-helper-v4.XXXXXX")
unzip -n "$HOME/Downloads/evilduck-routeb-lock-led-action-v4.zip" -d "$LED_WORK"
cd "$LED_WORK"
sw_vers -productVersion
python3 --version
clang --version | head -n 1
clang -std=c99 -Wall -Wextra led_action.c -framework IOKit -framework CoreFoundation -o led-action-native
file led-action-native
```

Stop if any preparation step fails. No downloads, installation, sudo or security
bypasses are needed. Mach-O x86_64 confirms architecture, not successful native
execution, IOKit access or LED delivery. The C source is unchanged. V4 resolves the script location first, then checks and invokes an absolute sibling executable. Relative Python invocation, another working directory and directory names containing spaces no longer cause PATH-based lookup of a different executable. The sibling itself is still rejected if it is a symlink or is not executable. Apple SDK
compilation/execution of this package is not established by the Linux checks.

Connect the Mac and iPhone to the existing dashboard network. For the separately
approved trial, use the same USB-connected owner board. Its recorded serial is
`3CDC757483C0`, VID/PID `303A:1001`; use this serial only for that confirmed board.
If the device is different, stop until its serial is confirmed. Do not select an
arbitrary keyboard. Keep the fixed-message receiver unarmed.

## 2. Save the existing fixture; authenticate before Run

On iPhone dashboard **Home → Script editor**, save the following harmless fixture
under a new name such as `lock_wait_caps_on_v4.txt`, using the established storage
selection. Press **Save** only. Keep autorun off; do not press **Start receiving**.

```ducky
DELAY 15000
WAIT_FOR_CAPS_ON
STRING 111
ENTER
```

Open a blank TextEdit document on the Mac. In the same Terminal directory, start
the helper with a fresh log (omit `--request`):

```bash
LED_LOG=$(mktemp "$HOME/Desktop/evilduck-led-wait-v4.XXXXXX")
set -o pipefail
python3 -u led_action.py --serial 3CDC757483C0 --command WAIT_FOR_CAPS_ON --value 1 2>&1 | tee "$LED_LOG"
LED_EXIT=${PIPESTATUS[0]}
printf 'helper exit: %s\nlog: %s\n' "$LED_EXIT" "$LED_LOG"
```

Enter the dashboard password privately at its prompt; never put it in a command,
log, screenshot or public report. Require successful preflight, then type
`APPLY ONCE` only under the owner's separate physical-test approval. Require:

`READY: authentication and native-file checks complete. No LED action sent.`

Leave the **Assigned request ID** prompt open. Password entry, authentication,
idle/receiver checks, native-file checks and consent have all occurred before
the fixture starts. The helper never starts scripts or predicts request IDs.

## 3. One bounded, manual retest

1. On iPhone press the saved fixture's **Run** exactly once. Read its actual
   `Request N accepted / queued` ID; do not use an old or predicted number.
2. Enter that ID at the waiting Mac prompt, aiming for **within about 10s** of
   Start. Immediately switch to TextEdit during the **3s** focus countdown.
3. Keep iPhone **STOP / check execution** accessible. The helper requires the
   exact owned Running request and wait, matching boot/session, two matching
   captures, captured wait age under 1000ms, and final checks under 1s. It attempts
   at most one native invocation; there are no action retries or automatic replay.
4. Preserve the complete Terminal log, helper exit, assigned ID, same request's
   final dashboard status, and TextEdit screenshot. Note date, macOS version,
   reported build and that firmware was unchanged. Share only sanitized relevant
   output; no password, private scripts, configuration or backups are requested.
5. On any error, timeout, cancellation or late request, stop and preserve partial
   evidence. Do not restart automatically. Ctrl-C cancels the host wait; dashboard
   STOP remains the script cancellation control. Keep the existing safety limits.

The 15s preparation DELAY and 5s active WAIT remain unchanged. The 3s focus
countdown is unchanged. Synthetic ID-entry tests at 0, 2, 10, 12.2 and 12.999s
reach one invocation in the first second of the wait; entries at 13, 15, 17 and
21s are refused in that model. Aim for about 10s, not the modeled boundary.
Human response time, native process launch and physical High Sierra latency
are not guaranteed. A missed window is a safe refusal, not permission to weaken
the checks. The final HTTP check/action is not atomic with device STOP.

## 4. Read the diagnostic without overclaiming

On error, one JSON `HELPER_ERROR` record identifies a fixed `phase`, `operation`
and bounded `sequence`, allowlisted `exceptionClass`/`causeClass`, numeric `errno`
or null, and a fixed `category`. HTTP errors may add numeric `httpStatus`. If
cleanup also fails, the original failure remains primary; only an allowlisted
`secondaryExceptionClass` is added. No raw error text, URLs, headers, credentials,
response bodies, paths or subprocess arguments are emitted by these diagnostics.

| Phase / category | Interpretation |
|---|---|
| `PREFLIGHT_IDENTITY`, `PREFLIGHT_STATUS`, `PREFLIGHT_CONFIRM` | Failure before READY / manual Start. No native invocation. |
| `WAIT_INITIAL_IDENTITY` | Initial post-countdown identity read failed. No native invocation. |
| `WAIT_POLL_STATUS`, `WAIT_POLL_IDENTITY`, `WAIT_RECHECK_STATUS` | Poll or final identity/status read failed. No native invocation. |
| `HTTP_OPEN`, `HTTP_READ`, `HTTP_CLOSE` | Operation distinguishes connection/open, response read or cleanup failure. |
| `HTTP_TIMEOUT`, `CONNECTION_REFUSED`, `HTTP_ERROR` | Network timeout, refusal or HTTP status; none establishes an IOKit failure. |
| `NATIVE_SUBPROCESS_SPAWN` / `NATIVE_INVOCATION_IO_ERROR` | Invocation raised an OS error; no returned native exit. Not proof of HID delivery. |
| `NATIVE_TIMEOUT_RESTORATION_UNVERIFIED` | Native subprocess timed out. Do not assume restoration or replay it. |
| `NATIVE_SUBPROCESS_RETURN`, event `NATIVE_RETURN` | Native subprocess returned; `helperExit=N` is its actual return code. |
| `REQUEST_ALREADY_TERMINAL`, `WAIT_TOO_LATE_NO_ACTION`, `WAIT_CHANGED` | Request safety refusal; no action replay. |

The selected native executable path is absolute even if this Python script was invoked relatively. Native lookup does not use PATH. Markers are stored in memory before I/O, not printed on every poll or before the
action. No new console logging delays the final check-to-invocation interval.
The retained `IO_UNAVAILABLE` text is accompanied by the structured diagnostic;
read both lines. A returned `helperExit=3` is distinct from a launch exception.
An OS launch exception alone does not prove that no child ever briefly existed.

`helperExit=0` establishes native API acceptance/restoration attempt only. Require
the same request's **Completed** status plus the expected `111` line before
calling this scoped WAIT trial successful. Deadline at line 2/code 26 establishes
wait expiry, not that the Mac transmitted an LED report. Missing or ambiguous
evidence is UNVERIFIED; a demonstrated host limitation is PLATFORM-LIMITED.
Native return, current LED evidence and WAIT completion are separate observations.
None proves global Caps behavior, USB wire delivery, host key release, general
platform compatibility or EDR1 roundtrip success. No broad Caps investigation is
part of this update.
