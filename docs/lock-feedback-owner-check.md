# Future owner acceptance — separate physical approval required

**No installation, hardware use or host LED action is authorized by preparing this
package.** Keep the current keyboard-control package and backups unchanged.
Rollback is the owner's working `ROUTEB-KEYBOARD-CONTROL-20261022-v1` artifact,
SHA-256 `de0d34d577cbaebb31bdeff825bd264d527f6c894103d6e0ed66140022016cf3`.
The new candidate is `ROUTEB-LOCK-FEEDBACK-20261023-v1`.

After a separately approved installation and benign idle check on High Sierra:

1. Save a harmless fixture with exactly `DELAY 15000`, then `WAIT_FOR_CAPS_ON`,
   then `STRING 111`, then `ENTER`. No held keys, shell shortcuts or private text.
   Keep autorun off and the EDR1 receiver unarmed. Focus a new TextEdit document.
2. Prepare the optional helper command in Terminal with the serial and command
   filled in. Manually start the fixture exactly once on the iPhone. Read the
   **actual assigned current request ID** from the dashboard acknowledgement/status
   during the 15-second DELAY, fill that ID into `--request`, and launch the helper.
   Do not predict the next ID: file/service transactions can also consume IDs.
   Enter the password privately and explicitly type `APPLY ONCE`. It polls at most
   30s for that specific active wait, then attempts one selected LED output plus
   restoration after 200ms. It retains the initial boot/session identity and refuses a change. It never
   starts a script or arms a receiver. Actual
   WAIT lifetime is still 5s; the helper does not extend it. If late, mismatched
   or already terminal, preserve the refusal and do not automatically replay.
3. Preserve terminal output, dashboard request/status, host text and timestamps.
   `111` and Completed for that request support the tested wait path. API success
   alone is not device receipt. A stale cached dashboard is not evidence.
4. Repeat only as separate explicitly reviewed trials for CAPS_OFF, NUM_ON/OFF
   and CHANGE. For CHANGE first establish a fresh opposite baseline, then the
   selected different bit value during the active same-session wait. Do not
   assume the built-in keyboard or its LED mirrors EvilDuck's output interface.
   For the helper's CHANGE action the explicit `--value` must differ from that
   observed baseline. Scroll requires separate direct-output capability evidence;
   do not improvise a Caps/Num substitution.
5. Test unknown/no-reply OFF timeout without treating it as OFF, and an external
   dashboard STOP during `HOLD SHIFT` / `WAIT_FOR_CAPS_ON` / `STRING 999bad`.
   For the latter **do not run the LED helper**: STOP before expiry, require
   Cancelled, absent `999bad`, and deliberate manual lowercase typing afterward.
   Retain request ID, final ownership/fault status and observation times. This
   supports only that host/trial, not disconnect retirement.

Optional helper compilation on the owner's Mac, only after review/approval:

```bash
clang -std=c99 -Wall -Wextra led_action.c -framework IOKit -framework CoreFoundation -o led-action-native
python3 led_action.py --serial ACTUAL_SERIAL --request ACTUAL_ASSIGNED_ID --command WAIT_FOR_CAPS_ON --value 1
```

Replace placeholders; do not paste credentials in commands. The helper sources
are in the separate `evilduck-routeb-lock-led-action-v1.zip`. No compiler or
Python installation/download is automated. Its native Apple portion is **not
executed or compiled against an Apple SDK in the Linux cloud**. Python3.8 syntax
and mocked policy tests pass; native Mac behavior remains UNVERIFIED. Missing
IOKit elements, OS refusal, latency or unavailable feedback should be recorded
as UNVERIFIED/PLATFORM-LIMITED when causation is unresolved, not universal FAIL.

The helper uses a non-seizing interface-specific IOKit LED element, report ID 1,
not key injection. It attempts selected-element restoration even after uncertain
API failure. A watchdog/kill/disconnect can prevent restoration: preserve that
uncertainty. It does not prove restoration of global Caps state. STOP may race
the last HTTP check and host action; there is no cross-host atomic ownership
transaction. Use only this supervised harmless fixture, no arbitrary running
payload. HTTP status/identity are bounded separate samples, not a USB wire proof.
If an HTTP 409, changed session, receiver activity or mismatched request occurs,
stop and preserve evidence; no automatic replay or recovery write is performed.

Do not repeat the broad Caps investigation, change EDR1, or use SAVE/RESTORE.
Windows 11 platform checks can follow later. No waiting indefinitely for it.
