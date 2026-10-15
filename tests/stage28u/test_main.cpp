#include "coordinator.h"
#include "task_platform.h"
#include "host.h"
#include "duckscript.h"
#include "com.h"
#include "hid_backend.h"
#include "backend_lease.h"
#include "scheduler_seam.h"
#include "lower.h"
#include "cli.h"
#include "USB.h"
#include <FS.h>
#include "allocations.h"
#include "attackmode.h"
#include "keyboard_locale.h"
#include "settings.h"
#include "execution_guard.h"
#include <thread>
#include <iostream>
#include <stdexcept>
#include <string>
static unsigned assertions=0;static unsigned phases[10]{};static unsigned retries=0;
namespace usb_msc_test {extern bool active,preparing;}
static void check(bool b,const char* m){++assertions;if(!b)throw std::runtime_error(m);}
static void tick(){++mock::now;duckscript::update();com::update();++phases[unsigned(route_u::status().phase)];}
static void done(){for(unsigned i=0;i<20000&&route_u::owned()&&route_u::status().phase!=route_u::Phase::Quarantined;++i)tick();check(!route_u::owned()||route_u::status().phase==route_u::Phase::Quarantined,"bounded terminal");}
static void until(route_u::Phase p){for(unsigned i=0;i<20000;++i){if(route_u::status().phase==p)return;tick();}check(false,"phase reachable");}
static void put(const std::string&s,const char* path="x.txt"){mock::file(path,s.c_str());}
static void start(const std::string&s){put(s);check(duckscript::runRouteB("x.txt"),"explicit accepted");check(duckscript::running()&&com::busy(),"queued ownership visible");}
static bool retryPoll(){return ++retries>5;}
static bool neverRead(){return false;}
static void reenter(){auto n=lower::count;u_platform::taskForTest(2);uint8_t k=4;check(!hid_backend::beginReport(0,&k,1),"foreign direct report refused");com::send("STRING BAD");u_platform::taskForTest(1);route_u::tick(mock::now);hid_backend::pressKeycode(4);check(lower::count==n,"reentrant owner update and helper rejected");route_u::stop();}
static void printLine(const char*s){mock::output+=s;}
int main(int argc,char**argv){
 if(argc!=2)return 2;
 try{auto allocBefore=native_alloc::calls(),bytesBefore=native_alloc::bytes();
 mock::reset();lower::reset();hid_backend::begin();com::update();lower::count=0;mock::reports.clear();mock::text="";
 std::string id=argv[1];if(id!="U01")check(route_u::bindOwner(),"owner bound");
 if(id=="U01") {put("STRING a\n");check(route_u::requestStart("x.txt")==route_u::Reply::Unbound,"no implicit owner");check(!route_u::owned()&&lower::count==0,"unbound no output");}
 else if(id=="U02"){put("STRING a\n");check(duckscript::run("x.txt"),"legacy default");check(!route_u::owned(),"no implicit mode switch");mock::drain();check(mock::text=="a","legacy output");}
 else if(id=="U03"||id=="U04"){start(id=="U03"?"STRING aa\n":"STRING ab\n");done();check(mock::text==(id=="U03"?"aa":"ab"),"actual file scheduler output");check(route_u::status().reason==route_u::Reason::Completed&&!File::opened(),"closed complete");check(lower::count==6,"sync taps restorations clear");for(size_t i=0;i<6;++i){for(unsigned j=0;j<8;++j){uint8_t expected=j==2&&i==1?4:j==2&&i==3?(id=="U03"?4:5):0;check(lower::calls[i].bytes[j]==expected&&lower::calls[i].id==1,"exact report bytes");}}}
 else if(id=="U05"){start("VAR $n = 0\nFUNCTION f()\nSTRING a\nRETURN 1\nEND_FUNCTION\nWHILE $n < 2\nIF f() == 1 THEN\nSTRING b\nEND_IF\n$n = $n + 1\nEND_WHILE\n");done();check(mock::text=="abab","loop function program");}
 else if(id=="U06"){std::string s;for(int i=0;i<1365;++i)s+="REM x\n";s+=" \n";check(s.size()==8192,"exact cap");start(s);done();check(route_u::status().reason==route_u::Reason::Completed,"exact cap accepted");}
 else if(id=="U07"){start(std::string(8193,' '));done();check(lower::count==0&&route_u::status().reason==route_u::Reason::File,"oversize before HID");}
 else if(id=="U08"){start("");done();check(mock::text.length()==0&&lower::count==2,"empty sync and clear only");}
 else if(id=="U09"){mock::readLimit=3;start("STRING ab\n");done();check(mock::text=="ab"&&mock::readCalls>6,"partial reads assembled by actual capture");}
 else if(id=="U10"){route_u::setReadPollForTest(retryPoll);start("STRING a\n");done();check(retries>5&&mock::text=="a","bounded poll Retry no read/submission duplication");}
 else if(id=="U11"){check(duckscript::runRouteB("missing.txt"),"queued missing");done();check(lower::count==0&&route_u::status().reason==route_u::Reason::File,"open error clean");}
 else if(id=="U12"){mock::failSeekAt=0;start("STRING a\n");done();check(lower::count==0&&!File::opened(),"seek failure closed");}
 else if(id=="U13"){mock::failReadAt=4;start("STRING a\n");done();check(lower::count==0&&route_u::status().reason==route_u::Reason::File,"truncated read refused");}
 else if(id=="U14"||id=="U15"){start("STRING a\n");tick();if(id=="U14")mock::sourceSizeIncrease=1;else File::mutate(0,'X');done();check(lower::count==0&&route_u::status().reason==route_u::Reason::File,"changed size or equal-size content rejected before HID");}
 else if(id=="U16"){start("STRING X\nVAR $n = (1 + )\n");done();check(lower::count==0&&route_u::status().reason==route_u::Reason::Compiler&&route_u::status().line==2,"preflight line retained no payload log");}
 else if(id=="U17"){start("IF FALSE THEN\nHOLD a\nEND_IF\n");done();check(lower::count==0&&route_u::status().reason==route_u::Reason::Capability,"inactive ownership rejected");}
 else if(id=="U18"||id=="U19"||id=="U20"||id=="U21"){
 start("DELAY 20\nSTRING ab\n");if(id=="U19")until(route_u::Phase::Capturing);if(id=="U20")until(route_u::Phase::Compiling);if(id=="U21")until(route_u::Phase::Running);duckscript::stop();done();check(!route_u::owned()&&!File::opened()&&mock::text.length()==0,"STOP actual engine and file lifetime");}
 else if(id=="U22"){start("STRING a\n");until(route_u::Phase::Verifying);duckscript::stop();done();check(lower::count==0&&!File::opened(),"STOP preflight verification");}
 else if(id=="U23"){start("STRING a\n");until(route_u::Phase::Stopping);duckscript::stop();done();check(!route_u::owned()&&!hid_backend::clearing(),"STOP clearing finishes known local release");}
 else if(id=="U24"){start("STRING a\n");while(std::string(route_b::phase())!="Press")tick();lower::next=lower::Outcome::FalseAfterPossibleAcceptance;tick();auto n=lower::count;done();for(int i=0;i<10;++i)tick();check(route_u::status().phase==route_u::Phase::Quarantined&&route_u::owned()&&duckscript::running(),"ambiguous quarantine visible");check(lower::count==n&&backend_b::status().first.called,"actual backend suppresses attempts");check(!duckscript::runRouteB("x.txt"),"no restart");}
 else if(id=="U25"){start("STRING a\n");while(std::string(route_b::phase())!="Wait")tick();mock::usbMounted=false;USB.stopped(nullptr,nullptr,ARDUINO_USB_STOPPED_EVENT,nullptr);auto n=lower::count;done();check(route_u::status().phase==route_u::Phase::Quarantined&&lower::count==n,"loss no cleanup send");}
 else if(id=="U26"){start("STRING a\n");u_platform::taskForTest(2);check(!route_u::bindOwner(),"no owner reassignment");auto n=mock::readCalls;duckscript::update();check(mock::readCalls==n,"foreign update no File work");uint8_t k=4;check(!hid_backend::beginReport(0,&k,1),"foreign before backend acquire rejected");u_platform::taskForTest(1);done();check(mock::text=="a","owner progresses");}
 else if(id=="U27"){start("STRING ab\n");while(std::string(route_b::phase())!="Press")tick();lower::hook=reenter;tick();done();check(!route_u::owned()&&mock::text!="ab","reentry no later source tick after priority STOP");}
 else if(id=="U28"||id=="U29"){start("STRING BAD\n");for(unsigned i=0;i<3;++i)check(route_u::requestSnapshot(i)==route_u::Reply::Accepted,"fill ordinary queue");check(route_u::requestSnapshot(7)==route_u::Reply::QueueFull,"queue full");if(id=="U28")duckscript::stop();else route_u::loss();done();check(lower::count==0&&!route_u::owned(),"priority outside saturated queue");}
 else if(id=="U30"||id=="U31"||id=="U32"||id=="U33"){
 route_u::Token t;auto s=id=="U30"?route_u::Service::Settings:id=="U31"?route_u::Service::Files:id=="U32"?route_u::Service::Upload:route_u::Service::Ota;check(route_u::begin(s,t),"service transaction admitted");put("STRING a\n");check(!duckscript::runRouteB("x.txt"),"transaction blocks capture before open");check(!File::opened(),"no file handle side effect");check(route_u::valid(t)&&!route_u::end({t.id+1}),"stale finish cannot release");u_platform::taskForTest(2);check(route_u::valid(t),"multi-callback explicit identity remains");check(route_u::end(t)&&!route_u::valid(t),"completion or abort releases once");u_platform::taskForTest(1);check(duckscript::runRouteB("x.txt"),"explicit subsequent start");done();}
 else if(id=="U34"){start("STRING a\n");for(auto s:{route_u::Service::Settings,route_u::Service::Files,route_u::Service::Upload,route_u::Service::Ota,route_u::Service::Layout,route_u::Service::Hid,route_u::Service::Storage,route_u::Service::Restart}){route_u::Token t;check(!route_u::begin(s,t)&&!t.id,"all conflict admission before mock side effect");}done();}
 else if(id=="U35"){start("STRING a\n");cli::parse("set ssid harmless",printLine,false);check(mock::output.indexOf("Busy")>=0,"actual CLI mutation ingress rejected");cli::parse("status",printLine,false);cli::parse("stop",printLine,false);done();check(lower::count==0,"CLI STOP routed preparing engine");}
 else if(id=="U36"){put("STRING a\n");check(duckscript::run("x.txt"),"legacy started");check(!duckscript::runRouteB("x.txt"),"no native over legacy");duckscript::stop();check(!duckscript::running(),"legacy STOP unchanged");}
 else if(id=="U37"||id=="U38"){put("STRING a\n");if(id=="U37")hid_backend::hold(2,4);else hid_backend::pressKeyHeld(4);check(!duckscript::runRouteB("x.txt")&&!File::opened(),"held or raw blocks request before capture");}
 else if(id=="U39"){put("STRING a\n");mock::usbReady=false;hid_backend::cancelReport();check(!duckscript::runRouteB("x.txt"),"unresolved clear blocks capture");}
 else if(id=="U40"){route_u::exhaustForTest();put("STRING a\n");check(route_u::requestStart("x.txt")==route_u::Reply::Exhausted,"no ID wrap");route_u::Token t;check(!route_u::begin(route_u::Service::Settings,t),"transaction namespace bounded");}
 else if(id=="U41"){check(route_u::requestStart(nullptr)==route_u::Reply::Invalid&&route_u::requestStart(std::string(96,'a').c_str())==route_u::Reply::Invalid&&route_u::requestStart("x.txt",route_u::Mode::Legacy)==route_u::Reply::Invalid,"bounded explicit mode path");}
 else if(id=="U42"){start("STRING a\n");while(std::string(route_b::phase())!="Press")tick();mock::usbReady=false;mock::now+=1001;tick();mock::usbReady=true;done();check(!route_u::owned()&&route_u::status().reason==route_u::Reason::Deadline,"deadline retains first failure despite known clear");}
 else if(id=="U43"){start("STRING a\n");duckscript::stop();done();check(!File::opened()&&!duckscript::running(),"reader reclaimed after cancellation");start("STRING b\n");done();check(mock::text=="b","fresh explicit file/source lifecycle");}
 else if(id=="U44"){start("STRING a\n");auto before=keyboard_locale::getLocale();check(!keyboard_locale::setLocaleByName("DE"),"actual layout setter refuses");keyboard_locale::begin();attackmode::setOff();attackmode::setHid(false);attackmode::setStorage(true);attackmode::setStorageOnly();check(!attackmode::applyFromString("STORAGE"),"actual personality entry refuses");attackmode::begin();check(attackmode::hidEnabled()&&!attackmode::storageRequested()&&keyboard_locale::getLocale()==before,"actual mode state immutable");done();check(mock::text=="a","unchanged session environment");}
 else if(id=="U45"){start("STRING a\n");while(std::string(route_b::phase())!="Wait")tick();for(unsigned i=0;i<4;++i)check(route_u::requestSnapshot(i)==route_u::Reply::Accepted,"full ordinary queue during running");check(route_u::requestSnapshot(9)==route_u::Reply::QueueFull,"full running queue");auto n=lower::count;route_u::loss();done();check(route_u::status().phase==route_u::Phase::Quarantined&&lower::count==n,"priority loss quarantine no retry");}
 else if(id=="U46"){route_u::setReadPollForTest(neverRead);start("STRING BAD\n");for(unsigned i=0;i<70000&&route_u::owned();++i)tick();check(!route_u::owned()&&!File::opened()&&lower::count==0&&route_u::status().reason==route_u::Reason::File,"unending Retry hits bounded capture budget");}
 else if(id=="U47"){start("STRING ab\n");while(std::string(route_b::phase())!="Wait")tick();mock::usbReady=false;duckscript::stop();tick();mock::now+=1001;tick();check(route_u::status().phase==route_u::Phase::Quarantined&&duckscript::running(),"unresolved clearing retains service ownership");route_u::Token t;check(!route_u::begin(route_u::Service::Files,t),"no early writer during quarantine");}
 else if(id=="U48"){start("STRING a\n");done();check(keyboard_locale::setLocaleByName("DE"),"layout available after known local detach");attackmode::setHid(false);check(!attackmode::hidEnabled(),"HID setting available after detach");}
 else if(id=="U49"){put("STRING a\n");char path[96]="x.txt";u_platform::taskForTest(2);check(duckscript::runRouteB(path),"foreign task copied request");memset(path,'X',5);u_platform::taskForTest(1);done();check(mock::text=="a","borrowed caller path not retained");}
 else if(id=="U50"){start("STRING a\n");bool denied=false;{execution::Guard held;std::thread other([&]{u_platform::taskForTest(2);uint8_t k=4;denied=!hid_backend::beginReport(0,&k,1);});other.join();}check(denied,"foreign backend rejects before waiting on held execution mutex");done();}
 else if(id=="U51"){mock::now=UINT32_MAX-10;start("DELAY 20\nSTRING a\n");done();check(mock::text=="a"&&route_u::status().reason==route_u::Reason::Completed,"single Runtime timebase across wrap");}
 else if(id=="U52"){start("STRING a\n");done();check(route_u::requestSnapshot(1)==route_u::Reply::Accepted,"poll before next start");start("STRING b\n");tick();check(route_u::owned()&&route_u::status().phase==route_u::Phase::Queued,"old terminal cannot complete queued new request");done();check(mock::text=="ab","second copied start not lost behind earlier poll");}
 else if(id=="U53"){start("VAR $n = 0\nVAR $x = 5 / $n\nSTRING BAD\n");done();check(route_u::status().line==2&&route_u::status().errorCode!=0&&route_u::status().reason==route_u::Reason::Runtime&&mock::text.length()==0,"runtime error retains source line without source text");}
 else if(id=="U54"){route_u::Token t;check(route_u::begin(route_u::Service::Upload,t)&&route_u::enterChunk(t),"upload chunk admitted");check(!route_u::enterChunk(t)&&!route_u::end(t)&&!route_u::valid(t),"abort closes admission but retains in-flight owner");put("STRING a\n");check(!duckscript::runRouteB("x.txt"),"capture cannot race unfinished chunk");u_platform::taskForTest(2);check(route_u::leaveChunk(t)&&!route_u::valid(t),"last chunk retires deferred abort");u_platform::taskForTest(1);route_u::Token next;check(route_u::begin(route_u::Service::Ota,next)&&next.id!=t.id,"fresh transaction identity");check(!route_u::leaveChunk(t)&&!route_u::end(t),"stale callback cannot retire new transaction");check(route_u::end(next),"explicit completion");}
 else if(id=="U55"){bool denied=false;{execution::Guard held;std::thread other([&]{u_platform::taskForTest(2);route_u::Token t;denied=!route_u::begin(route_u::Service::Settings,t);});other.join();}check(denied,"service admission uses zero-wait execution probe");}
 else if(id=="U56"){put("STRING BAD\n");check(duckscript::runRouteB("sd:x.txt"),"explicit SD queued");done();check(lower::count==0&&route_u::status().reason==route_u::Reason::File,"no fallback to other volume");}
 else if(id=="U57"){put("STRING a\n","sd:x.txt");check(duckscript::runRouteB("sd:x.txt"),"SD source selected");done();check(mock::text=="a","same actual bounded File adapter for SD");}
 else if(id=="U58"){start("STRING BAD\nVAR $x = (1 + )\n");done();check(duckscript::currentLine()==2&&duckscript::lastError().length()>0,"existing diagnostic accessors use selected RouteB result");put("STRING a\n");check(duckscript::run("x.txt"),"explicit legacy run after error");mock::drain();check(mock::text=="a"&&duckscript::lastError().length()==0,"legacy selection clears stale native display");}
 else if(id=="U59"){put("STRING a\n");cli::parse("run x.txt",printLine,false);check(!route_u::owned()&&duckscript::running(),"actual CLI retains legacy default");cli::parse("stop",printLine,false);check(!duckscript::running(),"actual CLI legacy STOP unchanged");}
 else if(id=="U60"){put("STRING a\n");for(unsigned i=0;i<4;++i)check(route_u::requestSnapshot(i)==route_u::Reply::Accepted,"idle poll queue fills");check(route_u::requestStart("x.txt")==route_u::Reply::QueueFull,"full idle queue rejects copied Start");tick();check(duckscript::runRouteB("x.txt"),"owner update drains idle queue without implicit start");done();check(mock::text=="a","queued start progresses after bounded idle draining");}
 else if(id=="U61"){route_u::Token t;check(route_u::begin(route_u::Service::Upload,t),"callback transaction owns admission");auto before=settings::getSSID();cli::parse("set ssid harmless",printLine,false);check(settings::getSSID()==before&&mock::output.indexOf("Busy")>=0,"actual CLI cannot bypass active service transaction");check(route_u::end(t),"transaction completes");}
 else if(id=="U62"||id=="U63"||id=="U64"){put("STRING BAD\n");if(id=="U62")attackmode::setStorage(true);if(id=="U63")usb_msc_test::active=true;if(id=="U64")usb_msc_test::preparing=true;check(!duckscript::runRouteB("x.txt")&&!File::opened()&&lower::count==0,"existing requested/active/preparing MSC blocks capture");route_u::Token t;check(!route_u::begin(route_u::Service::Files,t),"conflicting service also rejects existing MSC");}
 else check(false,"unknown case");
 check(mock::blockingDelays==0,"native candidate no blocking helper delay");
#ifdef STAGE28U_NEGATIVE_CONTROL
 check(false,"deliberate negative control");
#endif
 auto s=route_u::status();std::cout<<"PASS "<<id<<" ("<<assertions<<" assertions)\nTRACE {\"new_calls_with_fixture\":"<<native_alloc::calls()-allocBefore<<",\"new_bytes_with_fixture\":"<<native_alloc::bytes()-bytesBefore<<",\"request\":"<<s.request<<",\"phase\":"<<unsigned(s.phase)<<",\"reason\":"<<unsigned(s.reason)<<",\"line\":"<<s.line<<",\"owned\":"<<(s.owned?"true":"false")<<",\"storage_bytes\":"<<route_u::persistentBytes()<<",\"reads\":"<<mock::readCalls<<",\"seeks\":"<<mock::seekCalls<<",\"phases\":[";for(unsigned i=0;i<10;++i){if(i)std::cout<<',';std::cout<<phases[i];}std::cout<<"],\"calls\":[";for(size_t i=0;i<lower::count;++i){auto&c=lower::calls[i];if(i)std::cout<<',';std::cout<<"{\"at\":"<<c.at<<",\"session\":"<<c.session<<",\"operation\":"<<c.operation<<",\"id\":"<<unsigned(c.id)<<",\"bytes\":[";for(unsigned j=0;j<8;++j){if(j)std::cout<<',';std::cout<<unsigned(c.bytes[j]);}std::cout<<"]}";}std::cout<<"]}\n";return 0;
 }catch(const std::exception&e){std::cerr<<"FAIL "<<argv[1]<<": "<<e.what()<<" ("<<assertions<<")\n";return 1;}
}
