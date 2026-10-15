#pragma once
#include <stdint.h>
#include <stddef.h>
namespace fixture {
enum class Outcome { RefuseBeforeAdmission, Accept, FailBeforeAdmission, Ambiguous };
struct Call { uint32_t time;uint8_t bytes[8];Outcome outcome;bool clearing;uint64_t session,operation;char phase[12]; };
constexpr size_t CallCapacity=4096;
extern Call calls[CallCapacity];extern size_t count;
extern bool persistent;extern Outcome next;extern bool clearRefused,clearAmbiguous;
extern uint32_t clearRequests,clearSubmitted;
extern void (*hook)();extern void (*identity)(uint64_t&,uint64_t&);
void reset();
}
