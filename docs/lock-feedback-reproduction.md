# Offline reproduction

Use an isolated output directory for each run. No command here accesses a board.
Historical files and toolchains are read-only. Parent source, overlay patch and
all before/after hashes are pinned in `tests/lock_feedback/source-manifest.json`.

```bash
python3 tests/lock_feedback/run_tests.py --core /workspace/scratch/led-feedback-isolated-core/data/packages/esp32/hardware/esp32/3.3.0 --build-dir /workspace/scratch/NEW-lock-native --results /workspace/scratch/NEW-lock-native.json
python3 tests/lock_feedback/test_led_action.py
python3 tests/stage28h/verify_freeze.py
python3 tests/lock_feedback/build_candidate.py --output-dir /workspace/scratch/NEW-lock-build --config /workspace/scratch/led-feedback-isolated-core/arduino-cli.json --core /workspace/scratch/led-feedback-isolated-core/data/packages/esp32/hardware/esp32/3.3.0 --arduino-cli /workspace/tooling/arduino/bin/arduino-cli --jobs 4
python3 tests/lock_feedback/verify_link.py --build-root /workspace/scratch/NEW-lock-build --output /workspace/scratch/NEW-lock-linked.json
```

Build requires the previously approved separately pinned archive feedback profile,
Arduino ESP32 3.3.0 and exact dependency/source pins. USB routing and Arduino
NVS no-auto-erase protections, startup checks, 16MiB geometry, PSRAM disabled,
USB-OTG/TinyUSB/CDC and existing CPU/flash settings remain mandatory. No SDK
archives are rebuilt or replaced. The new selector and keyboard selector are
both mandatory; no fallback builder is supplied. Global installed dependencies
are not patched. Final link checks cover actual source identities, compile
flags, linked call edges, startup, archives, linker scripts/response files,
ELF-to-BIN regeneration and unchanged table identity.

Native tests build actual composed production modules with mocked USB/storage,
ASan/UBSan and leak detection. Each case runs in its own process. Earlier tests
are retained; only copied test build-ID literals reflect this candidate. Old
W34's obsolete 401-on-contention expectation stays separately classified; the
current authenticated 409 contract is tested by H09/H10/H18. Historical unsupported
ownership E18/K23 remain history rather than being relabelled as passes.

Packaging uses `tests/lock_feedback/package.py` after committing its exact source
and obtaining a successful new post-link receipt. It binds public image bytes,
ELF identity, new source pin, checked rollback and immutable support hashes.
`test_package.py` uses disposable public copies; `test_bound_installer.py` uses
only an injected fake esptool class. Neither opens a serial device or invokes
the real hardware dispatcher. Run the public `preflight.py --directory .` for
read-only package validation; absent current installed metadata deliberately
returns no executable write plan. The installer remains separate-owner-approved.

Publication is a new branch only, without merge/force-push or previous ref changes.
Verify commit-pinned downloads by byte size and SHA-256. This proves publication
integrity, not board installation or native macOS compatibility.
