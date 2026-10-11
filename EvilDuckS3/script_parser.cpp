#include "script_parser.h"
#include "hid_backend.h"
#include "duck_keys.h"
#include "storage.h"
#include "keyboard_locale.h"
#include "duck_constants.h"
#include "script_functions.h"
#include <cstdlib>

namespace script_parser {
namespace {
bool space(char c) { return c == ' ' || c == '\t'; }
String trimmed(String s) { s.trim(); return s; }
bool error(String &out, const char *message) { out = message; return false; }
bool word(const String &line, size_t &offset, String &out) {
  while (offset < line.length() && space(line[offset])) ++offset;
  size_t start = offset;
  while (offset < line.length() && !space(line[offset])) ++offset;
  out = line.substring(start, offset);
  return offset > start;
}
String words(const String &in) {
  String result, token;
  size_t offset = 0;
  while (word(in, offset, token)) { if (result.length()) result += ' '; result += token; }
  return result;
}
bool variable(const String &name) {
  return duck_expr::identifier(name.c_str(), name.length());
}
bool operand(const String &input) {
  String value = trimmed(input);
  if (!value.length()) return false;
  if (value.startsWith("\"")) return value.length() >= 2 && value.endsWith("\"");
  if (value.startsWith("$")) return variable(value);
  for (size_t i = 0; i < value.length(); ++i) if (space(value[i])) return false;
  return true;
}
// This recognizes only the old no-THEN atom/equality grammar, not expressions.
bool legacySyntax(const String &input, String &diagnostic, int *split = nullptr) {
  bool quoted = false;
  int equality = -1;
  for (size_t i = 0; i < input.length(); ++i) {
    char c = input[i];
    if (c == '"') quoted = !quoted;
    if (!quoted && strchr("<>!+-*/%&|()^~", c))
      return error(diagnostic, "Canonical IF expressions require a final THEN token");
    if (!quoted && c == '=') {
      if (input[i + 1] != '=' || equality >= 0) return error(diagnostic, "Malformed legacy IF equality");
      equality = i++;
    }
  }
  if (quoted) return error(diagnostic, "Unterminated quoted IF operand");
  if (equality < 0 ? !operand(input) :
      (!operand(input.substring(0, equality)) || !operand(input.substring(equality + 2))))
    return error(diagnostic, "Malformed legacy IF condition: expected atom or atom == atom");
  if (split) *split = equality;
  return true;
}
bool conditionalArgs(Statement &out, bool allowLegacy, String &diagnostic) {
  size_t end = out.args.length(), start = end;
  while (start && !space(out.args[start - 1])) --start;
  String last = out.args.substring(start); last.toUpperCase();
  if (last == "THEN") {
    out.args = trimmed(out.args.substring(0, start));
    return expression(out.args, diagnostic);
  }
  if (!allowLegacy) return error(diagnostic, "ELSE IF requires a condition and final THEN token");
  if (!out.args.length()) return error(diagnostic, "Missing control-flow condition");
  if (!legacySyntax(out.args, diagnostic)) return false;
  out.legacyCondition = true;
  uint16_t ignored;
  return condition(out.args, true, ignored, diagnostic, duck_expr::Mode::Syntax, nullptr);
}
bool number(const String &token, uint32_t maximum, bool hex = false) {
  size_t i = token[0] == '+' ? 1 : 0;
  unsigned base = 10;
  if (hex && (token.substring(i, i + 2) == "0x" || token.substring(i, i + 2) == "0X")) { base = 16; i += 2; }
  if (i >= token.length()) return false;
  uint32_t value = 0;
  for (; i < token.length(); ++i) {
    char c = token[i];
    unsigned digit = c >= '0' && c <= '9' ? c - '0' :
      c >= 'a' && c <= 'f' ? c - 'a' + 10 : c >= 'A' && c <= 'F' ? c - 'A' + 10 : 255;
    if (digit >= base || digit > maximum || value > (maximum - digit) / base) return false;
    value = value * base + digit;
  }
  return true;
}
bool character(const String &token) {
  if (token.length() == 1) return static_cast<uint8_t>(token[0]) >= 0x20 && static_cast<uint8_t>(token[0]) < 0x7F;
  // Allow one well-formed UTF-8 character as the legacy literal-key fallback.
  uint8_t first = token[0];
  size_t n = first >= 0xC2 && first <= 0xDF ? 2 : first >= 0xE0 && first <= 0xEF ? 3 :
    first >= 0xF0 && first <= 0xF4 ? 4 : 0;
  if (!n || token.length() != n) return false;
  for (size_t i = 1; i < n; ++i) if ((uint8_t(token[i]) & 0xC0) != 0x80) return false;
  uint8_t second = token[1];
  return !(first == 0xE0 && second < 0xA0) && !(first == 0xED && second >= 0xA0) &&
         !(first == 0xF0 && second < 0x90) && !(first == 0xF4 && second >= 0x90);
}
}

bool expression(const String &input, String &diagnostic, duck_expr::Resolver resolver, void *context) {
  uint16_t value = 0;
  duck_expr::Error failure;
  if (duck_expr::evaluate(input.c_str(), input.length(), value, failure, resolver, context, duck_expr::Mode::Syntax)) return true;
  diagnostic = "Expression column " + String(failure.column) + ": " + failure.message;
  return false;
}

bool condition(const String &input, bool legacy, uint16_t &value, String &diagnostic,
               duck_expr::Mode mode, duck_expr::Resolver resolver, void *context) {
  String adapted;
  const String *source = &input;
  if (legacy) {
    int equality = -1;
    if (!legacySyntax(input, diagnostic, &equality)) return false;
    String atoms[2]; bool textual = false;
    unsigned count = equality < 0 ? 1 : 2;
    for (unsigned i = 0; i < count; ++i) {
      String atom = trimmed(equality < 0 ? input : i ? input.substring(equality + 2) : input.substring(0, equality));
      if (atom[0] == '$') {
        uint16_t number = 0;
        duck_expr::Lookup type = resolver ? resolver(atom.c_str(), atom.length(), number, context) : duck_expr::Lookup::Number;
        if (type == duck_expr::Lookup::Undefined) return error(diagnostic, "Undefined variable in legacy condition");
        textual |= type == duck_expr::Lookup::Text;
        if (mode == duck_expr::Mode::Evaluate) {
          if (!duck_vars::expand(atom, atoms[i], diagnostic)) return false;
        } else atoms[i] = "1";
      } else {
        atoms[i] = atom;
        bool numeric = atom[0] >= '0' && atom[0] <= '9';
        if (numeric && !expression(atom, diagnostic)) return false;
        textual |= !numeric && atom != "TRUE" && atom != "FALSE";
      }
    }
    if (textual) {
      // Identity interning is confined to the old text extension. Equality and
      // truth evaluation still run through the sole Stage 3 expression engine.
      if (count == 2) adapted = atoms[0] == atoms[1] ? "1 == 1" : "1 == 2";
      else {
        atoms[0].trim(); atoms[0].toLowerCase();
        adapted = atoms[0].length() && atoms[0] != "0" && atoms[0] != "false" ? "TRUE" : "FALSE";
      }
      source = &adapted;
    }
  }
  duck_expr::Error failure;
  if (duck_expr::evaluate(source->c_str(), source->length(), value, failure, resolver, context, mode)) return true;
  diagnostic = "Expression column " + String(failure.column) + ": " + failure.message;
  return false;
}

bool assignment(const String &args, String &name, String &value, bool &text, String &diagnostic) {
  int eq = args.indexOf('=');
  if (eq < 0 || !variable(trimmed(args.substring(0, eq))))
    return error(diagnostic, "Malformed assignment: invalid variable identifier or missing '='; expected $name = expression or quoted text");
  name = trimmed(args.substring(0, eq));
  value = trimmed(args.substring(eq + 1));
  text = value.startsWith("\"");
  if (text) {
    if (value.length() < 2 || !value.endsWith("\"")) return error(diagnostic, "Unterminated quoted variable value");
    bool escaped = false;
    for (size_t i = 1; i < value.length(); ++i) {
      if (!escaped && value[i] == '"') return i == value.length() - 1 ? true :
        error(diagnostic, "Unexpected characters after quoted text value");
      if (!escaped && value[i] == '\\') escaped = true;
      else escaped = false;
    }
    return error(diagnostic, "Unterminated quoted variable value");
  }
  return expression(value, diagnostic);
}

bool numericArgument(const String &args, uint32_t &value, String &diagnostic,
                     duck_expr::Mode mode, duck_expr::Resolver resolver, void *context) {
  // Intentionally distinct compatibility path: plain decimal timers/counts
  // retain their existing unsigned 32-bit range (and optional leading '+').
  if (number(args, UINT32_MAX)) {
    value = static_cast<uint32_t>(strtoul(args.c_str(), nullptr, 10));
    return true;
  }
  uint16_t numberValue = 0;
  duck_expr::Error failure;
  if (!duck_expr::evaluate(args.c_str(), args.length(), numberValue, failure, resolver, context, mode)) {
    diagnostic = "Expression column " + String(failure.column) + ": " + failure.message;
    return false;
  }
  value = numberValue;
  return true;
}

bool hasKeyword(const String &line, const char *keyword) {
  size_t n = strlen(keyword);
  while (n && space(keyword[n - 1])) --n;
  if (line.length() < n) return false;
  for (size_t i = 0; i < n; ++i)
    if (toupper(static_cast<unsigned char>(line[i])) != toupper(static_cast<unsigned char>(keyword[i]))) return false;
  return line.length() == n || space(line[n]);
}

bool filePayload(const String &args, String &ref, String &payload) {
  size_t offset = 0;
  String token;
  while (offset < args.length()) {
    size_t start = offset;
    if (!word(args, offset, token)) break;
    token.toUpperCase();
    if (token == "STRING" && start > 0 && offset < args.length()) {
      ref = trimmed(args.substring(0, start));
      payload = args.substring(offset + 1);
      return ref.length() > 0;
    }
  }
  return false;
}

bool parse(const String &input, Statement &out, String &diagnostic) {
  out = Statement();
  diagnostic = "";
  if (input.length() > DUCKSCRIPT_MAX_LINE_LEN) return error(diagnostic, "Script line length limit exceeded");
  for (size_t i = 0; i < input.length(); ++i)
    if (!input[i] || input[i] == '\n' || input[i] == '\r') return error(diagnostic, "Expected one statement line without NUL/CR/LF");
  String line = trimmed(input);
  if (!line.length()) return true;
  if (line.startsWith("//")) { out.kind = Kind::Comment; out.line = line; return true; }
  if ((line[0] == '#' || (line[0] >= '0' && line[0] <= '9')) && line.indexOf('=') >= 0)
    return error(diagnostic, "Assignment target must be a mutable $variable; constants cannot be assigned");
  if (line[0] == '$' && line.length() > 1) {
    String name, value; bool text;
    if (!assignment(line, name, value, text, diagnostic)) return false;
    out.kind = Kind::Assignment; out.line = out.args = line;
    return true;
  }
  size_t offset = 0;
  String keyword;
  word(line, offset, keyword);
  keyword.toUpperCase();
  String rawArgs = offset < line.length() ? line.substring(offset + 1) : String();
  out.args = trimmed(rawArgs);
  out.line = keyword + (out.args.length() ? " " + out.args : String());
  if (keyword == "FUNCTION") {
    String identifier;
    if (!script_functions::name(out.args, identifier, diagnostic)) return false;
    out.kind = Kind::Function; out.args = identifier; return true;
  }
  if (keyword == "RETURN") {
    out.kind = Kind::Return;
    return !out.args.length() || expression(out.args, diagnostic);
  }
  if (keyword == "REM") { out.kind = Kind::Comment; return true; }
  if (keyword == "STRING" || keyword == "STRINGLN") {
    out.kind = out.args.length() ? Kind::Command : keyword == "STRING" ? Kind::StringBlock : Kind::StringLnBlock;
    if (out.args.length()) { out.args = rawArgs; out.line = keyword + " " + rawArgs; }
    return true;
  }
  struct Marker { const char *name; Kind kind; };
  static const Marker markers[] = {
    {"END_FUNCTION",Kind::EndFunction},{"REM_BLOCK",Kind::RemBlock},{"END_REM",Kind::EndRem},{"END_STRING",Kind::EndString},
    {"END_STRINGLN",Kind::EndStringLn},{"ENDIF",Kind::EndIf},{"END_IF",Kind::EndIf},
    {"ENDWHILE",Kind::EndWhile},{"END_WHILE",Kind::EndWhile}
  };
  if (keyword == "END") {
    String arg = words(out.args); arg.toUpperCase();
    if (arg == "IF") { out.kind = Kind::EndIf; return true; }
    if (arg == "WHILE") { out.kind = Kind::EndWhile; return true; }
    // END is also a navigation key. Other forms go through exact key validation.
  }
  for (const auto &marker : markers) if (keyword == marker.name) {
    if (out.args.length()) return error(diagnostic, "Block marker takes no arguments");
    out.kind = marker.kind;
    return true;
  }
  if (keyword == "ELSE") {
    if (!out.args.length()) { out.kind = Kind::Else; return true; }
    if (!hasKeyword(out.args, "IF")) return error(diagnostic, "ELSE takes no arguments except canonical ELSE IF condition THEN");
    out.args = trimmed(out.args.substring(2));
    out.kind = Kind::ElseIf;
    return conditionalArgs(out, false, diagnostic);
  }
  if (keyword == "IF") {
    out.kind = Kind::If;
    return conditionalArgs(out, true, diagnostic);
  }
  if (keyword == "WHILE") {
    out.kind = Kind::While;
    // Only the old bare-variable form permits the explicit text truthiness extension.
    out.legacyCondition = variable(out.args);
    return expression(out.args, diagnostic);
  }
  out.kind = Kind::Command;
  if (keyword == "STOP") return out.args.length() ? error(diagnostic, "STOP takes no arguments") : true;
  if (keyword == "VAR" || keyword == "DEFINE") {
    String name, value; bool text;
    if (keyword == "DEFINE" && duck_constants::declaration(input)) {
      if (!duck_constants::definition(input, name, value, diagnostic)) return false;
      out.kind = Kind::Define;
      return true;
    }
    return assignment(out.args, name, value, text, diagnostic);
  }
  if (keyword == "READ") {
    String args = out.args; args.replace("\t", " ");
    int last = args.lastIndexOf(' ');
    storage::Ref ref;
    if (last < 0 || !variable(trimmed(args.substring(last + 1))) ||
        !storage::parseRef(trimmed(args.substring(0, last)), ref)) return error(diagnostic, "Malformed READ: expected file $variable");
    out.line = keyword + " " + args;
    return true;
  }
  if (keyword == "SAVE" || keyword == "APPEND") {
    String file, payload;
    storage::Ref ref;
    if (!filePayload(out.args, file, payload) || !storage::parseRef(file, ref)) return error(diagnostic, "Malformed SAVE/APPEND: expected file STRING payload");
    if (payload.startsWith("\"") != payload.endsWith("\"") || (payload.startsWith("\"") && payload.length() < 2)) return error(diagnostic, "Unterminated quoted file payload");
    out.line = keyword + " " + file + " STRING " + payload;
    return true;
  }
  String args = words(out.args);
  if (keyword == "DELAY" || keyword == "WAIT" || keyword == "DEFAULT_DELAY" || keyword == "DEFAULTDELAY" ||
      keyword == "REPEAT" || keyword == "REPLAY") {
    uint32_t value;
    if (!numericArgument(args, value, diagnostic, duck_expr::Mode::Syntax, nullptr)) return false;
  } else if (keyword == "LOCALE") {
    if (!keyboard_locale::supportsLocale(args)) return error(diagnostic, "Unknown or unsupported LOCALE");
  } else if (keyword == "LED") {
    String upper = args; upper.toUpperCase();
    if (upper != "OFF") {
      size_t at = 0; String token; uint8_t count = 0;
      while (word(args, at, token)) { if (!number(token, 255)) return error(diagnostic, "LED expects OFF or three RGB bytes"); ++count; }
      if (count != 3) return error(diagnostic, "LED expects OFF or three RGB bytes");
    }
  } else if (keyword == "KEYCODE") {
    size_t at = 0; String token; uint8_t count = 0;
    while (word(args, at, token)) { if (!number(token, 255, true) || ++count > 7) return error(diagnostic, "KEYCODE expects a modifier byte and at most six key bytes"); }
    if (!count) return error(diagnostic, "KEYCODE requires a modifier byte");
  } else if (keyword == "ATTACKMODE") {
    size_t at = 0; String token; uint8_t count = 0; bool off = false;
    while (word(args, at, token)) {
      token.toUpperCase(); ++count; off |= token == "OFF";
      if (token != "OFF" && token != "HID" && token != "KEYBOARD" && token != "STORAGE" &&
          token != "MSC" && token != "DISK") return error(diagnostic, "Unsupported ATTACKMODE token");
    }
    if (!count || (off && count != 1)) return error(diagnostic, "ATTACKMODE expects OFF or HID/STORAGE modes");
  } else {
    const int open = line.indexOf('(');
    const String candidate = open >= 0 ? line.substring(0, open) : String();
    const bool invocation = open >= 0 && duck_expr::identifier(candidate.c_str(), candidate.length(), 0) &&
                            !(candidate[0] >= '0' && candidate[0] <= '9');
    if (invocation || line.endsWith("()")) {
      String identifier;
      if (!script_functions::name(line, identifier, diagnostic)) return false;
      out.kind = Kind::Call; out.args = identifier; out.line = line; return true;
    }
    out.kind = Kind::Keys;
    size_t at = 0; String token, keyLine; uint8_t value = 0;
    while (word(line, at, token)) {
      if (token != "-" && token.indexOf('-') >= 0) {
        if (token.startsWith("-") || token.endsWith("-") || token.indexOf("--") >= 0)
          return error(diagnostic, "Empty key in hyphen combination");
        token.replace("-", " ");
      }
      if (keyLine.length()) keyLine += " ";
      keyLine += token;
    }
    at = 0; uint8_t keys[6] = {}, keyCount = 0;
    while (word(keyLine, at, token)) {
      if (duck_keys::isModifierName(token, value)) continue;
      if (hid_backend::keyNameToHid(token, value)) {
        bool duplicate = false;
        for (uint8_t i = 0; i < keyCount; ++i) duplicate |= keys[i] == value;
        if (!duplicate) {
          if (keyCount == 6) return error(diagnostic, "Keyboard combination exceeds six distinct keys");
          keys[keyCount++] = value;
        }
      } else if (character(token)) {
        keyCount = 0; // Literal locale strokes follow a separately released group.
      } else {
        diagnostic = "Unsupported command or key: " + token + "; use STRING for literal text";
        return false;
      }
    }
    out.line = keyLine; // Preserve case of bare literal characters.
    return true;
  }
  out.line = keyword + " " + args;
  return true;
}

bool Lexer::scan(const String &line, uint32_t number, Statement &out, String &diagnostic) {
  out = Statement();
  String text = trimmed(line);
  if (mode == Kind::RemBlock) {
    if (!hasKeyword(text, "END_REM")) return true;
    if (!parse(text, out, diagnostic)) return false;
    mode = Kind::Empty; out.kind = Kind::Empty;
    return true;
  }
  if (mode == Kind::StringBlock || mode == Kind::StringLnBlock) {
    bool endString = hasKeyword(text, "END_STRING"), endStringLn = hasKeyword(text, "END_STRINGLN");
    if (!endString && !endStringLn) {
      // Source formatting is removed before substitution. Expanded text is data,
      // even if it resembles a command or a terminator; never parse it again.
      size_t start = 0;
      if (mode == Kind::StringBlock) {
        while (start < line.length() && space(line[start])) ++start;
      } else if (line[0] == '\t') start = 1;
      out.kind = mode == Kind::StringBlock ? Kind::TextBody : Kind::TextLnBody;
      return duck_constants::expand(line.substring(start), out.args, diagnostic);
    }
    if (!parse(text, out, diagnostic)) return false;
    if ((mode == Kind::StringBlock && !endString) || (mode == Kind::StringLnBlock && !endStringLn))
      return error(diagnostic, "Mismatched STRING/STRINGLN block terminator");
    mode = Kind::Empty; out.kind = Kind::Empty;
    return true;
  }
  String expanded;
  if (hasKeyword(text, "REM") || text.startsWith("//")) return parse(text, out, diagnostic);
  String upper = text; upper.toUpperCase();
  bool delimiter = hasKeyword(text, "REM_BLOCK") || hasKeyword(text, "END_REM") ||
    hasKeyword(text, "END_STRING") || hasKeyword(text, "END_STRINGLN") || upper == "STRING" || upper == "STRINGLN";
  bool rawIf = hasKeyword(text, "IF"), rawElse = hasKeyword(text, "ELSE");
  bool rawWhile = hasKeyword(text, "WHILE");
  bool rawFunction = hasKeyword(text, "FUNCTION") || hasKeyword(text,"END_FUNCTION") || hasKeyword(text,"RETURN");
  String callName, callError;
  bool rawCall = text.endsWith("()") && script_functions::name(text,callName,callError);
  String endArgs = words(text.substring(3)); endArgs.toUpperCase();
  bool rawEnd = hasKeyword(text, "END_IF") || hasKeyword(text, "ENDIF") ||
    (hasKeyword(text, "END") && (endArgs == "IF" || endArgs == "WHILE")) ||
    hasKeyword(text, "END_WHILE") || hasKeyword(text, "ENDWHILE");
  if (rawIf || rawElse) {
    size_t offset = rawIf ? 2 : 4;
    while (offset < text.length() && space(text[offset])) ++offset;
    if (rawElse && hasKeyword(text.substring(offset), "IF")) {
      offset += 2;
      while (offset < text.length() && space(text[offset])) ++offset;
    } else if (rawElse) offset = text.length();
    size_t suffix = text.length();
    while (suffix > offset && !space(text[suffix - 1])) --suffix;
    String last = text.substring(suffix); last.toUpperCase();
    bool then = last == "THEN";
    String args;
    if (!duck_constants::expand(text.substring(offset, then ? suffix : text.length()), args, diagnostic)) return false;
    if (!then) {
      String tail = trimmed(args); size_t lastAt = tail.length();
      while (lastAt && !space(tail[lastAt - 1])) --lastAt;
      String lastWord = tail.substring(lastAt); lastWord.toUpperCase();
      if (lastWord == "THEN") return error(diagnostic, "DEFINE expansion cannot create conditional THEN delimiter");
    }
    expanded = text.substring(0, offset) + args + (then ? text.substring(suffix) : String());
    if (expanded.length() > DUCKSCRIPT_MAX_EXPANDED_LINE) return error(diagnostic, "DEFINE expansion length limit exceeded");
  } else if (rawWhile) {
    String args;
    if (!duck_constants::expand(text.substring(5), args, diagnostic)) return false;
    expanded = text.substring(0, 5) + args;
    if (expanded.length() > DUCKSCRIPT_MAX_EXPANDED_LINE) return error(diagnostic, "DEFINE expansion length limit exceeded");
  } else if (hasKeyword(text,"RETURN") && text.length()>6) {
    String args; if(!duck_constants::expand(text.substring(6),args,diagnostic))return false;
    expanded=text.substring(0,6)+args;
  } else if (delimiter || rawEnd || rawFunction || rawCall) expanded = text;
  else if (!duck_constants::expand(text, expanded, diagnostic)) return false;
  if (!parse(hasKeyword(text, "DEFINE") ? line : expanded, out, diagnostic)) return false;
  if (!rawIf && !rawElse && !rawEnd &&
      (out.kind == Kind::If || out.kind == Kind::ElseIf || out.kind == Kind::Else || out.kind == Kind::EndIf))
    return error(diagnostic, "DEFINE expansion cannot create conditional block delimiters");
  if (!rawFunction && (out.kind==Kind::Function || out.kind==Kind::EndFunction || out.kind==Kind::Return))
    return error(diagnostic,"DEFINE expansion cannot create function/RETURN delimiters");
  if (!rawCall && out.kind==Kind::Call) return error(diagnostic,"DEFINE expansion cannot create function invocation");
  if (!rawWhile && !rawEnd && (out.kind == Kind::While || out.kind == Kind::EndWhile))
    return error(diagnostic, "DEFINE expansion cannot create WHILE block delimiters");
  if (expanded != text && (hasKeyword(expanded, "DEFINE") || out.kind == Kind::RemBlock || out.kind == Kind::EndRem ||
      out.kind == Kind::StringBlock || out.kind == Kind::StringLnBlock || out.kind == Kind::EndString || out.kind == Kind::EndStringLn))
    return error(diagnostic, "DEFINE expansion cannot create DEFINE or comment/text block delimiters");
  if (out.kind == Kind::EndRem || out.kind == Kind::EndString || out.kind == Kind::EndStringLn)
    return error(diagnostic, "Unmatched comment/text block terminator");
  if (out.kind == Kind::RemBlock || out.kind == Kind::StringBlock || out.kind == Kind::StringLnBlock) {
    mode = out.kind; openingLine = number;
  }
  return true;
}

bool Lexer::finish(String &diagnostic, uint32_t &number) const {
  if (mode == Kind::Empty) return true;
  number = openingLine;
  return error(diagnostic, mode == Kind::RemBlock ? "Unterminated REM_BLOCK" :
    mode == Kind::StringBlock ? "Unterminated STRING block" : "Unterminated STRINGLN block");
}

bool Validator::accept(const String &line, uint32_t number, String &diagnostic) {
  Statement stmt;
  if (!lexer.scan(line, number, stmt, diagnostic)) return false;
  if(stmt.kind==Kind::Function) {
    if(inFunction || depth)return error(diagnostic,"FUNCTION declarations must be top level, not nested");
    inFunction=true;functionLine=number;return true;
  }
  if(stmt.kind==Kind::EndFunction) {
    if(!inFunction)return error(diagnostic,"Unmatched END_FUNCTION");
    if(depth)return error(diagnostic,"Mismatched function/control-flow terminator");
    inFunction=false;return true;
  }
  duck_vars::Symbols &activeSymbols=inFunction && globals ? *globals : symbols;
  if(stmt.kind==Kind::Call) {
    return expression(stmt.args+"()",diagnostic);
  }
  if(stmt.kind==Kind::Return) {
    if(!inFunction && stmt.args.length())return error(diagnostic,"RETURN value requires a function; bare top-level RETURN remains Enter");
    return !stmt.args.length() || expression(stmt.args,diagnostic,duck_vars::Symbols::resolve,&activeSymbols);
  }
  if (stmt.kind == Kind::Assignment || (stmt.kind == Kind::Command &&
      (hasKeyword(stmt.line, "VAR") || hasKeyword(stmt.line, "DEFINE")))) {
    String name, value; bool text;
    if (!assignment(stmt.args, name, value, text, diagnostic)) return false;
    if (!text && !expression(value, diagnostic, duck_vars::Symbols::resolve, &activeSymbols)) return false;
    if (activeSymbols.declare(name, text ? duck_vars::Type::Text : duck_vars::Type::Numeric,
                        stmt.kind == Kind::Assignment, diagnostic) < 0) return false;
    if(inFunction && stmt.kind!=Kind::Assignment && symbols.declare(name,text ? duck_vars::Type::Text : duck_vars::Type::Numeric,false,diagnostic)<0)return false;
  } else if (stmt.kind == Kind::Command && hasKeyword(stmt.line, "READ")) {
    String args = stmt.args; args.replace("\t", " ");
    String name = trimmed(args.substring(args.lastIndexOf(' ') + 1));
    if (activeSymbols.declare(name, duck_vars::Type::Text, false, diagnostic) < 0) return false;
    if(inFunction && symbols.declare(name,duck_vars::Type::Text,false,diagnostic)<0)return false;
  } else if (stmt.kind == Kind::Command && (hasKeyword(stmt.line, "DELAY") || hasKeyword(stmt.line, "WAIT") ||
      hasKeyword(stmt.line, "DEFAULT_DELAY") || hasKeyword(stmt.line, "DEFAULTDELAY") ||
      hasKeyword(stmt.line, "REPEAT") || hasKeyword(stmt.line, "REPLAY"))) {
    uint32_t value;
    if (!numericArgument(stmt.args, value, diagnostic, duck_expr::Mode::Syntax, duck_vars::Symbols::resolve, &activeSymbols)) return false;
  }
  if (stmt.kind == Kind::If || stmt.kind == Kind::ElseIf || stmt.kind == Kind::While) {
    uint16_t value;
    if (!condition(stmt.args, stmt.legacyCondition, value, diagnostic, duck_expr::Mode::Syntax,
                   duck_vars::Symbols::resolve, &activeSymbols)) return false;
  }
  // Text uses the lexer's single literal mode, not a control-stack frame.
  // Opening it at the exact IF/WHILE depth limit therefore needs no extra slot.
  if (stmt.kind == Kind::If || stmt.kind == Kind::While) {
    if (depth >= DUCKSCRIPT_MAX_BLOCK_DEPTH) return error(diagnostic, "Block nesting limit exceeded");
    stack[depth++] = {stmt.kind, number, false};
  } else if (stmt.kind == Kind::Else || stmt.kind == Kind::ElseIf) {
    if (!depth || stack[depth - 1].kind != Kind::If || stack[depth - 1].sawElse) return error(diagnostic, "Unmatched or duplicate ELSE");
    stack[depth - 1].sawElse = stmt.kind == Kind::Else;
  } else if (stmt.kind == Kind::EndIf || stmt.kind == Kind::EndWhile) {
    Kind expected = stmt.kind == Kind::EndIf ? Kind::If : Kind::While;
    if (!depth) return error(diagnostic, "Unmatched control-flow terminator");
    if (stack[depth - 1].kind != expected) return error(diagnostic, "Mismatched IF/WHILE block terminator");
    --depth;
  }
  return true;
}

bool Validator::finish(String &diagnostic, uint32_t &number) const {
  if (!lexer.finish(diagnostic, number)) return false;
  if(inFunction) {number=functionLine;return error(diagnostic,"Unterminated FUNCTION");}
  if (depth) { number = stack[depth - 1].line; return error(diagnostic, "Unterminated IF/WHILE block"); }
  return true;
}
}
