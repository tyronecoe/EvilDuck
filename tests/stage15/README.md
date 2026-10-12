# Stage15 actual routing-source investigation

`python3 tests/stage15/run_tests.py --core-dir /path/to/esp32/3.3.0 --build-dir /tmp/stage15-routing --results /tmp/stage15-routing-results.json`

Use a fresh external build directory. The runner verifies installed source hashes,
extracts the actual report-ID lookup/dispatch/SET_REPORT callback bodies, and compiles
these against the actual EvilDuck backend plus RAM USB/storage/clock mocks. It also
extracts the stock keyboard OUT callback with a name-only adapter. These are boundary
probes, not compilation of the whole vendor stack or proof of physical packet reachability.

Original sanitizer crashes must contain a generated upstream source frame and match
expected faults to count XFAIL; they are separate from passing candidate guards. The
paired core/firmware proposals are applied only to temporary copies; neither installed
core nor shipped firmware changes. No hardware, real HID, flash/erase/OTA/format call.
Debug-enabled malformed report-type indexing is distinct from the normal log-off
firmware profile. Zero valid transfer backed by a64-byte allocation demonstrates
underflow without claiming that normal TinyUSB hands out a null/onepast buffer.

reference-vectors.json keeps DS3 numeric encodings null/unresolved. Existing USB HID
translation vectors are checked against actual translation; they do not prove packed
INJECT_VAR conformance. Restart acceptance cases are design specifications, not executed
restart tests. Physical cases in the readiness document are explicitly NOT RUN.
