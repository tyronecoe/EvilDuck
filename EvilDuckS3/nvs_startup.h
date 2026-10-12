#pragma once
#include <stdint.h>
#if !defined(EVILDUCK_HOST_TEST) && !defined(EVILDUCK_VERIFIED_NVS_PRESERVATION)
#error "Use the isolated build wrapper: early NVS preservation patch is required"
#endif
// Strong symbol supplied ONLY by the pinned patched Arduino core. Initial state
// is unknown/error until initArduino captures the exact nvs_flash_init result.
extern "C" int32_t evilduck_nvs_startup_error(void);
