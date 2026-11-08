#include "device/dcd.h"
#include <atomic>
namespace {std::atomic<uint32_t> calls{0};std::atomic<const dcd_event_t*> last{nullptr};std::atomic<bool> lastIsr{false};}
extern "C" void __real_dcd_event_handler(const dcd_event_t* event,bool inIsr){last.store(event);lastIsr.store(inIsr);calls.fetch_add(1);}
extern "C" void evilduck_mock_dcd_reset(){calls.store(0);last.store(nullptr);lastIsr.store(false);}
extern "C" uint32_t evilduck_mock_dcd_calls(){return calls.load();}
extern "C" const dcd_event_t* evilduck_mock_dcd_last(){return last.load();}
extern "C" bool evilduck_mock_dcd_last_isr(){return lastIsr.load();}
