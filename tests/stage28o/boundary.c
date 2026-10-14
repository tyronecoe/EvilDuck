// Fake controller/OS only. Dispatcher/class/claim source bodies come from pinned C.
#include "boundary.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <inttypes.h>
struct Boundary boundary;
static void capacity(bool ok){if(!ok){fputs("boundary evidence capacity violated\n",stderr);abort();}}
void boundary_reset(void){memset(&boundary,0,sizeof(boundary));}
void osal_task_delay(uint32_t ms){(void)ms;boundary.task_delays++;}
void osal_spin_init(osal_spinlock_t* s){s->depth=0;}
void osal_spin_lock(osal_spinlock_t* s,bool isr){(void)isr;s->depth++;boundary.spin_calls++;}
void osal_spin_unlock(osal_spinlock_t* s,bool isr){(void)isr;capacity(s->depth>0);s->depth--;}
osal_mutex_t osal_mutex_create(osal_mutex_def_t* d){d->locked=false;return d;}
bool osal_mutex_delete(osal_mutex_t m){capacity(m!=NULL);return true;}
bool osal_mutex_lock(osal_mutex_t m,uint32_t wait){boundary.mutex_calls++;boundary.last_wait=wait;if(wait==UINT32_MAX)boundary.mutex_wait_forever++;if(m->locked||boundary.fail_mutex){boundary.mutex_would_block++;return false;}m->locked=true;if(boundary.in_lock)boundary.in_lock();return true;}
bool osal_mutex_unlock(osal_mutex_t m){boundary.unlocks++;if(boundary.fail_unlock)return false;m->locked=false;return true;}
osal_queue_t osal_queue_create(osal_queue_def_t* q){capacity(q->capacity<=4&&q->item_size<=64);q->head=q->count=0;q->active=true;boundary.queue=q;return q;}
bool osal_queue_delete(osal_queue_t q){q->active=false;q->count=0;boundary.queue_deletes++;boundary.queue=NULL;return true;}
bool osal_queue_receive(osal_queue_t q,void* out,uint32_t wait){(void)wait;boundary.receive_calls++;if(!q->active||!q->count)return false;memcpy(out,q->data[q->head],q->item_size);q->head=(q->head+1)%q->capacity;q->count--;boundary.reads_this_pump++;return true;}
bool osal_queue_send(osal_queue_t q,const void* event,bool isr){
 capacity(boundary.event_count<EVIDENCE_CAPACITY);struct EventLog* e=&boundary.events[boundary.event_count++];const dcd_event_t* input=event;e->id=input->event_id;e->isr=isr;e->at=++boundary.order;e->queue_before=q?q->count:0;if(input->event_id==DCD_EVENT_XFER_COMPLETE){e->ep=input->xfer_complete.ep_addr;e->result=input->xfer_complete.result;e->length=input->xfer_complete.len;
#if CFG_TUD_TAGGED_NATIVE
 e->c=input->xfer_complete.c;e->q=input->xfer_complete.q;e->instance=input->xfer_complete.instance;
 e->protocol=input->xfer_complete.protocol;e->report_id=input->xfer_complete.report_id;
#endif
 }
 if(!q){boundary.null_queue_sends++;return false;}
 if(!q->active||q->count==q->capacity){boundary.queue_full++;e->queue_after=q->count;return false;}
 memcpy(q->data[(q->head+q->count)%q->capacity],event,q->item_size);q->count++;e->queue_after=q->count;e->admitted=true;return true;
}
bool osal_queue_empty(osal_queue_t q){return q->count==0;}
uint32_t tusb_time_millis_api(void){return 0;}
bool dcd_init(uint8_t port,const tusb_rhport_init_t* init){(void)port;(void)init;return true;}
bool dcd_deinit(uint8_t port){(void)port;boundary.deinits++;if(boundary.fail_deinit)return false;memset(boundary.controller_owned,0,sizeof(boundary.controller_owned));return true;}
void dcd_int_handler(uint8_t p){(void)p;}
bool dcd_edpt_iso_alloc(uint8_t p,uint8_t ep,uint16_t size){(void)p;(void)ep;(void)size;return false;}
bool dcd_edpt_iso_activate(uint8_t p,const tusb_desc_endpoint_t* d){(void)p;(void)d;return false;}
void dcd_int_enable(uint8_t p){(void)p;}void dcd_int_disable(uint8_t p){(void)p;}
void dcd_connect(uint8_t p){(void)p;}void dcd_disconnect(uint8_t p){(void)p;}
void dcd_remote_wakeup(uint8_t p){(void)p;}void dcd_sof_enable(uint8_t p,bool b){(void)p;(void)b;}
void dcd_set_address(uint8_t p,uint8_t address){(void)p;(void)address;}
bool dcd_edpt_open(uint8_t p,const tusb_desc_endpoint_t* d){(void)p;boundary.opened[tu_edpt_number(d->bEndpointAddress)][tu_edpt_dir(d->bEndpointAddress)]=true;return true;}
void dcd_edpt_close_all(uint8_t p){(void)p;memset(boundary.opened,0,sizeof(boundary.opened));memset(boundary.controller_owned,0,sizeof(boundary.controller_owned));boundary.close_all++;}
void dcd_edpt_close(uint8_t p,uint8_t ep){(void)p;boundary.opened[tu_edpt_number(ep)][tu_edpt_dir(ep)]=false;}
void dcd_edpt_stall(uint8_t p,uint8_t ep){(void)p;(void)ep;}void dcd_edpt_clear_stall(uint8_t p,uint8_t ep){(void)p;(void)ep;}
bool dcd_edpt_xfer(uint8_t p,uint8_t ep,uint8_t* buffer,uint16_t bytes){
 (void)p;capacity(boundary.submission_count<EVIDENCE_CAPACITY&&bytes<=64);struct Submission* s=&boundary.submissions[boundary.submission_count++];s->entered_at=++boundary.order;s->ep=ep;s->length=bytes;s->borrowed=buffer;if(bytes)memcpy(s->bytes,buffer,bytes);s->accepted=!boundary.fail_submit;
 if(s->accepted)boundary.controller_owned[tu_edpt_number(ep)][tu_edpt_dir(ep)]=true;
 if(s->accepted&&ep==0x81&&boundary.early_complete){inject_complete(ep,bytes,XFER_RESULT_SUCCESS);if(boundary.early_dispatch)fixture_dispatch();}
 s->returned_at=++boundary.order;return s->accepted;
}
static uint8_t const report_descriptor[]={TUD_HID_REPORT_DESC_KEYBOARD(HID_REPORT_ID(1))};
static uint8_t const config_descriptor[]={TUD_CONFIG_DESCRIPTOR(1,1,0,TUD_CONFIG_DESC_LEN+TUD_HID_DESC_LEN,0,100),TUD_HID_DESCRIPTOR(0,0,HID_ITF_PROTOCOL_KEYBOARD,sizeof(report_descriptor),0x81,64,1)};
uint8_t const* tud_descriptor_configuration_cb(uint8_t index){(void)index;return config_descriptor;}
uint8_t const* tud_descriptor_device_cb(void){static tusb_desc_device_t const d={.bLength=sizeof(d),.bDescriptorType=TUSB_DESC_DEVICE,.bcdUSB=0x0200,.bMaxPacketSize0=64,.bNumConfigurations=1};return (uint8_t const*)&d;}
uint16_t const* tud_descriptor_string_cb(uint8_t index,uint16_t language){(void)index;(void)language;return NULL;}
uint8_t const* tud_hid_descriptor_report_cb(uint8_t instance){(void)instance;return report_descriptor;}
uint16_t tud_hid_get_report_cb(uint8_t i,uint8_t id,hid_report_type_t t,uint8_t* b,uint16_t n){(void)i;(void)id;(void)t;(void)b;(void)n;return 0;}
void tud_hid_set_report_cb(uint8_t i,uint8_t id,hid_report_type_t t,uint8_t const* b,uint16_t n){(void)i;(void)id;(void)t;(void)b;(void)n;}
void tud_mount_cb(void){boundary.mounts++;}void tud_umount_cb(void){boundary.unmounts++;}
void tud_suspend_cb(bool enabled){(void)enabled;boundary.suspends++;}void tud_resume_cb(void){boundary.resumes++;}
void tud_hid_set_protocol_cb(uint8_t i,uint8_t protocol){(void)i;(void)protocol;boundary.protocol_changes++;}
static void callback(uint8_t instance,uint8_t type,uint8_t const* buffer,uint16_t length,bool success){capacity(boundary.callback_count<EVIDENCE_CAPACITY);struct Callback* c=&boundary.callbacks[boundary.callback_count++];c->at=++boundary.order;c->instance=instance;c->type=type;c->length=length;c->borrowed=buffer;c->success=success;if(length)memcpy(c->bytes,buffer,length>64?64:length);if(boundary.in_callback)boundary.in_callback();if(length)memcpy(c->after_hook,buffer,length>64?64:length);}
void tud_hid_report_complete_cb(uint8_t i,uint8_t const* b,uint16_t n){callback(i,HID_REPORT_TYPE_INPUT,b,n,true);}
void tud_hid_report_failed_cb(uint8_t i,hid_report_type_t t,uint8_t const* b,uint16_t n){callback(i,t,b,n,false);}
void fixture_dispatch(void){boundary.reads_this_pump=0;tud_task_ext(0,false);}
void inject_complete(uint8_t ep,uint32_t bytes,xfer_result_t result){dcd_event_xfer_complete(0,ep,bytes,(uint8_t)result,true);}
void inject_bus(uint8_t id){dcd_event_t e={.rhport=0,.event_id=id};if(id==DCD_EVENT_BUS_RESET)e.bus_reset.speed=TUSB_SPEED_FULL;dcd_event_handler(&e,true);}
void fixture_config(uint8_t number){uint8_t setup[8]={0,TUSB_REQ_SET_CONFIGURATION,number,0,0,0,0,0};dcd_event_setup_received(0,setup,true);fixture_dispatch();inject_complete(0x80,0,XFER_RESULT_SUCCESS);fixture_dispatch();}
void fixture_init(void){boundary_reset();tusb_rhport_init_t init={.role=TUSB_ROLE_DEVICE,.speed=TUSB_SPEED_FULL};capacity(tusb_rhport_init(0,&init));inject_bus(DCD_EVENT_BUS_RESET);fixture_dispatch();fixture_config(1);capacity(tud_mounted()&&tud_hid_n_ready(0));}
void fixture_finish(void){capacity(tud_deinit(0));}
size_t hid_submits(void){size_t count=0;for(size_t i=0;i<boundary.submission_count;i++)if(boundary.submissions[i].ep==0x81)count++;return count;}
void print_evidence(void){
 printf(",\"queue_count\":%zu,\"mounted\":%s,\"ready\":%s,\"busy\":%s,\"hid_submits\":%zu,\"callback_count\":%zu,\"wait_forever_entries\":%u,\"would_block_entries\":%u,\"queue_full\":%u,\"mounts\":%u,\"unmounts\":%u,\"suspends\":%u,\"resumes\":%u,\"protocol_changes\":%u,\"close_all\":%u,\"submissions\":[",boundary.queue?boundary.queue->count:0,tud_mounted()?"true":"false",tud_hid_n_ready(0)?"true":"false",usbd_edpt_busy(0,0x81)?"true":"false",hid_submits(),boundary.callback_count,boundary.mutex_wait_forever,boundary.mutex_would_block,boundary.queue_full,boundary.mounts,boundary.unmounts,boundary.suspends,boundary.resumes,boundary.protocol_changes,boundary.close_all);
 for(size_t i=0;i<boundary.submission_count;i++){struct Submission* s=&boundary.submissions[i];printf("%s{\"ep\":%u,\"length\":%u,\"accepted\":%s,\"frame\":\"",i?",":"",s->ep,s->length,s->accepted?"true":"false");for(unsigned j=0;j<s->length;j++)printf("%02X",s->bytes[j]);printf("\",\"entered_at\":%u,\"returned_at\":%u}",s->entered_at,s->returned_at);}printf("],\"callbacks\":[");
 for(size_t i=0;i<boundary.callback_count;i++){struct Callback* c=&boundary.callbacks[i];printf("%s{\"instance\":%u,\"type\":%u,\"length\":%u,\"success\":%s,\"frame\":\"",i?",":"",c->instance,c->type,c->length,c->success?"true":"false");for(unsigned j=0;j<c->length&&j<64;j++)printf("%02X",c->bytes[j]);printf("\",\"submission_identity_exposed\":false,\"at\":%u,\"after_hook\":\"",c->at);for(unsigned j=0;j<c->length&&j<64;j++)printf("%02X",c->after_hook[j]);printf("\"}");}printf("],\"events\":[");
 for(size_t i=0;i<boundary.event_count;i++){struct EventLog* e=&boundary.events[i];printf("%s{\"id\":%u,\"ep\":%u,\"result\":%u,\"length\":%u,\"queue_before\":%zu,\"queue_after\":%zu,\"isr\":%s,\"admitted\":%s,\"at\":%u",i?",":"",e->id,e->ep,e->result,e->length,e->queue_before,e->queue_after,e->isr?"true":"false",e->admitted?"true":"false",e->at);
#if CFG_TUD_TAGGED_NATIVE
 // Remove closing object emitted above, by replacing its format below.
 printf(",\"c\":%"PRIu64",\"q\":%"PRIu64",\"instance\":%u,\"protocol\":%u,\"report_id\":%u}",e->c,e->q,e->instance,e->protocol,e->report_id);
#else
 printf("}");
#endif
 }printf("],\"null_queue_sends\":%u,\"controller_owned_fixture\":%s",boundary.null_queue_sends,boundary.controller_owned[1][1]?"true":"false");
}

