#include "journal_driver.h"
#include <limits>
namespace stage28m {
using ds_preview::Accept;namespace b=ds_bridge;namespace k=ds_keyboard;
constexpr uint64_t Last=std::numeric_limits<uint64_t>::max();
Driver::Driver(Counters initial,uint64_t C,uint64_t Q):decision_(transportDecision),context_(nullptr),transport_(C,Q),ids_(initial){}
Accept Driver::transportDecision(void*,Driver& d,const Record& r){
 Accept a=d.transport_.poll(r.session,r.intent,r.report,r.snapshot);
 if(d.cancelRequested_)return Accept::Retry;return a;
}
Driver::~Driver(){compile_.cancel();bridge_.cancel();} // never emits a report
bool Driver::reject(Rejection r){rejection_=r;if(rejections_!=UINT32_MAX)++rejections_;return false;}
void Driver::terminal(){
 if(current_!=NoRecord&&records_[current_].receipt==Receipt::Pending)records_[current_].receipt=Receipt::Abandoned;
 current_=NoRecord;
 if(activeIntent_!=IntentCapacity&&intents_[activeIntent_].state==IntentState::Admitted)intents_[activeIntent_].state=IntentState::Cancelled;
 activeIntent_=IntentCapacity;
 for(size_t n=0;n<requestEvidenceCount_;++n)if(requestEvidence_[n].disposition==Disposition::Admitted||requestEvidence_[n].disposition==Disposition::Executing)requestEvidence_[n].disposition=Disposition::Cancelled;
 activeRequest_=RequestEvidenceCapacity;transport_.abandon();requestCount_=0;requestHead_=0;cancelRequested_=false;
 bridge_.cancel();state_=State::TerminalUndrained;uncertain_=true;
}
void Driver::fault(Fault f){
 if(diagnostic_.fault==Fault::None){diagnostic_.fault=f;diagnostic_.session=session_;diagnostic_.intent=activeIntent_==IntentCapacity?0:intents_[activeIntent_].intent;diagnostic_.report=current_==NoRecord?0:records_[current_].report;diagnostic_.bridge=bridge_.error();}
 uncertain_=true;terminal();
}
bool Driver::compileStart(ds_preview::Reader reader,const char* location){
 if(stepping_||!(state_==State::Idle||state_==State::Drained))return reject(Rejection::Busy);
 return compile_.start(program_,reader,location);
}
bool Driver::compileMemory(const char* text,size_t bytes,const char* location){
 if(stepping_||!(state_==State::Idle||state_==State::Drained)||compile_.state()==ds_preview::CompileState::Compiling)return reject(Rejection::Busy);
 reader_={text,bytes,0};return compileStart(reader_.reader(),location);
}
void Driver::compileStep(){if(!stepping_)compile_.step();}
void Driver::compileCancel(){if(!stepping_)compile_.cancel();}
bool Driver::begin(uint32_t now,uint32_t attempts,uint32_t elapsed){
 if(stepping_||compile_.state()==ds_preview::CompileState::Compiling)return reject(Rejection::Busy);
 if(!(state_==State::Idle||state_==State::Drained))return reject(Rejection::Undrained);
 if(transport_.unresolved()||!transport_.acquireLease())return reject(Rejection::NotReady);
 if(ids_.session==Last){fault(Fault::SessionExhaustion);return false;}
 // Consume a unique identity even if the underlying begin rejects; never reuse it.
 session_=++ids_.session;
 if(!bridge_.begin(sink,this,now,attempts,elapsed))return reject(Rejection::NotReady);
 state_=State::Syncing;now_=now;drainReport_=0;uncertain_=false;return true;
}
bool Driver::start(uint32_t now){
 if(stepping_||state_!=State::Prepared)return reject(Rejection::Busy);
 if(requestCount_||activeRequest_!=RequestEvidenceCapacity||bridge_.planner().state()!=k::State::Ready||transport_.unresolved()||!transport_.valid())return reject(Rejection::NotReady);
 if(!program_.ready())return reject(Rejection::NotReady);
 if(!bridge_.start(program_,now))return reject(Rejection::NotReady);
 state_=State::Running;runAt_=now;return true;
}
bool Driver::applySetup(const Request& r){
 if(state_!=State::Prepared||r.owner>=b::ScriptOwner)return reject(Rejection::SetupOnly);
 bool ok=r.acquire?bridge_.hold(r.owner,r.usage,now_):bridge_.release(r.owner,r.usage,now_);
 return ok?true:reject(Rejection::InvalidRequest);
}
bool Driver::hold(size_t owner,uint16_t usage,uint32_t now){
 if(stepping_)return reject(Rejection::Busy);
 if(owner>=b::ScriptOwner||state_!=State::Prepared)return reject(Rejection::SetupOnly);
 now_=now;return applySetup({usage,static_cast<uint8_t>(owner),true});
}
bool Driver::release(size_t owner,uint16_t usage,uint32_t now){
 if(stepping_)return reject(Rejection::Busy);
 if(owner>=b::ScriptOwner||state_!=State::Prepared)return reject(Rejection::SetupOnly);
 now_=now;return applySetup({usage,static_cast<uint8_t>(owner),false});
}
bool Driver::enqueue(const Request& r){
 if(r.owner>=b::ScriptOwner||!k::Planner::validUsage(r.usage))return reject(Rejection::InvalidRequest);
 if(state_!=State::Prepared)return reject(Rejection::SetupOnly);
 if(requestCount_==RequestCapacity)return reject(Rejection::QueueFull);
 if(requestEvidenceCount_==RequestEvidenceCapacity)return reject(Rejection::QueueFull);
 size_t slot=(requestHead_+requestCount_)%RequestCapacity;requests_[slot]=r;requestIndexes_[slot]=requestEvidenceCount_;requestEvidence_[requestEvidenceCount_++]={r,Disposition::Admitted};++requestCount_;return true;
}
void Driver::requestCancel(){cancelRequested_=true;}
bool Driver::drain(uint32_t now){
 if(stepping_||state_!=State::TerminalUndrained)return reject(Rejection::Busy);
 if(transport_.unresolved()||!transport_.valid()||transport_.fault()!=TransportFault::None)return reject(Rejection::NotReady);
 if(!bridge_.drain(now))return reject(Rejection::NotReady);
 current_=NoRecord;drainReport_=0;state_=State::DrainPending;return true;
}
bool Driver::reserveIntent()const{return ids_.intent!=Last&&intentsCount_<IntentCapacity;}
bool Driver::prepareReport(){
 const auto& p=bridge_.planner();
 if(current_!=NoRecord){const Record& r=records_[current_];if(r.phase!=p.phase()||!k::Planner::equal(r.snapshot,p.pending())){fault(Fault::Protocol);return false;}return true;}
 if(recordsCount_==ReportCapacity){fault(Fault::JournalFull);return false;}
 if(ids_.report==Last){fault(Fault::ReportExhaustion);return false;}
 current_=recordsCount_++;Record& r=records_[current_];r.session=session_;r.report=++ids_.report;r.phase=p.phase();r.snapshot=p.pending();
 if(state_==State::Running){
  if(activeIntent_==IntentCapacity){fault(Fault::Protocol);return false;}
  r.intent=intents_[activeIntent_].intent;
 }
 if(state_==State::DrainPending)drainReport_=r.report;
 return true;
}
Accept Driver::sink(void* pointer,const k::Report& report){
 auto& d=*static_cast<Driver*>(pointer);
 if(!d.stepping_||d.insideDecision_||d.current_==NoRecord)return Accept::Failed;
 Record& r=d.records_[d.current_];
 if(r.receipt!=Receipt::Pending||!k::Planner::equal(r.snapshot,report)){d.fault(Fault::Protocol);return Accept::Failed;}
 ++r.attempts;++d.attempts_;++d.work_.reportAttempts;d.insideDecision_=true;Accept answer=Accept::Failed;
 try{answer=d.decision_?d.decision_(d.context_,d,r):Accept::Accepted;}catch(...){answer=Accept::Failed;}
 d.insideDecision_=false;r.last=answer;
 if(answer==Accept::Accepted){
  // The sole acceptance point: one immutable copy for this current R.
  r.acceptedSnapshot=report;r.receipt=Receipt::Accepted;r.acceptedAt=d.now_;++d.accepted_;
  if(r.intent&&d.activeIntent_!=IntentCapacity)++d.intents_[d.activeIntent_].reportsAccepted;
  d.current_=NoRecord;
 }else if(answer!=Accept::Retry){r.receipt=Receipt::Rejected;}
 return answer;
}
void Driver::observe(uint32_t admitted,uint32_t acked,uint32_t delayed){
 uint32_t a=bridge_.admissions()-admitted,kacks=bridge_.keyboardAcks()-acked,delay=bridge_.delayAcks()-delayed;
 if(a>1||kacks>1||delay>1||a+delay>1||(a&&kacks)||(delay&&kacks)){fault(Fault::Protocol);return;}
 // Identity association is through authoritative counter deltas, never byte equality.
 if(a||delay){
  if(activeIntent_!=IntentCapacity||!reserveIntent()){fault(Fault::Protocol);return;}
  activeIntent_=intentsCount_++;IntentRecord& i=intents_[activeIntent_];i.session=session_;i.intent=++ids_.intent;i.admittedAt=now_;i.kind=delay?Kind::Delay:Kind::Keyboard;
 }
 if(kacks||delay){
  if(activeIntent_==IntentCapacity){fault(Fault::Protocol);return;}
  IntentRecord& i=intents_[activeIntent_];
  if(i.acknowledgements||i.state!=IntentState::Admitted||(!delay&&bridge_.intent()!=b::Intent::None)){fault(Fault::Protocol);return;}
  i.acknowledgements=1;i.acknowledgedAt=bridge_.lastAckAt();i.state=IntentState::Acknowledged;++acknowledged_;if(delay)++delayAcks_;activeIntent_=IntentCapacity;
 }
 if(bridge_.state()==b::State::Prepared)state_=State::Prepared;
 if(bridge_.state()==b::State::Failing||bridge_.state()==b::State::Error){fault(bridge_.error().reason==b::Reason::RuntimeFailure?Fault::Runtime:Fault::Planner);return;}
 if(state_==State::DrainPending&&bridge_.state()!=b::State::Draining){
  bool receipt=false;for(size_t n=0;n<recordsCount_;++n){const auto& r=records_[n];if(r.session==session_&&r.report==drainReport_&&r.phase==k::Phase::Drain&&r.receipt==Receipt::Accepted&&k::Planner::neutral(r.acceptedSnapshot))receipt=true;}
  if(!receipt){fault(Fault::Protocol);return;}uncertain_=false;state_=State::Drained;return;
 }
 if(state_==State::Running&&(bridge_.state()==b::State::Completed||bridge_.state()==b::State::Cancelled))terminal();
}
void Driver::step(uint32_t now){
 if(stepping_){reject(Rejection::Busy);return;}
 stepping_=true;work_={};now_=now;
 if(transport_.overflow()||!transport_.valid()){if(state_!=State::Idle&&state_!=State::Drained)fault(Fault::Protocol);}
 if(cancelRequested_)terminal();
 transport_.processOne();
 if(transport_.fault()!=TransportFault::None&&state_!=State::Idle&&state_!=State::Drained)fault(Fault::Protocol);
 resolveSetup();
 if(cancelRequested_){terminal();stepping_=false;return;}
 if(state_==State::Idle||state_==State::TerminalUndrained||state_==State::Drained){stepping_=false;return;}
 if(requestCount_&&activeRequest_==RequestEvidenceCapacity&&state_==State::Prepared&&bridge_.planner().state()==k::State::Ready){Request r=requests_[requestHead_];activeRequest_=requestIndexes_[requestHead_];requestHead_=(requestHead_+1)%RequestCapacity;--requestCount_;++work_.requests;requestEvidence_[activeRequest_].disposition=Disposition::Executing;
 if(!applySetup(r)){requestEvidence_[activeRequest_].disposition=Disposition::Rejected;activeRequest_=RequestEvidenceCapacity;}else resolveSetup();}
 bool reportWork=bridge_.planner().state()==k::State::Working;
 bool deadline=state_==State::Running&&uint32_t(now-runAt_)>=ds_preview::MaxElapsedMs;
 if(reportWork&&!deadline&&!prepareReport()){stepping_=false;return;}
 // A conservative guard before any unacknowledged source tick reserves capacity for
 // a potential E, including Delay (which is accepted within that tick). No guessed
 // statement/source event inspection and no identity committed for a non-event tick.
 if(state_==State::Running&&!deadline&&!reportWork&&bridge_.intent()==b::Intent::None&&!reserveIntent()){
  fault(ids_.intent==Last?Fault::IntentExhaustion:Fault::IntentFull);stepping_=false;return;
 }
 uint32_t a=bridge_.admissions(),ack=bridge_.keyboardAcks(),delay=bridge_.delayAcks();
 if(state_==State::Running&&(!reportWork||deadline))++work_.runtimeTicks;
 bridge_.step(now);
 if(deferredFault_!=Fault::None){Fault f=deferredFault_;deferredFault_=Fault::None;fault(f);stepping_=false;return;}
 if(cancelRequested_){terminal();stepping_=false;return;}
 observe(a,ack,delay);resolveSetup();stepping_=false;
}
void Driver::resolveSetup(){if(activeRequest_!=RequestEvidenceCapacity&&bridge_.planner().state()==k::State::Ready&&!transport_.unresolved()){requestEvidence_[activeRequest_].disposition=Disposition::Executed;activeRequest_=RequestEvidenceCapacity;}}
bool Driver::completionNotice(uint64_t session,uint64_t report){
 // Deliberately incapable of fabricating a receipt: D02 selects journal acceptance.
 (void)session;(void)report;if(notices_!=UINT32_MAX)++notices_;return false;
}
void Driver::mockDisconnect(bool ambiguous){
 transport_.loss();
 if(stepping_){if(deferredFault_==Fault::None)deferredFault_=ambiguous?Fault::Ambiguous:Fault::Disconnected;return;}fault(ambiguous?Fault::Ambiguous:Fault::Disconnected);
}
}
