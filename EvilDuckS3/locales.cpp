#include <Arduino.h>
#include "locale/locale_us.h"
#include "locale/locale_de.h"

hid_locale_t locale_us = {
  (uint8_t *)ascii_us, sizeof(ascii_us) / 2,
  (uint8_t *)utf8_us, 0,
  (uint8_t *)combinations_us, sizeof(combinations_us) / 8,
};

hid_locale_t locale_de = {
  // The existing DE table is shorter than 128 entries. Bound reads by its
  // actual storage; correcting its contents belongs to the locale stage.
  (uint8_t *)ascii_de, sizeof(ascii_de) / 2,
  (uint8_t *)utf8_de, sizeof(utf8_de) / 6,
  (uint8_t *)combinations_de, sizeof(combinations_de) / 8,
};
