#pragma once
// Explicit build-time recovery profile. Normal-operation defaults are unchanged.
#ifndef EVILDUCK_DEPLOYMENT_SAFE_START
#define EVILDUCK_DEPLOYMENT_SAFE_START 0
#endif
#if EVILDUCK_DEPLOYMENT_SAFE_START != 0 && EVILDUCK_DEPLOYMENT_SAFE_START != 1
#error "EVILDUCK_DEPLOYMENT_SAFE_START must be 0 or 1"
#endif
#ifndef EVILDUCK_CONTROLLED_START
#define EVILDUCK_CONTROLLED_START 0
#endif
#if EVILDUCK_CONTROLLED_START != 0 && EVILDUCK_CONTROLLED_START != 1
#error "EVILDUCK_CONTROLLED_START must be 0 or 1"
#endif
#if EVILDUCK_CONTROLLED_START && EVILDUCK_DEPLOYMENT_SAFE_START
#error "Controlled normal start and quiescent safe start are distinct profiles"
#endif
namespace deployment {
constexpr bool safeStart() { return EVILDUCK_DEPLOYMENT_SAFE_START == 1; }
constexpr bool controlledStart() { return EVILDUCK_CONTROLLED_START == 1; }
}
