#include "model.h"
#include <cstdio>
#include <cstdlib>
#include <limits>
using namespace q;
static unsigned checks;
#define CHECK(v) do{checks++;if(!(v)){std::fprintf(stderr,"FAIL line=%d: %s\n",__LINE__,#v);std::exit(1);}}while(0)
static void progress(Model& m,Sequencer& s,unsigned limit=40){
 for(unsigned i=0;i<limit&&s.phase!=Phase::Retired&&s.phase!=Phase::Quarantined;i++){
  if(s.phase==Phase::NakWait)m.nak_ack();
  if(s.phase==Phase::DisableWait)m.disable_ack();
  if(s.phase==Phase::FlushWait)m.flush_ack();
  // A fixture-provided CPU/publisher/visibility certificate, NOT inferred from masking.
  if(!m.isr_active&&!m.publishing)m.cpu_pending=false;
  m.fence_ack=true;m.visible=true;
  const unsigned before=m.operations;s.step(i);CHECK(m.operations-before<=1);
 }
}
static void until(Model& m,Sequencer& s,Phase p){
 for(unsigned i=0;i<25&&s.phase!=p&&s.phase!=Phase::Quarantined;i++){
  if(s.phase==Phase::NakWait)m.nak_ack();if(s.phase==Phase::DisableWait)m.disable_ack();if(s.phase==Phase::FlushWait)m.flush_ack();
  m.cpu_pending=false;m.fence_ack=true;m.visible=true;s.step(i);
 }CHECK(s.phase==p);
}
static void run(unsigned id){
 Model m;Sequencer s(m,Premises::synthetic());
 switch(id){
 case 1:m.assert_status(Complete);CHECK(m.enter_isr(s.retained));CHECK(m.finish_publish());m.consume();progress(m,s);CHECK(s.phase==Phase::Retired&&s.a&&s.b&&s.c&&s.reusable());CHECK(s.source_acceptance());break;
 case 2:s.cancel();s.cancel();progress(m,s);CHECK(s.reusable()&&!s.source_acceptance());CHECK(!s.admit_new());CHECK(s.admit_new(true));break;
 case 3:m.assert_status(Complete);m.mask_endpoint();CHECK(m.raw&Complete);CHECK(m.cpu_pending);CHECK(m.enter_isr(s.retained));CHECK(!m.producer_fence());CHECK(m.finish_publish());m.consume();progress(m,s);CHECK(s.reusable());break;
 case 4:m.raw=Complete|Disabled|Empty|Nak;m.w1c(Complete);CHECK(!(m.raw&Complete)&&(m.raw&Disabled)&&(m.raw&Empty)&&(m.raw&Nak));break;
 case 5:case 6:m.raw=Complete;m.w1c(Complete,Complete,id==5);CHECK(m.race);progress(m,s);CHECK(!s.reusable()&&s.first==Fault::Contradiction);break;
 case 7:m.assert_status(Complete);CHECK(m.enter_isr(s.retained));s.step(0);s.step(1);s.step(2);s.step(3);CHECK(!s.a&&!s.b);CHECK(!s.reusable());CHECK(m.finish_publish());m.consume();progress(m,s);CHECK(s.reusable());break;
 case 8:m.assert_status(Complete);CHECK(m.enter_isr(s.retained));CHECK(m.finish_publish());m.enabled=false;CHECK(m.queued==1);until(m,s,Phase::Observers);CHECK(!s.reusable());m.consume();progress(m,s);CHECK(s.reusable());break;
 case 9:case 10:case 11:{
  const Phase p=id==9?Phase::NakWait:id==10?Phase::DisableWait:Phase::FlushWait;until(m,s,p);
  for(unsigned i=0;i<40;i++)s.step(i);CHECK(s.phase==Phase::Quarantined&&s.first==Fault::Timeout);CHECK(!s.reusable());break;}
 case 12:until(m,s,Phase::FlushWait);CHECK(m.fifo_words==3&&!s.a);m.flush_ack();progress(m,s);CHECK(s.reusable());break;
 case 13:{Sequencer public_profile(m,Premises{});public_profile.step(0);CHECK(public_profile.first==Fault::Missing);CHECK(m.writes==0&&!public_profile.reusable());break;}
 case 14:for(unsigned l=0;l<3;l++)for(unsigned p=0;p<14;p++){Model x;Sequencer y(x,Premises::synthetic());until(x,y,static_cast<Phase>(p));y.lifecycle(static_cast<Life>(l));progress(x,y);CHECK(!y.reusable()&&y.first==Fault::Reset);}break;
 case 15:for(unsigned i=0;i<5;i++){m.cpu_pending=true;CHECK(m.enter_isr(s.retained));m.finish_publish();}CHECK(m.lost&&m.queued==4);progress(m,s);CHECK(s.first==Fault::Loss&&!s.reusable());break;
 case 16:m.lock_error=true;progress(m,s);CHECK(s.first==Fault::Lock&&m.writes==0);break;
 case 17:m.lock_available=false;progress(m,s);CHECK(s.first==Fault::Timeout&&m.writes==0);break;
 case 18:until(m,s,Phase::NakWait);CHECK(!s.admit_new()&&m.current==s.retained);progress(m,s);CHECK(s.admit_new());CHECK(m.current!=s.retained);CHECK((s.frame==std::array<uint8_t,9>({1,0,0,0,0,0,0,0,0})));CHECK(!s.admit_new());break;
 case 19:progress(m,s);CHECK(s.admit_new());m.queue[0]={s.retained,true};m.queued=1;m.consume();CHECK(m.dropped_stale==1&&m.accepted_current==0);break;
 case 20:progress(m,s);CHECK(s.admit_new());m.assert_status(Complete);m.cpu_pending=true;CHECK(!m.enter_isr(s.retained));CHECK(m.violation&&!s.reusable()); // deliberately violates synthetic no-late-old-status premise; no retag allowed
  break;
 case 21:m.shared=true;progress(m,s);CHECK(s.first==Fault::Shared&&m.writes==0);break;
 case 22:m.observers=1;until(m,s,Phase::Observers);s.step(30);CHECK(!s.reusable());m.observers=0;s.step(31);s.step(32);CHECK(s.reusable());break;
 case 23:m.current.q=std::numeric_limits<uint64_t>::max();{Sequencer x(m,Premises::synthetic());progress(m,x);CHECK(x.reusable());CHECK(!x.admit_new());CHECK(x.first==Fault::Exhausted&&m.current.q==std::numeric_limits<uint64_t>::max());}break;
 case 24:s.cancel();m.lost=true;s.step(0);CHECK(s.phase==Phase::Quarantined&&s.first==Fault::Cancelled&&!s.reusable());break;
 case 25:until(m,s,Phase::NakWait);s.steps=Sequencer::MaxSteps-1;s.step(1);CHECK(s.steps==Sequencer::MaxSteps);s.step(2);CHECK(s.first==Fault::Timeout&&!s.reusable());break;
 case 26:s.step(Sequencer::Deadline);CHECK(s.first==Fault::Timeout&&s.steps==0);break;
 case 27:{Sequencer wrap(m,Premises::synthetic(),UINT32_MAX-20);wrap.step(5);CHECK(wrap.first==Fault::None);wrap.step(79);CHECK(wrap.first==Fault::Timeout);break;}
 case 28:m.owned=false;progress(m,s);CHECK(s.first==Fault::Ownership&&m.writes==0);break;
 case 29:until(m,s,Phase::PublisherFence);m.visible=false;m.fence_ack=true;m.cpu_pending=false;s.step(1);CHECK(!s.a&&!s.b&&!s.reusable());m.visible=true;progress(m,s);CHECK(s.reusable());break;
 case 30:for(unsigned bit=0;bit<8;bit++){Model x;auto p=Premises::synthetic();bool* fields[]={&p.sequence,&p.stop_access,&p.no_late_status,&p.visibility,&p.software_fence,&p.exclusive,&p.ack_order,&p.scope};*fields[bit]=false;Sequencer y(x,p);y.step(0);CHECK(!y.reusable()&&y.first==Fault::Missing&&x.writes==0);}break;
 case 31:until(m,s,Phase::PublisherFence);m.assert_status(Complete);m.fence_ack=true;m.cpu_pending=false;s.step(1);CHECK(s.first==Fault::Contradiction&&!s.reusable());break;
 case 32:until(m,s,Phase::Gate);m.publishing=true;s.step(1);CHECK(!s.reusable()&&s.first==Fault::Contradiction);break;
 case 33:progress(m,s);CHECK(s.reusable()&&!s.source_acceptance()&&m.accepted_current==0);break;
 case 34:for(bool after:{false,true}){Model x;x.raw=Complete;x.w1c(Complete,Disabled,after);CHECK(x.raw&Disabled);CHECK(!x.race);}break;
 case 35:m.queue[0]={m.current,false,9};m.queued=1;m.consume();progress(m,s);CHECK(!s.source_acceptance());break;
 case 36:m.queue[0]={m.current,true,4};m.queued=1;m.consume();progress(m,s);CHECK(!s.source_acceptance());break;
 case 37:for(unsigned t=0;t<40;t++)s.step(t);CHECK(s.phase==Phase::Quarantined&&s.first==Fault::Timeout&&!s.reusable());break;
 default:CHECK(false);
 }
#ifdef STAGE28Q_NEGATIVE_CONTROL
 CHECK(false);
#endif
 std::printf("{\"id\":\"Q%02u\",\"PASS\":true,\"assertions\":%u,\"phase\":%u,\"fault\":%u,\"steps\":%u,\"raw\":%u,\"mask\":%u,\"cpu_pending\":%s,\"isr_active\":%s,\"queued\":%zu,\"loss\":%s,\"A\":%s,\"B\":%s,\"C\":%s,\"reusable\":%s,\"ticket_c\":%llu,\"ticket_q\":%llu,\"model_bytes\":%zu,\"sequencer_bytes\":%zu,\"physical_certificate\":false,\"trace\":[",id,checks,unsigned(s.phase),unsigned(s.first),s.steps,m.raw,m.mask,m.cpu_pending?"true":"false",m.isr_active?"true":"false",m.queued,m.lost?"true":"false",s.a?"true":"false",s.b?"true":"false",s.c?"true":"false",s.reusable()?"true":"false",(unsigned long long)m.current.c,(unsigned long long)m.current.q,sizeof(m),sizeof(s));
 for(unsigned i=0;i<s.trace_count;i++)std::printf("%s%u",i?",":"",unsigned(s.trace[i]));std::puts("]}");
}
int main(int argc,char** argv){CHECK(argc==2);run(unsigned(std::strtoul(argv[1],nullptr,10)));}
