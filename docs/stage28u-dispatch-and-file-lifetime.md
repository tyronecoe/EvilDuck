# Stage28U dispatch, status and file lifetime

Scratch `duckscript::run(String)` remains legacy. New explicit
`duckscript::runRouteB(const char*)` copies a bounded request; no DuckyScript
command, web mode toggle, autorun or startup output is added. `run`, `stop`,
`running`, `update`, `runningScript`, `currentLine` and `lastError` are actual
production functions compiled in the native candidate. STOP routes to the engine
that owns execution. Existing CLI stop/status remain usable while other CLI
commands reject before execution. Legacy selection clears stale native display.

`route_u::Status` is copied under the short lock: phase, first reason, request ID,
physical diagnostic line, compiler/runtime numeric error code and engine-owned
flag. Phases include Queued, Capturing, Verifying, Compiling, Ready, Running,
Stopping and Quarantined. Preparing/clearing/quarantined states remain busy;
quarantine cannot force-detach or automatically restart. RunningScript exposes a
fixed RouteB label, not the path/source. Error text is fixed; detailed typed
status exposes no payload or configuration values. Line0 means unavailable,
not measured current execution position. Compiler/runtime errors preserve their
actual available line; the legacy current-line display is not reused.

`FileSource` owns the actual File interface, opened only on the registered owner.
It uses production storage parseRef/exists/openRead APIs. Native platform storage
supplies bytes/errors; it does not implement capture or dispatch. Default volume
is the parser's SPIFFS choice; explicit SD uses its Ref. No resolveScript fallback
to another volume is permitted. The production resolver/parser/FS implementation
is target-object compiled but the native storage API implementation is mocked.

Open rejects missing/directory/oversize input, then verifies seek/position. The
existing8,192-byte Adapter source cap includes a separate terminator byte. The
Reader accepts partial positive reads with checked size/position; zero before
expected EOF is Error, not guessed backpressure. An optional owner scheduling
poll can return Retry before File::read; File itself has no portable Retry API.
Retry consumes the existing capture-turn budget. No readString/full-file heap
capture is introduced. All String path construction is outside publication.

At the end of capture, compilation is paused. A second32-byte-per-turn pass
compares the File byte-for-byte to Adapter's owned capture, checking size,
position, seek and EOF assumptions. Only then is File closed and compiler stepping
continued. Compiler already points to Adapter's owned MemoryReader, never the
closed File. Failed/stopped capture closes File and cancels compiler before the
reservation is released. File::close is called unconditionally: the pinned
implementation safely drops its internal pointer even for an unusable handle.

The application service lease excludes inventoried application writers during
capture. A matching second pass is a checked snapshot under that assumption,
not a lock against arbitrary external SD/raw writes. Concurrent same-size writes
to already-verified bytes can escape detection; media ownership and all bypass
writers must be resolved before production integration. Native File mutation,
growth and truncation are fault cases, not proof of external-media consistency.

S/T whitelist and numeric semantics remain unchanged: ASCII source, US locale,
HID enabled, no ownership IR, fixed named keys, Runtime-only Delay, source/line/
IR/expression/call/runtime budgets unchanged. Unsupported source fails before
even synchronization output. This does not replace the legacy large-file engine
or add language features, INJECT_MOD/RESET semantics or Unicode support.
