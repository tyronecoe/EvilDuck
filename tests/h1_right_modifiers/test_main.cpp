#include "h1_parent_cases.inc"
// Expected byte-0 masks are USB HID keyboard modifier bits, not H1 scalar values.
static const char* rightNames[]={"RCTRL","RSHIFT","RALT","RGUI"};
static const uint8_t rightMasks[]={0x10,0x20,0x40,0x80};
static void rightClear(){check(!route_u::owned()&&!hid_backend::hasPersistent()&&zero(lower::calls[lower::count-1]),"right state cleared to neutral");}
int main(int argc,char**argv){if(argc!=2)return 2;if(strncmp(argv[1],"AD",2))return inject_var_h1_main(argc,argv);
try{mscMock::reset();mock::reset();setup();check(startupControlledReady&&route_u::bindOwner(),"actual H1 right modifier startup");lower::reset();led_mock::nowUs=0;rng_mock::reset();auto r=req();std::string id=argv[1];
if(id=="AD01"||id=="AD02"||id=="AD03"||id=="AD04"){
 unsigned i=unsigned(id[3]-'1');completed((std::string(rightNames[i])+" a\n").c_str());check(operations().size()==2,"one right chord press/release");exactReport(0,rightMasks[i],{4});exactReport(1,0,{});
}else if(id=="AD05"){
 for(unsigned i=0;i<4;++i){lower::reset();completed((std::string("INJECT_MOD ")+rightNames[i]+"\n").c_str());check(operations().size()==2,"right modifier tap press/release");exactReport(0,rightMasks[i],{});exactReport(1,0,{});}
}else if(id=="AD06"){
 for(unsigned i=0;i<4;++i){lower::reset();completed((std::string("HOLD ")+rightNames[i]+"\nDELAY 10\nRELEASE "+rightNames[i]+"\n").c_str());check(operations().size()==2,"right ownership no automatic transient tap");exactReport(0,rightMasks[i],{});exactReport(1,0,{});}
}else if(id=="AD07"){
 for(unsigned subset=1;subset<16;++subset){lower::reset();std::string source;uint8_t mask=0;for(unsigned i=0;i<4;++i)if(subset&(1u<<i)){source+=rightNames[i];source+=(i&1)?" ":"-";mask|=rightMasks[i];}source+="a\n";completed(source.c_str());exactReport(0,mask,{4});exactReport(1,0,{});}
 lower::reset();completed("CTRL SHIFT ALT GUI RCTRL RSHIFT RALT RGUI a\n");exactReport(0,255,{4});exactReport(1,0,{});
}else if(id=="AD08"){
 const char* left[]={"CTRL","SHIFT","ALT","GUI"};for(unsigned i=0;i<4;++i){lower::reset();completed((std::string("HOLD ")+left[i]+"\nHOLD "+rightNames[i]+"\nRELEASE "+left[i]+"\nRELEASE "+rightNames[i]+"\n").c_str());exactReport(0,uint8_t(1u<<i),{});exactReport(1,uint8_t((1u<<i)|rightMasks[i]),{});exactReport(2,rightMasks[i],{});exactReport(3,0,{});}
}else if(id=="AD09"){
 for(const char*s:{"RSHIFT RSHIFT a\n","RCTRL-RCTRL a\n","CTRL CONTROL a\n","RALT-RALT-a\n","GUI COMMAND a\n"}){lower::reset();rejected(s);}
}else if(id=="AD10"){
 for(const char*s:{"RCTRL\n","RCTRL--a\n","RSHIFT- a\n","RSHIFT a b\n","RALT RGUI\n","HOLD RSHIFT a\n","RELEASE RSHIFT RALT\n","INJECT_MOD RCTRL RALT\n","INJECT_MOD RSHIFT-a\n","RCONTROL a\n","RWINDOWS a\n","IF FALSE THEN\nRSHIFT RSHIFT a\nEND_IF\n","FUNCTION unused()\nHOLD RCTRL extra\nEND_FUNCTION\n"}){lower::reset();rejected((std::string("STRING a\n")+s).c_str());}
}else if(id=="AD11"){
 completed("HOLD RSHIFT\nSTRING a\nSTRING A\nRELEASE RSHIFT\n");check(operations().size()==6,"held right Shift restored independently of implicit left Shift");exactReport(0,32,{});exactReport(1,32,{4});exactReport(2,32,{});exactReport(3,34,{4});exactReport(4,32,{});exactReport(5,0,{});
}else if(id=="AD12"){
 completed("HOLD a\nRCTRL b\nRELEASE a\n");exactReport(0,0,{4});exactReport(1,16,{4,5});exactReport(2,0,{4});exactReport(3,0,{});
}else if(id=="AD13"){
 for(unsigned i=0;i<4;++i){lower::reset();runSource((std::string("HOLD ")+rightNames[i]+"\nINJECT_MOD "+rightNames[i]+"\n").c_str());check(route_u::status().reason!=route_u::Reason::Completed&&operations().size()==1,"tapping exactly held right modifier refused without fake release");rightClear();noReplay();}
}else if(id=="AD14"){
 completed("HOLD RSHIFT\nINJECT_MOD SHIFT\nRELEASE RSHIFT\n");exactReport(0,32,{});exactReport(1,34,{});exactReport(2,32,{});exactReport(3,0,{});
 lower::reset();completed("HOLD SHIFT\nINJECT_MOD RSHIFT\nRELEASE SHIFT\n");exactReport(0,2,{});exactReport(1,34,{});exactReport(2,2,{});exactReport(3,0,{});
}else if(id=="AD15"){
 completed("HOLD RCTRL\nHOLD RSHIFT\nHOLD RALT\nHOLD RGUI\n");check(operations().size()==4,"completion clears all four right holds");exactReport(3,240,{});rightClear();noReplay();
}else if(id=="AD16"){
 put("/x.txt","HOLD RSHIFT\nDELAY 5000\nSTRING BAD\n");start();reports(1);auto before=mock::now;handleStop(&r);trialDone();check(route_u::status().reason==route_u::Reason::Cancelled&&mock::now-before<500&&operations().size()==1,"STOP remains cooperative and suppresses suffix");rightClear();noReplay();
}else if(id=="AD17"){
 put("/x.txt","HOLD RSHIFT\nSTRING BAD\n");start();awaitPhase("Ownership");mock::usbReady=false;handleStop(&r);for(unsigned i=0;i<20;++i)trialTick();check(route_u::owned()&&operations().empty(),"pending right hold not submitted after STOP");mock::usbReady=true;trialDone();check(operations().empty(),"right pending cancellation submits cleanup only");rightClear();noReplay();
}else if(id=="AD18"){
 put("/x.txt","HOLD RGUI\nDELAY 5000\n");start();reports(1);mock::usbReady=false;route_u::stop();for(unsigned i=0;i<20;++i)trialTick();check(route_u::owned()&&route_u::requestStart("/x.txt")==route_u::Reply::Busy,"right cleanup retains exclusive owner while blocked");mock::usbReady=true;trialDone();check(operations().size()==1,"cleanup does not replay held right GUI");rightClear();noReplay();
}else if(id=="AD19"){
 runSource("HOLD RCTRL\nSTOP_PAYLOAD\nSTRING BAD\n");check(route_u::status().reason==route_u::Reason::Cancelled&&operations().size()==1,"STOP_PAYLOAD preserves held-right cleanup");rightClear();noReplay();
}else if(id=="AD20"){
 runSource("HOLD RALT\nVAR $zero=0\nVAR $bad=1/$zero\nSTRING BAD\n");check(route_u::status().reason!=route_u::Reason::Completed&&operations().size()==1,"runtime arithmetic error suppresses suffix");rightClear();noReplay();
}else if(id=="AD21"){
 completed("HOLD RSHIFT\nRESET\nSTRING a\n");check(operations().size()==3,"keyboard RESET clears right state before later character");exactReport(0,32,{});exactReport(1,0,{4});exactReport(2,0,{});auto op=operations();bool between=false;for(auto c:clears())if(c.operation>op[0].operation&&c.operation<op[1].operation){check(zero(c),"RESET submits neutral");between=true;}check(between,"neutral submission ordered before subsequent text");
}else if(id=="AD22"){
 put("/x.txt","STRING a\nHOLD RSHIFT\nDELAY 20\nRESTART_PAYLOAD\n");start();reports(5);exactReport(0,0,{4});exactReport(2,32,{});exactReport(3,0,{4});exactReport(4,0,{});auto op=operations();check(op[0].session==op[3].session&&route_u::owned(),"restart retains lease while clearing right state");restartStop();
}else if(id=="AD23"){
 put("/x.txt","HOLD RSHIFT\nDELAY 5000\nSTRING BAD\n");start();reports(1);mock::usbMounted=false;tud_umount_cb();trialDone();check(route_u::status().phase==route_u::Phase::Quarantined&&operations().size()==1,"disconnect held right modifier quarantines");mock::usbMounted=true;tud_mount_cb();noReplay();
}else if(id=="AD24"){
 put("/x.txt","HOLD RGUI\nDELAY 5000\nSTRING BAD\n");start();awaitPhase("Ownership");lower::next=lower::Outcome::FalseAfterPossibleAcceptance;trialTick();trialDone();check(route_u::status().phase==route_u::Phase::Quarantined,"ambiguous right ownership write quarantines");noReplay();
}else if(id=="AD25"){
 put("/x.txt","RCTRL a\n");start();awaitPhase("Press");mock::usbReady=false;auto n=lower::count;for(unsigned i=0;i<100;++i)trialTick();check(lower::count==n,"right chord backpressure makes no lower calls");mock::usbReady=true;trialDone();check(operations().size()==2&&route_u::status().reason==route_u::Reason::Completed,"right chord accepted exactly once after retry");exactReport(0,16,{4});exactReport(1,0,{});noReplay();
}else if(id=="AD26"){
 completed("HOLD RCTRL\nHOLD RCTRL\nRELEASE RCTRL\nRELEASE RCTRL\n");check(operations().size()==4,"duplicate right hold/release remain idempotent fresh operations");exactReport(0,16,{});exactReport(1,16,{});exactReport(2,0,{});exactReport(3,0,{});std::set<uint64_t> ids;for(auto c:operations())ids.insert(c.operation);check(ids.size()==4,"operation identity never reused");
}else if(id=="AD27"){
 runSource("HOLD a\nHOLD b\nHOLD c\nHOLD d\nHOLD e\nHOLD f\nHOLD RSHIFT\nRCTRL g\n");check(route_u::status().reason!=route_u::Reason::Completed&&operations().size()==7,"right modifiers do not remove six-nonmodifier rollover limit");exactReport(6,32,{4,5,6,7,8,9});rightClear();noReplay();
}else if(id=="AD28"){
 for(unsigned mask:{16u,32u,64u,128u,18u,34u,240u}){lower::reset();runSource(h1Source(uint16_t((mask<<8)|4)).c_str());check(route_u::status().errorCode==unsigned(ds_preview::ErrorCode::InvalidExperimentalKeycode)&&operations().empty(),"right source names do not expand H1 packed whitelist");}
 lower::reset();completed("HOLD RSHIFT\nVAR $k=516\nINJECT_VAR $k\nRELEASE RSHIFT\n");exactReport(0,32,{});exactReport(1,34,{4});exactReport(2,32,{});exactReport(3,0,{});
}else if(id=="AD29"){
 completed("FUNCTION take()\nHOLD RSHIFT\nRETURN 1\nEND_FUNCTION\nVAR $x=take()\nWHILE $x<3\nSTRING a\n$x=$x+1\nEND_WHILE\nRELEASE RSHIFT\n");check(operations().size()==6,"right hold persists through function/loop");exactReport(0,32,{});exactReport(1,32,{4});exactReport(3,32,{4});exactReport(5,0,{});
}else if(id=="AD30"){
 completed("DEFINE #R RSHIFT\nHOLD #R\nSTRING a\nRELEASE #R\nIF_DEFINED_TRUE #ABSENT\nRSHIFT RSHIFT a\nEND_IF_DEFINED\n");exactReport(0,32,{});exactReport(1,32,{4});exactReport(3,0,{});lower::reset();rejected("DEFINE #CMD RCTRL\n#CMD a\n");
}else if(id=="AD31"){
 beginWait("$_EVILDUCK_LOCK_TIMEOUT=10000\nHOLD RSHIFT\nWAIT_FOR_CAPS_CHANGE\nSTRING BAD\n");handleStop(&r);trialDone();check(route_u::status().reason==route_u::Reason::Cancelled&&operations().size()==1,"right hold lockwait STOP suppresses text");rightClear();noReplay();
}else if(id=="AD32"){
 const char*s="HOLD RSHIFT\nRCTRL a\nRELEASE RSHIFT\n";ds_preview::Program p;check(p.compile(s,strlen(s)),"compile allocation probe");ds_preview::Runtime rt;unsigned count=0;check(rt.start(p,[](void*c,const ds_preview::Event&){++*static_cast<unsigned*>(c);return ds_preview::Accept::Accepted;},&count),"start allocation probe");auto before=native_alloc::calls();for(unsigned i=0;i<100&&rt.state()==ds_preview::State::Running;++i)rt.tick(i);check(rt.state()==ds_preview::State::Completed&&count==3&&native_alloc::calls()==before,"right command Runtime execution has no C++ heap allocation");
}else if(id=="AD33"){
 beginWait("$_EVILDUCK_LOCK_TIMEOUT=65535\nHOLD RSHIFT\nWAIT_FOR_CAPS_ON\nSTRING BAD\n");auto at=route_u::status().waitStarted;mock::now=at+30000;led_mock::nowUs=uint64_t(mock::now)*1000;finishBad();check(route_u::status().reason==route_u::Reason::Runtime&&route_u::status().errorCode==unsigned(ds_preview::ErrorCode::Timeout)&&operations().size()==1,"whole-run budget preserved while right modifier held");rightClear();noReplay();
}else if(id=="AD34"){
 put("/x.txt","HOLD RCTRL\nDELAY 5000\n");start();reports(1);auto n=lower::count;check(!hid_backend::hold(32,0)&&!hid_backend::release(16,0)&&!com::executeNow("INJECT_MOD RSHIFT"),"legacy mutation denied under right-side Route B lease");check(lower::count==n&&hid_backend::hasPersistent(),"denied right mutations leave ownership untouched");route_u::stop();trialDone();rightClear();
}else if(id=="AD35"){
 put("/x.txt","HOLD RSHIFT\nRELEASE RSHIFT\nSTRING a\n");start();reports(1);trialTick();awaitPhase("Ownership");mock::usbReady=false;auto n=lower::count;trialTick();check(!hid_backend::hasPersistent()&&lower::count==n,"right release intent removed before unavailable submit");for(unsigned i=0;i<50;++i)trialTick();check(lower::count==n,"later text cannot overtake right release");mock::usbReady=true;trialDone();exactReport(0,32,{});exactReport(1,0,{});exactReport(2,0,{4});exactReport(3,0,{});
}else if(id=="AD36"){
 put("/x.txt","HOLD RSHIFT\nDELAY 5000\n");start();reports(1);auto request=route_u::status().request;auto session=operations()[0].session;route_u::stop();trialDone();lower::reset();completed("STRING a\n");check(route_u::status().request!=request&&operations()[0].session!=session,"subsequent run receives fresh request and lease");exactReport(0,0,{4});exactReport(1,0,{});rightClear();noReplay();
}else check(false,"unknown right modifier case");std::cout<<"PASS "<<id<<" ("<<assertions<<" assertions)\n";return 0;
}catch(const std::exception&e){std::cerr<<"FAIL "<<argv[1]<<": "<<e.what()<<" ("<<assertions<<")\n";return 1;}}
