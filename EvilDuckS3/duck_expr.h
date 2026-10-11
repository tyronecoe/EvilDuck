#pragma once
#include <stddef.h>
#include <stdint.h>
#include "config.h"

namespace duck_expr {
enum class Lookup : uint8_t { Number, Undefined, Text, Unsupported, Unavailable, RandomError };
enum class Mode : uint8_t { Evaluate, Syntax };
using Resolver = Lookup (*)(const char *, size_t, uint16_t &, void *);
struct Error { const char *message = nullptr; uint16_t column = 0; };
// No allocations or retained program. Syntax mode checks known subexpressions
// but treats all resolved variable values as unknown, without executing them.
bool evaluate(const char *source, size_t length, uint16_t &value, Error &error,
              Resolver resolver = nullptr, void *context = nullptr,
              Mode mode = Mode::Evaluate);
// Function registry returns the bounded function index through value. Evaluation
// executes calls via Program::step; synchronous evaluate never executes a body.
void functions(Resolver resolver, void *context = nullptr);
bool containsCalls(const char *source, size_t length);
struct Instruction { uint16_t value = 0; uint8_t op = 0, length = 0; };
enum class Step : uint8_t { Yield, Call, Done, Error };
class Program {
  Instruction code[DUCKSCRIPT_MAX_EXPR_TOKENS] = {};
  char source[DUCKSCRIPT_MAX_EXPR_BYTES + 1] = {};
  uint16_t values[DUCKSCRIPT_MAX_EXPR_TOKENS / 2 + 1] = {};
  uint16_t count = 0, pc = 0, depth = 0;
public:
  bool compile(const char *, size_t, Error &, Resolver = nullptr, void * = nullptr);
  bool emit(uint8_t op, uint16_t value = 0, uint8_t length = 0);
  Step step(uint16_t &value, Error &, Resolver, void *, uint16_t budget = DUCKSCRIPT_EXPR_BUDGET);
  bool returned(uint16_t value);
};
bool identifier(const char *name, size_t length, char sigil = '$');
}
