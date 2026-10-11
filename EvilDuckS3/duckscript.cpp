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
#include "script_preprocessor.h"
#include "control_flow.h"
#include "script_functions.h"
#include <new>
#include <cstring>

// One bounded execution context. It is replaced on every successful run;
// parser/control-flow semantics will be extended in subsequent stages.
struct RunState {
  File scriptFile;
  script_source::Reader source;
  script_parser::Validator validator;
  script_parser::Lexer lexer;
  script_preprocessor::Filter preprocessing;
  bool collecting = true;
  bool inventory = true, inventoryFunction = false;
  script_parser::Lexer inventoryLexer;
  script_functions::Table functions;
  duck_vars::Symbols globals;
  script_functions::Calls calls;
  script_functions::Evaluation evaluation;
  uint32_t functionCalls = 0, currentOffset = 0;
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
  if (!settings::getDisableLed() && !com::statusLedOverridden()) led::setColor(r, g, b);
}

void setIdleColor() {
  if (com::statusLedOverridden()) return;
  if (settings::getDisableLed()) {
    led::setColor(0, 0, 0);
    return;
  }
  uint32_t color = settings::getLedColor();
  led::setColor((color >> 16) & 0xFF, (color >> 8) & 0xFF, color & 0xFF);
}

void fail(const String &message, uint32_t line) {
  state.lineNumber = line;
  const auto *call=state.calls.top();
  String trace;
  if(call) {
    const auto *function=state.functions.get(call->function);
    if(function)trace=" [in "+String(function->name)+"(), called at line "+String(call->nextLine)+"]";
  }
  state.lastErr = state.scriptRef.display + ": Error at line " + String(line) + ": " + message + trace;
  script_log::setLine(line, state.scriptRef.display);
  script_log::error(state.lastErr);
  duckscript::stop();
  if (!settings::getDisableLed()) led::setColor(50, 0, 0);
}

bool isControlLine(const script_parser::Statement &);

