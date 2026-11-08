# OS_DETECTION: DEFINE prerequisite resolved, detector still unsupported

Recorded 2026-11-08. This release changes only bounded DEFINE-label capacity.
The original [investigation](os-fingerprinting-compatibility-investigation.md)
and [DEL compile-only receipt](os-fingerprinting-compile-only-results.json)
remain unchanged historical evidence. No broad reference search, OS probe,
runtime execution or USB callback change was performed.

## Actual old/new whole-file observations

The exact pinned official source is OS_DETECTION v1.1 at revision
[`4fa639fd06972cd7efd9c48cc73136443f9cffb1`](https://github.com/hak5/usbrubberducky-payloads/blob/4fa639fd06972cd7efd9c48cc73136443f9cffb1/payloads/extensions/os_detect.txt),
7,875 bytes, SHA-256
`ef137faf626782fdcc6b43405f361b7a3c923c634f98dfd7774c73072e18399f`.
The fixture was compiled unchanged against both actual composed cores. It was
not patched, stripped or executed.

| Selected core | Actual first rejection |
| --- | --- |
| DEL parent | Physical line 50, column 1, Identifier/code 6: the 27-byte `#WINDOWS_HOST_REQUEST_COUNT` label exceeds the former 23-byte bound. |
| DEFINE candidate | Physical line 54, column 1, UndefinedSymbol/code 18: `$_HOST_CONFIGURATION_REQUEST_COUNT = 0` is unsupported. |

The new compiler passes the previously rejected DEFINE declaration. Its one
intermediate function instruction is not a published runnable program. Both
compilations reject before runtime; no HID operation or host observation occurs.
[Structured progress and exact host layout observations](define-labels-os-progress.json)
bind these results to the focused execution receipt.

Only this label-capacity blocker is resolved. Later whole-file statements were
not reached, so their rejection is not claimed as a new observation. Existing
source inspection and earlier isolated compile fragments identify the remaining
dependencies: counter read/reset, OS results/constants, indicators, Route B lock
save/restore, mode/identity and reconnect lifecycle. Full extension IR/runtime
capacity and host accuracy remain unestablished.

## Precise questions for the next separate planning stage

- **Counter event:** Which exact requests or completed transactions increment
  Hak5's count? Distinguish configuration-descriptor reads, repeated/partial
  reads, GET_CONFIGURATION, mount/configuration events and HID reports. What is
  counted when a transfer fails or is retried?
- **Counter lifecycle:** Which assignments reset it, at which serialization
  point, and what happens before enumeration or during reconnect? Establish read
  atomicity, width, overflow/exhaustion policy, and boot/USB-session boundaries.
  The primary quick reference's phrase "device enumeration count" does not
  settle these details.
- **Feedback lifecycle:** Does the extension's received-reply flag mean ever
  received or current-session evidence? How should a missing initial lock report
  behave? Preserve Route B's fresh/unknown/stale distinctions and never fabricate
  OFF to make a branch execute. This interface's reports are not global Mac
  keyboard state.
- **OS result contract:** Establish initial/unknown state, mutability, width,
  reset lifetime and symbolic comparisons for `$_OS` and the six OS labels.
  Public compiler tokens/property selectors do not by themselves establish the
  numeric runtime values. A fixed or manual MACOS label is not detection.
- **Lock and indicator interfaces:** Specify snapshots, restoration completion
  and cancellation/error outcomes before reusing legacy helpers. Preserve the
  request lease, priority cleanup, quarantine and no replay. Define indicator
  semantics independently; do not silently ignore unsupported commands.
- **USB lifecycle:** Determine actual mode/identity/reconnect semantics and how
  they interact with an active lease and STOP. The current descriptors and mode
  safeguards remain unchanged. Forwarding a line to a legacy parser that ignores
  identity parameters would not implement the official operation.
- **Remaining capacity and accuracy:** Once dependencies have real contracts,
  compile the unchanged extension again to observe remaining limits. Later
  authorized host checks would assess a heuristic, not establish universal OS
  identification. Windows availability is not a prerequisite for offline work.

Reuse the existing primary evidence for those questions. Do not substitute mount
or report counts, run probes, expand H1, reinterpret unknown lock state or start
an open-ended search to remove an unresolved label. Canonical H1 numeric encoding
remains unresolved. No credential collection, input capture or evasion feature
is included in this language update.
