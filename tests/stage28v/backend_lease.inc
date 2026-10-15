// Source-local access to actual Owned/clearing/loss state. Native-only opt-in.
namespace {
struct BackendLease {
 bool active=false,quarantined=false,inIo=false,closing=false,legacyDirty=false;
 uint64_t session=0,operation=0,sequence=0,clearRequest=0,clearSubmitted=0,cleanupFloor=0;
 uint32_t denied=0;u_platform::Task owner{};
 backend_b::Observation last{},first{};
} lease;
struct Permission {uint64_t session=0,operation=0;bool active=false;};
static Permission permission;
bool backendAllowed(){
 if(!lease.active)return true;
 const bool yes=permission.active&&permission.session==lease.session&&permission.operation==lease.operation&&lease.owner==u_platform::current()&&!lease.inIo;
 if(!yes&&lease.denied!=UINT32_MAX)++lease.denied;
 return yes;
}
void backendObserve(backend_b::Kind k,bool called=false,bool returned=false,bool clear=false){
 if(!lease.active||lease.quarantined)return;
 if(lease.sequence==UINT64_MAX){k=backend_b::Kind::Exhausted;}else ++lease.sequence;
 lease.last={lease.session,lease.operation,lease.sequence,k,called,returned,clear};
 if(k==backend_b::Kind::CalledFalse||k==backend_b::Kind::Loss||k==backend_b::Kind::Exhausted){lease.quarantined=true;lease.first=lease.last;}
}
bool backendClearRequest(){
 if(!lease.active)return true;
 if(lease.quarantined)return false;
 if(lease.clearRequest==UINT64_MAX){backendObserve(backend_b::Kind::Exhausted);return false;}
 ++lease.clearRequest;return true;
}
}
namespace backend_b {
bool permitted(){execution::Guard guard;return backendAllowed();}
Status status(){execution::Guard guard;return {lease.active,lease.quarantined,releasePending||lease.quarantined,lease.session,lease.operation,lease.clearRequest,lease.clearSubmitted,lease.last,lease.first,lease.denied};}
bool fatal(){execution::Guard guard;return lease.active&&(lease.quarantined||lease.last.kind==Kind::Invalid);}
Scope::Scope(uint64_t s,uint64_t op){
 execution::Guard guard;
 if(!lease.active||lease.session!=s||lease.operation!=op||permission.active||lease.inIo||lease.owner!=u_platform::current())return;
 permission={s,lease.operation,true};entered_=true;u_platform::permission(true);
}
Scope::~Scope(){execution::Guard guard;if(entered_){u_platform::permission(false);permission={};}}
bool available(){execution::Guard guard;
 if(lease.active||permission.active||releasePending||ownershipDirty||owned.modifiers||disconnectEvent.load()||transportLoss||!static_cast<bool>(USB)||lease.quarantined||lease.legacyDirty)return false;for(uint8_t k:owned.keys)if(k)return false;return true;
}
void externalLoss(){execution::Guard guard;if(backendAllowed())backendObserve(Kind::Loss);}
bool acquire(uint64_t s){
 execution::Guard guard;
 if(!s||lease.active||permission.active||releasePending||ownershipDirty||owned.modifiers||disconnectEvent.load()||transportLoss||!static_cast<bool>(USB))return false;
 for(uint8_t k:owned.keys)if(k)return false;
 if(lease.quarantined||lease.legacyDirty)return false;
 lease.active=true;lease.session=s;lease.operation=0;lease.owner=u_platform::current();lease.closing=false;lease.last={};lease.first={};
 // Only a known, unowned validation diagnostic is discarded. Loss/clear/ownership rejected above.
 failure="";return true;
}
bool bind(uint64_t s,uint64_t op){
 execution::Guard guard;
 if(!lease.active||s!=lease.session||lease.owner!=u_platform::current()||permission.active||lease.inIo||lease.quarantined||lease.closing||!op||op<=lease.operation)return false;
 lease.operation=op;lease.last={};return true;
}
bool cleanup(uint64_t s){execution::Guard guard;if(!lease.active||s!=lease.session||lease.owner!=u_platform::current()||permission.active||lease.inIo)return false;if(!lease.closing){lease.closing=true;lease.cleanupFloor=lease.clearRequest;}return true;}
bool release(uint64_t s){
 execution::Guard guard;
 if(!lease.active||s!=lease.session||lease.owner!=u_platform::current()||permission.active||lease.inIo||!lease.closing||lease.quarantined||releasePending||ownershipDirty||lease.clearRequest<=lease.cleanupFloor||lease.clearSubmitted!=lease.clearRequest)return false;
 for(uint8_t k:owned.keys)if(k)return false;if(owned.modifiers)return false;
 lease.active=false;lease.owner={};return true;
}
size_t sharedStorageBytes(){return sizeof(lease);}
size_t perThreadStorageBytes(){return sizeof(permission);}
void exhaustForTest(){execution::Guard guard;if(!lease.active)lease.sequence=UINT64_MAX;}
}
