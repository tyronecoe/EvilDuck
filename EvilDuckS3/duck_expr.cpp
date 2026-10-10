#include "duck_expr.h"
#include <string.h>

namespace duck_expr {
namespace {
bool word(char c) { return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') ||
  (c >= '0' && c <= '9') || c == '_'; }
bool space(char c) { return c == ' ' || c == '\t'; }
enum class Op : uint8_t { None, Or, And, BitOr, BitAnd, Eq, Ne, Lt, Le, Gt, Ge,
  Left, Right, Add, Sub, Mul, Div, Mod, Pow };
struct Operator { Op op = Op::None; uint8_t precedence = 0, bytes = 0; };
struct Value { uint16_t number = 0; bool known = true; };

class Parser {
  const char *source;
  size_t length, position = 0;
  uint16_t tokens = 0;
  Error &error;
  Resolver resolver;
  void *context;
  Mode mode;
  bool fail(const char *message, size_t at) {
    if (!error.message) { error.message = message; error.column = at + 1; }
    return false;
  }
  void spaces() { while (position < length && space(source[position])) ++position; }
  bool token() {
    return ++tokens <= DUCKSCRIPT_MAX_EXPR_TOKENS || fail("Expression token limit exceeded", position);
  }
  Operator operation() {
    spaces();
    if (position >= length) return {};
    char a = source[position], b = position + 1 < length ? source[position + 1] : 0;
    if (a == '|' && b == '|') return {Op::Or,1,2};
    if (a == '&' && b == '&') return {Op::And,2,2};
    if (a == '=' && b == '=') return {Op::Eq,5,2};
    if (a == '!' && b == '=') return {Op::Ne,5,2};
    if (a == '<' && b == '=') return {Op::Le,6,2};
    if (a == '>' && b == '=') return {Op::Ge,6,2};
    if (a == '<' && b == '<') return {Op::Left,7,2};
    if (a == '>' && b == '>') return {Op::Right,7,2};
    switch (a) {
      case '|': return {Op::BitOr,3,1}; case '&': return {Op::BitAnd,4,1};
      case '<': return {Op::Lt,6,1}; case '>': return {Op::Gt,6,1};
      case '+': return {Op::Add,8,1}; case '-': return {Op::Sub,8,1};
      case '*': return {Op::Mul,9,1}; case '/': return {Op::Div,9,1};
      case '%': return {Op::Mod,9,1}; case '^': return {Op::Pow,10,1};
      default: return {};
    }
  }
  bool primary(Value &out, uint8_t depth) {
    spaces();
    size_t start = position;
    if (start >= length) return fail("Expected expression operand", start);
    if (!token()) return false;
    char c = source[position];
    if (c == '(') {
      ++position;
      if (!expression(1, depth + 1, out)) return false;
      spaces();
      if (position >= length || source[position] != ')') return fail("Missing closing parenthesis", position);
      ++position;
      return token();
    }
    if (c == '$') {
      ++position;
      while (position < length && word(source[position])) ++position;
      size_t count = position - start;
      if (!identifier(source + start, count)) return fail("Invalid variable identifier", start);
      uint16_t number = 0;
      Lookup found = resolver ? resolver(source + start, count, number, context) : Lookup::Undefined;
      if (resolver || mode == Mode::Evaluate) {
        if (found == Lookup::Undefined) return fail("Undefined numeric variable", start);
        if (found == Lookup::Text) return fail("Text variable cannot be used in a numeric expression", start);
      }
      out = {number, mode == Mode::Evaluate};
      return true;
    }
    if (c >= '0' && c <= '9') {
      unsigned base = 10;
      if (c == '0' && position + 1 < length && (source[position + 1] == 'x' || source[position + 1] == 'X')) {
        base = 16; position += 2;
      }
      size_t digits = position;
      uint32_t number = 0;
      while (position < length && word(source[position])) {
        char digitChar = source[position++];
        unsigned digit = digitChar >= '0' && digitChar <= '9' ? digitChar - '0' :
          digitChar >= 'a' && digitChar <= 'f' ? digitChar - 'a' + 10 :
          digitChar >= 'A' && digitChar <= 'F' ? digitChar - 'A' + 10 : 255;
        if (digit >= base) return fail("Invalid numeric literal", start);
        if (number > (65535U - digit) / base) return fail("Numeric literal exceeds 65535", start);
        number = number * base + digit;
      }
      if (position == digits) return fail("Missing hexadecimal digits", start);
      out = {static_cast<uint16_t>(number), true};
      return true;
    }
    if (word(c)) {
      while (position < length && word(source[position])) ++position;
      size_t count = position - start;
      if (count == 4 && memcmp(source + start, "TRUE", 4) == 0) { out = {1,true}; return true; }
      if (count == 5 && memcmp(source + start, "FALSE", 5) == 0) { out = {0,true}; return true; }
      return fail("Expected number, TRUE/FALSE or $variable", start);
    }
    return fail(c == '#' ? "Undefined or unexpanded constant in expression" :
                "Unsupported operator or missing operand", start);
  }
  bool apply(Op op, Value &left, const Value &right, size_t at) {
    if ((op == Op::Div || op == Op::Mod) && right.known && !right.number)
      return fail("Division/modulo by zero", at);
    if ((op == Op::Left || op == Op::Right) && right.known && right.number >= 16)
      return fail("Shift count must be between 0 and 15", at);
    if (!left.known || !right.known) { left = {0,false}; return true; }
    uint32_t a = left.number, b = right.number, result = 0;
    switch (op) {
      case Op::Add: result = a + b; break;
      case Op::Sub: result = a + 65536U - b; break;
      case Op::Mul: result = a * b; break;
      case Op::Div: result = a / b; break;
      case Op::Mod: result = a % b; break;
      case Op::Left: result = a << b; break;
      case Op::Right: result = a >> b; break;
      case Op::Pow:
        result = 1;
        while (b) {
          if (b & 1) result = (result * a) & 65535U;
          b >>= 1;
          a = (a * a) & 65535U;
        }
        break;
      case Op::Eq: result = a == b; break; case Op::Ne: result = a != b; break;
      case Op::Lt: result = a < b; break; case Op::Le: result = a <= b; break;
      case Op::Gt: result = a > b; break; case Op::Ge: result = a >= b; break;
      case Op::And: result = a && b; break; case Op::Or: result = a || b; break;
      case Op::BitAnd: result = a & b; break; case Op::BitOr: result = a | b; break;
      default: return fail("Invalid expression operator", at);
    }
    left = {static_cast<uint16_t>(result),true};
    return true;
  }
  bool expression(uint8_t minimum, uint8_t depth, Value &out) {
    if (depth > DUCKSCRIPT_MAX_EXPR_DEPTH) return fail("Expression nesting limit exceeded", position);
    if (!primary(out, depth)) return false;
    for (;;) {
      Operator op = operation();
      if (!op.bytes || op.precedence < minimum) return true;
      size_t at = position;
      position += op.bytes;
      if (!token()) return false;
      Value right;
      if (!expression(op.precedence + (op.op == Op::Pow ? 0 : 1), depth + 1, right) ||
          !apply(op.op, out, right, at)) return false;
    }
  }
public:
  Parser(const char *s, size_t n, Error &e, Resolver r, void *ctx, Mode m) :
    source(s), length(n), error(e), resolver(r), context(ctx), mode(m) {}
  bool run(uint16_t &value) {
    Value result;
    if (!expression(1, 0, result)) return false;
    spaces();
    if (position != length) return fail("Unexpected token or extra parenthesis", position);
    value = result.number;
    return true;
  }
};
}

bool identifier(const char *name, size_t length, char sigil) {
  size_t start = sigil ? 1 : 0;
  if (length <= start || length > DUCKSCRIPT_MAX_IDENTIFIER_LEN || (sigil && name[0] != sigil)) return false;
  for (size_t i = start; i < length; ++i) if (!word(name[i])) return false;
  return true;
}

bool evaluate(const char *source, size_t length, uint16_t &value, Error &error,
              Resolver resolver, void *context, Mode mode) {
  static_assert(DUCKSCRIPT_MAX_EXPR_DEPTH < 128 && DUCKSCRIPT_MAX_EXPR_TOKENS < 65535,
                "Expression limits must fit bounded counters");
  error = Error();
  if (length > DUCKSCRIPT_MAX_EXPR_BYTES) { error = {"Expression byte limit exceeded",1}; return false; }
  return Parser(source, length, error, resolver, context, mode).run(value);
}
}
