#pragma once
#include "tusb.h"
#include "device/dcd.h"
#include "device/usbd_pvt.h"
#define EVIDENCE_CAPACITY 128
struct Submission {uint8_t ep;uint16_t length;uint8_t bytes[64];bool accepted;uint32_t entered_at,returned_at;const uint8_t* borrowed;};
struct Callback {uint8_t instance,type;uint16_t length;uint8_t bytes[64];const uint8_t* borrowed;uint8_t after_hook[64];uint32_t at;bool success;};
struct EventLog {uint64_t c,q;uint8_t instance,protocol,report_id;uint8_t id,ep,result;uint32_t length;size_t queue_before,queue_after;bool isr,admitted;uint32_t at;};
struct Boundary {
 struct Submission submissions[EVIDENCE_CAPACITY];size_t submission_count;
 struct Callback callbacks[EVIDENCE_CAPACITY];size_t callback_count;
 struct EventLog events[EVIDENCE_CAPACITY];size_t event_count;
 uint32_t order;unsigned null_queue_sends;bool fail_deinit,controller_owned[8][2];
 unsigned mounts,unmounts,suspends,resumes,protocol_changes,close_all,deinits;
 unsigned mutex_calls,mutex_wait_forever,mutex_would_block,unlocks,queue_full,queue_deletes,task_delays;
 uint32_t last_wait;unsigned receive_calls,spin_calls;
 bool fail_unlock;bool fail_submit,early_complete,early_dispatch,fail_mutex;
 bool opened[8][2];osal_queue_t queue;// All nonempty fixture receives deliver copied events.
 size_t reads_this_pump;
 void (*in_lock)(void);void (*in_callback)(void);
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

#if CFG_TUD_TAGGED_NATIVE
#include "device/tagged.h"
struct ControllerRecord { tag_transfer_t original; const tag_transfer_t* borrowed;
 bool retired,fenced,owned; unsigned emissions;uint32_t entered_at,returned_at; };
struct TaggedBoundary {
 struct ControllerRecord records[32]; unsigned count,attempts,callbacks;
 bool busy,refuse,ambiguous,early,dispatch,contradict,cancel_submit;
 bool fence_allow,retire_allow; unsigned cert_calls;
 tag_transfer_t last_callback;tag_transfer_t receipts[32];uint32_t receipt_at[32]; bool callback_stable;
 void (*hook)(void);void (*in_submit)(void);
};
extern struct TaggedBoundary tagged_boundary;
void emit_record(unsigned index,uint32_t length,uint8_t result);
void emit_tagged(const tag_transfer_t* original,uint32_t length,uint8_t result);
void certify(unsigned index);
void change_protocol(uint8_t protocol);
#endif
