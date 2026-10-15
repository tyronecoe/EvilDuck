#include "adapter.h"
#include "com.h"
#include "hid_backend.h"
#include <cstring>
namespace native_b {
using ds_preview::Accept;using ds_preview::EventType;
bool Adapter::prepare(const char* s,size_t n){
 if(inStep_||leased_||!(state_==State::Idle||state_==State::Completed||state_==State::Cancelled||state_==State::Error))return false;
 memory_={s,n,0};return prepare(memory_.reader());
}
bool Adapter::prepare(ds_preview::Reader r){
 if(inStep_||leased_||!(state_==State::Idle||state_==State::Completed||state_==State::Cancelled||state_==State::Error))return false;
 fault_=Fault::None;pending_=false;used_=0;loadTurns_=0;admissions_=acks_=retries_=delayAcks_=0;
 if(!r.read||!r.seek||r.bytes>ds_preview::MaxSource){fail(Fault::Reader);return false;}
 inStep_=true;bool ok=r.seek(r.context,0);inStep_=false;
 if(!ok){fail(Fault::Reader);return false;}
 reader_=r;state_=State::Loading;return true;
}
bool Adapter::start(uint32_t now){
 if(inStep_||leased_||state_!=State::Ready)return false;
 inStep_=true;bool ok=route_b::acquire(session_);inStep_=false;
 if(!ok)return false;
 leased_=true;now_=since_=now;turns_=0;state_=State::Syncing;return true;
}
void Adapter::fail(Fault f){if(fault_==Fault::None)fault_=f;finish(State::Error);}
void Adapter::finish(State terminal){
 compiler_.cancel();runtime_.cancel();pending_=false;target_=terminal;
 if(leased_){route_b::cancel(session_);state_=State::Clearing;since_=now_;turns_=0;}
 else state_=terminal;
}
void Adapter::cancel(){if(inStep_){cancelRequested_=true;return;}if(state_==State::Loading||state_==State::Compiling||state_==State::Ready||state_==State::Syncing||state_==State::Running)finish(State::Cancelled);}
bool Adapter::inspect(route_b::Result r){
 if(!pending_||state_!=State::Running||!route_b::equal(r.id,id_))return false;
 // Only the matching immutable admission's real scheduler result can advance.
 auto actual=route_b::result(session_);return route_b::equal(actual.id,r.id)&&actual.kind==r.kind;
}
Accept Adapter::sink(void* c,const ds_preview::Event& e){return static_cast<Adapter*>(c)->receive(e);}
Accept Adapter::receive(const ds_preview::Event& e){
 if(state_!=State::Running)return Accept::Failed;
 if(!route_b::environment()){fail(Fault::Environment);return Accept::Failed;}
 if(e.type==EventType::Delay){if(pending_){fail(Fault::Result);return Accept::Failed;}++delayAcks_;return Accept::Accepted;}
 if(pending_){
  if(e.type!=event_.type||e.value!=event_.value){fail(Fault::Result);return Accept::Failed;}
  auto r=route_b::result(session_);
  if(!route_b::equal(r.id,id_)){fail(Fault::Result);return Accept::Failed;}
  if(r.kind==route_b::ResultKind::Pending){++retries_;return Accept::Retry;}
  if(r.kind!=route_b::ResultKind::Done||!route_b::consume(r)){fail(Fault::Backend);return Accept::Failed;}
  pending_=false;++acks_;return Accept::Accepted;
 }
 route_b::Admission a=route_b::Admission::Rejected;
 if(e.type==EventType::Character)a=route_b::character(session_,e.value,id_);
 else if(e.type==EventType::KeyTap)a=route_b::key(session_,e.value,id_);
 if(a!=route_b::Admission::Admitted){fail(Fault::Admission);return Accept::Failed;}
 event_=e;pending_=true;since_=now_;turns_=0;++admissions_;++retries_;return Accept::Retry;
}
void Adapter::step(uint32_t now){
 if(inStep_)return;
 inStep_=true;struct Guard{bool& b;~Guard(){b=false;}}guard{inStep_};now_=now;
 if(cancelRequested_){cancelRequested_=false;finish(State::Cancelled);return;}
 if(state_==State::Loading){
  if(loadTurns_++==ds_preview::MaxCompileSteps){fail(Fault::Reader);return;}
  char chunk[ds_preview::ReadChunk];auto rr=reader_.read(reader_.context,chunk,sizeof(chunk));
  if(rr.status==ds_preview::ReadStatus::Retry){if(rr.bytes)fail(Fault::Reader);return;}
  if(rr.status==ds_preview::ReadStatus::Error||rr.bytes>sizeof(chunk)||rr.bytes>reader_.bytes-used_){fail(Fault::Reader);return;}
  for(size_t i=0;i<rr.bytes;++i){unsigned char c=chunk[i];if(!(c==9||c==10||c==13||(c>=32&&c<=126))){fail(Fault::Capability);return;}}
  if(rr.bytes)memcpy(source_+used_,chunk,rr.bytes);used_+=rr.bytes;
  if(rr.status==ds_preview::ReadStatus::Eof){
   if(used_!=reader_.bytes){fail(Fault::Reader);return;}source_[used_]=0;
   memory_={source_,used_,0};if(!compiler_.start(program_,memory_.reader(),"stage28t.duck")){fail(Fault::Compiler);return;}state_=State::Compiling;
  }else if(!rr.bytes)fail(Fault::Reader);
  return;
 }
 if(state_==State::Compiling){compiler_.step();if(compiler_.state()==ds_preview::CompileState::Error){fail(Fault::Compiler);return;}
  if(compiler_.state()==ds_preview::CompileState::Complete){if(program_.ownershipCommands())fail(Fault::Capability);else state_=State::Ready;}return;
 }
 if(state_==State::Syncing||state_==State::Clearing){
  if(turns_++>=ClearingTurns||uint32_t(now-since_)>=ClearingMs){if(fault_==Fault::None)fault_=Fault::Clearing;state_=State::Quarantined;return;}
  route_b::drive(session_);
  if(backend_b::fatal()&&state_==State::Syncing){fail(Fault::Backend);return;}
  if(cancelRequested_){cancelRequested_=false;finish(State::Cancelled);return;}
  if(!route_b::clearing(session_)){
   if(state_==State::Syncing){if(route_b::result(session_).kind!=route_b::ResultKind::None){fail(Fault::Ownership);return;}if(!route_b::environment()){fail(Fault::Environment);return;}
    if(!runtime_.start(program_,sink,this,now)){fail(Fault::Compiler);return;}state_=State::Running;
   }else if(route_b::detach(session_)){leased_=false;state_=target_;}
  }return;
 }
 if(state_!=State::Running)return;
 if(!route_b::environment()){fail(Fault::Environment);return;}
 if(pending_&&(turns_++>=PendingTurns||uint32_t(now-since_)>=PendingMs)){fail(Fault::Deadline);return;}
 route_b::drive(session_);
 if(cancelRequested_){cancelRequested_=false;finish(State::Cancelled);return;}
 // The source tick is separate from scheduler work, but each call is finite native work.
 runtime_.tick(now);
 if(state_!=State::Running)return;
 if(runtime_.state()==ds_preview::State::Completed)finish(State::Completed);
 else if(runtime_.state()==ds_preview::State::Error)fail(Fault::Runtime);
 else if(runtime_.state()==ds_preview::State::Cancelled)finish(State::Cancelled);
}
}
