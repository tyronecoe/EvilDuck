#include "com.h"
#include "hid_backend.h"
#include "keyboard_locale.h"
#include "duck_keys.h"
#include "led.h"
#include "storage.h"
#include "duck_vars.h"
#include "duckscript.h"
#include "attackmode.h"
#include "script_log.h"
#include "settings.h"
#include "execution_guard.h"
#include "script_parser.h"
#include "duck_constants.h"
#include "internal_vars.h"
#include <cstdlib>

namespace {
enum class Phase { Idle, Start, Wait, Storage, Ownership, Reset, LockWait, LockRestore, LockAck, Text, Keys, Press, Release, Finish };
struct Session {
  bool scriptOwned = false;
  int8_t lockCommand = -1;
  uint8_t lockTarget = 0, lockBit = 0, lockToggles = 0;
  bool lockBaselineKnown = false;
  uint32_t lockSession = 0, lockChanges = 0;
  uint16_t lockDeadline = 0;
  uint32_t lockStarted = 0;
  bool holding = false;
  uint8_t ownedModifier = 0, ownedKey = 0;
  bool ownsKeys = false;
  bool remember = false;
  bool repeating = false;
  bool enter = false;
  bool preprocessed = false;
  bool textLine = false, textEnter = false;
  bool historyText = false, historyEnter = false;
  bool warnedUnsupported = false;
  uint8_t textModifiers = 0;
  Phase phase = Phase::Idle;
  Phase afterWait = Phase::Finish;
  Phase afterRelease = Phase::Finish;
  Phase afterText = Phase::Finish;
  uint32_t defaultDelay = 0;
  uint32_t waitStarted = 0;
  uint32_t waitRemaining = 0;
  uint32_t repeatsRemaining = 0;
  String line, history, text, error;
  size_t offset = 0;
  keyboard_locale::Stroke strokes[2] = {};
  uint8_t strokeCount = 0, strokeIndex = 0;
  uint8_t reportModifiers = 0, reportKeys[6] = {}, reportCount = 0;
  duck_keys::Cursor cursor;
};
Session session;
String rejected;
com::cb_t cbDone = nullptr, cbRepeat = nullptr, cbError = nullptr;

String trimLine(const String &s) {
  int start = 0;
  while (start < (int)s.length() && (s[start] == ' ' || s[start] == '\t' || s[start] == '\r' || s[start] == '\n')) start++;
  int end = s.length() - 1;
  while (end >= start && (s[end] == ' ' || s[end] == '\t' || s[end] == '\r' || s[end] == '\n')) end--;
  if (end < start) return "";
  return s.substring(start, end + 1);
}

bool startsWithNoCase(const String &s, const char *keyword) {
  return script_parser::hasKeyword(s, keyword);
}

bool equalsNoCase(const String &aIn, const char *bIn) {
  String a = aIn; String b = String(bIn);
  a.toLowerCase(); b.toLowerCase();
  return a == b;
}

uint8_t parseNumberToken(const String &token) {
  String t = trimLine(token);
  t.toLowerCase();
  if (t.startsWith("0x")) return static_cast<uint8_t>(strtoul(t.c_str(), nullptr, 16));
  return static_cast<uint8_t>(t.toInt());
}

bool parseFilePayload(const String &line, const char *cmd, String &fileRef, String &payload) {
  if (!script_parser::filePayload(line.substring(strlen(cmd)), fileRef, payload)) return false;
  String expanded;
  if (!duck_vars::expand(payload, expanded, session.error)) return false;
  payload = expanded;
  if (payload.startsWith("\"") && payload.endsWith("\"") && payload.length() >= 2) {
    payload = payload.substring(1, payload.length() - 1);
  }
  return fileRef.length() > 0;
}

bool fileIoWrite(const String &fileRef, const String &payload, bool append) {
  storage::Ref ref;
  if (!storage::parseRef(fileRef, ref)) return false;
  bool ok = append ? storage::appendFile(ref, payload) : storage::writeFile(ref, payload);
  if (ok) script_log::info(String(append ? "APPEND " : "SAVE ") + ref.display);
  return ok;
}

void waitFor(uint32_t ms, Phase next) {
  session.waitStarted = millis();
  session.waitRemaining = ms;
  session.afterWait = next;
  session.phase = ms ? Phase::Wait : next;
}

void releaseOwnedKeys() {
  if (session.ownsKeys || hid_backend::hasPersistent()) hid_backend::cancelReport();
  session.ownsKeys = false;
}

void report(uint8_t modifiers, const uint8_t *keys, uint8_t count, Phase next) {
  session.reportModifiers = modifiers;
  session.reportCount = count > 6 ? 6 : count;
  memset(session.reportKeys, 0, sizeof(session.reportKeys));
  if (session.reportCount) memcpy(session.reportKeys, keys, session.reportCount);
  session.afterRelease = next;
  session.phase = Phase::Press;
}

void startText(const String &text, bool enter, Phase next, uint8_t modifiers = 0) {
  session.textModifiers = modifiers;
  session.warnedUnsupported = false;
  session.text = text;
  session.offset = 0;
  session.strokeCount = session.strokeIndex = 0;
  session.enter = enter;
  session.afterText = next;
  session.phase = Phase::Text;
}

// Non-output commands keep their existing syntax and storage/LED behavior.
// Timers and keyboard operations only schedule work here; update() advances it.
bool startLine() {
  if (session.textLine) {
    session.remember = false;
    session.phase = Phase::Finish;
    if (!attackmode::hidEnabled()) return true;
    String expanded;
    if (!duck_vars::expand(session.line, expanded, session.error)) return false;
    session.remember = true;
    startText(expanded, session.textEnter, Phase::Finish);
    return true;
  }
  if (!session.preprocessed) {
    script_parser::Lexer lexer;
    script_parser::Statement prepared;
    if (!lexer.scan(session.line, 0, prepared, session.error)) return false;
    session.line = prepared.line;
    session.preprocessed = true;
  }
  script_parser::Statement stmt;
  if (!script_parser::parse(session.line, stmt, session.error)) return false;
  if (stmt.kind == script_parser::Kind::Return && !stmt.args.length()) {
    stmt.kind = script_parser::Kind::Keys; stmt.line = "ENTER";
  }
  if (stmt.kind != script_parser::Kind::Command && stmt.kind != script_parser::Kind::Keys &&
      stmt.kind != script_parser::Kind::Comment && stmt.kind != script_parser::Kind::Empty &&
      stmt.kind != script_parser::Kind::Assignment && stmt.kind != script_parser::Kind::Define) {
    session.error = "Block/control syntax requires a script";
    return false;
  }
  session.line = stmt.line;
  const String &line = session.line;
  session.remember = false;
  session.phase = Phase::Finish;
  if (!line.length() || startsWithNoCase(line, "REM") || line.startsWith("//")) return true;
  if (stmt.kind == script_parser::Kind::Define) return duck_constants::define(line, 0, session.error);
  if (equalsNoCase(line, "STOP") || equalsNoCase(line, "STOP_PAYLOAD")) {
    duckscript::stop();
    return true;
  }
  session.lockCommand = internal_vars::lockCommand(line);
  if (session.lockCommand >= 0) {
    const auto state = hid_backend::lockState();
    if (session.lockCommand == 9) {
      if (!hid_backend::saveLockState()) { session.error = "Cannot save unknown host lock state"; return false; }
      return true;
    }
    session.lockSession = state.session;
    session.lockStarted = millis(); session.lockDeadline = internal_vars::lockTimeout();
    if (session.lockCommand == 10) {
      if (!state.known || !state.savedKnown) { session.error = "Cannot restore unknown current/saved host lock state"; return false; }
      if (!attackmode::hidEnabled()) { session.error = "Lock restore requires HID enabled"; return false; }
      if (hid_backend::hasPersistent()) { session.error = "Release persistent keys/modifiers before lock restore"; return false; }
      session.lockTarget = state.saved; session.lockToggles = 0; session.phase = Phase::LockRestore;
    } else {
      session.lockBit = session.lockCommand / 3;
      session.lockBaselineKnown = state.known;
      session.lockChanges = state.changes[session.lockBit];
      session.phase = Phase::LockWait;
    }
    return true;
  }
  if (equalsNoCase(line, "RESET")) {
    hid_backend::cancelReport();
    session.ownsKeys = false;
    session.phase = Phase::Reset;
    return true;
  }
  if (startsWithNoCase(line, "HOLD") || startsWithNoCase(line, "RELEASE")) {
    session.ownedModifier = session.ownedKey = 0;
    if (!duck_keys::isModifierName(stmt.args, session.ownedModifier))
      hid_backend::keyNameToHid(stmt.args, session.ownedKey);
    session.holding = startsWithNoCase(line, "HOLD");
    // Release remains allowed when injection is gated, so held states can clear.
    if (session.holding && !attackmode::hidEnabled()) return true;
    session.remember = true;
    session.phase = Phase::Ownership;
    return true;
  }
  if (startsWithNoCase(line, "INJECT_MOD")) {
    if (!stmt.args.length() || !attackmode::hidEnabled()) return true;
    uint8_t modifier = 0;
    duck_keys::isModifierName(stmt.args, modifier);
    session.remember = true;
    report(modifier, nullptr, 0, Phase::Finish);
    return true;
  }
  if (startsWithNoCase(line, "DELAY ") || startsWithNoCase(line, "WAIT ")) {
    uint32_t value;
    if (!script_parser::numericArgument(stmt.args, value, session.error)) return false;
    waitFor(value, Phase::Finish);
    return true;
  }
  if (startsWithNoCase(line, "DEFAULT_DELAY ") || startsWithNoCase(line, "DEFAULTDELAY ")) {
    if (!script_parser::numericArgument(stmt.args, session.defaultDelay, session.error)) return false;
    return true;
  }
  if (startsWithNoCase(line, "REPEAT ") || startsWithNoCase(line, "REPLAY ")) {
    if (!session.history.length() && !session.historyText) return false;
    if (!script_parser::numericArgument(stmt.args, session.repeatsRemaining, session.error)) return false;
    if (session.repeatsRemaining) {
      session.repeating = true;
      session.line = session.history;
      session.textLine = session.historyText;
      session.textEnter = session.historyEnter;
      session.phase = Phase::Start;
    }
    return true;
  }
  if (startsWithNoCase(line, "LOCALE ")) {
    return keyboard_locale::setLocaleByName(trimLine(line.substring(7)));
  }
  if (startsWithNoCase(line, "LED ")) {
    if (settings::getDisableLed()) return true;
    String rest = trimLine(line.substring(4));
    if (equalsNoCase(rest, "OFF")) {
      led::setColor(0, 0, 0);
      return true;
    }
    int sp1 = rest.indexOf(' ');
    int sp2 = rest.indexOf(' ', sp1 + 1);
    int r = sp1 > 0 ? rest.substring(0, sp1).toInt() : 0;
    int g = (sp1 > 0 && sp2 > sp1) ? rest.substring(sp1 + 1, sp2).toInt() : 0;
    int b = (sp2 > sp1) ? rest.substring(sp2 + 1).toInt() : 0;
    led::setColor(r, g, b);
    return true;
  }
  if (stmt.kind == script_parser::Kind::Assignment || startsWithNoCase(line, "VAR ") || startsWithNoCase(line, "DEFINE ")) {
    String name, value; bool text;
    if (!script_parser::assignment(stmt.args, name, value, text, session.error)) return false;
    bool declaration = stmt.kind != script_parser::Kind::Assignment;
    if (text) {
      String expanded;
      if (!duck_vars::expand(value.substring(1, value.length() - 1), expanded, session.error)) return false;
      return duck_vars::setText(name, expanded, declaration, session.error);
    }
    return duck_vars::assign(name, value, declaration, session.error);
  }
  if (startsWithNoCase(line, "READ ")) {
    String rest = trimLine(line.substring(5));
    int sp = rest.lastIndexOf(' ');
    if (sp < 0) return false;
    String fileRef = trimLine(rest.substring(0, sp));
    String varName = trimLine(rest.substring(sp + 1));
    storage::Ref ref;
    if (!storage::parseRef(fileRef, ref)) return false;
    String data = storage::readFile(ref);
    return duck_vars::setText(varName, data, true, session.error);
  }
  if (startsWithNoCase(line, "SAVE ")) {
    String fileRef, payload;
    if (!parseFilePayload(line, "SAVE", fileRef, payload)) return false;
    return fileIoWrite(fileRef, payload, false);
  }
  if (startsWithNoCase(line, "APPEND ")) {
    String fileRef, payload;
    if (!parseFilePayload(line, "APPEND", fileRef, payload)) return false;
    return fileIoWrite(fileRef, payload, true);
  }
  if (startsWithNoCase(line, "ATTACKMODE ")) {
    if (!attackmode::applyFromString(trimLine(line.substring(11)))) {
      session.error = attackmode::storageError();
      return false;
    }
    if (!attackmode::hidEnabled()) releaseOwnedKeys();
    if (attackmode::storagePreparing()) session.phase = Phase::Storage;
    return true;
  }
  if (startsWithNoCase(line, "KEYCODE ")) {
    String rest = trimLine(line.substring(8));
    if (!rest.length()) return false;
    // Translate numeric reports to the same incremental report path as keys.
    session.cursor = duck_keys::Cursor();
    int space = rest.indexOf(' ');
    uint8_t modifiers = parseNumberToken(space < 0 ? rest : rest.substring(0, space));
    uint8_t keys[6] = {}, count = 0;
    rest = space < 0 ? String() : trimLine(rest.substring(space + 1));
    while (rest.length()) {
      space = rest.indexOf(' ');
      String token = space < 0 ? rest : rest.substring(0, space);
      if (token.length() && count < 6) keys[count++] = parseNumberToken(token);
      rest = space < 0 ? String() : trimLine(rest.substring(space + 1));
    }
    session.remember = true;
    // Defer physical output until update(), including live submissions.
    session.cursor.modifiers = modifiers;
    session.cursor.count = count;
    memcpy(session.cursor.keys, keys, sizeof(keys));
    session.phase = Phase::Keys;
    return true;
  }
  if (!attackmode::hidEnabled()) return true;
  session.remember = true;
  if (startsWithNoCase(line, "STRINGLN ") || startsWithNoCase(line, "STRING ")) {
    bool enter = startsWithNoCase(line, "STRINGLN ");
    String expanded;
    if (!duck_vars::expand(line.substring(enter ? 9 : 7), expanded, session.error)) return false;
    startText(expanded, enter, Phase::Finish);
    return true;
  }
  uint8_t key = 0;
  if (hid_backend::keyNameToHid(line, key)) {
    report(0, &key, 1, Phase::Finish);
    return true;
  }
  session.cursor = duck_keys::Cursor();
  session.phase = Phase::Keys;
  return true;
}

void fail() {
  releaseOwnedKeys();
  session.error = "Command failed: " + session.line + (session.error.length() ? ": " + session.error : String());
  session.phase = Phase::Idle;
  session.repeating = false;
  session.repeatsRemaining = 0;
  script_log::error(session.error);
  if (session.scriptOwned && cbError) cbError();
}

void submit(const String &line, bool preprocessed = false) {
  session.line = trimLine(line);
  session.preprocessed = preprocessed;
  session.textLine = false;
  session.error = "";
  session.phase = Phase::Start;
}
}

