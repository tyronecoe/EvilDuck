#include "caps_trial.h"
#include "feedback_diag.h"
#ifdef EVILDUCK_HOST_TEST
#include <mutex>
namespace{std::mutex mux;struct Guard{std::lock_guard<std::mutex> l{mux};};}
#else
#include <freertos/FreeRTOS.h>
namespace{portMUX_TYPE mux=portMUX_INITIALIZER_UNLOCKED;struct Guard{Guard(){portENTER_CRITICAL(&mux);}~Guard(){portEXIT_CRITICAL(&mux);}};}
#endif
namespace{caps_trial::Snapshot state;}
namespace caps_trial {
bool valid(uint16_t ms){return ms==0||ms==100||ms==250||ms==500;}
void begin(uint64_t request,uint16_t ms){const auto d=feedback_diag::snapshot();Guard l;state={};state.request=request;state.boot=d.boot;state.feedbackSession=d.session;state.requestedMs=ms;state.active=true;}
void finish(uint64_t request,uint8_t reason){Guard l;if(state.request==request&&state.active){state.reason=reason;state.active=false;}}
uint16_t dwell(){Guard l;return state.active?state.requestedMs:0;}
bool sessionValid(){const auto d=feedback_diag::snapshot();const auto t=feedback_diag::transport();Guard l;return !state.active||(state.feedbackSession==d.session&&t.configured&&!t.suspended);}
Snapshot snapshot(){Guard l;return state;}
void submitted(bool caps,uint64_t at){Guard l;if(!state.active)return;if(caps&&!state.down){state.down=true;state.downReturnUs=at;}else if(!caps&&state.down&&!state.up){state.up=true;state.upReturnUs=at;}}
void completed(bool caps,uint64_t at){Guard l;if(!state.active)return;if(caps&&!state.downComplete){state.downComplete=true;state.downCompleteUs=at;}else if(!caps&&state.downComplete&&!state.upComplete){state.upComplete=true;state.upCompleteUs=at;}}
}
