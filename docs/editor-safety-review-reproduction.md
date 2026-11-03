# Editor-safety review — owner offline check and developer reproduction

## Owner first step: no device

From the extracted review ZIP, with EvilDuck unplugged:

```bash
python3 preflight.py --directory .
```

Require exit 0, `package_integrity: PASS`, `installed_metadata: NOT_SUPPLIED`,
`plan_ready: false`, no selected write ranges, `hardware_access: false` and
`installation_authorized: false`. This reads package files only. Do not run an
install/rollback launcher for the offline check. No Git, Arduino, browser driver,
compiler or new dependency installation is needed for this step. The host workflow
targets High Sierra 10.13.6, Bash 3.2, Python 3.8+ and preinstalled esptool 4.12;
actual native execution of this new ZIP remains unverified.

## Exact original application and source context

This packaging stage reuses, without rebuilding, the 1,437,696-byte application
`e825a8fb8e1c52ec998509b0191939e47572806b156ca591e51be1ece356fff0`
and ELF `51e918c98249af4fb79dbd79a31a2ecdbcb92a0045e2d6f213c99cd86e755057`.
The original build ran at Git base
`805d989c3ac50cb96025862c95916830c59f8ba7` with 17 then-uncommitted exact inputs.
Raw `local-inputs.json` SHA-256:
`525fc3f9e95c65f81a1233f3f31eac1f321233d0dd87ac2517d5a4c2f2eab768`.
The package includes it as `local-build-inputs.json`.

Source checkpoint `1664d4f25593e6cc99dba43ff0e5d74531555a51` was created
**after the build**, recording the identical reviewed local files. A Git-blob
attestation verifies all 17 recorded inputs against that checkpoint. It is a
post-build source checkpoint, not a claim that the old build used a future commit.
The 22 files originally local across source repair/integration are now preserved
there. No reviewed input was edited to make packaging work.

## Developer-only source reconstruction (already verified without rebuilding)

The frozen normal builder intentionally requires HEAD at its original base. Keep
that check; do not weaken it or claim that checking out the later checkpoint alone
satisfies it. From this review branch, the following creates a **new detached
source worktree**, restores only the 17 hash-checked new Git blobs from the source
checkpoint and proves its normal builder produces the identical input manifest:

```bash
python3 -B tests/editor_review_package/reproduce_checkpoint.py \
  --checkpoint 1664d4f25593e6cc99dba43ff0e5d74531555a51 \
  --local-inputs /workspace/scratch/editor-build-integration/build-v2-uninstalled/local-inputs.json \
  --output /workspace/scratch/editor-review-package/reconstructed-source-v1 \
  --results /workspace/scratch/editor-review-package/reconstructed-source-v1.json
```

Use fresh output/result paths. The observed result was
`SOURCE_RECONSTRUCTED_ONLY`, 17 materialized files, identical manifest SHA,
`compiler_invoked: false`, `firmware_rebuilt: false`, refs unchanged. This is not
an owner setup requirement or a physical test; it is a developer source check.
On another developer machine use the package's `local-build-inputs.json` as input,
with the repository and recorded checkpoint already available locally. It reads
Git blobs and never downloads source, executes a payload or operates a device.

A separately desired clean build can then use the same canonical entry from that
reconstructed source, with the existing pinned toolchain/configuration and a
fresh build directory:

```bash
python3 -B tools/build_routeb_candidate.py \
  --output-dir /workspace/scratch/editor-review-package/separate-reproduction-build \
  --config /workspace/scratch/led-feedback-isolated-core/arduino-cli.json \
  --core /workspace/scratch/led-feedback-isolated-core/data/packages/esp32/hardware/esp32/3.3.0 \
  --arduino-cli /workspace/tooling/arduino/bin/arduino-cli --jobs 4
```

That build was **not run for packaging**. The delivered image is the existing
verified original, not a speculative rebuild. Output paths/timestamps can affect
image/debug identities; no independent bit-for-bit rebuild claim is made.
Composition, exact tested resources, compiler/core/SDK pins and inherited checks
must pass on any reproduced build; do not silently replace this package's image.

Fresh packaging-stage verification reran the target verifier and full six-layer
release chain against the existing real ELF/BIN. Browser/native/sanitizer receipts
are reused only after matching the tested inputs and compiled resources. Firmware
source/target guards, USB identity, partition geometry and PSRAM-disabled profile
remain unchanged. See the package report for exact evidence and limits.
