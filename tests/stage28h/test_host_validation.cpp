// HOST-ONLY synthetic snapshots. No OS input, USB, files, clocks or network.
#include "../../language_preview/bridge.h"
#include <cstdio>
#include <cstring>
using ds_preview::Accept;namespace b=ds_bridge;namespace k=ds_keyboard;
#ifdef STAGE28H_TEST_MISMATCH
constexpr unsigned char SyncMask=1; // Negative test ONLY; runner never enables it.
#else
constexpr unsigned char SyncMask=0;
#endif
constexpr unsigned char Transient[][8]={{SyncMask,0,0,0,0,0,0,0},{0,0,4,0,0,0,0,0},{0,0,0,0,0,0,0,0},{0,0,4,0,0,0,0,0},{0,0,0,0,0,0,0,0},{0,0,5,0,0,0,0,0},{0,0,0,0,0,0,0,0}};
constexpr unsigned char Shared[][8]={{SyncMask,0,0,0,0,0,0,0},{0,0,4,0,0,0,0,0},{2,0,4,0,0,0,0,0},{2,0,4,0,0,0,0,0},{2,0,4,0,0,0,0,0},{2,0,4,0,0,0,0,0},{2,0,4,5,0,0,0,0},{2,0,4,0,0,0,0,0},{0,0,0,0,0,0,0,0}};
constexpr unsigned char Stale[][8]={{SyncMask,0,0,0,0,0,0,0},{0,0,0,0,0,0,0,0},{0,0,0,0,0,0,0,0}};
constexpr unsigned RetryMasks[]={ (1u<<1)|(1u<<2)|(1u<<4), (1u<<3)|(1u<<4)|(1u<<10)|(1u<<11), (1u<<2)|(1u<<3) };
struct Spec{const char* name;const char* source;const unsigned char (*reports)[8];unsigned count,attempts,admissions,acks,delays;};
constexpr Spec Specs[]={
 {"repeated_transient_delay_retry","STRING aa\nDELAY 2\nSTRING b",Transient,7,10,3,3,1},
 {"shared_owner_selective_release_drain","HOLD a\nDELAY 1\nRELEASE a\nRELEASE a\nSTRING b",Shared,9,13,4,4,1},
 {"stale_zero_current_drain","RELEASE a",Stale,3,5,1,1,0}
};
constexpr const char* Blocked[]={"INJECT_MOD\nHOLD CONTROL","HOLD SHIFT","RESET","RELEASE_ALL"};
struct Audit{
 unsigned assertions=0;const char* name;
 bool check(bool ok,const char* condition,unsigned line){++assertions;if(!ok)std::printf("FAIL trace=%s line=%u condition=%s\n",name,line,condition);return ok;}
};
#define REQUIRE(x) do{if(!audit.check((x),#x,__LINE__))return false;}while(0)
struct Trace{
 k::Report accepted[16]{},retry{};unsigned count=0,attempts=0,drainRetries=0,retryMask=0;bool retryPending=false,draining=false,mismatch=false;unsigned mode=0;Accept last=Accept::Failed;
 static Accept sink(void* ptr,const k::Report& r){auto& t=*static_cast<Trace*>(ptr);unsigned index=t.attempts++;if(index>=32){t.mismatch=true;return Accept::Failed;}
  if(t.retryPending&&!k::Planner::equal(t.retry,r)){t.mismatch=true;return Accept::Failed;}
  bool refuse=t.draining?t.drainRetries>0:(t.mode==0?(index==1||index==2||index==4):(t.mode==1&&(index==3||index==4)));
  if(refuse){t.retryMask|=1u<<index;if(t.draining)--t.drainRetries;t.retry=r;t.retryPending=true;t.last=Accept::Retry;return t.last;}
  t.retryPending=false;if(t.count==16){t.mismatch=true;return Accept::Failed;}t.accepted[t.count++]=r;t.last=Accept::Accepted;return t.last;
 }
};
bool oneStep(b::Bridge& bridge,Trace& trace,Audit& audit,unsigned now){unsigned calls=trace.attempts;unsigned ack=bridge.keyboardAcks(),admit=bridge.admissions();bridge.step(now);REQUIRE(trace.attempts-calls<=1);REQUIRE(bridge.keyboardAcks()<=bridge.admissions());REQUIRE(!trace.mismatch);
 if(trace.attempts!=calls){REQUIRE(bridge.keyboardAcks()==ack);if(trace.last==Accept::Retry){REQUIRE(bridge.admissions()==admit);}}
 return true;
}
void hex(const unsigned char* bytes){for(unsigned i=0;i<8;++i)std::printf("%s%02X",i?" ":"",bytes[i]);}
bool fixture(unsigned mode,unsigned& assertions){const Spec& spec=Specs[mode];Audit audit{0,spec.name};ds_preview::Program program;b::Bridge bridge;Trace trace;trace.mode=mode;
 REQUIRE(program.compile(spec.source,std::strlen(spec.source)));REQUIRE(bridge.begin(Trace::sink,&trace));REQUIRE(oneStep(bridge,trace,audit,0));REQUIRE(bridge.state()==b::State::Prepared);
 if(mode==1){REQUIRE(bridge.hold(0,4));REQUIRE(oneStep(bridge,trace,audit,0));REQUIRE(bridge.hold(1,0xe1));REQUIRE(oneStep(bridge,trace,audit,0));}
 REQUIRE(bridge.start(program));unsigned now=1,delayAt=0,delayReports=0;bool delaySeen=false;
 while(bridge.state()==b::State::Running&&now<500){unsigned before=bridge.delayAcks();REQUIRE(oneStep(bridge,trace,audit,now));if(bridge.delayAcks()!=before){REQUIRE(!delaySeen);delaySeen=true;delayAt=bridge.lastAckAt();delayReports=trace.count;REQUIRE(delayReports==(mode==0?5u:4u));}
  if(delaySeen&&now-delayAt<(mode==0?2u:1u))REQUIRE(trace.count==delayReports);++now;
 }
 REQUIRE(bridge.state()==b::State::Completed);REQUIRE(bridge.keyboardAcks()==spec.acks);REQUIRE(bridge.admissions()==spec.admissions);REQUIRE(bridge.delayAcks()==spec.delays);
 if(mode!=0){if(mode==1){REQUIRE(bridge.planner().releaseRequired());REQUIRE(!bridge.begin(Trace::sink,&trace));REQUIRE(bridge.planner().ownerEmpty(0)&&bridge.planner().ownerEmpty(1)&&bridge.planner().ownerEmpty(b::ScriptOwner));}else REQUIRE(bridge.planner().neutralConfirmed());
  trace.draining=true;trace.drainRetries=2;REQUIRE(bridge.drain(now));for(unsigned i=0;i<2;++i){REQUIRE(oneStep(bridge,trace,audit,now++));REQUIRE(bridge.state()==b::State::Draining);}REQUIRE(oneStep(bridge,trace,audit,now));REQUIRE(bridge.state()==b::State::Completed);REQUIRE(bridge.planner().neutralConfirmed());
 }
 REQUIRE(trace.count==spec.count);REQUIRE(trace.attempts==spec.attempts);REQUIRE(trace.retryMask==RetryMasks[mode]);
 for(unsigned i=0;i<spec.count;++i){if(std::memcmp(trace.accepted[i].bytes,spec.reports[i],8)){std::printf("FAIL trace=%s report=%u expected=",spec.name,i);hex(spec.reports[i]);std::printf(" actual=");hex(trace.accepted[i].bytes);std::puts("");return false;}}
 for(unsigned i=0;i<spec.count;++i){std::printf("VECTOR trace=%s report=%u bytes=",spec.name,i);hex(trace.accepted[i].bytes);std::puts("");}
 std::printf("PASS trace=%s reports=%u attempts=%u admissions=%u acks=%u delays=%u terminal=Completed\n",spec.name,trace.count,trace.attempts,bridge.admissions(),bridge.keyboardAcks(),bridge.delayAcks());assertions+=audit.assertions;return true;
}
bool negatives(unsigned& assertions){Audit audit{0,"blocked_preflight"};for(const char* source:Blocked){ds_preview::Program p;ds_preview::Runtime r;Trace t;char src[96];int n=std::snprintf(src,sizeof(src),"STRING MUST-NOT-APPEAR\n%s",source);REQUIRE(n>0&&static_cast<unsigned>(n)<sizeof(src));REQUIRE(!p.compile(src,n));REQUIRE(!p.ready());
  // Separate correctly typed event Sink; no Bridge begin/neutral callback in these cases.
  auto reject=[](void* ptr,const ds_preview::Event&)->Accept{++static_cast<Trace*>(ptr)->attempts;return Accept::Failed;};REQUIRE(!r.start(p,reject,&t));REQUIRE(t.attempts==0);REQUIRE(r.error().code==ds_preview::ErrorCode::NotCompiled);
 }
 std::puts("PASS blocked_preflight cases=4 callbacks=0");assertions+=audit.assertions;return true;
}
void manifest(){std::printf("{\"traces\":[");for(unsigned s=0;s<3;++s){const Spec& x=Specs[s];std::printf("%s{\"name\":\"%s\",\"reports\":[",s?",":"",x.name);for(unsigned i=0;i<x.count;++i){std::printf("%s\"",i?",":"");for(unsigned j=0;j<8;++j)std::printf("%02X",x.reports[i][j]);std::printf("\"");}std::printf("],\"attempts\":%u,\"admissions\":%u,\"acks\":%u,\"delays\":%u,\"terminal\":\"Completed\"}",x.attempts,x.admissions,x.acks,x.delays);}std::puts("],\"blocked_preflight\":{\"cases\":4,\"callbacks\":0},\"callback_behavior\":{\"index_base\":0,\"retry_attempt_indices\":[[1,2,4],[3,4,10,11],[2,3]],\"other_attempts\":\"Accepted\",\"maximum_attempts\":32}}");}
int main(int argc,char** argv){static_assert(sizeof(ds_preview::Event)==4&&sizeof(ds_preview::Instruction)==12,"Existing ABI");if(argc==2&&!std::strcmp(argv[1],"--manifest")){manifest();return 0;}if(argc!=1)return 2;unsigned assertions=0;for(unsigned i=0;i<3;++i)if(!fixture(i,assertions))return 1;if(!negatives(assertions))return 1;std::printf("PASS host-validation traces=3 blocked_cases=4 assertions=%u\n",assertions);return 0;}
