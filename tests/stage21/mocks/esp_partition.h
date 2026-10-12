#pragma once
// Host descriptor adapter, NOT the native Xtensa structure/ABI.
#include <cstddef>
#include <cstdint>
#include "esp_err.h"
struct esp_partition_t {
  void *flash_chip;
  uint32_t address, size;
  char label[17];
  bool encrypted, readonly;
};
using esp_partition_type_t = unsigned;
using esp_partition_subtype_t = unsigned;
constexpr unsigned ESP_PARTITION_TYPE_DATA=1, ESP_PARTITION_SUBTYPE_DATA_NVS=2;
extern "C" {
const esp_partition_t *esp_partition_find_first(unsigned, unsigned, const char *);
uint32_t esp_partition_get_main_flash_sector_size();
esp_err_t esp_partition_read(const esp_partition_t *, size_t, void *, size_t);
esp_err_t esp_partition_read_raw(const esp_partition_t *, size_t, void *, size_t);
esp_err_t esp_partition_write(const esp_partition_t *, size_t, const void *, size_t);
esp_err_t esp_partition_write_raw(const esp_partition_t *, size_t, const void *, size_t);
esp_err_t esp_partition_erase_range(const esp_partition_t *, size_t, size_t);
}
