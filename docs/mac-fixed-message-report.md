# Fixed-message LED return host workflow

## Result and boundary

Prepared an additive, source-only Mac host kit for the installed
`CAPS-STOP-TRACE-20261019-v1` receiver. The firmware did not need to change.
**GO: source review and a separately owner-operated native attempt.**
**PENDING: native Apple compilation, actual Num/Caps output capability, message
delivery and iPhone viewing.** No physical success is claimed here.

Baseline: `0803937b9b552fe4b6e6cb6d1dd60f80f098449c`.
New branch: `mac-fixed-message-led-workflow`.
The baseline's 1,786 tracked files/modes remain unchanged. The retained composed
candidate's 201 source hashes and five generated artifact hashes also match the
existing build receipt. The published application hash associated with the
owner-identified build remains
`25e17cadacf3b2ab5eb5ece32fc94f4bf36fb71eb90e91814dca7f7320bd5178`.
This rechecks retained workspace artifacts, not bytes on the owner device.

The Razer was disconnected in the formal recordings. The broad global Caps
investigation is parked; there is no new idle/typing/keyboard-mirroring gate.
The owner confirmed that this Mac can reach the EvilDuck Wi-Fi dashboard while
USB is connected. We did not test that connectivity from Codex.

## Implemented behavior

- Read-only discovery checks exact USB identity `303A:1001`, actual nonempty
  serial, unique interface selection, keyboard conformance, unambiguous Boolean
  Num/Caps output elements and report ID 1. It opens normally, without seizure,
  and retains the device and element collections through cleanup.
- Separate explicit `PROBE` and `SEND` prompts. Four Gray-cycle output writes
  require fresh same-boot/session device feedback for both Num values and Caps
  edges. Initial and pre-step idle/session/receiver checks prevent knowingly
  probing an armed or changed receiver. API success is insufficient.
- Only after capability passes: acknowledge a fresh authenticated receiver
  Start, send one fixed frame and verify new Complete/integrity evidence,
  advancing report counters/timestamps, exact authenticated 17-byte data and a
  same-session result recheck. Historical RAM success cannot satisfy arming.
- One message: `EVILDUCK TEST 123`. Frame25 bytes:
  `0045445231114556494c4455434b205445535420313233d6cc`.
  Num bit0 carries data, Caps bit1 changes clock, MSB first, CRC16-CCITT-FALSE.
  Existing direct-output pacing remains 100 ms before/after each clock change.
  No change to the separate 500 ms ordinary CAPSLOCK input policy.
- Overall600 seconds, probe4 seconds per step, sender90 seconds cooperative/
  95 seconds watchdog, HTTP2 seconds absolute including trickled headers/body.
  Bounded normal evidence polling does not replay failed requests or writes.
  No automatic message retry, background task, arbitrary data or capture.
- Ctrl-C or a failed run interrupts an active native sender before HTTP cleanup.
  Caps and Num restoration attempts are independent. Finite cleanup records
  failures and still saves a local receipt. Restoration is an API outcome,
  never proof of global Caps state or physical host delivery.
- Credentials are entered locally with a hidden password prompt, used only for
  existing authenticated local endpoints, and omitted from receipts/argv.
  Redirects, public hosts and proxies are rejected. Unrelated `/status` fields
  such as SSID/script names are discarded. Only `/led-test/start` and failure
  cleanup `/led-test/stop` mutate receiver RAM; there is no HTTP upload path.
- A new private Desktop directory holds `receipt.json` with safe counters and
  outcomes. It cannot overwrite an existing receipt. The iPhone `VIEWED` result
  is separately labeled owner-reported; Codex/the helper cannot inspect Safari.

Development review caught an HTTP/1.0 socket-lifetime issue, missing pre-step
receiver checks and delayed/fragile cleanup in the new code. These were corrected
and covered before publication. Existing firmware and historical verifiers were
not modified to make the new tests pass.

## Focused verification

Linux x86_64, Python3.12.14, GCC/G++14.2.0, Node24.19.0, Bash5.2.37,
Git2.52.0. The native target remains macOS10.13.6/Bash3.2/Python3.8+ with
existing Apple CLT. There is no Apple SDK/clang runtime in this environment.

| Executed checks | PASS | FAIL | Assertions |
| --- | ---: | ---: | ---: |
| Shared C engine and selection/element rules | 11 groups | 0 | 517,213 |
| HTTP evidence/client | 27 cases | 0 | not instrumented |
| Actual Python workflow and synthetic child-process cleanup | 26 cases | 0 | not instrumented |
| Existing composed receiver L01–L19 | 19 cases | 0 | 3,151 |
| Actual retained dashboard functions in Node VM | 15 cases | 0 | 195 |
| Source-only ZIP/checksum/source equality/Linux refusal | 3 cases | 0 | not instrumented |

