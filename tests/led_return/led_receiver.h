#pragma once
#include <stdint.h>
#include <stddef.h>
namespace led_return {
constexpr char Message[]="EVILDUCK TEST 123";
constexpr uint64_t TimeoutUs=120000000,StaleUs=5000000;
enum class State:uint8_t{Idle,Receiving,Complete,Stopped,Timeout,Overflow,Disconnected,InvalidFrame,ClockError};
struct Snapshot{State state=State::Idle;bool observed=false,connected=false,disconnected=false,stale=false,integrity=false;uint8_t mask=0;uint32_t session=0,reports=0,rejected=0,overflow=0,queued=0;uint64_t lastReportUs=0,capturedAtUs=0;char text[sizeof(Message)]={};};
// Callback ingress: fixed copies only; never execution mutex, I/O, USB or allocation.
void observe(uint8_t mask,uint32_t session,uint64_t at);
void invalidate(uint32_t session);void rejected();
void service(uint64_t now);bool start(uint64_t now);void stop();void clear();
Snapshot snapshot(uint64_t now);size_t storageBytes();
uint16_t crc16(const uint8_t* p,size_t n);
}
