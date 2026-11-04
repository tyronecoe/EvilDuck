# Static-response repair: affected native privacy regressions

This adapter reruns the existing 28 Privacy Fix 1 cases and 558 composed
regressions with the actual repaired `webserver.cpp`. It preserves their C++
drivers, assertions, selectors and sanitizer flags. It also retains the frozen
editor adapter's nine inert dashboard browser groups.

The target composition is checked against
`tests/static_response_build_integration/source-manifest.json`. The native
implementation binds `cli.cpp`, `webserver.cpp`, `settings.cpp` and the complete
`webfiles.h` to those exact target bytes. Native fixture identities remain the
historical generated identities; the new target's metadata-only identity change
is verified separately by its ELF/BIN target checks.

Only two native setup adaptations are added to the SHA-pinned editor runner:

1. Apply the reviewed static-response patch once to the native webserver, requiring
   the exact before/after hashes and no other generated source changes.
2. Copy the actual highest-priority historical `tests/caps_queue/mocks` directory,
   verify each file against commit `e692435a7c70dbc0d917bbff733c57900cf7d57c`, then
   add one explicit byte-pointer/length `send` overload in generated `network.h`.

The additional mock overload captures bytes into the existing response fixture;
it does **not** model streaming or ESP32 heap use. Actual SDK forwarding,
constructor/fill behavior and memory-pressure controls belong to the separate
`tests/dashboard_response_safety/test_native.py` suite. The generated mock retains
the existing HTTP send callbacks and backward-compatible route ordering.

Use fresh output paths in the existing Linux developer environment:

```bash
python3 -B tests/static_response_privacy_regression/run_tests.py \
  --core /workspace/scratch/led-feedback-isolated-core/data/packages/esp32/hardware/esp32/3.3.0 \
  --build-dir /workspace/scratch/static-response-privacy-regression/native-new \
  --results /workspace/scratch/static-response-privacy-regression/native-new.json \
  --target-composed /path/to/verified/final/EvilDuckS3
```

Earlier `native-v1` and `native-v2` setup attempts are preserved in scratch logs:
the first selected a mock preceding later HTTP callback additions; the second
correctly refused an assumed mock selection. The final adapter verifies the
actual inherited include selection before copying it. No production change or
test expectation was made to resolve these harness setup issues.

No Arduino/Xtensa firmware build, package, network/device access, real HID,
installer or owner-credential use occurs in this suite. Passing native mocks
does not establish High Sierra, iPhone, NVS flash or physical USB behavior.
