#pragma once
// Synthetic mock bridge ONLY. Never a HID/USB or OS adapter.
#include "keyboard.h"
namespace ds_bridge {
enum class State:uint8_t { Idle, Syncing, Prepared, Running, Failing, Completed, Cancelled, Error, Draining };
enum class Intent:uint8_t { None, Waiting, Ackable };
enum class Reason:uint8_t { None, Busy, InvalidSink, InvalidEvent, Protocol, PlannerRejected, PlannerFailure, RuntimeFailure, Cancelled };
struct Diagnostic {
 Reason reason=Reason::None;ds_keyboard::Reason planner=ds_keyboard::Reason::None;
 ds_keyboard::Phase phase=ds_keyboard::Phase::None;ds_preview::Error runtime{};
 ds_preview::Event event{ds_preview::EventType::Character,0};
};
class Bridge {
 ds_preview::Runtime runtime_;ds_keyboard::Planner planner_;
 ds_keyboard::Sink sink_=nullptr;void* context_=nullptr;
 State state_=State::Idle,drainOrigin_=State::Cancelled;Intent intent_=Intent::None;
 Diagnostic error_{};Reason rejection_=Reason::None;
 ds_preview::Event event_{ds_preview::EventType::Character,0};
 uint32_t now_=0,runAt_=0,runElapsed_=ds_preview::MaxElapsedMs;
 uint32_t admitted_=0,keyboardAcks_=0,delayAcks_=0,lastAckAt_=0;
 bool inStep_=false,sourceWindow_=false,inSource_=false,inReport_=false;
 static ds_preview::Accept report(void*,const ds_keyboard::Report&);
 ds_preview::Accept receive(const ds_preview::Event&);
 bool reject(Reason);
 void latch(Reason);
 void observeRuntime();
 void runtimeStep();
public:
 Bridge()=default;
 Bridge(const Bridge&)=delete;Bridge& operator=(const Bridge&)=delete;
 ~Bridge(){cancel();}
 bool begin(ds_keyboard::Sink,void*,uint32_t now=0,uint32_t attempts=ds_keyboard::MaxAttempts,uint32_t elapsed=ds_keyboard::MaxElapsed);
 bool start(const ds_preview::Program&,uint32_t now=0,uint32_t steps=ds_preview::MaxSteps,uint32_t elapsed=ds_preview::MaxElapsedMs);
 bool hold(size_t owner,uint16_t usage,uint32_t now=0);
 bool release(size_t owner,uint16_t usage,uint32_t now=0);
 void step(uint32_t now);
 void cancel();
 bool drain(uint32_t now=0);
 // Guarded Sink ABI entry, only enabled for the owned Runtime's tick window.
 static ds_preview::Accept sourceSink(void*,const ds_preview::Event&);
 static bool validEvent(const ds_preview::Event&);
 State state()const{return state_;} Intent intent()const{return intent_;}
 const Diagnostic& error()const{return error_;}Reason rejection()const{return rejection_;}
 const ds_preview::Runtime& runtime()const{return runtime_;}
 const ds_keyboard::Planner& planner()const{return planner_;}
 uint32_t admissions()const{return admitted_;}uint32_t keyboardAcks()const{return keyboardAcks_;}
 uint32_t delayAcks()const{return delayAcks_;}uint32_t lastAckAt()const{return lastAckAt_;}
};
}
