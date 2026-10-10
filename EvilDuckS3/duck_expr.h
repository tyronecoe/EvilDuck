#pragma once
#include <stddef.h>
#include <stdint.h>
#include "config.h"

namespace duck_expr {
enum class Lookup : uint8_t { Number, Undefined, Text };
enum class Mode : uint8_t { Evaluate, Syntax };
using Resolver = Lookup (*)(const char *, size_t, uint16_t &, void *);
struct Error { const char *message = nullptr; uint16_t column = 0; };
// No allocations or retained program. Syntax mode checks known subexpressions
// but treats all resolved variable values as unknown, without executing them.
bool evaluate(const char *source, size_t length, uint16_t &value, Error &error,
              Resolver resolver = nullptr, void *context = nullptr,
              Mode mode = Mode::Evaluate);
bool identifier(const char *name, size_t length, char sigil = '$');
}
