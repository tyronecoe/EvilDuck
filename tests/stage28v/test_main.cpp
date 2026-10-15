#include "coordinator.h"
#include "allocations.h"
#include "mutation_guard.h"
#include "task_platform.h"
#include "host.h"
#include "duckscript.h"
#include "com.h"
#include "hid_backend.h"
#include "backend_lease.h"
#include "scheduler_seam.h"
#include "lower.h"
#include "cli.h"
#include "storage.h"
#include "spiffs.h"
#include "sd_card.h"
#include "settings.h"
#include "attackmode.h"
#include "usb_msc.h"
#include "led.h"
#include "script_log.h"
#include "script_library.h"
#include "config.h"
#include "network.h"
#include "USB.h"
#include "USBMSC.h"
#include "SPIFFS.h"
#include "Adafruit_NeoPixel.h"
#include <thread>
#include <iostream>
#include <stdexcept>
#include <string>
#include <memory>
#include "webserver.cpp"
namespace nvsMock {extern unsigned reads,writes,opens,commits;extern bool fail;}
uint32_t esp_random(){return 0;}
static unsigned assertions=0;
static void check(bool b,const char*m){++assertions;if(!b)throw std::runtime_error(m);}
static void tick(){++mock::now;duckscript::update();com::update();}
static void until(route_u::Phase p){for(unsigned i=0;i<20000;++i){if(route_u::status().phase==p)return;tick();}check(false,"phase reachable");}
static void done(){for(unsigned i=0;i<20000&&route_u::owned()&&route_u::status().phase!=route_u::Phase::Quarantined;++i)tick();check(!route_u::owned()||route_u::status().phase==route_u::Phase::Quarantined,"bounded terminal");}
static void put(const char*path,const std::string&s){mscMock::put(path,s.size());mscMock::nodes[path]->bytes.assign(s.begin(),s.end());}
static AsyncWebServerRequest req(){AsyncWebServerRequest r;r.headers["X-Duck-Password"]=std::string(16,'w');return r;}
static void printLine(const char*s){mock::output+=s;}
static void start(){check(duckscript::runRouteB("x.txt"),"explicit start");}
static void stopped(){route_u::stop();done();check(!route_u::owned()&&mock::text.length()==0,"STOP before payload");}
static unsigned changes(){return mscMock::writes+mscMock::creates+mscMock::truncates+mscMock::removes+mscMock::renames+mscMock::mkdirs+mscMock::mounts+fsMock::mounts+fsMock::formats+nvsMock::writes+nvsMock::opens+pixelMock::begins+pixelMock::shows;}
int main(int argc,char**argv){if(argc!=2)return 2;try{
 mscMock::reset();settings::load();check(settings::ready(),"valid synthetic settings loaded");mock::reset();check(storage::begin(),"actual storage mounted");
 lower::reset();hid_backend::begin();com::update();lower::count=0;mock::reports.clear();mock::text="";
 check(webserver::prepareControlledNetwork(),"actual controlled network prepared over fake WiFi");webserver::begin();check(networkMock::begins==1,"actual server registrations");
 check(route_u::bindOwner(),"owner bound");put("/x.txt","DELAY 100\nSTRING a\n");put("/scripts/x.txt","STRING b\n");
 auto allocationsBefore=native_alloc::calls(),bytesBefore=native_alloc::bytes();
 std::string id=argv[1];auto r=req();
 if(id=="V01"){r.query["engine"]={"routeb"};r.query["s"]={"x.txt"};server.dispatch("/run",HTTP_GET,&r);check(r.code==202&&route_u::owned(),"actual explicit web frontend");done();check(mock::text=="a","real storage/compiler/backend path");}
 else if(id=="V02"){cli::parse("routeb sd:x.txt",printLine,false);check(route_u::owned(),"actual explicit CLI");done();check(mock::text=="b","exact SD selection");}
 else if(id=="V03"){start();r.query["s"]={"x.txt"};handleRunScript(&r);check(r.code==409,"legacy web cannot fall back while busy");stopped();}
 else if(id=="V04"){start();handleStatus(&r);check(r.code==200&&r.response.indexOf("\"running\":true")>=0,"actual status queued");handleStop(&r);done();check(r.code==202&&lower::count==0,"actual web STOP preparing");}
 else if(id=="V05"){start();cli::parse("status",printLine,false);cli::parse("stop",printLine,false);done();check(mock::output.indexOf("phase=")>=0&&lower::count==0,"actual CLI status/STOP");}
 else if(id=="V06"||id=="V07"){start();r.body["name"]={"x.txt"};r.body["content"]={"STRING BAD"};r.query["s"]={"x.txt"};unsigned before=changes();if(id=="V06")handleSaveScript(&r);else handleDeleteScript(&r);check(r.code==409&&changes()==before,"actual edit/delete denied before lower effect");stopped();}
 else if(id=="V08"||id=="V09"){start();r.body["ssid"]={"altered"};r.body["color"]={"#123456"};auto before=changes();auto ssid=settings::getSSID();if(id=="V08")handleSaveSettings(&r);else handleSetLed(&r);check(r.code==409&&changes()==before&&settings::getSSID()==ssid,"actual settings/LED denied");stopped();}
 else if(id=="V10"){start();r.body["line"]={"STRING BAD"};auto n=lower::count;handleSendLine(&r);check(r.code==409&&lower::count==n,"manual handler denied");stopped();}
 else if(id=="V11"||id=="V12"||id=="V13"){
  unsigned before=changes();uint8_t data[8]{};for(size_t index:{size_t(0),size_t(8)}){if(id=="V11")onUpload(&r,"x.txt",index,data,8,index!=0);else if(id=="V12")onFirmwareUpload(&r,"fw.bin",index,data,8,index!=0);else {fwUpdateOk=index!=0;handleFirmwareComplete(&r);}check(r.code==503,"actual disabled lifecycle response503");}check(changes()==before&&Update.calls==0&&ESP.restarts==0,"no chunk/update/reboot lower action");
 }
 else if(id=="V14"){r.body["name"]={"new.txt"};r.body["content"]={"REM harmless"};handleSaveScript(&r);check(r.code==200,"permitted legacy save");r.query["s"]={"new.txt"};handleDeleteScript(&r);check(r.code==200&&!SPIFFS.exists("/new.txt"),"permitted delete");}
 else if(id=="V15"){r.body["channel"]={"6"};auto n=nvsMock::writes;handleSaveSettings(&r);check(r.code==200&&settings::getChannel()==6&&nvsMock::writes==n+12,"actual settings successful flow");}
 else if(id=="V16"){r.body["color"]={"#123456"};auto n=pixelMock::shows;handleSetLed(&r);check(r.code==200&&settings::getLedColor()==0x123456&&pixelMock::shows==n+1,"actual LED successful flow");}
 else if(id=="V17"){start();unsigned n=changes();settings::load();settings::setSSID("changed");settings::setPassword(std::string(20,'q').c_str());settings::setChannel(6);settings::setWebPassword("changed");settings::setAutorun("bad.txt");settings::setStealthMode(true);settings::setHiddenAp(true);settings::setDisableLed(true);settings::setLedColor(0x123456);settings::setAutorunDelay(5,6);check(!settings::setLedColorHex("123456")&&!settings::saveChecked()&&!settings::resetChecked(),"actual direct settings denied");check(changes()==n&&settings::getChannel()==1&&!settings::autorunEnabled(),"no NVS or cached mutation");stopped();}
 else if(id=="V18"){start();auto n=changes();led::begin();led::setColor(1,2,3);check(changes()==n,"actual direct LED no lower call");stopped();}
 else if(id=="V19"){start();auto n=changes();check(!spiffs::begin()&&!spiffs::format()&&!spiffs::create("new.txt")&&!spiffs::remove("x.txt")&&!spiffs::rename("x.txt","z.txt")&&!spiffs::append("x.txt","bad")&&!spiffs::streamOpen("x.txt"),"direct SPIFFS denied");spiffs::streamClose();check(spiffs::streamWrite("a",1)==0&&changes()==n,"no stream/write side effect");stopped();}
 else if(id=="V20"){start();auto n=changes();check(!sd_card::begin()&&!sd_card::mkdir("/new")&&!sd_card::remove("/scripts/x.txt")&&!sd_card::rename("/scripts/x.txt","/new.txt")&&!sd_card::writeFile("/scripts/x.txt","bad")&&!sd_card::appendFile("/scripts/x.txt","bad"),"direct SD denied");check(changes()==n,"no direct SD lower action");stopped();}
 else if(id=="V21"){storage::Ref a,b;storage::parseRef("x.txt",a);storage::parseRef("sd:x.txt",b);start();auto n=changes();check(!storage::begin()&&!storage::remove(a)&&!storage::writeFile(a,"bad")&&!storage::appendFile(a,"bad")&&!storage::copyToSd("x.txt",b)&&!storage::copyToSpiffs(b,"copy.txt"),"actual storage facade denied");check(changes()==n,"no facade lower mutation");stopped();}
 else if(id=="V22"){start();auto n=changes();check(!usb_msc::begin(),"direct MSC start denied");usb_msc::update();usb_msc::end();check(changes()==n&&mscMock::starts==0&&usb_msc::state()==usb_msc::State::Off,"MSC direct calls no lower mutation");stopped();}
 else if(id=="V23"){start();auto n=changes();script_library::installIfNeeded();check(changes()==n,"actual library install denied");stopped();}
 else if(id=="V24"){check(spiffs::streamOpen("x.txt"),"legacy stream opens");check(!duckscript::runRouteB("x.txt"),"already-open write stream blocks capture");spiffs::streamClose();start();stopped();}
 else if(id=="V25"){storage::Ref a,b;storage::parseRef("x.txt",a);storage::parseRef("sd:copy.txt",b);check(storage::writeFile(a,"REM a")&&storage::appendFile(a,"\n"),"nested lower guards permit facade writes");check(storage::copyToSd("x.txt",b)&&storage::copyToSpiffs(b,"copy.txt"),"actual copies both directions");check(storage::readFile(a)==spiffs::readFile("copy.txt"),"copied content");}
 else if(id=="V26"){route_u::Mutation accepted;check(bool(accepted),"synchronous operation admitted");route_u::stop();check(!duckscript::runRouteB("x.txt"),"recursive Start blocked during accepted mutation");check(spiffs::append("x.txt","REM a\n"),"STOP cannot revoke admitted synchronous mutation");}
 else if(id=="V27"){bool denied=false;{route_u::Mutation admitted;std::thread other([&]{u_platform::taskForTest(2);denied=!spiffs::append("x.txt","BAD");});other.join();}check(denied,"cross-thread synchronous mutation refuses without wait");}
 else if(id=="V28"){route_u::Token t;check(route_u::begin(route_u::Service::Files,t),"transaction begins");check(!spiffs::append("x.txt","BAD"),"token existence alone no permission");check(route_u::enterChunk(t),"explicit chunk admitted");check(spiffs::append("x.txt","REM x\n"),"actual mutation inside admitted chunk");check(!route_u::end(t),"abort defers while chunk active");check(!spiffs::append("x.txt","BAD"),"closing transaction rejects new nested operation");check(route_u::leaveChunk(t)&&!route_u::valid(t),"chunk retirement releases reservation");start();stopped();}
 else if(id=="V29"){route_u::Token t;check(route_u::begin(route_u::Service::Files,t)&&route_u::enterChunk(t),"chunk admitted");u_platform::taskForTest(2);check(!spiffs::append("x.txt","BAD")&&!route_u::leaveChunk(t),"foreign same-process task cannot borrow chunk permission");u_platform::taskForTest(1);check(route_u::leaveChunk(t)&&route_u::end(t),"original task retires");}
 else if(id=="V30"){std::unique_ptr<route_u::Mutation> g[33];for(unsigned i=0;i<32;++i){g[i]=std::make_unique<route_u::Mutation>();check(bool(*g[i]),"bounded nested admission");}g[32]=std::make_unique<route_u::Mutation>();check(!bool(*g[32]),"depth33 rejected");for(unsigned i=33;i>0;--i)g[i-1].reset();start();stopped();}
 else if(id=="V31"){start();u_platform::taskForTest(2);tick();check(route_u::status().phase==route_u::Phase::Queued,"foreign task cannot step owner");handleStop(&r);u_platform::taskForTest(1);done();check(lower::count==0,"foreign callback only publishes STOP");}
 else if(id=="V32"){cli::parse("routeb x.txt",printLine,false);until(route_u::Phase::Running);handleStatus(&r);check(r.code==200,"status during running");cli::parse("stop",printLine,false);done();check(mock::text.length()==0&&!route_u::owned(),"runtime delay cancelled");}
 else if(id=="V33"){start();until(route_u::Phase::Stopping);handleStatus(&r);check(r.code==200&&route_u::owned(),"clearing status owns session");handleStop(&r);done();check(!route_u::owned(),"clearing completes locally");}
 else if(id=="V34"||id=="V35"){
  start();while(std::string(route_b::phase())!="Press")tick();if(id=="V34"){lower::next=lower::Outcome::FalseAfterPossibleAcceptance;tick();}else route_u::loss();done();auto n=lower::count;for(unsigned i=0;i<100;++i)tick();check(route_u::status().phase==route_u::Phase::Quarantined&&route_u::owned()&&lower::count==n,"permanent ambiguous/loss quarantine no retry");handleStatus(&r);check(r.code==200,"status quarantine");handleStop(&r);tick();check(!spiffs::append("x.txt","BAD")&&!duckscript::runRouteB("x.txt")&&lower::count==n,"STOP cannot release ambiguous quarantine or replay");
 }
 else if(id=="V36"){start();route_u::stop();done();auto n=lower::count;start();done();check(mock::text=="a"&&lower::count>n&&lower::calls[n].clear,"fresh safe session starts with local clearing");}
 else if(id=="V37"){r.query["engine"]={"routeb"};r.query["s"]={std::string(96,'x').c_str()};handleRunScript(&r);check(r.code==409&&!route_u::owned(),"bounded copied frontend path");}
 else if(id=="V38"){start();r.query["engine"]={"routeb"};r.query["s"]={"sd:x.txt"};handleRunScript(&r);check(r.code==409,"explicit busy no fallback");stopped();}
 else if(id=="V39"){r.query["engine"]={"typo"};r.query["s"]={"x.txt"};handleRunScript(&r);check(r.code==400&&!route_u::owned(),"unknown engine refuses");}
 else if(id=="V40"){r.headers.clear();r.query["engine"]={"routeb"};r.query["s"]={"x.txt"};handleRunScript(&r);check(r.code==401&&!route_u::owned(),"actual auth before start");}
 else if(id=="V41"){SPIFFS.remove("/scripts/x.txt");start();tick();mscMock::nodes["/x.txt"]->bytes[0]='X';done();check(lower::count==0&&route_u::status().reason==route_u::Reason::File,"external media mutation detected before backend");}
 else if(id=="V42"){start();tick();mscMock::present=false;done();check(lower::count==0&&route_u::status().reason==route_u::Reason::File,"media removal aborts capture");}
 else if(id=="V43"){mscMock::put("/sys/usb_disk.img",4194304);check(usb_msc::begin(),"MSC preparing admitted off-route");check(!duckscript::runRouteB("x.txt"),"actual preparing state rejects RouteB");for(int i=0;i<3;++i)usb_msc::update();check(usb_msc::active()&&!duckscript::runRouteB("x.txt"),"active real MSC state rejects RouteB");usb_msc::end();start();stopped();}
 else if(id=="V44"){mscMock::put("/sys/usb_disk.img",4194304);usb_msc::begin();for(int i=0;i<3;++i)usb_msc::update();usb_msc::end();start();auto n=changes();uint8_t data[8]{};check(mscMock::readCallback(0,0,data,8)==0&&mscMock::writeCallback(0,0,data,8)==0&&!mscMock::startCallback(0,true,false),"stale real callbacks busy/refuse during RouteB");check(changes()==n,"stale callbacks no lower mutation");stopped();}
 else if(id=="V45"){start();AsyncWebSocketClient client;AwsFrameInfo info;uint8_t command[]={'s','t','o','p'};onWsEvent(nullptr,&client,WS_EVT_DATA,&info,command,sizeof(command));done();check(client.output.indexOf("Stop requested")>=0&&lower::count==0,"actual WebSocket CLI STOP body");}
 else if(id=="V46"){start();for(int i=0;i<3;++i)check(route_u::requestSnapshot(i)==route_u::Reply::Accepted,"queue saturates");handleStop(&r);done();check(lower::count==0,"actual STOP priority independent of queue");}
 else if(id=="V47"){start();auto n=changes();r.body["name"]={"cancel.txt"};r.body["content"]={"REM harmless"};handleSaveScript(&r);handleStop(&r);done();check(changes()==n,"refused request cancellation has no file mutation");}
 else if(id=="V48"){
  // Demonstrated remaining boundary: raw SDK/VFS handles have no route admission.
  start();unsigned n=mscMock::writes;File raw=SPIFFS.open("/unfenced.txt",FILE_WRITE);check(raw&&raw.print("REM x")==5&&mscMock::writes==n+1,"BLOCKER: raw VFS call bypasses repository wrapper");raw.close();stopped();
 }

 else if(id=="V49"){start();unsigned n=networkMock::modes+networkMock::aps+networkMock::begins;check(!webserver::prepareControlledNetwork(),"direct AP setup denied");webserver::begin();check(n==networkMock::modes+networkMock::aps+networkMock::begins,"actual lifecycle bodies deny before lower action");stopped();}
 else if(id=="V50"){start();AsyncWebSocketClient client;AwsFrameInfo info;uint8_t data[129]{};onWsEvent(nullptr,&client,WS_EVT_DATA,&info,data,sizeof(data));onWsEvent(nullptr,&client,WS_EVT_DATA,&info,nullptr,4);check(client.output.indexOf("oversized")>=0&&route_u::owned(),"actual WS invalid bounds rejected");stopped();}
 else if(id=="V51"){int status=0;{route_u::Mutation operation;std::thread other([&]{u_platform::taskForTest(2);auto foreign=req();handleStatus(&foreign);status=foreign.code;});other.join();}check(status==409,"actual status uses nonblocking admission under contention");}
 else if(id=="V52"){mscMock::writeHook=[](){route_u::stop();check(!duckscript::runRouteB("x.txt"),"reentrant Start inside actual handler write rejected");};r.body["name"]={"new.txt"};r.body["content"]={"REM harmless"};handleSaveScript(&r);check(r.code==200&&spiffs::readFile("new.txt")=="REM harmless","accepted real handler not revoked by reentrant STOP");}
 else if(id=="V53"){nvsMock::fail=true;r.body["channel"]={"6"};auto n=nvsMock::writes;handleSaveSettings(&r);check(r.code==503&&nvsMock::writes==n,"actual settings failure no false persistence success");}
 else if(id=="V54"){mscMock::shortWrite=1;r.body["name"]={"new.txt"};r.body["content"]={"REM harmless"};handleSaveScript(&r);check(r.code==500&&mscMock::nodes["/new.txt"]->bytes.size()==1,"actual short write reported; no atomic rollback claim");}
 else if(id=="V55"){server.dispatch("/update",HTTP_POST,&r);check(r.code==503&&Update.calls==0&&ESP.restarts==0,"actual registered update completion disabled");server.dispatch("/upload",HTTP_POST,&r);check(r.code==503,"actual registered upload completion disabled");}
 else if(id=="V56"){start();server.dispatch("/status",HTTP_GET,&r);check(r.response.indexOf("routeBPhase")>=0,"actual registered status includes typed phase");server.dispatch("/stop",HTTP_POST,&r);done();check(r.code==202&&lower::count==0,"actual registered STOP priority");}
 else check(false,"unknown case");
 check(mock::blockingDelays==0,"no blocking delay in tested path");
#ifdef STAGE28V_NEGATIVE_CONTROL
 check(false,"deliberate negative control");
#endif
 std::cout<<"ALLOC calls="<<native_alloc::calls()-allocationsBefore<<" requested_bytes="<<native_alloc::bytes()-bytesBefore<<" persistent="<<route_u::persistentBytes()<<"\n";
 std::cout<<"PASS "<<id<<" ("<<assertions<<" assertions)\n";return 0;
}catch(const std::exception&e){std::cerr<<"FAIL "<<argv[1]<<": "<<e.what()<<" ("<<assertions<<")\n";return 1;}}
