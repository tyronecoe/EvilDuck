# Offline reproduction — HTTP snapshot contention

Run from the repository root, without connecting a device. All build/native output
paths below are disposable directories outside the repository and must be absent.
No command here opens a device, uploads firmware or invokes flashing/OTA.

Measured environment: Debian host GCC14.2.0, Python3.12.14, Arduino CLI1.3.1,
Xtensa GCC14.2.0 (`esp-14.2.0_20241119`). Exact dependency hashes/flags are in
`docs/http-snapshot-build.json`; source composition pins are in the HTTP, keyboard
shortcut and Stage28X manifests. No hardware or native macOS result is inferred.

The existing isolated patched-core installation and prior verified build must
already exist. The builder rejects wrong hashes and framework identities; it does
not install packages or alter a global Arduino/SDK installation.

```sh
python3 tests/http_snapshot/run_tests.py \
  --build-dir /workspace/tooling/http-snapshot/native-repro \
  --results /workspace/tooling/http-snapshot/native-repro.json
python3 tests/http_snapshot/run_related.py \
  --native-results /workspace/tooling/http-snapshot/native-repro.json \
  --build-dir /workspace/tooling/http-snapshot/related-repro \
  --results /workspace/tooling/http-snapshot/related-repro.json
python3 tests/http_snapshot/run_negative.py \
  --native-results /workspace/tooling/http-snapshot/native-repro.json \
  --build-dir /workspace/tooling/http-snapshot/negative-repro \
  --results /workspace/tooling/http-snapshot/negative-repro.json
python3 tests/http_snapshot/build_candidate.py \
  --output-dir /workspace/tooling/http-snapshot/build-repro \
  --config /workspace/tooling/stage26-final-controlled-core/arduino-cli.json \
  --baseline-build /workspace/tooling/arduino/build/stage26-final-controlled \
  --arduino-cli /workspace/tooling/arduino/bin/arduino-cli --jobs 2
python3 tests/http_snapshot/verify_link.py \
  --build-root /workspace/tooling/http-snapshot/build-repro \
  --output /workspace/tooling/http-snapshot/link-repro.json
python3 tests/http_snapshot/test_verifier_controls.py \
  --build-root /workspace/tooling/http-snapshot/build-repro \
  --output /workspace/tooling/http-snapshot/verifier-repro.json
python3 tests/stage28h/verify_freeze.py
```

The negative runner exits0 only when the intended immediate-409 H01 failure is
observed; that is separate expected-failure evidence, not a positive case.
ASan/UBSan and leak settings are recorded in the native runners/results.

For this delivery, native-final/related/negative and linked-final were the actual
output directories. The clean compiler succeeded before the decoder correction;
`--verify-existing` resumed provenance verification, checked expanded properties
(except Arduino's two generation-time values), retained stored original properties
and reran the unchanged safety predicates. It is not needed for a fresh build.

A reproduction at a different path/time can change ELF/application hashes; verify
that build's own linked provenance instead of claiming byte reproduction of this
receipt. Published artifact identities refer only to the exact reviewed build.

Future physical observation requires separate owner approval. Useful evidence,
if later authorized, would include spaced authenticated endpoint success/busy
counts, ticks/completedTurns/observationAgeMs, executionContentions/Timeouts,
lastContendedOwner, maxExecutionHoldUs and STOP result, with private settings and
credentials omitted. No automated hardware procedure is included here.
