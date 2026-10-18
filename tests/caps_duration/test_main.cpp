#include "feedback_cases.inc"
#include "caps_trial.h"
static void trialTick(){led_mock::nowUs=uint64_t(mock::now+1)*1000;tick();}
static void trialDone(){for(unsigned i=0;i<10000&&route_u::owned()&&route_u::status().phase!=route_u::Phase::Quarantined;++i)trialTick();}
static void trialPress(){for(unsigned i=0;i<9000&&presses().empty()&&route_u::owned();++i)trialTick();check(presses().size()==1,"exactly one Caps press reached");}
int main(int argc,char**argv){if(argc!=2)return 2;if(argv[1][0]!='E')return historical_feedback_main(argc,argv);try{
 mscMock::reset();mock::reset();setup();check(startupControlledReady&&route_u::bindOwner(),"controlled owner");lower::reset();led_mock::nowUs=0;auto r=req();std::string id=argv[1];
 if(id=="E01"||id=="E02"||id=="E03"||id=="E04"){
  uint16_t ms=id=="E01"?0:id=="E02"?100:id=="E03"?250:500;
  check(route_u::requestCapsTrial(ms)==route_u::Reply::Accepted,"admitted one shot");auto request=route_u::status().request;trialPress();auto d=caps_trial::snapshot();check(d.request==request&&d.active&&d.down&&!d.up&&d.requestedMs==ms,"request correlated dwell");input(true);trialDone();input(false);
  d=caps_trial::snapshot();check(!route_u::owned()&&route_u::status().reason==route_u::Reason::Completed&&!d.active,"completed owned cleanup");check(presses().size()==1&&d.down&&d.up,"one pair, no replay");check(d.upReturnUs>=d.downReturnUs+uint64_t(ms?ms:5)*1000,"minimum scheduled API-return dwell");check(d.downComplete&&d.downCompleteUs==d.downReturnUs,"completion hook independently records completion");auto count=lower::count;for(int i=0;i<100;++i)trialTick();check(lower::count==count,"no delayed report after owner retired");
 }else if(id=="E05"){
  check(route_u::requestCapsTrial(500)==route_u::Reply::Accepted,"admit");trialPress();auto d=caps_trial::snapshot();handleStop(&r);trialDone();auto end=caps_trial::snapshot();check(r.code==202&&!route_u::owned()&&route_u::status().reason==route_u::Reason::Cancelled,"STOP responsive during dwell");check(end.up&&end.upReturnUs-d.downReturnUs<500000&&lower::calls[lower::count-1].bytes[2]==0,"early local cleanup without host-release claim");
 }else if(id=="E06"){
  check(route_u::requestCapsTrial(100)==route_u::Reply::Accepted,"admit");route_u::stop();trialDone();check(presses().empty()&&!route_u::owned(),"queued STOP produces no key");
 }else if(id=="E07"){
  for(uint16_t ms:{1,5,99,101,251,501,65535})check(route_u::requestCapsTrial(ms)==route_u::Reply::Invalid,"finite allowlist");check(lower::count==0&&!route_u::owned(),"invalid duration no effect");
 }else if(id=="E08"){
  r.headers.clear();r.body["ms"]={"100"};handleCapsTrial(&r,true);check(r.code==401&&!route_u::owned()&&lower::count==0,"trial authenticated");handleCapsTrial(&r,false);check(r.code==401,"GET authenticated");
 }else if(id=="E09"){
  for(const char* value:{"-1","100x","0100"," 100","1000","","65536"}){r.body["ms"]={value};handleCapsTrial(&r,true);check(r.code==400&&!route_u::owned(),"strict textual bound");}r.body.clear();handleCapsTrial(&r,true);check(r.code==400,"required selection");
 }else if(id=="E10"){
  r.body["ms"]={"250"};handleCapsTrial(&r,true);auto request=route_u::status().request;check(r.code==202&&r.response.indexOf("\"requestedMs\":250")>=0,"admission correlated");handleCapsTrial(&r,true);check(r.code==409&&route_u::status().request==request,"second invocation refused");trialPress();handleCapsTrial(&r,false);check(r.code==200&&r.response.indexOf("\"hostReleaseProven\":false")>=0&&r.response.indexOf("CAPS-DURATION-")>=0,"live evidence no host success");route_u::stop();trialDone();
 }else if(id=="E11"){
  check(route_u::requestCapsTrial(100)==route_u::Reply::Accepted,"admit");trialPress();route_u::Token t;check(!route_u::begin(route_u::Service::Storage,t)&&route_u::requestStart("/x.txt")==route_u::Reply::Busy,"no new owner or storage during dwell");r.body["s"]={"x.txt"};handleDeleteScript(&r);check(r.code==409,"delete blocked");route_u::stop();trialDone();
 }else if(id=="E12"||id=="E13"){
  check(route_u::requestCapsTrial(250)==route_u::Reply::Accepted,"admit");trialPress();if(id=="E12"){mock::usbMounted=false;tud_umount_cb();}else tud_suspend_cb(false);trialDone();check(route_u::status().reason==route_u::Reason::Lost&&caps_trial::snapshot().reason==uint8_t(route_u::Reason::Lost),"loss visible");check(presses().size()==1,"no repeat after loss");auto count=lower::count;mock::usbMounted=true;tud_resume_cb();for(int i=0;i<50;++i)trialTick();check(lower::count==count,"reconnect no replay");
 }else if(id=="E14"){
  route_u::Token t;check(route_u::begin(route_u::Service::Files,t),"transaction");check(route_u::requestCapsTrial(100)==route_u::Reply::Busy,"transaction exclusion");check(route_u::end(t),"retire");
 }else if(id=="E15"){
  Holder h;r.body["ms"]={"100"};handleCapsTrial(&r,true);check(r.code==409&&!route_u::owned(),"bounded HTTP contention not suppressed");
 }else if(id=="E16"){
  check(route_u::requestCapsTrial(500)==route_u::Reply::Accepted,"admit");trialPress();mock::usbReady=false;trialDone();check(route_u::status().reason!=route_u::Reason::Completed&&presses().size()==1,"release backpressure bounded failure no repeat");
 }else if(id=="E17"){
  check(route_u::requestCapsTrial(100)==route_u::Reply::Accepted,"admit");trialPress();auto first=route_u::status().request;route_u::stop();trialDone();check(!route_u::owned(),"old owner retired");put("/x.txt","STRING a\n");start();done();auto count=lower::count;for(int i=0;i<1000;++i)trialTick();check(lower::count==count&&caps_trial::snapshot().request==first&&presses().size()==2,"no delayed trial release into subsequent script");
 }else if(id=="E18"){
  put("/x.txt","HOLD CAPSLOCK\nRELEASE CAPSLOCK\n");start();done();check(route_u::status().reason==route_u::Reason::Capability&&lower::count==0,"no language expansion");
 }else if(id=="E19"){
  mock::now=UINT32_MAX-5300;check(route_u::requestCapsTrial(500)==route_u::Reply::Accepted,"admit near clock wrap");trialPress();trialDone();check(route_u::status().reason==route_u::Reason::Completed&&presses().size()==1,"wrapped dwell finishes");
 }else if(id=="E20"){
  check(route_u::requestCapsTrial(250)==route_u::Reply::Accepted,"admit");trialPress();auto s=caps_trial::snapshot();for(unsigned i=0;i<100;++i){auto rr=req();handleStatus(&rr);check(rr.code==200,"status remains responsive");}check(caps_trial::snapshot().downReturnUs==s.downReturnUs,"poll no resubmit");route_u::stop();trialDone();
 }else if(id=="E21"){
  check(route_u::requestCapsTrial(100)==route_u::Reply::Accepted,"admit");trialPress();check(!led_return::snapshot(led_mock::nowUs).observed,"trial does not fabricate feedback");trialDone();handleLedTest(&r,0);check(r.response.indexOf("\"caps\":null")>=0&&r.response.indexOf("\"ledEvidenceValid\":false")>=0,"unknown preserved");
 }else if(id=="E22"){
  r.path="/caps-trial/start";r.body["ms"]={"100"};server.dispatch("/caps-trial/start",HTTP_POST,&r);check(r.code==202,"actual route registered");route_u::stop();trialDone();r.path="/caps-trial/nope";server.dispatch("/caps-trial/nope",HTTP_GET,&r);check(r.code==404,"no prefix fallback");
 }else if(id=="E23"){
  check(route_u::requestCapsTrial(100)==route_u::Reply::Accepted,"admit");trialPress();mock::now+=1001;trialTick();trialDone();check(route_u::status().reason==route_u::Reason::Deadline&&presses().size()==1,"scheduler stall deadline visible");
 }else if(id=="E24"){
  check(route_u::requestCapsTrial(100)==route_u::Reply::Accepted,"admit");trialPress();tud_mount_cb();trialDone();check(route_u::status().reason==route_u::Reason::Lost,"new feedback session cannot reuse trial");
 }else if(id=="E25"||id=="E26"){
  check(route_u::requestCapsTrial(100)==route_u::Reply::Accepted,"admit");if(id=="E25"){for(unsigned i=0;i<9000&&std::string(route_b::phase())!="Press";++i)trialTick();}else{trialPress();for(int i=0;i<200&&std::string(route_b::phase())!="Release";++i)trialTick();}
  lower::next=lower::Outcome::FalseAfterPossibleAcceptance;trialTick();trialDone();auto n=lower::count;for(int i=0;i<100;++i)trialTick();check(route_u::status().phase==route_u::Phase::Quarantined&&lower::count==n,"ambiguous called-false quarantined; no automatic retry");check(caps_trial::snapshot().reason!=uint8_t(route_u::Reason::Completed),"visible error not fake success");
 }else if(id=="E27"){
  http_mock::sending=atSend;r.body["ms"]={"invalid"};handleCapsTrial(&r,true);http_mock::sending=nullptr;check(r.code==400&&lockFreeAtSend,"invalid trial response outside execution lock");
 }else if(id=="E28"){
  check(route_u::requestCapsTrial(100)==route_u::Reply::Accepted,"admit");trialPress();auto before=lower::count;mock::usbReady=false;for(int i=0;i<100;++i)trialTick();check(lower::count==before,"not ready no HID action");mock::usbReady=true;trialDone();check(route_u::status().reason==route_u::Reason::Completed&&presses().size()==1,"availability resumes pending release once, no repress");
 }else check(false,"unknown case");std::cout<<"PASS "<<id<<" ("<<assertions<<" assertions)\n";return 0;
 }catch(const std::exception&e){std::cerr<<"FAIL "<<argv[1]<<": "<<e.what()<<" ("<<assertions<<")\n";return 1;}}
