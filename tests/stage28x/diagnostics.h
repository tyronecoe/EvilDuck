#ifndef EVILDUCK_STAGE28X_DIAGNOSTICS_H
#define EVILDUCK_STAGE28X_DIAGNOSTICS_H
#include <stdint.h>
#include <stddef.h>
#if defined(EVILDUCK_ROUTE_B_DIAGNOSTICS) && !defined(EVILDUCK_PORTABLE_ROUTE_B)
#error Diagnostics require the controlled Route B selector
#endif
namespace route_x {
struct Resources {uint32_t free8=0,min8=0,largest8=0,loopAllocated=0,loopFreeMinimum=0;bool heapKnown=false,stackKnown=false;};
struct Snapshot {
 uint32_t ticks=0,maxIntervalUs=0,maxWorkUs=0,clockErrors=0,samples=0;
 uint32_t accepted=0,refused=0,queuePeak=0,stopPublished=0,stopObserved=0;
 uint8_t phase=0,reason=0,firstFault=0,localKind=0,firstLocalFault=0;
 bool quarantined=false;uint64_t localSequence=0,clearRequest=0,clearSubmitted=0;
 Resources resources{};
};
#ifdef EVILDUCK_ROUTE_B_DIAGNOSTICS
// Locked functions require the existing publication Critical, never call lower APIs.
void admissionLocked(bool);void queueLocked(unsigned);void stopLocked();void observedLocked();
void beginTurn();void endTurn(uint32_t now);
Snapshot snapshot();size_t format(char*,size_t);size_t storageBytes();
#ifdef EVILDUCK_HOST_TEST
void saturateForTest();
#endif
#else
inline void admissionLocked(bool){}inline void queueLocked(unsigned){}inline void stopLocked(){}inline void observedLocked(){}
inline void beginTurn(){}inline void endTurn(uint32_t){}
#endif
}

#endif
