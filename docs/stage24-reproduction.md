# Stage 24 offline reproduction

Use the pinned Linux Arduino 3.3.0/GCC14.2/IDF5.5 environment and existing libraries.
No serial/device discovery, upload, flash, erase or OTA command belongs to this workflow.
The globally installed SDK/core is an immutable input. Stock firmware is owner-provided,
not a download dependency. Private owner backups are not required for these software tests.

Production normal and --deployment-safe-start builds use unchanged tools/build_s3_patched.py
and their existing protected-core hashes. Use distinct fresh external core/build directories.
Arduino may automatically emit a merged compile side output; discard that side output.
It must never become a deployment resource. No merge/flash operation is requested here.

```sh
python3 tools/stage24_sdk_scanner.py --core-dir "$VERIFIED_NORMAL_CORE" \
  --build-dir "$VERIFIED_NORMAL_BUILD" --source "$PINNED_PARTITION_TARGET_C" \
  --output-dir "$FRESH_EXTERNAL_REBUILD"
```

This checks original source/core/SDK/compiler and normal final-build provenance, rebuilds
original and corrected objects and compares runtime sections/relocations/ABI. Repeat in
another fresh external directory; archives must match pinned stage24-sdk-pin.json. Outputs
must not overlap protected dependency/source/build/repository directories.

```sh
python3 tools/stage24_candidate.py --experimental-readonly-failclosed-scanner \
  --core-dir "$ORIGINAL_CORE" --user-dir "$LIBRARIES" --arduino-cli "$CLI" \
  --verified-sdk-rebuild-dir "$FRESH_EXTERNAL_REBUILD" \
  --isolation-dir "$FRESH_CANDIDATE_CORE" --build-dir "$FRESH_CANDIDATE_BUILD"
```

The distinct selector accepts only the Stage 24 pinned SDK copy. Stage 22/23 builders
reject it; existing production builders reject experimental tables/cores. The candidate
uses unchanged Stage 22 gate/header/table and safe application source. Its linked Stage 22
quiescent identifier is supplemented by Stage 24 profile and scanner archive/object hashes
in mandatory final provenance. Merged output is discarded, not a migration resource.

Run tests/stage24/scanner_tests.py with --partition-dir, --reference-source, fresh
--build-dir and --results. protection_tests.py takes pinned --sdk-source,
--partition-source, --reference-source, --patched-core, fresh --build-dir and --results.
gate_tests.py instead takes --candidate-core. integration_tests.py takes the three cores,
actual candidate build, both verified SDK rebuilds, extended source reference and bounded
startup audit. The latter can be produced by tools/stage23_startup_audit.py. Run
fresh_tests.py with --core-dir, --sdk-source, --generator-dir, --mkspiffs, fresh
--fixture-output and --results; only explicit synthetic test credentials are used.

fresh_startup_tests.py accepts the same source/core arguments as protection_tests.py plus
--fresh-image pointing to the generated synthetic NVS. It compiles the real SDK/plaintext
settings/core/application sources with mocked services, normal and safe-start variants.
It never executes actual bundled or owner scripts.

For owner-private REVIEW ONLY image preparation, tools/stage24_fresh_images.py requires
--core-dir, --sdk-source, --generator-dir, --mkspiffs, --owner-config and --output-dir.
The JSON input has exactly ssid, ap_password and web_password. Values/images must stay
private and outside Git; no sample owner credentials are invented. Output is fresh NVS,
empty SPIFFS and review inventory; this is not a migration plan, flashing package or physical
provisioning instruction. Incomplete publication is rejected rather than resumed/repaired.

Rollback of offline work means selecting the existing Stage 23 builder/pins and discarding
only disposable new outputs. No owner backup, installed dependency or device was modified.
Physical rollback requires later owner-supplied verified recovery and explicit approval;
no physical recovery commands are supplied here.
