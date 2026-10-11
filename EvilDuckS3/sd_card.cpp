#include "sd_card.h"
#include "config.h"
#include "debug.h"
#include "execution_guard.h"

#if SD_ENABLED
#include <SPI.h>
#include <SD.h>

namespace {
bool mounted = false;

String normalizePath(const String &in) {
  execution::Guard guard;
  if (!in.length()) return "/";
  String p = in;
  if (p[0] != '/') p = "/" + p;
  return p;
}

bool isScriptName(const String &name) {
  execution::Guard guard;
  return name.endsWith(".txt") || name.endsWith(".duck");
}
}

namespace sd_card {

bool begin() {
  execution::Guard guard;
  mounted = false;
  SPI.begin(SD_SCK, SD_MISO, SD_MOSI, SD_CS);
  if (!SD.begin(SD_CS, SPI, SD_SPI_FREQ_HZ)) {
    debug::error("SD card mount failed");
    return false;
  }
  mounted = true;
  if (!SD.exists("/scripts")) {
    SD.mkdir("/scripts");
  }
  debug::info("SD card mounted");
  return true;
}

bool ready() {
  execution::Guard guard;
  return mounted && SD.cardType() != CARD_NONE;
}

size_t totalBytes() {
  execution::Guard guard;
  if (!ready()) return 0;
  return SD.totalBytes();
}

size_t usedBytes() {
  execution::Guard guard;
  if (!ready()) return 0;
  return SD.usedBytes();
}

size_t freeBytes() {
  execution::Guard guard;
  if (!ready()) return 0;
  return SD.totalBytes() - SD.usedBytes();
}

bool exists(const String &path) {
  execution::Guard guard;
  if (!ready()) return false;
  return SD.exists(normalizePath(path));
}

bool mkdir(const String &path) {
  execution::Guard guard;
  if (!ready()) return false;
  return SD.mkdir(normalizePath(path));
}

bool remove(const String &path) {
  execution::Guard guard;
  if (!ready()) return false;
  return SD.remove(normalizePath(path));
}

bool rename(const String &from, const String &to) {
  execution::Guard guard;
  if (!ready()) return false;
  return SD.rename(normalizePath(from), normalizePath(to));
}

File openRead(const String &path) {
  execution::Guard guard;
  if (!ready()) return File();
  return SD.open(normalizePath(path), FILE_READ);
}

String readFile(const String &path) {
  execution::Guard guard;
  if (!ready()) return "";
  File f = openRead(path);
  if (!f) return "";
  String out = f.readString();
  f.close();
  return out;
}

bool writeFile(const String &path, const String &content) {
  execution::Guard guard;
  if (!ready()) return false;
  File f = SD.open(normalizePath(path), FILE_WRITE);
  if (!f) return false;
  size_t n = f.print(content);
  f.close();
  return n == content.length();
}

bool appendFile(const String &path, const String &content) {
  execution::Guard guard;
  if (!ready()) return false;
  File f = SD.open(normalizePath(path), FILE_APPEND);
  if (!f) return false;
  size_t n = f.print(content);
  f.close();
  return n == content.length();
}

String listDir(const String &path) {
  execution::Guard guard;
  String output;
  if (!ready()) return output;
  File root = SD.open(normalizePath(path));
  if (!root || !root.isDirectory()) return output;
  File entry = root.openNextFile();
  while (entry) {
    output += String(entry.name());
    if (entry.isDirectory()) output += "/\n";
    else output += " (" + String(entry.size()) + ")\n";
    entry = root.openNextFile();
  }
  root.close();
  return output;
}

String listScriptsJson() {
  execution::Guard guard;
  String json = "[";
  if (!ready()) {
    json += "]";
    return json;
  }
  bool first = true;
  auto scan = [&](const char *dirPath) {
    File root = SD.open(dirPath);
    if (!root || !root.isDirectory()) return;
    File entry = root.openNextFile();
    while (entry) {
      if (!entry.isDirectory()) {
        String name = String(entry.name());
        int slash = name.lastIndexOf('/');
        if (slash >= 0) name = name.substring(slash + 1);
        if (isScriptName(name)) {
          if (!first) json += ",";
          first = false;
          json += "\"sd:" + name + "\"";
        }
      }
      entry = root.openNextFile();
    }
    root.close();
  };
  scan("/");
  scan("/scripts");
  json += "]";
  return json;
}

}

#else

namespace sd_card {
bool begin() {
  execution::Guard guard; return false; }
bool ready() {
  execution::Guard guard; return false; }
size_t totalBytes() {
  execution::Guard guard; return 0; }
size_t usedBytes() {
  execution::Guard guard; return 0; }
size_t freeBytes() {
  execution::Guard guard; return 0; }
bool exists(const String &) {
  execution::Guard guard; return false; }
bool mkdir(const String &) {
  execution::Guard guard; return false; }
bool remove(const String &) {
  execution::Guard guard; return false; }
bool rename(const String &, const String &) {
  execution::Guard guard; return false; }
String readFile(const String &) {
  execution::Guard guard; return ""; }
bool writeFile(const String &, const String &) {
  execution::Guard guard; return false; }
bool appendFile(const String &, const String &) {
  execution::Guard guard; return false; }
String listDir(const String &) {
  execution::Guard guard; return ""; }
String listScriptsJson() {
  execution::Guard guard; return "[]"; }
File openRead(const String &) {
  execution::Guard guard; return File(); }
}

#endif
