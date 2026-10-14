#include "tusb.h"
#include "device/dcd.h"
#include "stage28p_platform.h"
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
dwc2_regs_t simulated_regs;
struct SimulatedWrap USB_WRAP;
struct PlatformEvidence platform;
static void bound(bool ok){if(!ok)abort();}
void dwc2_dcd_int_enable(uint8_t p){(void)p;platform.interrupt_enable++;}
void dwc2_dcd_int_disable(uint8_t p){(void)p;platform.interrupt_disable++;}
void dwc2_remote_wakeup_delay(void){} // no real scheduler/time semantics
void dwc2_phy_init(dwc2_regs_t* r,uint8_t p){(void)r;(void)p;platform.phy_calls++;if(platform.watch){puts("WATCHDOG genuine common phy reached before reset loop");fflush(stdout);}}
void dwc2_phy_update(dwc2_regs_t* r,uint8_t p){(void)r;(void)p;platform.phy_calls++;}
uint32_t platform_grst_read(dwc2_regs_t* r){
 platform.flush_reads++;
 if(!platform.freeze_flush)r->grstctl=(r->grstctl&~(GRSTCTL_TXFFLSH|GRSTCTL_RXFFLSH|GRSTCTL_CSRST))|GRSTCTL_AHBIDL;
 return r->grstctl; // self-clear/idle here is a SCRIPTED assumption, not hardware proof
}
void platform_fifo_store(volatile uint32_t* p,uint32_t word){
 bound(platform.fifo_stores<128);platform.words[platform.fifo_stores++]=word;*p=word;
}
uint32_t platform_fifo_load(const volatile uint32_t* p){platform.fifo_loads++;return *p;}
void platform_packet_queued(dwc2_regs_t* r,uint8_t ep,uint16_t bytes){
 bound(platform.packets<32);platform.packet_lengths[platform.packets++]=bytes;
 if(platform.consume_fifo){
  dwc2_ep_tsize_t sz={.value=r->epin[ep].tsiz};bound(sz.xfer_size>=bytes && sz.packet_count);
  sz.xfer_size-=bytes;sz.packet_count--;r->epin[ep].tsiz=sz.value;
 }
 // Packet consumption on helper return is scripted timing, not validated silicon timing.
}
void platform_reset(void){
 memset(&simulated_regs,0,sizeof(simulated_regs));memset(&platform,0,sizeof(platform));
 dwc2_ghwcfg2_t cfg={.value=0};cfg.num_dev_ep=6;simulated_regs.ghwcfg2=cfg.value;
 simulated_regs.gsnpsid=DWC2_CORE_REV_3_00a;simulated_regs.grstctl=GRSTCTL_AHBIDL;
 for(unsigned i=0;i<7;i++)simulated_regs.epin[i].dtxfsts=64;
 platform.consume_fifo=true;
}
void platform_irq(uint32_t bits,uint32_t otg){
 // Plain status fields: inject deterministic snapshot, execute real ISR, then
 // simulate end-of-invocation acknowledgement. Assignments inside ISR are NOT W1C.
 simulated_regs.gintsts=bits;simulated_regs.gotgint=otg;dcd_int_handler(0);
 simulated_regs.gintsts=0;simulated_regs.gotgint=0;simulated_regs.daint=0;
 for(unsigned i=0;i<7;i++){simulated_regs.epin[i].intr=0;simulated_regs.epout[i].intr=0;}
}
void platform_bus_reset(void){
 platform_irq(GINTSTS_USBRST,0);platform_irq(GINTSTS_ENUMDNE,0);
}
void platform_in(uint8_t ep,uint32_t bits){
 simulated_regs.daint=1u<<ep;simulated_regs.epin[ep].intr=bits;
 platform_irq(GINTSTS_IEPINT,0);
}
