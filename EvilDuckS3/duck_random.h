#pragma once
#include <stdint.h>
#include <stddef.h>

namespace duck_random {
constexpr uint8_t MaxAttempts = 32;
void resetRun();
uint16_t minimum();
uint16_t maximum();
uint16_t jitterMaximum();
bool jitterEnabled();
void setMinimum(uint16_t);
void setMaximum(uint16_t);
void setJitterMaximum(uint16_t);
void setJitterEnabled(bool);
// Inclusive unbiased range, bounded failure on reversed bounds/stuck source.
bool range(uint16_t low, uint16_t high, uint16_t &value);
bool integer(uint16_t &value);
bool jitter(uint16_t &milliseconds);
int command(const char *name); // Six exact canonical names; -1 otherwise.
const char *characters(uint8_t kind);
bool character(uint8_t kind, char &value);
#ifdef EVILDUCK_HOST_TEST
using Source = uint32_t (*)();
void source(Source); // Test adapter only; no language seed/command extension.
#endif
}
