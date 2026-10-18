#ifndef EVILDUCK_FEEDBACK_DIAG_H
#define EVILDUCK_FEEDBACK_DIAG_H
#include <stdint.h>
#include <stddef.h>
namespace feedback_diag {
constexpr const char* BuildId="LED-FEEDBACK-BOUNDARY-20261018-v1";
struct Snapshot {
 uint64_t boot=0; uint32_t session=0, lifecycle[4]={},raw=0,attempts=0,dispatches=0,keyboardDispatches=0,features=0,reasons[9]={},receiver[7]={};
 uint8_t instance=0,id=0,type=0,effectiveId=0,protocol=255,interfaceProtocol=0;uint16_t length=0;
 bool registeredKeyboard=false,rawInSession=false;uint64_t rawUs=0,capsDownReturnUs=0,capsUpReturnUs=0,capsDownCompleteUs=0,capsUpCompleteUs=0;
 uint32_t capsDownQueued=0,capsUpQueued=0,capsDownCompleted=0,capsUpCompleted=0;
};
void initialize(uint64_t boot);void invalidate(uint32_t session);Snapshot snapshot();
void receiver(uint8_t reason,uint32_t session);
void submitted(bool caps,bool accepted,uint64_t at);
}
extern "C" void evilduck_hid_route_diagnostic(uint8_t stage,uint8_t instance,uint8_t id,uint8_t type,uint16_t length,uint8_t effective,uint8_t protocol,uint8_t interfaceProtocol,bool registered);
extern "C" void evilduck_usb_feedback_lifecycle(uint8_t event);
extern "C" void evilduck_hid_input_diagnostic(uint8_t instance,const uint8_t* report,uint16_t length,uint8_t protocol,uint8_t interfaceProtocol);
namespace feedback_diag {
struct Transport{bool busConnected,configured,suspended,hidReady;uint8_t protocol;};
Transport transport();
#ifdef EVILDUCK_HOST_TEST
extern bool mockSuspended;
#endif
}

#endif
