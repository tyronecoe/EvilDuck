#include "model.h"
#include <limits>
namespace q {
void Model::w1c(uint32_t bits,uint32_t arrival,bool after){
 // W1C hypothesis only for latched Complete/Disabled. Nak/Empty are modeled RO.
 const uint32_t clear=bits&(Complete|Disabled);writes++;operations++;
 if(arrival&clear)race=true; // missing same-bit set/clear priority cannot certify reuse
 if(!after)raw|=arrival;raw&=~clear;if(after)raw|=arrival;
 if(raw&mask)cpu_pending=true; // independent pending CPU latch is never acked here
}
bool Model::enter_isr(Ticket original){
 if(!cpu_pending||isr_active)return false;
 if(original!=current){violation=true;return false;}
 isr_active=true;publishing=true;publisher=original;cpu_pending=false;return true;
}
bool Model::finish_publish(bool success){
 if(!publishing)return false;
 if(queued==queue.size())lost=true;
 else{queue[queued++]={publisher,success};published++;}
 publishing=false;isr_active=false;return !lost;
}
void Model::consume(){
 if(!queued)return;const Event e=queue[0];
 for(size_t i=1;i<queued;i++)queue[i-1]=queue[i];queued--;
 if(e.ticket!=current)dropped_stale++;else if(e.success&&e.length==9){accepted_current++;full_success=true;}
 // This is model event classification, NOT Runtime/Sink/host acknowledgement.
}
bool Model::producer_fence(){
 operations++;
 // External synthetic software handshake; masking/queue-empty alone cannot set it.
 return fence_ack&&!isr_active&&!publishing&&!cpu_pending;
}
void Sequencer::step(uint32_t now){
 if(phase==Phase::Retired||phase==Phase::Quarantined)return;
 if(static_cast<uint32_t>(now-started)>=Deadline||steps>=MaxSteps){quarantine(Fault::Timeout);return;}
 steps++;trace[trace_count++]=phase;
 if(m.lost){quarantine(Fault::Loss);return;}
 if(m.race||m.violation){quarantine(Fault::Contradiction);return;}
 if(m.shared){quarantine(Fault::Shared);return;}
 switch(phase){
 case Phase::Stop:m.admission=false;if(!premises.all()){quarantine(Fault::Missing);return;}phase=Phase::Acquire;break;
 case Phase::Acquire:
  m.operations++;
  if(m.lock_error){quarantine(Fault::Lock);return;}
  if(!m.lock_available)break;
  if(!m.owned||m.current!=retained){quarantine(Fault::Ownership);return;}phase=Phase::Mask;break;
 case Phase::Mask:m.mask_endpoint();phase=Phase::Fence;break;
 case Phase::Fence:if(m.producer_fence())phase=Phase::NakRequest;break;
 case Phase::NakRequest:m.nak_request=true;m.operations++;phase=Phase::NakWait;break;
 case Phase::NakWait:if(m.nak)phase=Phase::DisableRequest;break;
 case Phase::DisableRequest:m.disable_request=true;m.operations++;phase=Phase::DisableWait;break;
 case Phase::DisableWait:if(!m.enabled&&(m.raw&Disabled))phase=Phase::FlushRequest;break;
 case Phase::FlushRequest:m.flush_request=true;m.operations++;phase=Phase::FlushWait;break;
 case Phase::FlushWait:if(!m.flush_request&&m.fifo_words==0)phase=Phase::Acknowledge;break;
 case Phase::Acknowledge:m.w1c(Complete|Disabled);phase=Phase::PublisherFence;break;
 case Phase::PublisherFence:
  if(m.producer_fence()){
   // RO Empty/Nak may persist. Any new latched completion/disable status forbids reuse.
   if(m.raw&(Complete|Disabled)){quarantine(Fault::Contradiction);return;}
   if(!m.visible)break;
   a=true;b=true;phase=Phase::Observers;
  }break;
 case Phase::Observers:if(!m.queued&&!m.observers&&!m.publishing){c=true;phase=Phase::Gate;}break;
 case Phase::Gate:
  if(!reusable()||m.current!=retained){quarantine(Fault::Contradiction);return;}
  phase=Phase::Retired;break;
 default:quarantine(Fault::Contradiction);break;
 }
}
bool Sequencer::reusable()const{
 return (phase==Phase::Gate||phase==Phase::Retired)&&premises.all()&&a&&b&&c&&
 !m.admission&&!m.enabled&&!m.fifo_words&&!m.flush_request&&!m.mask&&
 !(m.raw&(Complete|Disabled))&&!m.cpu_pending&&!m.isr_active&&!m.publishing&&
 !m.queued&&!m.observers&&!m.lost&&!m.race&&!m.violation&&!m.shared&&m.fence_ack&&m.visible&&
 (first==Fault::None||first==Fault::Cancelled);
}
bool Sequencer::admit_new(bool management){
 if(phase!=Phase::Retired||!reusable()||reused||(cancelled&&!management))return false;
 if(retained.q==std::numeric_limits<uint64_t>::max()||retained.c==std::numeric_limits<uint64_t>::max()){quarantine(Fault::Exhausted);return false;}
 // Explicit new lifetime/attempt, not a silent arming or descriptor callback-time tag.
 m.current={retained.c+1,retained.q+1};m.full_success=false;m.admission=true;reused=true;return true;
}
}
