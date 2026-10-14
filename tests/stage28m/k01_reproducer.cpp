// Deliberately failing intended barrier on historical code; same regression on Stage28M.
#ifdef HISTORICAL_K01
#include "../stage28k/journal_driver.h"
namespace j=stage28k;
#else
#include "journal_driver.h"
namespace j=stage28m;
#endif
#include <cstdio>
#include <cstring>
int main(){
 j::Driver d;const char* text="DELAY 0";
 if(!d.compileMemory(text,std::strlen(text)))return 2;
 for(unsigned n=0;d.compiler().state()==ds_preview::CompileState::Compiling&&n<65536;++n)d.compileStep();
 if(!d.program().ready()||!d.begin())return 2;
 for(unsigned n=0;d.state()!=j::State::Prepared&&n<20;++n)d.step(0);
 if(d.state()!=j::State::Prepared||!d.enqueue({4,0,true}))return 2;
 auto before=d.counters();bool started=d.start(0);auto queuedAfterStart=d.queuedRequests();
 for(unsigned n=0;started&&d.state()==j::State::Running&&n<100;++n)d.step(0);
 bool held=!d.bridge().planner().ownerEmpty(0);
 std::printf("{\"start\":%s,\"queued_after_start\":%zu,\"queued_after_terminal\":%zu,\"setup_held\":%s,\"state\":%u,\"reports\":%zu,\"S_before\":%llu,\"S_after\":%llu}\n",started?"true":"false",queuedAfterStart,d.queuedRequests(),held?"true":"false",unsigned(d.state()),d.recordCount(),(unsigned long long)before.session,(unsigned long long)d.counters().session);
 if(started){std::fprintf(stderr,"K01 INTENDED BARRIER FAILED: start crossed one admitted unresolved setup request; terminal cleared it without setup execution\n");return 1;}
 if(d.queuedRequests()!=1||d.state()!=j::State::Prepared||d.counters().session!=before.session)return 2;
#ifndef HISTORICAL_K01
 d.requestCancel();d.step(0);
 if(!d.transport().fence(d.transport().epoch())||!d.canReclaim())return 2;
#endif
 return 0;
}
