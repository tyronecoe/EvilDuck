#pragma once
#include <Arduino.h>
#include "config.h"

namespace duck_constants {
void clear();
bool declaration(const String &line); // Canonical DEFINE only, not DEFINE $name.
bool definition(const String &line, String &label, String &value, String &error);
bool define(const String &line, uint32_t number, String &error);
bool expand(const String &line, String &output, String &error);
class Collector {
  enum class Mode : uint8_t { Normal, Rem, Text };
  Mode mode = Mode::Normal;
public:
  bool accept(const String &line, uint32_t number, String &error);
};
}
