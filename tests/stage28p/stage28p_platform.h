#pragma once
// Native fake platform. Genuine register type from pinned dwc2_type.h.
#include "dwc2_type.h"
#define DWC2_EP_MAX 7
extern dwc2_regs_t simulated_regs;
static const dwc2_controller_t _dwc2_controller[]={
 {.reg_base=(uintptr_t)&simulated_regs,.irqnum=0,.ep_count=7,.ep_in_count=5,.ep_fifo_size=1024}
};
// Only field storage, not the actual ESP32 USB_WRAP register format or MMIO.
typedef struct {unsigned pad_pull_override,dp_pullup,dp_pulldown,dm_pullup,dm_pulldown;} usb_wrap_otg_conf_reg_t;
extern struct SimulatedWrap {usb_wrap_otg_conf_reg_t otg_conf;} USB_WRAP;
void dwc2_dcd_int_enable(uint8_t);
void dwc2_dcd_int_disable(uint8_t);
void dwc2_remote_wakeup_delay(void);
void dwc2_phy_init(dwc2_regs_t*,uint8_t);
void dwc2_phy_update(dwc2_regs_t*,uint8_t);
uint32_t platform_grst_read(dwc2_regs_t*);
void platform_fifo_store(volatile uint32_t*,uint32_t);
uint32_t platform_fifo_load(const volatile uint32_t*);
void platform_packet_queued(dwc2_regs_t*,uint8_t,uint16_t);
struct PlatformEvidence {
 unsigned flush_reads,fifo_stores,fifo_loads,packets,interrupt_enable,interrupt_disable,phy_calls;
 uint32_t words[128];uint16_t packet_lengths[32];bool freeze_flush,consume_fifo,watch;
};
extern struct PlatformEvidence platform;
void platform_reset(void);
void platform_bus_reset(void);
void platform_irq(uint32_t,uint32_t);
void platform_in(uint8_t,uint32_t);
struct DriverSnapshot {const uint8_t* cursor;const tu_fifo_t* fifo;uint16_t total,max_packet;uint8_t interval;};
struct DriverSnapshot driver_snapshot(uint8_t ep);

size_t driver_native_xfer_bytes(void);
size_t driver_native_control_bytes(void);