The two C/C++ suites pass ASan, UBSan and leak detection. Python/Node cases are
not sanitizer runs. Assertions cover exhaustive failure boundaries in the shared
engine, including all402 frame-write failures and400 wait-cancellation boundaries;
their volume is not evidence of physical coverage. Existing L01–L19 cases were
selected by a new hash-pinned wrapper that replaces only the historical runner's
top-level case iterable **in memory**. Source composition, dependency checks,
compiler/sanitizer options and expectations remain unchanged. No unrelated full
regression suite was rerun, and no historical classification was changed.

The dashboard tests execute actual `duckHeaders`, `controlFetch` and `viewLedData`
from the retained composed source, pinned by source/function hashes. They verify
authenticated exact-text view/download and rejection of 409, bad content, newline,
BOM, NUL and authentication failures. This is a Node/mock-DOM result, not Safari.
The historical UI MIME check uses a `text/plain` prefix; the new Python download
check validates the exact media type. The historical UI remains untouched.

## Reproduction and delivery

From the repository root, safe offline commands:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests/mac_fixed_message -p 'test_*.py' -v
python3 tests/mac_fixed_message/run_native_tests.py --build-dir /tmp/evilduck-fixed-engine-NEW
node tests/mac_fixed_message/test_dashboard.js /path/to/retained/composed/EvilDuckS3/webfiles.h
python3 tests/mac_fixed_message/run_receiver_tests.py --core /path/to/verified/isolated/3.3.0 --build-dir /tmp/evilduck-fixed-receiver-NEW --results /tmp/evilduck-fixed-receiver-NEW.json
bash -n host_tests/led_return/mac_fixed_message/run-mac.sh
python3 tests/mac_fixed_message/package.py --output /tmp/evilduck-macos-fixed-message-v1.zip
```

Use fresh build/output paths; builders refuse to overwrite their output. The
receiver runner requires the existing pinned isolated core/source dependencies.
It builds native mocked test code only, not a deployable firmware image.
Package tests require the committed download ZIP. Its new allowlisted packager
includes sources, instructions, fixed constants, manifest, checksums and this
report/results; it does not glob private directories or include board artifacts.

Download: `downloads/evilduck-macos-fixed-message-v1.zip` on the new branch,
published as actual repository bytes. Publication uses a new branch only; previous
refs must match the64-ref pre-work snapshot. Post-push downloaded bytes must match
the locally assembled ZIP before supplying the commit-pinned download link.

One owner command after unzipping into Downloads:

```bash
bash "$HOME/Downloads/evilduck-macos-fixed-message-v1/run-mac.sh"
```

The packaged README supplies the complete short procedure and stop conditions.
No firmware installer or native compiled executable is included.

## Limitations and next decision

The receiver exposes no per-receive nonce, and its USB state/counter fields are
separate bounded samples, not a single atomic whole-transport trace. The helper
checks session, lifecycle, monotonic counters, freshness and ordering, but trial
attribution still assumes one supervised sender and no competing receiver control.
CRC is integrity, not authentication. Authentication is the existing local HTTP
password mechanism, not encryption. OS scheduling, IOKit stalls and forced exits
can prevent bounded real-world cleanup; no hardware-level timing guarantee exists.

A complete RAM result remains history after LED freshness expires; it is accepted
only because a new Start and subsequent new evidence were verified. Neither a
historical mask nor a global macOS Caps flag is relabeled current. A disconnect,
session change, new error, saturated counter or wrong text cannot pass.

Next: owner compiles this source-only kit natively, then may explicitly choose
PROBE. If native compilation or Num/Caps feedback is blocked, retain the specific
diagnostic/receipt and review it. Do not tune input Caps dwell, invent a Caps-only
fallback, change firmware or repeat a message automatically. Successful native
compilation still does not establish physical delivery; all four physical
acceptance conditions, including iPhone viewing, remain pending until observed.

No firmware behavior/build, hardware access, flash/erase/OTA, owner payload
execution, real HID output, driver installation or macOS setting change occurred.

## Added file inventory

- `host_tests/led_return/mac_fixed_message/`: README, fixed constants, launcher,
  native helper, shared engine/header, HTTP evidence module and workflow.
- `tests/mac_fixed_message/`: C engine tests, native and focused receiver runners,
  HTTP/workflow/package unit tests, dashboard test and allowlisted packager.
- `docs/mac-fixed-message-report.md` and `docs/mac-fixed-message-results.json`.
- `downloads/evilduck-macos-fixed-message-v1.zip`.

Every historical source, report, verifier, package and ref is protected; only
these new paths are part of this change.
