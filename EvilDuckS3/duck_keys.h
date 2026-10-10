#pragma once

#include <Arduino.h>

namespace duck_keys {
  struct Cursor {
    size_t offset = 0;
    uint8_t modifiers = 0;
    uint8_t keys[6] = {};
    uint8_t count = 0;
  };
  enum class Item { Done, Yield, Report, Text };
  // Preserve legacy token/group semantics while advancing in bounded chunks.
  Item next(const String &line, Cursor &cursor, uint8_t &modifiers,
            uint8_t (&keys)[6], uint8_t &count, String &text);
  bool isModifierName(const String &token, uint8_t &modMask);
  bool tokenToHid(const String &token, uint8_t &hidCode);
  void pressLineTokens(const String &line);
}
