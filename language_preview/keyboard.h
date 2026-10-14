#pragma once
// Offline report model ONLY. No transport, descriptors, report IDs or hardware.
#include "core.h"
namespace ds_keyboard {
constexpr size_t MaxOwners=4, MaxKeys=6;
constexpr uint32_t MaxAttempts=256, MaxElapsed=30000;
struct Report { uint8_t bytes[8]={}; };
struct Owner { uint8_t modifiers=0, keys[MaxKeys]={}; };
struct OwnerTable { Owner owners[MaxOwners]={}; };
using Sink=ds_preview::Accept(*)(void*,const Report&);
enum class State:uint8_t { Idle, Ready, Working, Cancelled, Failed };
enum class Phase:uint8_t { None, Sync, Held, Press, Release, Drain };
enum class Reason:uint8_t { None, Busy, InvalidOwner, InvalidUsage, InvalidModifiers, UnsupportedCharacter, Rollover, HeldTap, InvalidBudget, SinkFailure, Exception, Attempts, Timeout, ReleaseRequired };
class Planner {
 OwnerTable owners_{}; Report desired_{}, pending_{}, accepted_{};
 Sink sink_=nullptr;void* context_=nullptr;
 State state_=State::Idle;Phase phase_=Phase::None,diagnostic_=Phase::None;Reason reason_=Reason::None;
 uint32_t since_=0,attempts_=0,attemptLimit_=MaxAttempts,elapsedLimit_=MaxElapsed;
 bool known_=false,uncertain_=false,inStep_=false;
 bool reject(Reason);
 bool available();
 void queue(const Report&,Phase,uint32_t);
 void failure(Reason,Phase);
 static bool ordinary(uint16_t);
 static bool snapshot(const OwnerTable&,Report&,uint8_t key=0,uint8_t modifiers=0);
 bool ownership(size_t,uint16_t,bool,uint32_t,bool confirm=false);
public:
 Planner()=default;
 Planner(const Planner&)=delete;Planner& operator=(const Planner&)=delete;
 bool start(Sink,void*,uint32_t now=0,uint32_t attempts=MaxAttempts,uint32_t elapsed=MaxElapsed);
 bool hold(size_t owner,uint16_t usage,uint32_t now=0);
 bool release(size_t owner,uint16_t usage,uint32_t now=0);
 // Source ownership commands require fresh union-report acceptance even when idempotent.
 bool holdConfirmed(size_t owner,uint16_t usage,uint32_t now=0);
 bool releaseConfirmed(size_t owner,uint16_t usage,uint32_t now=0);
 bool ownerEmpty(size_t owner)const;
 bool tap(uint16_t usage,uint16_t modifiers=0,uint32_t now=0);
 bool character(uint16_t ascii,uint32_t now=0); // fixed US reference model only
 void step(uint32_t now);
 void cancel();
 void stop(){cancel();}
 bool drain(uint32_t now=0); // explicit mock neutral cleanup; never runs ordinary actions
 State state()const{return state_;} Phase phase()const{return phase_;}
 Phase diagnosticPhase()const{return diagnostic_;} Reason reason()const{return reason_;}
 const Report& desired()const{return desired_;} const Report& pending()const{return pending_;}
 const Report& lastAccepted()const{return accepted_;} bool acceptedKnown()const{return known_;}
 bool neutralConfirmed()const;
 bool releaseRequired()const{return !neutralConfirmed();}
 static bool equal(const Report&,const Report&);
 static bool neutral(const Report&);
 static bool validUsage(uint16_t usage);
 static bool mapUS(uint16_t ascii,uint8_t& usage,uint8_t& modifiers);
};
}
