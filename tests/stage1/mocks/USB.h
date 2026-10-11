#pragma once
#include <cstdint>
using esp_event_base_t = const char *;
constexpr int ARDUINO_USB_STOPPED_EVENT = 1;
using UsbCallback = void (*)(void *, esp_event_base_t, int32_t, void *);
namespace mock { extern bool usbMounted; }
struct MockUSB {
  UsbCallback stopped = nullptr;
  void begin() {}
  explicit operator bool() const { return mock::usbMounted; }
  void onEvent(int, UsbCallback cb) { stopped = cb; }
};
inline MockUSB USB;
