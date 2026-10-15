#pragma once
// Native prototype only. Ownership/call observations, never USB completion.
#include <stdint.h>
#include <stddef.h>
namespace backend_b {
enum class Kind { None, NoCall, Submitted, CalledFalse, Loss, Invalid, Exhausted };
struct Observation {uint64_t session=0,operation=0,sequence=0;Kind kind=Kind::None;bool called=false,returned=false,clear=false;};
struct Status {bool active=false,quarantined=false,clearing=false;uint64_t session=0,operation=0,clearRequest=0,clearSubmitted=0;Observation last{},first{};uint32_t denied=0;};
class Scope {
 bool entered_=false;
 public:explicit Scope(uint64_t session,uint64_t operation);~Scope();explicit operator bool()const{return entered_;}
 Scope(const Scope&)=delete;Scope& operator=(const Scope&)=delete;
};
bool acquire(uint64_t session);
bool bind(uint64_t session,uint64_t operation);
bool cleanup(uint64_t session);
bool release(uint64_t session);
bool permitted();
bool fatal();
Status status();
void exhaustForTest();
size_t sharedStorageBytes();size_t perThreadStorageBytes();
}
