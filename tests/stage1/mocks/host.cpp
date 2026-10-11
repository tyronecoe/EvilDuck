#include "host.h"
#include "com.h"
#include "duckscript.h"
#include "duck_vars.h"
#include "storage.h"
#include "settings.h"
#include "spiffs.h"
#include "sd_card.h"
#include "keyboard_locale.h"
#include "script_log.h"
#include "attackmode.h"
#include "debug.h"
#include "led.h"
#include "USBHID.h"
#include <stdexcept>

namespace mock {
uint32_t now=0;
unsigned blockingDelays=0;
uint8_t heldModifiers=0;
bool usbReady=true, usbAccept=true, usbMounted=true;
std::vector<Report> reports;
std::vector<uint8_t> heldKeys;
std::vector<Press> presses;
String text, output;
std::map<std::string, String> files;
std::vector<std::array<int,3>> colors;
void press(uint8_t code) {
  if (code >= 0xE0 && code <= 0xE7) { heldModifiers |= uint8_t(1 << (code-0xE0)); return; }
  if (std::find(heldKeys.begin(),heldKeys.end(),code)!=heldKeys.end()) return;
  heldKeys.push_back(code);
  presses.push_back({now,heldModifiers,code});
  // Visible US text only. Modifier combinations remain inspectable as reports.
  if (heldModifiers & ~uint8_t(0x22)) return;
  bool shift = heldModifiers & 0x22;
  if (code >= 4 && code <= 29) text += char((shift ? 'A' : 'a') + code-4);
  else if (code == 0x28) text += '\n';
  else if (code == 0x2B) text += '\t';
  else if (code == 0x2C) text += ' ';
  else if (code >= 0x1E && code <= 0x27) text += (shift ? "!@#$%^&*()" : "1234567890")[code-0x1E];
  else {
    struct Punctuation { uint8_t code; char plain, shifted; };
    static const Punctuation punctuation[] = {
      {0x2D,'-','_'},{0x2E,'=','+'},{0x2F,'[','{'},{0x30,']','}'},{0x31,'\\','|'},
      {0x33,';',':'},{0x34,'\'','"'},{0x35,'`','~'},{0x36,',','<'},{0x37,'.','>'},{0x38,'/','?'}
    };
    for(auto p:punctuation) if(code==p.code) text += shift ? p.shifted : p.plain;
  }
}
void release() { heldModifiers=0; heldKeys.clear(); }
bool report(const hid_keyboard_report_t &report, uint8_t instance, uint8_t id, size_t length) {
  if (length != 8) throw std::runtime_error("incorrect HID report length");
  if (!usbReady || !usbAccept) return false;
  Report raw = {now, instance, id, {}};
  memcpy(raw.bytes.data(), &report, 8); reports.push_back(raw);
  release(); heldModifiers=report.modifier;
  for(auto code:report.keycode) if(code) press(code);
  return true;
}
void print(const char *s) { output += String(s)+"\n"; }
void file(const char *name,const char *content) {
  storage::Ref ref; storage::parseRef(name,ref); files[ref.display.c_str()]=content;
}
void tick(uint32_t ms) { now+=ms; duckscript::update(); com::update(); }
void drain(unsigned limit) {
  while ((duckscript::running() || com::busy()) && limit--) tick();
  if (duckscript::running() || com::busy()) throw std::runtime_error("mock drain exceeded bounded tick budget");
}
void reset() {
  duckscript::stop();
  failReadAt=failSeekAt=std::numeric_limits<size_t>::max();
  bytesRead=readCalls=seekCalls=sourceSizeIncrease=0;
  usbReady=usbAccept=usbMounted=true; com::update();
  now=0; blockingDelays=0; release(); presses.clear(); reports.clear(); text=""; output="";
  files.clear(); colors.clear(); keyboard_locale::begin(); settings::reset();
  attackmode::begin(); script_log::clear();
}
}
uint32_t millis() { return mock::now; }
void delay(uint32_t ms) { ++mock::blockingDelays; mock::now+=ms; }
namespace debug { void info(const String &) {} void error(const String &) {} }
namespace led {
void setColor(int r,int g,int b) { mock::colors.push_back({r,g,b}); }
bool enabled() { return true; } void begin() {}
}
namespace storage {
bool parseRef(const String &input,Ref &out) {
  String s=input; s.trim(); if(!s.length()) return false;
  out.volume=s.startsWith("sd:") ? Volume::SD : Volume::SPIFFS;
  if(s.startsWith("sd:")) s=s.substring(3);
  if(s.startsWith("spiffs:")) s=s.substring(7);
  if(s.startsWith("/")) s=s.substring(1);
  out.path="/"+s; out.display=out.volume==Volume::SD ? "sd:"+s : s;
  return true;
}
String toDisplay(const Ref &r) { return r.display; }
bool exists(const Ref &r) { return mock::files.count(r.display.c_str()); }
String readFile(const Ref &r) { auto i=mock::files.find(r.display.c_str()); return i==mock::files.end() ? String() : i->second; }
bool writeFile(const Ref &r,const String &s) { mock::files[r.display.c_str()]=s; return true; }
bool appendFile(const Ref &r,const String &s) { mock::files[r.display.c_str()]+=s; return true; }
bool remove(const Ref &r) { return mock::files.erase(r.display.c_str()); }
File openRead(const Ref &r) { return exists(r) ? File(readFile(r)) : File(); }
bool resolveScript(const String &s,Ref &r) { return parseRef(s,r) && exists(r); }
bool resolveScriptForLoad(const String &s,Ref &r) { return resolveScript(s,r); }
bool sdReady() { return true; } bool begin() { return true; }
String infoJson() { return "{\"mock\":true}"; }
String listSpiffsScriptsJson() { return "[]"; } String listAllScriptsJson() { return "[]"; }
bool copyToSpiffs(const Ref &r,const String &s) { Ref to; return parseRef(s,to) && writeFile(to,readFile(r)); }
bool copyToSd(const String &s,const Ref &r) { Ref from; return parseRef(s,from) && writeFile(r,readFile(from)); }
}
#ifndef EVILDUCK_PRODUCTION_STORAGE
namespace attackmode {
bool hid=true, disk=false;
bool storageRequested() { return disk; }
bool storagePreparing() { return false; }
const char *storageState() { return disk ? "active" : "off"; }
const char *storageError() { return ""; }
void update() {}
void cancelPendingStorage() {}
void begin() { hid=true; disk=false; }
bool hidEnabled() { return hid; } bool storageEnabled() { return disk; }
void setHid(bool on) { hid=on; } void setStorage(bool on) { disk=on; }
void setOff() { hid=disk=false; } void setHidOnly() { hid=true; disk=false; }
void setStorageOnly() { hid=false; disk=true; } void setHidStorage() { hid=disk=true; }
bool applyFromString(const String &input) {
  String s=input; s.toUpperCase(); if(s.indexOf("OFF")>=0) { setOff(); return true; }
  hid=s.indexOf("HID")>=0 || s.indexOf("KEYBOARD")>=0;
  disk=s.indexOf("STORAGE")>=0 || s.indexOf("MSC")>=0 || s.indexOf("DISK")>=0;
  if (!hid && !disk) hid=true;
  return true;
}
}
#endif
namespace settings {
bool disable=false, stealth=false, hidden=false;
String ssid="mock", password, autorun, webPassword;
uint8_t channel=1; uint32_t color=0; uint16_t delayMin=0,delayMax=0;
void load() {} void save() {}
void reset() { disable=stealth=hidden=false; color=0; autorun=""; }
bool autorunEnabled() { return autorun.length(); }
String getAutorun() { return autorun; } void setAutorun(const String &s) { autorun=s; }
String getSSID() { return ssid; } void setSSID(const String &s) { ssid=s; }
String getPassword() { return password; } void setPassword(const String &s) { password=s; }
uint8_t getChannel() { return channel; } void setChannel(uint8_t n) { channel=n; }
bool getDisableLed() { return disable; } void setDisableLed(bool b) { disable=b; }
bool getStealthMode() { return stealth; } void setStealthMode(bool b) { stealth=b; }
bool getHiddenAp() { return hidden; } void setHiddenAp(bool b) { hidden=b; }
uint32_t getLedColor() { return color; } void setLedColor(uint32_t n) { color=n; }
String getLedColorHex() { return "000000"; } bool setLedColorHex(const String &) { return true; }
String getWebPassword() { return webPassword; } void setWebPassword(const String &s) { webPassword=s; }
uint16_t getAutorunDelayMin() { return delayMin; } uint16_t getAutorunDelayMax() { return delayMax; }
void setAutorunDelay(uint16_t a,uint16_t b) { delayMin=a; delayMax=b; }
uint32_t pickAutorunDelayMs() { return delayMin; }
}
namespace spiffs {
size_t size() { return 1024; } size_t usedBytes() { return 0; } size_t freeBytes() { return 1024; }
bool begin() { return true; } bool format() { mock::files.clear(); return true; }
String listDir(const String &) { return "mock"; }
String readFile(const String &s) { storage::Ref r; storage::parseRef(s,r); return storage::readFile(r); }
bool create(const String &s) { storage::Ref r; return storage::parseRef(s,r) && storage::writeFile(r,""); }
bool remove(const String &s) { storage::Ref r; return storage::parseRef(s,r) && storage::remove(r); }
bool append(const String &s,const String &text) { storage::Ref r; return storage::parseRef(s,r) && storage::appendFile(r,text); }
bool rename(const String &,const String &) { return false; }
bool streamOpen(const String &) { return false; } void streamClose() {}
bool streaming() { return false; } bool streamAvailable() { return false; }
size_t streamWrite(const char *,size_t) { return 0; } size_t streamRead(char *,size_t) { return 0; }
}
#ifndef EVILDUCK_PRODUCTION_STORAGE
namespace sd_card { String listDir(const String &) { return "mock SD"; } }
#endif
