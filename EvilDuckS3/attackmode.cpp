#include "attackmode.h"
#include "usb_msc.h"
#include "script_log.h"
#include "execution_guard.h"

namespace {
bool hidOn = true, storageWanted = false;
}
namespace attackmode {
void begin() { execution::Guard guard; usb_msc::end(); hidOn = true; storageWanted = false; }
bool hidEnabled() { execution::Guard guard; return hidOn; }
bool storageEnabled() { execution::Guard guard; return usb_msc::active(); }
bool storageRequested() { execution::Guard guard; return storageWanted; }
bool storagePreparing() { return usb_msc::preparing(); }
const char *storageState() { return usb_msc::stateName(); }
const char *storageError() { return usb_msc::lastError(); }
void update() { usb_msc::update(); }
void cancelPendingStorage() {
  execution::Guard guard;
  if (usb_msc::preparing()) { usb_msc::end(); storageWanted = false; }
}
void setHid(bool on) { execution::Guard guard; hidOn = on; }
void setStorage(bool on) {
  execution::Guard guard;
  storageWanted = on;
  if (!on) usb_msc::end();
  else if (!usb_msc::begin()) script_log::warn(usb_msc::lastError());
}
void setOff() { execution::Guard guard; setStorage(false); hidOn = false; }
void setHidOnly() { execution::Guard guard; setStorage(false); hidOn = true; }
void setStorageOnly() { execution::Guard guard; hidOn = false; setStorage(true); }
void setHidStorage() { execution::Guard guard; hidOn = true; setStorage(true); }
bool applyFromString(const String &modes) {
  execution::Guard guard;
  String m = modes; m.toUpperCase();
  if (m.indexOf("OFF") >= 0) { setOff(); return true; }
  bool wantHid = m.indexOf("HID") >= 0 || m.indexOf("KEYBOARD") >= 0;
  bool wantStorage = m.indexOf("STORAGE") >= 0 || m.indexOf("MSC") >= 0 || m.indexOf("DISK") >= 0;
  if (!wantHid && !wantStorage) wantHid = true;
  hidOn = wantHid;
  setStorage(wantStorage); // No requested-state equality check: errors/ejects can retry.
  return !wantStorage || usb_msc::active() || usb_msc::preparing();
}
}
