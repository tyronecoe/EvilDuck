#include "synthetic_transport.h"
#include <cstring>
namespace stage28m {
using ds_preview::Accept;
static bool equal(Identity a,Identity b){return a.C==b.C&&a.Q==b.Q&&a.S==b.S&&a.E==b.E&&a.R==b.R;}
static bool equal(Binding a,Binding b){return a.instance==b.instance&&a.endpoint==b.endpoint&&a.protocol==b.protocol&&a.reportId==b.reportId;}
static bool equal(Wire a,Wire b){return a.length==b.length&&a.length<=9&&!std::memcmp(a.bytes,b.bytes,a.length);}
void Transport::fail(TransportFault f){if(fault_==TransportFault::None)fault_=f;}
bool Transport::acquireLease(){
 if(submitting_){++roleRejections_;return false;}
 if(foreign_||unresolved()||!valid_||fault_!=TransportFault::None)return false;
 if(!lease_){if(C_==UINT64_MAX){fail(TransportFault::Exhaustion);return false;}++C_;lease_=true;observerQuiescent_=false;}return true;
}
bool Transport::plan(Plan p){if(planCount_==PlanCapacity)return false;plans_[(planHead_+planCount_)%PlanCapacity]=p;++planCount_;return true;}
Notice Transport::notice(NoticeKind kind)const{
 Notice n;n.kind=kind;if(current()){n.id=current()->id;n.binding=current()->binding;n.wire=current()->wire;}return n;
}
bool Transport::publish(const Notice& n){
 if(queued_==ObservationCapacity){overflow_=true;return false;}
 observations_[(head_+queued_)%ObservationCapacity]=n;++queued_;return true;
}
void Transport::clearRetiredCancelled(){if(current()&&current()->retired&&current()->cancelled)slot_=TransferCapacity;}
void Transport::processOne(){
 if(submitting_){++roleRejections_;return;}
 if(overflow_)fail(TransportFault::Overflow);
 if(!queued_)return;
 Notice n=observations_[head_];head_=(head_+1)%ObservationCapacity;--queued_;
 if(noticeCount_==NoticeCapacity){fail(TransportFault::Capacity);return;}
 auto& evidence=notices_[noticeCount_++];evidence.notice=n;evidence.classification=3;
 if(!n.tagged){fail(TransportFault::Tokenless);return;}
 size_t index=0;while(index<count_&&!(transfers_[index].id.C==n.id.C&&transfers_[index].id.Q==n.id.Q))++index;
 if(index==count_){fail(TransportFault::Identity);return;}
 auto& t=transfers_[index];
 if(!equal(t.id,n.id)){fail(TransportFault::Identity);return;}
 if(!equal(t.binding,n.binding)||!equal(t.wire,n.wire)){fail(TransportFault::Shape);return;}
 if(t.outcome==Outcome::NotSubmitted){fail(TransportFault::Contradiction);return;}
 // Known genuinely retired old identities may be ignored; current slot/bytes never mint a Q.
 if(index!=slot_){if(t.retired){evidence.classification=2;++duplicates_;return;}fail(TransportFault::Identity);return;}
 evidence.classification=1;++order_;
 if(n.kind==NoticeKind::Success){if(t.success){++duplicates_;evidence.classification=2;}else{t.success=true;t.successOrder=order_;}}
 else if(n.kind==NoticeKind::Retired){if(t.retired){++duplicates_;evidence.classification=2;}else{t.retired=true;t.retirementOrder=order_;}}
 else fail(TransportFault::Transfer);
 clearRetiredCancelled();
}
Accept Transport::poll(uint64_t S,uint64_t E,uint64_t R,const ds_keyboard::Report& report){
 if(submitting_){++roleRejections_;return Accept::Failed;}
 if(!valid()||fault_!=TransportFault::None)return Accept::Failed;
 if(current()){
  auto& t=transfers_[slot_];++t.polls;
  Wire wire;wire.length=binding_.reportId?9:8;unsigned offset=binding_.reportId?1:0;if(offset)wire.bytes[0]=binding_.reportId;std::memcpy(wire.bytes+offset,report.bytes,8);
  if(t.id.S!=S||t.id.E!=E||t.id.R!=R||!equal(t.wire,wire)||t.cancelled){fail(TransportFault::Identity);return Accept::Failed;}
  if(t.success&&t.retired){t.accepted=true;t.acceptanceOrder=++order_;slot_=TransferCapacity;return Accept::Accepted;}
  return Accept::Retry;
 }
 if(Q_==UINT64_MAX){fail(TransportFault::Exhaustion);return Accept::Failed;}
 if(count_==TransferCapacity){fail(TransportFault::Capacity);return Accept::Failed;}
 slot_=count_++;auto& t=transfers_[slot_];t.id={C_,++Q_,S,E,R};t.binding=binding_;t.polls=1;
 t.wire.length=binding_.reportId?9:8;unsigned offset=binding_.reportId?1:0;if(offset)t.wire.bytes[0]=binding_.reportId;std::memcpy(t.wire.bytes+offset,report.bytes,8);
 Plan p=defaultPlan_;if(planCount_){p=plans_[planHead_];planHead_=(planHead_+1)%PlanCapacity;--planCount_;}
 // Mock identity/outcome published before callback. Actual SDK does NOT expose this API.
 t.outcome=p.outcome;++submits_;if(p.outcome==Outcome::Submitted)++submitted_;
 if(p.earlySuccess)publish(notice(NoticeKind::Success));if(p.earlyRetired)publish(notice(NoticeKind::Retired));
 submitting_=true;struct Guard{bool& flag;~Guard(){flag=false;}} guard{submitting_};
 if(duringSubmit)duringSubmit(hookContext);
 if(p.outcome==Outcome::NotSubmitted){t.retired=true;t.retirementOrder=++order_;slot_=TransferCapacity;}
 else if(p.outcome==Outcome::Ambiguous){fail(TransportFault::Ambiguous);}
 return fault_==TransportFault::None?Accept::Retry:Accept::Failed;
}
void Transport::abandon(){if(current()){transfers_[slot_].cancelled=true;clearRetiredCancelled();}}
void Transport::loss(){valid_=false;fail(TransportFault::Lost);abandon();}
bool Transport::fence(uint64_t C){
 if(submitting_){++roleRejections_;return false;}
 if(C!=C_)return false;if(current()){auto& t=transfers_[slot_];t.retired=true;t.cancelled=true;t.fenced=true;t.retirementOrder=++order_;slot_=TransferCapacity;}
 // A fixture-supplied transfer + observer certificate, NOT inferred from empty queue/mount.
 head_=queued_=0;observerQuiescent_=true;valid_=false;return true;
}
bool Transport::rebind(Binding b){
 if(submitting_){++roleRejections_;return false;}
 if(!observerQuiescent_||unresolved()||queued_||C_==UINT64_MAX||foreign_||b.instance!=0||(b.protocol!=0&&b.protocol!=1)||b.endpoint!=0x81||b.reportId>1){return false;}
 ++C_;binding_=b;valid_=true;lease_=true;observerQuiescent_=false;overflow_=false;fault_=TransportFault::None;return true;
}
}
