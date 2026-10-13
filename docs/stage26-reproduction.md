# Stage26 reproduction

REVIEW ONLY — NOT AUTHORIZED FOR FLASHING

The existing cloud toolchain was already ready; the setup skill required no global configuration
change. Start from Stage25 commit f929bdf2353e0022f10c164d2c09cb3db2564a5a. No production
source edits are needed. New build/output directories are required; do not reuse owner backups.

```sh
python3 tools/build_s3_patched.py --controlled-normal-start \
  --core-dir "$ORIGINAL_CORE_3_3_0" --user-dir "$LIBRARIES" --arduino-cli "$CLI" \
  --isolation-dir "$NEW_CONTROLLED_CORE" --build-dir "$NEW_CONTROLLED_BUILD" --jobs 2
python3 tools/build_s3_patched.py --deployment-safe-start \
  --core-dir "$ORIGINAL_CORE_3_3_0" --user-dir "$LIBRARIES" --arduino-cli "$CLI" \
  --isolation-dir "$NEW_SAFE_CORE" --build-dir "$NEW_SAFE_BUILD" --jobs 2
python3 tools/stage26_prepare.py --core-dir "$PATCHED_CONTROLLED_CORE" \
  --build-dir "$NEW_CONTROLLED_BUILD" --safe-core-dir "$PATCHED_SAFE_CORE" \
  --safe-build-dir "$NEW_SAFE_BUILD" --mkspiffs "$MK_SPIFFS" --output-dir "$NEW_PUBLIC_REVIEW"
```

Preparation invokes mandatory source and final linked verification, packs/unpacks the empty
filesystem, and publishes the inventory last. Installed cores remain unchanged. Compiled metadata
can vary across clean output paths/times: accept this commit's public binaries against this commit's
trusted pin; a newly rebuilt set with different application hashes needs its own deliberate review.
Do not automatically rewrite trusted pins to bypass a mismatch. No merged image is generated.

Focused automated checks use new external result/build paths:

```sh
python3 tests/stage26/run_tests.py --core-dir "$ORIGINAL_CORE_3_3_0" \
  --sdk-source "$PINNED_SDK_SOURCE" --generator-dir "$PINNED_GENERATOR" \
  --mkspiffs "$MK_SPIFFS" --controlled-core "$PATCHED_CONTROLLED_CORE" \
  --controlled-build "$NEW_CONTROLLED_BUILD" --safe-core "$PATCHED_SAFE_CORE" \
  --safe-build "$NEW_SAFE_BUILD" --results "$NEW_ARTIFACT_RESULTS"
python3 tests/stage25_startup/run_tests.py --sdk-source "$PINNED_SDK_SOURCE" \
  --build-dir "$NEW_HOST_STARTUP_BUILD" --results "$NEW_STARTUP_RESULTS"
python3 tests/stage25_startup/network_tests.py \
  --build-dir "$NEW_HOST_NETWORK_BUILD" --results "$NEW_NETWORK_RESULTS"
python3 tools/analyze_s3_stack.py --build-dir "$NEW_CONTROLLED_BUILD" --output "$NEW_STACK_REPORT"
```

The C++ runners enable ASan/UBSan and startup leak detection. Tests use only synthetic credentials,
selected real production modules and mock interfaces; no physical SDK/USB execution is represented.
The SDK generator and mkspiffs really execute as desktop file tools. See the exact test index/results.
Normal legacy and experimental readonly profiles remain unchanged and were not needlessly rebuilt.
No unrelated historical suites/observations are claimed as newly executed.
