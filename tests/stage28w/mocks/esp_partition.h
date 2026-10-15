#pragma once
#include <cstdint>
#include "esp_flash.h"
struct esp_partition_t { esp_flash_t *flash_chip; uint8_t type,subtype; uint32_t address,size; char label[17]; bool encrypted,readonly; };
using esp_partition_iterator_t=unsigned*;
constexpr unsigned ESP_PARTITION_TYPE_ANY=255,ESP_PARTITION_SUBTYPE_ANY=255;
esp_partition_iterator_t esp_partition_find(unsigned,unsigned,const char*);
esp_partition_iterator_t esp_partition_next(esp_partition_iterator_t);
const esp_partition_t *esp_partition_get(esp_partition_iterator_t);
void esp_partition_iterator_release(esp_partition_iterator_t);
