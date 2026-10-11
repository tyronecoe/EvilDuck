#pragma once
#include <cstdint>
#include <cstddef>
struct hid_keyboard_report_t { uint8_t modifier, reserved, keycode[6]; };
constexpr uint8_t HID_REPORT_ID_KEYBOARD=1;
namespace mock { extern bool usbReady; bool report(const hid_keyboard_report_t &, uint8_t, uint8_t, size_t); }
struct USBHID { void begin() {} bool ready() { return mock::usbReady; } };
inline bool tud_hid_n_report(uint8_t instance, uint8_t id, const void *data, size_t length) {
  return mock::report(*static_cast<const hid_keyboard_report_t *>(data), instance, id, length);
}
