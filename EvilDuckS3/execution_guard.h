#pragma once

// Serialize main-loop execution and asynchronous web/CLI requests. Recursive
// locking allows the existing completion/error callbacks to call stop(). Never
// hold this lock while deliberately waiting for a timer or typing a whole line.
#ifdef EVILDUCK_HOST_TEST
#include <mutex>
namespace execution {
inline std::recursive_mutex &mutex() {
  static std::recursive_mutex value;
  return value;
}
class Guard {
  std::lock_guard<std::recursive_mutex> lock;
public:
  Guard() : lock(mutex()) {}
};
// USB callbacks must not wait behind script/web filesystem work.
class TryGuard {
  std::unique_lock<std::recursive_mutex> lock;
public:
  TryGuard() : lock(mutex(), std::try_to_lock) {}
  explicit operator bool() const { return lock.owns_lock(); }
};

}
#else
#include <freertos/FreeRTOS.h>
#include <freertos/semphr.h>
namespace execution {
inline SemaphoreHandle_t mutex() {
  static SemaphoreHandle_t value = xSemaphoreCreateRecursiveMutex();
  configASSERT(value);
  return value;
}
class Guard {
public:
  Guard() { xSemaphoreTakeRecursive(mutex(), portMAX_DELAY); }
  ~Guard() { xSemaphoreGiveRecursive(mutex()); }
  Guard(const Guard &) = delete;
  Guard &operator=(const Guard &) = delete;
};
class TryGuard {
  bool locked;
public:
  TryGuard() : locked(xSemaphoreTakeRecursive(mutex(), 0) == pdTRUE) {}
  ~TryGuard() { if (locked) xSemaphoreGiveRecursive(mutex()); }
  explicit operator bool() const { return locked; }
  TryGuard(const TryGuard &) = delete;
  TryGuard &operator=(const TryGuard &) = delete;
};

}
#endif
