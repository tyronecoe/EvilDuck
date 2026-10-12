#include "settings.h"
#include "debug.h"
#include "config.h"
#include "execution_guard.h"
#include <atomic>
#include <nvs.h>
#include <memory>
#include <new>
#include <cstring>
#include <utility>

static bool autorun_enabled = false;
static String autorun_script_name = "";
static String ap_ssid = WIFI_SSID;
static String ap_password = WIFI_PASSWORD;
static uint8_t ap_channel = 1;

static bool stealth_mode = false;
static bool hidden_ap = false;
static bool disable_led = false;
static uint32_t led_color = 0x000028;
static String web_password = "";
static uint16_t autorun_delay_min = 0;
static uint16_t autorun_delay_max = 0;

namespace settings {

// Read failures are distinct from missing keys; never write defaults while loading.
static bool load_ready = false;
static esp_err_t load_error = ESP_ERR_INVALID_STATE;
bool ready() { return load_ready; }
int32_t loadError() { return load_error; }

static esp_err_t readString(nvs_handle_t handle, const char *key, String &value) {
  size_t length = 0;
  esp_err_t error = nvs_get_str(handle, key, nullptr, &length);
  if (error == ESP_ERR_NVS_NOT_FOUND) return ESP_OK;
  if (error != ESP_OK) return error;
  if (length == 0 || length > 4000) return ESP_ERR_NVS_INVALID_LENGTH;
  std::unique_ptr<char[]> buffer(new (std::nothrow) char[length]);
  if (!buffer) return ESP_ERR_NO_MEM;
  const size_t expected = length;
  error = nvs_get_str(handle, key, buffer.get(), &length);
  if (error != ESP_OK) return error;
  if (length != expected || buffer[length - 1] != 0 ||
      std::memchr(buffer.get(), 0, length - 1)) return ESP_ERR_NVS_INVALID_LENGTH;
  value = buffer.get();
  return value.length() == length - 1 ? ESP_OK : ESP_ERR_NO_MEM;
}

void load() {
  load_ready = false;
  load_error = ESP_OK;
  nvs_handle_t handle = 0;
  load_error = nvs_open("duck", NVS_READONLY, &handle);
  if (load_error == ESP_ERR_NVS_NOT_FOUND) {
    // A fresh device may have no namespace; in-memory defaults are sufficient.
    autorun_enabled = false; autorun_script_name = "";
    ap_ssid = WIFI_SSID; ap_password = WIFI_PASSWORD; ap_channel = 1;
    stealth_mode = false; hidden_ap = false; disable_led = false;
    led_color = 0x000028; web_password = "";
    autorun_delay_min = 0; autorun_delay_max = 0;
    load_error = ESP_OK;
    load_ready = true;
    return;
  }
  if (load_error != ESP_OK) return;
  uint8_t ar = 0, channel = 1, stealth = 0, hidden = 0, disabled = 0;
  uint32_t color = 0x000028;
  uint16_t minimum = 0, maximum = 0;
  String script = "", ssid = WIFI_SSID, password = WIFI_PASSWORD, web = "";
  auto accept = [](esp_err_t error) { return error == ESP_ERR_NVS_NOT_FOUND ? ESP_OK : error; };
  // Stop at the first real error and close without any commit/set/erase operation.
#define ED_READ(operation) do { if (load_error == ESP_OK) load_error = accept(operation); } while (0)
  ED_READ(nvs_get_u8(handle, "autorun_enabled", &ar));
  ED_READ(readString(handle, "autorun_script", script));
  ED_READ(readString(handle, "ap_ssid", ssid));
  ED_READ(readString(handle, "ap_password", password));
  ED_READ(nvs_get_u8(handle, "ap_channel", &channel));
  ED_READ(nvs_get_u8(handle, "stealth", &stealth));
  ED_READ(nvs_get_u8(handle, "hidden_ap", &hidden));
  ED_READ(nvs_get_u8(handle, "disable_led", &disabled));
  ED_READ(nvs_get_u32(handle, "led_color", &color));
  ED_READ(readString(handle, "web_pw", web));
  ED_READ(nvs_get_u16(handle, "ar_dly_min", &minimum));
  ED_READ(nvs_get_u16(handle, "ar_dly_max", &maximum));
#undef ED_READ
  nvs_close(handle);
  if (load_error != ESP_OK) return;
  if (ar > 1 || stealth > 1 || hidden > 1 || disabled > 1 || channel < 1 || channel > 13 ||
      ssid.length() == 0 || ssid.length() > 32 || password.length() < 8 || password.length() > 63 ||
      color > 0xffffff || minimum > maximum || (ar && script.length() == 0)) {
    load_error = ESP_ERR_INVALID_ARG;
    return;
  }
  autorun_enabled = ar;
  autorun_script_name = std::move(script);
  ap_ssid = std::move(ssid);
  ap_password = std::move(password);
  ap_channel = channel;
  stealth_mode = stealth;
  hidden_ap = hidden;
  disable_led = disabled;
  led_color = color;
  web_password = std::move(web);
  autorun_delay_min = minimum;
  autorun_delay_max = maximum;
  load_ready = true;
}

static std::atomic<esp_err_t> save_error{ESP_ERR_INVALID_STATE};
int32_t saveError() { return save_error.load(); }

bool saveChecked() {
  execution::TryGuard guard;
  if (!guard) { save_error.store(ESP_ERR_INVALID_STATE); return false; }
  if (!load_ready) {
    save_error = load_error == ESP_OK ? ESP_ERR_INVALID_STATE : load_error;
    return false;
  }
  if (ap_ssid.length() == 0 || ap_ssid.length() > 32 ||
      ap_password.length() < 8 || ap_password.length() > 63 || ap_channel < 1 || ap_channel > 13 ||
      led_color > 0xffffff || autorun_delay_min > autorun_delay_max ||
      autorun_script_name.length() >= 4000 || web_password.length() >= 4000 ||
      std::strlen(ap_ssid.c_str()) != ap_ssid.length() ||
      std::strlen(ap_password.c_str()) != ap_password.length() ||
      std::strlen(autorun_script_name.c_str()) != autorun_script_name.length() ||
      std::strlen(web_password.c_str()) != web_password.length() ||
      (autorun_enabled && autorun_script_name.length() == 0)) {
    save_error = ESP_ERR_INVALID_ARG;
    return false;
  }
  nvs_handle_t handle = 0;
  esp_err_t error = nvs_open("duck", NVS_READWRITE, &handle);
  if (error != ESP_OK) { save_error.store(error); return false; }
  // NVS setters may write immediately. First-error stopping is not rollback/atomicity.
#define ED_WRITE(operation) do { if (error == ESP_OK) error = operation; } while (0)
  ED_WRITE(nvs_set_u8(handle, "autorun_enabled", autorun_enabled));
  ED_WRITE(nvs_set_str(handle, "autorun_script", autorun_script_name.c_str()));
  ED_WRITE(nvs_set_str(handle, "ap_ssid", ap_ssid.c_str()));
  ED_WRITE(nvs_set_str(handle, "ap_password", ap_password.c_str()));
  ED_WRITE(nvs_set_u8(handle, "ap_channel", ap_channel));
  ED_WRITE(nvs_set_u8(handle, "stealth", stealth_mode));
  ED_WRITE(nvs_set_u8(handle, "hidden_ap", hidden_ap));
  ED_WRITE(nvs_set_u8(handle, "disable_led", disable_led));
  ED_WRITE(nvs_set_u32(handle, "led_color", led_color));
  ED_WRITE(nvs_set_str(handle, "web_pw", web_password.c_str()));
  ED_WRITE(nvs_set_u16(handle, "ar_dly_min", autorun_delay_min));
  ED_WRITE(nvs_set_u16(handle, "ar_dly_max", autorun_delay_max));
#undef ED_WRITE
  if (error == ESP_OK) error = nvs_commit(handle);
  nvs_close(handle);
  save_error.store(error);
  return error == ESP_OK;
}

void save() {
  if (!saveChecked()) debug::info("Settings save failed; partial persistence possible");
}

bool resetChecked() {
  execution::TryGuard guard;
  if (!guard) { save_error.store(ESP_ERR_INVALID_STATE); return false; }
  if (!load_ready) {
    save_error = load_error == ESP_OK ? ESP_ERR_INVALID_STATE : load_error;
    return false;
  }
  autorun_enabled = false;
  autorun_script_name = "";
  ap_ssid = WIFI_SSID;
  ap_password = WIFI_PASSWORD;
  ap_channel = 1;
  stealth_mode = false;
  hidden_ap = false;
  disable_led = false;
  led_color = 0x000028;
  web_password = "";
  autorun_delay_min = 0;
  autorun_delay_max = 0;
  return saveChecked();
}

void reset() {
  if (!resetChecked()) debug::info("Settings reset failed; partial persistence possible");
}

bool autorunEnabled() { return autorun_enabled; }
String getAutorun() { return autorun_script_name; }
void setAutorun(const String &scriptName) {
  autorun_script_name = scriptName;
  autorun_enabled = scriptName.length() > 0;
}

String getSSID() { return ap_ssid; }
String getPassword() { return ap_password; }
uint8_t getChannel() { return ap_channel; }

void setSSID(const String &ssid) {
  if (ssid.length() > 0 && ssid.length() <= 32) ap_ssid = ssid;
}
void setPassword(const String &password) {
  if (password.length() >= 8 && password.length() <= 63) ap_password = password;
}
void setChannel(uint8_t channel) {
  if (channel >= 1 && channel <= 13) ap_channel = channel;
}

bool getStealthMode() { return stealth_mode; }
void setStealthMode(bool on) { stealth_mode = on; }
bool getHiddenAp() { return hidden_ap; }
void setHiddenAp(bool on) { hidden_ap = on; }
bool getDisableLed() { return disable_led; }
void setDisableLed(bool on) { disable_led = on; }
uint32_t getLedColor() { return led_color; }
String getLedColorHex() {
  char buf[8];
  snprintf(buf, sizeof(buf), "#%06X", static_cast<unsigned int>(led_color & 0xFFFFFF));
  return String(buf);
}
void setLedColor(uint32_t color) { led_color = color & 0xFFFFFF; }
bool setLedColorHex(const String &hex) {
  String h = hex;
  h.trim();
  if (h.startsWith("#")) h = h.substring(1);
  if (h.length() != 6) return false;
  uint32_t color = 0;
  for (uint8_t i = 0; i < 6; ++i) {
    char c = h[i];
    uint8_t v;
    if (c >= '0' && c <= '9') v = c - '0';
    else if (c >= 'a' && c <= 'f') v = c - 'a' + 10;
    else if (c >= 'A' && c <= 'F') v = c - 'A' + 10;
    else return false;
    color = (color << 4) | v;
  }
  setLedColor(color);
  return true;
}
String getWebPassword() { return web_password; }
void setWebPassword(const String &pw) { web_password = pw; }
uint16_t getAutorunDelayMin() { return autorun_delay_min; }
uint16_t getAutorunDelayMax() { return autorun_delay_max; }
void setAutorunDelay(uint16_t minMs, uint16_t maxMs) {
  autorun_delay_min = minMs;
  autorun_delay_max = maxMs;
}

uint32_t pickAutorunDelayMs() {
  if (autorun_delay_max <= autorun_delay_min) return autorun_delay_min;
  return autorun_delay_min + (esp_random() % (autorun_delay_max - autorun_delay_min + 1));
}

}
