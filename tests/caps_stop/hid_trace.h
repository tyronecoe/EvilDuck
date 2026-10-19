#ifndef EVILDUCK_HID_TRACE_H
#define EVILDUCK_HID_TRACE_H
#include <stdint.h>
#include <stddef.h>
namespace hid_trace {
constexpr unsigned Capacity=128,Page=8;constexpr uint64_t WindowUs=120000000;
enum class Source:uint8_t{Owner,Backend,Usb,Led,Http};
enum class Kind:uint8_t{Admitted,Dequeued,Phase,StopPublished,StopObserved,Terminal,Pending,OperationEnd,Attempt,Accepted,Refused,Completed,TransferFailed,LedAccepted,Loss,Http202,RawOutput};
struct Event{uint64_t atUs=0,run=0,operation=0;uint32_t sequence=0;uint16_t detail=0;Source source{};Kind kind{};};
struct Batch{Event events[Page]{};uint64_t startedUs=0,nowUs=0;uint32_t latest=0,first=0,overwritten=0,clockErrors=0,counters[17]{};uint8_t count=0;bool enabled=false,more=false;};
bool enabled();void enable();void disable();void admit(uint64_t,uint16_t);
void httpReceipt(uint64_t,bool);
void note(Source,Kind,uint16_t detail=0,uint64_t operation=0);Batch read(uint32_t after);
const char* name(Source);const char* name(Kind);size_t storageBytes();
}
#endif
