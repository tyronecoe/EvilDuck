/* Experimental single-slot coordinator inside genuine usbd.c. No threads/ISR
 * safety claimed: the native port serializes these calls, including reentry. */
#if CFG_TUD_TAGGED_NATIVE
#ifndef TAG_ID_MAX
#define TAG_ID_MAX UINT64_MAX
#endif
#ifndef TAG_TEST_ID_START
#define TAG_TEST_ID_START 0
#endif
static tag_state_t _tag={.c=TAG_TEST_ID_START,.last_q=TAG_TEST_ID_START};
static void tag_fault(tag_fault_t f) {
 if (_tag.first_fault == TAG_OK) _tag.first_fault=f;
 _tag.valid=false; _tag.transfer.eligible=false;
}
const tag_state_t* usbd_tagged_state(void) { return &_tag; }
bool usbd_tagged_leased(uint8_t ep) { return _tag.leased && _tag.transfer.ep==ep; }
void usbd_tagged_invalidate(tag_fault_t reason) { if (_tag.leased) tag_fault(reason); }
void usbd_tagged_cancel(void) {
 _tag.valid=false;
 if (_tag.transfer.active) _tag.transfer.eligible=false;
 if (_tag.first_fault==TAG_OK) _tag.first_fault=TAG_CANCELLED;
}
bool usbd_tagged_bind(uint8_t instance,uint8_t ep,uint8_t protocol,uint8_t id) {
 if (_tag.leased || _tag.transfer.active || _tag.submitting || !tud_ready() || ep==0 ||
     tu_edpt_number(ep)>=CFG_TUD_ENDPPOINT_MAX || tu_edpt_dir(ep)!=TUSB_DIR_IN ||
     protocol!=HID_PROTOCOL_REPORT || id>1 || _tag.c==TAG_ID_MAX ||
     _usbd_dev.ep_status[tu_edpt_number(ep)][1].busy ||
     _usbd_dev.ep_status[tu_edpt_number(ep)][1].claimed) return false;
 _tag.c++; _tag.leased=true; _tag.valid=true; _tag.first_fault=TAG_OK;
 _tag.transfer=(tag_transfer_t){.ep=ep,.instance=instance,.protocol=protocol,.id=id};
 return true;
}
static bool tag_current(const dcd_event_t* e) {
 const tag_transfer_t* t=&_tag.transfer;
 return t->active && e->rhport==_usbd_rhport && e->xfer_complete.c==t->c &&
 e->xfer_complete.q==t->q && e->xfer_complete.ep_addr==t->ep;
}
static bool tag_validate(const dcd_event_t* e) {
 if (!tag_current(e) || _tag.transfer.seen) { _tag.rejected++; return false; }
 if (!_tag.valid || e->xfer_complete.instance!=_tag.transfer.instance ||
     e->xfer_complete.protocol!=_tag.transfer.protocol ||
     e->xfer_complete.report_id!=_tag.transfer.id ||
     e->xfer_complete.len!=_tag.transfer.length ||
     e->xfer_complete.result!=XFER_RESULT_SUCCESS) {
   _tag.rejected++; tag_fault(TAG_SHAPE); return false;
 }
 _tag.transfer.seen=true; return true;
}
tag_outcome_t usbd_tagged_try(uint64_t c,uint8_t instance,uint8_t ep,uint8_t protocol,uint8_t id,const void* raw,uint16_t length) {
 _tag.last_refusal=TAG_OK;
 if (_tag.transfer.active || _tag.submitting) { _tag.last_refusal=TAG_PENDING; return TAG_NOT_SUBMITTED; }
 if (!_tag.leased || !_tag.valid || c!=_tag.c || !tud_ready() ||
     instance!=_tag.transfer.instance || ep!=_tag.transfer.ep ||
     protocol!=_tag.transfer.protocol || id!=_tag.transfer.id || !raw || length!=8) {
   _tag.last_refusal=TAG_INVALID; return TAG_NOT_SUBMITTED;
 }
 if (_tag.last_q==TAG_ID_MAX) { _tag.last_refusal=TAG_EXHAUSTED; return TAG_NOT_SUBMITTED; }
 uint64_t q=++_tag.last_q; /* burn before any claim or lower ownership */
 if (!dcd_tagged_ready()) { _tag.last_refusal=TAG_BUSY; return TAG_NOT_SUBMITTED; }
 _tag.try_claims++; _tag.submitting=true;
 if (!osal_mutex_lock(_usbd_mutex,0)) { _tag.submitting=false; _tag.last_refusal=TAG_LOCK; return TAG_NOT_SUBMITTED; }
 if (!_tag.valid) {
   if (!osal_mutex_unlock(_usbd_mutex)) tag_fault(TAG_LOCK_RELEASE);
   _tag.submitting=false; _tag.last_refusal=TAG_INVALID; return TAG_NOT_SUBMITTED;
 }
 tu_edpt_state_t* s=&_usbd_dev.ep_status[tu_edpt_number(ep)][1];
 if (s->busy || s->claimed) { if (!osal_mutex_unlock(_usbd_mutex)) tag_fault(TAG_LOCK_RELEASE); _tag.submitting=false; _tag.last_refusal=TAG_BUSY; return TAG_NOT_SUBMITTED; }
 s->claimed=1; s->busy=1;
 _tag.transfer=(tag_transfer_t){.c=c,.q=q,.instance=instance,.ep=ep,.protocol=protocol,.id=id,
   .length=(uint16_t)(8+(id!=0)),.active=true,.eligible=true,.outcome=TAG_AMBIGUOUS};
 if (id) _tag.transfer.frame[0]=id;
 memcpy(_tag.transfer.frame+(id!=0),raw,8);
 if (!osal_mutex_unlock(_usbd_mutex)) { _tag.submitting=false; tag_fault(TAG_LOCK_RELEASE); return TAG_AMBIGUOUS; }
 _tag.submitting=true;
 tag_outcome_t result=dcd_tagged_try(_usbd_rhport,&_tag.transfer);
 _tag.submitting=false;
 if (result==TAG_NOT_SUBMITTED) {
   /* A queued event is contradictory evidence even if not dispatched yet. */
   if (_tag.transfer.seen || _tag.queued || _tag.receipt_pending) {
     tag_fault(TAG_CONTRADICTION); result=TAG_AMBIGUOUS;
   } else {
     s->busy=0; s->claimed=0; _tag.transfer.active=false;
     _tag.transfer.eligible=false; _tag.last_refusal=TAG_REFUSED;
   }
 } else if (result!=TAG_SUBMITTED) { tag_fault(TAG_CONTROLLER); result=TAG_AMBIGUOUS; }
 _tag.transfer.outcome=result;
 return result;
}
bool usbd_tagged_observe(uint8_t instance,uint8_t ep,uint8_t result,uint32_t length) {
 if (!_tag.transfer.active || !_tag.transfer.seen || instance!=_tag.transfer.instance ||
     ep!=_tag.transfer.ep || result!=XFER_RESULT_SUCCESS || length!=_tag.transfer.length) return false;
 if (_tag.receipt_pending || _tag.observing) { tag_fault(TAG_LOSS); return false; }
 _tag.transfer.success=true; _tag.receipt_pending=true; _tag.observations++;
 /* Snapshot on stack; current slot cannot be reused while callback executes. */
 tag_transfer_t snapshot=_tag.transfer;
 _tag.observing++;
 tud_hid_tagged_observer(&snapshot);
 _tag.observing--;
 return true;
}
bool usbd_tagged_take(tag_transfer_t* out) {
 if (!out || !_tag.receipt_pending || _tag.observing) return false;
 *out=_tag.transfer; _tag.receipt_pending=false; return true;
}
bool usbd_tagged_retire(uint64_t c,uint64_t q) {
 if (!_tag.transfer.active || c!=_tag.transfer.c || q!=_tag.transfer.q ||
     !dcd_tagged_retired(c,q)) return false;
 _tag.transfer.retired=true; return true;
}
bool usbd_tagged_fence(uint64_t c,uint64_t q) {
 if (!_tag.transfer.active || c!=_tag.transfer.c || q!=_tag.transfer.q ||
     !_tag.transfer.retired || _tag.queued || _tag.observing || _tag.receipt_pending ||
     !dcd_tagged_fenced(c)) return false;
 if (_tag.submitting) return false;
 _tag.transfer.fenced=true; return true;
}
bool usbd_tagged_accepted(void) {
 const tag_transfer_t* t=&_tag.transfer;
 return t->active && t->success && t->outcome==TAG_SUBMITTED && t->retired &&
 t->fenced && tud_ready() && !_tag.queued && !_tag.observing && !_tag.receipt_pending && !_tag.submitting && t->eligible && _tag.valid && _tag.first_fault==TAG_OK;
}
bool usbd_tagged_release(void) {
 if (!_tag.transfer.active || !_tag.transfer.retired || !_tag.transfer.fenced ||
     _tag.queued || _tag.observing || _tag.receipt_pending || _tag.submitting) return false;
 _usbd_dev.ep_status[tu_edpt_number(_tag.transfer.ep)][1].busy=0;
 _usbd_dev.ep_status[tu_edpt_number(_tag.transfer.ep)][1].claimed=0;
 _tag.transfer.active=false; return true;
}
bool usbd_tagged_unbind(void) {
 if (!_tag.leased || _tag.transfer.active || _tag.submitting || _tag.first_fault==TAG_LOCK_RELEASE || _tag.queued || _tag.observing ||
     _tag.receipt_pending || !dcd_tagged_fenced(_tag.c)) return false;
 _tag.leased=false; _tag.valid=false; return true;
}
#endif
