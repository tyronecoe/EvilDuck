# Stage 9 harmless compatibility observation library

Run from repository root:

```
python3 tests/stage9/run_tests.py --build-dir /tmp/evilduck-stage9 --results /tmp/stage9-observations.json
```

Python3, g++, and ASan/UBSan are used; HID, clock and SPIFFS/SD source adapters are RAM mocks. No port discovery, serial access, flash, host command injection, network payloads or hardware operations occur.39 human-readable .duck fixtures run on both mocked source profiles; one separate probe links **production attackmode.cpp** with a failing MSC stub. External fixture files enable independent script review; `fixtures.json` distinguishes canonical/reference expectation from expected current observations.

`OBSERVED` means the harness reproduced the expected **current** output/diagnostic and checked termination/nonblocking/released keys. A matched GAP is still unsupported; an UNRESOLVED result is not canonical proof. These79 observations are reported separately from the380 existing regression passes.The final run has596 observation assertions, separately recorded in docs/stage9-observations.json. Do not add audit gaps to the historical XFAIL/XPASS suite or inflate the language pass count.

All fixture outputs are simple visible words/numbers or mocked key operations. Unsupported commands are rejected before any output; preceding MUST-NOT-APPEAR text detects failed preflight. The production attackmode failure probe records a false-success/retry suppression defect, not a successful attack-mode implementation. No reference runtime is available for eager evaluation/overflow/implicit returns; those entries stay unresolved. Script interpolation cases clearly label the EvilDuck extension.

Storage mocks do not validate real SD mounts/path normalization, real SPIFFS geometry, USB callback offsets or host enumeration. Those gaps are expressly listed in the audit and roadmap.

The inline_trailing.duck fixture intentionally contains three trailing spaces. A git diff whitespace warning on that line is expected test data, not accidental formatting; removing it would destroy the whitespace observation.
