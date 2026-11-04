# Static-response repair: offline review and developer reproduction

## Owner first step

Extract the new review ZIP into a fresh folder. With EvilDuck **unplugged**, run:

```bash
python3 preflight.py --directory .
```

Require exit 0 and `package_integrity: PASS`. Without installed metadata, expect
`plan_ready: false`, `selected_write_ranges: []`, `hardware_access: false` and
`installation_authorized: false`. This reads package files only. Do not invoke
an installer/device-check or rollback launcher for this offline check.

Python 3.8+ standard library is sufficient for preflight. No Git, Arduino, browser
driver, new dependency installation or connection to the board is needed. The
guarded installation workflow retains its High Sierra 10.13.6 / Bash 3.2 /
Python 3.8+ / preinstalled esptool 4.12 target. Native execution of this new ZIP
and dashboard behavior remain pending owner verification.

## Exact build source and normal entry

Firmware source checkpoint:
`68f7fb2de5af2988a3136eb9222fb8c3e7dee8f5`.

The source-only repair was preserved first at
`7c3ed81238b89b89b92924c366ecbb9afe391856`. The firmware checkpoint then selects
it through the canonical normal entry, preserving the editor/privacy/dashboard
stack and adding only the new build-identity literal. The recorded compiler
inputs are committed Git blobs, not an older base plus untracked changes.
`build-inputs.json` and `source-attestation.json` in the ZIP bind those blobs.
Historical source-only reports describe their earlier stage; the new report is
the current integration/build status. A host-only post-link decoder correction
was needed after the one compile: Xtensa formed several lengths with signed
`MOVI` plus `ADDMI`, rather than the direct-immediate/literal forms recognized by
the first decoder. The correction retains exact length checks and is separately
revisioned in the final report. It changes no compiled firmware source or image.

Developer-only reproduction requires the exact pinned existing toolchain, SDK
and archive configuration. The final review branch contains the corrected host
decoder and keeps the normal entry selected by default. Use a clean checkout and
a **fresh** output directory. The following normal build command was used for the
single actual compile at the source checkpoint above:

```bash
python3 -B tools/build_routeb_candidate.py \
  --output-dir /workspace/scratch/static-response-repair-review/build-v1 \
  --config /workspace/scratch/led-feedback-isolated-core/arduino-cli.json \
  --core /workspace/scratch/led-feedback-isolated-core/data/packages/esp32/hardware/esp32/3.3.0 \
  --arduino-cli /workspace/tooling/arduino/bin/arduino-cli --jobs 4
```

Choose another fresh output path when reproducing; never overwrite the release
evidence directory. The command exposes no hardware/installation operation.
It preserves the approved isolated Arduino ESP32 3.3.0 archive-based profile,
dependency checks, partitions, USB identity and PSRAM-disabled settings. Do not
use older stage-specific builders and assume they select the new repair.

The compile/link completed at that checkpoint. Its initial target verification
stopped on the decoder-format issue. The post-link resume step uses the existing
image without recompiling. Original compile inputs and their hashes remain intact,
with the host verifier-only old/new revision and hashes recorded separately.
The final report gives the exact post-link resume command and verification
checkpoint. Reproduction from the final corrected branch uses that current
committed source revision and may produce different artifact identities.

The actual verification-only completion used host verifier revision
`89d499fdb4dde13782cb09c7882ab55cc604a4dd` and completion helper revision
`520716462ffd66858a686e6c3a06eae037b3c5d4`:

```bash
python3 -B tests/static_response_postlink/complete_existing.py \
  --build-root /workspace/scratch/static-response-repair-review/build-v1 \
  --snapshot /workspace/scratch/static-response-repair-review/original-compiled-checkpoint \
  --results /workspace/scratch/static-response-repair-review/postcompile-completion-v2.json \
  --verify-existing
```

This records the command already executed; its paths contain preserved evidence.
The helper refuses existing output receipts and applies only to the exact recorded
image/snapshot. It is not a general resume bypass for arbitrary builds. Fresh
developer builds should use the corrected normal entry on the final branch.
The only permitted compiler command during completion was the SHA-pinned
two-argument `-print-prog-name=ld` query used by an inherited linker-location
guard. No source compilation or firmware relink occurred.

The normal entry enforces a committed input checkpoint, executes one deterministic
overlay chain and performs mandatory target/release verification. Outputs include
`build-inputs.json`, `static-response-composition.json`,
`static-response-target-verification.json`, `report.json` and
`static-response-release-verification.json`. A failed guard blocks publication;
do not substitute another image, remove a check or rerun compilation merely to
make verification pass. Build paths/timestamps may affect artifact identities;
no independent bit-for-bit rebuild claim is made.

## What the target proof must establish

Resource presence alone was insufficient in the earlier e825 image. The new
verification also inspects the actual compiled/linked static handler, its
byte-pointer/length overload and SDK factory/Progmem response implementation.
It binds source/dependency/object/map LOAD identities and exact resource pointers
and non-NUL lengths. It verifies all five complete dashboard/settings resources
once in the actual ELF and BIN, and runs the inherited six-layer release chain
with all 190 inherited Python verifier Assert nodes preserved. This is a source
predicate count, not 190 independently executed test cases. The small existing unknown-path 503
response remains allowed; globally banning every ordinary response would be
incorrect.

Native transport and browser checks are inert software tests. They do not measure
real ESP32 heap availability or establish native Mac/iPhone/other-platform runtime
acceptance. The owner-observed empty response is preserved separately from the
inferred allocation-pressure trigger and the new candidate's pending acceptance.

## Packaging and recovery

The packaging checkpoint is separate from the firmware source checkpoint. The
packager requires its exact committed sources/docs and a frozen release binding
for the verified new application/ELF/receipt/input manifest. It uses the existing
reviewed Mac installer unchanged apart from generated release-binding values.
The final report/publication receipt records the ZIP identity and commit-pinned
download after a fresh download comparison.

The previous e825 application is historical **faulty firmware**, not a known-good
recovery target. The mandatory exact older source/text-v2 rollback remains
`cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02`,
1,413,200 bytes. It has no Privacy Fix 1 or subsequent dashboard/editor/response
repairs. It is application-only and does not restore scripts or old settings.
Existing private backups, including the owner's `w7uhm8z7` backup, are neither
read nor included. Installation, flashing, OTA, payload execution and owner
acceptance remain separate owner-operated steps.
