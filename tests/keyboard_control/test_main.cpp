#include "control_parent_cases.inc"
#include <array>
#include <set>

static std::vector<lower::Call> operations(){
 std::vector<lower::Call> out;
 for(size_t i=0;i<lower::count;++i)if(!lower::calls[i].clear)out.push_back(lower::calls[i]);
 return out;
}
static bool zero(const lower::Call& c){for(uint8_t b:c.bytes)if(b)return false;return true;}
static bool contains(const lower::Call& c,uint8_t usage){for(unsigned i=2;i<8;++i)if(c.bytes[i]==usage)return true;return false;}
static void exactReport(size_t index,uint8_t modifiers,std::initializer_list<uint8_t> keys){
 auto calls=operations();check(index<calls.size(),"expected current operation report exists");auto c=calls[index];
 std::array<uint8_t,8> expected{};expected[0]=modifiers;unsigned i=2;for(auto key:keys){check(i<8,"fixture report bounded");expected[i++]=key;}
 check(memcmp(c.bytes,expected.data(),8)==0,"exact eight-byte modifier/reserved/usage bytes");
 check(c.instance==0&&c.id==1&&c.session&&c.operation,"actual report ID and fresh lease correlation");
}
static void awaitPhase(const char* wanted){for(unsigned i=0;i<20000&&route_u::owned();++i){if(std::string(route_b::phase())==wanted)return;trialTick();}check(false,"expected scheduler phase reachable");}
static void reports(unsigned wanted){for(unsigned i=0;i<20000&&route_u::owned()&&operations().size()<wanted;++i)trialTick();check(operations().size()==wanted,"bounded report count reached");}
static void completed(const char* source){runSource(source);check(route_u::status().reason==route_u::Reason::Completed&&!route_u::owned(),"actual Route B completed");check(!hid_backend::hasPersistent()&&!backend_b::status().active,"terminal state relinquishes held ownership and lease");check(lower::count&&zero(lower::calls[lower::count-1]),"last local cleanup submission neutral");}
static void rejected(const char* source){runSource(source);check(route_u::status().reason!=route_u::Reason::Completed&&lower::count==0,"invalid source rejects before output and no legacy fallback");}
static void noReplay(){auto n=lower::count;for(unsigned i=0;i<1000;++i)trialTick();check(lower::count==n,"no delayed report after terminal state");}
static bool reentrantSent;

