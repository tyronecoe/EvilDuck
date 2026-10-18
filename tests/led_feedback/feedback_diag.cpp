#include "feedback_diag.h"
#include "hid_backend.h"
#include <esp_timer.h>
#ifdef EVILDUCK_HOST_TEST
#include <mutex>
namespace{std::mutex mux;struct Guard{std::lock_guard<std::mutex> l{mux};};}
#else
#include <freertos/FreeRTOS.h>
namespace{portMUX_TYPE mux=portMUX_INITIALIZER_UNLOCKED;struct Guard{Guard(){portENTER_CRITICAL(&mux);}~Guard(){portEXIT_CRITICAL(&mux);}};}
#endif
namespace {feedback_diag::Snapshot state;bool capsQueued=false,capsCompletedPending=false;void inc(uint32_t& n){if(n!=UINT32_MAX)++n;}}
namespace feedback_diag {
void initialize(uint64_t boot){Guard l;if(!state.boot)state.boot=boot;}
void invalidate(uint32_t session){Guard l;state.session=session;state.rawInSession=false;state.registeredKeyboard=false;state.protocol=255;state.rawUs=0;state.length=0;state.id=state.type=state.instance=state.effectiveId=0;capsQueued=capsCompletedPending=false;}
Snapshot snapshot(){Guard l;return state;}
// 0 accepted,1 ID,2 length/null,3 padding,4 not configured,5 stale session,6 suspended.
void receiver(uint8_t reason,uint32_t session){Guard l;if(reason==0&&session!=state.session)reason=5;if(reason<7)inc(state.receiver[reason]);}
void submitted(bool caps,bool accepted,uint64_t at){if(!accepted)return;Guard l;
 if(caps&&!capsQueued){inc(state.capsDownQueued);state.capsDownReturnUs=at;}
 if(!caps&&capsQueued){inc(state.capsUpQueued);state.capsUpReturnUs=at;}capsQueued=caps;
}
}
// Stage0 raw,1 route attempt,2 dispatch,3 FEATURE,4..12 rejection by reason.
extern "C" void evilduck_hid_route_diagnostic(uint8_t stage,uint8_t instance,uint8_t id,uint8_t type,uint16_t length,uint8_t effective,uint8_t protocol,uint8_t interfaceProtocol,bool registered){
 const uint64_t now=uint64_t(esp_timer_get_time());Guard l;
 if(stage==0){inc(state.raw);state.rawInSession=true;state.instance=instance;state.id=id;state.type=type;state.length=length;state.protocol=protocol;state.interfaceProtocol=interfaceProtocol;state.registeredKeyboard=registered;state.rawUs=now;}
 else if(stage==1){inc(state.attempts);state.effectiveId=effective;}
 else if(stage==2){inc(state.dispatches);if(effective==1&&registered)inc(state.keyboardDispatches);}
 else if(stage==3)inc(state.features);
 else if(stage>=4&&stage<13)inc(state.reasons[stage-4]);
}
extern "C" void evilduck_usb_feedback_lifecycle(uint8_t event){
 {Guard l;if(event<4)inc(state.lifecycle[event]);}
 // Called synchronously by TinyUSB mount/unmount/suspend/resume, before queued Arduino events.
#ifdef EVILDUCK_HOST_TEST
 feedback_diag::mockSuspended=event==2;
#endif
 hid_backend::invalidateLockState();
}
extern "C" void evilduck_hid_input_diagnostic(uint8_t instance,const uint8_t* report,uint16_t length,uint8_t protocol,uint8_t interfaceProtocol){
 if(instance||!report)return;const uint8_t* p=nullptr;
 if(length==9&&report[0]==1&&protocol==1)p=report+1;
 else if(length==8&&protocol==0&&interfaceProtocol==1)p=report;
 if(!p)return;bool caps=false;for(unsigned i=2;i<8;++i)caps|=p[i]==0x39;
 const uint64_t now=uint64_t(esp_timer_get_time());Guard l;
 if(caps){inc(state.capsDownCompleted);state.capsDownCompleteUs=now;capsCompletedPending=true;}
 else if(capsCompletedPending){capsCompletedPending=false;inc(state.capsUpCompleted);state.capsUpCompleteUs=now;}
}
