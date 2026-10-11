# Stage 13 offline production-source verification

`python3 tests/stage13/run_tests.py --build-dir /tmp/evilduck-stage13 --results /tmp/stage13-results.json`

Compiles actual S3 parser, preprocessing, source reader, expression/function runtime,
cooperative command scheduler, HID backend and Stage10 storage modules. All clocks,
USB endpoints, output, files and SD media are RAM mocks. ASan/UBSan are mandatory in
this harness. No serial discovery, physical HID/storage or write/erase/OTA operation.

Fourteen separately named alias fixtures cover all documented languages/families.
Other cases check source syntax, ordered inclusion, strict boundaries, frozen seek
behavior, faults, ownership/cancellation, runtime integration and LED policy. Tests
are independent processes; a nonzero exit is FAIL, never a compatibility pass.
The allocation probe checks bitmap membership over every source-line boundary after
setting two bits; it does not claim String parsing is allocation-free.

The two `.duck` examples are harmless visible-output fixtures. `source-compatibility`
outputs `literal IF/WHILE text` plus Enter; `excluded-source` outputs `included-only`
plus Enter. Their file contents are exercised verbatim by named regression cases.
Stage9 observations retain gap classifications where behavior remains unsupported;
resolved comment, alias, wrapper, preprocessing and LED fixtures are separately
labelled RESOLVED_STAGE13. Historical five XPASS labels remain auditable.
