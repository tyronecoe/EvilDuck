#pragma once
#include "Arduino.h"
#include <array>
#include <map>
#include <vector>

namespace mock {
struct Press { uint32_t time; uint8_t modifiers, key; };
extern uint32_t now;
extern unsigned blockingDelays;
extern uint8_t heldModifiers;
extern bool usbReady;
extern std::vector<uint8_t> heldKeys;
extern std::vector<Press> presses;
extern String text, output;
extern std::map<std::string, String> files;
extern std::vector<std::array<int,3>> colors;
void reset();
void print(const char *s);
void file(const char *name, const char *content);
void tick(uint32_t ms=1);
void drain(unsigned limit=20000);
}