#if CFG_TUD_TAGGED_NATIVE
struct TaggedBoundary tagged_boundary;
bool dcd_tagged_ready(void) { return !tagged_boundary.busy; }
tag_outcome_t dcd_tagged_try(uint8_t port,const tag_transfer_t* t) {
 (void)port; tagged_boundary.attempts++;
 if (tagged_boundary.refuse && !tagged_boundary.contradict) return TAG_NOT_SUBMITTED;
 capacity(tagged_boundary.count<32);
 struct ControllerRecord* r=&tagged_boundary.records[tagged_boundary.count++];
 r->original=*t; r->borrowed=t; r->owned=true;r->entered_at=++boundary.order;
 if (tagged_boundary.in_submit) tagged_boundary.in_submit();
 if (tagged_boundary.cancel_submit) usbd_tagged_cancel();
 if (tagged_boundary.early || tagged_boundary.contradict) {
  emit_record(tagged_boundary.count-1,t->length,XFER_RESULT_SUCCESS);
  if (tagged_boundary.dispatch) fixture_dispatch();
 }
 r->returned_at=++boundary.order;
 if (tagged_boundary.contradict) return TAG_NOT_SUBMITTED;
 return tagged_boundary.ambiguous ? TAG_AMBIGUOUS : TAG_SUBMITTED;
}
void emit_tagged(const tag_transfer_t* t,uint32_t length,uint8_t result) {
 dcd_event_t e={.rhport=0,.event_id=DCD_EVENT_XFER_COMPLETE};
 e.xfer_complete.ep_addr=t->ep; e.xfer_complete.len=length; e.xfer_complete.result=result;
 e.xfer_complete.c=t->c; e.xfer_complete.q=t->q;
 e.xfer_complete.instance=t->instance; e.xfer_complete.protocol=t->protocol; e.xfer_complete.report_id=t->id;
 dcd_event_handler(&e,true);
}
void emit_record(unsigned index,uint32_t length,uint8_t result) {
 capacity(index<tagged_boundary.count);
 struct ControllerRecord* r=&tagged_boundary.records[index];
 r->emissions++; emit_tagged(&r->original,length,result);
}
void certify(unsigned index) {
 capacity(index<tagged_boundary.count);
 struct ControllerRecord* r=&tagged_boundary.records[index];
 r->retired=true; r->owned=false; r->fenced=true;
}
bool dcd_tagged_retired(uint64_t c,uint64_t q) {
 tagged_boundary.cert_calls++;
 for(unsigned i=0;i<tagged_boundary.count;i++) {
  struct ControllerRecord* r=&tagged_boundary.records[i];
  if(r->original.c==c && r->original.q==q) return r->retired && tagged_boundary.retire_allow;
 } return false;
}
bool dcd_tagged_fenced(uint64_t c) {
 if(!tagged_boundary.fence_allow) return false;
 for(unsigned i=0;i<tagged_boundary.count;i++) {
  struct ControllerRecord* r=&tagged_boundary.records[i];
  if(r->original.c==c && !r->fenced) return false;
 } return true;
}
void tud_hid_tagged_observer(const tag_transfer_t* t) {
 capacity(tagged_boundary.callbacks<32);tagged_boundary.receipts[tagged_boundary.callbacks]=*t;
 tagged_boundary.receipt_at[tagged_boundary.callbacks]=++boundary.order;
 tagged_boundary.callbacks++; tagged_boundary.last_callback=*t;
 if(tagged_boundary.hook) tagged_boundary.hook();
 tagged_boundary.callback_stable=memcmp(t,&tagged_boundary.last_callback,sizeof(*t))==0;
}
void change_protocol(uint8_t protocol) {
 uint8_t setup[8]={0x21,HID_REQ_CONTROL_SET_PROTOCOL,protocol,0,0,0,0,0};
 dcd_event_setup_received(0,setup,true);fixture_dispatch();
 inject_complete(0x80,0,XFER_RESULT_SUCCESS);fixture_dispatch();
}
#endif
