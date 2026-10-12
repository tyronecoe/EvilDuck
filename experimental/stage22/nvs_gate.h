// EXPERIMENTAL — REVIEW ONLY — NOT AUTHORIZED FOR FLASHING
// Pinned ESP-IDF 5.5 only. No flash write/erase, retry or repair.
#include "esp_partition.h"
#include "esp_flash.h"
#include <string.h>
#include "evilduck_expected_table.h"
static volatile unsigned evilduck_gate_reason = 0;
static bool evilduck_gate_consumed = false;
__attribute__((noinline)) unsigned evilduck_nvs_gate_failure(void) { return evilduck_gate_reason; }
static const char *volatile evilduck_candidate_marker =
  "STAGE22_READONLY_QUIESCENT_EXPERIMENTAL_REVIEW_ONLY_NOT_AUTHORIZED_FOR_FLASHING";
const char *evilduck_nvs_candidate_identity(void) { return evilduck_candidate_marker; }
// Reasons: 1 repeated, 2 missing table, 3 table mismatch/read, 4 iteration,
// 5 geometry/flags/chip, 6 duplicate/extra, 7 canonical identity, 8 callback.
static esp_err_t gate_reject(unsigned reason) {
  evilduck_gate_reason = reason;
  return ESP_ERR_INVALID_STATE;
}
__attribute__((noinline)) esp_err_t evilduck_nvs_preinit_gate(void) {
  (void)evilduck_candidate_marker;
  if (evilduck_gate_consumed) return gate_reject(1);
  evilduck_gate_consumed = true; // one bounded attempt, even after failure
  if (!esp_flash_default_chip) return gate_reject(2);
  unsigned char block[32];
  for (unsigned off = 0; off < sizeof(evilduck_expected_table); off += sizeof(block)) {
    esp_err_t err = esp_flash_read(esp_flash_default_chip, block, 0x8000 + off, sizeof(block));
    if (err != ESP_OK) { evilduck_gate_reason = 3; return err; }
    if (memcmp(block, evilduck_expected_table + off, sizeof(block))) return gate_reject(3);
  }
  static const struct { const char *name; unsigned type, subtype, address, size; } expected[] = {
    {"nvs",1,2,0x9000,0x5000}, {"otadata",1,0,0xe000,0x2000},
    {"app0",0,0x10,0x10000,0x740000}, {"app1",0,0x11,0x750000,0x740000},
    {"spiffs",1,0x82,0xe90000,0x160000}, {"coredump",1,3,0xff0000,0x10000}
  };
  unsigned seen = 0, count = 0;
  const esp_partition_t *nvs = NULL;
  esp_partition_iterator_t it = esp_partition_find(ESP_PARTITION_TYPE_ANY, ESP_PARTITION_SUBTYPE_ANY, NULL);
  if (!it) return gate_reject(4); // API cannot distinguish OOM from absent table
  while (it) {
    const esp_partition_t *p = esp_partition_get(it);
    unsigned index = 6;
    if (!p || ++count > 6) { esp_partition_iterator_release(it); return gate_reject(6); }
    for (unsigned i = 0; i < 6; ++i) {
      if (!strncmp(p->label, expected[i].name, sizeof(p->label))) { index = i; break; }
    }
    if (index == 6 || (seen & (1u << index))) { esp_partition_iterator_release(it); return gate_reject(6); }
    if (p->type != expected[index].type || p->subtype != expected[index].subtype ||
        p->address != expected[index].address || p->size != expected[index].size ||
        p->flash_chip != esp_flash_default_chip || p->erase_size != 4096 ||
        p->encrypted || p->readonly != (index == 0)) {
      esp_partition_iterator_release(it); return gate_reject(5);
    }
    // SDK verify does not check readonly; explicit comparison above is mandatory.
    if (esp_partition_verify(p) != p) { esp_partition_iterator_release(it); return gate_reject(7); }
    seen |= 1u << index;
    if (index == 0) nvs = p;
    it = esp_partition_next(it); // SDK frees at exhaustion; copies are invalid
  }
  if (seen != 63 || !nvs) return gate_reject(4);
  // Advanced, version-pinned fields: SDK explicitly does not promise a stable API.
  // Probe callback policy only, never a write/erase. It does not authenticate it.
  if (!esp_flash_default_chip->os_func || !esp_flash_default_chip->os_func->region_protected ||
      esp_flash_default_chip->os_func->region_protected(esp_flash_default_chip->os_func_data,
                                                     0x9000, 0x5000) != ESP_ERR_NOT_ALLOWED)
    return gate_reject(8);
  evilduck_gate_reason = 0;
  return ESP_OK;
}
