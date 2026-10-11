#include "duck_expr.h"
#include "internal_vars.h"
#include <string.h>

namespace duck_expr {
namespace {
bool word(char c) { return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') ||
  (c >= '0' && c <= '9') || c == '_'; }
bool space(char c) { return c == ' ' || c == '\t'; }
Resolver functionResolver = nullptr;
void *functionContext = nullptr;
enum class Op : uint8_t { Literal, Variable, Function, None, Or, And, BitOr, BitAnd, Eq, Ne, Lt, Le, Gt, Ge,
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
  Program *program;
  bool emit(Op op, uint16_t value = 0, uint8_t length = 0) {
    return !program || program->emit(static_cast<uint8_t>(op), value, length) || fail("Expression instruction limit exceeded", position);
  }
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
      Lookup found = mode==Mode::Syntax && internal_vars::reserved(source+start,count) ?
        internal_vars::resolve(source+start,count,number,true) :
        resolver ? resolver(source + start, count, number, context) : Lookup::Undefined;
      if (resolver || mode == Mode::Evaluate) {
        if (found == Lookup::RandomError) return fail("Random generation failed: reversed range or source rejection limit", start);
        if (found == Lookup::Unsupported) return fail("Unsupported internal variable", start);
        if (found == Lookup::Unavailable) return fail("Internal variable state unknown in this USB session", start);
        if (found == Lookup::Undefined) return fail("Undefined numeric variable", start);
        if (found == Lookup::Text) return fail("Text variable cannot be used in a numeric expression", start);
      }
      out = {number, mode == Mode::Evaluate};
      return emit(Op::Variable, start, count);
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
      return emit(Op::Literal, number);
    }
    if (word(c)) {
      while (position < length && word(source[position])) ++position;
      size_t count = position - start;
      if (position < length && source[position] == '(') {
        if ((source[start] >= '0' && source[start] <= '9') || !identifier(source + start, count, 0))
          return fail("Invalid function identifier", start);
        if (position + 1 >= length || source[position + 1] != ')')
          return fail("Function arguments are unsupported; use global variables and ()", position);
        position += 2;
        if (!token() || !token()) return false;
        uint16_t index = 0;
        Lookup found = functionResolver ? functionResolver(source + start, count, index, functionContext) : Lookup::Number;
        if (found != Lookup::Number) return fail("Undefined function", start);
        if (mode == Mode::Evaluate) return fail("Function calls require cooperative script execution", start);
        out = {0, false}; return emit(Op::Function, index);
      }
      if (count == 4 && memcmp(source + start, "TRUE", 4) == 0) { out = {1,true}; return emit(Op::Literal, 1); }
      if (count == 5 && memcmp(source + start, "FALSE", 5) == 0) { out = {0,true}; return emit(Op::Literal, 0); }
      return fail("Expected number, TRUE/FALSE or $variable", start);
    }
    return fail(c == '#' ? "Undefined or unexpanded constant in expression" :
                "Unsupported operator or missing operand", start);
  }
public:
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
          !apply(op.op, out, right, at) || !emit(op.op, at)) return false;
    }
  }
public:
  Parser(const char *s, size_t n, Error &e, Resolver r, void *ctx, Mode m, Program *p = nullptr) :
    source(s), length(n), error(e), resolver(r), context(ctx), mode(m), program(p) {}
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

void functions(Resolver resolver, void *context) { functionResolver = resolver; functionContext = context; }
bool containsCalls(const char *s, size_t length) {
  for (size_t i = 0; i < length;) {
    if (s[i] == '$') { ++i; while (i < length && word(s[i])) ++i; continue; }
    if ((s[i] >= 'A' && s[i] <= 'Z') || (s[i] >= 'a' && s[i] <= 'z') || s[i] == '_') {
      while (i < length && word(s[i])) ++i;
      if (i < length && s[i] == '(') return true;
    } else ++i;
  }
  return false;
}
bool Program::emit(uint8_t op, uint16_t value, uint8_t length) {
  if (count >= DUCKSCRIPT_MAX_EXPR_TOKENS) return false;
  code[count++] = {value, op, length}; return true;
}
bool Program::compile(const char *text, size_t length, Error &error, Resolver resolver, void *context) {
  count = pc = depth = 0; error = Error();
  if (length > DUCKSCRIPT_MAX_EXPR_BYTES) { error = {"Expression byte limit exceeded",1}; return false; }
  memcpy(source, text, length); source[length] = 0;
  uint16_t ignored;
  bool ok=Parser(source, length, error, resolver, context, Mode::Syntax, this).run(ignored);
  if(!ok)count=pc=depth=0;
  return ok;
}
bool Program::returned(uint16_t value) {
  if (pc >= count || static_cast<Op>(code[pc].op) != Op::Function || depth >= sizeof(values)/sizeof(values[0])) return false;
  values[depth++] = value; ++pc; return true;
}
Step Program::step(uint16_t &value, Error &error, Resolver resolver, void *context, uint16_t budget) {
  error = Error();
  while (pc < count && budget--) {
    const auto instruction = code[pc]; Op op = static_cast<Op>(instruction.op);
    if (op == Op::Function) { value = instruction.value; return Step::Call; }
    if (op == Op::Literal || op == Op::Variable) {
      uint16_t number = instruction.value;
      if (op == Op::Variable) {
        Lookup found = resolver ? resolver(source + instruction.value, instruction.length, number, context) : Lookup::Undefined;
        if (found != Lookup::Number) { error = {found == Lookup::RandomError ? "Random generation failed: reversed range or source rejection limit" : found == Lookup::Unsupported ? "Unsupported internal variable" : found == Lookup::Unavailable ? "Internal variable state unknown in this USB session" : found == Lookup::Text ? "Text variable cannot be used in numeric expression" : "Undefined numeric variable", uint16_t(instruction.value+1)}; return Step::Error; }
      }
      if (depth >= sizeof(values)/sizeof(values[0])) { error = {"Expression operand stack exhausted",1}; return Step::Error; }
      values[depth++] = number;
    } else {
      if (depth < 2) { error = {"Invalid expression operand stack",1}; return Step::Error; }
      Value left = {values[depth-2],true}, right = {values[depth-1],true};
      Parser arithmetic(source, strlen(source), error, nullptr, nullptr, Mode::Evaluate);
      if (!arithmetic.apply(op, left, right, instruction.value)) return Step::Error;
      --depth; values[depth-1] = left.number;
    }
    ++pc;
  }
  if (pc < count) return Step::Yield;
  if (depth != 1) { error = {"Invalid expression result stack",1}; return Step::Error; }
  value = values[0]; return Step::Done;
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
