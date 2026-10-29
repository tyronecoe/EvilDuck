#include "text_keyboard_parent_cases.inc"
#include "adapter.h"

struct RestartProbe {
 ds_preview::Runtime* runtime=nullptr;ds_preview::Program* program=nullptr;
 unsigned restarts=0,restartAttempts=0,refuse=0,stopAfter=0,draws=0;uint32_t now=0,raw=0;
 bool borrowChecked=false,borrowDenied=false;std::vector<ds_preview::Event> events;
 static bool random(void* c,uint32_t& value){auto& h=*static_cast<RestartProbe*>(c);++h.draws;value=h.raw;return true;}
 static ds_preview::Accept sink(void* c,const ds_preview::Event& e){auto& h=*static_cast<RestartProbe*>(c);
  if(e.type==ds_preview::EventType::Restart){++h.restartAttempts;if(h.refuse){--h.refuse;return ds_preview::Accept::Retry;}++h.restarts;
   if(h.program&&!h.borrowChecked){h.borrowChecked=true;h.borrowDenied=!h.program->compile("STRING z\n",strlen("STRING z\n"));}
   if(h.stopAfter&&h.restarts>=h.stopAfter)h.runtime->cancel();
  }
  h.events.push_back(e);return ds_preview::Accept::Accepted;
 }
};
static void restartStart(const char* source,ds_preview::Program& p,ds_preview::Runtime& rt,RestartProbe& h,uint32_t now=0,uint32_t steps=ds_preview::MaxSteps,uint32_t elapsed=ds_preview::MaxElapsedMs){
 check(p.compile(source,strlen(source)),"restart source passes actual compiler");h.runtime=&rt;rt.randomReader=RestartProbe::random;rt.randomContext=&h;check(rt.start(p,RestartProbe::sink,&h,now,steps,elapsed),"restart runtime starts once");
}
static void restartPump(ds_preview::Runtime& rt,RestartProbe& h,unsigned turns,uint32_t origin=0,bool advance=true){for(unsigned i=0;i<turns&&rt.state()==ds_preview::State::Running;++i){h.now=origin+(advance?i:0);rt.tick(h.now);}}
static std::string restartText(const RestartProbe& h){std::string s;for(auto e:h.events)if(e.type==ds_preview::EventType::Character)s+=char(e.value);return s;}
static void restartStop(){route_u::stop();trialDone();check(route_u::status().reason==route_u::Reason::Cancelled&&!route_u::owned()&&!hid_backend::hasPersistent(),"explicit STOP ends restart owner and persistent state");noReplay();}
static void pendingRestart(){put("/x.txt","HOLD SHIFT\nDELAY 50\nRESTART_PAYLOAD\nSTRING BAD\n");start();reports(1);mock::usbReady=false;awaitPhase("Reset");}
static void adapterReady(native_b::Adapter& a,SourceProbe& p){check(a.prepare(p.reader()),"adapter captures source");for(unsigned i=0;i<20000&&a.state()!=native_b::State::Ready&&a.state()!=native_b::State::Error;++i)a.step(mock::now++);check(a.state()==native_b::State::Ready,"adapter ready after bounded source capture/preflight");check(a.start(mock::now),"direct adapter lease starts");}
static void adapterFinish(native_b::Adapter& a){for(unsigned i=0;i<5000&&a.leased()&&a.state()!=native_b::State::Quarantined;++i)a.step(mock::now++);check(!a.leased()||a.state()==native_b::State::Quarantined,"direct adapter cleanup bounded");}
struct NoAllocRestart {ds_preview::Runtime* rt=nullptr;unsigned count=0;static ds_preview::Accept sink(void* c,const ds_preview::Event& e){auto& p=*static_cast<NoAllocRestart*>(c);if(e.type==ds_preview::EventType::Restart&&++p.count==5)p.rt->cancel();return ds_preview::Accept::Accepted;}};

