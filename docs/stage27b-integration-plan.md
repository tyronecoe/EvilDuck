# Stage27B source boundary and future integration plan

NOT FLASH-AUTHORIZED. Stage27A uses only frozen Stage26 artifacts/hashes and separate owner
approval. Stage27B creates no firmware BIN, table, OTA initializer or installation manifest.
Original firmware remains OWNER CONFIRMED — AVAILABLE EXTERNALLY; no stock search/request.

## Actual source call sites and dependencies

- EvilDuckS3/EvilDuckS3.ino setup initializes settings/storage/network/HID with the existing
  controlled-start safeguards. Its loop invokes duckscript::update, com::update and subsystem
  updates. Stage26 skips autorun and example installation. None of these paths changes here.
- webserver.cpp handleRunScript resolves a storage::Ref and calls duckscript::run at line209.
  Live web commands call com::executeNow at171. cli.cpp calls duckscript::run at195 and
  com::executeNow at206. Library-run paths may explicitly copy examples; that behavior is
  not silently reused or enabled by this preview.
- duckscript.cpp run owns File/script_source::Reader, performs incremental preflight, collects
  DEFINE/preprocessing/functions, then drives legacy expressions/control flow through callbacks
  from com. Its static RunState contains source/parser/global/function/control state. It uses
  execution_guard admission and storage SPIFFS/SD references. Compile and execution are coupled
  through the cooperative state machine rather than this preview's bounded immutable IR.
- com.cpp parses legacy runtime/key/text commands and schedules delay/text/transient/persistent
  keyboard ownership. hid_backend.cpp implements transport reports, retries, ownership, lock
  feedback and disconnect clearing. keyboard_locale.cpp plus locale tables translate characters.
- script_source.cpp remains valuable as a bounded read/seek/error-aware storage service.
  storage.cpp/spiffs.cpp/sd_card.cpp remain adapters; attackmode/usb_msc remain storage/USB
  infrastructure, not language semantics to copy into the new core.

## Candidate retirement boundary — future, not performed

After conformance and adapter review, retire/replace the language portions of duckscript.cpp,
script_parser.cpp, script_preprocessor.cpp, duck_expr.cpp, duck_vars.cpp, duck_constants.cpp,
script_functions.cpp and control_flow.h. Refactor com's language dispatch away from transport
scheduling; do not preserve its bare unknown-key fallback or old aliases by accident. The
existing useful scheduler/backpressure/release code should be adapted rather than blindly
replaced. New syntax is independently derived from the official reference, not legacy tests.
This is not authorization to delete any of those production files in Stage27B.

## Narrow eventual adapter

An explicitly owner-armed, separately selected preview session would acquire execution_guard
ownership before accepting events. Character events go through a reviewed locale-aware transient
text scheduler; KeyTap events go through nonblocking press AND release; Delay events have a
single designated timing owner so the adapter and interpreter do not double-wait. Adapter Retry
must mean **no event accepted**, while Accepted must not prematurely acknowledge a partially
sent press/release pair. Cancellation/error/disconnect must cancel scheduled work and request
release before subsequent sessions. Existing persistent ownership must be isolated or explicitly
merged under a reviewed contract; this preview does not currently support HOLD/RELEASE.

No raw script line ever goes to com::executeNow. Unknown hardware commands remain diagnostics.
No autorun, button, saved payload or remote request can silently arm the preview. Start must be
explicit and authenticated; admission is denied in safe/readonly profiles. No implicit transition
from quiescent/readonly to writable normal operation exists. Existing Stage26 controlled profile
and all its binaries/manifests remain frozen and are the only Stage27A reviewed installation set.

Before any real integration: implement bounded expression-function continuations, choose the
streaming/bounded-source contract for scripts exceeding8192 bytes, review exact language edge
semantics and reference ambiguities, budget approximately7KiB per preview context plus compiler
stack/callees, add adapter report/release/backpressure/disconnect tests, then select an unambiguous
new build profile for review. Do not drop this synchronous small-script compiler onto a web
callback without cooperative admission/compilation design. No real adapter is added now.
