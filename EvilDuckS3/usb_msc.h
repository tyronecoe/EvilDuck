#pragma once
#include <stdint.h>

namespace usb_msc {
  enum class State : uint8_t { Off, Preparing, Active, Ejected, Failed };
  // Request accepted is NOT startup completed. Poll preparing()/active()/lastError().
  bool begin();
  void update(); // At most one bounded preparation step; never creates/formats media.
  void end();
  bool active();
  bool preparing();
  State state();
  const char *stateName();
  const char *lastError(); // Immutable literal; safe lifetime after releasing the lock.
}
