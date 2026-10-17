#include "http_cases.inc"
int main(int argc,char**argv){if(argc!=2)return 2;if(argv[1][0]!='S')return historical_http_main(argc,argv);try{
 mscMock::reset();mock::reset();setup();check(startupControlledReady,"controlled setup");check(route_u::bindOwner(),"owner");lower::reset();std::string id=argv[1];auto r=req();
 if(id=="S01"||id=="S02"){
  put("/x.txt",id=="S01"?"DELAY 60000\nSTRING BAD\n":"WHILE TRUE\nDELAY 5\nEND_WHILE\nSTRING BAD\n");start();phase("Idle"); // delay owns Runtime rather than keyboard phase
  handleStop(&r);check(r.code==202&&r.response.indexOf("requestId")>=0,"correlated accepted receipt");done();check(route_u::status().reason==route_u::Reason::Cancelled&&presses().empty(),"owner cancels wait/loop without text");
 }else if(id=="S03"){
  put("/x.txt","CTRL a\nSTRING zzzzzzzzzzzzzzzzzzzzzzzzzzz\n");start();phase("Wait");auto count=lower::count;check(count>0,"held transient reached");handleStop(&r);check(lower::count==count,"callback only publishes STOP");done();check(route_u::status().reason==route_u::Reason::Cancelled,"terminal cancel");auto after=lower::count;for(int i=0;i<100;++i)tick();check(lower::count==after,"no late queued output");for(auto b:lower::calls[after-1].bytes)check(b==0,"final submitted neutral mock report");
 }else if(id=="S04"){
  check(hid_backend::hold(2,4),"legacy held state");auto count=lower::count;u_platform::taskForTest(2);handleStop(&r);check(r.code==202&&lower::count==count&&hid_backend::hasPersistent(),"legacy HTTP ingress defers cleanup");u_platform::taskForTest(1);tick();check(!hid_backend::hasPersistent(),"owner clears legacy holds");
 }else if(id=="S05"){
  put("/x.txt","DELAY 1000\n");start();auto request=route_u::status().request;handleStatus(&r);char idText[24];snprintf(idText,sizeof(idText),"%llu",(unsigned long long)request);check(r.code==200&&r.response.indexOf(String("\"routeBRequestId\":\"")+idText+"\"")>=0,"same status ID as owner");handleStop(&r);done();auto last=route_u::status().request;handleStatus(&r);check(last==request&&r.response.indexOf("\"routeBOwned\":false")>=0,"terminal status retains correlation");
 }else if(id=="S06"){
  r.headers.clear();handleStop(&r);check(r.code==401&&lower::count==0,"auth required no cleanup");
 }else if(id=="S07"){
  put("/x.txt","HOLD a\n");start();done();check(route_u::status().reason==route_u::Reason::Capability&&lower::count==0,"unsupported Route B HOLD not enabled by UI");
 }else if(id=="S08"){
  r.path="/index.html";handleStatic(&r);check(r.code==200&&r.response.indexOf("STOP script")>=0&&r.response.indexOf("Stops EvilDuck script execution.")>=0,"served built-in home contains visible stop");r.path="/index.js";handleStatic(&r);check(r.response.indexOf("/run?engine=routeb&s=")>=0&&r.response.indexOf("/stop")>=0,"served script uses actual routes");
 }else check(false,"unknown case");std::cout<<"PASS "<<id<<" ("<<assertions<<" assertions)\n";return 0;
 }catch(const std::exception&e){std::cerr<<"FAIL "<<argv[1]<<": "<<e.what()<<" ("<<assertions<<")\n";return 1;}}
