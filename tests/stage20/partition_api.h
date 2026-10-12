#pragma once
#include "esp_err.h"
#include <cassert>
#include <cstddef>
struct esp_partition_t {size_t size,address;bool readonly,encrypted;void*flash_chip;};
static unsigned lower_flash_calls=0;
static esp_err_t esp_flash_write(void*,const void*,size_t,size_t){++lower_flash_calls;return ESP_OK;}
static esp_err_t esp_flash_erase_region(void*,size_t,size_t){++lower_flash_calls;return ESP_OK;}
#define SPI_FLASH_SEC_SIZE 4096
#include "actual_partition_api.inc"
