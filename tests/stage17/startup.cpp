#include "Arduino.h"
#include <iostream>
#include <stdexcept>
#include <vector>
#include <string>
#include "../../EvilDuckS3/EvilDuckS3.ino"
static std::vector<std::string> calls;
extern "C" int32_t evilduck_nvs_startup_error(void) { return 0; }
static bool autorun=true;
static unsigned assertions=0;
void check(bool ok,const char *why){++assertions;if(!ok)throw std::runtime_error(why);}
void delay(uint32_t){calls.push_back("delay");}uint32_t millis(){return 0;}
namespace debug{void begin(){calls.push_back("debug");}void info(const String&){calls.push_back("log");}}
namespace led{void begin(){calls.push_back("led");}void setColor(int,int,int){calls.push_back("color");}}
namespace hid_backend{void begin(){calls.push_back("hid");}}
namespace keyboard_locale{void begin(){calls.push_back("locale");}}
namespace attackmode{void begin(){calls.push_back("attackmode");}}
namespace storage{bool begin(){calls.push_back("storage-mount-format-risk");return false;}}
namespace script_library{void installIfNeeded(){calls.push_back("install");}}
namespace settings{bool ready(){return true;}int32_t loadError(){return 0;}void load(){calls.push_back("settings");}bool autorunEnabled(){return autorun;}String getAutorun(){return "stored-not-executed.txt";}uint32_t pickAutorunDelayMs(){return 0;}bool getStealthMode(){return false;}bool getDisableLed(){return false;}uint32_t getLedColor(){return 0;}}
namespace cli{void begin(){calls.push_back("cli");}void update(){calls.push_back("cli-update");}}
namespace webserver{void begin(){calls.push_back("web");}}
namespace duckscript{bool run(const String&){calls.push_back("run-request-only");return true;}void update(){calls.push_back("script-update");}}
namespace com{void update(){calls.push_back("com-update");}}
static bool contains(const char *s){return std::find(calls.begin(),calls.end(),s)!=calls.end();}
int main(){try{
 setup();
 if(deployment::safeStart()){
  check(calls.size()==2&&calls[0]=="debug"&&calls[1]=="log","safe setup logs only");
  for(auto name:{"hid","storage-mount-format-risk","install","settings","attackmode","web","cli","run-request-only"})check(!contains(name),"no unsafe application service initialized");
  for(unsigned i=0;i<10000;++i)loop();
  check(!contains("script-update")&&!contains("com-update")&&!contains("cli-update"),"safe loop never executes queued work");
  check(calls.size()==10002,"safe loop only yields");
  std::cout<<"PASS stage17_safe_start_actual_setup_loop ("<<assertions<<" assertions)\n";
 }else{
  for(auto name:{"hid","storage-mount-format-risk","install","settings","attackmode","web","cli","run-request-only"})check(contains(name),"normal startup remains unchanged even with mount failure");
  check(std::find(calls.begin(),calls.end(),"storage-mount-format-risk")<std::find(calls.begin(),calls.end(),"run-request-only"),"existing startup ordering");
  loop();check(contains("script-update")&&contains("com-update")&&contains("cli-update"),"normal schedulers unchanged");
  std::cout<<"PASS stage17_normal_startup_compatibility ("<<assertions<<" assertions)\n";
 }
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
