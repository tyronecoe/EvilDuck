#include "diagnostics.h"
#ifdef EVILDUCK_ROUTE_B_DIAGNOSTICS
#include "diagnostic_platform.h"
#include "task_platform.h"
#include "coordinator.h"
#include "backend_lease.h"
#include <stdio.h>
namespace route_x {
namespace {
struct State {Snapshot published{};int64_t previous=0,started=0;uint32_t lastSample=0;bool havePrevious=false,haveSample=false;} state;
void increment(uint32_t& n){if(n!=UINT32_MAX)++n;}
uint32_t bounded(uint64_t n){return n>UINT32_MAX?UINT32_MAX:static_cast<uint32_t>(n);}
void maximum(uint32_t& n,uint64_t v){uint32_t b=bounded(v);if(b>n)n=b;}
}
void admissionLocked(bool ok){increment(ok?state.published.accepted:state.published.refused);}
void queueLocked(unsigned n){maximum(state.published.queuePeak,n);}
void stopLocked(){increment(state.published.stopPublished);}
void observedLocked(){increment(state.published.stopObserved);}
void beginTurn(){
 // Only the bound owner invokes this, never from a USB/AsyncTCP callback.
 int64_t now=x_platform::clockUs();
 u_platform::Critical lock;auto& d=state.published;increment(d.ticks);
 if(now<0||(state.havePrevious&&now<state.previous))increment(d.clockErrors);
 else if(state.havePrevious)maximum(d.maxIntervalUs,uint64_t(now-state.previous));
 state.previous=now;state.started=now;state.havePrevious=now>=0;
}
void endTurn(uint32_t now){
 // No publication lock while calling backend/SDK measurement APIs.
 auto s=route_u::status();auto b=backend_b::status();
 bool sample=!state.haveSample||uint32_t(now-state.lastSample)>=1000;
 Resources resources{};if(sample){resources=x_platform::sample();state.lastSample=now;state.haveSample=true;}
 int64_t ended=x_platform::clockUs();
 u_platform::Critical lock;auto& d=state.published;
 if(state.started<0||ended<state.started)increment(d.clockErrors);else maximum(d.maxWorkUs,uint64_t(ended-state.started));
 d.phase=uint8_t(s.phase);d.reason=uint8_t(s.reason);
 if(!d.firstFault&&s.reason!=route_u::Reason::None&&s.reason!=route_u::Reason::Completed&&s.reason!=route_u::Reason::Cancelled)d.firstFault=uint8_t(s.reason);
 d.localKind=uint8_t(b.last.kind);d.firstLocalFault=uint8_t(b.first.kind);d.quarantined=b.quarantined;
 d.localSequence=b.last.sequence;d.clearRequest=b.clearRequest;d.clearSubmitted=b.clearSubmitted;
 if(sample){increment(d.samples);d.resources=resources;}
}
Snapshot snapshot(){u_platform::Critical lock;return state.published;}
size_t format(char* out,size_t n){
 if(!out||!n)return 0;auto d=snapshot();auto r=d.resources;
 int wrote=snprintf(out,n,"{\"observational\":true,\"ticks\":%lu,\"maxIntervalUs\":%lu,\"maxWorkUs\":%lu,\"clockErrors\":%lu,\"samples\":%lu,\"accepted\":%lu,\"refused\":%lu,\"queuePeak\":%lu,\"stopPublished\":%lu,\"stopObserved\":%lu,\"phase\":%u,\"reason\":%u,\"firstFault\":%u,\"quarantined\":%s,\"localKind\":%u,\"firstLocalFault\":%u,\"localSequence\":%llu,\"clearRequest\":%llu,\"clearSubmitted\":%llu,\"heapKnown\":%s,\"free8\":%lu,\"min8\":%lu,\"largest8\":%lu,\"loopStackKnown\":%s,\"loopAllocatedBytes\":%lu,\"loopMinimumFreeBytes\":%lu,\"asyncStackKnown\":false}",
 (unsigned long)d.ticks,(unsigned long)d.maxIntervalUs,(unsigned long)d.maxWorkUs,(unsigned long)d.clockErrors,(unsigned long)d.samples,(unsigned long)d.accepted,(unsigned long)d.refused,(unsigned long)d.queuePeak,(unsigned long)d.stopPublished,(unsigned long)d.stopObserved,unsigned(d.phase),unsigned(d.reason),unsigned(d.firstFault),d.quarantined?"true":"false",unsigned(d.localKind),unsigned(d.firstLocalFault),(unsigned long long)d.localSequence,(unsigned long long)d.clearRequest,(unsigned long long)d.clearSubmitted,r.heapKnown?"true":"false",(unsigned long)r.free8,(unsigned long)r.min8,(unsigned long)r.largest8,r.stackKnown?"true":"false",(unsigned long)r.loopAllocated,(unsigned long)r.loopFreeMinimum);
 if(wrote<0||size_t(wrote)>=n){out[0]=0;return 0;}return size_t(wrote);
}
size_t storageBytes(){return sizeof(state);}
#ifdef EVILDUCK_HOST_TEST
void saturateForTest(){u_platform::Critical lock;auto&d=state.published;d.ticks=d.accepted=d.refused=d.stopPublished=d.stopObserved=d.samples=UINT32_MAX;}
#endif
}
#endif
