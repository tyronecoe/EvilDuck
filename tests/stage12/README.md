# Stage 12 offline production-source tests

`python3 tests/stage12/run_tests.py --build-dir /tmp/evilduck-stage12 --results /tmp/stage12-results.json`

Builds the actual scheduler, HID backend, parser/evaluator/functions, locale, CLI,
Stage10 attackmode/MSC/SD production modules against RAM filesystem/storage, mocked
USB endpoints and clock. ASan/UBSan are enabled. No device enumeration, ports, real
HID, media writes, erase, migration or OTA operations. SD source adapters remain RAM
mocks; separate backing-image fault probes link the production SD/MSC adapters.

All exact test names/results/assertions are included in the delivery report/results
JSON. Virtual dispatch tests call the actual derived keyboard callback through the
mocked base interface. They do not execute the entire Arduino/TinyUSB USB transfer
path. Source/build verification identifies its routing and descriptor contracts;
physical USB control/interrupt OUT behavior remains unverified.

Feedback tests cover every valid five-bit LED value, three lock masks, padding and
ID/size/null rejection, duplicates/transitions, unknown state, saved evidence,
concurrency, cancellation, timeout, session invalidation and stale explicit tokens.
Tests of functions/IF/WHILE/DEFINE/text use the same production evaluator. Restores
require observed feedback, verify exact ID1/instance0/eight-byte reports and zero
release padding, and never derive acknowledgments from accepted input reports.
Tests exercise wrong/missing feedback, backpressure and stale planned toggles.

Registry tests protect all37 audited native names, preserve extension-defined $_OS,
check read/write policy and table independence, and expose truthful Stage10 requested,
preparing, active, ejected, failed and retry states. Canonical unsupported native
variables remain unsupported; observations of their diagnostics are not language
compatibility passes.

The allocation probe instruments C++ new/delete for 10000 feedback/registry/save
cycles after initialization, separately from String parsing, filesystem drivers,
web requests and transport library initialization. A zero result applies only to
that bounded hot path, not overall firmware heap behavior. Transition counters are
uint32; a test crosses65536 events to prove no16-bit alias. Session generation and
counters have theoretical2^32 wrap, not unlimited histories.
