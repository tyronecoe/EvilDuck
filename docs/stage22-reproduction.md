# Stage 22 offline reproduction

**EXPERIMENTAL — REVIEW ONLY — NOT AUTHORIZED FOR FLASHING**

Use Arduino ESP32 3.3.0, the pinned GCC14.2 toolchain/SDK inputs and existing Arduino
libraries. Keep the installed core untouched. These commands compile or inspect files
only. No serial port, esptool physical command or uploader is invoked. High Sierra
compatibility of these firmware build tools has not been established by Codex.

Normal and production safe builds retain the existing wrapper:

```sh
python3 tools/build_s3_patched.py --core-dir "$CORE" --user-dir "$LIBRARIES" \
  --arduino-cli "$CLI" --isolation-dir "$NEW_NORMAL_CORE" --build-dir "$NEW_NORMAL_BUILD"
python3 tools/build_s3_patched.py --core-dir "$CORE" --user-dir "$LIBRARIES" \
  --arduino-cli "$CLI" --isolation-dir "$NEW_SAFE_CORE" --build-dir "$NEW_SAFE_BUILD" \
  --deployment-safe-start
```

The candidate has an explicit required selector and separate fresh external directories:

```sh
python3 tools/stage22_candidate.py --experimental-readonly-quiescent \
  --core-dir "$CORE" --user-dir "$LIBRARIES" --arduino-cli "$CLI" \
  --isolation-dir "$NEW_EXPERIMENTAL_CORE" --build-dir "$NEW_EXPERIMENTAL_BUILD"
```

The same exact FQBN is used: `esp32:esp32:esp32s3:USBMode=default,CDCOnBoot=cdc,FlashSize=16M,PartitionScheme=custom,FlashMode=qio,PSRAM=disabled,CPUFreq=240,MSCOnBoot=default,DFUOnBoot=default`.
The candidate's application snapshot is byte-identical except its separate CSV. Required
USB/NVS and safe-start compiler flags are verified, and the disposable core receives the
Stage16/18 patches before the candidate patch/header pair. Pin mismatches fail closed.
There is no upload mode. Final verification regenerates the app from ELF and checks the
real gate and branch before the initializer. Generated padded merged bytes are removed;
review-only inventory collection never copies them.

With fresh external output and the candidate core path from its receipt:

```sh
python3 tests/stage22/run_tests.py --sdk-source "$VERIFIED_NVS_SOURCE" \
  --partition-source "$VERIFIED_PARTITION_TARGET_C" --reference-source "$VERIFIED_STARTUP_REFERENCES" \
  --candidate-core "$CANDIDATE_CORE" --build-dir "$NEW_NATIVE_BUILD" --results "$NEW_NATIVE_RESULTS"
python3 tests/stage22/integration_tests.py --original-core "$CORE" \
  --normal-core "$NORMAL_CORE" --safe-core "$SAFE_CORE" --candidate-core "$CANDIDATE_CORE" \
  --candidate-build "$NEW_EXPERIMENTAL_BUILD" --inventory "$NEW_REVIEW_INVENTORY" \
  --results "$NEW_INTEGRATION_RESULTS"
```

SDK reference preparation/pins remain Stage19–21's documented process. New header
provenance is in stage22-header-evidence.json; all three actual headers matched the
immutable official SDK commit. Actual archive/header hashes are also checked by the
candidate verifier. Native tests require Linux g++ and ASan/UBSan; they do not run the
Xtensa firmware/RTOS/ROM. Production-source service adapters emit no real HID.

Review inventory is not a deployment manifest. It is explicitly unauthorized and binds
artifact size/hash/profile/table/ELF identity. Original backups and repacked filesystem
are not supplied, fabricated or included. Discard disposable directories to roll back
the experiment; production builders still use the original dependency pins/CSV. No
installed toolchain or device rollback is necessary because neither is modified.
