#pragma once
#include <Arduino.h>
#include "script_parser.h"
#include "config.h"

namespace duck_constants {
void clear();
bool boolean(const String &label, bool &value, String &error);
bool declaration(const String &line); // Canonical DEFINE only, not DEFINE $name.
bool definition(const String &line, String &label, String &value, String &error);
bool define(const String &line, uint32_t number, String &error);
bool expand(const String &line, String &output, String &error);
class Collector {
  script_parser::RawBlocks blocks;
public:
  bool accept(const String &line, uint32_t number, String &error);
};
}
