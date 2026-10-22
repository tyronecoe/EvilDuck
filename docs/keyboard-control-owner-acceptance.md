# Owner acceptance: fixed-message LED return on High Sierra

This note records the completed prerequisite supplied for the keyboard-control
work. It supplements historical reports without rewriting their earlier
UNVERIFIED status. No physical experiment was performed by Codex for this note.

The owner accepted the controlled Mac-to-EvilDuck LED-return milestone on the
physical macOS High Sierra 10.13.6 laptop, including independent iPhone dashboard
display of **EVILDUCK TEST 123**. The owner confirmed unchanged firmware/no
reflashing during validation and preservation of Terminal output and screenshots.

## Supplied receipt and separate screenshot

The original local-workflow receipt, supplied again in
`EvilDuck-DuckyScript3-Compatibility-Codex-Plan.zip`, has SHA-256
`a06ed227c3e8aa2300df9ae66d1fd5f218ed7664a0c371ed6ee8fde5baf05ffd`.
Its duplicate filename in earlier chat is the same evidence, not an additional
independent test. The attachment's checksum manifest was checked before work.

| Recorded item | Receipt evidence |
| --- | --- |
| Host tool baseline | Published host-only workflow `cb3a147719850a0dc4a4797b401b606ea14c6571` |
| Owner-identified firmware | `CAPS-STOP-TRACE-20261019-v1` |
| Firmware/report baseline | `0803937b9b552fe4b6e6cb6d1dd60f80f098449c` |
| Coherent identity | Boot marker `74f39b50638bee97`, feedback session 3 |
| Capability | Four fresh matching probes, masks `1 → 3 → 2 → 0` |
| New receive session | `state=1`, `integrity=false`, before frame send |
| Completion | `state=2`, `integrity=true`; 408 accepted reports; no recorded receiver rejection or overflow |
| Exact data | 17 ASCII bytes, `EVILDUCK TEST 123`, no newline/NUL/BOM |
| Payload SHA-256 | `22cc949af769332238c663b383e1990183dd6e9b8577377e2398f9f6b2d41169` |
| Observation interval | Approximately 41.677 seconds from new receiver snapshot to verified message; not a wire-latency measurement |
| Restoration | Both saved output-element restoration API results recorded successful; global Caps restoration explicitly not proven |
| iPhone receipt field | `OWNER_REPORTED_PASS`; not automated screenshot inspection |

Codex separately inspected the uploaded iPhone image showing the exact phrase.
That image showed a cumulative accepted-report count of **820**. The owner
identified it as a **later repeat**. It is independent display evidence from that
later run; it must not be merged with the 408-report receipt into one matched
trial. Original matching evidence remains owner-preserved. No new run is required
to accept the milestone, and no second receipt is invented.

The associated published application artifact is
`25e17cadacf3b2ab5eb5ece32fc94f4bf36fb71eb90e91814dca7f7320bd5178`.
That is the known installer/build artifact identity, not a new physical board
image readback. The receiver/host workflow are the unchanged custom EDR1
fixed-data path described in [the host report](https://github.com/tyronecoe/EvilDuck/blob/cb3a147719850a0dc4a4797b401b606ea14c6571/docs/mac-fixed-message-report.md).

## Accepted boundary

**PASS — owner-operated physical fixed-message LED return in this tested
configuration.** Receipt fields were inspected and validated in chat; physical
host identity, no firmware changes, and preservation of supporting records were
owner-confirmed. The later iPhone screenshot was visually inspected separately.

This establishes Caps/Num output capability and the bounded EDR1 17-byte message
roundtrip under the tested workflow. It does not establish arbitrary message
reflection, logging, full DuckyScript 3.0 compatibility, Scroll behavior, Windows
11 support, another keyboard's LED state, or reliable global Caps restoration.
The Razer keyboard was disconnected during the recent formal recordings; broad
Caps/global-flag diagnostics are not a gate for the keyboard-control upgrade.

Keep all original receipts, screenshots, backups and working firmware packages
untouched. New keyboard-control source/tests/build results do not alter this
accepted historical outcome. New firmware behavior remains physically unverified
until separately installed and tested by the owner; producing a package does not
authorize installation, flashing, OTA or real HID execution.
