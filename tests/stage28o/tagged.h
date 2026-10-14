#pragma once
/* Stage28O experimental native API. Not a deployed SDK/controller contract. */
#include <stdint.h>
#include <stdbool.h>
#ifndef CFG_TUD_TAGGED_NATIVE
#define CFG_TUD_TAGGED_NATIVE 0
#endif
#if CFG_TUD_TAGGED_NATIVE
typedef enum { TAG_NOT_SUBMITTED, TAG_SUBMITTED, TAG_AMBIGUOUS } tag_outcome_t;
typedef enum { TAG_OK, TAG_INVALID, TAG_PENDING, TAG_LOCK, TAG_BUSY, TAG_REFUSED,
 TAG_CONTRADICTION, TAG_CONTROLLER, TAG_SHAPE, TAG_LOSS, TAG_CANCELLED,
 TAG_EXHAUSTED, TAG_LIFETIME, TAG_LOCK_RELEASE } tag_fault_t;
typedef struct {
 uint64_t c,q; uint8_t instance,ep,protocol,id; uint16_t length; uint8_t frame[9];
 bool active,eligible,seen,success,retired,fenced; tag_outcome_t outcome;
} tag_transfer_t;
typedef struct {
 tag_transfer_t transfer; uint64_t c,last_q; unsigned queued,observing;
 unsigned rejected,observations,try_claims; bool leased,valid,receipt_pending,submitting;
 tag_fault_t first_fault,last_refusal;
} tag_state_t;
const tag_state_t* usbd_tagged_state(void);
bool tud_hid_tagged_bind(uint8_t instance,uint8_t id);
tag_outcome_t tud_hid_tagged_try(uint64_t c,uint8_t instance,uint8_t id,const void* raw,uint16_t length);
bool usbd_tagged_bind(uint8_t instance,uint8_t ep,uint8_t protocol,uint8_t id);
tag_outcome_t usbd_tagged_try(uint64_t c,uint8_t instance,uint8_t ep,uint8_t protocol,uint8_t id,const void* raw,uint16_t length);
bool usbd_tagged_leased(uint8_t ep);
void usbd_tagged_invalidate(tag_fault_t reason);
void usbd_tagged_cancel(void);
bool usbd_tagged_retire(uint64_t c,uint64_t q);
bool usbd_tagged_fence(uint64_t c,uint64_t q);
bool usbd_tagged_accepted(void);
bool usbd_tagged_release(void);
bool usbd_tagged_unbind(void);
bool usbd_tagged_take(tag_transfer_t* out);
bool usbd_tagged_observe(uint8_t instance,uint8_t ep,uint8_t result,uint32_t length);
void tud_hid_tagged_observer(const tag_transfer_t* transfer);
/* Native fake implements these proposed seams, NOT actual builder DCD. */
bool dcd_tagged_ready(void);
tag_outcome_t dcd_tagged_try(uint8_t port,const tag_transfer_t* transfer);
bool dcd_tagged_retired(uint64_t c,uint64_t q);
bool dcd_tagged_fenced(uint64_t c);
#endif
