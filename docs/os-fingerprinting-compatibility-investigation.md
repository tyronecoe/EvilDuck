# OS fingerprinting: concrete compatibility blockers

Investigated 2026-11-07 after the owner requested direct Hak5 OS fingerprinting
compatibility. This is a targeted source and compile-only investigation alongside
the independent DEL release. No OS-detection firmware was implemented, no USB
telemetry was collected and no host probe or payload was executed.

## What the official extension actually requires

The primary reference is Hak5's [OS_DETECTION extension, version 1.1](https://github.com/hak5/usbrubberducky-payloads/blob/4fa639fd06972cd7efd9c48cc73136443f9cffb1/payloads/extensions/os_detect.txt),
repository revision `4fa639fd06972cd7efd9c48cc73136443f9cffb1`, blob
`1df4013ffc6c1006c7df265038e79a3652f84a51`. The independently retrieved source is
7,875 bytes, SHA-256
`ef137faf626782fdcc6b43405f361b7a3c923c634f98dfd7774c73072e18399f`.
Its source says that detection is a moving target, particularly for Macs; it
does not promise universal OS identification. No publication date is supplied
by the source; retrieval was on November 7, 2026.

This is an extension composed from language, telemetry and device-control
interfaces, rather than a single intrinsic command. Disabling its optional
debugging and advanced-detection branches leaves the default dependencies below.

| Dependency in the pinned official file | Actual composed Route B result |
| --- | --- |
| Line 50: `DEFINE #WINDOWS_HOST_REQUEST_COUNT 2` | The label is 27 bytes including `#`; the current constant name buffer is 24 bytes and rejects lengths at least 24. The unmodified extension compile-rejects here, Identifier/code 6, line 50, column 1, before any IR is published. |
| Lines 54/88: reset/read `$_HOST_CONFIGURATION_REQUEST_COUNT` | Neither the internal getter nor its reset assignment is implemented. Isolated compile fixtures reject the assignment with code 18 and the read with code 6. |
| Line 55: ATTACKMODE with HID and VID/PID parameters | No Route B handler. The separate legacy mode parser neither implements those VID/PID parameters nor permits mode mutation during Route B ownership. Forwarding to it would not reproduce the official operation. |
| Lines 57/205: SAVE/RESTORE_HOST_KEYBOARD_LOCK_STATE | No Route B command handlers. Legacy helpers do not establish lease-safe Route B compatibility or global Mac restoration. |
| Lines 71/75/87: LED_R, LED_OFF, LED_G | No Route B command handlers. Existing local indicator helpers are reusable components, not active language support. |
| Lines 93/99/108: `$_OS` and OS constants | The selected engine lacks the internal result binding and reserved OS-constant expression semantics. Ordinary fake variables must not replace them. |
| Lines 70-73: lock-state read and conditional Caps tap | Fresh interface-specific feedback and key taps exist. Route B deliberately refuses unknown/stale lock reads instead of manufacturing OFF. A syntax-only compile pass does not establish that the official runtime's initial-state assumptions hold. |

Advanced mode additionally requires disconnect/reconnect behavior and Num/Scroll
probes. The current work does not run these or change device identities.

## What was actually verified

[Compile-only results](os-fingerprinting-compile-only-results.json) bind the
original official file and the actual composed DEL candidate core/header. The
unchanged OS source fails at line 50, code 6, with zero IR instructions. Isolated
fixtures establish the additional rejection paths above; separate existing
feedback, Caps-key and EXTENSION syntax controls compile. No runtime is started.
The host harness used ASan/UBSan/leak checking and reported empty sanitizer
stderr. Its executable and raw receipts remain under
`/workspace/scratch/os-detect-audit/`.

Raw source size and physical line length are not the first blocker: 217 lines,
maximum physical line 106 bytes, ASCII source, final LF, and 317 bytes below the
8,192-byte source limit. Compiled IR capacity is not claimed for an unsupported
extension.

Host-only size inspection measured Compiler at 3,856 of 4,096 workspace bytes.
This is not ESP32 target RAM/stack evidence. Increasing the 16 constant-name
buffers from 24 to 32 bytes would add 128 bytes to that compiler workspace;
any proposal must retain the existing workspace assertion and verify the actual
target before acceptance. Raising this bound alone does not resolve the other
dependencies.

## Telemetry and representation contracts still missing

The [official quick reference](https://documentation.hak5.org/hak5-usb-rubber-ducky/duckyscript-tm-quick-reference)
describes the counter only as being used to detect device enumeration count.
It does not establish which USB requests increment it, duplicate handling,
reset/read timing, overflow behavior or lifecycle across reconnection. A USB
mount count, HID report count or arbitrary GET_CONFIGURATION count cannot be
silently substituted.

The approved Arduino ESP32 3.3.0 core has a weak
`tud_descriptor_configuration_cb` in `esp32-hal-tinyusb.c:352`, invoked for GET
CONFIGURATION DESCRIPTOR. It returns a private static descriptor pointer.
Replacing it without preserving the descriptor implementation could break USB;
its existence also does not prove that its call count equals Hak5's metric.
No SDK patch, hook or linker change was made.

Static inspection of the already captured public PayloadStudio source identifies
OS symbol/property encodings. These are compiler representations, not proof of
the numeric runtime values held by `$_OS`. No compiler functions or INJECT_VAR
checks were rerun. H1 and its unresolved numeric contract remain untouched.

## Practical next steps

1. A separate bounded language increment can admit the official 27-byte DEFINE
   label, keeping variable/function limits unchanged. Test exact limits,
   expansion, exclusions, malformed retained source and target workspace use.
   Do not present that as working OS detection.
2. Establish the counter's event/reset/session contract from authoritative
   evidence. Then assess a transparent observer that preserves all descriptors,
   ownership and dependency guards; test with fabricated request sequences.
3. Specify OS symbols, indicators and lock save/restore independently. Preserve
   fresh/unknown/stale evidence, request ownership, STOP priority, cleanup and
   quarantine. Do not convert unknown to OFF to force the extension to run.
4. Mode/identity and reconnect behavior require a separately reviewed scope.
   Stripping these lines, substituting manual OS selection or returning a fixed
   MACOS label would be an EvilDuck-specific adaptation, not direct support for
   the pinned official extension.

Several language interfaces are implementable, but **direct official extension
compatibility is not established and is not a one-counter fix**. The precise
counter/runtime and device-lifecycle contracts are concrete blockers. No Windows
hardware prerequisite is introduced; useful software work can continue with
offline models while host accuracy remains a separate later question.

The accepted owner milestones, experimental H1 policy and exact source/text-v2
rollback remain unchanged. No OS firmware source, USB identity, hardware,
settings, protected files or credentials were changed or accessed.
