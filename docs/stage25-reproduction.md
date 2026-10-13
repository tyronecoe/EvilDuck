# Stage 25 reproduction and review

Use the existing isolated Arduino3.3.0 environment. No global dependency edit or physical
operation is required. `tests/stage25` is the historical Stage2.5 suite and was not overwritten;
new focused tests are under `tests/stage25_startup`.

```sh
python3 tools/build_s3_patched.py --controlled-normal-start \
  --core-dir "$ORIGINAL_CORE_3_3_0" --user-dir "$LIBRARIES" --arduino-cli "$CLI" \
  --isolation-dir "$FRESH_CONTROLLED_CORE" --build-dir "$FRESH_CONTROLLED_BUILD"
```

Use no selector for legacy normal, --deployment-safe-start for quiescence. The existing
Stage24 readonly candidate builder retains its explicit separate selector, SDK pin and
Stage22 table/gate. Never substitute its table into the controlled candidate. Startup-profile
conflicts fail closed. Every build needs mandatory final source/core/SDK/ELF/bin/table
verification. The normal builder now disables its automatic merge hook and validates
individual images/OTA data; it does not fabricate a padded image to satisfy old tooling.

Focused startup tests take --sdk-source, fresh --build-dir and --results. network_tests.py
requires fresh --build-dir/--results; it extracts and executes the actual AP helper only.
regression_tests.py takes the same SDK/build/results inputs and runs affected legacy settings
and persistence cases. recovery_tests.py requires original core plus normal/safe/controlled
cores/builds and --results, and checks compiled artifacts with temporary format-fault vectors.
Existing tests/stage1/run_tests.py checks the five runtime/cancellation/ownership regressions.

Private factory preparation is tools/stage25_fresh_config.py with --core-dir, --sdk-source,
--generator-dir, --mkspiffs, --owner-config and --output-dir. Existing pinned Stage24
factory generation and verification are retained, with the additional legacy-password
rejection. Credential inputs and generated NVS stay private/outside Git; no default owner
password is supplied. Empty SPIFFS uses0x160000/block4096/page256; no old-size relocation.
No output/backup is overwritten. This is not firmware installation authorization.

Recovery checking is read-only as described in stage25-recovery-readiness.md. Actual owner
files were not available here. Run locally and provide only the privacy-safe resource
summary if preferred. Public review binaries are available in review/stage25-controlled
and every exact size/hash is recorded there; they are not a complete deployment set.

High Sierra GCC execution is unverified. The source/profile is reproducible in the verified
Linux environment; public prebuilt binaries allow offline Mac inspection without assuming
local compilation. The owner already has working Python3.8.10/esptool4.12.0 for ROM checks.
No upgrade or physical access is performed by these file-only utilities.
