#pragma once
#include "duck_expr.h"
#include <Arduino.h>

// Fixed registry, implemented with the existing symbol adapter (no dynamic table).
namespace internal_vars {
bool reserved(const char *, size_t);
bool writable(const char *, size_t);
duck_expr::Lookup resolve(const char *, size_t, uint16_t &, bool syntax = false);
bool write(const String &, uint16_t, String &);
void resetRun();
uint16_t lockTimeout();
// 0..8 waits: index/3 Num,Caps,Scroll; index%3 OFF,ON,CHANGE. -1 unmatched.
int lockCommand(const String &line);
}
