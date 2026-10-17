#pragma once
#include <stdint.h>
namespace led_mock{inline int64_t nowUs=0;}
inline int64_t esp_timer_get_time(){return led_mock::nowUs;}
