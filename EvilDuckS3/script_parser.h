#pragma once
#include <Arduino.h>
#include "config.h"
#include "duck_vars.h"

namespace script_parser {
static_assert(DUCKSCRIPT_MAX_BLOCK_DEPTH > 0 && DUCKSCRIPT_MAX_BLOCK_DEPTH < 256, "Invalid block depth limit");
enum class Kind : uint8_t {
  Empty, Comment, Keys, Command, Assignment, Define, If, ElseIf, Else, EndIf, While, EndWhile,
  Function, EndFunction, Call, Return, RemBlock, EndRem, StringBlock, StringLnBlock, EndString, EndStringLn,
  TextBody, TextLnBody
};
struct Statement { Kind kind = Kind::Empty; String line, args; bool legacyCondition = false; };
bool hasKeyword(const String &line, const char *keyword);
bool parse(const String &line, Statement &out, String &error);
bool condition(const String &input, bool legacy, uint16_t &value, String &error,
               duck_expr::Mode mode = duck_expr::Mode::Evaluate,
               duck_expr::Resolver resolver = duck_vars::resolve, void *context = nullptr);
bool filePayload(const String &args, String &ref, String &payload);
bool assignment(const String &args, String &name, String &value, bool &text, String &error);
bool expression(const String &input, String &error, duck_expr::Resolver resolver = nullptr, void *context = nullptr);
bool numericArgument(const String &args, uint32_t &value, String &error,
                     duck_expr::Mode mode = duck_expr::Mode::Evaluate,
                     duck_expr::Resolver resolver = duck_vars::resolve, void *context = nullptr);

class Lexer {
  Kind mode = Kind::Empty;
  uint32_t openingLine = 0;
public:
  bool scan(const String &line, uint32_t number, Statement &out, String &error);
  bool finish(String &error, uint32_t &number) const;
};

class Validator {
  struct Frame { Kind kind; uint32_t line; bool sawElse; };
  Frame stack[DUCKSCRIPT_MAX_BLOCK_DEPTH] = {};
  uint8_t depth = 0;
  Lexer lexer;
  duck_vars::Symbols symbols;
  duck_vars::Symbols *globals = nullptr;
  bool inFunction = false;
  uint32_t functionLine = 0;
public:
  void functionSymbols(duck_vars::Symbols *table) { globals = table; }
  bool accept(const String &line, uint32_t number, String &error);
  bool finish(String &error, uint32_t &number) const;
};
}
