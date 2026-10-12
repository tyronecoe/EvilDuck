#pragma once
struct esp_flash_os_functions_t { esp_err_t (*region_protected)(void*,size_t,size_t); };
struct esp_flash_t { const esp_flash_os_functions_t *os_func;void *os_func_data; };
extern esp_flash_t *esp_flash_default_chip;
