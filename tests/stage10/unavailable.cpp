#include "attackmode.h"
#include "usb_msc.h"
#include "script_log.h"
#include <iostream>
namespace script_log {void warn(const String&){} }
int main(){
 unsigned assertions=0;
 auto check=[&](bool ok){++assertions;if(!ok)throw "unexpected enabled MSC";};
 try{
  attackmode::begin();check(!attackmode::applyFromString("STORAGE"));
  check(attackmode::storageRequested()&&!attackmode::storageEnabled()&&!attackmode::storagePreparing());
  check(String(attackmode::storageError()).indexOf("unavailable")>=0);
  attackmode::setOff();check(!attackmode::storageRequested()&&usb_msc::state()==usb_msc::State::Off);
  std::cout<<"PASS build_without_msc_reports_unavailable ("<<assertions<<" assertions)\n";return 0;
 }catch(...){std::cerr<<"FAIL build_without_msc_reports_unavailable\n";return 1;}
}
