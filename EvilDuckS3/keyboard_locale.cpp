#include "keyboard_locale.h"
#include "hid_backend.h"
#include "locale/locales.h"
#include <pgmspace.h>

static hid_locale_t *activeLocale = &locale_us;

namespace keyboard_locale {

void begin() {
  activeLocale = &locale_us;
}

void setLocale(hid_locale_t *locale) {
  if (locale) activeLocale = locale;
}

hid_locale_t *getLocale() {
  return activeLocale;
}

static bool nameEq(const String &a, const char *b) {
  String x = a;
  x.toUpperCase();
  return x == b;
}

static hid_locale_t *findLocale(const String &name) {
  if (nameEq(name, "US")) { return &locale_us; }
  if (nameEq(name, "DE")) { return &locale_de; }
#if defined(HAS_LOCALE_GB)
  if (nameEq(name, "GB")) { return &locale_gb; }
#endif
#if defined(HAS_LOCALE_ES)
  if (nameEq(name, "ES")) { return &locale_es; }
#endif
#if defined(HAS_LOCALE_FR)
  if (nameEq(name, "FR")) { return &locale_fr; }
#endif
#if defined(HAS_LOCALE_RU)
  if (nameEq(name, "RU")) { return &locale_ru; }
#endif
  return nullptr;
}

bool supportsLocale(const String &name) { return findLocale(name) != nullptr; }
bool setLocaleByName(const String &name) {
  auto locale = findLocale(name);
  if (!locale) return false;
  setLocale(locale);
  return true;
}

size_t translate(const char *text, size_t remaining, Stroke (&strokes)[2], uint8_t &count) {
  count = 0;
  if (!remaining) return 0;
  const uint8_t *b = reinterpret_cast<const uint8_t *>(text);
  for (size_t i = 0; i < activeLocale->combinations_len; ++i) {
    uint8_t res = 0;
    for (uint8_t j = 0; j < 4; ++j) {
      uint8_t keyCode = pgm_read_byte(activeLocale->combinations + (i * 8) + j);
      if (keyCode == 0) break;
      if (j < remaining && keyCode == b[j]) ++res;
      else { res = 0; break; }
    }
    if (res > 0) {
      uint8_t m1 = pgm_read_byte(activeLocale->combinations + (i * 8) + 4);
      uint8_t k1 = pgm_read_byte(activeLocale->combinations + (i * 8) + 5);
      uint8_t m2 = pgm_read_byte(activeLocale->combinations + (i * 8) + 6);
      uint8_t k2 = pgm_read_byte(activeLocale->combinations + (i * 8) + 7);
      if (k1) strokes[count++] = {m1, k1};
      if (k2) strokes[count++] = {m2, k2};
      return res;
    }
  }

  if (b[0] < activeLocale->ascii_len) {
    uint8_t mod = pgm_read_byte(activeLocale->ascii + (b[0] * 2));
    uint8_t key = pgm_read_byte(activeLocale->ascii + (b[0] * 2) + 1);
    if (key != 0) {
      strokes[count++] = {mod, key};
    }
    return 1;
  }

  for (size_t i = 0; i < activeLocale->utf8_len; ++i) {
    uint8_t res = 0;
    for (uint8_t j = 0; j < 4; ++j) {
      uint8_t keyCode = pgm_read_byte(activeLocale->utf8 + (i * 6) + j);
      if (keyCode == 0) break;
      if (j < remaining && keyCode == b[j]) ++res;
      else { res = 0; break; }
    }
    if (res > 0) {
      uint8_t mod = pgm_read_byte(activeLocale->utf8 + (i * 6) + 4);
      uint8_t key = pgm_read_byte(activeLocale->utf8 + (i * 6) + 5);
      if (key) strokes[count++] = {mod, key};
      return res;
    }
  }
  return 1;
}

void write(const char *str, size_t len) {
  for (size_t i = 0; i < len; ) {
    Stroke strokes[2];
    uint8_t count;
    i += translate(str + i, len - i, strokes, count);
    for (uint8_t j = 0; j < count; ++j) {
      hid_backend::pressKeycode(strokes[j].key, strokes[j].modifiers);
    }
  }
}

void write(const String &text) {
  write(text.c_str(), text.length());
}

}
