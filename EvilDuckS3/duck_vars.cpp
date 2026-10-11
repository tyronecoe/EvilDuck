#include "duck_vars.h"
#include <string.h>
#include "internal_vars.h"
#include "duck_random.h"
#include "hid_backend.h"
#include "attackmode.h"

namespace duck_vars {
namespace {
Symbols symbols;
uint32_t changes = 0;
uint16_t numbers[DUCKSCRIPT_MAX_VARIABLES] = {};
String texts[DUCKSCRIPT_MAX_VARIABLES];
bool fail(String &error, const char *message) { error = message; return false; }
}

int Symbols::index(const char *name, size_t length) const {
  for (uint8_t i = 0; i < count; ++i)
    if (strlen(entries[i].name) == length && memcmp(entries[i].name, name, length) == 0) return i;
  return -1;
}
Type Symbols::type(const char *name, size_t length) const {
  int at = index(name, length);
  return at < 0 ? Type::Missing : entries[at].type;
}
int Symbols::declare(const String &name, Type kind, bool mustExist, String &error) {
  static_assert(DUCKSCRIPT_MAX_VARIABLES > 0 && DUCKSCRIPT_MAX_VARIABLES < 256, "Invalid variable limit");
  if (!duck_expr::identifier(name.c_str(), name.length())) { error = "Invalid variable identifier"; return -1; }
  if (internal_vars::reserved(name.c_str(), name.length())) {
    if (mustExist && kind == Type::Numeric && internal_vars::writable(name.c_str(), name.length())) return 0;
    error = "Reserved internal variable: declaration or write is unsupported/read-only"; return -1;
  }
  int at = index(name.c_str(), name.length());
  if (at >= 0) {
    if (entries[at].type != kind) { error = "Variable type cannot change between numeric and text"; return -1; }
    return at;
  }
  if (mustExist) { error = "Assignment to undefined variable"; return -1; }
  if (count >= DUCKSCRIPT_MAX_VARIABLES) { error = "Variable table exhausted"; return -1; }
  at = count++;
  memcpy(entries[at].name, name.c_str(), name.length());
  entries[at].name[name.length()] = 0;
  entries[at].type = kind;
  return at;
}
duck_expr::Lookup Symbols::resolve(const char *name, size_t length, uint16_t &value, void *context) {
  if (internal_vars::reserved(name, length)) return internal_vars::resolve(name, length, value, true);
  Type kind = static_cast<Symbols *>(context)->type(name, length);
  return kind == Type::Numeric ? duck_expr::Lookup::Number :
    kind == Type::Text ? duck_expr::Lookup::Text : duck_expr::Lookup::Undefined;
}

uint32_t revision() { return changes; }
void clear() {
  symbols.clear();
  internal_vars::resetRun();
  changes = 0;
  for (size_t i = 0; i < DUCKSCRIPT_MAX_VARIABLES; ++i) { texts[i] = String(); numbers[i] = 0; }
}
duck_expr::Lookup resolve(const char *name, size_t length, uint16_t &value, void *) {
  if (internal_vars::reserved(name, length)) return internal_vars::resolve(name, length, value);
  int at = symbols.index(name, length);
  if (at < 0) return duck_expr::Lookup::Undefined;
  if (symbols.type(name, length) == Type::Text) return duck_expr::Lookup::Text;
  value = numbers[at];
  return duck_expr::Lookup::Number;
}
bool getNumeric(const String &name, uint16_t &value) {
  return resolve(name.c_str(), name.length(), value, nullptr) == duck_expr::Lookup::Number;
}
bool assign(const String &name, const String &expression, bool declaration, String &error) {
  uint16_t value = 0;
  duck_expr::Error diagnostic;
  if (!duck_expr::evaluate(expression.c_str(), expression.length(), value, diagnostic, resolve)) {
    error = "Expression column " + String(diagnostic.column) + ": " + diagnostic.message;
    return false;
  }
  if (internal_vars::reserved(name.c_str(), name.length())) {
    if (declaration) return fail(error, "Reserved internal variable cannot be declared");
    uint16_t before=0;
    const bool changed = internal_vars::resolve(name.c_str(),name.length(),before,true)==duck_expr::Lookup::Number && before!=value;
    if (!internal_vars::write(name, value, error)) return false;
    if (changed) ++changes;
    return true;
  }
  bool created = symbols.type(name.c_str(), name.length()) == Type::Missing;
  int at = symbols.declare(name, Type::Numeric, !declaration, error);
  if (at < 0) return false;
  if (created || numbers[at] != value) ++changes;
  numbers[at] = value;
  return true;
}
bool setText(const String &name, const String &value, bool declaration, String &error) {
  bool created = symbols.type(name.c_str(), name.length()) == Type::Missing;
  int at = symbols.declare(name, Type::Text, !declaration, error);
  if (at < 0) return false;
  if (created || texts[at] != value) ++changes;
  texts[at] = value;
  return true;
}
bool set(const String &name, const String &value) {
  String error;
  return setText(name, value, true, error); // Preserved interface: explicitly text.
}
bool get(const String &name, String &out) {
  if (internal_vars::reserved(name.c_str(), name.length())) {
    uint16_t value;
    if (internal_vars::resolve(name.c_str(), name.length(), value) != duck_expr::Lookup::Number) return false;
    out = String(value); return true;
  }
  int at = symbols.index(name.c_str(), name.length());
  if (at < 0) return false;
  out = symbols.type(name.c_str(), name.length()) == Type::Text ? texts[at] : String(numbers[at]);
  return true;
}
bool expand(const String &input, String &out, String &error) {
  out = "";
  if (input.length() > DUCKSCRIPT_MAX_EXPANDED_LINE) return fail(error, "Interpolation length limit exceeded");
  for (size_t i = 0; i < input.length();) {
    size_t end = i;
    String value;
    bool found = false;
    if (input[i] == '$') {
      end = i + 1;
      while (end < input.length() && (isalnum(static_cast<unsigned char>(input[end])) || input[end] == '_')) ++end;
      const String name = input.substring(i, end);
      found = get(name, value);
      if (!found && internal_vars::reserved(name.c_str(), name.length()))
        return fail(error, name=="$_RANDOM_INT" ? "Random generation failed: reversed range or source rejection limit" : "Internal variable unsupported or state unknown during interpolation");
    }
    if (found) {
      if (value.length() > DUCKSCRIPT_MAX_EXPANDED_LINE - out.length()) return fail(error, "Interpolation length limit exceeded");
      out += value;
      i = end;
    } else {
      if (out.length() >= DUCKSCRIPT_MAX_EXPANDED_LINE) return fail(error, "Interpolation length limit exceeded");
      out += input[i++];
    }
  }
  return true;
}
String expand(const String &input) {
  String output, error;
  if (!expand(input, output, error)) return String();
  return output;
}
bool truthy(const String &name) {
  uint16_t number = 0;
  if (getNumeric(name, number)) return number != 0;
  String value;
  if (!get(name, value)) return false;
  value.trim(); value.toLowerCase();
  return value.length() && value != "0" && value != "false";
}
}

