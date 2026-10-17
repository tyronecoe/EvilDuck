# Change C — separate visible fake-phrase host tests

The original DuckyLogger2 source was inspected read-only at Hak5 repository revision
`4e2254d61757acaae974ae2b2038469d1d030139`, with README/payload/decoder hashes
recorded in [primary reference receipts](stop-led-references.json). README describes
Unix-like/systemd. The payload uses X11 `xinput` keyboard tests, a PHP reverse TCP
connection and user systemd service/timer persistence. It does NOT use LED reflection.
Its downloaded xinput binary was not fetched or executed. The payload/README/root
listing at that revision expose no license grant; root LICENSE fetch returned404.
Do not assume code reuse rights. No original code, reverse shell, download,
persistence, service or obfuscation was reused. New tools are independently written
under this repository's MIT context using documented OS APIs.

The new Windows and macOS tools receive keyboard events outside their own window,
but deliberately retain only a match of EVILDUCK TEST 123; Linux has an independent
bounded evdev variant. They are visible, explicitly started, terminate at match/
Stop/Exit/60seconds and do not deliver anything automatically. See the [host README](../host_tests/capture/README.md).
Windows uses WH_KEYBOARD_LL with a normal message loop, explicit unhook and software-
injected event exclusion. macOS uses a listen-only CGEventTap, run-loop deadline,
signal-controlled stop and ordinary permission failures. Official Apple metadata
marks CGEventTapCreate available since10.4. Linux uses nonexclusive read-only evdev,
fixed buffer, normal permissions and closes its descriptor after failure/timeout.
No claim is made that private/secure/elevated input is observable or that these
helpers reproduce arbitrary Unicode or all layouts. Windows/Linux use a narrow
ASCII key-code subset; the owner's second-editor text must be independently checked.

A matched fake phrase can be reviewed locally; Windows offers an explicit save
of that17-byte constant. Other keystrokes are discarded, not logged. Only after a
physically supported fixed-message channel is established could the owner manually
send the same reviewed17-byte sample using the separate B sender. No automatic
capture-to-LED integration is enabled without that prerequisite. Generic arbitrary
key logging/transport and external webhooks are not implemented. This is a safety
scope boundary, not a claim that window-only capture satisfied cross-application
acceptance. Actual second-application capture remains unperformed on every host.

## Executed checks

-11 Python production-detector/entry-point unit tests PASS,0FAIL. Synthetic keys,
  ignored release/repeat, wrong/partial text, no general log, explicit start gate,
  invalid path, permission failure, metadata failure cleanup and finite timeout
  are tested through mocks; no physical input device is opened.
-Four new public launcher sources compile with the actual pinned composed preview
  compiler and complete through a memory-only event sink. ASan/UBSan/leaks clean.
  These are fake sink events, not HID reports, host shell execution or API capture.
-Windows/.NET and macOS/Apple SDK compilation and runtime: NOT TESTED/ENVIRONMENT
  BLOCKED. No compatible host toolchains are installed here. Primary API research
  and source implementations are not native compilation evidence.

[Exact command/results receipt](host-capture-results.json). The first launcher
harness used the wrong Runtime::start argument order and failed compilation;
its API call was corrected against the actual header. Mac launcher uses `~/...`
rather than `$HOME`, avoiding accidental DuckyScript variable interpolation.
No production parser, language, partitions, USB descriptors or settings changed.

## Host/control matrix

| Platform | Source/API evidence | Native helper build | Other-app capture | LED delivery | Security product result |
|---|---|---|---|---|---|
| Windows11 | SendInput/GetKeyState/WH_KEYBOARD_LL attempt | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED |
| macOS10.13.6 | IOHID element/CGEventTap attempt | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED |
| Linux workspace | Python detector + mocks PASS | Python imported/tested | NOT TESTED | No sender; gap | NOT TESTED |

For later separately authorized trials, keep controls enabled for baseline, use
one change at a time, first establish benign local capture and a known-working
fixed delivery, then include a no-sender/no-capture negative control. Record actual
OS build, product/version/policy, permissions, runID, binary/source hashes, timestamps,
expected17bytes, sent/received counts and integrity in the [template](../host_tests/defensive-record-template.json).
Unperformed values stay null/NOT TESTED. Distinguish failed start/permission/capture/
reflection/receiver/transport from a security alert or documented prevention.
No-delivery alone is not proof antivirus blocked it; delivery is not a vulnerability
or evidence of complete security quality. These visible fake-only adaptations omit
original persistence, reverse connection, hidden files, external downloads and raw
key logs, so defense comparisons to original DuckyLogger are materially limited.

**GO:** source review and owner-controlled offline native compilation.
**PENDING:** real permissions, outside-helper fake phrase, independent stop, fixed
LED return and iPhone view. **NOT COMPLETE:** whole logger/security-testing goal.
No owner-host process, shell payload, real HID or physical device was executed.
