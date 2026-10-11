#include "duck_constants.h"
#include "duck_expr.h"
#include "script_parser.h"
#include <string.h>

namespace duck_constants {
namespace {
struct Constant { char name[DUCKSCRIPT_MAX_IDENTIFIER_LEN + 1] = {};
  uint16_t offset = 0, length = 0; uint32_t line = 0; };
Constant constants[DUCKSCRIPT_MAX_CONSTANTS];
char values[DUCKSCRIPT_CONSTANT_POOL_BYTES];
uint16_t used = 0;
uint8_t count = 0;
bool space(char c) { return c == ' ' || c == '\t'; }
bool fail(String &error, const char *message) { error = message; return false; }
size_t start(const String &line) { size_t at = 0; while (at < line.length() && space(line[at])) ++at; return at; }
}
void clear() { count = 0; used = 0; }
bool declaration(const String &line) {
  String trimmed = line; trimmed.trim();
  if (!script_parser::hasKeyword(trimmed, "DEFINE")) return false;
  size_t at = 6;
  while (at < trimmed.length() && space(trimmed[at])) ++at;
  return trimmed[at] != '$';
}
bool definition(const String &line, String &label, String &value, String &error) {
  if (line.length() > DUCKSCRIPT_MAX_EXPANDED_LINE + DUCKSCRIPT_MAX_IDENTIFIER_LEN + 8)
    return fail(error, "DEFINE value length limit exceeded");
  if (!script_parser::hasKeyword(line.substring(start(line)), "DEFINE")) return fail(error, "Expected DEFINE keyword");
  size_t at = start(line) + 6;
  while (at < line.length() && space(line[at])) ++at;
  size_t labelStart = at;
  while (at < line.length() && !space(line[at])) ++at;
  if (at - labelStart > DUCKSCRIPT_MAX_IDENTIFIER_LEN) return fail(error, "Invalid DEFINE label");
  label = line.substring(labelStart, at);
  char sigil = label[0] == '#' ? '#' : 0;
  if (!duck_expr::identifier(label.c_str(), label.length(), sigil)) return fail(error, "Invalid DEFINE label");
  if (at >= line.length() || at + 1 >= line.length()) return fail(error, "DEFINE requires a value");
  if (line.length() - at - 1 > DUCKSCRIPT_MAX_EXPANDED_LINE) return fail(error, "DEFINE value length limit exceeded");
  value = line.substring(at + 1);
  if (value.length() > DUCKSCRIPT_MAX_EXPANDED_LINE) return fail(error, "DEFINE value length limit exceeded");
  return true;
}
bool define(const String &line, uint32_t number, String &error) {
  static_assert(DUCKSCRIPT_MAX_CONSTANTS > 0 && DUCKSCRIPT_MAX_CONSTANTS < 256 &&
                DUCKSCRIPT_CONSTANT_POOL_BYTES < 65536, "Invalid constant storage limits");
  String label, value;
  if (!definition(line, label, value, error)) return false;
  for (uint8_t i = 0; i < count; ++i) if (label == constants[i].name) {
    error = "Duplicate DEFINE label " + label + " (first defined at line " + String(constants[i].line) + ")";
    return false;
  }
  if (count >= DUCKSCRIPT_MAX_CONSTANTS) return fail(error, "Constant table exhausted");
  if (value.length() + 1 > size_t(DUCKSCRIPT_CONSTANT_POOL_BYTES - used)) return fail(error, "DEFINE value pool exhausted");
  Constant &entry = constants[count++];
  memcpy(entry.name, label.c_str(), label.length() + 1);
  entry.offset = used; entry.length = value.length(); entry.line = number;
  memcpy(values + used, value.c_str(), value.length() + 1);
  used += value.length() + 1;
  return true;
}
bool boolean(const String &label, bool &value, String &error) {
  value = false;
  for (uint8_t i = 0; i < count; ++i) if (label == constants[i].name) {
    String literal = values + constants[i].offset; literal.trim();
    if (literal == "TRUE" || literal == "FALSE") { value = literal == "TRUE"; return true; }
    return fail(error, "Preprocessing flag must be a literal TRUE or FALSE");
  }
  return true; // Undefined labels are false, as specified by IF_DEFINED_TRUE.
}
bool expand(const String &line, String &output, String &error) {
  if (script_parser::hasKeyword(line, "DEFINE")) { output = line; return true; }
  char buffer[DUCKSCRIPT_MAX_EXPANDED_LINE + 1];
  size_t size = 0;
  for (size_t at = 0; at < line.length();) {
    const Constant *match = nullptr;
    size_t longest = 0;
    for (uint8_t i = 0; i < count; ++i) {
      size_t n = strlen(constants[i].name);
      if (n <= longest || n > line.length() - at || memcmp(line.c_str() + at, constants[i].name, n)) continue;
      if (constants[i].name[0] != '#' &&
          ((at && !space(line[at - 1])) || (at + n < line.length() && !space(line[at + n])))) continue;
      match = &constants[i]; longest = n;
    }
    size_t bytes = match ? match->length : 1;
    if (bytes > DUCKSCRIPT_MAX_EXPANDED_LINE - size) return fail(error, "DEFINE expansion length limit exceeded");
    memcpy(buffer + size, match ? values + match->offset : line.c_str() + at, bytes);
    size += bytes;
    at += match ? longest : 1;
  }
  buffer[size] = 0;
  output = buffer;
  return true;
}
bool Collector::accept(const String &line, uint32_t number, String &error) {
  bool ordinary;
  if (!blocks.scan(line, number, ordinary, error)) return false;
  return !ordinary || !declaration(line) || define(line, number, error);
}
}
