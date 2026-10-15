#include "adapter.h"
#include "allocations.h"
#include "lower.h"
#include "backend_lease.h"
#include "host.h"
#include "com.h"
#include "hid_backend.h"
#include "duckscript.h"
#include "attackmode.h"
#include "keyboard_locale.h"
#include "duck_random.h"
#include "USB.h"
#include "execution_guard.h"
#include <iostream>
#include <stdexcept>
#include <string>
#include <thread>
#include <vector>
using native_b::Adapter;using native_b::State;using native_b::Fault;
static unsigned assertions=0;static std::vector<std::string> programs;static Adapter* current=nullptr;
static uint32_t resultAcks=0,resultAdmissions=0,resultRetries=0,resultDelays=0;static uint64_t finalSession=0;static int finalState=0,finalFault=0;
static void check(bool b,const char* s){++assertions;if(!b)throw std::runtime_error(s);}
static bool terminal(State s){return s==State::Completed||s==State::Cancelled||s==State::Error||s==State::Quarantined;}
static void step(Adapter&a,uint32_t d=1){mock::now+=d;a.step(mock::now);}
static void prepare(Adapter&a,const std::string&s){programs.push_back(s);check(a.prepare(s.c_str(),s.size()),"prepare");for(int i=0;i<10000&&(a.state()==State::Loading||a.state()==State::Compiling);++i)step(a,0);}
static void finish(Adapter&a){for(int i=0;i<10000&&!terminal(a.state());++i)step(a);check(terminal(a.state()),"bounded terminal");}
static void start(Adapter&a,const std::string&s){prepare(a,s);check(a.state()==State::Ready,"capability validated");check(a.start(mock::now),"lease acquired");}
static void run(Adapter&a,const std::string&s){start(a,s);finish(a);check(a.state()==State::Completed&&a.fault()==Fault::None,"local done");check(a.acks()==a.admissions(),"single local ack each admission");}
static void phase(Adapter&a,const char*p){for(int i=0;i<10000;++i){if(a.state()==State::Running&&strcmp(route_b::phase(),p)==0)return;step(a);}check(false,"phase reached");}
static unsigned callbacks=0;static void callback(){++callbacks;}
static void interference(){
 check(!current->start(mock::now),"reentrant start refused");auto n=lower::count;current->step(mock::now);check(lower::count==n,"reentrant adapter tick refused");
 uint8_t k=4;check(!hid_backend::beginReport(0,&k,1),"reentrant backend report denied while IO active");check(!com::executeNow("STRING BAD"),"reentrant com denied");com::update();check(lower::count==n,"reentrant scheduler update did not mutate/send");
 hid_backend::pressKeycode(4);hid_backend::releaseAll();check(lower::count==n,"raw helpers denied in lower callback");
}
static void deferredCancel(){current->cancel();check(!current->start(mock::now),"cannot restart inside callback");}
static void test(const std::string&n){
 mock::reset();lower::reset();hid_backend::begin();com::update();lower::count=0;mock::reports.clear();mock::text="";
 static Adapter a;current=&a;
 if(n=="T01"||n=="T02"){
  run(a,n=="T01"?"STRING aa\n":"STRING ab\n");check(mock::text==(n=="T01"?"aa":"ab"),"literal output");check(lower::count==6,"fresh sync two tap/restorations cleanup");
  for(size_t i=0;i<6;++i){check(lower::calls[i].instance==0&&lower::calls[i].id==1,"actual backend id/framing");for(unsigned j=0;j<8;++j){uint8_t v=j==2&&i==1?4:j==2&&i==3?(n=="T01"?4:5):0;check(lower::calls[i].bytes[j]==v,"exact eight byte ordered report");}}
 }else if(n=="T03"){
  std::string s="STRINGLN\n\t";for(int c=32;c<=126;++c)s+=char(c);s+="\t\nEND_STRINGLN\n";run(a,s);std::string e;for(int c=32;c<=126;++c)e+=char(c);e+="\t\n";check(mock::text==String(e),"all printables dollar quotes whitespace tab newline");check(a.acks()==97,"all character whitelist through real locale/backend");
 }else if(n=="T04"){
  run(a,"ENTER\nTAB\nSPACE\nESCAPE\nBACKSPACE\nDELETE\nUPARROW\nDOWNARROW\nLEFTARROW\nRIGHTARROW\n");const uint8_t k[]={0x28,0x2b,0x2c,0x29,0x2a,0x4c,0x52,0x51,0x50,0x4f};size_t j=0;for(size_t i=0;i<lower::count;++i)if(lower::calls[i].bytes[2]){check(j<10&&lower::calls[i].bytes[2]==k[j],"all fixed named key mappings");++j;}check(j==10,"ten keys");
 }else if(n=="T05"){
  run(a,"VAR $n = 0\nFUNCTION f()\nSTRING a\nRETURN 1\nEND_FUNCTION\nWHILE $n < 3\nIF f() == 1 THEN\nSTRING b\nEND_IF\n$n = $n + 1\nEND_WHILE\n");check(mock::text=="ababab","actual expression/function/while path");
 }else if(n=="T06"||n=="T07"||n=="T08"){
  prepare(a,n=="T06"?"STRING X\nVAR $n = (1 + )\n":n=="T07"?"IF FALSE THEN\nHOLD a\nEND_IF\n":"STRING \xC3\xA4\n");check(a.state()==State::Error&&lower::count==0,"whole preflight reject no sync");
 }else if(n=="T09"||n=="T10"){
  prepare(a,"STRING a\n");if(n=="T09")attackmode::setHid(false);else keyboard_locale::setLocaleByName("DE");check(!a.start(mock::now)&&lower::count==0,"HID/layout invalid before output");
 }else if(n=="T11"){
  start(a,"STRING a\n");phase(a,"Press");size_t c=lower::count;mock::usbReady=false;for(int i=0;i<5;++i)step(a);auto s=backend_b::status();check(lower::count==c&&s.last.kind==backend_b::Kind::NoCall&&!s.last.called,"precall readiness no lower API");check(a.admissions()==1&&a.acks()==0,"no duplicate admission/ack");mock::usbReady=true;finish(a);check(a.state()==State::Completed&&mock::text=="a","known no-call polling recovers");
 }else if(n=="T12"||n=="T13"||n=="T14"||n=="T15"){
  start(a,"STRING ab\n");phase(a,(n=="T14"||n=="T15")?"Release":"Press");auto id=a.operation();lower::next=(n=="T13"||n=="T15")?lower::Outcome::FalseAfterPossibleAcceptance:lower::Outcome::FalseWithoutAcceptance;size_t before=lower::count;step(a);auto s=backend_b::status();check(s.quarantined&&s.first.kind==backend_b::Kind::CalledFalse&&s.first.called&&!s.first.returned,"real backend retained lower-called false");check(s.first.session==id.session&&s.first.operation==id.operation,"originating local identity retained");check(lower::count==before+1&&a.acks()==0,"exactly one ambiguous lower call no ack");
  auto first=s.first;for(int i=0;i<10;++i){route_b::drive(a.session());hid_backend::cancelReport();com::endScript();}
  check(lower::count==before+1,"cleanup/update/cancel cannot send after ambiguity");check(backend_b::status().first.sequence==first.sequence,"first fault retained");finish(a);check(a.state()==State::Quarantined&&a.leased()&&!a.start(mock::now),"quarantine prevents context detach/restart");
 }else if(n=="T16"){
  start(a,"STRING a\n");phase(a,"Release");size_t c=lower::count;mock::usbReady=false;for(int i=0;i<5;++i)step(a);check(lower::count==c&&a.acks()==0,"restoration unavailable no lower call");mock::usbReady=true;finish(a);check(a.state()==State::Completed&&a.acks()==1,"restoration submission required before local done");
 }else if(n=="T17"||n=="T18"||n=="T19"||n=="T20"){
  start(a,"STRING ab\n");phase(a,n=="T17"?"Press":n=="T18"?"Wait":n=="T19"?"Release":"Finish");if(n=="T20"){route_b::drive(a.session());check(route_b::result(a.session()).kind==route_b::ResultKind::Done,"done before source ack");}auto ack=a.acks();a.cancel();finish(a);check(a.state()==State::Cancelled&&a.acks()==ack&&!a.leased(),"cancel no late ack and known local cleanup");
 }else if(n=="T21"){
  start(a,"DELAY 50\nSTRING BAD\n");for(int i=0;i<1000&&!a.delayAcks();++i)step(a);a.cancel();finish(a);check(a.state()==State::Cancelled&&a.admissions()==0&&mock::text.length()==0,"Runtime-only delay cancellation");
 }else if(n=="T22"){
  start(a,"STRING a\nSTOP_PAYLOAD\nSTRING BAD\n");finish(a);check(a.state()==State::Cancelled&&mock::text=="a","STOP with real backend clearing");
 }else if(n=="T23"){
  start(a,"STRING a\n");phase(a,"Press");lower::disconnectOnReady=true;size_t c=lower::count;step(a);auto s=backend_b::status();check(lower::count==c+1&&s.quarantined&&s.first.kind==backend_b::Kind::Loss&&s.first.called,"disconnect between ready and lower retained as loss after call");finish(a);check(a.state()==State::Quarantined&&lower::count==c+1,"no cleanup send after raced loss");
 }else if(n=="T24"){
  start(a,"STRING a\n");phase(a,"Wait");mock::usbMounted=false;USB.stopped(nullptr,nullptr,ARDUINO_USB_STOPPED_EVENT,nullptr);size_t c=lower::count;step(a);finish(a);check(a.state()==State::Quarantined&&lower::count==c,"real loss event inhibits clearing retries under lease");check(backend_b::status().first.kind==backend_b::Kind::Loss,"actual backend loss latch");
 }else if(n=="T25"){
  start(a,"STRING a\n");phase(a,"Wait");mock::usbReady=false;a.cancel();check(a.leased()&&!a.start(mock::now),"pending clear blocks restart");for(int i=0;i<10;++i)step(a);check(a.state()==State::Clearing,"pre-call clear wait");mock::usbReady=true;finish(a);check(a.state()==State::Cancelled&&!a.leased(),"clear submitted then detach");auto old=backend_b::status().clearSubmitted;run(a,"STRING b\n");check(backend_b::status().clearSubmitted>old&&mock::text=="ab","fresh explicit session sync and clear");
 }else if(n=="T26"){
  start(a,"STRING a\n");phase(a,"Wait");lower::next=lower::Outcome::FalseWithoutAcceptance;size_t c=lower::count;a.cancel();finish(a);check(a.state()==State::Quarantined&&lower::count==c+1,"clearing lower false no repeated call");
 }else if(n=="T27"){
  uint8_t k=4;check(!hid_backend::beginReport(0,&k,7)&&*hid_backend::reportError(),"real stale validation error");run(a,"STRING a\n");check(mock::text=="a","known clean validation diagnostic may reset at acquire");
 }else if(n=="T28"){
  start(a,"STRING a\n");phase(a,"Press");{backend_b::Scope permit(a.session(),a.operation().operation);uint8_t k=4;check(permit&&!hid_backend::beginReport(0,&k,7),"current native invalid request");}auto s=backend_b::status();check(s.last.kind==backend_b::Kind::Invalid&&!s.last.called,"typed validation is not lower completion/error");step(a);finish(a);check(a.state()==State::Error&&a.acks()==0&&!a.leased(),"fresh local validation error clears safely, no source ack");
 }else if(n=="T29"){
  mock::usbMounted=false;USB.stopped(nullptr,nullptr,ARDUINO_USB_STOPPED_EVENT,nullptr);prepare(a,"STRING a\n");mock::usbMounted=true;check(!a.start(mock::now),"unconsumed USB callback loss rejects acquire");com::update();check(!hid_backend::takeTransportLoss(),"legacy com consumed observed loss once");check(!hid_backend::clearing(),"known legacy local clear completed");check(a.start(mock::now),"explicit start only after known local health");finish(a);check(a.state()==State::Completed,"clean new session");
 }else if(n=="T30"){
  com::onDone(callback);com::onError(callback);start(a,"STRING a\n");mock::file("competing.txt","STRING BAD\n");check(!duckscript::run("competing.txt")&&!com::executeNow("STRING BAD"),"actual script/live entries refused");com::onDone(nullptr);com::send("STRING BAD");com::sendText("BAD",false);finish(a);check(callbacks==0&&mock::text=="a","native didn't steal/fire legacy callbacks");com::beginScript();com::send("STRING b");mock::drain();check(callbacks==1&&mock::text=="ab","legacy callback remains after detach");com::endScript();
 }else if(n=="T31"){
  start(a,"STRING a\n");auto c=lower::count;uint8_t k=4;
  check(!hid_backend::beginReport(0,&k,1)&&!hid_backend::releaseReport()&&!hid_backend::hold(2,4)&&!hid_backend::release(0,4),"foreign report/ownership ingress denied");
  hid_backend::cancelReport();hid_backend::update();hid_backend::pressModifier(2);hid_backend::pressKeyHeld(4);hid_backend::pressReport(0,&k,1);hid_backend::pressKeycode(4);hid_backend::pressNamedCombo("ENTER");hid_backend::sendText("BAD");hid_backend::sendTextLn("BAD");hid_backend::releaseAll();hid_backend::pressEnter();hid_backend::begin();
  check(lower::count==c&&!hid_backend::hasPersistent()&&mock::text.length()==0,"raw helpers/lifecycle denied before key mutation/output");finish(a);check(a.state()==State::Completed&&mock::text=="a","owned route still works");
 }else if(n=="T32"||n=="T33"){
  start(a,"STRING a\n");phase(a,"Press");lower::hook=n=="T32"?interference:deferredCancel;step(a);finish(a);check(a.state()==(n=="T32"?State::Completed:State::Cancelled),"reentrant callback handling");
 }else if(n=="T34"){
  start(a,"STRING a\n");bool scope=false,sent=true;auto c=lower::count;auto session=a.session();std::thread other([&]{backend_b::Scope p(session,a.operation().operation);scope=bool(p);uint8_t k=4;sent=hid_backend::beginReport(0,&k,1);});other.join();check(!scope&&!sent&&lower::count==c,"different host thread cannot borrow owner scope");finish(a);check(a.state()==State::Completed,"owner unaffected by contention");
 }else if(n=="T35"||n=="T36"){
  start(a,"STRING a\n");phase(a,"Wait");if(n=="T35")attackmode::setHid(false);else keyboard_locale::setLocaleByName("DE");auto c=lower::count;step(a);finish(a);check(a.state()==State::Error&&a.acks()==0,"changed mode/layout terminates source");check(lower::count<=c+1,"only known clearing, no later text");
 }else if(n=="T37"){
  start(a,"STRING a\n");phase(a,"Press");mock::usbReady=false;mock::now+=Adapter::PendingMs;a.step(mock::now);check(a.fault()==Fault::Deadline,"exact pending timeout");mock::usbReady=true;finish(a);check(a.fault()==Fault::Deadline&&a.state()==State::Error,"first fault not erased by successful clear");
 }else if(n=="T38"){
  start(a,"STRING a\n");phase(a,"Wait");mock::usbReady=false;a.cancel();mock::now+=Adapter::ClearingMs;a.step(mock::now);check(a.state()==State::Quarantined&&a.leased(),"clear equality deadline retains context");
 }else if(n=="T39"){
  mock::now=UINT32_MAX-10;run(a,"DELAY 20\nSTRING a\n");check(a.delayAcks()==1&&lower::calls[1].at<100,"wrap one Runtime timer only");
 }else if(n=="T40"||n=="T41"||n=="T42"){
  if(n=="T42")backend_b::exhaustForTest();else route_b::exhaustForTest(n=="T40",n=="T41");prepare(a,"STRING a\n");if(n=="T40")check(!a.start(mock::now)&&lower::count==0,"session exhaustion before output");else{check(a.start(mock::now),"acquire for namespace test");finish(a);check(a.acks()==0&&a.state()==(n=="T41"?State::Error:State::Quarantined),"bounded operation or observation namespace exhaustion");}
 }else if(n=="T43"){
  com::beginScript();prepare(a,"STRING a\n");check(!a.start(mock::now),"prior script owner prevents start");com::endScript();hid_backend::hold(2,4);auto c=lower::count;check(!a.start(mock::now)&&lower::count==c,"persistent external owner prevents sync/clearing");hid_backend::cancelReport();check(a.start(mock::now),"only after explicit prior cleanup");finish(a);check(a.state()==State::Completed,"recovered local lease");
 }else if(n=="T44"){
  duck_random::setJitterEnabled(true);duck_random::setJitterMaximum(19);check(com::executeNow("DEFAULT_DELAY 20"),"legacy default set");mock::drain();run(a,"STRING a\n");check(duck_random::jitterEnabled()&&duck_random::jitterMaximum()==19,"global jitter preserved");auto before=mock::now;check(com::executeNow("STRING b"),"legacy after lease");mock::drain();check(mock::now-before>=25,"legacy timing restored");
 }else if(n=="T45"){
  start(a,"STRING a\n");phase(a,"Press");lower::journalLimit=lower::count;step(a);check(lower::overflowCall.bytes[2]==4&&lower::overflowCall.operation==a.operation().operation,"capacity attempt snapshot retained");check(lower::overflowAttempts==1&&backend_b::status().quarantined,"bounded lower journal exhaustion returns false and backend quarantines");for(int i=0;i<10;++i)route_b::drive(a.session());check(lower::overflowAttempts==1,"no hidden repeat after capacity fault");finish(a);check(a.state()==State::Quarantined,"capacity cleanup unresolved");
 }else if(n=="T46"){
  start(a,"STRING aa\n");phase(a,"Wait");auto old=a.operation();check(!a.inspect({{old.session,old.operation+1},route_b::ResultKind::Done})&&!a.inspect({old,route_b::ResultKind::Done}),"wrong/forged done cannot acknowledge source");for(int i=0;i<1000&&a.admissions()<2;++i)step(a);check(a.admissions()==2&&a.operation().operation!=old.operation,"identical source creates new operation");auto c=lower::count;{backend_b::Scope stale(old.session,old.operation);check(!stale,"stale operation scope cannot bind current backend");uint8_t k=4;check(!hid_backend::beginReport(0,&k,1),"stale scope denies backend mutation");}check(lower::count==c&&!a.inspect({old,route_b::ResultKind::Done}),"old success cannot acknowledge new operation");finish(a);check(a.state()==State::Completed&&a.acks()==2,"two distinct local completions");
 }else if(n=="T47"){
  hid_backend::pressKeyHeld(4);check(!hid_backend::hasPersistent(),"legacy raw Keyboard state is outside Owned");prepare(a,"STRING a\n");auto c=lower::count;check(!a.start(mock::now)&&lower::count==c,"unobserved legacy ownership refuses acquisition");hid_backend::cancelReport();check(!a.start(mock::now),"raw zero cannot clear Keyboard software ownership evidence");hid_backend::releaseAll();check(a.start(mock::now),"explicit software release permits fresh native sync");finish(a);check(a.state()==State::Completed,"fresh explicit session after legacy clear");
 }else check(false,"unknown case");
 resultAcks=a.acks();resultAdmissions=a.admissions();resultRetries=a.retries();resultDelays=a.delayAcks();finalSession=a.session();finalState=int(a.state());finalFault=int(a.fault());
 check(mock::blockingDelays==0,"native route has no blocking legacy helper calls");
#ifdef STAGE28T_NEGATIVE_CONTROL
 check(false,"deliberate negative control");
#endif
}
static void quote(const std::string&s){std::cout<<'"';for(unsigned char c:s){if(c=='"'||c=='\\')std::cout<<'\\'<<c;else if(c=='\n')std::cout<<"\\n";else if(c=='\t')std::cout<<"\\t";else if(c<32||c>126)std::cout<<'?';else std::cout<<c;}std::cout<<'"';}
int main(int argc,char**argv){if(argc!=2)return 2;try{auto allocBefore=native_alloc::calls(),bytesBefore=native_alloc::bytes();test(argv[1]);auto allocCalls=native_alloc::calls()-allocBefore,allocBytes=native_alloc::bytes()-bytesBefore;auto s=backend_b::status();std::cout<<"PASS "<<argv[1]<<" ("<<assertions<<" assertions)\nTRACE {\"programs\":[";for(size_t i=0;i<programs.size();++i){if(i)std::cout<<',';quote(programs[i]);}std::cout<<"],\"session\":"<<finalSession<<",\"admissions\":"<<resultAdmissions<<",\"local_acks\":"<<resultAcks<<",\"retries\":"<<resultRetries<<",\"delay_acks\":"<<resultDelays<<",\"state\":"<<finalState<<",\"fault\":"<<finalFault<<",\"quarantined\":"<<(s.quarantined?"true":"false")<<",\"first_kind\":"<<int(s.first.kind)<<",\"first_operation\":"<<s.first.operation<<",\"clear_request\":"<<s.clearRequest<<",\"clear_submitted\":"<<s.clearSubmitted<<",\"denied\":"<<s.denied<<",\"overflow_attempts\":"<<lower::overflowAttempts<<",\"cpp_new_calls_with_fixture\":"<<allocCalls<<",\"cpp_new_bytes_with_fixture\":"<<allocBytes<<",\"backend_shared_bytes\":"<<backend_b::sharedStorageBytes()<<",\"backend_thread_bytes\":"<<backend_b::perThreadStorageBytes()<<",\"adapter_bytes\":"<<sizeof(Adapter)<<",\"calls\":[";for(size_t i=0;i<lower::count;++i){auto&c=lower::calls[i];if(i)std::cout<<',';std::cout<<"{\"at\":"<<c.at<<",\"session\":"<<c.session<<",\"operation\":"<<c.operation<<",\"phase\":\""<<c.phase<<"\",\"clear\":"<<(c.clear?"true":"false")<<",\"outcome\":"<<int(c.outcome)<<",\"id\":"<<unsigned(c.id)<<",\"instance\":"<<unsigned(c.instance)<<",\"bytes\":[";for(int j=0;j<8;++j){if(j)std::cout<<',';std::cout<<unsigned(c.bytes[j]);}std::cout<<"]}";}std::cout<<"]}\n";return 0;}catch(const std::exception&e){std::cerr<<"FAIL "<<argv[1]<<": "<<e.what()<<" ("<<assertions<<")\n";return 1;}}
