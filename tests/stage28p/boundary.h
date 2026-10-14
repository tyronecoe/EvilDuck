#pragma once
#include "tusb.h"
#include "device/dcd.h"
#include "device/usbd_pvt.h"
#define EVIDENCE_CAPACITY 128
struct Submission {uint8_t ep;uint16_t length;uint8_t bytes[64];bool accepted;uint32_t entered_at,returned_at;const uint8_t* borrowed;};
struct Callback {uint8_t instance,type;uint16_t length;uint8_t bytes[64];const uint8_t* borrowed;uint8_t after_hook[64];uint32_t at;bool success;};
struct EventLog {uint8_t id,ep,result;uint32_t length;size_t queue_before,queue_after;bool isr,admitted;uint32_t at;};
struct Boundary {
 struct Submission submissions[EVIDENCE_CAPACITY];size_t submission_count;
 struct Callback callbacks[EVIDENCE_CAPACITY];size_t callback_count;
 struct EventLog events[EVIDENCE_CAPACITY];size_t event_count;
 uint32_t order;unsigned null_queue_sends;bool fail_deinit,controller_owned[8][2];
 unsigned mounts,unmounts,suspends,resumes,protocol_changes,close_all,deinits;
 unsigned mutex_calls,mutex_wait_forever,mutex_would_block,unlocks,queue_full,queue_deletes,task_delays;
 uint32_t last_wait;unsigned receive_calls,spin_calls;
 bool fail_submit,early_complete,early_dispatch,fail_mutex;
 bool opened[8][2];osal_queue_t queue;// All nonempty fixture receives deliver copied events.
 size_t reads_this_pump;
 void (*in_lock)(void);void (*in_unlock)(void);void (*in_callback)(void);
};
extern struct Boundary boundary;
void boundary_reset(void);
void fixture_init(void);
void fixture_config(uint8_t number);
void fixture_dispatch(void);
void fixture_finish(void);
void inject_complete(uint8_t ep,uint32_t length,xfer_result_t result);
void inject_bus(uint8_t id);
size_t hid_submits(void);
void print_evidence(void);
