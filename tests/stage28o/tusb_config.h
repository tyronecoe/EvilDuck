#pragma once
// Native fixture only. Not the SDK/board configuration or a real USB descriptor.
#define CFG_TUSB_MCU OPT_MCU_ESP32S3
#define CFG_TUSB_OS OPT_OS_CUSTOM
#define CFG_TUSB_DEBUG 0
#define CFG_TUSB_RHPORT0_MODE (OPT_MODE_DEVICE | OPT_MODE_FULL_SPEED)
#define CFG_TUD_ENABLED 1
#define CFG_TUH_ENABLED 0
#define CFG_TUD_HID 1
#define CFG_TUD_CDC 0
#define CFG_TUD_MSC 0
#define CFG_TUD_MIDI 0
#define CFG_TUD_VENDOR 0
#define CFG_TUD_AUDIO 0
#define CFG_TUD_VIDEO 0
#define CFG_TUD_ECM_RNDIS 0
#define CFG_TUD_NCM 0
#define CFG_TUD_DFU 0
#define CFG_TUD_DFU_RUNTIME 0
#define CFG_TUD_HID_EP_BUFSIZE 64
#define CFG_TUD_ENDPOINT0_SIZE 64
#define CFG_TUD_TASK_QUEUE_SZ 4
#define CFG_TUD_INTERFACE_MAX 4
#define CFG_TUD_ENDPPOINT_MAX 7
#define CFG_TUSB_MEM_SECTION
#define CFG_TUSB_MEM_ALIGN __attribute__((aligned(4)))
// Explicit command-line opt-in; never enabled by this configuration alone.
#ifndef CFG_TUD_TAGGED_NATIVE
#define CFG_TUD_TAGGED_NATIVE 0
#endif
