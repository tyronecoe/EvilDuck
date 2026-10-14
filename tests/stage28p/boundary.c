// Fake controller/OS only. Dispatcher/class/claim source bodies come from pinned C.
#include "boundary.h"
#include "stage28p_platform.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
struct Boundary boundary;
static void capacity(bool ok){if(!ok){fputs("boundary evidence capacity violated\n",stderr);abort();}}
void boundary_reset(void){memset(&boundary,0,sizeof(boundary));}
void osal_task_delay(uint32_t ms){(void)ms;boundary.task_delays++;}
void osal_spin_init(osal_spinlock_t* s){s->depth=0;}
void osal_spin_lock(osal_spinlock_t* s,bool isr){(void)isr;s->depth++;boundary.spin_calls++;}
void osal_spin_unlock(osal_spinlock_t* s,bool isr){(void)isr;capacity(s->depth>0);s->depth--;if(boundary.in_unlock){void(*hook)(void)=boundary.in_unlock;boundary.in_unlock=NULL;hook();}}
osal_mutex_t osal_mutex_create(osal_mutex_def_t* d){d->locked=false;return d;}
bool osal_mutex_delete(osal_mutex_t m){capacity(m!=NULL);return true;}
bool osal_mutex_lock(osal_mutex_t m,uint32_t wait){boundary.mutex_calls++;boundary.last_wait=wait;if(wait==UINT32_MAX)boundary.mutex_wait_forever++;if(m->locked||boundary.fail_mutex){boundary.mutex_would_block++;return false;}m->locked=true;if(boundary.in_lock)boundary.in_lock();return true;}
bool osal_mutex_unlock(osal_mutex_t m){boundary.unlocks++;m->locked=false;return true;}
osal_queue_t osal_queue_create(osal_queue_def_t* q){capacity(q->capacity<=4&&q->item_size<=64);q->head=q->count=0;q->active=true;boundary.queue=q;return q;}
bool osal_queue_delete(osal_queue_t q){q->active=false;q->count=0;boundary.queue_deletes++;boundary.queue=NULL;return true;}
bool osal_queue_receive(osal_queue_t q,void* out,uint32_t wait){(void)wait;boundary.receive_calls++;if(!q->active||!q->count)return false;memcpy(out,q->data[q->head],q->item_size);q->head=(q->head+1)%q->capacity;q->count--;boundary.reads_this_pump++;return true;}
bool osal_queue_send(osal_queue_t q,const void* event,bool isr){
 capacity(boundary.event_count<EVIDENCE_CAPACITY);struct EventLog* e=&boundary.events[boundary.event_count++];const dcd_event_t* input=event;e->id=input->event_id;e->isr=isr;e->at=++boundary.order;e->queue_before=q?q->count:0;if(input->event_id==DCD_EVENT_XFER_COMPLETE){e->ep=input->xfer_complete.ep_addr;e->result=input->xfer_complete.result;e->length=input->xfer_complete.len;}
 if(!q){boundary.null_queue_sends++;return false;}
 if(!q->active||q->count==q->capacity){boundary.queue_full++;e->queue_after=q->count;return false;}
 memcpy(q->data[(q->head+q->count)%q->capacity],event,q->item_size);q->count++;e->queue_after=q->count;e->admitted=true;return true;
}
bool osal_queue_empty(osal_queue_t q){return q->count==0;}
uint32_t tusb_time_millis_api(void){return 0;}
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
void fixture_init(void){boundary_reset();platform_reset();tusb_rhport_init_t init={.role=TUSB_ROLE_DEVICE,.speed=TUSB_SPEED_FULL};capacity(tusb_rhport_init(0,&init));platform_bus_reset();fixture_dispatch();fixture_config(1);capacity(tud_mounted()&&tud_hid_n_ready(0));}
void fixture_finish(void){capacity(tud_deinit(0));}
size_t hid_submits(void){size_t count=0;for(size_t i=0;i<boundary.submission_count;i++)if(boundary.submissions[i].ep==0x81)count++;return count;}
void print_evidence(void){
 printf(",\"queue_count\":%zu,\"mounted\":%s,\"ready\":%s,\"busy\":%s,\"callback_count\":%zu,\"queue_full\":%u,\"mutex_wait_forever\":%u,\"callbacks\":[",boundary.queue?boundary.queue->count:0,tud_mounted()?"true":"false",tud_hid_n_ready(0)?"true":"false",usbd_edpt_busy(0,0x81)?"true":"false",boundary.callback_count,boundary.queue_full,boundary.mutex_wait_forever);
 for(size_t i=0;i<boundary.callback_count;i++){
  const struct Callback* c=&boundary.callbacks[i];
  printf("%s{\"instance\":%u,\"type\":%u,\"length\":%u,\"success\":%s,\"at\":%u,\"frame\":\"",i?",":"",c->instance,c->type,c->length,c->success?"true":"false",c->at);
  for(unsigned j=0;j<c->length&&j<64;j++)printf("%02X",c->bytes[j]);printf("\",\"after_hook\":\"");
  for(unsigned j=0;j<c->length&&j<64;j++)printf("%02X",c->after_hook[j]);printf("\"}");
 }
 printf("],\"events\":[");
 for(size_t i=0;i<boundary.event_count;i++){
  const struct EventLog* e=&boundary.events[i];
  printf("%s{\"id\":%u,\"ep\":%u,\"result\":%u,\"length\":%u,\"queue_before\":%zu,\"queue_after\":%zu,\"isr\":%s,\"admitted\":%s,\"at\":%u}",i?",":"",e->id,e->ep,e->result,e->length,e->queue_before,e->queue_after,e->isr?"true":"false",e->admitted?"true":"false",e->at);
 }
 printf("],\"null_queue_sends\":%u",boundary.null_queue_sends);
}
