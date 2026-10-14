#include "bridge.h"
#include <new>
namespace ds_bridge {
using ds_preview::Accept;using ds_preview::EventType;
bool Bridge::reject(Reason reason){rejection_=reason;return false;}
bool Bridge::validEvent(const ds_preview::Event& event){
 if(event.type==EventType::Delay)return true;
 if(event.type==EventType::KeyTap)return ds_keyboard::Planner::validUsage(event.value);
 if(event.type==EventType::Character){uint8_t usage,modifiers;return ds_keyboard::Planner::mapUS(event.value,usage,modifiers);}return false;
}
void Bridge::latch(Reason reason){
 if(error_.reason==Reason::None){error_.reason=reason;error_.planner=planner_.reason();error_.phase=planner_.diagnosticPhase()==ds_keyboard::Phase::None?planner_.phase():planner_.diagnosticPhase();error_.event=event_;}
}
bool Bridge::begin(ds_keyboard::Sink sink,void* context,uint32_t now,uint32_t attempts,uint32_t elapsed){
 if(inStep_||!(state_==State::Idle||state_==State::Completed||state_==State::Cancelled||state_==State::Error))return reject(Reason::Busy);
 if(!sink)return reject(Reason::InvalidSink);
 if(!planner_.start(report,this,now,attempts,elapsed))return reject(Reason::PlannerRejected);
 runtime_.~Runtime();new(&runtime_) ds_preview::Runtime();
 sink_=sink;context_=context;intent_=Intent::None;event_={EventType::Character,0};error_={};rejection_=Reason::None;
 admitted_=keyboardAcks_=delayAcks_=lastAckAt_=0;now_=now;state_=State::Syncing;return true;
}
bool Bridge::start(const ds_preview::Program& program,uint32_t now,uint32_t steps,uint32_t elapsed){
 if(inStep_||state_!=State::Prepared||planner_.state()!=ds_keyboard::State::Ready)return reject(Reason::Busy);
 if(!runtime_.start(program,sourceSink,this,now,steps,elapsed)){latch(Reason::RuntimeFailure);error_.runtime=runtime_.error();planner_.cancel();state_=State::Error;return false;}
 intent_=Intent::None;runAt_=now;runElapsed_=elapsed;state_=State::Running;rejection_=Reason::None;return true;
}
bool Bridge::hold(size_t owner,uint16_t usage,uint32_t now){
 if(inStep_||state_!=State::Prepared)return reject(Reason::Busy);if(!planner_.hold(owner,usage,now))return reject(Reason::PlannerRejected);return true;
}
bool Bridge::release(size_t owner,uint16_t usage,uint32_t now){
 if(inStep_||state_!=State::Prepared)return reject(Reason::Busy);if(!planner_.release(owner,usage,now))return reject(Reason::PlannerRejected);return true;
}
Accept Bridge::report(void* ptr,const ds_keyboard::Report& report){
 auto& b=*static_cast<Bridge*>(ptr);if(!b.inStep_||b.inReport_)return Accept::Failed;
 b.inReport_=true;struct Guard{bool& flag;~Guard(){flag=false;}} guard{b.inReport_};return b.sink_(b.context_,report);
}
Accept Bridge::sourceSink(void* ptr,const ds_preview::Event& event){
 if(!ptr)return Accept::Failed;auto& b=*static_cast<Bridge*>(ptr);if(!b.sourceWindow_||b.inSource_||b.inReport_){b.reject(Reason::Busy);return Accept::Failed;}
 b.inSource_=true;struct Guard{bool& flag;~Guard(){flag=false;}} guard{b.inSource_};return b.receive(event);
}
Accept Bridge::receive(const ds_preview::Event& event){
 if(state_==State::Failing||error_.reason!=Reason::None)return Accept::Failed;
 if(state_!=State::Running)return Accept::Failed;
 if(intent_!=Intent::None){
  if(event.type!=event_.type||event.value!=event_.value){latch(Reason::Protocol);planner_.cancel();return Accept::Failed;}
  if(intent_==Intent::Waiting)return Accept::Retry;
  ++keyboardAcks_;lastAckAt_=now_;intent_=Intent::None;return Accept::Accepted;
 }
 event_=event;
 if(!validEvent(event)){latch(Reason::InvalidEvent);planner_.cancel();return Accept::Failed;}
 if(planner_.state()!=ds_keyboard::State::Ready){latch(Reason::Protocol);planner_.cancel();return Accept::Failed;}
 if(event.type==EventType::Delay){++delayAcks_;lastAckAt_=now_;return Accept::Accepted;}
 bool ok=event.type==EventType::Character?planner_.character(event.value,now_):planner_.tap(event.value,0,now_);
 if(!ok){latch(Reason::PlannerRejected);planner_.cancel();return Accept::Failed;}
 ++admitted_;intent_=Intent::Waiting;return Accept::Retry;
}
void Bridge::observeRuntime(){
 if(runtime_.state()==ds_preview::State::Running)return;
 if(runtime_.state()==ds_preview::State::Error){latch(Reason::RuntimeFailure);error_.runtime=runtime_.error();state_=State::Error;}
 else if(runtime_.state()==ds_preview::State::Completed)state_=State::Completed;
 else if(runtime_.state()==ds_preview::State::Cancelled)state_=State::Cancelled;
 intent_=Intent::None;planner_.cancel();
}
void Bridge::runtimeStep(){sourceWindow_=true;runtime_.tick(now_);sourceWindow_=false;observeRuntime();}
void Bridge::step(uint32_t now){
 if(inStep_)return;inStep_=true;struct Guard{bool& flag;~Guard(){flag=false;}} guard{inStep_};now_=now;
 if(state_==State::Failing){runtimeStep();return;}
 if(state_==State::Running&&uint32_t(now-runAt_)>=runElapsed_){runtimeStep();return;}
 if(state_==State::Syncing||state_==State::Prepared||state_==State::Draining||(state_==State::Running&&planner_.state()==ds_keyboard::State::Working)){
  if(planner_.state()==ds_keyboard::State::Working)planner_.step(now);
  if(planner_.state()==ds_keyboard::State::Failed){latch(Reason::PlannerFailure);if(state_==State::Running)state_=State::Failing;else state_=State::Error;return;}
  if(state_==State::Cancelled||state_==State::Error)return;
  if(state_==State::Syncing&&planner_.state()==ds_keyboard::State::Ready)state_=State::Prepared;
  else if(state_==State::Running&&intent_==Intent::Waiting&&planner_.state()==ds_keyboard::State::Ready)intent_=Intent::Ackable;
  else if(state_==State::Draining&&planner_.state()==ds_keyboard::State::Cancelled&&planner_.neutralConfirmed())state_=drainOrigin_;
  return;
 }
 if(state_==State::Running)runtimeStep();
}
void Bridge::cancel(){
 if(state_==State::Idle||state_==State::Completed||state_==State::Cancelled||state_==State::Error)return;
 runtime_.cancel();planner_.cancel();intent_=Intent::None;state_=State::Cancelled;
}
bool Bridge::drain(uint32_t now){
 if(inStep_||!(state_==State::Completed||state_==State::Cancelled||state_==State::Error))return reject(Reason::Busy);
 if(!planner_.drain(now))return reject(Reason::PlannerRejected);drainOrigin_=state_;state_=State::Draining;return true;
}
}