bool beginEvaluation(const String &expression, script_functions::Consumer consumer,
                     const char *target = nullptr, bool declaration = false, uint8_t command = 0) {
  auto &evaluation=state.evaluation;
  evaluation=script_functions::Evaluation();
  duck_expr::Error error;
  if(!evaluation.program.compile(expression.c_str(),expression.length(),error,duck_vars::Symbols::resolve,&state.globals)) {
    fail("Expression column "+String(error.column)+": "+error.message,state.lineNumber);return false;
  }
  evaluation.consumer=consumer;evaluation.offset=state.currentOffset;evaluation.line=state.lineNumber;
  evaluation.variables=duck_vars::revision();evaluation.actions=state.actions;
  evaluation.declaration=declaration;evaluation.command=command;evaluation.reenter=state.reenterWhile;
  if(target)memcpy(evaluation.target,target,strlen(target)+1);
  return true;
}
bool enterFunction(uint16_t index,bool valueRequired) {
  const auto *function=state.functions.get(index);
  if(!function) {fail("Undefined function",state.lineNumber);return false;}
  if(state.functionCalls>=DUCKSCRIPT_MAX_FUNCTION_CALLS) {fail("Function invocation budget exceeded",state.lineNumber);return false;}
  script_functions::Call frame;
  frame.caller=state.evaluation;frame.nextOffset=state.source.position();frame.nextLine=state.lineNumber;
  frame.base=state.flow.size();frame.callerBase=state.flow.base();frame.function=index;frame.valueRequired=valueRequired;
  if(!state.calls.push(frame)) {fail("Function call depth/stack limit exceeded",state.lineNumber);return false;}
  ++state.functionCalls;state.flow.isolate(frame.base);
  state.evaluation.consumer=script_functions::Consumer::None;state.reenterWhile=false;
  if(!state.source.seek(function->body,function->headerLine)) {fail(state.source.error(),state.lineNumber);return false;}
  state.lineNumber=function->headerLine;return true;
}
void returnFunction(bool hasValue,uint16_t value) {
  const auto *top=state.calls.top();
  if(!top) {fail("RETURN/END_FUNCTION without active call",state.lineNumber);return;}
  if(top->valueRequired && !hasValue) {fail("Function returned without a value in an expression",state.lineNumber);return;}
  script_functions::Call frame;
  state.calls.pop(frame);
  if(!state.flow.restore(frame.base) || !state.flow.isolate(frame.callerBase)) {fail("Function corrupted caller control-flow boundaries",state.lineNumber);return;}
  if(!state.source.seek(frame.nextOffset,frame.nextLine)) {fail(state.source.error(),state.lineNumber);return;}
  state.evaluation=frame.caller;state.currentOffset=frame.caller.offset;state.lineNumber=frame.nextLine;
  state.reenterWhile=frame.caller.reenter;
  if(frame.valueRequired && !state.evaluation.program.returned(value)) fail("Invalid suspended expression return",state.lineNumber);
}
void advanceEvaluation() {
  uint16_t value=0;duck_expr::Error error;
  auto status=state.evaluation.program.step(value,error,duck_vars::resolve,nullptr);
  if(status==duck_expr::Step::Yield)return;
  if(status==duck_expr::Step::Call) {enterFunction(value,true);return;}
  if(status==duck_expr::Step::Error) {fail("Expression column "+String(error.column)+": "+error.message,state.evaluation.line);return;}
  auto consumer=state.evaluation.consumer;
  state.lineNumber=state.evaluation.line;state.currentOffset=state.evaluation.offset;
  state.reenterWhile=state.evaluation.reenter;state.evaluation.consumer=script_functions::Consumer::None;
  if(consumer==script_functions::Consumer::Return) {returnFunction(true,value);return;}
  if(consumer==script_functions::Consumer::Assignment) {
    com::send(String(state.evaluation.declaration?"VAR ":"")+state.evaluation.target+" = "+String(value));return;
  }
  if(consumer==script_functions::Consumer::Numeric) {
    static const char *commands[]={"DELAY","WAIT","DEFAULT_DELAY","DEFAULTDELAY","REPEAT","REPLAY"};
    ++state.actions;com::send(String(commands[state.evaluation.command])+" "+String(value));return;
  }
  script_parser::Statement statement;statement.args=String(value);
  statement.kind=consumer==script_functions::Consumer::If?script_parser::Kind::If:
    consumer==script_functions::Consumer::ElseIf?script_parser::Kind::ElseIf:script_parser::Kind::While;
  isControlLine(statement);
  if(state.active && consumer==script_functions::Consumer::While)
    state.flow.conditionProgress(state.evaluation.variables,state.evaluation.actions);
}
bool inventoryLine(const String &line,String &error) {
  script_parser::Statement stmt;
  if(!state.inventoryLexer.scan(line,state.lineNumber,stmt,error))return false;
  if(stmt.kind==script_parser::Kind::Function) {
    if(state.inventoryFunction) {error="Nested FUNCTION declarations are unsupported";return false;}
    if(!state.functions.add(stmt.args,state.source.position(),state.lineNumber,error))return false;
    state.inventoryFunction=true;
  } else if(stmt.kind==script_parser::Kind::EndFunction) {
    if(!state.inventoryFunction) {error="Unmatched END_FUNCTION";return false;}
    state.functions.close(state.source.position(),state.lineNumber);state.inventoryFunction=false;
  }
  if(stmt.kind==script_parser::Kind::Command && (script_parser::hasKeyword(stmt.line,"VAR") || script_parser::hasKeyword(stmt.line,"DEFINE"))) {
    String name,value;bool text;
    if(!script_parser::assignment(stmt.args,name,value,text,error))return false;
    if(state.globals.declare(name,text?duck_vars::Type::Text:duck_vars::Type::Numeric,false,error)<0)return false;
  } else if(stmt.kind==script_parser::Kind::Command && script_parser::hasKeyword(stmt.line,"READ")) {
    String args=stmt.args;args.replace("\t"," ");String name=args.substring(args.lastIndexOf(' ')+1);name.trim();
    if(state.globals.declare(name,duck_vars::Type::Text,false,error)<0)return false;
  }
  return true;
}

