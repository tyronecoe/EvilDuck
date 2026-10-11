// Production attackmode.cpp; MSC start failure is a mock, never a USB operation.
#include "attackmode.h"
#include "usb_msc.h"
#include "script_log.h"
#include "debug.h"
#include <iostream>
static unsigned warnings=0,starts=0;
namespace usb_msc { bool begin(){++starts;return false;}void end(){}bool active(){return false;} }
namespace script_log {void info(const String&){}void warn(const String&){++warnings;} }
namespace debug {void info(const String&){}void error(const String&){} }
int main(){
 attackmode::begin();bool accepted=attackmode::applyFromString("STORAGE");
 bool observed=accepted&&attackmode::storageEnabled()&&!usb_msc::active()&&warnings==1&&starts==1;
 std::cout<<"MSC failure: accepted="<<accepted<<", reported storage="<<attackmode::storageEnabled()
          <<", actual active="<<usb_msc::active()<<", warnings="<<warnings<<'\n';
 // Assertions confirm the finding, not compliance. This is an acknowledged defect.
 if(!observed)return 1;
 attackmode::applyFromString("STORAGE");
 if(starts!=1)return 1; // Logical flag also prevents a retry after failed start.
 std::cout<<"OBSERVED 2 assertions; canonical behavior GAP (false success, retry suppressed)\n";
}
