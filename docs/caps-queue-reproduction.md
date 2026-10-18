# Software-only reproduction

Baseline3dd4a083aa6634cf413ac7a43c36baaa749b7540. Existing working source and
package artifacts are immutable inputs. No board/port/OTA command is involved.
Use fresh external output directories; runners reject overwrite.

Current cloud tools: Python3.12.14, GCC14.2.0, Node24.19.0, ArduinoCLI1.3.1.
The original repository scripts assume the pinned Stage19 native SDK headers at
`/workspace/tooling/stage19-sdk-source`. They were restored with the existing
source-pinned downloader; no private data or SDK binary replacement is involved:

```sh
python3 tools/nvs_source_prepare.py --output /workspace/tooling/stage19-sdk-source
python3 tests/caps_queue/run_tests.py --build-dir /tmp/caps-new-native --results /tmp/caps-new-native.json
node tests/caps_queue/test_ui.cjs /tmp/caps-new-native/sources/webfiles.h
python3 tests/caps_queue/run_related.py --native-results /tmp/caps-new-native.json --build-dir /tmp/caps-new-related --results /tmp/caps-new-related.json
python3 tests/stop_led_package/sender_cleanup_tests.py --results /tmp/caps-new-sender.json
python3 tests/stage28h/verify_freeze.py
```

The actual executed native paths/results were `/workspace/scratch/caps-queue/native6`
and `native6.json`, after documented test/environment corrections. The source
composition hashes are checked before applying every historical overlay and this
new overlay. No earlier test expectations or source files are modified. The new
network mock uses ordered registration and the exact source-derived pinned
BackwardCompatible URI predicate; it is **not the full AsyncTCP task/runtime**.
C++ runners retain ASan/UBSan/leak flags and execute memory-only lower interfaces.

Resource/allocation comparison needs BEFORE and AFTER receiver source directories:

```sh
python3 tests/caps_queue/check_resources.py --base /absolute/path/to/composed-published-source --changed /tmp/caps-new-native/sources --output-dir /tmp/caps-new-resources
```

The actual BEFORE was `/workspace/scratch/caps-queue/base`, composed with unchanged
historical STOP/LED prepare/overlays; AFTER was identical to the source-hash-pinned
new composition. This comparison reports native sizes only, not embedded RAM.

## Clean target build: currently BLOCKED, not a skipped successful check

The exact published Arduino3.3.0 release archive SHA matched the historical receipt;
extraction did NOT match the historical whole-tree fingerprint. All nine individual
Stage15 source pins and framework trees match, but the strict builder still refuses.
See `caps-queue-build-blocker.json`. Do not change the expected tree hash, filter
unknown differences away or mark target verification PASS based on native tests.
The actual `tools/build_s3_patched.py --controlled-normal-start ...` attempt stopped
at `check_sources`: `FAIL: Core tree mismatch`, before patching/building.

Once an independently verified historical protected-core environment is restored,
the existing composition/build checks can be extended without weakening them:

```sh
python3 tests/caps_queue/build_candidate.py --output-dir /tmp/caps-new-linked --config /absolute/path/to/verified-isolated/arduino-cli.json --baseline-build /absolute/path/to/verified-stage26-build --arduino-cli /absolute/path/to/arduino-cli --jobs 2
python3 tests/caps_queue/verify_link.py --build-root /tmp/caps-new-linked --output /tmp/caps-new-checked.json
```

These new wrapper executions have NOT succeeded here. They preserve the protected
core/SDK/profile, composition and final linked checks. No ELF/BIN or installation
package for the new source is represented as verified. No global toolchain is
patched. No saved startup service or auto-launch is needed for this workflow.
