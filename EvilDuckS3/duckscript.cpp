#include "duckscript.h"
#include "com.h"
#include "debug.h"
#include "config.h"
#include "storage.h"
#include "script_log.h"
#include "duck_vars.h"
#include "led.h"
#include "settings.h"
#include "execution_guard.h"
#include "script_source.h"
#include "script_parser.h"
#include "duck_constants.h"
#include "conditional_state.h"

// One bounded execution context. It is replaced on every successful run;
// parser/control-flow semantics will be extended in subsequent stages.
struct RunState {
  File scriptFile;
  script_source::Reader source;
  script_parser::Validator validator;
  script_parser::Lexer lexer;
  duck_constants::Collector collector;
  bool collecting = true;
  bool preflight = true;
  storage::Ref scriptRef;
  bool active = false;
  uint32_t lineNumber = 0;
  String lastErr;
  bool skipBlock = false;
  conditional_state::Stack conditionals;
  uint32_t whileStartPos = 0;
  uint32_t whileStartLine = 0;
  String whileKey;
  bool inWhile = false;
};
static RunState state;

static void loadNextLine();
static void comDone();
static void comRepeat();
static void comError();

namespace {

void setStatusColor(int r, int g, int b) {
  if (!settings::getDisableLed()) led::setColor(r, g, b);
}

void setIdleColor() {
  if (settings::getDisableLed()) {
    led::setColor(0, 0, 0);
    return;
  }
  uint32_t color = settings::getLedColor();
  led::setColor((color >> 16) & 0xFF, (color >> 8) & 0xFF, color & 0xFF);
}

void fail(const String &message, uint32_t line) {
  state.lineNumber = line;
  state.lastErr = state.scriptRef.display + ": Error at line " + String(line) + ": " + message;
  script_log::setLine(line, state.scriptRef.display);
  script_log::error(state.lastErr);
  duckscript::stop();
  setStatusColor(50, 0, 0);
}

bool isControlLine(const script_parser::Statement &stmt) {
  using script_parser::Kind;
  if (stmt.kind == Kind::Empty || stmt.kind == Kind::Comment || stmt.kind == Kind::RemBlock || stmt.kind == Kind::Define) return true;
  if (stmt.kind == Kind::EndIf) {
    if (!state.conditionals.leave()) fail("Unmatched END_IF at runtime", state.lineNumber);
    return true;
  }
  if (stmt.kind == Kind::EndWhile) {
    if (state.inWhile && state.whileKey.length() && duck_vars::truthy(state.whileKey)) {
      if (!state.source.seek(state.whileStartPos, state.whileStartLine)) {
        fail(state.source.error(), state.lineNumber);
        return true;
      }
      state.lineNumber = state.whileStartLine;
      return true;
    }
    state.inWhile = false;
    state.whileKey = "";
    return true;
  }
  if (stmt.kind == Kind::Else || stmt.kind == Kind::ElseIf) {
    uint16_t condition = stmt.kind == Kind::Else ? 1 : 0;
    String diagnostic;
    if (stmt.kind == Kind::ElseIf && state.conditionals.eligible() &&
        !script_parser::condition(stmt.args, false, condition, diagnostic)) {
      fail(diagnostic, state.lineNumber); return true;
    }
    if (!state.conditionals.alternative(condition != 0, stmt.kind == Kind::Else))
      fail("Unmatched or misordered ELSE/ELSE IF at runtime", state.lineNumber);
    return true;
  }
  if (stmt.kind == Kind::If) {
    uint16_t condition = 0;
    String diagnostic;
    if (state.conditionals.active() && !state.skipBlock &&
        !script_parser::condition(stmt.args, stmt.legacyCondition, condition, diagnostic)) {
      fail(diagnostic, state.lineNumber); return true;
    }
    if (!state.conditionals.enter(condition != 0)) fail("Conditional nesting limit exceeded", state.lineNumber);
    return true;
  }
  if (!state.conditionals.active()) return true;
  if (stmt.kind == Kind::While) {
    state.whileKey = stmt.args;
    state.whileStartPos = state.source.position();
    state.whileStartLine = state.lineNumber;
    state.inWhile = true;
    state.skipBlock = !duck_vars::truthy(state.whileKey);
    return true;
  }
  return state.skipBlock;
}

}

