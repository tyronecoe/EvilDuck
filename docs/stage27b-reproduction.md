# Stage27B offline reproduction

NOT FLASH-AUTHORIZED. No Stage26 profile or artifact is regenerated.

From the Stage27B branch, use fresh outside-checkout paths:

```sh
python3 tests/stage27b/run_tests.py --build-dir "$NEW_HOST_TEST_DIR" \
  --results "$NEW_HOST_RESULTS_JSON"
python3 tests/stage27b/target_check.py --baseline-build "$FROZEN_STAGE26_BUILD_DIR" \
  --original-core "$ORIGINAL_CORE_3_3_0" --output-dir "$NEW_TARGET_OBJECT_DIR"
```

Host runner uses g++/C++17 with ASan/UBSan, leak detection, warnings-as-errors (only compact
formatting's misleading-indentation diagnostic is disabled). Every case runs as its own process
with a20-second external timeout. This preview has its own compile/runtime bounds regardless of
that timeout. The sanitizer tests really execute the new core; no old counts are reused.

Target check requires the existing reviewed Stage26 controlled build receipts/compile database
and unchanged installed core. It verifies original core identity, compiler SHA and SDK NVS archive/
QIO_QSPI sdkconfig hashes, then compiles only two temporary objects with the actual pinned flags.
The sizes object encodes sizeof(Program/Runtime/Event/Instruction). No firmware ELF/BIN, SDK
archive replacement, global installation change or physical operation occurs. Local outputs
contain no owner inputs. The target object is software evidence, not firmware integration.

The public fixture is executed only through the mock sink. Visible output is:

```text
ready
middle
ready
complete
```

Each line ends with a mock ENTER. invalid.duck fails preflight with no events. There are no
host-shell commands, credentials, exfiltration or offensive fixture payloads. USB timing, layout
translation, keyboard release and storage streaming integration are intentionally not claimed.

Frozen Stage26 source/review file sizes and SHA-256 are in stage27b-stage26-freeze.json. Compare
them to the immutable Stage26 commit; use only Stage26 artifacts for separately authorized
Stage27A hardware work. Recompiling or installing Stage27B is not part of that process.