int main(int argc,char**argv){
 if(argc!=2)return 2;
 if(argv[1][0]!='Q')return historical_caps_stop_main(argc,argv);
 try{
  mscMock::reset();mock::reset();setup();check(startupControlledReady&&route_u::bindOwner(),"actual controlled owner startup");lower::reset();led_mock::nowUs=0;auto r=req();std::string id=argv[1];
  if(id=="Q01"){
   completed("INJECT_MOD CONTROL\n");check(operations().size()==2,"one modifier press and one release");exactReport(0,1,{});exactReport(1,0,{});
  }else if(id=="Q02"){
   completed("INJECT_MOD CONTROL\nINJECT_MOD CTRL\nINJECT_MOD SHIFT\nINJECT_MOD ALT\nINJECT_MOD OPTION\nINJECT_MOD GUI\nINJECT_MOD WINDOWS\nINJECT_MOD COMMAND\n");
   const uint8_t masks[]={1,1,2,4,4,8,8,8};check(operations().size()==16,"supported existing aliases each tap once");for(unsigned i=0;i<8;++i){exactReport(i*2,masks[i],{});exactReport(i*2+1,0,{});}
  }else if(id=="Q03"){
   for(const char* s:{"INJECT_MOD\n","INJECT_MOD 2\n","INJECT_MOD SHIFT ALT\n","INJECT_MOD SHIFT A\n","INJECT_MOD UNSUPPORTED\n","IF FALSE THEN\nINJECT_MOD\nEND_IF\n","FUNCTION untouched()\nINJECT_MOD\nEND_FUNCTION\n"}){lower::reset();rejected(s);}
  }else if(id=="Q04"){
   completed("HOLD a\nDELAY 10\nRELEASE a\n");check(operations().size()==2,"hold has no automatic transient release");exactReport(0,0,{4});exactReport(1,0,{});
  }else if(id=="Q05"){
   completed("HOLD SHIFT\nSTRING a\nRELEASE SHIFT\n");check(operations().size()==4,"persistent modifier merged and restored around text");exactReport(0,2,{});exactReport(1,2,{4});exactReport(2,2,{});exactReport(3,0,{});
  }else if(id=="Q06"){
   completed("HOLD a\nSTRING b\nRELEASE a\n");check(operations().size()==4,"held nonmodifier restored after transient");exactReport(0,0,{4});exactReport(1,0,{4,5});exactReport(2,0,{4});exactReport(3,0,{});
  }else if(id=="Q07"){
   completed("HOLD CONTROL\nHOLD CTRL\nRELEASE CTRL\nRELEASE CONTROL\n");check(operations().size()==4,"duplicate alias hold and absent release each fresh acknowledgement");exactReport(0,1,{});exactReport(1,1,{});exactReport(2,0,{});exactReport(3,0,{});auto c=operations();std::set<uint64_t> ids;for(auto v:c)ids.insert(v.operation);check(ids.size()==4,"no prior operation acknowledgement reused");
  }else if(id=="Q08"){
   completed("HOLD a\nHOLD a\nRELEASE a\nRELEASE a\n");check(operations().size()==4,"idempotent ownership each reports current union");exactReport(0,0,{4});exactReport(1,0,{4});exactReport(2,0,{});exactReport(3,0,{});
  }else if(id=="Q09"){
   completed("HOLD a\nHOLD b\nHOLD c\nHOLD d\nHOLD e\nHOLD f\nRELEASE a\nRELEASE b\nRELEASE c\nRELEASE d\nRELEASE e\nRELEASE f\n");check(operations().size()==12,"six-key bound and selective releases");exactReport(5,0,{4,5,6,7,8,9});exactReport(6,0,{5,6,7,8,9});exactReport(11,0,{});
  }else if(id=="Q10"||id=="Q11"){
   runSource(id=="Q10"?"HOLD a\nHOLD b\nHOLD c\nHOLD d\nHOLD e\nHOLD f\nHOLD g\n":"HOLD a\nHOLD b\nHOLD c\nHOLD d\nHOLD e\nHOLD f\nSTRING g\n");
   check(route_u::status().reason!=route_u::Reason::Completed,"seventh distinct usage fails");check(operations().size()==6,"offending hold/tap made no partial report");for(auto c:operations())check(!contains(c,10),"overflow usage never submitted");check(!route_u::owned()&&!hid_backend::hasPersistent()&&zero(lower::calls[lower::count-1]),"runtime overflow neutral cleanup");
  }else if(id=="Q12"){
   completed("HOLD SHIFT\nINJECT_MOD CONTROL\nRELEASE SHIFT\n");exactReport(0,2,{});exactReport(1,3,{});exactReport(2,2,{});exactReport(3,0,{});
  }else if(id=="Q13"||id=="Q14"){
   runSource(id=="Q13"?"HOLD SHIFT\nINJECT_MOD SHIFT\n":"HOLD a\nSTRING a\n");check(route_u::status().reason!=route_u::Reason::Completed&&operations().size()==1,"tap of owned physical usage rejected, not fake release/repress");check(!route_u::owned()&&!hid_backend::hasPersistent()&&zero(lower::calls[lower::count-1]),"held-tap failure clears ownership");
  }else if(id=="Q15"){
   put("/x.txt","HOLD SHIFT\nDELAY 5000\nSTRING BAD\n");start();reports(1);auto before=mock::now;handleStop(&r);trialDone();check(r.code==202&&route_u::status().reason==route_u::Reason::Cancelled&&!route_u::owned()&&mock::now-before<500,"STOP responsive while held/delayed");check(operations().size()==1&&!hid_backend::hasPersistent()&&zero(lower::calls[lower::count-1]),"only neutral cleanup follows stop");noReplay();
  }else if(id=="Q16"){
   put("/x.txt","HOLD a\nSTRING BAD\n");start();awaitPhase("Ownership");mock::usbReady=false;handleStop(&r);for(unsigned i=0;i<10;++i)trialTick();check(operations().empty()&&route_u::owned(),"STOP pending hold never submits it; retains cleanup lease");mock::usbReady=true;trialDone();check(!route_u::owned()&&!hid_backend::hasPersistent()&&operations().empty(),"only priority cleanup after pending hold cancellation");
  }else if(id=="Q17"){
   put("/x.txt","HOLD a\nDELAY 5000\n");start();reports(1);mock::usbReady=false;handleStop(&r);for(unsigned i=0;i<10;++i)trialTick();check(route_u::owned()&&route_u::requestStart("/x.txt")==route_u::Reply::Busy,"held cleanup backpressure blocks future owner");mock::usbReady=true;trialDone();check(!route_u::owned()&&operations().size()==1&&!hid_backend::hasPersistent(),"pending cleanup resumes once without stale held report");noReplay();
  }else if(id=="Q18"){
   completed("HOLD a\n");check(operations().size()==1,"completion clears outstanding hold without artificial tap");noReplay();
  }else if(id=="Q19"){
   runSource("HOLD SHIFT\nSTOP_PAYLOAD\nSTRING BAD\n");check(route_u::status().reason==route_u::Reason::Cancelled&&operations().size()==1&&!route_u::owned()&&!hid_backend::hasPersistent(),"STOP_PAYLOAD cancels persistent ownership");noReplay();
  }else if(id=="Q20"){
   completed("FUNCTION take()\nHOLD SHIFT\nRETURN 1\nEND_FUNCTION\nVAR $x = take()\nWHILE $x < 3\nIF $x > 0 THEN\nSTRING a\nEND_IF\n$x = $x + 1\nEND_WHILE\nRELEASE SHIFT\n");
   check(operations().size()==6,"held state survives function return and nested control flow");exactReport(1,2,{4});exactReport(3,2,{4});exactReport(5,0,{});
  }else if(id=="Q21"){
   put("/x.txt","HOLD a\nDELAY 5000\n");start();reports(1);mock::usbMounted=false;tud_umount_cb();trialDone();auto n=lower::count;mock::usbMounted=true;tud_mount_cb();for(unsigned i=0;i<100;++i)trialTick();check(lower::count==n&&route_u::status().phase==route_u::Phase::Quarantined,"loss while held preserves quarantine and prevents replay");
  }else if(id=="Q22"||id=="Q23"){
   put("/x.txt","HOLD a\nDELAY 1\nRELEASE a\nSTRING BAD\n");start();if(id=="Q23"){reports(1);trialTick();}awaitPhase("Ownership");lower::next=lower::Outcome::FalseAfterPossibleAcceptance;trialTick();trialDone();check(route_u::status().phase==route_u::Phase::Quarantined,"ambiguous ownership write quarantined");auto n=lower::count;for(unsigned i=0;i<100;++i)trialTick();check(lower::count==n,"no automatic retry after ambiguous ownership write");
  }else if(id=="Q24"){
   put("/x.txt","HOLD a\nRELEASE a\n");start();awaitPhase("Ownership");mock::usbReady=false;auto n=lower::count;for(unsigned i=0;i<100;++i)trialTick();check(lower::count==n,"not-ready ownership makes no lower call");mock::usbReady=true;trialDone();check(route_u::status().reason==route_u::Reason::Completed&&operations().size()==2,"pending ownership resumes once on readiness");
  }else if(id=="Q25"){
   put("/x.txt","HOLD SHIFT\nDELAY 5000\n");start();reports(1);auto n=lower::count;check(!hid_backend::hold(1,0)&&!hid_backend::release(2,0)&&!com::executeNow("INJECT_MOD ALT"),"legacy calls remain denied under Route B lease");check(lower::count==n&&hid_backend::hasPersistent(),"denied live operations do not touch owned state or output");route_u::stop();trialDone();
  }else if(id=="Q26"){
   put("/x.txt","HOLD a\nDELAY 5000\n");start();reports(1);auto first=route_u::status().request;route_u::stop();trialDone();lower::reset();completed("STRING b\n");check(route_u::status().request!=first&&operations().size()==2,"new run gets fresh identity and no stale held replay");exactReport(0,0,{5});exactReport(1,0,{});noReplay();
  }else if(id=="Q27"){
   completed("DEFINE #MOD SHIFT\nHOLD #MOD\nSTRING a\nRELEASE #MOD\n");exactReport(0,2,{});exactReport(1,2,{4});exactReport(3,0,{});
  }else if(id=="Q28"){
   for(const char* s:{"HOLD\n","RELEASE\n","HOLD SHIFT A\n","RELEASE SHIFT ALT\n","IF FALSE THEN\nHOLD UNKNOWN_KEY\nEND_IF\n","FUNCTION unused()\nRELEASE UNKNOWN_KEY\nEND_FUNCTION\n"}){lower::reset();rejected(s);}
  }else if(id=="Q29"){
   completed("FUNCTION skipped()\nHOLD SHIFT\nEND_FUNCTION\nSTRING a\n");check(operations().size()==2,"unused function body never acquires key state");exactReport(0,0,{4});exactReport(1,0,{});
  }else if(id=="Q30"){
   put("/x.txt","HOLD SHIFT\nDELAY 5000\n");start();reports(1);check(led_return::start(led_mock::nowUs),"explicit independent LED receiver start while held");feed();auto s=led_return::snapshot(led_mock::nowUs);check(s.state==led_return::State::Complete&&s.integrity&&std::string(s.text)==led_return::Message,"fixed EDR1 decode unchanged during persistent keyboard ownership");route_u::stop();trialDone();check(!route_u::owned()&&!hid_backend::hasPersistent(),"receiver does not prevent STOP cleanup");
  }else if(id=="Q31"){
   put("/x.txt","HOLD a\nDELAY 5000\n");start();reports(1);auto s=backend_b::status();auto n=lower::count;
   check(!backend_b::ownership(s.session,s.operation,5,true),"new entrypoint rejects missing permission");
   {backend_b::Scope permission(s.session,s.operation);check(bool(permission),"owner can establish current permission");check(!backend_b::ownership(s.session+1,s.operation,5,true),"wrong session denied");check(!backend_b::ownership(s.session,s.operation+1,5,true),"wrong operation denied");}
   check(lower::count==n,"denied entrypoints make no lower calls");route_u::stop();trialDone();check(!hid_backend::hasPersistent(),"permission denials preserve safe cleanup");
  }else if(id=="Q32"){
   put("/x.txt","HOLD a\nDELAY 5000\n");start();reports(1);auto s=backend_b::status();auto n=lower::count;bool entered=true,sent=true;
   std::thread other([&]{u_platform::taskForTest(2);backend_b::Scope permission(s.session,s.operation);entered=bool(permission);sent=backend_b::ownership(s.session,s.operation,5,true);});other.join();
   check(!entered&&!sent&&lower::count==n,"foreign task cannot mutate ownership through new public API");route_u::stop();trialDone();
  }else if(id=="Q33"){
   put("/x.txt","HOLD a\nRELEASE a\n");start();awaitPhase("Ownership");reentrantSent=true;lower::hook=[](){auto s=backend_b::status();reentrantSent=backend_b::ownership(s.session,s.operation,5,true);};trialTick();trialDone();
   check(!reentrantSent&&route_u::status().reason==route_u::Reason::Completed,"in-I/O reentrant ownership mutation refused");check(operations().size()==2,"reentrancy cannot inject extra report");exactReport(0,0,{4});exactReport(1,0,{});
  }else if(id=="Q34"){
   put("/x.txt","HOLD a\nRELEASE a\nSTRING b\n");start();reports(1);trialTick();awaitPhase("Ownership");mock::usbReady=false;auto n=lower::count;trialTick();
   check(!hid_backend::hasPersistent()&&lower::count==n,"release intent removed before unavailable submit without lower call");for(unsigned i=0;i<100;++i)trialTick();check(lower::count==n,"later transient cannot overtake release target");
   mock::usbReady=true;trialDone();check(route_u::status().reason==route_u::Reason::Completed&&operations().size()==4,"release target acknowledged before later tap");exactReport(0,0,{4});exactReport(1,0,{});exactReport(2,0,{5});exactReport(3,0,{});
  }else if(id=="Q35"){
   completed("HOLD CONTROL\nALT b\nRELEASE CONTROL\n");check(operations().size()==4,"held and transient chord modifiers merge once");exactReport(0,1,{});exactReport(1,5,{5});exactReport(2,1,{});exactReport(3,0,{});
  }else if(id=="Q36"){
   runSource("HOLD SHIFT\nVAR $zero=0\nVAR $bad=1/$zero\nSTRING BAD\n");check(route_u::status().reason!=route_u::Reason::Completed&&operations().size()==1,"runtime arithmetic failure after hold has no later text");check(!route_u::owned()&&!hid_backend::hasPersistent()&&zero(lower::calls[lower::count-1]),"runtime failure releases current logical owner");noReplay();
  }else if(id=="Q37"){
   rejected("REM preserved physical line\n\nINJECT_MOD\n");check(route_u::status().line==3&&route_u::status().errorCode!=0,"new grammar failure retains physical source line diagnostic");
  }else check(false,"unknown keyboard-control case");
  std::cout<<"PASS "<<id<<" ("<<assertions<<" assertions)\n";return 0;
 }catch(const std::exception& e){std::cerr<<"FAIL "<<argv[1]<<": "<<e.what()<<" ("<<assertions<<")\n";return 1;}
}
