#pragma once
#include <array>
#include <cstdint>
#include <cstddef>
namespace q {
// Exact bits checked against pinned dwc2_type.h by source receipt checker.
constexpr uint32_t Complete=1,Disabled=2,Nak=64,Empty=128;
struct Ticket {uint64_t c=1,q=1;bool operator==(Ticket b)const{return c==b.c&&q==b.q;}bool operator!=(Ticket b)const{return !(*this==b);}};
struct Premises {
 bool sequence=false,stop_access=false,no_late_status=false,visibility=false;
 bool software_fence=false,exclusive=false,ack_order=false,scope=false;
 bool all()const{return sequence&&stop_access&&no_late_status&&visibility&&software_fence&&exclusive&&ack_order&&scope;}
 static Premises synthetic(){return {true,true,true,true,true,true,true,true};}
};
enum class Fault {None,Cancelled,Missing,Lock,Ownership,Timeout,Loss,Reset,Contradiction,Shared,Exhausted};
enum class Phase {Stop,Acquire,Mask,Fence,NakRequest,NakWait,DisableRequest,DisableWait,FlushRequest,FlushWait,Acknowledge,PublisherFence,Observers,Gate,Retired,Quarantined};
enum class Life {Reset,Unplug,Suspend};
struct Event {Ticket ticket;bool success=true;uint16_t length=9;};
struct Model {
 // Only CPU interface/FIFO/interrupt hierarchy is documentation established.
 // Detailed device register semantics below are explicit conditional hypotheses.
 uint32_t raw=0,mask=Complete|Disabled|Nak|Empty;
 bool cpu_pending=false,isr_active=false,publishing=false,admission=true;
 bool enabled=true,nak=false,nak_request=false,disable_request=false,flush_request=false;
 bool lock_available=true,lock_error=false,owned=true,lost=false,race=false,violation=false,shared=false;
 bool fence_ack=false,visible=false,full_success=false;Life last_lifecycle=Life::Reset;unsigned fifo_words=3,observers=0;
 std::array<Event,4> queue{};size_t queued=0;Ticket current{},publisher{};
 unsigned writes=0,operations=0,published=0,dropped_stale=0,accepted_current=0;
 void assert_status(uint32_t bits){raw|=bits;if(raw&mask)cpu_pending=true;}
 void w1c(uint32_t bits,uint32_t simultaneous=0,bool arrival_after=true);
 void mask_endpoint(){mask=0;writes++;operations++;} // does NOT clear raw/CPU/ISR
 bool enter_isr(Ticket original);bool finish_publish(bool success=true);void consume();
 void nak_ack(){nak=true;assert_status(Nak);}
 void disable_ack(){if(disable_request&&nak){enabled=false;assert_status(Disabled);}}
 void flush_ack(){if(flush_request&&!enabled){fifo_words=0;flush_request=false;}}
 bool producer_fence();
};
struct Sequencer {
 static constexpr unsigned MaxSteps=32;static constexpr uint32_t Deadline=100;
 Model& m;Premises premises;const Ticket retained;const std::array<uint8_t,9> frame{1,0,0,0,0,0,0,0,0};
 Phase phase=Phase::Stop;Fault first=Fault::None;unsigned steps=0;uint32_t started;
 bool cancelled=false,a=false,b=false,c=false,reused=false;
 std::array<Phase,64> trace{};unsigned trace_count=0;
 Sequencer(Model& model,Premises p,uint32_t now=0):m(model),premises(p),retained(model.current),started(now){}
 void fault(Fault f){if(first==Fault::None)first=f;}
 void quarantine(Fault f){fault(f);phase=Phase::Quarantined;m.admission=false;}
 void cancel(){cancelled=true;fault(Fault::Cancelled);}
 void lifecycle(Life l=Life::Reset){m.last_lifecycle=l;quarantine(Fault::Reset);}
 void step(uint32_t now);
 bool reusable()const;
 bool source_acceptance()const{return reusable()&&m.full_success&&!cancelled&&first==Fault::None;}
 bool admit_new(bool management=false);
};
}
