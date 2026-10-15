#pragma once
#include <stdint.h>
#ifdef EVILDUCK_HOST_TEST
#include <mutex>
namespace u_platform {
using Task=uintptr_t;
inline thread_local Task simulatedTask=1;
inline Task current(){return simulatedTask;}
inline void taskForTest(Task t){simulatedTask=t;}
inline std::mutex publicationMutex;
struct Critical{std::lock_guard<std::mutex> lock{publicationMutex};};
}
#else
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>
namespace u_platform {
using Task=TaskHandle_t;
inline Task current(){return xTaskGetCurrentTaskHandle();}
inline portMUX_TYPE publicationMux=portMUX_INITIALIZER_UNLOCKED;
struct Critical{Critical(){portENTER_CRITICAL(&publicationMux);}~Critical(){portEXIT_CRITICAL(&publicationMux);}};
}
#endif
namespace u_platform {
// Access Gate only under Critical. No execution mutex is taken inside Critical.
struct Gate{Task owner{};bool reserved=false,permitted=false,inIo=false;};
inline Gate gate;
inline bool allowed(){Critical lock;return !gate.reserved||(gate.owner==current()&&gate.permitted&&!gate.inIo);}
inline void permission(bool p){Critical lock;if(gate.owner==current())gate.permitted=p;}
inline void io(bool p){Critical lock;if(gate.owner==current())gate.inIo=p;}
}