namespace internal_vars {
namespace {
const char *const nativeNames[] = {"$_BUTTON_ENABLED", "$_BUTTON_PUSH_RECEIVED", "$_BUTTON_TIMEOUT", "$_BUTTON_USER_DEFINED", "$_CAPSLOCK_ON", "$_CURRENT_ATTACKMODE", "$_CURRENT_PID", "$_CURRENT_VID", "$_EXFIL_LEDS_ENABLED", "$_EXFIL_MODE_ENABLED", "$_HOST_CONFIGURATION_REQUEST_COUNT", "$_INJECTING_LEDS_ENABLED", "$_JITTER_ENABLED", "$_JITTER_MAX", "$_LED_CONTINUOUS_SHOW_STORAGE_ACTIVITY", "$_LED_SHOW_CAPS", "$_LED_SHOW_NUM", "$_LED_SHOW_SCROLL", "$_NUMLOCK_ON", "$_RANDOM_CHAR_KEYCODE", "$_RANDOM_INT", "$_RANDOM_LETTER_KEYCODE", "$_RANDOM_LOWER_LETTER_KEYCODE", "$_RANDOM_MAX", "$_RANDOM_MIN", "$_RANDOM_NUMBER_KEYCODE", "$_RANDOM_SEED", "$_RANDOM_SPECIAL_KEYCODE", "$_RANDOM_UPPER_LETTER_KEYCODE", "$_RECEIVED_HOST_LOCK_LED_REPLY", "$_SAVED_CAPSLOCK_ON", "$_SAVED_NUMLOCK_ON", "$_SAVED_SCROLLLOCK_ON", "$_SCROLLLOCK_ON", "$_STORAGE_ACTIVITY_TIMEOUT", "$_STORAGE_LEDS_ENABLED", "$_SYSTEM_LEDS_ENABLED"};
const char *const extraNames[] = {"$_EVILDUCK_STORAGE_REQUESTED", "$_EVILDUCK_STORAGE_ACTIVE",
  "$_EVILDUCK_STORAGE_PREPARING", "$_EVILDUCK_STORAGE_FAILED", "$_EVILDUCK_STORAGE_STATE",
  "$_EVILDUCK_HID_ENABLED", "$_EVILDUCK_LOCK_KNOWN", "$_EVILDUCK_LOCK_TIMEOUT"};
uint16_t timeout = 5000;
bool equal(const char *name, size_t length, const char *candidate) {
  return strlen(candidate) == length && !memcmp(name, candidate, length);
}
}
bool reserved(const char *name, size_t length) {
  for (auto candidate : nativeNames) if (equal(name, length, candidate)) return true;
  for (auto candidate : extraNames) if (equal(name, length, candidate)) return true;
  return false;
}
bool writable(const char *name, size_t length) {
  return equal(name,length,"$_EVILDUCK_LOCK_TIMEOUT") || equal(name,length,"$_RANDOM_MIN") ||
    equal(name,length,"$_RANDOM_MAX") || equal(name,length,"$_JITTER_ENABLED") || equal(name,length,"$_JITTER_MAX");
}
int lockCommand(const String &line) {
  static const char *const commands[] = {"WAIT_FOR_NUM_OFF", "WAIT_FOR_NUM_ON", "WAIT_FOR_NUM_CHANGE",
    "WAIT_FOR_CAPS_OFF", "WAIT_FOR_CAPS_ON", "WAIT_FOR_CAPS_CHANGE",
    "WAIT_FOR_SCROLL_OFF", "WAIT_FOR_SCROLL_ON", "WAIT_FOR_SCROLL_CHANGE",
    "SAVE_HOST_KEYBOARD_LOCK_STATE", "RESTORE_HOST_KEYBOARD_LOCK_STATE"};
  String upper = line; upper.toUpperCase();
  for (unsigned i = 0; i < sizeof(commands)/sizeof(*commands); ++i) if (upper == commands[i]) return i;
  return -1;
}
uint16_t lockTimeout() { return timeout; }
void resetRun() { timeout = 5000; duck_random::resetRun(); }
bool validate(const String &name, uint16_t value, String &error) {
  if (!writable(name.c_str(), name.length())) { error = "Internal variable is read-only or unsupported"; return false; }
  if (name=="$_EVILDUCK_LOCK_TIMEOUT" && !value) { error="Lock timeout must be 1..65535 milliseconds";return false; }
  if (name=="$_JITTER_ENABLED" && value>1) { error="Jitter enabled requires TRUE/FALSE (0 or 1)";return false; }
  return true;
}
bool write(const String &name, uint16_t value, String &error) {
  if(!validate(name,value,error))return false;
  if(name=="$_RANDOM_MIN")duck_random::setMinimum(value);
  else if(name=="$_RANDOM_MAX")duck_random::setMaximum(value);
  else if(name=="$_JITTER_MAX")duck_random::setJitterMaximum(value);
  else if(name=="$_JITTER_ENABLED")duck_random::setJitterEnabled(value!=0);
  else timeout=value;
  return true;
}
duck_expr::Lookup resolve(const char *name, size_t length, uint16_t &value, bool syntax) {
  using L = duck_expr::Lookup;
  if (!reserved(name, length)) return L::Undefined;
  if (equal(name,length,"$_RANDOM_INT")) {
    if(syntax) {value=0;return L::Number;}
    return duck_random::integer(value) ? L::Number : L::RandomError;
  }
  if (equal(name,length,"$_RANDOM_MIN")) {value=duck_random::minimum();return L::Number;}
  if (equal(name,length,"$_RANDOM_MAX")) {value=duck_random::maximum();return L::Number;}
  if (equal(name,length,"$_JITTER_ENABLED")) {value=duck_random::jitterEnabled();return L::Number;}
  if (equal(name,length,"$_JITTER_MAX")) {value=duck_random::jitterMaximum();return L::Number;}
  const auto state = hid_backend::lockState();
  const char *const locks[] = {"$_NUMLOCK_ON", "$_CAPSLOCK_ON", "$_SCROLLLOCK_ON",
    "$_SAVED_NUMLOCK_ON", "$_SAVED_CAPSLOCK_ON", "$_SAVED_SCROLLLOCK_ON"};
  for (unsigned i = 0; i < 6; ++i) if (equal(name, length, locks[i])) {
    if (!syntax && !(i < 3 ? state.known : state.savedKnown)) return L::Unavailable;
    value = ((i < 3 ? state.leds : state.saved) >> (i % 3)) & 1;
    return L::Number;
  }
  if (equal(name, length, "$_RECEIVED_HOST_LOCK_LED_REPLY") || equal(name, length, "$_EVILDUCK_LOCK_KNOWN")) value = state.known;
  else if (equal(name, length, "$_EVILDUCK_LOCK_TIMEOUT")) value = timeout;
  else if (equal(name, length, "$_EVILDUCK_HID_ENABLED")) value = attackmode::hidEnabled();
  else if (equal(name, length, "$_EVILDUCK_STORAGE_REQUESTED")) value = attackmode::storageRequested();
  else if (equal(name, length, "$_EVILDUCK_STORAGE_ACTIVE")) value = attackmode::storageEnabled();
  else if (equal(name, length, "$_EVILDUCK_STORAGE_PREPARING")) value = attackmode::storagePreparing();
  else if (equal(name, length, "$_EVILDUCK_STORAGE_FAILED")) value = !strcmp(attackmode::storageState(), "failed");
  else if (equal(name, length, "$_EVILDUCK_STORAGE_STATE")) {
    const char *state = attackmode::storageState();
    value = !strcmp(state, "preparing") ? 1 : !strcmp(state, "active") ? 2 : !strcmp(state, "ejected") ? 3 : !strcmp(state, "failed") ? 4 : 0;
  } else return L::Unsupported;
  return L::Number;
}
}
