#include "hid_trace.h"
#include <atomic>
#include <cstring>
#include <esp_timer.h>
#ifdef EVILDUCK_HOST_TEST
#include <mutex>
namespace{std::mutex mux;struct Guard{std::lock_guard<std::mutex> l{mux};};}
#else
#include <freertos/FreeRTOS.h>
namespace{portMUX_TYPE mux=portMUX_INITIALIZER_UNLOCKED;struct Guard{Guard(){portENTER_CRITICAL(&mux);}~Guard(){portEXIT_CRITICAL(&mux);}};}
#endif
namespace {
std::atomic<bool> on{false};hid_trace::Event events[hid_trace::Capacity]{};
uint64_t run=0,started=0,last=0;uint32_t sequence=0,overwritten=0,clockErrors=0,counters[17]{};unsigned head=0,count=0;
void inc(uint32_t& v){if(v!=UINT32_MAX)++v;}
uint64_t now(){return uint64_t(esp_timer_get_time());}
bool current(uint64_t t){if(t<last){inc(clockErrors);on.store(false);return false;}last=t;if(t-started>=hid_trace::WindowUs){on.store(false);return false;}return on.load();}
void append(hid_trace::Source source,hid_trace::Kind kind,uint16_t detail,uint64_t op,uint64_t explicitRun=UINT64_MAX){
 uint64_t t=now();if(!current(t))return;if(sequence==UINT32_MAX){on.store(false);return;}
 bool callback=source==hid_trace::Source::Usb||source==hid_trace::Source::Led;
 auto e=hid_trace::Event{t,explicitRun!=UINT64_MAX?explicitRun:(callback||(source==hid_trace::Source::Backend&&!(detail&16)))?0:run,op,++sequence,detail,source,kind};
 if(count==hid_trace::Capacity){head=(head+1)%hid_trace::Capacity;--count;inc(overwritten);}
 events[(head+count)%hid_trace::Capacity]=e;++count;inc(counters[unsigned(kind)]);
}
}
namespace hid_trace {
bool enabled(){return on.load(std::memory_order_relaxed);}
void enable(){Guard g;on.store(false);run=0;head=count=sequence=overwritten=clockErrors=0;std::memset(counters,0,sizeof(counters));for(auto& e:events)e=Event{};started=last=now();on.store(true);}
void disable(){Guard g;on.store(false);}
void admit(uint64_t id,uint16_t ms){if(!enabled())return;Guard g;if(!on.load())return;run=id;append(Source::Owner,Kind::Admitted,ms,0);}
void note(Source s,Kind k,uint16_t detail,uint64_t op){if(!enabled())return;Guard g;if(on.load())append(s,k,detail,op);}
void httpReceipt(uint64_t id,bool owned){if(!enabled())return;Guard g;if(on.load())append(Source::Http,Kind::Http202,owned?1:0,0,id);}
Batch read(uint32_t after){Guard g;Batch b;b.nowUs=now();if(on.load())current(b.nowUs);b.enabled=on.load();b.startedUs=started;b.latest=sequence;b.first=count?events[head].sequence:0;b.overwritten=overwritten;b.clockErrors=clockErrors;for(unsigned i=0;i<17;++i)b.counters[i]=counters[i];
 for(unsigned i=0;i<count;++i){const auto& e=events[(head+i)%Capacity];if(e.sequence<=after)continue;if(b.count==Page){b.more=true;break;}b.events[b.count++]=e;}return b;
}
const char* name(Source s){static const char* names[]={"owner","backend","usb-callback","led-receiver","http"};return unsigned(s)<5?names[unsigned(s)]:"unknown";}
const char* name(Kind k){static const char* names[]={"admitted","dequeued","phase","stop-published","stop-observed","terminal","operation-pending","operation-end","report-attempt","report-accepted","report-refused","input-completed","transfer-failed","led-accepted","loss","http202-prepared","raw-output"};return unsigned(k)<17?names[unsigned(k)]:"unknown";}
size_t storageBytes(){return sizeof(events)+sizeof(counters)+sizeof(run)+sizeof(started)+sizeof(last)+sizeof(sequence)+sizeof(overwritten)+sizeof(clockErrors)+sizeof(head)+sizeof(count)+sizeof(on);}
}
