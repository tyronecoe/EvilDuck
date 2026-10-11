#pragma once

#include <Arduino.h>

namespace attackmode {
  void begin();
  bool hidEnabled();
  bool storageEnabled(); // Verified raw media active, not requested mode.
  bool storageRequested();
  bool storagePreparing();
  const char *storageState();
  const char *storageError();
  void update();
  void cancelPendingStorage();
  void setHid(bool on);
  void setStorage(bool on);
  void setOff();
  void setHidOnly();
  void setStorageOnly();
  void setHidStorage();
  bool applyFromString(const String &modes);
}
