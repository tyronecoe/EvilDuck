# Reproduce installation-package checks (offline from hardware)

Existing checkout `/workspace/EvilDuck-stage6`; no setup configuration changes
were needed. Use Python3.8+ for package tools, Bash, Git, GCC `cc` for the cleanup
harness. Development verification ran on Linux, Python3.12. No Arduino compilation.
Do not execute host sender or owner hardware commands as tests.

Existing verified inputs (not regenerated):

- `docs/stop-led-build.json` and `/workspace/tooling/stop-led/linked-final/build`.
- `docs/keyboard-shortcuts-build.json` and
  `/workspace/tooling/shortcuts-dev/linked-verified/build`.
- Isolated core `/workspace/tooling/stage26-final-controlled-core/data/packages/esp32/hardware/esp32/3.3.0`.
- Public OTA inspection template `review/stage26-installation/ota-app0.bin`.

Use NEW external output paths for each reproduction; builder rejects overwrite.

```bash
python3 tests/stop_led_package/package.py --directory /tmp/stop-led-package-NEW --build /workspace/tooling/stop-led/linked-final/build --core /workspace/tooling/stage26-final-controlled-core/data/packages/esp32/hardware/esp32/3.3.0 --rollback-build /workspace/tooling/shortcuts-dev/linked-verified/build --archive /tmp/stop-led-install-NEW.zip
python3 tests/stop_led_package/run_tests.py --directory /tmp/stop-led-package-NEW --archive /tmp/stop-led-install-NEW.zip --ota-template review/stage26-installation/ota-app0.bin --results /tmp/stop-led-package-results-NEW.json
python3 tests/stop_led_package/sender_cleanup_tests.py --results /tmp/stop-led-cleanup-results-NEW.json
```

Actual run used `/workspace/tooling/stop-led-install/package` and the committed
ZIP path. Full outputs copied to the three `stop-led-install-*-results.json`
files (package results is `stop-led-install-results.json`). Package runner reports
37 PASS. Cleanup output separates 8 executable combinations from 3 C# static checks.
No assertion grand total is fabricated for these focused Python/C/static checks.

The esptool parser-only harness requires esptool **4.12.0** in an isolated Python
environment, never a global installation. The already prepared environment is
`/workspace/tooling/stop-led-install/esptool-env`. Its source archive URL and
SHA-256 are in `stop-led-install-tool-evidence.json`. Verify that archive before
installing it into a fresh disposable venv. Only version/help and a parser AST
prefix are executed; the latter excludes the connection/operation dispatcher.

```bash
/workspace/tooling/stop-led-install/esptool-env/bin/python -m esptool version
/workspace/tooling/stop-led-install/esptool-env/bin/python tests/stop_led_package/tool_parser_tests.py --directory /workspace/tooling/stop-led-install/package --results /tmp/stop-led-parser-results-NEW.json
cc --version
python3 --version
bash --version
```

The parser source SHA is independently pinned in its harness. Successful parsing
of the guide's address/file/keep flags is not physical programming verification.
Native Apple IOKit and Windows C# execution remain pending. No new setup scripts,
global dependency modifications, firmware rebuilds or device access are needed.
