#include "lower.h"
#include "scheduler_seam.h"
#include "USBHID.h"
#include "USB.h"
#include "host.h"
#include "backend_lease.h"
namespace mock { bool report(const hid_keyboard_report_t&,uint8_t,uint8_t,size_t); }
#include <cstring>
#include <stdexcept>
namespace lower {
size_t journalLimit=Capacity;unsigned overflowAttempts=0;Call overflowCall{};Call calls[Capacity]{};size_t count=0;Outcome next=Outcome::True;bool disconnectOnReady=false;void(*hook)()=nullptr;
void reset(){journalLimit=Capacity;overflowAttempts=0;overflowCall={};count=0;next=Outcome::True;disconnectOnReady=false;hook=nullptr;}
bool ready(){bool r=mock::usbReady;if(disconnectOnReady){disconnectOnReady=false;mock::usbMounted=false;if(USB.stopped)USB.stopped(nullptr,nullptr,ARDUINO_USB_STOPPED_EVENT,nullptr);}return r;}
bool submit(uint8_t instance,uint8_t id,const void* data,size_t size){
 if(size!=8)throw std::runtime_error("lower report shape");
 auto s=backend_b::status();bool overflow=count>=journalLimit;Call&c=overflow?overflowCall:calls[count++];c={};c.at=mock::now;c.instance=instance;c.id=id;c.outcome=next;next=Outcome::True;c.session=s.active?s.session:0;c.operation=s.active?s.operation:0;c.clear=s.clearing;std::strncpy(c.phase,route_b::phase(),sizeof(c.phase)-1);memcpy(c.bytes,data,8);
 if(overflow){c.outcome=Outcome::FalseWithoutAcceptance;++overflowAttempts;return false;}
 if(hook){auto h=hook;hook=nullptr;h();}
 // No poisoning, no quarantine and no retry suppression in this fake.
 if(c.outcome!=Outcome::FalseWithoutAcceptance)mock::report(*static_cast<const hid_keyboard_report_t*>(data),instance,id,size);
 return c.outcome==Outcome::True;
}
}