namespace com {
void onDone(cb_t cb) { execution::Guard guard; cbDone = cb; }
void onRepeat(cb_t cb) { execution::Guard guard; cbRepeat = cb; }
void onError(cb_t cb) { execution::Guard guard; cbError = cb; }

void beginScript() {
  execution::Guard guard;
  releaseOwnedKeys();
  session = Session();
  session.scriptOwned = true;
  rejected = "";
  duck_vars::clear();
  duck_constants::clear();
}

void endScript() {
  execution::Guard guard;
  attackmode::cancelPendingStorage();
  releaseOwnedKeys();
  session = Session(); // Cancels waits, text, repeat work, and queued commands.
  duck_vars::clear();
  duck_constants::clear();
}

bool busy() { execution::Guard guard; return session.phase != Phase::Idle; }
String lastError() { execution::Guard guard; return session.error; }
String submissionError() { execution::Guard guard; return rejected; }

void send(const String &line) {
  execution::Guard guard;
  if (session.scriptOwned && session.phase == Phase::Idle) submit(line, true);
}

void sendText(const String &text, bool enter) {
  execution::Guard guard;
  if (!session.scriptOwned || session.phase != Phase::Idle) return;
  session.line = text;
  session.textLine = true;
  session.textEnter = enter;
  session.preprocessed = true;
  session.error = "";
  session.phase = Phase::Start;
}

bool executeNow(const String &line) {
  execution::Guard guard;
  if (session.scriptOwned || session.phase != Phase::Idle) {
    rejected = session.scriptOwned ? "Busy: script running" : "Busy: command in progress";
    return false;
  }
  rejected = "";
  if (line.length() > DUCKSCRIPT_MAX_LINE_LEN) {
    rejected = "Script line length limit exceeded";
    return false;
  }
  submit(line);
  if (!startLine()) {
    fail();
    rejected = session.error;
    return false;
  }
  return true; // Accepted; timed/output work completes through update().
}

void update() {
  execution::Guard guard;
  attackmode::update();
  hid_backend::update(); // Cancellation releases are serviced even when idle.
  if (hid_backend::takeTransportLoss()) {
    if (session.scriptOwned || session.phase != Phase::Idle) {
      session.error = "USB transport disconnected; keyboard ownership cleared";
      fail();
      return;
    }
  }
  if (session.lockCommand == 10 && session.phase != Phase::Idle && session.phase != Phase::Start &&
      session.phase != Phase::Finish && millis() - session.lockStarted >= session.lockDeadline) {
    session.error = "Host lock feedback timeout during transport work"; fail(); return;
  }
  switch (session.phase) {
    case Phase::Idle: return;
    case Phase::Start:
      if (!startLine()) fail();
      return;
    case Phase::Storage:
      if (attackmode::storagePreparing()) return;
      if (!attackmode::storageEnabled()) {
        session.error = attackmode::storageError();
        if (!session.error.length()) session.error = "MSC: preparation cancelled or media unavailable";
        fail();
      } else session.phase = Phase::Finish;
      return;
    case Phase::Ownership: {
      const bool accepted = session.holding ?
        hid_backend::hold(session.ownedModifier, session.ownedKey) :
        hid_backend::release(session.ownedModifier, session.ownedKey);
      if (!accepted) {
        if (*hid_backend::reportError()) { session.error = hid_backend::reportError(); fail(); }
        return;
      }
      session.phase = Phase::Finish;
      return;
    }
    case Phase::LockWait:
    case Phase::LockRestore:
    case Phase::LockAck: {
      const auto state = hid_backend::lockState();
      if (state.session != session.lockSession) { session.error = "USB session changed during lock operation"; fail(); return; }
      if (millis() - session.lockStarted >= session.lockDeadline) { session.error = "Host lock feedback timeout; no acknowledged success"; fail(); return; }
      if (session.phase == Phase::LockWait) {
        if (!state.known) return;
        const auto action = session.lockCommand % 3;
        if (action == 2) {
          if (!session.lockBaselineKnown) { session.lockBaselineKnown = true; session.lockChanges = state.changes[session.lockBit]; return; }
          if (state.changes[session.lockBit] == session.lockChanges) return;
        } else if (((state.leds >> session.lockBit) & 1) != action) return;
        session.phase = Phase::Finish; return;
      }
      if (!state.known) { session.error = "Host lock state became unknown during restore"; fail(); return; }
      if (session.phase == Phase::LockAck) {
        const uint8_t mask = 1u << session.lockBit;
        if (state.changes[session.lockBit] == session.lockChanges || ((state.leds ^ session.lockTarget) & mask)) return;
        session.phase = Phase::LockRestore; return;
      }
      if (state.leds == session.lockTarget) { session.lockCommand = -1; session.phase = Phase::Finish; return; }
      if (hid_backend::hasPersistent() || !attackmode::hidEnabled()) { session.error = "Keyboard ownership/HID changed during restore"; fail(); return; }
      if (session.lockToggles++ >= 6) { session.error = "Host lock state changed repeatedly during restore"; fail(); return; }
      for (uint8_t bit = 0; bit < 3; ++bit) if ((state.leds ^ session.lockTarget) & (1u << bit)) { session.lockBit = bit; break; }
      session.lockChanges = state.changes[session.lockBit];
      const uint8_t keys[] = {0x53, 0x39, 0x47};
      report(0, &keys[session.lockBit], 1, Phase::LockAck);
      return;
    }
    case Phase::Reset:
      if (!hid_backend::clearing()) session.phase = Phase::Finish;
      return;
    case Phase::Wait: {
      uint32_t now = millis();
      uint32_t elapsed = now - session.waitStarted; // Safe across millis() wrap.
      if (elapsed >= session.waitRemaining) session.phase = session.afterWait;
      else {
        session.waitRemaining -= elapsed;
        session.waitStarted = now;
      }
      return;
    }
    case Phase::Press:
      if (session.lockCommand == 10) {
        const auto state = hid_backend::lockState();
        if (!state.known || state.session != session.lockSession) {
          session.error = "USB lock state became unknown before restore injection"; fail(); return;
        }
        // Host may change state while endpoint backpressure delays the press.
        // Do not send a stale toggle that would undo an already restored bit.
        if (!((state.leds ^ session.lockTarget) & (1u << session.lockBit))) {
          session.phase = Phase::LockRestore; return;
        }
        session.lockChanges = state.changes[session.lockBit];
      }
      if (!hid_backend::beginReport(session.reportModifiers, session.reportKeys, session.reportCount)) {
        if (*hid_backend::reportError()) { session.error = hid_backend::reportError(); fail(); }
        return;
      }
      session.ownsKeys = true;
      waitFor(5, Phase::Release);
      return;
    case Phase::Release:
      if (!hid_backend::releaseReport()) return;
      session.ownsKeys = false;
      session.phase = session.afterRelease;
      return;
    case Phase::Text:
      if (!attackmode::hidEnabled()) { session.phase = session.afterText; return; }
      if (session.strokeIndex < session.strokeCount) {
        auto stroke = session.strokes[session.strokeIndex++];
        report(stroke.modifiers | session.textModifiers, &stroke.key, 1, Phase::Text);
        return;
      }
      if (session.offset < session.text.length()) {
        const bool nonAscii = uint8_t(session.text[session.offset]) >= 128;
        session.offset += keyboard_locale::translate(session.text.c_str() + session.offset,
          session.text.length() - session.offset, session.strokes, session.strokeCount);
        session.strokeIndex = 0;
        if (nonAscii && !session.strokeCount && !session.warnedUnsupported) {
          script_log::warn("Unsupported text character skipped by selected locale");
          session.warnedUnsupported = true;
        }
        return;
      }
      if (session.enter) {
        session.enter = false;
        const uint8_t enter = 0x28;
        report(0, &enter, 1, Phase::Text);
        return;
      }
      session.phase = session.afterText;
      return;
    case Phase::Keys: {
      uint8_t modifiers = 0, keys[6] = {}, count = 0;
      String text;
      if (!attackmode::hidEnabled()) { session.phase = Phase::Finish; return; }
      if (startsWithNoCase(session.line, "KEYCODE ")) {
        report(session.cursor.modifiers, session.cursor.keys, session.cursor.count, Phase::Finish);
        return;
      }
      auto item = duck_keys::next(session.line, session.cursor, modifiers, keys, count, text);
      if (item == duck_keys::Item::Report) report(modifiers, keys, count, Phase::Keys);
      else if (item == duck_keys::Item::Text) startText(text, false, Phase::Keys, modifiers);
      else if (item == duck_keys::Item::Done) session.phase = Phase::Finish;
      return;
    }
    case Phase::Finish:
      if (session.remember) {
        if (!session.repeating) {
          session.history = session.line;
          session.historyText = session.textLine;
          session.historyEnter = session.textEnter;
        }
        session.remember = false;
        waitFor(session.defaultDelay, Phase::Finish);
        return;
      }
      if (session.repeating && --session.repeatsRemaining) {
        session.line = session.history;
        session.textLine = session.historyText;
        session.textEnter = session.historyEnter;
        session.phase = Phase::Start;
        if (session.scriptOwned && cbRepeat) cbRepeat();
        return;
      }
      session.repeating = false;
      session.phase = Phase::Idle;
      if (session.scriptOwned && cbDone) cbDone();
      return;
  }
}
}
