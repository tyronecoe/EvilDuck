#include "keyboard.h"
#include <string.h>
namespace ds_keyboard {
bool Planner::equal(const Report& a,const Report& b){return memcmp(a.bytes,b.bytes,8)==0;}
bool Planner::neutral(const Report& r){for(uint8_t b:r.bytes)if(b)return false;return true;}
bool Planner::neutralConfirmed()const{return known_&&!uncertain_&&neutral(accepted_);}
bool Planner::ordinary(uint16_t usage){return usage>=4&&usage<=0x73;}
bool Planner::validUsage(uint16_t usage){return ordinary(usage)||(usage>=0xe0&&usage<=0xe7);}
bool Planner::reject(Reason r){if(state_!=State::Failed)reason_=r;return false;}
bool Planner::available(){if(inStep_||state_!=State::Ready)return reject(Reason::Busy);reason_=Reason::None;return true;}
bool Planner::snapshot(const OwnerTable& table,Report& result,uint8_t key,uint8_t modifiers){
 result=Report{};result.bytes[0]=modifiers;
 for(const Owner& owner:table.owners){result.bytes[0]|=owner.modifiers;
  for(uint8_t usage:owner.keys){if(!usage)continue;bool found=false;for(unsigned i=2;i<8;++i)if(result.bytes[i]==usage)found=true;if(found)continue;
   unsigned slot=2;while(slot<8&&result.bytes[slot])++slot;if(slot==8)return false;result.bytes[slot]=usage;
  }
 }
 if(key){bool found=false;for(unsigned i=2;i<8;++i)if(result.bytes[i]==key)found=true;if(!found){unsigned slot=2;while(slot<8&&result.bytes[slot])++slot;if(slot==8)return false;result.bytes[slot]=key;}}
 for(unsigned i=3;i<8;++i)for(unsigned j=i;j>2&&result.bytes[j]&&(!result.bytes[j-1]||result.bytes[j]<result.bytes[j-1]);--j){uint8_t t=result.bytes[j];result.bytes[j]=result.bytes[j-1];result.bytes[j-1]=t;}
 return true;
}
void Planner::queue(const Report& report,Phase phase,uint32_t now){pending_=report;phase_=phase;state_=State::Working;since_=now;attempts_=0;reason_=Reason::None;diagnostic_=Phase::None;}
bool Planner::start(Sink sink,void* context,uint32_t now,uint32_t attempts,uint32_t elapsed){
 if(inStep_||state_==State::Ready||state_==State::Working)return reject(Reason::Busy);
 if(state_!=State::Idle&&!neutralConfirmed())return reject(Reason::ReleaseRequired);
 if(!sink)return reject(Reason::SinkFailure);if(!attempts||attempts>MaxAttempts||!elapsed||elapsed>MaxElapsed)return reject(Reason::InvalidBudget);
 owners_=OwnerTable{};desired_=Report{};sink_=sink;context_=context;attemptLimit_=attempts;elapsedLimit_=elapsed;queue(Report{},Phase::Sync,now);return true;
}
bool Planner::ownership(size_t owner,uint16_t usage,bool acquire,uint32_t now,bool confirm){
 if(!available())return false;if(owner>=MaxOwners)return reject(Reason::InvalidOwner);
 bool modifier=usage>=0xe0&&usage<=0xe7;if(!modifier&&!ordinary(usage))return reject(Reason::InvalidUsage);
 OwnerTable proposed=owners_;Owner& record=proposed.owners[owner];
 if(modifier){uint8_t bit=static_cast<uint8_t>(1u<<(usage-0xe0));if(acquire)record.modifiers|=bit;else record.modifiers&=static_cast<uint8_t>(~bit);}
 else{size_t slot=0;while(slot<MaxKeys&&record.keys[slot]!=usage)++slot;
  if(acquire&&slot==MaxKeys){slot=0;while(slot<MaxKeys&&record.keys[slot])++slot;if(slot==MaxKeys)return reject(Reason::Rollover);record.keys[slot]=static_cast<uint8_t>(usage);}
  else if(!acquire&&slot<MaxKeys)record.keys[slot]=0;
 }
 Report report;if(!snapshot(proposed,report))return reject(Reason::Rollover);
 owners_=proposed;desired_=report;if(confirm||!known_||!equal(report,accepted_))queue(report,Phase::Held,now);return true;
}
bool Planner::hold(size_t owner,uint16_t usage,uint32_t now){return ownership(owner,usage,true,now);}
bool Planner::release(size_t owner,uint16_t usage,uint32_t now){return ownership(owner,usage,false,now);}
bool Planner::holdConfirmed(size_t owner,uint16_t usage,uint32_t now){return ownership(owner,usage,true,now,true);}
bool Planner::releaseConfirmed(size_t owner,uint16_t usage,uint32_t now){return ownership(owner,usage,false,now,true);}
bool Planner::ownerEmpty(size_t owner)const{
 if(owner>=MaxOwners)return false;const Owner& record=owners_.owners[owner];
 if(record.modifiers)return false;for(uint8_t key:record.keys)if(key)return false;return true;
}
bool Planner::tap(uint16_t usage,uint16_t modifierMask,uint32_t now){
 if(!available())return false;if(modifierMask>255)return reject(Reason::InvalidModifiers);uint8_t modifiers=static_cast<uint8_t>(modifierMask),key=0;
 if(usage>=0xe0&&usage<=0xe7){uint8_t bit=static_cast<uint8_t>(1u<<(usage-0xe0));if(desired_.bytes[0]&bit)return reject(Reason::HeldTap);modifiers|=bit;}
 else{if(!ordinary(usage))return reject(Reason::InvalidUsage);key=static_cast<uint8_t>(usage);for(unsigned i=2;i<8;++i)if(desired_.bytes[i]==key)return reject(Reason::HeldTap);}
 Report report;if(!snapshot(owners_,report,key,modifiers))return reject(Reason::Rollover);queue(report,Phase::Press,now);return true;
}
bool Planner::mapUS(uint16_t c,uint8_t& usage,uint8_t& modifiers){
 usage=modifiers=0;if(c>126)return false;
 if(c>='a'&&c<='z'){usage=static_cast<uint8_t>(4+c-'a');return true;}
 if(c>='A'&&c<='Z'){usage=static_cast<uint8_t>(4+c-'A');modifiers=2;return true;}
 if(c>='1'&&c<='9'){usage=static_cast<uint8_t>(0x1e + c-'1');return true;}if(c=='0'){usage=0x27;return true;}
 if(c==' '){usage=0x2c;return true;}if(c=='\t'){usage=0x2b;return true;}if(c=='\n'){usage=0x28;return true;}
 const char* plain="-=[]\\;'`,./";const char* shifted="_+{}|:\"~<>?";
 const uint8_t usages[]={0x2d,0x2e,0x2f,0x30,0x31,0x33,0x34,0x35,0x36,0x37,0x38};
 for(unsigned i=0;i<11;++i){if(c==static_cast<uint8_t>(plain[i])){usage=usages[i];return true;}if(c==static_cast<uint8_t>(shifted[i])){usage=usages[i];modifiers=2;return true;}}
 const char* digits="!@#$%^&*()";for(unsigned i=0;i<10;++i)if(c==static_cast<uint8_t>(digits[i])){usage=static_cast<uint8_t>(i==9?0x27:0x1e + i);modifiers=2;return true;}return false;
}
bool Planner::character(uint16_t ascii,uint32_t now){if(!available())return false;uint8_t key,mods;if(!mapUS(ascii,key,mods))return reject(Reason::UnsupportedCharacter);return tap(key,mods,now);}
void Planner::failure(Reason reason,Phase phase){reason_=reason;diagnostic_=phase;owners_=OwnerTable{};desired_=Report{};state_=State::Failed;phase_=Phase::None;uncertain_=true;}
void Planner::step(uint32_t now){
 if(inStep_||state_!=State::Working)return;
 if(attempts_==attemptLimit_){failure(Reason::Attempts,phase_);return;}if(uint32_t(now-since_)>=elapsedLimit_){failure(Reason::Timeout,phase_);return;}
 ++attempts_;inStep_=true;struct Guard{bool& flag;~Guard(){flag=false;}} guard{inStep_};Report attempted=pending_;Phase phase=phase_;ds_preview::Accept result;
 try{result=sink_(context_,attempted);}catch(...){failure(Reason::Exception,phase);return;}
 if(result==ds_preview::Accept::Accepted){accepted_=attempted;known_=true;if(neutral(attempted))uncertain_=false;}
 else if(result!=ds_preview::Accept::Retry){failure(Reason::SinkFailure,phase);return;}
 if(state_!=State::Working)return;if(result==ds_preview::Accept::Retry)return;
 if(phase==Phase::Press){pending_=desired_;phase_=Phase::Release;return;}
 phase_=Phase::None;state_=phase==Phase::Drain?State::Cancelled:State::Ready;reason_=Reason::None;
}
void Planner::cancel(){if(state_==State::Idle||state_==State::Cancelled)return;if(phase_!=Phase::None)diagnostic_=phase_;owners_=OwnerTable{};desired_=Report{};state_=State::Cancelled;phase_=Phase::None;}
bool Planner::drain(uint32_t now){
 if(inStep_||!(state_==State::Cancelled||state_==State::Failed))return reject(Reason::Busy);
 if(!sink_)return reject(Reason::SinkFailure);queue(Report{},Phase::Drain,now);return true;
}
}
