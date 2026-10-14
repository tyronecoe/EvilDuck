#include "boundary.h"
#include "stage28p_platform.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static unsigned assertions;
#define CHECK(v) do{assertions++;if(!(v)){fprintf(stderr,"FAIL line=%d: %s\n",__LINE__,#v);exit(1);}}while(0)
static uint8_t A[192],B[192],ring[32];static tu_fifo_t stream;
static void reenter(void){CHECK(tud_hid_n_report(0,1,B,8));}
static void submit(uint16_t bytes){CHECK(dcd_edpt_xfer(0,0x81,A,bytes));}
static void fifo(void){platform_in(1,DIEPINT_TXFE);}
static void done(void){platform_in(1,DIEPINT_XFRC);}
static void clear_evidence(void){boundary.callback_count=boundary.event_count=0;platform.fifo_stores=platform.packets=0;}
static bool call_pending;
static void early(void){CHECK(call_pending);fifo();done();fixture_dispatch();}
static void run(unsigned n){
 struct DriverSnapshot s;
 switch(n){
 case 1:
  submit(9);s=driver_snapshot(0x81);CHECK(s.cursor==A && s.total==9 && s.max_packet==64);
  CHECK(simulated_regs.epin[1].tsiz==((1u<<DIEPTSIZ_PKTCNT_Pos)|9u));CHECK(simulated_regs.diepempmsk&2);
  fifo();s=driver_snapshot(0x81);CHECK(s.cursor==A+9);CHECK(platform.fifo_stores==3 && platform.packets==1);
  CHECK(platform.words[0]==0x03020100 && platform.words[1]==0x07060504 && platform.words[2]==8);
  CHECK(!(simulated_regs.diepempmsk&2));CHECK(boundary.callback_count==0);
  done();CHECK(boundary.queue->count==1);fixture_dispatch();CHECK(boundary.callback_count==1 && boundary.callbacks[0].length==9);break;
 case 2:
  CHECK(!dcd_edpt_xfer(0,0x82,A,9));s=driver_snapshot(0x82);
  CHECK(!s.cursor && !s.total && !s.max_packet);CHECK(!(simulated_regs.diepempmsk&4));break;
 case 3:
  submit(9);CHECK(dcd_edpt_xfer(0,0x81,B,17));s=driver_snapshot(0x81);
  CHECK(s.cursor==B && s.total==17);CHECK(simulated_regs.epin[1].tsiz==((1u<<DIEPTSIZ_PKTCNT_Pos)|17u));
  fifo();CHECK(platform.words[0]==0x83828180);done();fixture_dispatch();CHECK(boundary.callbacks[0].length==17);break;
 case 4:
  submit(137);fifo();CHECK(platform.packets==3);CHECK(platform.packet_lengths[0]==64 && platform.packet_lengths[1]==64 && platform.packet_lengths[2]==9);
  CHECK(platform.fifo_stores==35 && driver_snapshot(0x81).cursor==A+137);done();fixture_dispatch();CHECK(boundary.callbacks[0].length==137);break;
 case 5:
  submit(9);simulated_regs.epin[1].dtxfsts=0;fifo();CHECK(platform.fifo_stores==0 && driver_snapshot(0x81).cursor==A);
  simulated_regs.epin[1].dtxfsts=64;fifo();CHECK(platform.fifo_stores==3 && driver_snapshot(0x81).cursor==A+9);break;
 case 6:
  submit(0);CHECK(!(simulated_regs.diepempmsk&2));done();fixture_dispatch();CHECK(boundary.callbacks[0].length==0);break;
 case 7:
  boundary.in_unlock=early;call_pending=true;CHECK(tud_hid_n_report(0,1,A,8));call_pending=false;CHECK(boundary.callback_count==1);CHECK(boundary.callbacks[0].bytes[0]==1);CHECK(boundary.callbacks[0].length==9);break;
 case 8:
  CHECK(tud_hid_n_report(0,1,A,8));fifo();done();fixture_dispatch();
  CHECK(tud_hid_n_report(0,1,A,8));fifo();done();fixture_dispatch();
  CHECK(boundary.callback_count==2);CHECK(!memcmp(boundary.callbacks[0].bytes,boundary.callbacks[1].bytes,9));break;
 case 9:
  submit(9);CHECK(dcd_edpt_xfer(0,0x81,B,17));done();fixture_dispatch();
  CHECK(boundary.callback_count==1 && boundary.callbacks[0].length==17);
  CHECK(driver_snapshot(0x81).cursor==B); // an unlabeled IRQ reads current descriptor, not original A
  break;
 case 10:
  CHECK(tud_hid_n_report(0,1,A,8));fifo();done();fixture_dispatch();
  CHECK(tud_hid_n_report(0,1,B,8));CHECK(usbd_edpt_busy(0,0x81));done();fixture_dispatch();
  CHECK(!usbd_edpt_busy(0,0x81));CHECK(boundary.callback_count==2);CHECK(boundary.callbacks[1].bytes[1]==B[0]);break;
 case 11:
  submit(9);fifo();done();done();fixture_dispatch();CHECK(boundary.callback_count==2);CHECK(driver_snapshot(0x81).cursor==A+9);break;
 case 12:
  submit(9);simulated_regs.daint=2;simulated_regs.epin[1].intr=DIEPINT_XFRC;
  platform_irq(GINTSTS_USBRST|GINTSTS_IEPINT,0);CHECK(!driver_snapshot(0x81).cursor && driver_snapshot(0x81).total==0);
  CHECK(boundary.events[boundary.event_count-1].id==DCD_EVENT_XFER_COMPLETE && boundary.events[boundary.event_count-1].length==0);break;
 case 13:
  submit(9);platform_bus_reset();fixture_dispatch();CHECK(!driver_snapshot(0x81).max_packet && !driver_snapshot(0x81).cursor);
  CHECK(!dcd_edpt_xfer(0,0x81,B,9));fixture_config(1);CHECK(dcd_edpt_xfer(0,0x81,B,9));break;
 case 14:
  submit(9);platform_irq(GINTSTS_USBSUSP,0);CHECK(boundary.events[boundary.event_count-1].id==DCD_EVENT_UNPLUGGED);
  CHECK(driver_snapshot(0x81).cursor==A && driver_snapshot(0x81).total==9);
  fixture_dispatch();CHECK(!tud_mounted());break;
 case 15:
  submit(9);platform_irq(GINTSTS_OTGINT,GOTGINT_SEDET);CHECK(boundary.events[boundary.event_count-1].id==DCD_EVENT_UNPLUGGED);
  CHECK(driver_snapshot(0x81).cursor==A);break;
 case 16:
  submit(9);platform_irq(GINTSTS_USBSUSP,0);fixture_dispatch();
  CHECK(dcd_edpt_xfer(0,0x81,B,9));CHECK(driver_snapshot(0x81).cursor==B);break;
 case 17:
  submit(9);dcd_edpt_close_all(0);s=driver_snapshot(0x81);
  CHECK(s.max_packet==0 && s.cursor==A && s.total==9);CHECK(!dcd_edpt_xfer(0,0x81,B,9));CHECK(platform.flush_reads>0);break;
 case 18:
  submit(9);dcd_edpt_close_all(0);done();fixture_dispatch();
  CHECK(boundary.callback_count==1 && boundary.callbacks[0].length==9);break;
 case 19:
  submit(9);simulated_regs.epin[1].intr=DIEPINT_INEPNE|DIEPINT_EPDISD;
  dcd_edpt_stall(0,0x81);CHECK(simulated_regs.epin[1].ctl&DIEPCTL_STALL);
  CHECK(driver_snapshot(0x81).cursor==A && driver_snapshot(0x81).total==9);
  dcd_edpt_clear_stall(0,0x81);CHECK(!(simulated_regs.epin[1].ctl&DIEPCTL_STALL));break;
 case 20:
  submit(9);for(unsigned i=0;i<5;i++)done();CHECK(boundary.queue_full==1);CHECK(boundary.queue->count==4);
  fixture_dispatch();CHECK(boundary.callback_count==4);break;
 case 21:
  CHECK(tud_hid_n_report(0,1,A,8));fifo();done();fixture_dispatch();
  CHECK(tud_hid_n_report(0,1,B,8));dcd_edpt_close_all(0);fixture_config(0);fixture_config(1);
  CHECK(tud_hid_n_report(0,1,A,8));done();fixture_dispatch();CHECK(boundary.callback_count==2);break;
 case 22:
  submit(9);fifo();done();fixture_dispatch();CHECK(driver_snapshot(0x81).cursor==A+9 && driver_snapshot(0x81).total==9);
  CHECK(simulated_regs.epin[1].ctl&DIEPCTL_EPENA); // plain-field simulator does not self-clear enable
  break;
 case 23:
  dcd_remote_wakeup(0);CHECK(!(simulated_regs.dctl&DCTL_RWUSIG));CHECK(simulated_regs.gintmsk&GINTMSK_SOFM);
  platform_irq(GINTSTS_WKUINT,0);CHECK(boundary.events[boundary.event_count-1].id==DCD_EVENT_RESUME);break;
 case 24:
  CHECK(tud_hid_n_report(0,0,A,8));fifo();done();fixture_dispatch();CHECK(boundary.callbacks[0].length==8);CHECK(boundary.callbacks[0].bytes[0]==0);break;
 case 25:
  CHECK(!tud_hid_n_report(0,1,A,65));CHECK(!tud_hid_n_report(0,1,A,8));CHECK(!driver_snapshot(0x81).cursor);break;
 case 26:
  dcd_remote_wakeup(0);platform_irq(GINTSTS_SOF,0);CHECK(!(simulated_regs.gintmsk&GINTMSK_SOFM));break;
 case 27:
  submit(9);simulated_regs.epin[1].intr=0;
  puts("WATCHDOG entered original dcd_edpt_stall with INEPNE=0");fflush(stdout);dcd_edpt_stall(0,0x81);CHECK(false);break;
 case 28:
  submit(9);platform.freeze_flush=true;
  puts("WATCHDOG entered original close_all with TXFFLSH held");fflush(stdout);dcd_edpt_close_all(0);CHECK(false);break;
 case 29:
  // Original helper bodies under only platform-header substitution: init hangs
  // on CSRST. PHY boundary marker independently establishes genuine init entry.
  CHECK(false);break;
 case 30:
  CHECK(tu_fifo_config(&stream,ring,32,1,false));CHECK(tu_fifo_write_n(&stream,A,9)==9);
  CHECK(dcd_edpt_xfer_fifo(0,0x81,&stream,9));CHECK(driver_snapshot(0x81).fifo==&stream);
  fifo();CHECK(tu_fifo_count(&stream)==0);CHECK(platform.fifo_stores==0);
  CHECK(simulated_regs.epin[1].tsiz==((1u<<DIEPTSIZ_PKTCNT_Pos)|9u)); // plain FIFO does not consume TSIZ
  done();fixture_dispatch();CHECK(boundary.callbacks[0].length==9);break;
 case 31:
  CHECK(tu_fifo_config(&stream,ring,16,2,false));CHECK(!dcd_edpt_xfer_fifo(0,0x81,&stream,9));
  CHECK(!driver_snapshot(0x81).cursor && !driver_snapshot(0x81).fifo);break;
 case 32:{
  tusb_desc_endpoint_t out={.bLength=7,.bDescriptorType=TUSB_DESC_ENDPOINT,.bEndpointAddress=1,.bmAttributes={.xfer=TUSB_XFER_BULK},.wMaxPacketSize=64};
  CHECK(dcd_edpt_open(0,&out));CHECK(dcd_edpt_xfer(0,1,B,9));CHECK(driver_snapshot(1).cursor==B);
  simulated_regs.daint=1u<<17;simulated_regs.epout[1].intr=DOEPINT_XFRC;
  platform_irq(GINTSTS_OEPINT,0);CHECK(boundary.events[boundary.event_count-1].ep==1);
  CHECK(boundary.events[boundary.event_count-1].length==9); // injected completion only; no RX data copied
  break;}
 case 33:
  submit(9);simulated_regs.epin[1].tsiz=(1u<<DIEPTSIZ_PKTCNT_Pos)|4u;
  done();fixture_dispatch();CHECK(boundary.callbacks[0].length==9);CHECK(driver_snapshot(0x81).cursor==A);break;
 case 34:
  submit(9);CHECK(tud_deinit(0));CHECK(driver_snapshot(0x81).cursor==A);
  done();CHECK(boundary.null_queue_sends==1);CHECK(platform.interrupt_disable>0);break;
 case 35:
  CHECK(tud_hid_n_report(0,1,A,8));boundary.in_callback=reenter;fifo();done();fixture_dispatch();
  CHECK(boundary.callback_count==1);CHECK(boundary.callbacks[0].bytes[1]==A[0]);
  CHECK(boundary.callbacks[0].after_hook[1]==B[0]);CHECK(driver_snapshot(0x81).total==9 && usbd_edpt_busy(0,0x81));break;
 case 36:
  submit(9);platform_in(1,DIEPINT_TOC|DIEPINT_AHBERR);
  CHECK(boundary.callback_count==0 && boundary.queue->count==0);
  CHECK(driver_snapshot(0x81).cursor==A && driver_snapshot(0x81).total==9);break;
 default:CHECK(false);
 }
}
int main(int argc,char** argv){
 CHECK(argc==2);for(unsigned i=0;i<192;i++){A[i]=(uint8_t)i;B[i]=(uint8_t)(128+i);}
 unsigned n=(unsigned)strtoul(argv[1],NULL,10);
 if(n==29){platform_reset();platform.watch=true;puts("WATCHDOG calling genuine dcd_init with original common body");fflush(stdout);tusb_rhport_init_t init={.role=TUSB_ROLE_DEVICE,.speed=TUSB_SPEED_FULL};dcd_init(0,&init);return 2;}
 fixture_init();clear_evidence();run(n);
#ifdef STAGE28P_NEGATIVE_CONTROL
 CHECK(false);
#endif
 printf("{\"id\":\"P%02u\",\"status\":\"PASS\",\"assertions\":%u,\"fifo_words\":[",n,assertions);
 for(unsigned i=0;i<platform.fifo_stores;i++)printf("%s%u",i?",":"",platform.words[i]);
 printf("],\"packet_lengths\":[");for(unsigned i=0;i<platform.packets;i++)printf("%s%u",i?",":"",platform.packet_lengths[i]);
 struct DriverSnapshot s=driver_snapshot(0x81);
 printf("],\"descriptor_total\":%u,\"descriptor_max\":%u,\"descriptor_retained_cursor\":%s,\"spin_calls\":%u,\"flush_reads\":%u,\"driver_identity_available\":false,\"retirement_certified\":false",s.total,s.max_packet,s.cursor?"true":"false",boundary.spin_calls,platform.flush_reads);
 printf(",\"native_xfer_state_bytes\":%zu,\"native_control_state_bytes\":%zu",driver_native_xfer_bytes(),driver_native_control_bytes());print_evidence();printf("}\n");return 0;
}