int main(int argc,char** argv){if(argc!=2)return 2;if(argv[1][0]!='Y')return text_keyboard_main(argc,argv);
try{mscMock::reset();mock::reset();setup();check(startupControlledReady&&route_u::bindOwner(),"actual composed controlled startup");lower::reset();led_mock::nowUs=0;rng_mock::reset();auto r=req();std::string id=argv[1];
if(id=="Y01"){
 put("/x.txt","STRING a\nDELAY 20\nRESTART_PAYLOAD\nSTRING BAD\n");start();reports(4);exactReport(0,0,{4});exactReport(1,0,{});exactReport(2,0,{4});exactReport(3,0,{});auto op=operations();check(op[0].session==op[2].session&&op[2].operation>op[0].operation,"restart preserves lease and increases operation IDs");bool between=false;for(auto c:clears())if(c.operation>op[0].operation&&c.operation<op[2].operation){check(zero(c),"intervening restart report exactly neutral");between=true;}check(between,"neutral submission precedes restarted first character");restartStop();
}else if(id=="Y02"){
 put("/x.txt","WHILE TRUE\nSTRING a\nRESTART_PAYLOAD\nSTRING BAD\nEND_WHILE\n");start();reports(4);exactReport(0,0,{4});exactReport(2,0,{4});restartStop();
}else if(id=="Y03"){
 put("/x.txt","FUNCTION work()\nSTRING a\nRESTART_PAYLOAD\nRETURN 99\nEND_FUNCTION\nVAR $x=1+work()\nSTRING BAD\n");start();reports(4);exactReport(0,0,{4});exactReport(2,0,{4});check(operations().size()==4,"function suspended in caller expression restarts without old return or suffix");restartStop();
 ds_preview::Program p;ds_preview::Runtime rt;RestartProbe h;h.stopAfter=3;h.raw=2;restartStart("FUNCTION resetter()\nRESTART_PAYLOAD\nRETURN 1\nEND_FUNCTION\nVAR $x=$_RANDOM_INT+resetter()\nSTRING BAD\n",p,rt,h);restartPump(rt,h,300);check(h.restarts==3&&h.draws==3&&restartText(h).empty()&&rt.state()==ds_preview::State::Cancelled,"rewind discards sampled parent operand and retains provider for each fresh evaluation");
}else if(id=="Y04"){
 put("/x.txt","FUNCTION work()\nWHILE TRUE\nSTRING a\nRESTART_PAYLOAD\nEND_WHILE\nEND_FUNCTION\nwork()\nSTRING BAD\n");start();reports(4);exactReport(0,0,{4});exactReport(2,0,{4});restartStop();
}else if(id=="Y05"){
 put("/x.txt","STRING a\nHOLD SHIFT\nDELAY 20\nRESTART_PAYLOAD\n");start();reports(5);exactReport(0,0,{4});exactReport(2,2,{});exactReport(3,0,{4});exactReport(4,0,{});check(!hid_backend::hasPersistent(),"held Shift removed before rewound lowercase report");restartStop();
}else if(id=="Y06"){
 put("/x.txt","HOLD a\nDELAY 20\nRESTART_PAYLOAD\n");start();reports(2);exactReport(0,0,{4});exactReport(1,0,{4});auto op=operations();bool between=false;for(auto c:clears())if(c.operation>op[0].operation&&c.operation<op[1].operation)between=zero(c);check(between,"held nonmodifier cleared before reacquisition on restart");restartStop();
}else if(id=="Y07"){
 pendingRestart();auto n=lower::count;auto s=backend_b::status();for(unsigned i=0;i<100;++i)trialTick();check(lower::count==n&&route_u::owned()&&!hid_backend::hasPersistent(),"NoCall backpressure leaves neutral pending, lease held and no stale held state");check(backend_b::status().clearSubmitted<s.clearRequest,"pending clear is not acknowledged");handleStop(&r);mock::usbReady=true;trialDone();check(operations().size()==1&&route_u::status().reason==route_u::Reason::Cancelled,"STOP pending restart prevents rewind output");noReplay();
}else if(id=="Y08"){
 put("/x.txt","STRING a\nHOLD SHIFT\nDELAY 20\nRESTART_PAYLOAD\n");start();reports(3);mock::usbReady=false;awaitPhase("Reset");auto target=backend_b::status().clearRequest;auto n=lower::count;for(unsigned i=0;i<50;++i)trialTick();check(lower::count==n&&backend_b::status().clearRequest==target,"retry never readmits restart clear");mock::usbReady=true;reports(5);exactReport(3,0,{4});check(backend_b::status().clearSubmitted==target,"one completed clear for one restart admission");restartStop();
}else if(id=="Y09"){
 pendingRestart();lower::next=lower::Outcome::FalseAfterPossibleAcceptance;mock::usbReady=true;trialTick();trialDone();check(route_u::status().phase==route_u::Phase::Quarantined&&backend_b::status().quarantined&&operations().size()==1,"ambiguous neutral acceptance quarantines without restart output");noReplay();
}else if(id=="Y10"){
 pendingRestart();auto n=lower::count;mock::usbMounted=false;tud_umount_cb();trialDone();check(route_u::status().phase==route_u::Phase::Quarantined&&lower::count==n,"disconnect pending restart never rewinds");mock::usbMounted=true;tud_mount_cb();noReplay();
}else if(id=="Y11"){
 pendingRestart();lower::hook=[](){route_u::stop();};mock::usbReady=true;trialTick();trialDone();check(route_u::status().reason==route_u::Reason::Cancelled&&operations().size()==1,"STOP in neutral submit callback takes priority over rewind");noReplay();
}else if(id=="Y12"){
 put("/x.txt","HOLD SHIFT\nDELAY 5000\nRESTART_PAYLOAD\n");start();reports(1);handleStop(&r);trialDone();check(route_u::status().reason==route_u::Reason::Cancelled&&operations().size()==1,"STOP before restart admission suppresses restart");noReplay();
}else if(id=="Y13"){
 for(const char* source:{"RESTART_PAYLOAD extra\n","RESTART_PAYLOAD 1\n","RESTART\n","REPEAT 2 RESTART_PAYLOAD\n","IF FALSE THEN\nRESTART_PAYLOAD extra\nEND_IF\n","FUNCTION unused()\nRESTART_PAYLOAD extra\nEND_FUNCTION\nSTRING a\n"}){lower::reset();rejected(source);}
}else if(id=="Y14"){
 completed("IF_DEFINED_TRUE #ABSENT\nRESTART_PAYLOAD extra\nEND_IF_DEFINED\nSTRING a\n");oneA();lower::reset();rejected("FUNCTION RESTART_PAYLOAD()\nEND_FUNCTION\n");
}else if(id=="Y15"){
 ds_preview::Program p;ds_preview::Runtime rt;RestartProbe h;h.stopAfter=3;restartStart("STRING a\nRESTART_PAYLOAD\nSTRING BAD\n",p,rt,h);restartPump(rt,h,300);check(rt.state()==ds_preview::State::Cancelled&&h.restarts==3&&restartText(h)=="aaa","accepted restart discards old flow and repeats first instruction exactly");
}else if(id=="Y16"){
 ds_preview::Program p;ds_preview::Runtime rt;RestartProbe h;h.refuse=4;h.stopAfter=2;restartStart("RESTART_PAYLOAD\n",p,rt,h);restartPump(rt,h,100);check(h.restartAttempts==6&&h.restarts==2&&rt.steps()==2,"cached restart retries do not redispatch instruction or consume extra step");
}else if(id=="Y17"){
 ds_preview::Program p;ds_preview::Runtime rt;RestartProbe h;restartStart("VAR $v=7\n$_RANDOM_MIN=40\n$_RANDOM_MAX=50\n$_JITTER_ENABLED=TRUE\n$_JITTER_MAX=500\nRESTART_PAYLOAD\n",p,rt,h);for(unsigned i=0;i<100&&h.restarts==0;++i)rt.tick(i);uint16_t v=0;check(h.restarts==1&&rt.state()==ds_preview::State::Running&&!rt.variable("$v",v),"rewind clears variable initialization before next instruction");check(rt.line()==1&&rt.steps()>0&&h.draws==0,"rewind returns at first line, preserves steps, bypasses jitter");rt.cancel();
}else if(id=="Y18"){
 ds_preview::Program p;ds_preview::Runtime rt;RestartProbe h;h.stopAfter=3;restartStart("VAR $v=$_RANDOM_MIN+$_RANDOM_MAX+$_JITTER_MAX+$_JITTER_ENABLED\nIF $v==29 THEN\nSTRING a\nEND_IF\n$_RANDOM_MIN=40\n$_RANDOM_MAX=50\n$_JITTER_MAX=500\n$_JITTER_ENABLED=TRUE\nRESTART_PAYLOAD\n",p,rt,h);restartPump(rt,h,1000);check(h.restarts==3&&restartText(h)=="aaa"&&h.draws==0,"random and jitter defaults restored every restart without reseeding");
}else if(id=="Y19"){
 ds_preview::Program p;ds_preview::Runtime rt;RestartProbe h;h.program=&p;h.stopAfter=2;restartStart("RESTART_PAYLOAD\n",p,rt,h);restartPump(rt,h,30);check(h.borrowChecked&&h.borrowDenied&&h.restarts==2,"borrow remains exclusive through restart barrier");check(p.compile("STRING a\n",strlen("STRING a\n")),"terminal cancellation releases Program for subsequent compile");
}else if(id=="Y20"){
 ds_preview::Program p;ds_preview::Runtime rt;RestartProbe h;restartStart("RESTART_PAYLOAD\n",p,rt,h,0,7);restartPump(rt,h,100);check(rt.state()==ds_preview::State::Error&&rt.error().code==ds_preview::ErrorCode::StepLimit&&rt.steps()==7&&h.restarts==7,"restart cannot renew smaller instruction limit");
}else if(id=="Y21"){
 ds_preview::Program p;ds_preview::Runtime rt;RestartProbe h;restartStart("RESTART_PAYLOAD\n",p,rt,h,100,ds_preview::MaxSteps,25);restartPump(rt,h,100,100);check(rt.state()==ds_preview::State::Error&&rt.error().code==ds_preview::ErrorCode::Timeout&&h.restarts==25,"restart preserves smaller original elapsed deadline");
}else if(id=="Y22"){
 ds_preview::Program p;ds_preview::Runtime rt;RestartProbe h;restartStart("RESTART_PAYLOAD\n",p,rt,h,UINT32_MAX-10,ds_preview::MaxSteps,25);restartPump(rt,h,100,UINT32_MAX-10);check(rt.error().code==ds_preview::ErrorCode::Timeout&&h.restarts==25,"original restart deadline survives uint32 wrap");
}else if(id=="Y23"){
 ds_preview::Program p;ds_preview::Runtime rt;RestartProbe h;h.refuse=ds_preview::MaxTicks+10;restartStart("RESTART_PAYLOAD\n",p,rt,h);restartPump(rt,h,ds_preview::MaxTicks+5,0,false);check(rt.error().code==ds_preview::ErrorCode::TickLimit&&h.restarts==0&&rt.steps()==1,"pending restart preserves bounded tick budget without advancing clock");
}else if(id=="Y24"){
 ds_preview::Program p;ds_preview::Runtime rt;RestartProbe h;restartStart("RESTART_PAYLOAD\n",p,rt,h);restartPump(rt,h,ds_preview::MaxSteps+10,0,false);check(rt.error().code==ds_preview::ErrorCode::StepLimit&&h.restarts==ds_preview::MaxSteps,"default step bound survives repeated restart");
}else if(id=="Y25"){
 ds_preview::Program p;ds_preview::Runtime rt;RestartProbe h;h.refuse=UINT32_MAX;restartStart("RESTART_PAYLOAD\n",p,rt,h);restartPump(rt,h,30005);check(rt.error().code==ds_preview::ErrorCode::Timeout&&h.restarts==0&&rt.steps()==1,"default elapsed budget covers suspended restart");
}else if(id=="Y26"){
 std::string src="STRING a\nDELAY 20\nRESTART_PAYLOAD\nSTRING BAD\n";SourceProbe q;q.memory={src.data(),src.size(),0};native_b::Adapter a;adapterReady(a,q);unsigned reads=q.reads,seeks=q.seeks;src[7]='b';for(unsigned i=0;i<1000&&operations().size()<2;++i)a.step(mock::now++);auto admissionBefore=a.admissions(),ackBefore=a.acks(),retryBefore=a.retries();for(unsigned i=0;i<1000&&operations().size()<4;++i)a.step(mock::now++);check(a.admissions()>admissionBefore&&a.acks()>ackBefore&&a.retries()>=retryBefore,"adapter counters accumulate across restart rather than resetting");check(operations().size()==4&&q.reads==reads&&q.seeks==seeks,"restart uses captured immutable Program without source callbacks");exactReport(0,0,{4});exactReport(2,0,{4});a.cancel();adapterFinish(a);check(a.state()==native_b::State::Cancelled,"direct adapter cleanup after source-lifetime probe");
}else if(id=="Y27"){
 const char* src="HOLD SHIFT\nDELAY 20\nRESTART_PAYLOAD\n";SourceProbe q;q.memory={src,strlen(src),0};native_b::Adapter a;adapterReady(a,q);for(unsigned i=0;i<1000&&operations().size()<1;++i)a.step(mock::now++);mock::usbReady=false;for(unsigned i=0;i<1000&&std::string(route_b::phase())!="Reset";++i)a.step(mock::now++);check(std::string(route_b::phase())=="Reset","direct adapter has pending restart reset");auto op=a.operation();auto admissions=a.admissions();check(!a.inspect({{op.session+1,op.operation},route_b::ResultKind::Done})&&!a.inspect({{op.session,op.operation+1},route_b::ResultKind::Done})&&!a.inspect({op,route_b::ResultKind::Done}),"wrong owner, operation and fabricated Done cannot acknowledge pending restart");for(unsigned i=0;i<30;++i)a.step(mock::now++);check(a.admissions()==admissions&&operations().size()==1,"inspection cannot readmit or rewind");a.cancel();mock::usbReady=true;adapterFinish(a);
}else if(id=="Y28"){
 select("mac");put("/x.txt","STRING a\nDELAY 20\nRESTART_PAYLOAD\n");start();reports(2);auto status=route_u::status();auto caps=caps_trial::snapshot();auto session=operations()[0].session;reports(4);auto after=route_u::status();auto capsAfter=caps_trial::snapshot();check(after.request==status.request&&route_u::owned()&&operations()[2].session==session,"request and lease remain stable across restart");check(status.capsMs==500&&after.capsMs==500&&caps.request==capsAfter.request&&caps.requestedMs==capsAfter.requestedMs&&capsAfter.active==caps.active,"ordinary request captures Mac Caps timing without creating or restarting a diagnostic trial");check(route_u::requestStart("/x.txt")==route_u::Reply::Busy,"restart does not relinquish exclusive owner admission");restartStop();
}else if(id=="Y29"){
 put("/x.txt","STRING a\nDELAY 20\nRESTART_PAYLOAD\n");start();reports(4);restartStop();auto first=route_u::status().request;auto session=operations()[0].session;lower::reset();completed("STRING a\n");check(route_u::status().request!=first&&operations()[0].session!=session,"independent next run gets fresh request and lease");oneA();noReplay();
}else if(id=="Y30"){
 pendingRestart();for(unsigned i=0;i<2300&&route_u::status().phase!=route_u::Phase::Quarantined;++i)trialTick();check(route_u::status().phase==route_u::Phase::Quarantined&&operations().size()==1,"bounded pending/cleanup deadline quarantines unavailable restart without later output");noReplay();
}else if(id=="Y31"){
 ds_preview::Program p;ds_preview::Runtime rt;RestartProbe h;h.stopAfter=2;restartStart("DEFINE #X a\nEXTENSION RepeatFlow\nVERSION 1\nFUNCTION leaf()\nSTRING #X\nRESTART_PAYLOAD\nRETURN 1\nEND_FUNCTION\nEND_EXTENSION\nVAR $v=leaf()\n",p,rt,h);restartPump(rt,h,200);check(h.restarts==2&&restartText(h)=="aa","compiled constants, function table and extension selections retained");
}else if(id=="Y32"){
 ds_preview::Program p;check(p.compile("RESTART_PAYLOAD\n",strlen("RESTART_PAYLOAD\n")),"compile allocation probe");ds_preview::Runtime rt;NoAllocRestart h;h.rt=&rt;check(rt.start(p,NoAllocRestart::sink,&h),"start allocation probe");auto before=native_alloc::calls();for(unsigned i=0;i<20&&rt.state()==ds_preview::State::Running;++i)rt.tick(i);auto after=native_alloc::calls();check(before==after&&h.count==5&&rt.state()==ds_preview::State::Cancelled,"runtime rewind allocates no C++ heap and honors callback cancellation");
}else check(false,"unknown restart case");std::cout<<"PASS "<<id<<" ("<<assertions<<" assertions)\n";return 0;
}catch(const std::exception& e){std::cerr<<"FAIL "<<argv[1]<<": "<<e.what()<<" ("<<assertions<<")\n";return 1;}}
