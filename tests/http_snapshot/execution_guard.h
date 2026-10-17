#ifndef EVILDUCK_HTTP_SNAPSHOT_EXECUTION_GUARD_H
#define EVILDUCK_HTTP_SNAPSHOT_EXECUTION_GUARD_H
#ifndef EVILDUCK_ROUTE_B_STATUS_HARDENING
#error Explicit HTTP snapshot hardening selector required
#endif
#include <stdint.h>

#ifdef EVILDUCK_HOST_TEST
#include <mutex>
#include <chrono>
#else
#include <freertos/FreeRTOS.h>
#include <freertos/semphr.h>
#include <esp_timer.h>
#endif
namespace execution {
// Named outermost holder, not a task id or proof of physical root cause.
enum class Owner:uint32_t{Other=1,DuckUpdate,ComUpdate,DiagnosticBackend,HttpStatus,HttpDiagnostics,HttpStop};
constexpr uint32_t HttpWaitMs=5;
struct Statistics{uint32_t acquired=0,contentions=0,timeouts=0,lastContendedOwner=0,maxHoldUs=0;};
namespace detail {
#ifdef EVILDUCK_HOST_TEST
inline std::mutex statsMutex;
struct Critical{std::lock_guard<std::mutex> held{statsMutex};};
#else
inline portMUX_TYPE statsMux=portMUX_INITIALIZER_UNLOCKED;
struct Critical{Critical(){portENTER_CRITICAL(&statsMux);}~Critical(){portEXIT_CRITICAL(&statsMux);}};
#endif
inline uint32_t acquired=0,contentions=0,timeouts=0,lastOwner=0,owner=0,maxHold=0;
inline void increment(uint32_t& n){if(n!=UINT32_MAX)++n;}
// depth/start protected by the execution mutex itself; no task-local allocation.
inline uint32_t depth=0,start=0;
inline uint32_t clockUs(){
#ifdef EVILDUCK_HOST_TEST
 return uint32_t(std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::steady_clock::now().time_since_epoch()).count());
#else
 return uint32_t(esp_timer_get_time());
#endif
}
inline void enter(Owner who){if(depth++==0){start=clockUs();Critical lock;owner=uint32_t(who);increment(acquired);}}
inline void leave(){if(--depth==0){uint32_t span=clockUs()-start;Critical lock;if(span>maxHold)maxHold=span;owner=0;}}
inline void contention(){Critical lock;lastOwner=owner;increment(contentions);}
}
// Independently observed counters, NOT one atomic multi-field execution snapshot.
inline Statistics statistics(){detail::Critical lock;return {detail::acquired,detail::contentions,detail::timeouts,detail::lastOwner,detail::maxHold};}
#ifdef EVILDUCK_HOST_TEST
inline std::recursive_timed_mutex& mutex(){static std::recursive_timed_mutex value;return value;}
inline void(*contendedForTest)()=nullptr;
inline bool take(bool wait){if(mutex().try_lock())return true;if(!wait)return false;detail::contention();if(contendedForTest)contendedForTest();return mutex().try_lock_for(std::chrono::milliseconds(HttpWaitMs));}
inline void give(){mutex().unlock();}
#else
inline SemaphoreHandle_t mutex(){static SemaphoreHandle_t value=xSemaphoreCreateRecursiveMutex();configASSERT(value);return value;}
inline bool take(bool wait){if(xSemaphoreTakeRecursive(mutex(),0)==pdTRUE)return true;if(!wait)return false;detail::contention();
 // Round UP: five milliseconds must not silently become zero ticks.
 constexpr TickType_t ticks=TickType_t((uint64_t(HttpWaitMs)*configTICK_RATE_HZ+999)/1000);
 static_assert(ticks>0 && ticks<portMAX_DELAY,"Bounded HTTP lock wait");
 return xSemaphoreTakeRecursive(mutex(),ticks)==pdTRUE;}
inline void give(){xSemaphoreGiveRecursive(mutex());}
#endif
class Guard{
public:explicit Guard(Owner who=Owner::Other){
#ifdef EVILDUCK_HOST_TEST
 mutex().lock();
#else
 xSemaphoreTakeRecursive(mutex(),portMAX_DELAY);
#endif
 detail::enter(who);}
 ~Guard(){detail::leave();give();}Guard(const Guard&)=delete;Guard& operator=(const Guard&)=delete;
};
class TryGuard{
 bool locked;
public:explicit TryGuard(Owner who=Owner::Other):locked(take(false)){if(locked)detail::enter(who);}
 ~TryGuard(){if(locked){detail::leave();give();}}explicit operator bool()const{return locked;}TryGuard(const TryGuard&)=delete;TryGuard& operator=(const TryGuard&)=delete;
};
class BoundedGuard{
 bool locked;
public:explicit BoundedGuard(Owner who):locked(take(true)){if(locked)detail::enter(who);else {detail::Critical lock;detail::increment(detail::timeouts);}}
 ~BoundedGuard(){if(locked){detail::leave();give();}}explicit operator bool()const{return locked;}BoundedGuard(const BoundedGuard&)=delete;BoundedGuard& operator=(const BoundedGuard&)=delete;
};
}
#endif
