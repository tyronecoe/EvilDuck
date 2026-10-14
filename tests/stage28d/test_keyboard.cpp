#define main stage27b_main
#include "../stage27b/test_core.cpp"
#undef main
#include "../../language_preview/keyboard.h"
namespace k=ds_keyboard;
struct Reports {
 std::vector<k::Report> accepted,attempted;unsigned retry=0;bool fail=false,throws=false,cancel=false,reenter=false;
 k::Planner* planner=nullptr;
 static Accept sink(void* ptr,const k::Report& report){auto& c=*static_cast<Reports*>(ptr);c.attempted.push_back(report);
  if(c.reenter){c.planner->step(0);CHECK(!c.planner->start(sink,ptr));CHECK(!c.planner->hold(0,4));CHECK(!c.planner->drain());}
  if(c.cancel)c.planner->cancel();if(c.throws)throw std::runtime_error("mock report exception");if(c.fail)return Accept::Failed;if(c.retry){--c.retry;return Accept::Retry;}c.accepted.push_back(report);return Accept::Accepted;
 }
};
k::Report report(uint8_t mods,std::initializer_list<uint8_t> keys={}){k::Report r;r.bytes[0]=mods;unsigned i=2;for(auto key:keys){CHECK(i<8);r.bytes[i++]=key;}return r;}
void bytes(const k::Report& actual,const k::Report& expected){CHECK(k::Planner::equal(actual,expected));CHECK(actual.bytes[1]==0);}
void ready(k::Planner& p,uint32_t now=0){for(unsigned i=0;i<300&&p.state()==k::State::Working;++i)p.step(now+i);CHECK(p.state()==k::State::Ready);}
void init(k::Planner& p,Reports& c,uint32_t now=0){c.planner=&p;CHECK(p.start(Reports::sink,&c,now));ready(p,now);CHECK(p.neutralConfirmed());bytes(c.accepted.back(),report(0));}
void drain(k::Planner& p,uint32_t now=0){CHECK(p.drain(now));for(unsigned i=0;i<300&&p.state()==k::State::Working;++i)p.step(now+i);CHECK(p.state()==k::State::Cancelled);CHECK(p.neutralConfirmed());}
void keyRun(const std::string& name){
 if(name=="empty_sync_and_exact_single_key"){
  k::Planner p;Reports c;CHECK(!p.acceptedKnown());CHECK(p.releaseRequired());init(p,c);CHECK(p.tap(4));CHECK(c.accepted.size()==1);p.step(0);CHECK(p.phase()==k::Phase::Release);bytes(c.accepted.back(),report(0,{4}));CHECK(p.releaseRequired());p.step(1);bytes(c.accepted.back(),report(0));CHECK(p.state()==k::State::Ready);CHECK(p.neutralConfirmed());
 }else if(name=="all_modifier_bits_and_combinations"){
  for(unsigned mask=0;mask<256;++mask){k::Planner p;Reports c;init(p,c);for(unsigned bit=0;bit<8;++bit)if(mask&(1u<<bit)){CHECK(p.hold(bit%4,0xe0+bit));ready(p);}bytes(p.lastAccepted(),report(static_cast<uint8_t>(mask)));for(unsigned bit=0;bit<8;++bit){CHECK(p.release(bit%4,0xe0+bit));ready(p);}CHECK(p.neutralConfirmed());}
 }else if(name=="two_owners_shared_keys_and_modifiers"){
  k::Planner p;Reports c;init(p,c);CHECK(p.hold(0,4));ready(p);size_t count=c.accepted.size();CHECK(p.hold(1,4));CHECK(p.state()==k::State::Ready);CHECK(c.accepted.size()==count);CHECK(p.release(0,4));CHECK(p.state()==k::State::Ready);bytes(p.lastAccepted(),report(0,{4}));CHECK(p.release(1,4));ready(p);CHECK(p.neutralConfirmed());CHECK(p.hold(3,0xe1));ready(p);CHECK(p.hold(0,0xe1));CHECK(p.release(3,0xe1));bytes(p.desired(),report(2));CHECK(p.release(0,0xe1));ready(p);CHECK(p.neutralConfirmed());
 }else if(name=="idempotence_unmatched_invalid_usage_owner"){
  k::Planner p;Reports c;init(p,c);CHECK(p.hold(0,4));ready(p);for(unsigned i=0;i<1000;++i)CHECK(p.hold(0,4));CHECK(p.release(0,4));ready(p);CHECK(p.release(0,4));CHECK(p.neutralConfirmed());for(uint16_t usage:{0u,1u,3u,0x74u,0xdfu,0xe8u,0x100u,65535u}){CHECK(!p.hold(0,usage));CHECK(p.reason()==k::Reason::InvalidUsage);}CHECK(!p.hold(4,4));CHECK(p.reason()==k::Reason::InvalidOwner);CHECK(!p.release(size_t(-1),4));CHECK(!p.tap(4,256));CHECK(p.reason()==k::Reason::InvalidModifiers);CHECK(!p.tap(4,65535));CHECK(p.reason()==k::Reason::InvalidModifiers);CHECK(c.accepted.size()==3);
 }else if(name=="six_keys_seventh_reject_and_recovery"){
  k::Planner p;Reports c;init(p,c);for(unsigned key=9;key>=4;--key){CHECK(p.hold(key%4,key));ready(p);}bytes(p.desired(),report(0,{4,5,6,7,8,9}));auto before=p.desired();CHECK(!p.hold(0,10));CHECK(p.reason()==k::Reason::Rollover);bytes(p.desired(),before);CHECK(!p.tap(10));CHECK(p.reason()==k::Reason::Rollover);CHECK(p.release(0,8));ready(p);CHECK(p.hold(0,10));ready(p);bytes(p.lastAccepted(),report(0,{4,5,6,7,9,10}));
 }else if(name=="single_owner_capacity_and_reordering"){
  k::Planner p;Reports c;init(p,c);for(uint16_t key:{9,4,8,5,7,6}){CHECK(p.hold(0,key));ready(p);}CHECK(!p.hold(0,10));CHECK(p.release(0,5));ready(p);CHECK(p.hold(0,10));ready(p);bytes(p.lastAccepted(),report(0,{4,6,7,8,9,10}));CHECK(p.release(0,4));ready(p);CHECK(p.hold(1,4));ready(p);bytes(p.lastAccepted(),report(0,{4,6,7,8,9,10}));
 }else if(name=="persistent_transient_shift_and_lowercase_conflict"){
  k::Planner p;Reports c;init(p,c);CHECK(p.hold(0,0xe1));ready(p);CHECK(p.character('A'));ready(p);bytes(c.accepted[c.accepted.size()-2],report(2,{4}));bytes(p.lastAccepted(),report(2));CHECK(p.character('a'));ready(p);bytes(c.accepted[c.accepted.size()-2],report(2,{4}));CHECK(p.hold(1,0xe5));ready(p);CHECK(p.character('!'));ready(p);bytes(c.accepted[c.accepted.size()-2],report(0x22,{0x1e}));bytes(p.lastAccepted(),report(0x22));
 }else if(name=="us_printable_mapping_reference_vectors"){
  const std::string plain="abcdefghijklmnopqrstuvwxyz0123456789 -=[]\\;'`,./";const std::string shifted="ABCDEFGHIJKLMNOPQRSTUVWXYZ)!@#$%^&*( _+{}|:\"~<>?";
  CHECK(plain.size()==shifted.size());for(size_t i=0;i<plain.size();++i){uint8_t key,mods,sk,sm;CHECK(k::Planner::mapUS(plain[i],key,mods));CHECK(mods==0);CHECK(k::Planner::mapUS(shifted[i],sk,sm));CHECK(key==sk);CHECK(sm==(plain[i]==' '?0:2));}
  const char* punctuation="-=[]\\;'`,./_+{}|:\"~<>?!@#$%^&*()";
  const uint8_t keys[]={0x2d,0x2e,0x2f,0x30,0x31,0x33,0x34,0x35,0x36,0x37,0x38,0x2d,0x2e,0x2f,0x30,0x31,0x33,0x34,0x35,0x36,0x37,0x38,0x1e,0x1f,0x20,0x21,0x22,0x23,0x24,0x25,0x26,0x27};
  CHECK(strlen(punctuation)==sizeof(keys));for(unsigned i=0;i<sizeof(keys);++i){uint8_t usage,mods;CHECK(k::Planner::mapUS(punctuation[i],usage,mods));CHECK(usage==keys[i]);CHECK(mods==(i<11?0:2));}
  for(unsigned i=0;i<26;++i){uint8_t usage,mods;CHECK(k::Planner::mapUS('a'+i,usage,mods));CHECK(usage==4+i&&mods==0);CHECK(k::Planner::mapUS('A'+i,usage,mods));CHECK(usage==4+i&&mods==2);}
  for(unsigned ascii=32;ascii<=126;++ascii){k::Planner p;Reports c;init(p,c);uint8_t key,mods;CHECK(k::Planner::mapUS(ascii,key,mods));CHECK(p.character(ascii));ready(p);bytes(c.accepted[1],report(mods,{key}));bytes(c.accepted[2],report(0));}
  k::Planner p;Reports c;init(p,c);for(uint16_t ch:{9,10}){CHECK(p.character(ch));ready(p);bytes(c.accepted[c.accepted.size()-2],report(0,{static_cast<uint8_t>(ch==9?0x2b:0x28)}));}
 }else if(name=="unsupported_bytes_and_held_tap_policy"){
  k::Planner p;Reports c;init(p,c);for(uint16_t ch:{0u,1u,13u,31u,127u,128u,0xe4u,0x100u}){CHECK(!p.character(ch));CHECK(p.reason()==k::Reason::UnsupportedCharacter);CHECK(c.accepted.size()==1);}CHECK(p.hold(0,4));ready(p);CHECK(!p.tap(4));CHECK(p.reason()==k::Reason::HeldTap);bytes(p.desired(),report(0,{4}));CHECK(p.hold(1,0xe0));ready(p);CHECK(!p.tap(0xe0));CHECK(p.reason()==k::Reason::HeldTap);
 }else if(name=="named_function_navigation_key_usage_vectors"){
  for(uint16_t key:{0x28,0x2b,0x3a,0x45,0x68,0x73,0x4c,0x52,0x59,0xe7}){k::Planner p;Reports c;init(p,c);CHECK(p.tap(key));ready(p);bytes(c.accepted[1],key==0xe7?report(0x80):report(0,{static_cast<uint8_t>(key)}));bytes(c.accepted[2],report(0));}
 }else if(name=="retry_press_and_release_without_replay"){
  k::Planner p;Reports c;init(p,c);CHECK(p.character('!'));c.retry=2;p.step(0);auto press=p.pending();p.step(1);bytes(p.pending(),press);CHECK(c.accepted.size()==1);p.step(2);CHECK(c.accepted.size()==2);auto release=p.pending();c.retry=3;for(unsigned i=3;i<6;++i){p.step(i);bytes(p.pending(),release);CHECK(c.accepted.size()==2);}p.step(6);CHECK(!p.tap(4,256));CHECK(p.reason()==k::Reason::InvalidModifiers);CHECK(!p.tap(4,65535));CHECK(p.reason()==k::Reason::InvalidModifiers);CHECK(c.accepted.size()==3);CHECK(p.neutralConfirmed());for(unsigned i=1;i<4;++i)bytes(c.attempted[i],press);for(unsigned i=4;i<8;++i)bytes(c.attempted[i],release);
 }else if(name=="cancel_all_phases_and_explicit_neutral_drain"){
  for(unsigned phase=0;phase<3;++phase){k::Planner p;Reports c;init(p,c);CHECK(p.tap(4));if(phase>=1)p.step(0);if(phase==2)p.step(1);p.cancel();p.cancel();CHECK(p.state()==k::State::Cancelled);bytes(p.desired(),report(0));size_t n=c.attempted.size();p.step(2);CHECK(c.attempted.size()==n);CHECK(p.releaseRequired()==(phase==1));if(phase==1){CHECK(!p.start(Reports::sink,&c));CHECK(p.reason()==k::Reason::ReleaseRequired);}drain(p);CHECK(p.start(Reports::sink,&c));ready(p);CHECK(p.neutralConfirmed());}
 }else if(name=="failure_exception_and_uncertain_release"){
  for(unsigned phase=0;phase<3;++phase){k::Planner p;Reports c;init(p,c);CHECK(p.tap(4));if(phase)p.step(0);c.fail=phase!=2;c.throws=phase==2;p.step(1);CHECK(p.state()==k::State::Failed);CHECK(p.reason()==(phase==2?k::Reason::Exception:k::Reason::SinkFailure));CHECK(p.releaseRequired());bytes(p.desired(),report(0));CHECK(!p.hold(0,5));CHECK(p.reason()==(phase==2?k::Reason::Exception:k::Reason::SinkFailure));c.fail=c.throws=false;drain(p);CHECK(p.neutralConfirmed());}
 }else if(name=="drain_retry_failure_and_retry_exhaustion"){
  k::Planner p;Reports c;init(p,c);CHECK(p.hold(0,4));ready(p);p.stop();CHECK(p.releaseRequired());CHECK(p.drain());c.retry=3;for(unsigned i=0;i<3;++i){p.step(i);CHECK(!p.neutralConfirmed());}p.step(3);CHECK(p.neutralConfirmed());
  CHECK(p.start(Reports::sink,&c,0,3));ready(p);CHECK(p.tap(4));c.retry=4;for(unsigned i=0;i<4;++i)p.step(0);CHECK(p.reason()==k::Reason::Attempts);CHECK(p.state()==k::State::Failed);CHECK(p.releaseRequired());c.retry=0;CHECK(p.drain());c.fail=true;p.step(0);CHECK(p.state()==k::State::Failed);CHECK(p.releaseRequired());c.fail=false;drain(p);
 }else if(name=="wrap_timeout_and_stuck_clock"){
  k::Planner p;Reports c;init(p,c,0xfffffffe);CHECK(p.tap(4,0,0xfffffffe));p.step(0xffffffff);p.step(0);CHECK(p.neutralConfirmed());p.cancel();CHECK(p.start(Reports::sink,&c,0,2,3));ready(p);CHECK(p.tap(4));p.step(0);p.step(3);CHECK(p.reason()==k::Reason::Timeout);CHECK(p.releaseRequired());drain(p,3);
  CHECK(p.start(Reports::sink,&c,0,2));ready(p);CHECK(p.tap(4));c.retry=4;p.step(0);p.step(0);p.step(0);CHECK(p.reason()==k::Reason::Attempts);
 }else if(name=="reentrant_cancel_accepted_report_is_retained"){
  k::Planner p;Reports c;init(p,c);CHECK(!p.start(Reports::sink,&c));CHECK(p.tap(4));c.reenter=true;c.cancel=true;p.step(0);CHECK(p.state()==k::State::Cancelled);bytes(p.lastAccepted(),report(0,{4}));CHECK(p.releaseRequired());p.cancel();CHECK(p.diagnosticPhase()==k::Phase::Press);c.reenter=c.cancel=false;drain(p);CHECK(p.start(Reports::sink,&c));ready(p);CHECK(p.neutralConfirmed());
 }else if(name=="queue_single_action_and_restart_isolation"){
  k::Planner p;Reports c;init(p,c);CHECK(p.hold(0,0xe0));CHECK(!p.character('a'));CHECK(!p.hold(1,5));CHECK(p.reason()==k::Reason::Busy);ready(p);CHECK(p.tap(4));CHECK(!p.tap(5));ready(p);bytes(p.lastAccepted(),report(1));p.stop();CHECK(!p.start(Reports::sink,&c));drain(p);CHECK(p.start(Reports::sink,&c));ready(p);CHECK(p.tap(4));ready(p);bytes(c.accepted[c.accepted.size()-2],report(0,{4}));
 }else if(name=="budget_validation_and_noop_deduplication"){
  k::Planner p;Reports c;CHECK(!p.start(nullptr,&c));CHECK(!p.start(Reports::sink,&c,0,0));CHECK(!p.start(Reports::sink,&c,0,k::MaxAttempts+1));CHECK(!p.start(Reports::sink,&c,0,256,0));CHECK(!p.start(Reports::sink,&c,0,256,k::MaxElapsed+1));init(p,c);for(unsigned i=0;i<20;++i){CHECK(p.release(0,4));CHECK(p.release(1,0xe1));}CHECK(c.accepted.size()==1);CHECK(p.neutralConfirmed());
 }else if(name=="seeded_ownership_property_ordering"){
  k::Planner p;Reports c;init(p,c);bool keys[4][6]={};uint32_t seed=0x28d;for(unsigned i=0;i<500;++i){seed=seed*1664525u+1013904223u;unsigned owner=seed%4,key=(seed>>4)%6;bool hold=(seed>>16)&1;CHECK(hold?p.hold(owner,4+key):p.release(owner,4+key));keys[owner][key]=hold;ready(p);k::Report expected;unsigned n=2;for(unsigned k=0;k<6;++k){bool held=false;for(unsigned o=0;o<4;++o)held|=keys[o][k];if(held)expected.bytes[n++]=4+k;}bytes(p.desired(),expected);bytes(p.lastAccepted(),expected);}
 }else if(name=="hostile_cancel_retry_throw_and_one_attempt_bound"){
  for(unsigned mode=0;mode<3;++mode){k::Planner p;Reports c;init(p,c);CHECK(p.tap(4));c.cancel=true;c.retry=mode==0?1:0;c.throws=mode==1;size_t before=c.attempted.size();p.step(0);CHECK(c.attempted.size()==before+1);CHECK(p.state()==(mode==1?k::State::Failed:k::State::Cancelled));CHECK(p.releaseRequired()==(mode!=0));p.step(1);CHECK(c.attempted.size()==before+1);c.cancel=c.throws=false;c.retry=0;drain(p);}
  k::Planner initial;Reports sync;sync.planner=&initial;CHECK(initial.start(Reports::sink,&sync));initial.cancel();CHECK(initial.releaseRequired());drain(initial);CHECK(initial.neutralConfirmed());
  CHECK(initial.start(Reports::sink,&sync));ready(initial);CHECK(initial.tap(4));initial.step(0);initial.cancel();CHECK(initial.drain());initial.cancel();CHECK(initial.releaseRequired());drain(initial);
  k::Planner p;Reports c;init(p,c);for(unsigned i=0;i<100;++i){CHECK(p.character('x'));while(p.state()==k::State::Working){size_t before=c.attempted.size();p.step(i);CHECK(c.attempted.size()-before<=1);}CHECK(p.neutralConfirmed());}
 }else if(name=="zero_heap_planner_hot_path"){
  k::Planner p;auto sink=[](void*,const k::Report&){return Accept::Accepted;};allocationProbe=true;allocations=0;bool ok=p.start(sink,nullptr);p.step(0);bool held=p.hold(0,0xe1);p.step(0);bool typed=p.character('!');p.step(0);p.step(0);p.cancel();bool cleanup=p.drain();p.step(0);size_t count=allocations;allocationProbe=false;CHECK(ok&&held&&typed&&cleanup);CHECK(count==0);CHECK(p.neutralConfirmed());
 }else throw std::runtime_error("Unknown keyboard test");
}
int main(int argc,char** argv){try{if(argc!=2)return 2;keyRun(argv[1]);std::cout<<"PASS "<<argv[1]<<" ("<<assertions<<" assertions)\n";return 0;}catch(const std::exception& e){allocationProbe=false;std::cerr<<e.what()<<"\n";return 1;}}
