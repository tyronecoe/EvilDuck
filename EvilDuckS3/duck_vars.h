#pragma once
#include <Arduino.h>
#include "duck_expr.h"

namespace duck_vars {
  enum class Type : uint8_t { Missing, Numeric, Text };
  class Symbols {
    struct Symbol { char name[DUCKSCRIPT_MAX_IDENTIFIER_LEN + 1] = {}; Type type = Type::Missing; };
    Symbol entries[DUCKSCRIPT_MAX_VARIABLES] = {};
    uint8_t count = 0;
  public:
    void clear() { count = 0; }
    int index(const char *name, size_t length) const;
    Type type(const char *name, size_t length) const;
    int declare(const String &name, Type type, bool mustExist, String &error);
    static duck_expr::Lookup resolve(const char *, size_t, uint16_t &, void *);
  };
  void clear();
  uint32_t revision(); // Changes only when a runtime symbol is created or its value changes.
  bool assign(const String &name, const String &expression, bool declaration, String &error);
  bool setText(const String &name, const String &value, bool declaration, String &error);
  duck_expr::Lookup resolve(const char *, size_t, uint16_t &, void *);
  bool getNumeric(const String &name, uint16_t &value);
  bool set(const String &name, const String &value);
  bool get(const String &name, String &out);
  bool expand(const String &input, String &output, String &error);
  String expand(const String &input);
  bool truthy(const String &name);
}
