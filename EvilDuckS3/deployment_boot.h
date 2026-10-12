#pragma once
// Explicit build-time recovery profile. Normal-operation defaults are unchanged.
#ifndef EVILDUCK_DEPLOYMENT_SAFE_START
#define EVILDUCK_DEPLOYMENT_SAFE_START 0
#endif
#if EVILDUCK_DEPLOYMENT_SAFE_START != 0 && EVILDUCK_DEPLOYMENT_SAFE_START != 1
#error "EVILDUCK_DEPLOYMENT_SAFE_START must be 0 or 1"
#endif
namespace deployment {
constexpr bool safeStart() { return EVILDUCK_DEPLOYMENT_SAFE_START == 1; }
}
