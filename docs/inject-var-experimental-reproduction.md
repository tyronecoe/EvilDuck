# Reproduction — offline experiment only

Use fresh disposable output directories. The source composition, native regression runner and build/link wrappers hash-pin historical parents; global dependencies and accepted sources remain untouched. No command here opens hardware, sends HID or constructs an installer. The target build's images remain local research outputs.

```bash
python3 tests/inject_var_experimental/run_tests.py --core /workspace/scratch/led-feedback-isolated-core/data/packages/esp32/hardware/esp32/3.3.0 --build-dir /workspace/scratch/inject-var-experimental/native-v2 --results /workspace/scratch/inject-var-experimental/native-v2.json
python3 tests/inject_var_experimental/test_reference_results.py
python3 tests/inject_var_experimental/build_candidate.py --output-dir /workspace/scratch/inject-var-experimental/build-v1 --config /workspace/scratch/led-feedback-isolated-core/arduino-cli.json --core /workspace/scratch/led-feedback-isolated-core/data/packages/esp32/hardware/esp32/3.3.0 --arduino-cli /workspace/tooling/arduino/bin/arduino-cli --jobs 4
python3 tests/inject_var_experimental/verify_link.py --build-root /workspace/scratch/inject-var-experimental/build-v1 --output /workspace/scratch/inject-var-experimental/linked-final2.json
python3 tests/stage28h/verify_freeze.py
```

The focused primary-source trace consumes the public captured HTML after verifying its exact hash, then executes selected reviewed functions in bounded Node contexts with explicit mocks. The exact trace invocation is `python3 tests/inject_var_experimental/compiler_trace.py --page /workspace/scratch/inject-var-experimental/research/4b83bb20574b81.txt --output /workspace/scratch/inject-var-experimental/research/compiler-trace-final2.json`; use a fresh output path and the independently retrieved hash-matching public capture. This is not a full compiler/UI/runtime run or an execution of reference-repository payload scripts. The preserved25checks are historical evidence, not rerun as the main result. New assignment/copy/EXFIL and competing-hypothesis checks have separate receipts. NodeVM is not claimed as a general security sandbox.

Native-only `-fno-access-control` supports fault injection without production hooks; no such option is allowed in target firmware. ASan/UBSan/leak options, actual commands/tool versions, generated-only historical expectation adaptations and any development failures appear in the native receipt. Historical classifications and original unresolved vectors remain unchanged. Reference-parser fixtures are manufactured data, not device evidence. No broad Caps or reference-repository audit is repeated.
