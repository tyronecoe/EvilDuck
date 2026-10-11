#include "script_preprocessor.h"
#include "duck_constants.h"
#include <cstring>

namespace script_preprocessor {
namespace {
bool fail(String &error, const char *message) { error = message; return false; }
bool space(char c) { return c == ' ' || c == '\t'; }
}
bool Filter::accept(const String &line, uint32_t number, String &error) {
  if (!number || number > DUCKSCRIPT_MAX_SOURCE_LINES) return fail(error, "Preprocessing source-line limit exceeded");
  String text = line; text.trim();
  bool selected = active(), ordinary = false;
  // Included unmatched markers are checked in the expanded inventory pass, so
  // an earlier illegal macro-created delimiter retains its own source error.
  // Excluded markers still need raw structural validation here.
  if (!blocks.scan(line, number, ordinary, error, selected)) return false;
  if (ordinary) {
    size_t end = 0; while (end < text.length() && !space(text[end])) ++end;
    String keyword = text.substring(0, end); keyword.toUpperCase();
    String args = text.substring(end); args.trim();
    if (keyword == "IF_DEFINED_TRUE" || keyword == "IF_NOT_DEFINED_TRUE") {
      char sigil = args[0] == '#' ? '#' : 0;
      if (!duck_expr::identifier(args.c_str(), args.length(), sigil)) return fail(error, "Preprocessing condition requires one DEFINE label");
      if (depth == DUCKSCRIPT_MAX_PREPROCESS_DEPTH) return fail(error, "Preprocessing nesting limit exceeded");
      bool value = false;
      if (selected && !duck_constants::boolean(args, value, error)) return false;
      frames[depth++] = {number, selected, selected && (keyword == "IF_DEFINED_TRUE" ? value : !value), false};
      return true;
    }
    if (keyword == "ELSE_DEFINED" || keyword == "END_IF_DEFINED") {
      if (args.length()) return fail(error, "Preprocessing delimiter takes no arguments");
      if (!depth) return fail(error, "Unmatched preprocessing delimiter");
      if (extension && depth <= extensionDepth) return fail(error, "Preprocessing delimiter crosses EXTENSION boundary");
      Frame &frame = frames[depth - 1];
      if (keyword == "ELSE_DEFINED") {
        if (frame.sawElse) return fail(error, "Duplicate ELSE_DEFINED");
        frame.sawElse = true; frame.selected = frame.parent && !frame.selected;
      } else --depth;
      return true;
    }
    if (keyword == "EXTENSION" || keyword == "END_EXTENSION" || keyword == "VERSION") {
      script_parser::Statement statement;
      if (!script_parser::parse(text, statement, error)) return false;
      if (keyword == "EXTENSION") {
        if (extension) return fail(error, "Nested EXTENSION is unsupported");
        if (selected) {
          for (uint8_t i = 0; i < extensionCount; ++i)
            if (args == extensions[i]) return fail(error, "Duplicate EXTENSION name");
          if (extensionCount == DUCKSCRIPT_MAX_EXTENSIONS) return fail(error, "Extension table exhausted");
          memcpy(extensions[extensionCount++], args.c_str(), args.length() + 1);
        }
        extension = true; extensionIncluded = selected; extensionDepth = depth;
        extensionLine = number; versionSeen = contentSeen = false;
      } else if (keyword == "END_EXTENSION") {
        if (!extension || depth != extensionDepth) return fail(error, "Mismatched EXTENSION/preprocessing boundary");
        extension = false;
      } else {
        if (!extension || depth != extensionDepth) return fail(error, "VERSION requires an extension header");
        if (selected && extensionIncluded) {
          if (versionSeen || contentSeen) return fail(error, "Duplicate or misplaced VERSION metadata");
          versionSeen = true;
        }
      }
    } else if (selected && text.length()) {
      if (extension) contentSeen = true;
      if (duck_constants::declaration(line) && !duck_constants::define(line, number, error)) return false;
    }
  }
  if (selected) included[(number - 1) / 8] |= 1U << ((number - 1) % 8);
  return true;
}
bool Filter::finish(String &error, uint32_t &number) const {
  if (!blocks.finish(error, number)) return false;
  if (extension) { number = extensionLine; return fail(error, "Unterminated EXTENSION"); }
  if (depth) { number = frames[depth - 1].line; return fail(error, "Unterminated conditional preprocessing block"); }
  return true;
}
}
