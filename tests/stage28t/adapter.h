#pragma once
#include "core.h"
#include "scheduler_seam.h"
namespace native_b {
enum class State { Idle, Loading, Compiling, Ready, Syncing, Running, Clearing, Completed, Cancelled, Error, Quarantined };
enum class Fault { None, Busy, Reader, Compiler, Runtime, Capability, Ownership, Environment, Admission, Result, Backend, Deadline, Clearing };
class Adapter {
 ds_preview::Program program_;ds_preview::CompileSession compiler_;ds_preview::Runtime runtime_;
 char source_[ds_preview::MaxSource+1]{};ds_preview::MemoryReader memory_{};ds_preview::Reader reader_{};
 size_t used_=0;State state_=State::Idle,target_=State::Completed;Fault fault_=Fault::None;
 bool cancelRequested_=false,inStep_=false,pending_=false,leased_=false;uint64_t session_=0;
 route_b::Id id_{};ds_preview::Event event_{ds_preview::EventType::Delay,0};
 uint32_t now_=0,since_=0,turns_=0,loadTurns_=0;uint32_t admissions_=0,acks_=0,retries_=0,delayAcks_=0;
 static ds_preview::Accept sink(void*,const ds_preview::Event&);
 ds_preview::Accept receive(const ds_preview::Event&);
 void fail(Fault);void finish(State);
 public:
 static constexpr uint32_t PendingTurns=1000,PendingMs=1000,ClearingTurns=1000,ClearingMs=1000;
 bool prepare(ds_preview::Reader);
 bool prepare(const char*,size_t); // MemoryReader is owned, bytes copied cooperatively before compile
 bool start(uint32_t now);
 void step(uint32_t now);
 void cancel();
 // Bounded copied result entrance, used for stale/wrong/duplicate fault injection.
 // Real seam is polled; this API never manufactures a successful result.
 bool inspect(route_b::Result);
 State state()const{return state_;}Fault fault()const{return fault_;}
 bool leased()const{return leased_;}uint64_t session()const{return session_;}
 route_b::Id operation()const{return id_;}
 const ds_preview::Runtime& runtime()const{return runtime_;}
 uint32_t admissions()const{return admissions_;}uint32_t acks()const{return acks_;}
 uint32_t retries()const{return retries_;}uint32_t delayAcks()const{return delayAcks_;}
};
}
