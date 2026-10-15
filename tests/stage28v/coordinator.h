#pragma once
#include <stdint.h>
#include <stddef.h>
namespace route_u {
enum class Mode{Legacy,RouteB};
enum class Phase{Idle,Queued,Capturing,Verifying,Compiling,Ready,Running,Stopping,Quarantined};
enum class Reason{None,Completed,Cancelled,File,Compiler,Capability,Runtime,Backend,Lost,Deadline};
enum class Reply{Accepted,Busy,QueueFull,Invalid,Unbound,Exhausted};
enum class Service{Settings,Files,Layout,Hid,Storage,Upload,Ota,Restart,Manual};
struct Status{Phase phase=Phase::Idle;Reason reason=Reason::None;uint64_t request=0;uint32_t line=0;uint16_t errorCode=0;bool owned=false;};
bool bindOwner();bool ownerTask();bool owned();Status status();
Reply requestStart(const char*,Mode=Mode::RouteB);Reply requestSnapshot(uint32_t tag);
void stop();void loss();void tick(uint32_t now);
struct Token{uint64_t id=0;};
bool begin(Service,Token&);bool valid(Token);bool end(Token); // explicit multi-callback lifetime
bool enterChunk(Token);bool leaveChunk(Token); // end/abort cannot retire an in-flight chunk
class Transaction {
 Token token_{};
 public:explicit Transaction(Service s){begin(s,token_);}~Transaction(){if(token_.id)end(token_);}
 explicit operator bool()const{return token_.id!=0;}
 Transaction(const Transaction&)=delete;Transaction& operator=(const Transaction&)=delete;
};
bool enterMutation();void leaveMutation();
bool legacyAllowed();
bool selected();void legacySelected();
void exhaustForTest();void setReadPollForTest(bool(*)());
size_t persistentBytes();
}
