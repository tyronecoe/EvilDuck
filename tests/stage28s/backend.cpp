#include "backend.h"
#include "scheduler_seam.h"
#include "hid_backend.h"
#include "host.h"
#include "USBHID.h"
#include <cstring>
#include <stdexcept>
namespace fixture {
Call calls[CallCapacity]{};size_t count=0;Outcome next=Outcome::Accept;
bool persistent=false;bool clearRefused=false,clearAmbiguous=false;uint32_t clearRequests=0,clearSubmitted=0;
void (*hook)()=nullptr;void (*identity)(uint64_t&,uint64_t&)=nullptr;
}
namespace {
bool pending=false,poison=false;const char* error="";
bool queue(uint8_t mods,const uint8_t *keys,size_t n,bool clear){
 using namespace fixture;
 Outcome o=next;next=Outcome::Accept;
 if(!mock::usbReady||!mock::usbMounted||!mock::usbAccept|| (clear&&clearRefused))o=Outcome::RefuseBeforeAdmission;
 if(clear&&clearAmbiguous)o=Outcome::Ambiguous;
 if(poison)return false;
 if(count==CallCapacity)throw std::runtime_error("fixed backend log exhausted");
 Call &c=calls[count++];c={};c.time=mock::now;c.bytes[0]=mods;c.outcome=o;c.clearing=clear;if(identity&&route_b::active())identity(c.session,c.operation);std::strncpy(c.phase,route_b::phase(),sizeof(c.phase)-1);
 for(size_t i=0;i<n&&i<6;++i)c.bytes[i+2]=keys[i];
 if(hook){auto h=hook;hook=nullptr;h();}
 if(o==Outcome::RefuseBeforeAdmission)return false;
 if(o==Outcome::FailBeforeAdmission){error="known local backend failure";return false;}
 hid_keyboard_report_t r{};r.modifier=mods;for(size_t i=0;i<n&&i<6;++i)r.keycode[i]=keys[i];
 mock::report(r,0,1,8);
 if(o==Outcome::Ambiguous){error="ambiguous backend submission";poison=true;return false;}
 if(clear)++clearSubmitted;return true;
}
}
namespace fixture {void reset(){pending=poison=false;persistent=false;error="";count=0;next=Outcome::Accept;clearRefused=clearAmbiguous=false;clearRequests=clearSubmitted=0;hook=nullptr;identity=nullptr;}}
namespace hid_backend {
void begin(){}
bool beginReport(uint8_t m,const uint8_t *k,uint8_t n){return !pending&&queue(m,k,n,false);}
bool releaseReport(){return !pending&&queue(0,nullptr,0,false);}
void cancelReport(){++fixture::clearRequests;pending=true;if(queue(0,nullptr,0,true))pending=false;}
void update(){if(pending&&queue(0,nullptr,0,true))pending=false;}
bool clearing(){return pending;}
const char* reportError(){return error;}
bool hasPersistent(){return fixture::persistent;}
bool takeTransportLoss(){return !mock::usbMounted;}
bool hold(uint8_t,uint8_t){error="ownership outside native subset";return false;}
bool release(uint8_t,uint8_t){error="ownership outside native subset";return false;}
LockState lockState(){return {};}
uint32_t lockSession(){return 0;}
bool receiveLockReport(uint8_t,const uint8_t*,uint16_t,uint32_t){return false;}
void invalidateLockState(){}
bool saveLockState(){return false;}
void pressKeycode(uint8_t k,uint8_t m){beginReport(m,&k,1);}
void releaseAll(){cancelReport();}
void sendText(const String&){}
void sendTextLn(const String&){}
void pressModifier(uint8_t){}
void pressKeyHeld(uint8_t){}
void pressReport(uint8_t m,const uint8_t*k,uint8_t n){beginReport(m,k,n);}
bool pressNamedCombo(const String&,uint8_t){return false;}
bool keyNameToHid(const String& input,uint8_t& out){
 String n=input;n.toUpperCase();const char* names[]={"ENTER","TAB","SPACE","ESCAPE","BACKSPACE","DELETE","UPARROW","DOWNARROW","LEFTARROW","RIGHTARROW"};
 const uint8_t keys[]={0x28,0x2b,0x2c,0x29,0x2a,0x4c,0x52,0x51,0x50,0x4f};
 for(unsigned i=0;i<10;++i)if(n==names[i]){out=keys[i];return true;}return false;
}
void pressEnter(){pressKeycode(0x28);}void pressTab(){pressKeycode(0x2b);}void pressEscape(){pressKeycode(0x29);}void pressSpace(){pressKeycode(0x2c);}void pressBackspace(){pressKeycode(0x2a);}void pressDelete(){pressKeycode(0x4c);}void pressArrowUp(){pressKeycode(0x52);}void pressArrowDown(){pressKeycode(0x51);}void pressArrowLeft(){pressKeycode(0x50);}void pressArrowRight(){pressKeycode(0x4f);}
}
