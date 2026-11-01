// Memory-only NVS fixture: no SDK/flash/hardware execution is claimed.
#include "nvs_fixture.h"
#include "nvs.h"
#include <cstring>
#include <map>
#include <vector>

namespace {
struct Value { char type; std::vector<unsigned char> bytes; };
Value text(const std::string &s) {
  std::vector<unsigned char> bytes(s.begin(), s.end());
  bytes.push_back(0);
  return {'s', bytes};
}
std::map<std::string, Value> initial() {
  return {{"ap_ssid", text(std::string(12, 's'))},
          {"ap_password", text(std::string(16, 'p'))},
          {"web_pw", text(std::string(16, 'w'))}};
}
std::map<std::string, Value> values = initial();
esp_err_t get(const char *key, char type, void *out, size_t size) {
  ++nvsMock::reads;
  auto it = values.find(key);
  if (it == values.end()) return ESP_ERR_NVS_NOT_FOUND;
  if (it->second.type != type || it->second.bytes.size() != size)
    return ESP_ERR_NVS_TYPE_MISMATCH;
  std::memcpy(out, it->second.bytes.data(), size);
  return ESP_OK;
}
esp_err_t put(const char *key, Value value) {
  ++nvsMock::writes;
  nvsMock::writtenKeys.emplace_back(key);
  if (nvsMock::failWriteAt == nvsMock::writes) return ESP_FAIL;
  values[key] = std::move(value);
  return ESP_OK;
}
}

namespace nvsMock {
unsigned reads = 0, writes = 0, opens = 0, closes = 0, commits = 0;
bool fail = false, failCommit = false;
unsigned failWriteAt = 0;
std::vector<std::string> writtenKeys;
void reset() {
  reads = writes = opens = closes = commits = 0;
  fail = failCommit = false;
  failWriteAt = 0;
  writtenKeys.clear();
  values = initial();
}
std::string persistedString(const char *key) {
  auto it = values.find(key);
  if (it == values.end() || it->second.type != 's' || it->second.bytes.empty()) return {};
  return std::string(reinterpret_cast<const char *>(it->second.bytes.data()), it->second.bytes.size()-1);
}
}

extern "C" esp_err_t nvs_open(const char *, nvs_open_mode_t, nvs_handle_t *handle) {
  ++nvsMock::opens;
  if (nvsMock::fail) return ESP_FAIL;
  *handle = 1;
  return ESP_OK;
}
extern "C" void nvs_close(nvs_handle_t) { ++nvsMock::closes; }
extern "C" esp_err_t nvs_get_u8(nvs_handle_t, const char *key, uint8_t *out) {
  return get(key, 'b', out, sizeof(*out));
}
extern "C" esp_err_t nvs_get_u16(nvs_handle_t, const char *key, uint16_t *out) {
  unsigned char bytes[2];
  auto error = get(key, 'h', bytes, sizeof(bytes));
  if (error == ESP_OK) *out = uint16_t(bytes[0]) | (uint16_t(bytes[1]) << 8);
  return error;
}
extern "C" esp_err_t nvs_get_u32(nvs_handle_t, const char *key, uint32_t *out) {
  unsigned char bytes[4];
  auto error = get(key, 'w', bytes, sizeof(bytes));
  if (error == ESP_OK) *out = uint32_t(bytes[0]) | (uint32_t(bytes[1]) << 8) |
                            (uint32_t(bytes[2]) << 16) | (uint32_t(bytes[3]) << 24);
  return error;
}
extern "C" esp_err_t nvs_get_str(nvs_handle_t, const char *key, char *out, size_t *size) {
  ++nvsMock::reads;
  auto it = values.find(key);
  if (it == values.end()) return ESP_ERR_NVS_NOT_FOUND;
  if (it->second.type != 's') return ESP_ERR_NVS_TYPE_MISMATCH;
  const size_t required = it->second.bytes.size();
  if (!out) { *size = required; return ESP_OK; }
  if (*size < required) return ESP_ERR_NVS_INVALID_LENGTH;
  std::memcpy(out, it->second.bytes.data(), required);
  *size = required;
  return ESP_OK;
}
extern "C" esp_err_t nvs_set_u8(nvs_handle_t, const char *key, uint8_t value) {
  return put(key, {'b', {value}});
}
extern "C" esp_err_t nvs_set_u16(nvs_handle_t, const char *key, uint16_t value) {
  return put(key, {'h', {uint8_t(value), uint8_t(value >> 8)}});
}
extern "C" esp_err_t nvs_set_u32(nvs_handle_t, const char *key, uint32_t value) {
  return put(key, {'w', {uint8_t(value), uint8_t(value >> 8), uint8_t(value >> 16), uint8_t(value >> 24)}});
}
extern "C" esp_err_t nvs_set_str(nvs_handle_t, const char *key, const char *value) {
  return put(key, text(value));
}
extern "C" esp_err_t nvs_commit(nvs_handle_t) {
  ++nvsMock::commits;
  return nvsMock::failCommit ? ESP_FAIL : ESP_OK;
}
