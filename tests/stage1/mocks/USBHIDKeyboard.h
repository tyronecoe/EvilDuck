#pragma once
#include "Arduino.h"
#include <stdexcept>
namespace mock { void press(uint8_t); void release(); }
struct USBHIDKeyboard {
  void begin() {}
  void pressRaw(uint8_t code) { mock::press(code); }
  void releaseAll() { mock::release(); }
  void print(const String &) { throw std::runtime_error("blocking Keyboard.print invoked"); }
};
