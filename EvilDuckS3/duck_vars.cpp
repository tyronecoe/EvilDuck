#include "duck_vars.h"
#include <string.h>

namespace duck_vars {
namespace {
Symbols symbols;
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
duck_expr::Lookup Symbols::resolve(const char *name, size_t length, uint16_t &, void *context) {
  Type kind = static_cast<Symbols *>(context)->type(name, length);
  return kind == Type::Numeric ? duck_expr::Lookup::Number :
    kind == Type::Text ? duck_expr::Lookup::Text : duck_expr::Lookup::Undefined;
}

void clear() {
  symbols.clear();
  for (size_t i = 0; i < DUCKSCRIPT_MAX_VARIABLES; ++i) { texts[i] = String(); numbers[i] = 0; }
}
duck_expr::Lookup resolve(const char *name, size_t length, uint16_t &value, void *) {
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
  int at = symbols.declare(name, Type::Numeric, !declaration, error);
  if (at < 0) return false;
  numbers[at] = value;
  return true;
}
bool setText(const String &name, const String &value, bool declaration, String &error) {
  int at = symbols.declare(name, Type::Text, !declaration, error);
  if (at < 0) return false;
  texts[at] = value;
  return true;
}
bool set(const String &name, const String &value) {
  String error;
  return setText(name, value, true, error); // Preserved interface: explicitly text.
}
bool get(const String &name, String &out) {
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
      found = get(input.substring(i, end), value);
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
