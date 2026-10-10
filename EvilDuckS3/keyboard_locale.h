#pragma once

#include <Arduino.h>
#include "locale/locale_types.h"

namespace keyboard_locale {
  struct Stroke { uint8_t modifiers; uint8_t key; };
  // Translate at most one character, without emitting HID. Dead keys may
  // produce two strokes. Unsupported characters retain the legacy skip policy.
  size_t translate(const char *text, size_t remaining, Stroke (&strokes)[2], uint8_t &count);
  void begin();
  void setLocale(hid_locale_t *locale);
  hid_locale_t *getLocale();
  bool supportsLocale(const String &name);
  bool setLocaleByName(const String &name);
  void write(const char *str, size_t len);
  void write(const String &text);
}
