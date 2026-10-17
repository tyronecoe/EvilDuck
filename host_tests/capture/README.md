# Visible temporary fake-phrase cross-application diagnostics

These are independent adaptations for this experiment, not original DuckyLogger
payloads and not general-purpose key loggers. OS keyboard events reach the helper;
only a prefix length and a match of **EVILDUCK TEST 123** can be retained. No other
text, credentials, window titles or application contents are logged or transmitted.
Close sensitive applications and deliberately use a fake-data editor for any later
authorized test. A fixed-message receiver or a test in this helper's own window
does not prove system-wide capture.

**No physical host capture has been performed by Codex.** All native Windows and
macOS build/runtime outcomes remain NOT TESTED. Linux detector tests use synthetic
input and mocked file descriptors, not a keyboard. No defense product was tested.

Windows11: keep WindowsCapture.cs beside capture-windows.ps1. In a normal visible
PowerShell5.1+ console, invoke `powershell -NoProfile -File .\capture-windows.ps1`.
Respect execution policy; no Bypass, hidden window, administrator requirement or
security-control change is supplied. A visible form starts INACTIVE. Click Start,
then manually type the fake phrase in another ordinary editor. Stop/Exit and a
60-second monotonic deadline remove the hook. Only an exact fake match enables
saving a17-byte fake-result file via an explicit save dialog. The low-level hook
is current interactive desktop scope; it does not promise secure desktops,
protected input, other sessions or elevated targets. Injected software events are
excluded. The small ASCII VK subset/case normalization is not arbitrary Unicode
or complete locale reconstruction. Confirm actual editor text visually.

macOS10.13.6: compile with the owner's installed Apple tools:
`clang -std=c11 -mmacosx-version-min=10.13 -Wall -Wextra capture-macos.c -framework ApplicationServices -framework CoreFoundation -o capture-macos`.
No SDK/compiler is downloaded by these tools. Run visibly in Terminal; type START,
then manually type the fake phrase into a second ordinary editor. Ctrl-C,60-second
limit or a match ends the listen-only session event tap. Output contains only an
agreed fake match or a generic failure/no-match result. Respect normal Accessibility
permission; do not bypass prompts. CGEventTapCreate returning NULL or a disabled
tap is a failure/unavailable result. Secure Input may withhold events; macOS10.13.6
is not assumed to offer newer Input Monitoring APIs. No API is used to evade it.
No host text injection, persistence, automatic delivery or settings repair occurs.

Linux: `python3 capture_linux.py /dev/input/eventN` with an owner-selected existing
evdev keyboard and ordinary read permission. It prompts START before opening,
rejects non-evdev paths/symlinks/non-character files, limits read buffers, keeps no
raw log and closes on Stop/Ctrl-C/60seconds/error. Do not change device permissions
or run with elevated privileges simply to make a test pass. Permission denial is
a valid classification. It uses a small US/DE physical-key subset, not desktop
Unicode/layout translation. Device selection, real evdev operation and a portable
Linux DuckyScript launcher remain unverified/gaps. No LED sender is provided for Linux.

Review a local fake match first. Only after a real fixed-message LED roundtrip is
established for that OS/channel, a separately authorized operator may deliberately
run the independent `../led_return/` sender for that same17-byte sample. There is
no automatic capture-to-transport integration; physical capability evidence does
not yet exist. No arbitrary data or external webhook is sent. HTTP fallback is
not implemented: it would need a small separately reviewed size-limited authenticated
fake-message endpoint/host sender, route reachability and CSRF/auth/error tests.
Do not call it USB reflection. Home Wi-Fi does not itself route to the EvilDuck AP.

Finite launcher sources in `launchers/` only open pre-reviewed local helpers.
Place the reviewed source beside the Windows script at Desktop/EvilDuckTest or the
compiled Mac helper at Desktop/EvilDuckTest/capture-macos. Mac Spotlight/Terminal
and Windows Run conventions must match the actual host; otherwise start manually.
They do not download tools, disable controls, auto-confirm START or type the fake
phrase. No launcher was executed against a host. STOP script/unplugging EvilDuck
will not necessarily stop an independently launched helper: use its own Stop/Exit
or Ctrl-C and confirm process exit. After exit, remove only your newly staged
EvilDuckTest helper folder and any fake result you deliberately saved. There are
no installed services/startup hooks/uninstall scripts.

See the defensive record template and docs/host-capture-report.md. A missing match
or failed transfer is not evidence of antivirus prevention; successful delivery is
not a vulnerability or an overall security score.
