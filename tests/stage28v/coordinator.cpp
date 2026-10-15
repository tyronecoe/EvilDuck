#include "coordinator.h"
#include "task_platform.h"
#include "adapter.h"
#include "file_source.h"
#include "com.h"
#include "duckscript.h"
#include "hid_backend.h"
#include "execution_guard.h"
#include "attackmode.h"
#include "spiffs.h"
#include <cstring>
namespace route_u {
namespace {
struct Request{bool start=false;uint64_t id=0;char path[96]{};uint32_t tag=0;};
struct Publication{
 u_platform::Task owner{};Status status{};uint64_t next=0,transaction=0;Service service{};
 Request queue[4]{};unsigned head=0,count=0;bool stop=false,loss=false;
 bool transactionBusy=false,transactionClosing=false;
 bool selected=false;unsigned mutationDepth=0;u_platform::Task mutationTask{},chunkTask{};
} pub;
static native_b::Adapter adapter;
static FileSource file;
static bool stepping=false,verified=false;
void phase(Phase p){u_platform::Critical lock;pub.status.phase=p;}
void reason(Reason r){u_platform::Critical lock;if(pub.status.reason==Reason::None)pub.status.reason=r;}
Reason faultReason(native_b::Fault f){
 return f==native_b::Fault::Reader?Reason::File:f==native_b::Fault::Compiler?Reason::Compiler:f==native_b::Fault::Capability?Reason::Capability:f==native_b::Fault::Runtime?Reason::Runtime:f==native_b::Fault::Deadline||f==native_b::Fault::Clearing?Reason::Deadline:Reason::Backend;
}
void complete(Reason r){file.close();u_platform::Critical lock;if(pub.status.reason==Reason::None)pub.status.reason=r;pub.status.phase=Phase::Idle;pub.status.owned=false;pub.count=pub.head=0;u_platform::gate={};}
bool mediaIdle(){return !attackmode::storageRequested()&&!attackmode::storageEnabled()&&!attackmode::storagePreparing();}
bool safeLegacyIdle(){return !duckscript::running()&&!com::busy()&&backend_b::available()&&mediaIdle()&&!spiffs::streaming();}
bool priority(){
 bool stop,loss;{u_platform::Critical lock;stop=pub.stop;loss=pub.loss;}
 if(loss){reason(Reason::Lost);backend_b::Scope scope(adapter.session(),backend_b::status().operation);if(scope)backend_b::externalLoss();}
 return stop||loss;
}
}
bool bindOwner(){bool ok;{u_platform::Critical lock;if(!pub.owner)pub.owner=u_platform::current();ok=pub.owner&&pub.owner==u_platform::current();}if(ok&&!stepping)adapter.cancellationPoll=priority;return ok;}
bool ownerTask(){u_platform::Critical lock;return pub.owner&&pub.owner==u_platform::current();}
bool owned(){u_platform::Critical lock;return pub.status.owned;}
Status status(){u_platform::Critical lock;return pub.status;}
bool legacyAllowed(){u_platform::Critical lock;return !pub.status.owned&&!pub.transaction;}
bool selected(){u_platform::Critical lock;return pub.selected;}
void legacySelected(){u_platform::Critical lock;if(!pub.status.owned)pub.selected=false;}
Reply requestStart(const char* path,Mode mode){
 if(!path||mode!=Mode::RouteB)return Reply::Invalid;
 size_t n=0;while(n<96&&path[n]){unsigned char c=path[n];if(c<32||c>126)return Reply::Invalid;++n;}
 if(!n||n==96)return Reply::Invalid;
 // Never wait behind execution/filesystem work from a service task.
 execution::TryGuard executionLock;if(!executionLock)return Reply::Busy;
 if(!safeLegacyIdle())return Reply::Busy;
 u_platform::Critical lock;if(!pub.owner)return Reply::Unbound;
 if(pub.status.owned||pub.transaction||pub.mutationDepth)return Reply::Busy;
 if(pub.count==4)return Reply::QueueFull;
 if(pub.next==UINT64_MAX)return Reply::Exhausted;
 Request& q=pub.queue[(pub.head+pub.count)%4];q={};q.start=true;q.id=++pub.next;memcpy(q.path,path,n+1);++pub.count;
 pub.status={Phase::Queued,Reason::None,q.id,0,0,true};pub.stop=pub.loss=false;pub.selected=true;
 u_platform::gate={pub.owner,true,false,false};return Reply::Accepted;
}
Reply requestSnapshot(uint32_t tag){u_platform::Critical lock;if(pub.count==4)return Reply::QueueFull;if(pub.next==UINT64_MAX)return Reply::Exhausted;Request& q=pub.queue[(pub.head+pub.count)%4];q={};q.id=++pub.next;q.tag=tag;++pub.count;return Reply::Accepted;}
void stop(){u_platform::Critical lock;if(pub.status.owned)pub.stop=true;}
void loss(){u_platform::Critical lock;if(pub.status.owned)pub.loss=true;}
bool begin(Service s,Token& out){
 if(out.id)return false;execution::TryGuard executionLock;if(!executionLock)return false;
 if(duckscript::running()||com::busy()||!mediaIdle())return false;
 u_platform::Critical lock;if(pub.status.owned||pub.transaction||pub.mutationDepth||pub.next==UINT64_MAX)return false;
 pub.transaction=++pub.next;pub.service=s;pub.transactionBusy=pub.transactionClosing=false;out.id=pub.transaction;return true;
}
// Called only with execution::TryGuard held. Publication never calls a lower API.
bool enterMutation(){u_platform::Critical lock;
 if(pub.status.owned||pub.mutationDepth==32)return false;
 if(pub.mutationDepth){if(pub.mutationTask!=u_platform::current())return false;}
 else if(pub.transaction&&(!pub.transactionBusy||pub.transactionClosing||pub.chunkTask!=u_platform::current()))return false;
 pub.mutationTask=u_platform::current();++pub.mutationDepth;return true;
}
void leaveMutation(){u_platform::Critical lock;if(pub.mutationDepth&&pub.mutationTask==u_platform::current()){if(!--pub.mutationDepth)pub.mutationTask={};}}
bool valid(Token t){u_platform::Critical lock;return t.id&&t.id==pub.transaction&&!pub.transactionClosing;}
bool enterChunk(Token t){u_platform::Critical lock;if(!t.id||t.id!=pub.transaction||pub.transactionBusy||pub.transactionClosing)return false;pub.transactionBusy=true;pub.chunkTask=u_platform::current();return true;}
bool leaveChunk(Token t){u_platform::Critical lock;if(!t.id||t.id!=pub.transaction||!pub.transactionBusy||pub.chunkTask!=u_platform::current())return false;pub.transactionBusy=false;pub.chunkTask={};if(pub.transactionClosing){pub.transaction=0;pub.transactionClosing=false;}return true;}
bool end(Token t){u_platform::Critical lock;if(!t.id||t.id!=pub.transaction)return false;if(pub.transactionBusy){pub.transactionClosing=true;return false;}pub.transaction=0;pub.transactionClosing=false;return true;}
void tick(uint32_t now){
 if(!ownerTask()||stepping)return;
 stepping=true;struct Exit{~Exit(){stepping=false;}}exit;
 bool stopping,lost;Request request;bool have=false;
 {u_platform::Critical lock;stopping=pub.stop;lost=pub.loss;pub.stop=pub.loss=false;
  if(!stopping&&!lost&&pub.count){request=pub.queue[pub.head];pub.head=(pub.head+1)%4;--pub.count;have=true;}}
 if(!owned())return;
 if(stopping||lost){
  if(lost)reason(Reason::Lost);
  if(!adapter.leased()){adapter.cancel();complete(lost?Reason::Lost:Reason::Cancelled);return;}
  if(lost){backend_b::Scope scope(adapter.session(),backend_b::status().operation);if(scope)backend_b::externalLoss();}
  adapter.cancel();file.close();phase(Phase::Stopping);
 }
 if(have&&request.start){
  if(request.id!=status().request){complete(Reason::Backend);return;}
  if(!file.open(request.path)){complete(Reason::File);return;}
  verified=false;if(!adapter.prepare(file.reader())){complete(Reason::File);return;}phase(Phase::Capturing);
 }
 if(status().phase==Phase::Queued)return; // A poll ahead of Start cannot reuse old terminal state.
 auto state=adapter.state();
 if(state==native_b::State::Loading){adapter.step(now);phase(Phase::Capturing);}
 else if(state==native_b::State::Compiling&&!verified){
  phase(Phase::Verifying);auto v=file.verify(adapter.capturedData(),adapter.capturedSize());
  if(v==FileSource::Verify::Error){adapter.cancel();complete(Reason::File);return;}if(v==FileSource::Verify::Complete)verified=true;
 }else if(state==native_b::State::Compiling){adapter.step(now);phase(Phase::Compiling);}
 else if(state==native_b::State::Ready){phase(Phase::Ready);if(!adapter.start(now)){complete(Reason::Backend);return;}}
 else if(state==native_b::State::Syncing||state==native_b::State::Running||state==native_b::State::Clearing){adapter.step(now);phase(adapter.state()==native_b::State::Clearing?Phase::Stopping:Phase::Running);}
 state=adapter.state();
 if(adapter.fault()!=native_b::Fault::None){reason(faultReason(adapter.fault()));auto d=adapter.diagnostic();u_platform::Critical lock;pub.status.line=d.line;pub.status.errorCode=static_cast<uint16_t>(d.code);}
 if(state==native_b::State::Completed)complete(Reason::Completed);
 else if(state==native_b::State::Cancelled)complete(Reason::Cancelled);
 else if(state==native_b::State::Error){
  auto d=adapter.diagnostic();{u_platform::Critical lock;pub.status.line=d.line;}
  complete(faultReason(adapter.fault()));
 }else if(state==native_b::State::Quarantined){file.close();reason(Reason::Backend);phase(Phase::Quarantined);}
}
void exhaustForTest(){u_platform::Critical lock;if(!pub.status.owned&&!pub.transaction)pub.next=UINT64_MAX;}
void setReadPollForTest(bool(*poll)()){if(ownerTask()&&!owned())file.mayRead=poll;}
size_t persistentBytes(){return sizeof(pub)+sizeof(adapter)+sizeof(file);}
}
