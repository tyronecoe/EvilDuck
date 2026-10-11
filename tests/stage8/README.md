# Stage 8: mocked HID and keyboard locales

From the repository root:

```sh
python3 tests/stage8/run_tests.py
```

The shared Stage 1 compiler builds actual S3 parser, scheduler, locale and HID
sources with ASan/UBSan. All USB, storage, clock and command-output interfaces are
mocks. No host keyboard, serial port or physical device is opened. Each test has
a 20-second process timeout; compilation, assertions, sanitizer faults and
unexpected exits fail the runner. This suite requires no new firmware dependency.

The mock captures accepted report instance/ID, exact eight-byte payload and time.
Readiness and queue acceptance are separate controls. Rejected submissions do not
appear as accepted reports. Reference usages are literal numbers from USB HUT
page 0x07 and independent US / German PC/ISO physical key rows; expected data are
not read from the production locale arrays. Tests check every ASCII index and
runtime printable character, F1–F24, aliases/navigation/keypad, all 256 modifier
masks and cancellation for all 255 nonzero masks. The US visible-text emulator
is never used as evidence of German host output.

Runtime fixtures cover normal and dead-key strokes, correct release/dwell,
reported unsupported Unicode skips, malformed UTF-8 bounds, six-key rollover,
DEFINE/replay, multiline/control/function integration, source faults, ownership,
STOP/cancellation and release priority across a simulated disconnect or endpoint
refusal. Firmware uses the existing bounded one-report scheduler, not a queue.

The allocation probe counts C++ new requests during isolated translation and
report construction, with mock vectors pre-reserved. It is not an ESP32 heap
watermark or a claim that parsing, String expansion, warning logging, USB
libraries or complete script runs allocate nothing.

One Stage 1 assertion deliberately protecting the *short broken DE table* is
updated to expect its intended DEL-to-Delete mapping. Historical known-bug
labels/desired expectations remain; both fixes now naturally XPASS. Stage 8
exhaustive reference tests establish the fixes beyond mere table length.

See [the report](../../docs/stage8-report.md), [capability inventory](../../docs/stage8-keyboard-compatibility.md)
and [design decisions](../../docs/stage8-design.md) for exact executed results,
compatibility changes, reproducible builds and pending physical validation.
