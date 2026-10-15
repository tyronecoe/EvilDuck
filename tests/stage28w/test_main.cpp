#include "coordinator.h"
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
#include "webserver.cpp"
#include "EvilDuckS3.ino"
uint32_t esp_random(){return 0;}
static unsigned assertions=0;
static void check(bool b,const char*m){++assertions;if(!b)throw std::runtime_error(m);}
static AsyncWebServerRequest req(){AsyncWebServerRequest r;r.headers["X-Duck-Password"]=std::string(16,'w');return r;}
static void put(const char*p,const std::string&s){mscMock::put(p,s.size());mscMock::nodes[p]->bytes.assign(s.begin(),s.end());}
static void tick(){++mock::now;duckscript::update();com::update();}
static void done(){for(unsigned i=0;i<20000&&route_u::owned()&&route_u::status().phase!=route_u::Phase::Quarantined;++i)tick();check(!route_u::owned()||route_u::status().phase==route_u::Phase::Quarantined,"bounded terminal");}
static void start(){check(duckscript::runRouteB("x.txt"),"explicit start");}
static void printLine(const char*s){mock::output+=s;}
static void readAll(){for(unsigned i=0;i<1000&&Serial.available();++i)cli::update();check(!Serial.available(),"finite serial source consumed");}
static void actualLoop(){auto before=serialMock::reads;loop();check(serialMock::reads-before<=64,"serial budget per actual loop turn");}
int main(int argc,char**argv){if(argc!=2)return 2;try{
 mscMock::reset();mock::reset();setup();check(startupControlledReady&&settings::ready(),"actual controlled setup succeeds over lower mocks");
 check(!settings::autorunEnabled()&&fsMock::formats==0&&networkMock::begins==1,"controlled no autorun/format");check(!route_u::owned(),"boot never selects Route B");
 check(route_u::bindOwner(),"operational owner bound");lower::reset();lower::count=0;mock::text="";mock::blockingDelays=0;
 put("/x.txt","DELAY 40\nSTRING a\n");put("/scripts/x.txt","STRING b\n");auto r=req();std::string id=argv[1];
 if(id=="W01"||id=="W02"){
  if(id=="W02")start();r.path="/custom.txt";put("/custom.txt","REM harmless");auto n=mscMock::opens;handleStatic(&r);check(r.code==503&&mscMock::opens==n&&AsyncWebServerRequest::fileResponses==0,"no asynchronous File accepted, idle or owned");if(route_u::owned()){route_u::stop();done();}
 }
 else if(id=="W03"){r.path="/";handleStatic(&r);check(r.code==200&&r.response.length()>0&&AsyncWebServerRequest::fileResponses==0,"immutable built-in page available");start();r.path="/style.css";handleStatic(&r);check(r.code==200,"immutable style while owned");route_u::stop();done();}
 else if(id=="W04"){r.query["s"]={"x.txt"};auto n=mscMock::opens;handleGetScript(&r);check(r.code==200&&r.response=="DELAY 40\nSTRING a\n"&&mscMock::opens>n,"synchronous File read into response copy");auto saved=r.response;start();check(r.response==saved,"response owns copy after handler returns");route_u::stop();done();}
 else if(id=="W05"){start();auto n=mscMock::opens;r.query["s"]={"x.txt"};r.body["name"]={"x.txt"};handleGetScript(&r);check(r.code==409,"GET read excluded");handleLoadScriptPost(&r);check(r.code==409,"POST read excluded");handleLibrary(&r);check(r.code==409,"library excluded");handleListScripts(&r);check(r.code==409,"list excluded");handleStorageInfo(&r);check(r.code==409&&mscMock::opens==n,"no lower read opens while owned");route_u::stop();done();}
 else if(id=="W06"||id=="W07"){if(id=="W07")start();AsyncWebSocketClient client;AwsFrameInfo info;uint8_t command[]={'r','o','u','t','e','b',' ','x','.','t','x','t'};check(ws.event!=nullptr,"actual WS event registration");ws.event(nullptr,&client,WS_EVT_DATA,&info,command,sizeof(command));check(client.output.indexOf("503")>=0&&(route_u::owned()==(id=="W07")),"registered mutating WS rejected");if(route_u::owned()){route_u::stop();done();}}
 else if(id=="W08"){AsyncWebSocketClient client;ws.event(nullptr,&client,WS_EVT_DISCONNECT,nullptr,nullptr,0);ws.event(nullptr,&client,WS_EVT_CONNECT,nullptr,nullptr,0);check(!route_u::owned()&&client.output.length()==0,"disconnect/connect never arm or retain work");start();route_u::stop();done();}
 else if(id=="W09"){AsyncWebSocketClient client;uint8_t data[1024]{};ws.event(nullptr,&client,WS_EVT_DATA,nullptr,nullptr,0);ws.event(nullptr,&client,WS_EVT_DATA,nullptr,data,sizeof(data));check(client.output.indexOf("503")>=0&&!route_u::owned()&&lower::count==0,"malformed/oversize frame never decoded/dispatched");}
 else if(id=="W10"){serialMock::continuous=true;auto n=serialMock::reads;cli::update();check(serialMock::reads-n==64,"serial budget exactly64 for always-available input");serialMock::continuous=false;}
 else if(id=="W11"){start();serialMock::continuous=true;for(unsigned i=0;i<2000&&route_u::owned();++i)actualLoop();serialMock::continuous=false;check(!route_u::owned()&&mock::text=="a","continuous serial cannot prevent owner completion");}
 else if(id=="W12"){serialMock::set("rou");readAll();check(!route_u::owned(),"partial command not executed");serialMock::set("teb x.txt\r\n");readAll();check(route_u::owned(),"fragmented CRLF start preserved");serialMock::set("sto");readAll();check(route_u::owned(),"partial STOP not executed");serialMock::set("p\n");readAll();done();check(lower::count==0,"fragmented STOP published before payload");}
 else if(id=="W13"){serialMock::set(std::string(513,'x')+"\nrouteb x.txt\n");readAll();check(serialMock::output.find("line rejected")!=std::string::npos&&route_u::owned(),"overflow discards whole line, next line recovers");route_u::stop();done();}
 else if(id=="W14"){serialMock::set(std::string("routeb x.txt")+'\0'+"BAD\n");readAll();check(!route_u::owned()&&serialMock::output.find("line rejected")!=std::string::npos,"embedded NUL cannot execute prefix");}
 else if(id=="W15"){start();serialMock::set(std::string(128,'x')+"\nstop\n");actualLoop();check(route_u::owned(),"STOP behind backlog not instantaneous");actualLoop();check(route_u::owned(),"backlog still pending");actualLoop();done();check(lower::count==0,"framed STOP consumed within three64-byte turns in this fixture");}
 else if(id=="W16"){start();for(unsigned i=0;i<3;++i)check(route_u::requestSnapshot(i)==route_u::Reply::Accepted,"queue saturation");serialMock::set("stop\n");actualLoop();done();check(!route_u::owned()&&lower::count==0,"serial STOP priority despite full publication queue");}
 else if(id=="W17"){serialMock::set("routeb sd:x.txt\n");readAll();done();check(mock::text=="b","explicit SD selection retained");}
 else if(id=="W18"){r.query["engine"]={"routeb"};r.query["s"]={"x.txt"};server.dispatch("/run",HTTP_GET,&r);check(r.code==202,"authenticated explicit HTTP path");server.dispatch("/status",HTTP_GET,&r);check(r.code==200&&r.response.indexOf("routeBPhase")>=0,"typed status");server.dispatch("/stop",HTTP_POST,&r);done();check(r.code==202&&lower::count==0,"HTTP STOP");}
 else if(id=="W19"){r.headers.clear();r.query["engine"]={"routeb"};r.query["s"]={"x.txt"};server.dispatch("/run",HTTP_GET,&r);check(r.code==401&&!route_u::owned(),"HTTP authentication remains required");}
 else if(id=="W20"){start();r.query["s"]={"x.txt"};server.dispatch("/run",HTTP_GET,&r);check(r.code==409,"no busy fallback to legacy");route_u::stop();done();}
 else if(id=="W21"){uint8_t bytes[4]{};auto n=mscMock::writes;onUpload(&r,"x.txt",0,bytes,4,false);check(r.code==503,"file upload first chunk");onUpload(&r,"x.txt",4,bytes,4,true);check(r.code==503,"file upload final chunk");server.dispatch("/upload",HTTP_POST,&r);check(r.code==503,"upload completion");onFirmwareUpload(&r,"firmware.bin",0,bytes,4,true);check(r.code==503,"firmware chunk");for(bool b:{false,true}){fwUpdateOk=b;server.dispatch("/update",HTTP_POST,&r);check(r.code==503,"restart completion");}check(mscMock::writes==n&&Update.calls==0&&ESP.restarts==0,"disabled operations no lower action");}
 else if(id=="W22"){start();r.body["name"]={"new.txt"};r.body["content"]={"REM harmless"};r.body["channel"]={"6"};auto n=mscMock::writes;handleSaveScript(&r);check(r.code==409,"actual file writer denial");handleSaveSettings(&r);check(r.code==409&&mscMock::writes==n&&settings::getChannel()==1,"actual settings denial");route_u::stop();done();}
 else if(id=="W23"){start();while(std::string(route_b::phase())!="Press")tick();lower::next=lower::Outcome::FalseAfterPossibleAcceptance;tick();done();auto n=lower::count;serialMock::set("status\nstop\nrouteb x.txt\n");readAll();for(int i=0;i<10;++i)tick();check(route_u::status().phase==route_u::Phase::Quarantined&&lower::count==n,"ambiguous lower outcome permanently quarantined, no retry");}
 else if(id=="W24"){start();while(std::string(route_b::phase())!="Wait")tick();route_u::loss();done();auto n=lower::count;route_u::stop();tick();check(route_u::owned()&&route_u::status().phase==route_u::Phase::Quarantined&&lower::count==n,"loss preserves permanent quarantine");}
 else if(id=="W25"){start();route_u::stop();done();auto n=lower::count;start();done();check(!route_u::owned()&&mock::text=="a"&&lower::calls[n].clear,"fresh safe session performs new local clear");}
 else if(id=="W26"){mscMock::writeHook=[](){route_u::stop();check(!duckscript::runRouteB("x.txt"),"reentrant Start inside admitted write denied");};r.body["name"]={"new.txt"};r.body["content"]={"REM harmless"};handleSaveScript(&r);check(r.code==200,"admitted synchronous work not revoked by STOP");}
 else if(id=="W27"){serialMock::set("routeb x.txt\n");auto n=serialMock::reads;u_platform::taskForTest(2);cli::update();u_platform::taskForTest(1);check(serialMock::reads==n&&!route_u::owned(),"foreign task cannot drain owner serial buffer");readAll();check(route_u::owned(),"owner consumes pending input");route_u::stop();done();}
 else if(id=="W28"){r.query["s"]={"x.txt"};handleGetScript(&r);auto content=r.response;r=AsyncWebServerRequest{};start();done();check(mock::text=="a"&&!route_u::owned()&&content.length()>0,"simulated response disconnect leaves no filesystem reservation");}
 else if(id=="W29"){check(spiffs::streamOpen("x.txt"),"existing stream opens");check(!duckscript::runRouteB("x.txt"),"stream blocks capture");spiffs::streamClose();start();route_u::stop();done();}
 else if(id=="W30"){mscMock::put("/sys/usb_disk.img",4194304);check(usb_msc::begin()&&!duckscript::runRouteB("x.txt"),"real preparing MSC rejects admission");usb_msc::end();start();route_u::stop();done();}
 else if(id=="W31"){put("/x.txt",std::string(8193,' '));start();done();check(lower::count==0&&route_u::status().reason==route_u::Reason::File,"8192 capture limit preserved");}
 else if(id=="W32"){start();tick();mscMock::nodes["/x.txt"]->bytes[0]='X';done();check(lower::count==0&&route_u::status().reason==route_u::Reason::File,"byte verification detects changed source");}
 else if(id=="W33"){int code=0;{execution::Guard guard;std::thread other([&]{u_platform::taskForTest(2);auto foreign=req();handleGetSettings(&foreign);code=foreign.code;});other.join();}check(code==409,"settings response refuses contended snapshot");handleGetSettings(&r);check(r.code==200,"uncontended authenticated settings snapshot");}
 else if(id=="W34"){int code=0;start();{execution::Guard guard;std::thread other([&]{u_platform::taskForTest(2);auto foreign=req();handleStop(&foreign);code=foreign.code;});other.join();}check(code==401&&route_u::owned(),"auth refuses contended snapshot; no false authorization");handleStop(&r);done();check(r.code==202&&lower::count==0,"authenticated retry STOP after snapshot available");}
 else check(false,"unknown case");
 check(AsyncWebServerRequest::fileResponses==0,"candidate never constructed async File response");
 std::cout<<"PASS "<<id<<" ("<<assertions<<" assertions)\n";return 0;
}catch(const std::exception&e){std::cerr<<"FAIL "<<argv[1]<<": "<<e.what()<<" ("<<assertions<<")\n";return 1;}}
