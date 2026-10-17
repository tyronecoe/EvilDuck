#include "bridge.h"
#include "shortcut_keys.h"
#include <vector>
#include <string>
#include <iostream>
#include <stdexcept>
using ds_preview::Accept;
static unsigned assertions=0;static void check(bool b,const char*m){++assertions;if(!b)throw std::runtime_error(m);}
struct Output{std::vector<ds_keyboard::Report> accepted;bool retry=false,fail=false;unsigned calls=0;static Accept sink(void*p,const ds_keyboard::Report&r){auto&o=*static_cast<Output*>(p);++o.calls;if(o.fail)return Accept::Failed;if(o.retry)return Accept::Retry;o.accepted.push_back(r);return Accept::Accepted;}};
int main(int argc,char**argv){if(argc!=2)return 2;try{
 std::string id=argv[1];ds_preview::Program p;Output o;ds_bridge::Bridge b;
 constexpr char source[]="COMMAND a\nSHIFT LEFT\n";check(p.compile(source,sizeof(source)-1),"compile");
 check(b.begin(Output::sink,&o),"begin");b.step(0);check(b.start(p,1),"start");
 if(id=="B01"){
  for(unsigned t=2;t<500&&b.state()==ds_bridge::State::Running;++t)b.step(t);
  check(b.state()==ds_bridge::State::Completed&&b.admissions()==2&&b.keyboardAcks()==2,"two immutable acks");check(o.accepted.size()==5,"sync + two press/restores");check(o.accepted[1].bytes[0]==8&&o.accepted[1].bytes[2]==4,"command report");check(o.accepted[3].bytes[0]==2&&o.accepted[3].bytes[2]==0x50,"shift report");for(auto i:{0,2,4})for(auto v:o.accepted[i].bytes)check(v==0,"neutral sync/restores");
 }else if(id=="B02"){
  o.retry=true;for(unsigned t=2;t<10;++t)b.step(t);check(b.admissions()==1&&b.keyboardAcks()==0,"single admission during retry");o.retry=false;for(unsigned t=10;t<500&&b.state()==ds_bridge::State::Running;++t)b.step(t);check(b.state()==ds_bridge::State::Completed&&o.accepted[1].bytes[0]==8,"retry preserves modifiers");
 }else if(id=="B03"){
  for(unsigned t=2;t<8;++t){b.step(t);if(o.accepted.size()>1)break;}b.cancel();check(b.state()==ds_bridge::State::Cancelled,"cancel");check(b.drain(10),"explicit drain");for(unsigned t=11;t<30&&b.state()==ds_bridge::State::Draining;++t)b.step(t);check(ds_keyboard::Planner::neutral(o.accepted.back()),"local neutral accepted");
 }else if(id=="B04"){
  o.fail=true;for(unsigned t=2;t<20&&(b.state()==ds_bridge::State::Running||b.state()==ds_bridge::State::Failing);++t)b.step(t);check(b.state()==ds_bridge::State::Error,"failed press error");check(b.keyboardAcks()==0,"failed press no ack");
 }else if(id=="B05"){
  for(unsigned t=2;t<20&&o.accepted.size()<2;++t)b.step(t);o.fail=true;for(unsigned t=20;t<40&&(b.state()==ds_bridge::State::Running||b.state()==ds_bridge::State::Failing);++t)b.step(t);check(b.state()==ds_bridge::State::Error&&b.keyboardAcks()==0,"failed release no source ack");
 }else if(id=="B06"){
  for(auto e:{ds_preview::Event{ds_preview::EventType::Character,'a',2},ds_preview::Event{ds_preview::EventType::Delay,1,2},ds_preview::Event{ds_preview::EventType::Hold,4,2}})check(!ds_bridge::Bridge::validEvent(e),"reject modifier on wrong event type");check(ds_bridge::Bridge::validEvent({ds_preview::EventType::KeyTap,4,15}),"valid typed mask");
 }else if(id=="B07"){
  ds_preview::Program q;check(q.compile("COMMAND A\nCOMMAND !\n",20),"implicit shift compile");b.cancel();check(b.drain(10),"drain old");b.step(11);check(b.begin(Output::sink,&o,12),"new begin");b.step(13);check(b.start(q,14),"new source");for(unsigned t=15;t<500&&b.state()==ds_bridge::State::Running;++t)b.step(t);check(b.state()==ds_bridge::State::Completed,"implicit shift complete");check(o.accepted[o.accepted.size()-4].bytes[0]==10&&o.accepted[o.accepted.size()-2].bytes[0]==10,"automatic shift merged");
 }else if(id=="B08"){
  for(unsigned c=32;c<=126;++c){uint8_t a=0,m=0,u=0,n=0;check(ds_shortcut::mapUS(c,a,m)&&ds_keyboard::Planner::mapUS(c,u,n)&&a==u&&m==n,"shared printable mapping");}
  check(sizeof(ds_preview::Event)==6,"fixed bounded event bytes");std::cout<<"SIZES Program="<<sizeof(ds_preview::Program)<<" Runtime="<<sizeof(ds_preview::Runtime)<<" Bridge="<<sizeof(ds_bridge::Bridge)<<" Planner="<<sizeof(ds_keyboard::Planner)<<"\n";
 }else check(false,"unknown");std::cout<<"PASS "<<id<<" ("<<assertions<<" assertions)\n";return 0;
 }catch(const std::exception&e){std::cerr<<"FAIL "<<argv[1]<<": "<<e.what()<<"\n";return 1;}}
