#pragma once
// Memory-only synthetic harness. No firmware adapter or USB/OS endpoint.
#include "../../language_preview/bridge.h"
#include <stdint.h>
#include "synthetic_transport.h"
namespace stage28m {
constexpr size_t ReportCapacity=256, IntentCapacity=128, RequestCapacity=8;
constexpr size_t NoRecord=ReportCapacity;
enum class State:uint8_t {Idle,Syncing,Prepared,Running,TerminalUndrained,DrainPending,Drained};
enum class Receipt:uint8_t {Pending,Accepted,Rejected,Abandoned};
enum class IntentState:uint8_t {Admitted,Acknowledged,Cancelled};
enum class Kind:uint8_t {Keyboard,Delay};
enum class Fault:uint8_t {None,JournalFull,IntentFull,SessionExhaustion,IntentExhaustion,ReportExhaustion,Protocol,Planner,Runtime,Disconnected,Ambiguous};
enum class Rejection:uint8_t {None,Busy,QueueFull,SetupOnly,Undrained,NotReady,InvalidRequest};
struct Counters {uint64_t session=0,intent=0,report=0;};
struct Record {
 uint64_t session=0,intent=0,report=0;
 ds_keyboard::Report snapshot{},acceptedSnapshot{};
 uint32_t attempts=0,acceptedAt=0;
 ds_keyboard::Phase phase=ds_keyboard::Phase::None;
 Receipt receipt=Receipt::Pending;ds_preview::Accept last=ds_preview::Accept::Retry;
};
struct IntentRecord {
 uint64_t session=0,intent=0;
 uint32_t admittedAt=0,acknowledgedAt=0,reportsAccepted=0,acknowledgements=0;
 Kind kind=Kind::Keyboard;IntentState state=IntentState::Admitted;
};
struct Request {uint16_t usage=0;uint8_t owner=0;bool acquire=true;};
struct Diagnostic {
 Fault fault=Fault::None;uint64_t session=0,intent=0,report=0;
 ds_bridge::Diagnostic bridge{};
};
struct Work {uint8_t reportAttempts=0,runtimeTicks=0,requests=0;};
enum class Disposition:uint8_t {Admitted,Executing,Executed,Rejected,Cancelled};
constexpr size_t RequestEvidenceCapacity=128;
struct RequestEvidence {Request request{};Disposition disposition=Disposition::Admitted;};
class Driver {
public:
 // Derived from unchanged Stage28K; synthetic tagged completion + retirement only.
 using Decision=ds_preview::Accept(*)(void*,Driver&,const Record&);
private:
 ds_preview::Program program_;
 ds_preview::CompileSession compile_;
 ds_preview::MemoryReader reader_{};
 ds_bridge::Bridge bridge_;
 Record records_[ReportCapacity]{};IntentRecord intents_[IntentCapacity]{};
 Request requests_[RequestCapacity]{};
 Decision decision_=nullptr;void* context_=nullptr;
 Transport transport_;RequestEvidence requestEvidence_[RequestEvidenceCapacity]{};
 size_t requestEvidenceCount_=0,activeRequest_=RequestEvidenceCapacity;
 size_t requestIndexes_[RequestCapacity]{};
 Counters ids_{};Diagnostic diagnostic_{};State state_=State::Idle;
 Rejection rejection_=Rejection::None;Work work_{};
 size_t recordsCount_=0,intentsCount_=0,current_=NoRecord,activeIntent_=IntentCapacity;
 size_t requestHead_=0,requestCount_=0;
 uint64_t session_=0,drainReport_=0;uint32_t now_=0,runAt_=0,attempts_=0,accepted_=0,acknowledged_=0,delayAcks_=0,rejections_=0,notices_=0;
 Fault deferredFault_=Fault::None;
 static ds_preview::Accept transportDecision(void*,Driver&,const Record&);
 void resolveSetup();
 bool stepping_=false,insideDecision_=false,cancelRequested_=false,uncertain_=false;
 static ds_preview::Accept sink(void*,const ds_keyboard::Report&);
 bool reject(Rejection);
 void fault(Fault);
 void terminal();
 bool prepareReport();
 bool applySetup(const Request&);
 bool reserveIntent()const;
 void observe(uint32_t,uint32_t,uint32_t);
public:
 explicit Driver(Counters initial={},uint64_t C=0,uint64_t Q=0);
 Driver(const Driver&)=delete;Driver& operator=(const Driver&)=delete;
 ~Driver();
 bool compileStart(ds_preview::Reader,const char* location="stage28k.synthetic");
 bool compileMemory(const char*,size_t,const char* location="stage28k.synthetic");
 void compileStep();void compileCancel();
 bool begin(uint32_t now=0,uint32_t attempts=ds_keyboard::MaxAttempts,uint32_t elapsed=ds_keyboard::MaxElapsed);
 bool start(uint32_t now=0);
 bool hold(size_t owner,uint16_t usage,uint32_t now=0);
 bool release(size_t owner,uint16_t usage,uint32_t now=0);
 bool enqueue(const Request&);
 void requestCancel(); // priority bit, cannot be lost to ordinary queue saturation
 bool drain(uint32_t now=0);
 void step(uint32_t now);
 bool completionNotice(uint64_t session,uint64_t report); // diagnostics only; never an acceptance
 void mockDisconnect(bool ambiguous=false);
 State state()const{return state_;}
 const Diagnostic& diagnostic()const{return diagnostic_;}
 Rejection rejection()const{return rejection_;}
 const Work& work()const{return work_;}
 const Counters& counters()const{return ids_;}
 uint64_t session()const{return session_;}
 uint64_t drainReport()const{return drainReport_;}
 size_t recordCount()const{return recordsCount_;}
 size_t intentCount()const{return intentsCount_;}
 size_t queuedRequests()const{return requestCount_;}
 uint32_t attempts()const{return attempts_;}
 uint32_t accepted()const{return accepted_;}
 uint32_t acknowledgements()const{return acknowledged_;}
 uint32_t delayAcknowledgements()const{return delayAcks_;}
 uint32_t rejections()const{return rejections_;}
 uint32_t notices()const{return notices_;}
 bool uncertain()const{return uncertain_;}
 const Record* record(size_t n)const{return n<recordsCount_?&records_[n]:nullptr;}
 const IntentRecord* intent(size_t n)const{return n<intentsCount_?&intents_[n]:nullptr;}
 Transport& transport(){return transport_;}
 const Transport& transport()const{return transport_;}
 size_t requestEvidenceCount()const{return requestEvidenceCount_;}
 const RequestEvidence* requestEvidence(size_t i)const{return i<requestEvidenceCount_?&requestEvidence_[i]:nullptr;}
 bool canReclaim()const{return transport_.canReclaim()&&compile_.state()!=ds_preview::CompileState::Compiling&&(state_==State::Idle||state_==State::TerminalUndrained||state_==State::Drained);}
 const ds_preview::Program& program()const{return program_;}
 const ds_preview::CompileSession& compiler()const{return compile_;}
 const ds_bridge::Bridge& bridge()const{return bridge_;}
};
}
