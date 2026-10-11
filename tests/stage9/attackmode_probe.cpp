// Production attackmode.cpp; MSC start failure is a mock, never a USB operation.
#include "attackmode.h"
#include "usb_msc.h"
#include "script_log.h"
#include "debug.h"
#include <iostream>
static unsigned warnings=0,starts=0;
static usb_msc::State probeState=usb_msc::State::Off;
namespace usb_msc {
 bool begin(){++starts;probeState=State::Failed;return false;}
 void end(){probeState=State::Off;}
 void update(){}
 bool active(){return false;}
 bool preparing(){return false;}
 const char *lastError(){return "MSC: simulated startup failure";}
 const char *stateName(){return probeState==State::Off?"off":"failed";}
}
namespace script_log {void info(const String&){}void warn(const String&){++warnings;} }
namespace debug {void info(const String&){}void error(const String&){} }
int main(){
 attackmode::begin();bool accepted=attackmode::applyFromString("STORAGE");
 // Stage10 directly resolved the source defect. Preserve its history and assert
 // corrected failure propagation and retry, not the former buggy observation.
 bool observed=!accepted&&!attackmode::storageEnabled()&&!usb_msc::active()&&
               attackmode::storageRequested()&&warnings==1&&starts==1;
 std::cout<<"MSC failure: accepted="<<accepted<<", reported storage="<<attackmode::storageEnabled()
          <<", actual active="<<usb_msc::active()<<", warnings="<<warnings<<'\n';
 // This proves failure reporting/retry, not USB personality conformance.
 if(!observed)return 1;
 attackmode::applyFromString("STORAGE");
 if(starts!=2||warnings!=2||attackmode::storageEnabled())return 1;
 std::cout<<"OBSERVED 2 assertions; Stage10 RESOLVED (failure propagated, retry attempted; personality remains partial)\n";
}
