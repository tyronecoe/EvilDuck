#pragma once
// Test-only transport. Tags, lease and fences are injected model evidence, NOT SDK APIs.
#include "../../language_preview/keyboard.h"
#include <stdint.h>
namespace stage28m {
constexpr size_t ObservationCapacity=4, TransferCapacity=1024, NoticeCapacity=1024, PlanCapacity=16;
enum class Outcome:uint8_t {NotSubmitted,Submitted,Ambiguous};
enum class TransportFault:uint8_t {None,Identity,Shape,Contradiction,Transfer,Ambiguous,Overflow,Tokenless,Lost,Exhaustion,Capacity};
enum class NoticeKind:uint8_t {Success,Failure,Retired};
struct Binding {uint8_t instance=0,endpoint=0x81,protocol=1,reportId=1;}; // fixture binding, NOT discovered real endpoint
struct Identity {uint64_t C=0,Q=0,S=0,E=0,R=0;};
struct Wire {uint8_t bytes[9]={};uint8_t length=0;};
struct Notice {Identity id{};Binding binding{};Wire wire{};NoticeKind kind=NoticeKind::Success;bool tagged=true;};
struct Plan {Outcome outcome=Outcome::Submitted;bool earlySuccess=true,earlyRetired=true;};
struct Transfer {
 Identity id{};Binding binding{};Wire wire{};Outcome outcome=Outcome::Submitted;
 uint32_t polls=0,successOrder=0,retirementOrder=0,acceptanceOrder=0;
 bool success=false,retired=false,accepted=false,cancelled=false,fenced=false;
};
struct NoticeEvidence {Notice notice{};uint8_t classification=0;}; // 1 current, 2 duplicate/stale, 3 invalid
class Transport {
 Transfer transfers_[TransferCapacity]{};Notice observations_[ObservationCapacity]{};
 NoticeEvidence notices_[NoticeCapacity]{};Plan plans_[PlanCapacity]{};
 size_t count_=0,slot_=TransferCapacity,head_=0,queued_=0,noticeCount_=0,planHead_=0,planCount_=0;
 uint64_t C_=0,Q_=0;Binding binding_{};Plan defaultPlan_{};
 TransportFault fault_=TransportFault::None;uint32_t submits_=0,submitted_=0,order_=0,duplicates_=0;
 uint32_t roleRejections_=0;bool submitting_=false;
 bool lease_=false,valid_=true,foreign_=false,observerQuiescent_=false,overflow_=false;
 void fail(TransportFault);
 void clearRetiredCancelled();
public:
 using DuringSubmit=void(*)(void*);DuringSubmit duringSubmit=nullptr;void* hookContext=nullptr;
 explicit Transport(uint64_t C=0,uint64_t Q=0):C_(C),Q_(Q){}
 bool acquireLease();void foreignProducer(bool value){foreign_=value;}
 bool plan(Plan);void defaultPlan(Plan p){defaultPlan_=p;}
 ds_preview::Accept poll(uint64_t S,uint64_t E,uint64_t R,const ds_keyboard::Report&);
 bool publish(const Notice&); // callback role: copy or sticky overflow only; no Bridge mutation
 void processOne(); // owner role only
 Notice notice(NoticeKind kind)const;
 void abandon();void loss();bool fence(uint64_t C);bool rebind(Binding);
 bool canReclaim()const{return observerQuiescent_&&slot_==TransferCapacity&&queued_==0;}
 bool unresolved()const{return slot_!=TransferCapacity;}
 bool valid()const{return valid_&&lease_&&!foreign_;}
 bool overflow()const{return overflow_;}
 TransportFault fault()const{return fault_;}
 uint64_t epoch()const{return C_;}uint64_t submission()const{return Q_;}
 uint32_t calls()const{return submits_;}uint32_t submissions()const{return submitted_;}
 uint32_t roleRejections()const{return roleRejections_;}
 uint32_t duplicates()const{return duplicates_;}
 size_t transferCount()const{return count_;}size_t noticeCount()const{return noticeCount_;}
 size_t queued()const{return queued_;}
 const Transfer* transfer(size_t i)const{return i<count_?&transfers_[i]:nullptr;}
 const Transfer* current()const{return slot_!=TransferCapacity?&transfers_[slot_]:nullptr;}
 const NoticeEvidence* evidence(size_t i)const{return i<noticeCount_?&notices_[i]:nullptr;}
};
}
