#include "adapter.h"
#include "backend.h"
#include "host.h"
#include "com.h"
#include "duckscript.h"
#include "hid_backend.h"
#include "attackmode.h"
#include "keyboard_locale.h"
#include "duck_random.h"
#include <iostream>
#include <stdexcept>
#include <string>
#include <cstring>
#include <climits>
using native_b::Adapter;using native_b::State;using native_b::Fault;
static unsigned assertions=0;static uint64_t finalSession=0,finalOperation=0;static uint32_t finalAdmissions=0,finalAcks=0,finalRetries=0,finalDelays=0;static int finalState=0,finalFault=0;static std::string sourceRecord;static std::vector<std::string> programs;static Adapter* current=nullptr;
static void check(bool b,const char* why){++assertions;if(!b)throw std::runtime_error(why);}
static bool terminal(State s){return s==State::Completed||s==State::Cancelled||s==State::Error||s==State::Quarantined;}
static void step(Adapter& a,uint32_t delta=1){mock::now+=delta;a.step(mock::now);}
static void prepare(Adapter& a,const std::string& s){sourceRecord=s;programs.push_back(s);check(a.prepare(s.c_str(),s.size()),"prepare accepted");for(int i=0;i<10000&&(a.state()==State::Loading||a.state()==State::Compiling);++i)step(a,0);}
static void run(Adapter& a,const std::string& s){prepare(a,s);check(a.state()==State::Ready,"compile/cap ready");check(a.start(mock::now),"exclusive acquired");for(int i=0;i<10000&&!terminal(a.state());++i)step(a);check(a.state()==State::Completed,"completed local scheduler");check(a.fault()==Fault::None,"no fault");check(a.admissions()==a.acks(),"every local operation acked once");check(!a.leased()&&!route_b::active(),"detached after clearing");}
static void until(Adapter& a,const char* phase){for(int i=0;i<10000;++i){if(a.state()==State::Running&&std::strcmp(route_b::phase(),phase)==0)return;step(a);}check(false,"phase reached");}
static void finish(Adapter& a){for(int i=0;i<10000&&!terminal(a.state());++i)step(a);check(terminal(a.state()),"terminal bounded");}
static void identity(uint64_t &s,uint64_t &op){s=current->session();op=current->operation().operation;}
static unsigned callbacks=0;static void callback(){++callbacks;}
static void reenter(){check(current!=nullptr,"callback context valid");check(!current->start(mock::now),"callback start rejected");auto before=current->admissions();current->step(mock::now);check(current->admissions()==before,"callback tick no mutation");check(!com::executeNow("STRING X"),"live owner rejected");}
static void cancelHook(){current->cancel();check(!current->start(mock::now),"callback cancellation cannot restart");}
static unsigned readCalls=0;static int readerMode=0;static ds_preview::MemoryReader external{};
static ds_preview::ReadResult read(void* c,char* b,size_t n){++readCalls;if(readerMode==1&&readCalls==1)return {ds_preview::ReadStatus::Retry,0};if(readerMode==2)return {ds_preview::ReadStatus::Error,0};if(readerMode==3)return {ds_preview::ReadStatus::Eof,0};return ds_preview::MemoryReader::read(c,b,n);}
static bool seek(void* c,size_t n){return readerMode!=4&&ds_preview::MemoryReader::seek(c,n);}
static void test(const std::string& n){
 mock::reset();fixture::reset();callbacks=0;
 Adapter a;current=&a;fixture::identity=identity;
 if(n=="S01"||n=="S02"){
  run(a,n=="S01"?"STRING aa\n":"STRING ab\n");check(mock::text==(n=="S01"?"aa":"ab"),"exact repeated/distinct visible text");check(a.admissions()==2,"two distinct ids");check(fixture::count==6,"sync two taps and terminal clear");for(size_t i=0;i<6;++i)for(unsigned j=0;j<8;++j){uint8_t expected=(j==2&&i==1)?4:(j==2&&i==3)?(n=="S01"?4:5):0;check(fixture::calls[i].bytes[j]==expected,"exact ordered eight-byte tap/restoration");}
 }else if(n=="S03"){
  run(a,"VAR $n = 0\nFUNCTION say()\nSTRING a\nRETURN 1\nEND_FUNCTION\nWHILE $n < 3\nIF say() == 1 THEN\nSTRING b\nEND_IF\n$n = $n + 1\nEND_WHILE\n");check(mock::text=="ababab","loop/function expression output");uint16_t value=0;check(a.runtime().variable("$n",value)&&value==3,"numeric variable retained");
 }else if(n=="S04"){
  // All95 printable ASCII, plus tab/newline. Single block avoids command/quote syntax.
  std::string s="STRINGLN\n\t";for(int c=32;c<=126;++c)s+=char(c);s+="\t\nEND_STRINGLN\n";run(a,s);std::string expected;for(int c=32;c<=126;++c)expected+=char(c);expected+="\t\n";check(mock::text==String(expected),"entire exact ASCII whitelist including literal dollar/quotes/spaces/tab");check(a.acks()==97,"95 printables tab enter");
 }else if(n=="S05"){
  run(a,"ENTER\nTAB\nSPACE\nESCAPE\nBACKSPACE\nDELETE\nUPARROW\nDOWNARROW\nLEFTARROW\nRIGHTARROW\n");const uint8_t keys[]={0x28,0x2b,0x2c,0x29,0x2a,0x4c,0x52,0x51,0x50,0x4f};size_t j=0;for(size_t i=0;i<fixture::count;++i)if(fixture::calls[i].bytes[2]){check(j<10&&fixture::calls[i].bytes[2]==keys[j],"named fixed key mapping");++j;}check(j==10,"all ten mappings");
 }else if(n=="S06"||n=="S07"||n=="S08"||n=="S09"){
  std::string s=n=="S06"?"STRING X\nVAR $a = (5 + )\n":n=="S07"?"IF FALSE THEN\nHOLD a\nEND_IF\n":n=="S08"?"FUNCTION x()\nRELEASE a\nEND_FUNCTION\n":"STRING \xC3\xA4\n";
  prepare(a,s);check(a.state()==State::Error,"whole program rejected");check(fixture::count==0&&!a.start(mock::now),"rejection zero backend output");
 }else if(n=="S10"||n=="S11"){
  prepare(a,"STRING a\n");if(n=="S10")attackmode::setHid(false);else keyboard_locale::setLocaleByName("DE");check(!a.start(mock::now)&&fixture::count==0,"invalid HID/layout refused before sync");if(n=="S10"){attackmode::setHid(true);fixture::persistent=true;check(!a.start(mock::now)&&fixture::count==0,"foreign persistent owner refused without clearing");}
 }else if(n=="S12"){
  prepare(a,"STRING a\n");check(a.start(mock::now),"start");until(a,"Press");fixture::next=fixture::Outcome::RefuseBeforeAdmission;step(a);check(a.admissions()==1&&a.acks()==0,"not ack on queue refusal");finish(a);check(a.state()==State::Completed&&a.admissions()==1&&a.acks()==1,"one admission after retries");check(mock::text=="a","one press only");
 }else if(n=="S13"||n=="S14"){
  prepare(a,"STRING ab\n");check(a.start(mock::now),"start");until(a,"Press");fixture::next=n=="S13"?fixture::Outcome::Ambiguous:fixture::Outcome::FailBeforeAdmission;step(a);finish(a);check(a.acks()==0&&a.admissions()==1,"failed or ambiguous no ack/resubmit");check(a.fault()==Fault::Backend,"original backend fault");check(a.state()==(n=="S13"?State::Quarantined:State::Error),"ambiguous cleanup retained vs safe error");
 }else if(n=="S15"||n=="S16"||n=="S17"){
  prepare(a,"STRING a\n");check(a.start(mock::now),"start");until(a,"Release");fixture::next=n=="S15"?fixture::Outcome::RefuseBeforeAdmission:n=="S16"?fixture::Outcome::FailBeforeAdmission:fixture::Outcome::Ambiguous;step(a);check(a.acks()==0,"no ack restoration refusal");finish(a);check(a.state()==(n=="S15"?State::Completed:n=="S16"?State::Error:State::Quarantined),"restoration error correct");check(a.admissions()==1,"never duplicate admitted text");
 }else if(n=="S18"||n=="S19"||n=="S20"||n=="S21"||n=="S22"){
  prepare(a,"STRING ab\n");check(a.start(mock::now),"start");until(a,n=="S18"?"Press":n=="S19"?"Wait":n=="S20"?"Release":"Finish");auto id=a.operation();auto before=a.acks();if(n=="S22"){com::update();check(route_b::result(a.session()).kind==route_b::ResultKind::Done,"local Done before source ack");}a.cancel();finish(a);check(a.state()==State::Cancelled&&a.acks()==before,"cancel no later source acceptance");check(!a.inspect({id,route_b::ResultKind::Done}),"late success cannot revive cancel");check(!a.leased(),"cancel clearing locally detached");
 }else if(n=="S23"){
  prepare(a,"DELAY 50\nSTRING X\n");check(a.start(mock::now),"start");for(int i=0;i<1000&&!a.delayAcks();++i)step(a);a.cancel();finish(a);check(a.state()==State::Cancelled&&a.admissions()==0&&mock::text.length()==0,"cancel Runtime delay");
 }else if(n=="S24"){
  prepare(a,"STRING a\nSTOP_PAYLOAD\nSTRING wrong\n");check(a.start(mock::now),"start");finish(a);check(a.state()==State::Cancelled&&mock::text=="a","STOP terminal prevents remaining output");
 }else if(n=="S25"||n=="S26"||n=="S27"){
  prepare(a,"STRING ab\n");check(a.start(mock::now),"start");until(a,n=="S25"?"Press":"Wait");if(n=="S27")attackmode::setHid(false);else mock::usbMounted=false;step(a);check(a.state()==State::Clearing,"loss cancels source");finish(a);check(a.acks()==0,"no loss ack");check(a.state()==(n=="S27"?State::Error:State::Quarantined),"local clear allowed after HID mode loss but not disconnect");
 }else if(n=="S28"){
  prepare(a,"STRING a\n");check(a.start(mock::now),"start");until(a,"Wait");fixture::clearRefused=true;a.cancel();auto requests=fixture::clearRequests;check(!a.start(mock::now),"pending clear blocks restart");for(int i=0;i<10;++i)step(a);check(a.state()==State::Clearing&&a.leased(),"old owner retained");a.cancel();check(fixture::clearRequests==requests,"cancel end invoked once");fixture::clearRefused=false;finish(a);check(a.state()==State::Cancelled&&!a.leased(),"clear recover then detach");run(a,"STRING b\n");check(mock::text=="ab","explicit fresh session");
 }else if(n=="S29"){
  prepare(a,"STRING a\n");check(a.start(mock::now),"start");until(a,"Wait");fixture::clearAmbiguous=true;a.cancel();finish(a);check(a.state()==State::Quarantined&&a.leased(),"clear failure unresolved");check(!a.start(mock::now),"quarantine no restart");
 }else if(n=="S30"){
  com::onDone(callback);com::onError(callback);prepare(a,"STRING a\n");check(a.start(mock::now),"start");check(!com::executeNow("STRING BAD"),"competing live refused");mock::file("competing.txt","STRING BAD\n");check(!duckscript::run("competing.txt")&&!duckscript::running(),"actual production script entry refuses native lease even between operations");com::send("STRING BAD");com::sendText("BAD",false);com::beginScript();com::endScript();com::onDone(nullptr);finish(a);check(mock::text=="a"&&callbacks==0,"legacy callbacks untouched and suppressed under lease");check(com::executeNow("STRING b"),"legacy resumes after detach");mock::drain();check(callbacks==0,"live callback not falsely script-owned");com::beginScript();com::send("STRING c");mock::drain();check(callbacks==1,"original callback retained");com::endScript();
 }else if(n=="S31"||n=="S32"){
  prepare(a,"STRING a\n");check(a.start(mock::now),"start");until(a,"Press");fixture::hook=n=="S31"?reenter:cancelHook;step(a);finish(a);check(a.state()==(n=="S31"?State::Completed:State::Cancelled),"callback reentry handled");
 }else if(n=="S33"){
  com::beginScript();prepare(a,"STRING a\n");check(!a.start(mock::now)&&fixture::count==0,"legacy script owner blocks K01-style start");com::endScript();check(com::executeNow("DELAY 20"),"legacy queued work");check(!a.start(mock::now),"busy action blocks start");mock::drain();check(a.start(mock::now),"start only after prior work");finish(a);check(a.state()==State::Completed,"complete");
 }else if(n=="S34"){
  mock::now=UINT32_MAX-10;run(a,"DELAY 20\nSTRING a\n");check(a.delayAcks()==1,"one Runtime delay acceptance");check(fixture::calls[1].time<100,"wrap correct no double timer");check(mock::text=="a","delay preserves text");
 }else if(n=="S35"){
  prepare(a,"STRING a\n");check(a.start(mock::now),"start");until(a,"Press");auto began=mock::now;mock::usbReady=false;mock::now=began+Adapter::PendingMs; a.step(mock::now);check(a.fault()==Fault::Deadline&&a.acks()==0,"exact equality timeout");mock::usbReady=true;finish(a);check(a.fault()==Fault::Deadline,"first fault retained through clear");
 }else if(n=="S36"){
  duck_random::setJitterEnabled(true);duck_random::setJitterMaximum(31);run(a,"STRING ab\n");check(duck_random::jitterEnabled()&&duck_random::jitterMaximum()==31,"session did not rewrite global jitter");uint32_t press=0;unsigned seen=0;for(size_t i=0;i<fixture::count;++i)if(fixture::calls[i].bytes[2]){if(!seen)press=fixture::calls[i].time;++seen;}check(seen==2&&fixture::calls[fixture::count-1].time-press<30,"native zero jitter but real dwell");
 }else if(n=="S37"||n=="S38"||n=="S39"||n=="S40"){
  const char* s="STRING a\n";sourceRecord=s;programs.push_back(s);external={s,strlen(s),0};readerMode=n=="S37"?1:n=="S38"?2:n=="S39"?3:4;readCalls=0;
  bool ok=a.prepare({read,seek,&external,strlen(s)});if(n=="S40")check(!ok,"failed initial seek");else{check(ok,"reader begin");for(int i=0;i<10000&&(a.state()==State::Loading||a.state()==State::Compiling);++i)step(a,0);}
  if(n=="S37"){check(a.state()==State::Ready,"Retry then compile");check(a.start(mock::now),"start");finish(a);check(mock::text=="a","Reader source correct");}else check(a.state()==State::Error&&fixture::count==0,"read/eof/seek failure zero output");
 }else if(n=="S41"){
  const char* s="STRING a\n";sourceRecord=s;programs.push_back(s);check(a.prepare(s,strlen(s)),"load start");step(a);a.cancel();check(a.state()==State::Cancelled&&fixture::count==0,"loading cancel");check(a.prepare(s,strlen(s)),"new compile");for(int i=0;i<1000&&a.state()!=State::Compiling;++i)step(a);a.cancel();check(a.state()==State::Cancelled&&fixture::count==0,"compilation cancel releases borrow");run(a,"STRING b\n");
 }else if(n=="S42"||n=="S43"){
  route_b::exhaustForTest(n=="S42",n=="S43");prepare(a,"STRING a\n");if(n=="S42")check(!a.start(mock::now)&&fixture::count==0,"session exhaustion before output");else{check(a.start(mock::now),"old cleanup allowed");finish(a);check(a.state()==State::Error&&a.admissions()==0&&!a.leased(),"op exhaustion fail before admission, cleanup works");}
 }else if(n=="S44"){
  prepare(a,"STRING aa\n");check(a.start(mock::now),"start");until(a,"Wait");auto id=a.operation();check(!a.inspect({{id.session,id.operation+1},route_b::ResultKind::Done}),"wrong operation");check(!a.inspect({{id.session+1,id.operation},route_b::ResultKind::Done}),"wrong session");check(!a.inspect({id,route_b::ResultKind::Done}),"manufactured premature Done rejected");check(a.acks()==0,"no synthetic ack");finish(a);check(a.acks()==2&&a.admissions()==2,"old/repeated output operations distinct");check(!a.inspect({id,route_b::ResultKind::Done}),"late duplicate terminal ignored");
 }else if(n=="S45"){
  prepare(a,"DELAY 1\nSTRING a\n");check(a.start(mock::now),"start");for(int i=0;i<2000&&!a.delayAcks();++i)step(a,0);check(a.delayAcks()==1,"one delay owner");for(int i=0;i<5;++i)step(a,0);check(a.admissions()==0,"stuck caller clock no delay progress");step(a,1);finish(a);check(a.state()==State::Completed&&a.admissions()==1,"exact delay boundary");
 }else if(n=="S46"){
  run(a,"DELAY 0\n");check(mock::text.length()==0&&a.admissions()==0&&a.delayAcks()==1,"numeric-only no key");auto clear=fixture::clearSubmitted;run(a,"STRING a\n");check(fixture::clearSubmitted>=clear+2,"new session has fresh sync and terminal clear");
 }else if(n=="S47"){
  prepare(a,"DELAY 0\n");check(a.start(mock::now),"lease");route_b::Id id{};for(uint16_t v:{uint16_t(0),uint16_t(8),uint16_t(11),uint16_t(13),uint16_t(31),uint16_t(127),uint16_t(128),uint16_t(65535)})check(route_b::character(a.session(),v,id)==route_b::Admission::Rejected,"invalid ASCII rejected");for(uint16_t v:{uint16_t(0),uint16_t(4),uint16_t(0x3a),uint16_t(0xe0),uint16_t(256),uint16_t(65535)})check(route_b::key(a.session(),v,id)==route_b::Admission::Rejected,"invalid fixed key rejected");finish(a);check(a.state()==State::Completed,"rejection did not mutate lease");
 }else if(n=="S48"){
  prepare(a,"STRING b\n");check(a.start(mock::now),"lease");route_b::Id id{};check(route_b::character(a.session(),'a',id)==route_b::Admission::Admitted,"prior local action");step(a);check(a.state()==State::Clearing&&a.admissions()==0,"K01 local action prevents Runtime start");finish(a);check(a.state()==State::Error,"prior operation isolated and cancelled");
 }else if(n=="S49"){
  check(com::executeNow("DEFAULT_DELAY 20"),"legacy default configured");mock::drain();duck_random::setJitterEnabled(true);duck_random::setJitterMaximum(10);run(a,"STRING a\n");check(duck_random::jitterEnabled()&&duck_random::jitterMaximum()==10,"native session preserved jitter config");uint32_t began=mock::now;check(com::executeNow("STRING b"),"legacy command after native");mock::drain();check(uint32_t(mock::now-began)>=25,"legacy default-delay restored and dwell retained");
 }else if(n=="S50"){
  prepare(a,"STRING a\n");check(a.start(mock::now),"start");until(a,"Wait");fixture::clearRefused=true;a.cancel();uint32_t began=mock::now;mock::now=began+Adapter::ClearingMs;a.step(mock::now);check(a.state()==State::Quarantined&&a.leased()&&a.fault()==Fault::Clearing,"exact clear equality retains unresolved lease");
 }else if(n=="S51"){
  prepare(a,"VAR $x = 1\nIF FALSE THEN\nHOLD a\nEND_IF\n");check(a.state()==State::Error&&fixture::count==0,"source ownership in inactive code rejected statically");
 }else if(n=="S52"){
  char s[]="STRING a\n";sourceRecord=s;programs.push_back(s);check(a.prepare(s,strlen(s)),"copy start");for(int i=0;i<10000&&a.state()!=State::Ready;++i)step(a,0);s[7]='z';check(a.start(mock::now),"start immutable compiled copy");finish(a);check(mock::text=="a","caller mutation after completed capture cannot alter owned Program");
 }else if(n=="S53"){
  prepare(a,"VAR $x = 1\nVAR $d = 0\n$x = $x / $d\nSTRING X\n");check(a.state()==State::Ready,"runtime-only variable division valid structural compile");check(a.start(mock::now),"start");finish(a);check(a.state()==State::Error&&a.fault()==Fault::Runtime&&a.runtime().error().line==3&&mock::text.length()==0,"runtime error precise line and no key output");
 }else if(n=="S54"){
  std::string s(ds_preview::MaxSource+1,'a');sourceRecord=s;programs.push_back(s);check(!a.prepare(s.c_str(),s.size())&&a.state()==State::Error&&fixture::count==0,"source bound fails before output");
 }else if(n=="S55"){
  prepare(a,"STRING a\n");check(a.start(mock::now),"start");until(a,"Press");mock::usbReady=false;for(unsigned i=0;i<Adapter::PendingTurns+5&&!terminal(a.state())&&a.state()!=State::Clearing;++i)step(a,0);check(a.fault()==Fault::Deadline&&a.acks()==0,"pending turn bound with stuck clock");mock::usbReady=true;finish(a);
 }else if(n=="S56"){
  run(a,"STRINGLN\n\tVAR $x = 1\n\tRESET\n\tSTRING nope\nEND_STRINGLN\n");check(mock::text=="VAR $x = 1\nRESET\nSTRING nope\n","literal command-looking text not interpreted/interpolated");
 }else check(false,"unknown test");
 finalSession=a.session();finalOperation=a.operation().operation;finalAdmissions=a.admissions();finalAcks=a.acks();finalRetries=a.retries();finalDelays=a.delayAcks();finalState=int(a.state());finalFault=int(a.fault());
#ifndef STAGE28S_NEGATIVE_CONTROL
 check(mock::blockingDelays==0,"cooperative production scheduler no delay call");
#else
 check(false,"deliberate negative control");
#endif
}
static void quoted(const std::string&s){std::cout<<'"';for(unsigned char c:s){if(c=='"'||c=='\\')std::cout<<'\\'<<c;else if(c=='\n')std::cout<<"\\n";else if(c=='\t')std::cout<<"\\t";else if(c<32||c>126)std::cout<<'?';else std::cout<<c;}std::cout<<'"';}
int main(int argc,char**argv){if(argc!=2)return 2;try{test(argv[1]);std::cout<<"PASS "<<argv[1]<<" ("<<assertions<<" assertions)\n";std::cout<<"TRACE {\"source\":";quoted(sourceRecord);std::cout<<",\"programs\":[";for(size_t i=0;i<programs.size();++i){if(i)std::cout<<',';quoted(programs[i]);}std::cout<<']';std::cout<<",\"session\":"<<finalSession<<",\"last_operation\":"<<finalOperation<<",\"admissions\":"<<finalAdmissions<<",\"local_acks\":"<<finalAcks<<",\"retries\":"<<finalRetries<<",\"delay_acks\":"<<finalDelays<<",\"terminal_state\":"<<finalState<<",\"first_fault\":"<<finalFault<<",\"adapter_bytes_native\":"<<sizeof(Adapter)<<",\"calls\":[";for(size_t i=0;i<fixture::count;++i){if(i)std::cout<<',';auto&c=fixture::calls[i];std::cout<<"{\"at\":"<<c.time<<",\"session\":"<<c.session<<",\"operation\":"<<c.operation<<",\"phase\":\""<<c.phase<<"\",\"outcome\":"<<int(c.outcome)<<",\"clear\":"<<(c.clearing?"true":"false")<<",\"bytes\":[";for(int j=0;j<8;++j){if(j)std::cout<<',';std::cout<<unsigned(c.bytes[j]);}std::cout<<"]}";}std::cout<<"]}\n";return 0;}catch(const std::exception&e){std::cerr<<"FAIL "<<argv[1]<<": "<<e.what()<<" ("<<assertions<<")\n";return 1;}}