bool isControlLine(const script_parser::Statement &stmt) {
  if(stmt.kind==script_parser::Kind::Function) {
    int index=state.functions.find(stmt.args.c_str(),stmt.args.length());const auto *function=index<0?nullptr:state.functions.get(index);
    if(!function || !function->end)fail("Invalid function declaration metadata",state.lineNumber);
    else if(!state.source.seek(function->end,function->endLine))fail(state.source.error(),state.lineNumber);
    else state.lineNumber=function->endLine;
    return true;
  }
  if(stmt.kind==script_parser::Kind::EndFunction) {returnFunction(false,0);return true;}
  if(stmt.kind==script_parser::Kind::Call) {
    if(state.flow.active()) {
      state.evaluation.consumer=script_functions::Consumer::None;
      state.evaluation.line=state.lineNumber;state.evaluation.offset=state.currentOffset;state.evaluation.reenter=state.reenterWhile;
      int index=state.functions.find(stmt.args.c_str(),stmt.args.length());
      if(index<0)fail("Undefined function",state.lineNumber);else enterFunction(index,false);
    }
    return true;
  }
  if(stmt.kind==script_parser::Kind::Return) {
    if(!state.flow.active())return true;
    if(!state.calls.size())return false; // Bare RETURN stays the top-level Enter alias.
    if(stmt.args.length())beginEvaluation(stmt.args,script_functions::Consumer::Return);
    else returnFunction(false,0);
    return true;
  }
  bool functionCondition=duck_expr::containsCalls(stmt.args.c_str(),stmt.args.length());
  if(functionCondition && (stmt.kind==script_parser::Kind::If || stmt.kind==script_parser::Kind::ElseIf || stmt.kind==script_parser::Kind::While)) {
    bool eligible=stmt.kind==script_parser::Kind::ElseIf?state.flow.eligible():state.flow.active();
    if(eligible) {
      beginEvaluation(stmt.args,stmt.kind==script_parser::Kind::If?script_functions::Consumer::If:
        stmt.kind==script_parser::Kind::ElseIf?script_functions::Consumer::ElseIf:script_functions::Consumer::While);
      return true;
    }
  }
  // Qualified parser kinds below keep runtime and lexical frame types separate.
  if (stmt.kind == script_parser::Kind::Extension || stmt.kind == script_parser::Kind::EndExtension ||
      stmt.kind == script_parser::Kind::Version || stmt.kind == script_parser::Kind::Empty || stmt.kind == script_parser::Kind::Comment ||
      stmt.kind == script_parser::Kind::RemBlock || stmt.kind == script_parser::Kind::Define ||
      stmt.kind == script_parser::Kind::StringBlock || stmt.kind == script_parser::Kind::StringLnBlock) return true;
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
      state.flow.enterWhile(condition != 0, state.currentOffset, state.lineNumber, duck_vars::revision(), state.actions);
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
  // Construct directly in place: the bounded call storage is deliberately too
  // large for an aggregate temporary on the ESP32 main-loop task stack.
  state.~RunState();new (&state) RunState();

  if (!storage::resolveScript(filename, state.scriptRef)) {
    state.lastErr = "Cannot open script: " + filename;
    debug::error(state.lastErr);
    script_log::error(state.lastErr);
    if (!settings::getDisableLed()) led::setColor(50, 0, 0);
    return false;
  }

  state.scriptFile = storage::openRead(state.scriptRef);
  if (!state.scriptFile) {
    state.lastErr = "Open failed: " + state.scriptRef.display;
    script_log::error(state.lastErr);
    if (!settings::getDisableLed()) led::setColor(50, 0, 0);
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
  state.calls.clear();state.evaluation.consumer=script_functions::Consumer::None;
  state.functionCalls=0;duck_expr::functions(nullptr);
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
  if(state.active && !com::busy()) {
    if(state.evaluation.consumer!=script_functions::Consumer::None)advanceEvaluation();
    else loadNextLine();
  }
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
        String diagnostic; uint32_t number = state.lineNumber;
        if (!state.preprocessing.finish(diagnostic, number)) { fail(diagnostic, number); return; }
        if (!state.source.seek(0, 0)) { fail(state.source.error(), 1); return; }
        state.collecting = false;
        state.lineNumber = 0;
      } else if(state.inventory) {
        String diagnostic;uint32_t number=state.lineNumber;
        if(!state.inventoryLexer.finish(diagnostic,number)) {fail(diagnostic,number);return;}
        if(!state.source.seek(0,0)) {fail(state.source.error(),1);return;}
        state.inventory=false;state.lineNumber=0;
        state.validator.functionSymbols(&state.globals);
        duck_expr::functions(script_functions::Table::resolve,&state.functions);
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
        if(state.calls.size() || state.flow.size()) {fail("Unexpected EOF inside active function/control flow",state.lineNumber);return;}
        script_log::info("Finished");
        duckscript::stop();
      }
      return;
    }
    state.lineNumber = state.source.lineNumber();
    state.currentOffset=state.source.lineStartPosition();
    script_log::setLine(state.lineNumber, state.scriptRef.display);
    String diagnostic;
    if (state.collecting) {
      if (!state.preprocessing.accept(line, state.lineNumber, diagnostic)) { fail(diagnostic, state.lineNumber); return; }
    } else if (!state.preprocessing.contains(state.lineNumber)) {
      continue; // Frozen compile-time exclusion, independent of reader seeks.
    } else if(state.inventory) {
      if(!inventoryLine(line,diagnostic)) {fail(diagnostic+" ["+line+"]",state.lineNumber);return;}
    } else if (state.preflight) {
      if (!state.validator.accept(line, state.lineNumber, diagnostic)) { fail(diagnostic + " [" + line + "]", state.lineNumber); return; }
    } else {
      script_parser::Statement stmt;
      if (!state.lexer.scan(line, state.lineNumber, stmt, diagnostic)) { fail(diagnostic, state.lineNumber); return; }
      if (state.reenterWhile && (stmt.kind != script_parser::Kind::While || !state.flow.top() ||
          state.source.lineStartPosition() != state.flow.top()->offset || state.lineNumber != state.flow.top()->line)) {
        fail("WHILE header changed during execution", state.lineNumber); return;
      }
      if (isControlLine(stmt)) {
        if (!state.active || state.evaluation.consumer!=script_functions::Consumer::None ||
            stmt.kind==script_parser::Kind::Call || stmt.kind==script_parser::Kind::Return ||
            stmt.kind==script_parser::Kind::EndFunction || stmt.kind==script_parser::Kind::Function) return;
        continue;
      }
      // Only numeric consumers evaluate calls; text/file payloads stay literal.
      if (stmt.kind == script_parser::Kind::TextBody || stmt.kind == script_parser::Kind::TextLnBody) {
        bool enter = stmt.kind == script_parser::Kind::TextLnBody;
        if (!stmt.args.length() && !enter) continue;
        ++state.actions;
        com::sendText(stmt.args, enter);
        return;
      }
      if(stmt.kind==script_parser::Kind::Assignment || script_parser::hasKeyword(stmt.line,"VAR") ||
         script_parser::hasKeyword(stmt.line,"DEFINE")) {
        String name,value;bool text;
        if(!script_parser::assignment(stmt.args,name,value,text,diagnostic)) {fail(diagnostic,state.lineNumber);return;}
        if(!text && duck_expr::containsCalls(value.c_str(),value.length())) {
          beginEvaluation(value,script_functions::Consumer::Assignment,name.c_str(),stmt.kind!=script_parser::Kind::Assignment);return;
        }
      }
      static const char *numericCommands[]={"DELAY","WAIT","DEFAULT_DELAY","DEFAULTDELAY","REPEAT","REPLAY"};
      for(uint8_t i=0;i<6;++i)if(script_parser::hasKeyword(stmt.line,numericCommands[i]) &&
          duck_expr::containsCalls(stmt.args.c_str(),stmt.args.length())) {
        beginEvaluation(stmt.args,script_functions::Consumer::Numeric,nullptr,false,i);return;
      }
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
