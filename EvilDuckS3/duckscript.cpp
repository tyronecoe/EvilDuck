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
#include "control_flow.h"

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
  control_flow::Stack flow;
  bool reenterWhile = false;
  uint32_t loopIterations = 0, actions = 0;
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
  // Qualified parser kinds below keep runtime and lexical frame types separate.
  if (stmt.kind == script_parser::Kind::Empty || stmt.kind == script_parser::Kind::Comment ||
      stmt.kind == script_parser::Kind::RemBlock || stmt.kind == script_parser::Kind::Define) return true;
  if (stmt.kind == script_parser::Kind::EndIf) {
    if (!state.flow.leave(control_flow::Kind::If)) fail("Unmatched or mismatched END_IF at runtime", state.lineNumber);
    return true;
  }
  if (stmt.kind == script_parser::Kind::EndWhile) {
    const auto *frame = state.flow.top();
    if (!frame || frame->kind != control_flow::Kind::While) {
      fail("Unmatched or mismatched END_WHILE at runtime", state.lineNumber); return true;
    }
    if (!frame->active) { state.flow.leave(control_flow::Kind::While); return true; }
    uint32_t offset = frame->offset, openingLine = frame->line;
    if (!state.flow.completedIteration(duck_vars::revision(), state.actions)) {
      fail("WHILE stalled: consecutive iterations without variable changes or executed actions", openingLine); return true;
    }
    // Reread and reevaluate the WHILE header; Reader resets read-ahead and lexical
    // line location. No expression strings/AST or recursive execution are retained.
    if (!state.source.seek(offset, openingLine - 1)) { fail(state.source.error(), state.lineNumber); return true; }
    state.lineNumber = openingLine - 1;
    state.reenterWhile = true;
    return true;
  }
  if (stmt.kind == script_parser::Kind::Else || stmt.kind == script_parser::Kind::ElseIf) {
    uint16_t condition = stmt.kind == script_parser::Kind::Else ? 1 : 0;
    String diagnostic;
    if (stmt.kind == script_parser::Kind::ElseIf && state.flow.eligible() &&
        !script_parser::condition(stmt.args, false, condition, diagnostic)) {
      fail(diagnostic, state.lineNumber); return true;
    }
    if (!state.flow.alternative(condition != 0, stmt.kind == script_parser::Kind::Else))
      fail("Unmatched or misordered ELSE/ELSE IF at runtime", state.lineNumber);
    return true;
  }
  if (stmt.kind == script_parser::Kind::If) {
    uint16_t condition = 0;
    String diagnostic;
    if (state.flow.active() &&
        !script_parser::condition(stmt.args, stmt.legacyCondition, condition, diagnostic)) {
      fail(diagnostic, state.lineNumber); return true;
    }
    if (!state.flow.enterIf(condition != 0)) fail("Control-flow nesting limit exceeded", state.lineNumber);
    return true;
  }
  if (stmt.kind == script_parser::Kind::While) {
    const auto *frame = state.flow.top();
    bool parent = state.reenterWhile ? frame && frame->parent : state.flow.active();
    uint16_t condition = 0;
    String diagnostic;
    if (parent && !script_parser::condition(stmt.args, stmt.legacyCondition, condition, diagnostic)) {
      fail(diagnostic, state.lineNumber); return true;
    }
    if (parent && condition && state.loopIterations >= DUCKSCRIPT_MAX_LOOP_ITERATIONS) {
      fail("WHILE total iteration limit exceeded", state.lineNumber); return true;
    }
    bool entered = state.reenterWhile ? state.flow.reevaluateWhile(condition != 0, duck_vars::revision(), state.actions) :
      state.flow.enterWhile(condition != 0, state.source.lineStartPosition(), state.lineNumber, duck_vars::revision(), state.actions);
    state.reenterWhile = false;
    if (!entered) fail("Control-flow nesting limit exceeded", state.lineNumber);
    else if (parent && condition) ++state.loopIterations;
    return true;
  }
  return !state.flow.active();
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
  state.flow.clear();
  state.reenterWhile = false;
  state.loopIterations = state.actions = 0;
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
      if (state.reenterWhile && (stmt.kind != script_parser::Kind::While || !state.flow.top() ||
          state.source.lineStartPosition() != state.flow.top()->offset || state.lineNumber != state.flow.top()->line)) {
        fail("WHILE header changed during execution", state.lineNumber); return;
      }
      if (isControlLine(stmt)) { if (!state.active) return; continue; }
      // Variable updates count only when their value actually changes. Other
      // accepted runtime commands are observable actions, including timers and
      // storage/LED/HID commands; their cooperative completion gates the next line.
      if (stmt.kind != script_parser::Kind::Assignment && !script_parser::hasKeyword(stmt.line, "VAR") &&
          !script_parser::hasKeyword(stmt.line, "DEFINE")) ++state.actions;
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
