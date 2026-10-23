# Mac LED-action helper v2 — High Sierra setup and one deliberate trial

This is a **host-helper correction only**. It does not contain firmware, an
installer or an updater. No board access or flashing was performed to prepare it.
Use physical actions only after the owner's separate test approval. Do not
reflash or change EDR1 for this correction. Keep all existing packages/backups.

Required existing firmware buildId: `ROUTEB-LOCK-FEEDBACK-20261023-v1`.
Its application artifact SHA-256 is
`ae079c5a1b0c10849bdf79c12a40e5f0f3a01fb50996e4499f5352b91b1c9a5d`.
This is an artifact identity, not a device readback. If a different build is
installed, the helper refuses; this guide does not authorize changing it.

## 1. Download and prepare before starting the script

Download **evilduck-routeb-lock-led-action-v2.zip**, not v1. Verify its SHA-256
against the separately published checksum/download receipt. The original v1
ZIP is retained as history and must not be used: it has an undefined `base64`
reference. V2 removes that unused calculation and retains the actual
`X-Duck-Password` authentication header.

On the MacBook (macOS 10.13.6; existing Python 3.8.10 and Apple command-line tools),
open Terminal. Assuming the ZIP is in Downloads:

```bash
cd "$HOME/Downloads"
shasum -a 256 evilduck-routeb-lock-led-action-v2.zip
```

Stop if the hash does not match the published receipt. Extract into a new,
uniquely named directory, without modifying previous downloads:

```bash
LED_WORK=$(mktemp -d "$HOME/Desktop/evilduck-led-helper-v2.XXXXXX")
unzip -n "$HOME/Downloads/evilduck-routeb-lock-led-action-v2.zip" -d "$LED_WORK"
cd "$LED_WORK"
sw_vers -productVersion
python3 --version
clang --version | head -n 1
clang -std=c99 -Wall -Wextra led_action.c -framework IOKit -framework CoreFoundation -o led-action-native
```

Do not continue if compilation fails. No dependencies are downloaded or installed.
The unchanged native C file has not been compiled against an Apple SDK in the
Linux cloud. Missing compiler/framework capability is UNVERIFIED/PLATFORM-LIMITED,
not evidence of universal firmware failure. Do not use sudo or disable security
controls to bypass a refusal.

Connect the Mac and iPhone to the existing EvilDuck dashboard network. Keep the
USB-connected EvilDuck available to the Mac, as required by the separately
approved trial. The helper checks the actual device interface using the explicit
serial, VID 303A / PID 1001, keyboard usage and report-ID-1 LED elements. The
previously recorded serial is `3CDC757483C0`; use that value **only for that same
owner-confirmed board**. Otherwise substitute its confirmed serial. Never select
an arbitrary matching keyboard.

## 2. Prepare the harmless fixture without running it

On the iPhone dashboard Home, in **Script editor**, choose a new filename such as
`lock_wait_caps_on_v2.txt`, retain the established storage selection and enter:

```ducky
DELAY 15000
WAIT_FOR_CAPS_ON
STRING 111
ENTER
```

Press **Save** only. Keep autorun off. Do not press Run yet. Leave the fixed-message
receiver unarmed: do not press **Start receiving**. No held modifiers or other
scripts should be active. Open a new TextEdit document on the Mac.

## 3. Authenticate and consent before the 15-second clock starts

In the same Terminal directory, create a new evidence log and launch v2 without
`--request`:

```bash
LED_LOG=$(mktemp "$HOME/Desktop/evilduck-led-wait-v2.XXXXXX")
set -o pipefail
python3 -u led_action.py --serial 3CDC757483C0 --command WAIT_FOR_CAPS_ON --value 1 2>&1 | tee "$LED_LOG"
LED_EXIT=${PIPESTATUS[0]}
printf 'helper exit: %s\nlog: %s\n' "$LED_EXIT" "$LED_LOG"
```

Substitute the serial only if needed as described above. Do not put the dashboard
password in the command. It is entered privately at the prompt and is not saved.
Compilation, native-file checks, authentication, idle/receiver checks and initial
boot/session binding all happen before Start.

After separate owner approval, enter `APPLY ONCE`. Require the message:

`READY: authentication and native-file checks complete. No LED action sent.`

The helper now waits for **Assigned request ID**. Leave that prompt open. A script
must still be started manually; the helper never issues Start or arms EDR1.

## 4. One Start, actual ID, then focus TextEdit

1. On the iPhone, press the saved fixture's **Run** once. The current dashboard
   uses Route B. Its run log reports `Request N accepted / queued`; use that
   actual ID, not a predicted next ID or an old completed request's number.
2. Enter that ID at the already-open Mac Terminal prompt. Aim to do this within
   about **10 seconds** of Start. There is no second password or consent prompt.
3. The helper prints a **three-second focus countdown**. Immediately bring the
   blank TextEdit document forward, keeping the iPhone's **STOP / check execution**
   control accessible. No LED action occurs during that countdown.
4. After the countdown the helper polls only the specified owned request. It
   requires the exact active wait, unchanged boot/session and a current captured
   wait age **under 1000ms**. It then attempts one Caps LED ON action and one
   best-effort restoration of that selected output element after 200ms.
5. Preserve the Terminal log, assigned request ID, dashboard final status and a
   TextEdit screenshot. `helperExit=0` means only native API acceptance and its
   restoration attempt succeeded. Require the same request's Completed status
   and the expected `111` line before classifying this scoped trial as successful.

If the wait is already late/terminal, the ID differs, an HTTP 409/error occurs or
the USB session changes, **no automatic retry occurs**. Keep the evidence. Do not
rerun blindly or change firmware/timing to force a result. Cancel at the prompt
with Ctrl-C; the owner's dashboard STOP remains the actual script cancellation
control. Once a native action has begun, interrupt/timeout/disconnect may leave
restoration unverified. No host helper can atomically synchronize its final HTTP
check with device STOP; that residual race remains explicit.

## Timing evidence and limits

The old procedure could not justify fitting password entry, launching and consent
inside 15 seconds. V2 moves all those steps before Start. Only copying/entering
the actual ID and switching focus remain. The 15 seconds begins at runtime DELAY
entry, so using the earlier Start acknowledgement as the human clock is a
conservative approximation, not an exact timer measurement.

Mocked full-launch tests cover ID entry at 0, 2, 10, 12.2 and 12.999 seconds after
a synthetic Start, including the 3s focus countdown: all invoke once during the
first second of the active wait. Entries at 13, 15, 17 and 21 seconds are safely
refused in that model. The practical recommendation is **within about 10s**, not
the modeled boundary. No human response time or native High Sierra latency was
measured. The Mac is not a real-time system, so 15 seconds is a practical budget,
not a guarantee. Post-capture transport delays and OS scheduling remain physical
validation limits. The firmware's five-second wait deadline is never extended.

The advanced `--request N` option remains for an already assigned owned request;
it still requires consent and the same focus countdown/late checks. It must not
be used to predict the next request. Prepared interactive mode is recommended.
No LED API invocation proves global Caps state, USB wire delivery or key release.
EDR1 protocol, the C helper, firmware and existing rollback remain unchanged.
