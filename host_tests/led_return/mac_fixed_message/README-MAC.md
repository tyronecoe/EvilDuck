# Fixed-message LED return — Mac review kit v1

This foreground host tool sends only **EVILDUCK TEST 123** to the installed
EvilDuck LED-test receiver. It contains no board installer or firmware. Native
Apple compilation and physical delivery have **not** been performed in Codex.
The Linux checks exercise shared logic and mocks, not High Sierra IOKit.

Target: macOS High Sierra 10.13.6, Bash 3.2, already installed Apple command-line
tools and Python 3.8+. Nothing is downloaded or installed by the launcher.
Target firmware build: `CAPS-STOP-TRACE-20261019-v1`. The associated published
application hash is
`25e17cadacf3b2ab5eb5ece32fc94f4bf36fb71eb90e91814dca7f7320bd5178`;
this tool checks the reported build/session, not a physical firmware hash.

## One launch command

Unzip `evilduck-macos-fixed-message-v1.zip` into Downloads. In Terminal run:

```bash
bash "$HOME/Downloads/evilduck-macos-fixed-message-v1/run-mac.sh"
```

The launcher checks the kit checksums, compiles only the Mac helper in its own
temporary directory, and removes that directory on exit. A compilation failure
is a native-build blocker: retain the compiler diagnostic and stop. Do not
install drivers, change security settings, or change the board firmware to get
past it. Paths in a compiler diagnostic can be redacted before sharing.

## Short owner procedure

1. Keep the existing installed firmware. Connect EvilDuck USB to the Mac. Leave
   the Razer disconnected. Do not run scripts, press keyboard lock keys, run
   another sender, reboot/unplug EvilDuck, or operate receiver controls during
   this trial. Laptop Caps LED mirroring and global Caps flags are not tests of
   this device-specific output channel.
2. Join the existing EvilDuck Wi-Fi on the Mac and iPhone, and confirm the
   dashboard opens on both. The Mac must reach the local dashboard directly;
   an iPhone connection alone is insufficient. Leave application execution idle.
   Only ordinary existing local HTTP diagnostics are used; the password travels
   over that existing local HTTP connection. No cloud service receives it.
3. Run the command above. Identification is read-only: it prints actual
   `303A:1001` HID serials and element compatibility. Enter the exact unique
   usable serial printed locally, the local dashboard address (for example
   `http://192.168.4.1` **only if that is your actual address**), and your existing
   Web UI password at the hidden prompt. No password goes in command arguments,
   logs or the receipt. Addresses must be literal private/link-local IPv4 HTTP
   addresses; there is no public-address, redirect or proxy fallback.
4. Type `PROBE` only when ready. Four small Gray-cycle output writes change
   Num, Caps, Num, Caps, relative to saved interface output values. Each step
   must be confirmed by a newer, same-session device LED report with the
   expected mask and timestamp. Mac API success alone cannot pass the probe.
   The receiver is kept unarmed. Initial Num/Caps output values are then restored
   independently. Stop on any failure; there is no automatic retry.
5. After all four device-confirmed steps, type `SEND` when ready. The helper
   explicitly starts a **new** receive session, requires `Receiving` with
   integrity false, and sends exactly one 25-byte EDR1 frame. Progress is printed
   as host API submission only. Expect roughly 40 seconds of deliberate LED
   pacing, plus local HTTP overhead. Do not manually click Start/Clear/Stop
   while this automatic sequence is running.
6. Delivery is reported only after same-boot/session counters and timestamps,
   `Complete` (`state=2`), `integrity=true`, an authenticated exact 17-byte
   `/led-test/data` response, and a coherent result recheck. On iPhone use the
   existing **Observe LEDs / refresh** control and **View test data**. Check the
   fixed text exactly. **Download test data** is optional. Do not click Start or
   Clear: the completed RAM result remains available even when LED feedback
   becomes stale. Type `VIEWED` in Terminal only after this iPhone check.
7. Keep the newly created Desktop folder `evilduck-fixed-message-*`. Its
   `receipt.json` records sanitized snapshots, step outcomes, exact message
   hash, restoration and the separately owner-reported iPhone check. Share that
   file and a sanitized compiler diagnostic if needed; do not send passwords,
   configuration, full backups or a recording of unrelated terminal activity.

The Mac helper does not collect iPhone screenshots. `VIEWED` records your
confirmation; it is not an automated Safari inspection. If the Mac cannot reach
the local dashboard, stop with that connectivity result. The iPhone can still
read diagnostics manually, but this version does not substitute manual
screenshots or HTTP message upload for the required automatic readback.

## Bounds, cancellation and interpretation

- Entire workflow: 600 seconds, including prompts. Probe: at most four steps,
  each with a four-second evidence window. Normal bounded GET polling is allowed;
  failed HTTP requests, LED writes and frames are never replayed automatically.
- Sender: 90-second cooperative phase limit and 95-second native watchdog.
  HTTP requests have a two-second absolute deadline, including headers/body.
  OS stalls or forced process termination can prevent prompt exit or cleanup.
- Ctrl-C cancels. The child is interrupted before bounded receiver-stop cleanup
  if transmission is active. Saved Caps and Num output values are restored in
  independent best-effort operations; failure of one does not skip the other.
  Cleanup results concern API attempts, not verified global macOS restoration.
  A hard kill, blocked IOKit call, process crash or unplug can prevent restoration.
- Discovery opens normally without seizing devices. Missing/duplicate serials,
  ambiguous elements, unsupported report IDs/shapes, permission refusal or
  unavailable initial output values stop the tool. It never selects the first
  ambiguous interface, guesses a serial, or uses a serial-port name as HID ID.
- This channel uses LED **output elements**, not a CAPSLOCK keypress. Num carries
  data and Caps transitions clock bits. Pacing stays at 100 ms before/after each
  clock transition; the separate 500 ms ordinary Caps input dwell is unchanged.
- Fresh probe evidence requires LED freshness. A completed receive result is RAM
  history tied to a newly acknowledged Start, so it does not require the final
  LED report to remain younger than five seconds. Stale feedback is never labeled
  current. Boot/session changes, new receiver errors and saturated counters abort.
- There is no per-trial firmware nonce. Attribution assumes this exclusive,
  supervised workflow and ordered same-session observations; neither CRC nor
  local HTTP proves cryptographic run identity or complete USB capture.

`DEVICE_MESSAGE_VERIFIED_IPHONE_PENDING` means the Mac verified fresh device
data, with the required iPhone check still pending.
`DEVICE_VERIFIED_AND_OWNER_IPHONE_CONFIRMED` adds your local `VIEWED` statement.
Neither is claimed before you actually run the kit. Any stop/error is a specific
unconfirmed result, not permission to change firmware or repeat automatically.
If Num feedback is unavailable, stop and review that evidence; no Caps-only
protocol or alternate data delivery is enabled.

## Package and scope

`SOURCE-MANIFEST.json` lists every packaged source/report file, size and SHA-256.
`SHA256SUMS.txt` also covers that manifest. The ZIP contains only this README,
launcher, `native.c`, shared `engine.c/.h`, `workflow.py`, `device.py`, fixed
protocol constants and the offline results summary. It has no compiled Mac
binary, firmware, installer, owner evidence, credentials or arbitrary payload.
The protocol constants are descriptive; there is no configurable message input.

This milestone does not prove full DuckyScript compatibility, Hak5 wire
compatibility, host-wide Caps correctness, arbitrary reflection or a logger.
