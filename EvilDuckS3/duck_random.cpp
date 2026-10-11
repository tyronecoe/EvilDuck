#include "duck_random.h"
#include <cstring>
#ifndef EVILDUCK_HOST_TEST
#include <esp_random.h>
#endif

namespace duck_random {
namespace {
uint16_t low = 0, high = 9, jitterMax = 20;
bool jitterOn = false;
#ifdef EVILDUCK_HOST_TEST
uint32_t testDefault() { return 0x80000000U; }
Source rawSource = testDefault;
uint32_t raw() { return rawSource(); }
#else
uint32_t raw() { return esp_random(); }
#endif
constexpr char Lower[] = "abcdefghijklmnopqrstuvwxyz";
constexpr char Upper[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
constexpr char Letters[] = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";
constexpr char Numbers[] = "0123456789";
constexpr char Special[] = "!@#$%^&*()";
constexpr char All[] = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()";
}
#ifdef EVILDUCK_HOST_TEST
void source(Source source) { rawSource = source ? source : testDefault; }
#endif
void resetRun() { low=0; high=9; jitterMax=20; jitterOn=false; }
uint16_t minimum() { return low; }
uint16_t maximum() { return high; }
uint16_t jitterMaximum() { return jitterMax; }
bool jitterEnabled() { return jitterOn; }
void setMinimum(uint16_t value) { low=value; }
void setMaximum(uint16_t value) { high=value; }
void setJitterMaximum(uint16_t value) { jitterMax=value; }
void setJitterEnabled(bool value) { jitterOn=value; }
bool range(uint16_t minimum, uint16_t maximum, uint16_t &value) {
  if (minimum > maximum) return false;
  if (minimum == maximum) { value=minimum; return true; }
  const uint32_t width = uint32_t(maximum)-minimum+1U;
  // Reject the incomplete low-end bucket. Unsigned wrap is defined; width may
  // be65536. Each accepted residue has exactly the same number of preimages.
  const uint32_t threshold = (uint32_t(0)-width)%width;
  for(uint8_t attempt=0;attempt<MaxAttempts;++attempt) {
    const uint32_t sample=raw();
    if(sample>=threshold) { value=uint16_t(minimum+sample%width); return true; }
  }
  return false;
}
bool integer(uint16_t &value) { return range(low,high,value); }
bool jitter(uint16_t &milliseconds) {
  milliseconds=0; return !jitterOn || range(0,jitterMax,milliseconds);
}
int command(const char *name) {
  static const char *const names[]={"RANDOM_LOWERCASE_LETTER","RANDOM_UPPERCASE_LETTER","RANDOM_LETTER","RANDOM_NUMBER","RANDOM_SPECIAL","RANDOM_CHAR"};
  for(uint8_t i=0;i<6;++i)if(!strcmp(name,names[i]))return i;
  return -1;
}
const char *characters(uint8_t kind) {
  switch(kind) {case 0:return Lower;case 1:return Upper;case 2:return Letters;case 3:return Numbers;case 4:return Special;case 5:return All;default:return nullptr;}
}
bool character(uint8_t kind, char &value) {
  const char *set=characters(kind); uint16_t index;
  if(!set || !range(0,strlen(set)-1,index))return false;
  value=set[index];return true;
}
}
