#pragma once
// RAM-only structural mock of the pinned TinyUSB event API. Not a USB driver.
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
typedef enum {DCD_EVENT_INVALID=0,DCD_EVENT_BUS_RESET=1,DCD_EVENT_UNPLUGGED=2,DCD_EVENT_SOF=3,DCD_EVENT_SUSPEND=4,DCD_EVENT_RESUME=5,DCD_EVENT_SETUP_RECEIVED=6,DCD_EVENT_XFER_COMPLETE=7,USBD_EVENT_FUNC_CALL=8,DCD_EVENT_COUNT=9} dcd_eventid_t;
typedef enum {TUSB_SPEED_FULL=0,TUSB_SPEED_LOW=1,TUSB_SPEED_HIGH=2,TUSB_SPEED_AUTO=0xaa,TUSB_SPEED_INVALID=0xff} tusb_speed_t;
typedef struct {uint8_t bytes[8];} tusb_control_request_t;
typedef struct __attribute__((aligned(4))) {
 uint8_t rhport,event_id;
 union {
  struct {tusb_speed_t speed;} bus_reset;
  struct {uint32_t frame_count;} sof;
  tusb_control_request_t setup_received;
  struct {uint8_t ep_addr,result;uint32_t len;} xfer_complete;
  struct {void (*func)(void*);void* param;} func_call;
 };
} dcd_event_t;
void dcd_event_handler(dcd_event_t const*,bool);
void __wrap_dcd_event_handler(dcd_event_t const*,bool);
void __real_dcd_event_handler(dcd_event_t const*,bool);
void evilduck_mock_dcd_reset();
uint32_t evilduck_mock_dcd_calls();
const dcd_event_t* evilduck_mock_dcd_last();
bool evilduck_mock_dcd_last_isr();
#ifdef __cplusplus
}
#endif