namespace duckscript {

bool run(const String &filename) {
  execution::Guard guard;
  if (state.active || com::busy()) return false;
  state = RunState();

  if (!storage::resolveScript(filename, state.scriptRef)) {
    state.lastErr = "Cannot open script: " + filename;
    debug::error(state.lastErr);
    script_log::error(state.lastErr);
    setStatusColor(50, 0, 0);
    return false;
  }

  state.scriptFile = storage::openRead(state.scriptRef);
  if (!state.scriptFile) {
    state.lastErr = "Open failed: " + state.scriptRef.display;
    script_log::error(state.lastErr);
    setStatusColor(50, 0, 0);
    return false;
  }

  state.active = true;
  state.lineNumber = 0;
  state.skipBlock = false;
  state.inWhile = false;
  com::beginScript();
  script_log::clear();
  script_log::info("Preflight " + state.scriptRef.display);
  if (!state.source.begin(state.scriptFile)) {
    fail(state.source.error(), 1);
    return false;
  }
  setStatusColor(35, 0, 45);

  com::onDone(comDone);
  com::onRepeat(comRepeat);
  com::onError(comError);

  return true;
}

void stop() {
  execution::Guard guard;
  bool wasActive = state.active || com::busy();
  state.active = false;
  state.conditionals.clear();
  com::endScript();
  if (state.scriptFile) state.scriptFile.close();
  state.source = script_source::Reader();
  if (wasActive) script_log::info("Stopped");
  setIdleColor();
}

void update() {
  execution::Guard guard;
  if (state.active && !com::busy()) loadNextLine();
}

bool running() { execution::Guard guard; return state.active; }
String runningScript() { execution::Guard guard; return state.active ? state.scriptRef.display : String(); }
uint32_t currentLine() { execution::Guard guard; return state.lineNumber; }
String lastError() { execution::Guard guard; return state.lastErr; }

}

static void loadNextLine() {
  if (!state.active) return;
  uint16_t bytes = DUCKSCRIPT_READ_BUDGET;
  for (uint8_t lines = 0; lines < DUCKSCRIPT_LINE_BUDGET; ++lines) {
    String line;
    auto result = state.source.next(line, bytes);
    if (result == script_source::Result::Yield) return;
    if (result == script_source::Result::Error) { fail(state.source.error(), state.source.errorLine()); return; }
    if (result == script_source::Result::End) {
      if (state.collecting) {
        if (!state.source.seek(0, 0)) { fail(state.source.error(), 1); return; }
        state.collecting = false;
        state.lineNumber = 0;
      } else if (state.preflight) {
        String diagnostic;
        uint32_t errorLine = state.lineNumber;
        if (!state.validator.finish(diagnostic, errorLine)) { fail(diagnostic, errorLine); return; }
        if (!state.source.seek(0, 0)) { fail(state.source.error(), 1); return; }
        state.preflight = false;
        state.lineNumber = 0;
        script_log::setLine(0, state.scriptRef.display);
        script_log::info("Started " + state.scriptRef.display);
      } else {
        script_log::info("Finished");
        duckscript::stop();
      }
      return;
    }
    state.lineNumber = state.source.lineNumber();
    script_log::setLine(state.lineNumber, state.scriptRef.display);
    String diagnostic;
    if (state.collecting) {
      if (!state.collector.accept(line, state.lineNumber, diagnostic)) { fail(diagnostic, state.lineNumber); return; }
    } else if (state.preflight) {
      if (!state.validator.accept(line, state.lineNumber, diagnostic)) { fail(diagnostic + " [" + line + "]", state.lineNumber); return; }
    } else {
      script_parser::Statement stmt;
      if (!state.lexer.scan(line, state.lineNumber, stmt, diagnostic)) { fail(diagnostic, state.lineNumber); return; }
      if (isControlLine(stmt)) { if (!state.active) return; continue; }
      com::send(stmt.line);
      return;
    }
  }
}

static void comDone() {} // The main loop advances the next line, never callbacks.

static void comRepeat() {}

static void comError() {
  fail(com::lastError(), state.lineNumber);
}
