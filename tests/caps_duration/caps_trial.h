#ifndef EVILDUCK_CAPS_TRIAL_H
#define EVILDUCK_CAPS_TRIAL_H
#include <stdint.h>
namespace caps_trial {
constexpr const char* BuildId="CAPS-DURATION-20261018-v1";
struct Snapshot {
 uint64_t request=0,boot=0,downReturnUs=0,upReturnUs=0,downCompleteUs=0,upCompleteUs=0;
 uint32_t feedbackSession=0;uint16_t requestedMs=0;uint8_t reason=0;
 bool active=false,down=false,up=false,downComplete=false,upComplete=false;
};
bool valid(uint16_t);void begin(uint64_t,uint16_t);void finish(uint64_t,uint8_t);
uint16_t dwell();bool sessionValid();Snapshot snapshot();
void submitted(bool caps,uint64_t at);void completed(bool caps,uint64_t at);
}

#endif
