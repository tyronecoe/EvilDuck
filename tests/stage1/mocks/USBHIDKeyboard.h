#pragma once
#include "Arduino.h"
#include <stdexcept>
namespace mock { void press(uint8_t); void release(); }
struct USBHIDKeyboard;
inline USBHIDKeyboard *mockKeyboard = nullptr;
struct USBHIDKeyboard {
  USBHIDKeyboard() { mockKeyboard = this; }
  virtual void _onOutput(uint8_t, const uint8_t *, uint16_t) {}
  virtual void _onSetFeature(uint8_t, const uint8_t *, uint16_t) {}
  void begin() {}
  void pressRaw(uint8_t code) { mock::press(code); }
  void releaseAll() { mock::release(); }
  void print(const String &) { throw std::runtime_error("blocking Keyboard.print invoked"); }
};
