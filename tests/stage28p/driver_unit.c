/* Native textual inclusion preserves all original driver bytes and static
 * declarations. Only this read-only probe is added; no private state mutation. */
#include "dcd_dwc2.c"
#include "stage28p_platform.h"
struct DriverSnapshot driver_snapshot(uint8_t ep){
 const xfer_ctl_t* x=&xfer_status[tu_edpt_number(ep)][tu_edpt_dir(ep)];
 return (struct DriverSnapshot){x->buffer,x->ff,x->total_len,x->max_size,x->interval};
}

size_t driver_native_xfer_bytes(void){return sizeof(xfer_status);}
size_t driver_native_control_bytes(void){return sizeof(_dcd_data);}
