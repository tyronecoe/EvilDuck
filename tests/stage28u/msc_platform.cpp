// Lower platform fake only: actual attackmode state and guards execute.
#include "usb_msc.h"
#include "sd_card.h"
namespace sd_card {String listDir(const String&){return "[]";}}
namespace usb_msc_test {bool active=false,preparing=false;}
namespace usb_msc {
bool begin(){return false;}void end(){}void update(){}
bool active(){return usb_msc_test::active;}bool preparing(){return usb_msc_test::preparing;}
const char* stateName(){return "off";}const char* lastError(){return "mock unavailable";}
State state(){return State::Off;}
}
