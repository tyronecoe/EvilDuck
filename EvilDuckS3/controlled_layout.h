#pragma once
#include "deployment_boot.h"
#if EVILDUCK_CONTROLLED_START
#include <esp_partition.h>
#include <esp_flash.h>
#include <cstring>

namespace deployment {
// Application-level table check before mounting media. This is not an early-NVS gate.
inline bool controlledLayoutReady() {
  struct Expected { const char *name; uint8_t type, subtype; uint32_t offset, size; };
  static const Expected expected[] = {
    {"nvs", 1, 2, 0x9000, 0x5000}, {"otadata", 1, 0, 0xE000, 0x2000},
    {"app0", 0, 0x10, 0x10000, 0x740000}, {"app1", 0, 0x11, 0x750000, 0x740000},
    {"spiffs", 1, 0x82, 0xE90000, 0x160000}, {"coredump", 1, 3, 0xFF0000, 0x10000}
  };
  auto it = esp_partition_find(ESP_PARTITION_TYPE_ANY, ESP_PARTITION_SUBTYPE_ANY, nullptr);
  if (!it) return false;
  unsigned index = 0;
  for (; it; it = esp_partition_next(it)) {
    const auto *p = esp_partition_get(it);
    if (index >= 6 || !p || p->flash_chip != esp_flash_default_chip ||
        p->encrypted || p->readonly || p->type != expected[index].type ||
        p->subtype != expected[index].subtype || p->address != expected[index].offset ||
        p->size != expected[index].size || std::strcmp(p->label, expected[index].name)) {
      esp_partition_iterator_release(it);
      return false;
    }
    ++index;
  }
  return index == 6;
}
}
#else
namespace deployment { inline bool controlledLayoutReady() { return true; } }
#endif
