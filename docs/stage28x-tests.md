# Stage28X executed verification

| Suite / classification | PASS | Unexpected FAIL | Assertions |
| --- | ---: | ---: | ---: |
| X new actual-body diagnostics |19|0|2,201|
| Unchanged W |34|0|380|
| Unchanged V |56|0|566|
| Unchanged U |64|0|515|
| Unchanged T |47|0|467|
| Affected production |77|0|67,371|
| Controlled startup |30|0|635|
| Pinned selected framework components |5|0|116|
| Unique current coverage total |332|0|72,251|

Additional comparisons, not extra coverage:34 unchanged W cases/380 assertions on
instrumented X sources;77 production cases/67,371 assertions with disabled portable
selector matched original stdout/stderr/exit exactly. Relevant regressions were
selected because X observes the owner, backend, service snapshots and controlled
startup; no language/runtime rewrite or unrelated suite inflation.

X01 measured copies/work; X02 sparse API bounds; X03 millisecond wrap; X04 invalid/
backward clock; X05 duration saturation; X06 counter saturation; X07 unknown resources;
X08 zero/OOM-like pressure valid; X09 fail-all C++ allocator and2000 idle turns;
X10 real native mutex-held snapshot observer; X11 request/queue/STOP;
X12 actual loop continuous serial; X13 authenticated bounded HTTP; X14 cross-thread
execution contention =>409; X15 formatting truncation/buffer rejection; X16 source
failure; X17 called-false permanent quarantine/first identity; X18 simulated request
pressure +STOP; X19 observational CLI. Resource APIs/tasks/network/NVS/File/USB/clock
are named mocks. Actual patched coordinator, CLI, web handlers, setup/loop, scheduler,
settings/storage and backend bodies are compiled, not toy counter implementations.

Final ASan/UBSan and detect_leaks=1 completed cleanly. Deliberate negative control
changes actual sampling interval1000->1 in separate disposable source; X02 exits1
with `sparse probe bound before1000ms`, not a forced final assert or watchdog. Existing
W/V/U/T negative controls remain expected detections, not unexpected final failures.
The separate selector-negative receipt records an actual compiler rejection of diagnostics
without Route B; it is an expected negative, not an extra coverage pass.
Historical language XPASS, upstream USB XFAIL, Stage9 observations, SDK mutation/
retirement diagnostics remain unchanged and separate; not rerun/relabeled as passes.

Development diagnostics are retained externally, excluded from final totals: initial
native include path/pragma-once alias errors; a development negative link attempted
a newly edited allocation test with an older shim; corrected final stable source
run succeeds. A successful pre-final native run was tightened for X10's explicit
publisher-held snapshot check. Initial target link predating final header/mock-clock
refinement was superseded by clean final links. No installed/owner files were altered.
Machine test-results retains actual commands, exits, per-case output and negative
receipts; no old count is presented as a new full-history execution.

Source/freeze/range audits are structural checks, separately reported, not thousands
of invented test assertions. Every physical, actual FreeRTOS/AsyncTCP execution,
SDK heap/stack observation, media test and USB/host delivery trace: NOT EXECUTED.
