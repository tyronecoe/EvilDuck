#pragma once
#include "diagnostics.h"
#ifdef EVILDUCK_HOST_TEST
namespace x_mock {inline int64_t nowUs=0;inline uint32_t probes=0;inline int64_t clockStep=0;inline route_x::Resources values{100000,90000,80000,8192,4096,true,true};}
namespace x_platform {inline int64_t clockUs(){auto n=x_mock::nowUs;x_mock::nowUs+=x_mock::clockStep;return n;}inline route_x::Resources sample(){++x_mock::probes;return x_mock::values;}}
#else
#include <esp_timer.h>
#include <esp_heap_caps.h>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>
extern size_t getArduinoLoopTaskStackSize(void);
namespace x_platform {
inline int64_t clockUs(){return esp_timer_get_time();}
inline route_x::Resources sample(){
 route_x::Resources r;
 r.free8=heap_caps_get_free_size(MALLOC_CAP_8BIT);
 r.min8=heap_caps_get_minimum_free_size(MALLOC_CAP_8BIT);
 r.largest8=heap_caps_get_largest_free_block(MALLOC_CAP_8BIT);r.heapKnown=true;
 // Pinned Xtensa StackType_t is uint8_t. No generic four-byte-word assumption.
 static_assert(sizeof(StackType_t)==1,"Pinned ESP-IDF Xtensa stack units changed");
 r.loopAllocated=getArduinoLoopTaskStackSize();
 TaskHandle_t task=xTaskGetCurrentTaskHandle();
 if(task){r.loopFreeMinimum=uxTaskGetStackHighWaterMark(task)*sizeof(StackType_t);r.stackKnown=true;}
 return r;
}}
#endif
