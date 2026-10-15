#pragma once
// Native-only scratch scheduler seam. No USB, firmware or host-delivery promise.
#include <stdint.h>
namespace route_b {
struct Id { uint64_t session=0, operation=0; };
inline bool equal(Id a,Id b){return a.session==b.session&&a.operation==b.operation;}
enum class ResultKind { None, Pending, Done, Error, Cancelled };
struct Result { Id id{}; ResultKind kind=ResultKind::None; };
enum class Admission { Rejected, Admitted };
bool acquire(uint64_t &session);
Admission character(uint64_t session,uint16_t value,Id &id);
Admission key(uint64_t session,uint16_t usage,Id &id);
Result result(uint64_t session);
bool consume(Result);
bool cancel(uint64_t session);
bool clearing(uint64_t session);
bool detach(uint64_t session);
bool active();
bool environment();
// Fixture diagnostic APIs, never exposed outside native opt-in scratch build.
const char* phase();
void exhaustForTest(bool session,bool operation);
}
