# Reproduce the separately approved archive build

This additive profile implements the owner's approval of f47e46d. Historical
profiles, proposals and verifiers are unchanged and continue rejecting this tree.
This is **not** a reconstruction of the unavailable historical full core tree.
Read docs/mac-install-build-profile-proposal.md for that unresolved discrepancy.

Inputs: Arduino CLI1.3.1; Arduino ESP32 core3.3.0 archive SHA
c8525462e47b37b726c211b71afada0fca5859ba748963e4d967131355716ba2;
ESP-IDF idf-release_v5.5-b66b5448-v1; Xtensa GCC14.2.0 (esp-14.2.0_20241119).
All177 linked SDK archives are compared by SDK-relative path and exact hash to
Stage28W and the working STOP/LED build. Paths differ because isolation is
required; archive content identities do not. No SDK is rebuilt or patched.
NeoPixel1.15.5 is publisher-checksummed and fully inventoried separately;
AsyncTCP3.5.0 and ESPAsyncWebServer3.12.1 retain their previous full-tree pins.

The new pin inherits historical diagnostic fields from Stage18, including its
unused historical HID-only tree and baseline commit. The **selected** new raw and
HID+NVS tree hashes, profile label and publisher archive are explicitly separate.
The proposed archive HID-only fingerprint remains recorded in the approved
proposal; it is not a selectable build in this release.

All paths below are this cloud instance's disposable paths; provide equivalent
verified local paths on a build host. These commands do not access hardware.
No native Mac compiler is required to install the prebuilt package.

```bash
python3 tests/mac_release/prepare_core.py --archive /workspace/tooling/arduino/downloads/esp32-3.3.0.zip --core /workspace/scratch/mac-recovery/cli-data/packages/esp32/hardware/esp32/3.3.0 --destination /workspace/scratch/NEW-archive-core --user /workspace/tooling/arduino/user
python3 tests/mac_release/build_candidate.py --output-dir /workspace/scratch/NEW-release-build --config /workspace/scratch/NEW-archive-core/arduino-cli.json --core /workspace/scratch/NEW-archive-core/data/packages/esp32/hardware/esp32/3.3.0 --arduino-cli /workspace/tooling/arduino/bin/arduino-cli --jobs 4
python3 tests/mac_release/verify_link.py --build-root /workspace/scratch/NEW-release-build --output /workspace/scratch/NEW-linked.json
```

prepare_core requires the exact archive SHA and independently verified raw tree,
then copies core source bytes, applies two exact patches with zero fuzz and
attests the complete patched tree. Tools are shared read-only; outputs/caches
are external. No global core/SDK source is modified. Builder materializes the
selected tests/caps_queue composition, retains all source/ELF/USB/NVS/controlled
startup predicates, disables merged-image generation, and has no upload interface.
The additive startup decoder changes only the core-check import plus the exact
existing bounded disassembly decoders, after pinning the historical verifier SHA.
It does not replace success conditions. Final check records all linker response
files, archive/object/script hashes and checks the real ELF-to-BIN byte equality.

Relevant tests:

```bash
python3 tests/caps_queue/run_tests.py --build-dir /workspace/scratch/NEW-native --results /workspace/scratch/NEW-native.json
python3 tests/caps_queue/run_related.py --native-results /workspace/scratch/NEW-native.json --build-dir /workspace/scratch/NEW-related --results /workspace/scratch/NEW-related.json
node tests/caps_queue/test_ui.cjs /workspace/scratch/NEW-release-build/candidate/EvilDuckS3/webfiles.h
python3 tests/stage28h/verify_freeze.py
```

Additional exact package/profile/parser test commands and results are recorded
in the final report. Use unique output paths: existing evidence is never overwritten.
The installation guide uses fresh owner-local ROM metadata and cannot be tested
against a physical board by this task. No successful build or mock test proves
High Sierra serial transport, host key release, Caps Lock or LED feedback.
