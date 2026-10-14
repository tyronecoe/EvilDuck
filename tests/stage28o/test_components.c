// All device/queue/class calls resolve to patched genuine vendor translation units.
#include "boundary.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <inttypes.h>
static unsigned assertions;
#define CHECK(v) do { assertions++; if(!(v)){fprintf(stderr,"FAIL line=%d: %s\n",__LINE__,#v);exit(1);} }while(0)
static const uint8_t A[8]={0,0,4,0,0,0,0,0},B[8]={2,0,5,0,0,0,0,0},Z[8]={0};
static const tag_state_t* state(void){return usbd_tagged_state();}
static void bind_id(uint8_t id){CHECK(tud_hid_tagged_bind(0,id));}
static void bind(void){bind_id(1);}
static tag_outcome_t send(const uint8_t* raw){return tud_hid_tagged_try(state()->c,0,state()->transfer.id,raw,8);}
static void start(const uint8_t* raw){CHECK(send(raw)==TAG_SUBMITTED);CHECK(state()->transfer.active);}
static void complete(unsigned i){emit_record(i,tagged_boundary.records[i].original.length,XFER_RESULT_SUCCESS);fixture_dispatch();}
static void take(void){tag_transfer_t receipt;CHECK(usbd_tagged_take(&receipt));CHECK(receipt.c==state()->transfer.c && receipt.q==state()->transfer.q);CHECK(receipt.success);}
static void retire(unsigned i){tag_transfer_t t=tagged_boundary.records[i].original;certify(i);CHECK(usbd_tagged_retire(t.c,t.q));CHECK(usbd_tagged_fence(t.c,t.q));}
static void finish_success(unsigned i){complete(i);take();retire(i);CHECK(usbd_tagged_accepted());CHECK(usbd_tagged_release());}
static void hook(void){
 uint64_t q=state()->last_q;unsigned calls=tagged_boundary.attempts;
 CHECK(send(B)==TAG_NOT_SUBMITTED);CHECK(state()->last_q==q);CHECK(tagged_boundary.attempts==calls);
 CHECK(!tud_hid_n_report(0,1,B,8));CHECK(!usbd_tagged_release());
 CHECK(!usbd_tagged_fence(state()->transfer.c,state()->transfer.q));
 tag_transfer_t receipt;CHECK(!usbd_tagged_take(&receipt));
}
static void cancel_lock_hook(void){usbd_tagged_cancel();}
static void lock_hook(void){
 uint64_t q=state()->last_q;CHECK(send(B)==TAG_NOT_SUBMITTED);
 CHECK(state()->last_q==q);CHECK(!usbd_tagged_unbind());
}
static void submit_hook(void){
 certify(0);CHECK(usbd_tagged_retire(state()->transfer.c,state()->transfer.q));
 CHECK(!usbd_tagged_fence(state()->transfer.c,state()->transfer.q));
 CHECK(!usbd_tagged_release());CHECK(send(B)==TAG_NOT_SUBMITTED);
}
static void rebind_after_loss(unsigned i){
 tag_transfer_t t=tagged_boundary.records[i].original;
 fixture_dispatch();certify(i);CHECK(usbd_tagged_retire(t.c,t.q));
 CHECK(usbd_tagged_fence(t.c,t.q));CHECK(!usbd_tagged_accepted());
 CHECK(usbd_tagged_release());CHECK(usbd_tagged_unbind());fixture_config(1);bind();
}
static void run(unsigned n){
 switch(n){
 case 1:
  bind();start(A);CHECK(tagged_boundary.count==1);CHECK(state()->transfer.length==9);
  CHECK(state()->transfer.frame[0]==1);CHECK(!memcmp(state()->transfer.frame+1,A,8));
  CHECK(boundary.last_wait==0 && boundary.mutex_wait_forever==0);
  complete(0);CHECK(tagged_boundary.callbacks==1);CHECK(!usbd_tagged_accepted());
  CHECK(!usbd_tagged_release());CHECK(send(B)==TAG_NOT_SUBMITTED);take();
  CHECK(!usbd_tagged_retire(state()->transfer.c,state()->transfer.q));retire(0);
  CHECK(usbd_tagged_accepted());CHECK(usbd_tagged_release());break;
 case 2:
  bind_id(0);start(A);CHECK(state()->transfer.length==8);CHECK(!memcmp(state()->transfer.frame,A,8));finish_success(0);break;
 case 3:{
  bind();tag_transfer_t old=state()->transfer;unsigned locks=boundary.mutex_calls;
  CHECK(tud_hid_tagged_try(state()->c,0,1,A,65)==TAG_NOT_SUBMITTED);
  CHECK(tud_hid_tagged_try(state()->c,1,1,A,8)==TAG_NOT_SUBMITTED);
  CHECK(tud_hid_tagged_try(state()->c,0,2,A,8)==TAG_NOT_SUBMITTED);
  CHECK(tud_hid_tagged_try(state()->c,0,1,NULL,8)==TAG_NOT_SUBMITTED);
  CHECK(tud_hid_tagged_try(state()->c+1,0,1,A,8)==TAG_NOT_SUBMITTED);
  CHECK(!memcmp(&old,&state()->transfer,sizeof(old)));CHECK(boundary.mutex_calls==locks);
  CHECK(tagged_boundary.count==0);start(A);finish_success(0);break;}
 case 4:{
  bind();unsigned unlocks=boundary.unlocks;boundary.fail_mutex=true;
  CHECK(send(A)==TAG_NOT_SUBMITTED);CHECK(state()->last_refusal==TAG_LOCK);
  CHECK(boundary.last_wait==0 && boundary.unlocks==unlocks);CHECK(tagged_boundary.count==0);
  boundary.fail_mutex=false;tagged_boundary.busy=true;
  CHECK(send(A)==TAG_NOT_SUBMITTED);CHECK(state()->last_refusal==TAG_BUSY);
  CHECK(!state()->transfer.active && !usbd_edpt_busy(0,0x81));
  tagged_boundary.busy=false;start(A);finish_success(0);break;}
 case 5:{
  bind();tagged_boundary.refuse=true;CHECK(send(A)==TAG_NOT_SUBMITTED);
  CHECK(state()->last_refusal==TAG_REFUSED);uint64_t q=state()->last_q;
  CHECK(!state()->transfer.active && !usbd_edpt_busy(0,0x81));CHECK(tagged_boundary.count==0);
  tagged_boundary.refuse=false;start(A);CHECK(state()->last_q==q+1);finish_success(0);break;}
 case 6:
  bind();tagged_boundary.early=true;tagged_boundary.dispatch=true;start(A);
  CHECK(state()->transfer.success && tagged_boundary.callbacks==1);take();retire(0);CHECK(usbd_tagged_accepted());break;
 case 7:
  bind();tagged_boundary.contradict=true;tagged_boundary.dispatch=true;
  CHECK(send(A)==TAG_AMBIGUOUS);CHECK(state()->first_fault==TAG_CONTRADICTION);
  CHECK(state()->transfer.active && tagged_boundary.count==1);CHECK(send(A)==TAG_NOT_SUBMITTED);
  take();retire(0);CHECK(!usbd_tagged_accepted());break;
 case 8:
  bind();start(A);for(unsigned i=0;i<100;i++){CHECK(!usbd_tagged_accepted());CHECK(send(A)==TAG_NOT_SUBMITTED);}
  CHECK(tagged_boundary.attempts==1 && state()->last_q==1);finish_success(0);break;
 case 9:
  bind();start(A);finish_success(0);start(A);CHECK(tagged_boundary.records[0].original.q!=state()->transfer.q);
  CHECK(!memcmp(tagged_boundary.records[0].original.frame,state()->transfer.frame,9));finish_success(1);break;
 case 10:
  bind();start(A);complete(0);emit_record(0,9,XFER_RESULT_SUCCESS);fixture_dispatch();
  CHECK(tagged_boundary.callbacks==1 && state()->rejected==1);take();retire(0);CHECK(usbd_tagged_accepted());break;
 case 11:
  bind();start(A);finish_success(0);start(B);emit_record(0,9,XFER_RESULT_SUCCESS);fixture_dispatch();
  CHECK(usbd_edpt_busy(0,0x81));CHECK(tagged_boundary.callbacks==1);CHECK(state()->rejected==1);
  CHECK(!memcmp(state()->transfer.frame+1,B,8));finish_success(1);break;
 case 12:
 case 13:
  bind();start(A);emit_record(0,9,XFER_RESULT_SUCCESS);
  inject_bus(n==12?DCD_EVENT_BUS_RESET:DCD_EVENT_UNPLUGGED);CHECK(!state()->valid);
  rebind_after_loss(0);start(B);emit_record(0,9,XFER_RESULT_SUCCESS);fixture_dispatch();
  CHECK(usbd_edpt_busy(0,0x81));CHECK(tagged_boundary.callbacks==0);finish_success(1);break;
 case 14:
  bind();start(A);change_protocol(0);CHECK(!state()->valid);
  CHECK(send(B)==TAG_NOT_SUBMITTED);complete(0);CHECK(tagged_boundary.callbacks==0);
  retire(0);CHECK(!usbd_tagged_accepted());break;
 case 15:{
  bind();start(A);tag_transfer_t bad=state()->transfer;
  bad.c++;emit_tagged(&bad,9,XFER_RESULT_SUCCESS);bad=state()->transfer;bad.q++;
  emit_tagged(&bad,9,XFER_RESULT_SUCCESS);inject_complete(0x81,9,XFER_RESULT_SUCCESS);fixture_dispatch();
  CHECK(usbd_edpt_busy(0,0x81));CHECK(state()->rejected==3);CHECK(!state()->transfer.seen);finish_success(0);break;}
 case 16:{
  bind();start(A);tag_transfer_t bad=state()->transfer;bad.ep=0x82;
  emit_tagged(&bad,9,XFER_RESULT_SUCCESS);fixture_dispatch();CHECK(usbd_edpt_busy(0,0x81));CHECK(state()->rejected==1);finish_success(0);break;}
 case 17:{
  bind();start(A);tag_transfer_t bad=state()->transfer;bad.instance=1;
  emit_tagged(&bad,9,XFER_RESULT_SUCCESS);fixture_dispatch();CHECK(state()->first_fault==TAG_SHAPE);
  CHECK(usbd_edpt_busy(0,0x81));bad=state()->transfer;bad.id=0;emit_tagged(&bad,9,XFER_RESULT_SUCCESS);
  bad=state()->transfer;bad.protocol=0;emit_tagged(&bad,9,XFER_RESULT_SUCCESS);fixture_dispatch();
  CHECK(tagged_boundary.callbacks==0);retire(0);CHECK(!usbd_tagged_accepted());break;}
 case 18:
 case 19:
  bind();start(A);emit_record(0,n==18?4:70,XFER_RESULT_SUCCESS);fixture_dispatch();
  CHECK(state()->first_fault==TAG_SHAPE && usbd_edpt_busy(0,0x81));CHECK(tagged_boundary.callbacks==0);retire(0);CHECK(!usbd_tagged_accepted());break;
 case 20:
  bind();start(A);tagged_boundary.hook=hook;complete(0);
  CHECK(tagged_boundary.callback_stable);CHECK(!memcmp(tagged_boundary.last_callback.frame+1,A,8));
  CHECK(state()->transfer.success);take();retire(0);CHECK(usbd_tagged_accepted());break;
 case 21:
  bind();usbd_tagged_cancel();CHECK(send(A)==TAG_NOT_SUBMITTED);CHECK(tagged_boundary.count==0);break;
 case 22:
  bind();tagged_boundary.cancel_submit=true;start(A);complete(0);CHECK(tagged_boundary.callbacks==0);retire(0);CHECK(!usbd_tagged_accepted());break;
 case 23:
  bind();start(A);usbd_tagged_cancel();complete(0);CHECK(!state()->transfer.success);retire(0);CHECK(!usbd_tagged_accepted());CHECK(usbd_tagged_release());break;
 case 24:
  bind();start(A);retire(0);CHECK(!usbd_tagged_accepted());CHECK(usbd_tagged_release());break;
 case 25:
  bind();start(A);for(unsigned i=0;i<5;i++)emit_record(0,9,XFER_RESULT_SUCCESS);
  CHECK(boundary.queue_full==1 && state()->first_fault==TAG_LOSS);
  CHECK(!usbd_tagged_fence(state()->transfer.c,state()->transfer.q));fixture_dispatch();
  CHECK(state()->queued==0 && tagged_boundary.callbacks==0);retire(0);CHECK(!usbd_tagged_accepted());break;
 case 26:
  bind();CHECK(!tud_hid_n_report(0,1,A,8));CHECK(!usbd_edpt_claim(0,0x81));
  CHECK(!usbd_edpt_release(0,0x81));CHECK(!usbd_edpt_xfer(0,0x81,(uint8_t*)A,8));
  CHECK(!usbd_edpt_xfer_fifo(0,0x81,NULL,8));CHECK(hid_submits()==0);start(A);finish_success(0);break;
 case 27:
  bind();start(A);emit_record(0,9,XFER_RESULT_SUCCESS);certify(0);
  CHECK(usbd_tagged_retire(state()->transfer.c,state()->transfer.q));
  CHECK(!usbd_tagged_fence(state()->transfer.c,state()->transfer.q));
  tagged_boundary.hook=hook;fixture_dispatch();CHECK(state()->receipt_pending);
  CHECK(!usbd_tagged_fence(state()->transfer.c,state()->transfer.q));
  CHECK(send(B)==TAG_NOT_SUBMITTED);take();retire(0);CHECK(usbd_tagged_accepted());break;
 case 28:
  bind();for(unsigned i=0;i<8;i++){start(A);finish_success(i);}
  CHECK(state()->last_q==8);CHECK(send(A)==TAG_NOT_SUBMITTED);CHECK(state()->last_refusal==TAG_EXHAUSTED);
  CHECK(state()->last_q==8 && tagged_boundary.count==8);break;
 case 29:
  for(unsigned i=0;i<8;i++){bind();CHECK(usbd_tagged_unbind());}
  CHECK(state()->c==8);CHECK(!tud_hid_tagged_bind(0,1));CHECK(state()->c==8);break;
 case 30:
  bind();start(Z);finish_success(0);CHECK(usbd_tagged_unbind());bind();start(Z);
  emit_record(0,9,XFER_RESULT_SUCCESS);fixture_dispatch();CHECK(!state()->transfer.success);
  CHECK(usbd_edpt_busy(0,0x81));CHECK(state()->transfer.c!=tagged_boundary.records[0].original.c);
  finish_success(1);CHECK(state()->observations==2);break;
 case 31:
  bind();tagged_boundary.ambiguous=true;CHECK(send(A)==TAG_AMBIGUOUS);
  CHECK(state()->first_fault==TAG_CONTROLLER);CHECK(send(A)==TAG_NOT_SUBMITTED);CHECK(tagged_boundary.count==1);
  complete(0);CHECK(tagged_boundary.callbacks==0);retire(0);CHECK(!usbd_tagged_accepted());break;
 case 32:
  bind();start(A);tag_transfer_t old=state()->transfer;for(unsigned i=0;i<10;i++)CHECK(send(B)==TAG_NOT_SUBMITTED);
  CHECK(!memcmp(&old,&state()->transfer,sizeof(old)));CHECK(tagged_boundary.count==1);CHECK(!usbd_tagged_unbind());finish_success(0);break;
 case 33:
  bind();start(A);usbd_tagged_cancel();usbd_tagged_invalidate(TAG_LOSS);CHECK(state()->first_fault==TAG_CANCELLED);
  certify(0);CHECK(!usbd_tagged_retire(state()->transfer.c+1,state()->transfer.q));
  CHECK(!usbd_tagged_retire(state()->transfer.c,state()->transfer.q+1));retire(0);CHECK(!usbd_tagged_accepted());break;
 case 34:
  CHECK(usbd_edpt_claim(0,0x81));CHECK(!tud_hid_tagged_bind(0,1));CHECK(usbd_edpt_release(0,0x81));
  bind();start(A);finish_success(0);break;
 case 35:
  bind();start(A);emit_record(0,9,XFER_RESULT_FAILED);fixture_dispatch();
  CHECK(state()->first_fault==TAG_SHAPE && tagged_boundary.callbacks==0);retire(0);CHECK(!usbd_tagged_accepted());break;
 case 36:
  bind();start(A);complete(0);take();certify(0);
  tagged_boundary.fence_allow=false;CHECK(usbd_tagged_retire(state()->transfer.c,state()->transfer.q));
  CHECK(!usbd_tagged_fence(state()->transfer.c,state()->transfer.q));CHECK(!usbd_tagged_release());
  tagged_boundary.fence_allow=true;CHECK(usbd_tagged_fence(state()->transfer.c,state()->transfer.q));CHECK(usbd_tagged_accepted());break;
 case 37:
  bind();tagged_boundary.contradict=true;CHECK(send(A)==TAG_AMBIGUOUS);
  CHECK(state()->queued==1 && state()->first_fault==TAG_CONTRADICTION);
  fixture_dispatch();CHECK(tagged_boundary.callbacks==0);retire(0);CHECK(!usbd_tagged_accepted());break;
 case 38:
  bind();start(A);inject_bus(DCD_EVENT_UNPLUGGED);fixture_dispatch();fixture_config(1);
  CHECK(!tud_hid_tagged_bind(0,1));CHECK(!usbd_tagged_unbind());CHECK(!usbd_tagged_release());
  CHECK(send(B)==TAG_NOT_SUBMITTED);retire(0);CHECK(usbd_tagged_release());
  CHECK(usbd_tagged_unbind());bind();start(B);finish_success(1);break;
 case 39:
  bind();boundary.fail_unlock=true;CHECK(send(A)==TAG_AMBIGUOUS);
  CHECK(state()->first_fault==TAG_LOCK_RELEASE);CHECK(state()->transfer.active);
  CHECK(tagged_boundary.attempts==0);CHECK(send(A)==TAG_NOT_SUBMITTED);
  CHECK(!usbd_tagged_release());CHECK(!usbd_tagged_unbind());break;
 case 40:
  bind();tagged_boundary.in_submit=submit_hook;start(A);
  CHECK(state()->transfer.retired);CHECK(!state()->submitting);complete(0);take();
  CHECK(usbd_tagged_fence(state()->transfer.c,state()->transfer.q));CHECK(usbd_tagged_accepted());break;
 case 41:
  bind();CHECK(state()->c==UINT64_MAX);start(A);CHECK(state()->last_q==UINT64_MAX);
  complete(0);take();retire(0);CHECK(usbd_tagged_accepted());CHECK(usbd_tagged_release());
  CHECK(send(A)==TAG_NOT_SUBMITTED);CHECK(state()->last_q==UINT64_MAX);
  CHECK(usbd_tagged_unbind());CHECK(!tud_hid_tagged_bind(0,1));CHECK(state()->c==UINT64_MAX);break;
 case 42:
  bind();start(A);complete(0);take();retire(0);CHECK(usbd_tagged_accepted());
  emit_record(0,9,XFER_RESULT_SUCCESS);CHECK(!usbd_tagged_accepted());
  CHECK(state()->first_fault==TAG_LIFETIME && !state()->transfer.fenced);
  fixture_dispatch();CHECK(tagged_boundary.callbacks==1);CHECK(!usbd_tagged_accepted());
  retire(0);CHECK(!usbd_tagged_accepted());break;
 case 43:
  bind();start(Z);usbd_tagged_cancel();complete(0);retire(0);
  CHECK(!usbd_tagged_accepted());CHECK(usbd_tagged_release());CHECK(usbd_tagged_unbind());
  bind();start(Z);emit_record(0,9,XFER_RESULT_SUCCESS);fixture_dispatch();
  CHECK(!state()->transfer.success && usbd_edpt_busy(0,0x81));finish_success(1);break;
 case 44:
  bind();start(A);complete(0);take();retire(0);CHECK(usbd_tagged_accepted());
  CHECK(tud_deinit(0));CHECK(!usbd_tagged_accepted());CHECK(!state()->valid);break;
 case 45:
  bind();boundary.in_lock=cancel_lock_hook;CHECK(send(A)==TAG_NOT_SUBMITTED);
  CHECK(state()->first_fault==TAG_CANCELLED && !state()->transfer.active);
  CHECK(tagged_boundary.attempts==0 && !usbd_edpt_busy(0,0x81));
  CHECK(!state()->submitting);break;
 case 46:
  bind();boundary.in_lock=lock_hook;start(A);boundary.in_lock=NULL;
  CHECK(tagged_boundary.attempts==1 && state()->last_q==1);finish_success(0);break;
 default:CHECK(false);
 }
}
int main(int argc,char** argv){
 CHECK(argc==2);unsigned n=(unsigned)strtoul(argv[1],NULL,10);fixture_init();
 tagged_boundary.retire_allow=true;tagged_boundary.fence_allow=true;run(n);
#ifdef STAGE28O_NEGATIVE_CONTROL
 CHECK(false);
#endif
 const tag_state_t* s=state();
 printf("{\"id\":\"O%02u\",\"status\":\"PASS\",\"assertions\":%u,\"native_sizes\":{\"event\":%zu,\"state\":%zu,\"transfer\":%zu},\"c\":%"PRIu64",\"q\":%"PRIu64",\"queued\":%u,\"rejected\":%u,\"tagged_callbacks\":%u,\"controller_attempts\":%u,\"controller_records\":%u,\"first_fault\":%u,\"accepted\":%s,\"mutex_wait_forever\":%u,\"records\":[",n,assertions,sizeof(dcd_event_t),sizeof(*s),sizeof(tag_transfer_t),s->c,s->last_q,s->queued,s->rejected,tagged_boundary.callbacks,tagged_boundary.attempts,tagged_boundary.count,s->first_fault,usbd_tagged_accepted()?"true":"false",boundary.mutex_wait_forever);
 for(unsigned i=0;i<tagged_boundary.count;i++){
  struct ControllerRecord* r=&tagged_boundary.records[i];tag_transfer_t* t=&r->original;
  printf("%s{\"c\":%"PRIu64",\"q\":%"PRIu64",\"ep\":%u,\"id\":%u,\"length\":%u,\"retired\":%s,\"fenced\":%s,\"entered_at\":%u,\"returned_at\":%u,\"emissions\":%u,\"frame\":\"",i?",":"",t->c,t->q,t->ep,t->id,t->length,r->retired?"true":"false",r->fenced?"true":"false",r->entered_at,r->returned_at,r->emissions);
  for(unsigned j=0;j<t->length;j++)printf("%02X",t->frame[j]);printf("\"}");
 }
 printf("],\"tagged_receipts\":[");
 for(unsigned i=0;i<tagged_boundary.callbacks;i++){
  const tag_transfer_t* t=&tagged_boundary.receipts[i];
  printf("%s{\"c\":%"PRIu64",\"q\":%"PRIu64",\"at\":%u,\"length\":%u,\"frame\":\"",i?",":"",t->c,t->q,tagged_boundary.receipt_at[i],t->length);
  for(unsigned j=0;j<t->length;j++)printf("%02X",t->frame[j]);printf("\"}");
 }
 printf("]");print_evidence();printf("}");return 0;
}
