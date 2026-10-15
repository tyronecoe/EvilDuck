#pragma once
#include <stdint.h>
#include <stddef.h>
namespace lower {
enum class Outcome { True,FalseWithoutAcceptance,FalseAfterPossibleAcceptance };
struct Call {uint32_t at;uint8_t bytes[8];uint8_t instance,id;Outcome outcome;uint64_t session,operation;bool clear;char phase[12];};
constexpr size_t Capacity=4096;
extern size_t journalLimit;extern unsigned overflowAttempts;extern Call overflowCall;extern Call calls[Capacity];extern size_t count;extern Outcome next;extern bool disconnectOnReady;
extern void (*hook)();
void reset();bool ready();bool submit(uint8_t,uint8_t,const void*,size_t);
}
