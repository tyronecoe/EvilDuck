#include "keyboard_cases.inc"
#include <condition_variable>
#include <chrono>
#include <atomic>
#include <cstring>
#include "diagnostics.h"
struct Holder{
 std::mutex m;std::condition_variable cv;bool held=false,release=false,finished=false;std::thread worker;
 Holder(execution::Owner owner=execution::Owner::DuckUpdate):worker([this,owner]{u_platform::taskForTest(2);{execution::Guard lock(owner);std::unique_lock<std::mutex> l(m);held=true;cv.notify_all();cv.wait(l,[&]{return release;});}{std::lock_guard<std::mutex> l(m);finished=true;}cv.notify_all();}){std::unique_lock<std::mutex> l(m);cv.wait(l,[&]{return held;});}
 void end(){std::unique_lock<std::mutex> l(m);release=true;cv.notify_all();cv.wait(l,[&]{return finished;});}
 ~Holder(){end();worker.join();}
};
static Holder* holder=nullptr;
static void releaseHolder(){holder->end();}
static bool lockFreeAtSend=false;
static void atSend(){std::thread t([]{execution::TryGuard g;lockFreeAtSend=bool(g);});t.join();}
int main(int argc,char**argv){if(argc!=2)return 2;if(argv[1][0]!='H')return historical_keyboard_main(argc,argv);try{
 mscMock::reset();mock::reset();setup();check(startupControlledReady&&settings::ready(),"controlled startup");check(route_u::bindOwner(),"owner bound");lower::reset();mock::blockingDelays=0;std::string id=argv[1];auto r=req();
 if(id=="H01"||id=="H02"){
  Holder h;holder=&h;execution::contendedForTest=releaseHolder;
  if(id=="H01")handleStatus(&r);else handleDiagnostics(&r);
  execution::contendedForTest=nullptr;check(r.code==200&&r.replies==1,"short contention yields then captures");check(execution::statistics().contentions>0&&execution::statistics().lastContendedOwner==uint32_t(execution::Owner::DuckUpdate),"actual holder classified");
 }else if(id=="H03"||id=="H04"){
  Holder h;auto before=execution::statistics().timeouts;auto began=std::chrono::steady_clock::now();if(id=="H03")handleStatus(&r);else handleDiagnostics(&r);auto elapsed=std::chrono::steady_clock::now()-began;check(r.code==409&&r.replies==1&&r.response=="Execution busy","persistent contention not suppressed");check(execution::statistics().timeouts==before+1,"one bounded timeout");check(elapsed<std::chrono::seconds(1),"no indefinite host wait; not physical 5ms bound");
 }else if(id=="H05"||id=="H06"){
  r.headers.clear();Holder h;holder=&h;execution::contendedForTest=releaseHolder;if(id=="H05")handleStatus(&r);else handleDiagnostics(&r);execution::contendedForTest=nullptr;check(r.code==401&&r.response.indexOf("Unauthorized")>=0,"unauthenticated request still refused after wait");
 }else if(id=="H07"||id=="H08"){
  http_mock::sending=atSend;if(id=="H07")handleStatus(&r);else handleDiagnostics(&r);http_mock::sending=nullptr;check(r.code==200&&lockFreeAtSend,"HTTP send outside execution lock");
 }else if(id=="H09"){
  put("/x.txt","DELAY 1000\nSTRING BAD\n");start();tick();Holder h;holder=&h;execution::contendedForTest=releaseHolder;handleStop(&r);execution::contendedForTest=nullptr;check(r.code==202,"auth wait then STOP publication");done();check(route_u::status().reason==route_u::Reason::Cancelled&&!route_u::owned()&&presses().empty(),"STOP observed without any payload");
 }else if(id=="H10"){
  put("/x.txt","DELAY 1000\nSTRING BAD\n");start();{Holder h;handleStop(&r);check(r.code==409&&route_u::owned(),"timed-out STOP not falsely acknowledged or auth401");}handleStop(&r);done();check(r.code==202&&!route_u::owned()&&route_u::status().reason==route_u::Reason::Cancelled,"explicit STOP retry responsive");
 }else if(id=="H11"){
  for(int i=0;i<20;++i){auto q=req();loop();handleStatus(&q);check(q.code==200&&q.response.indexOf("request-capture")>=0,"idle current request capture");}
  check(route_x::snapshot().ticks>=20&&lower::count==0,"idle progress without HID");
 }else if(id=="H12"){
  put("/x.txt","DELAY 500\nCOMMAND a\n");start();unsigned passed=0;for(int i=0;i<2000&&route_u::owned();++i){tick();auto q=req();handleStatus(&q);check(q.code==200,"progress polling no contention when owner yielded");++passed;}check(passed>500&&!route_u::owned()&&route_u::status().reason==route_u::Reason::Completed,"single-owner progresses with polling");reports({{8,4}});
 }else if(id=="H13"){
  mock::now=100;route_u::tick(mock::now);auto s=route_x::snapshot();mock::now=350;handleDiagnostics(&r);check(r.code==200&&r.response.indexOf("published-observation")>=0&&r.response.indexOf("\"observationAgeMs\":250")>=0&&s.observedAtMs==100,"published observation explicitly aged, not current");
 }else if(id=="H14"){
  mock::now=UINT32_MAX-10;route_u::tick(mock::now);mock::now=9;handleDiagnostics(&r);check(r.code==200&&r.response.indexOf("\"observationAgeMs\":20")>=0,"unsigned age wrap");
 }else if(id=="H15"){
  route_x::Snapshot s{};s.observationKnown=true;s.ticks=s.maxIntervalUs=s.maxWorkUs=s.clockErrors=s.samples=s.accepted=s.refused=s.queuePeak=s.stopPublished=s.stopObserved=s.completedTurns=UINT32_MAX;s.localSequence=s.clearRequest=s.clearSubmitted=UINT64_MAX;s.resources={UINT32_MAX,UINT32_MAX,UINT32_MAX,UINT32_MAX,UINT32_MAX,true,true};char out[1536];check(route_x::formatSnapshot(s,UINT32_MAX,out,sizeof(out))>0&&strlen(out)<sizeof(out),"worst-width diagnostic record bounded");char tiny[4];check(!route_x::formatSnapshot(s,0,tiny,sizeof(tiny))&&tiny[0]==0,"truncation still reported");
 }else if(id=="H16"){
  settings::setSSID("quoted\"name\\line");handleStatus(&r);check(r.code==200&&r.response.indexOf("quoted\\\"name\\\\line")>=0,"owned status text escaped before JSON response");
 }else if(id=="H17"){
  put("/x.txt","STRING BAD\n");start();statusCapturedForTest=[](){route_u::stop();route_u::tick(mock::now);};handleStatus(&r);statusCapturedForTest=nullptr;check(!route_u::owned()&&route_u::status().phase==route_u::Phase::Idle,"owner can complete after captured publication");check(r.code==200&&r.response.indexOf("\"routeBPhase\":1")>=0&&r.response.indexOf("\"running\":true")>=0&&r.response.indexOf("\"script\":\"RouteB\"")>=0,"one Route B snapshot drives all related fields");check(presses().empty(),"coherence probe sends no payload");
 }else if(id=="H18"){
  r.headers["X-Duck-Password"]="incorrect";http_mock::sending=atSend;handleStop(&r);http_mock::sending=nullptr;check(r.code==401&&lockFreeAtSend,"incorrect STOP credentials rejected and response unlocked");
 }else check(false,"unknown case");
 std::cout<<"PASS "<<id<<" ("<<assertions<<" assertions)\n";return 0;
 }catch(const std::exception&e){std::cerr<<"FAIL "<<argv[1]<<": "<<e.what()<<" ("<<assertions<<")\n";return 1;}}
