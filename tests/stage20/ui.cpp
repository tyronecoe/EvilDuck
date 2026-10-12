#include "host.h"
#include "cli.h"
#include "settings.h"
#include "led.h"
#include "duckscript.h"
#include "storage.h"
#include "execution_guard.h"
#include <future>
#include <thread>
#include <iostream>
#include <stdexcept>
#include <map>
struct Param {String content;String value(){return content;}};
class AsyncWebServerRequest {
public:
 std::map<std::string,Param> parameters;int code=0;String body;
 bool hasParam(const char*n,bool){return parameters.count(n);}
 Param*getParam(const char*n,bool){return &parameters[n];}
 void send(int status,const char*,const String&text){code=status;body=text;}
};
static bool checkAuth(AsyncWebServerRequest*){return true;}
static void sendAuthRequired(AsyncWebServerRequest*r){r->send(401,"text/plain","Auth");}
static bool isSafeScriptName(const String&){return true;}
#include "actual_web_handlers.inc"
static unsigned assertions=0;
void check(bool x,const char*s){++assertions;if(!x)throw std::runtime_error(s);}
int main(int argc,char**argv){try{check(argc==2,"case required");std::string n=argv[1];mock::reset();mock::settingsSaveOk=n.find("failure")==std::string::npos;
 if(n.rfind("cli_",0)==0){
  const char*command=n.find("reset")!=std::string::npos?"reset":n.find("autorun")!=std::string::npos?"autorun harmless.txt":"set channel 2";
  cli::parse(command,mock::print,false);bool failure=mock::output.indexOf("failed")>=0;check(failure==!mock::settingsSaveOk,"CLI matches checked persistence result");if(failure)check(mock::output.indexOf("Settings reset\n")<0&&mock::output.indexOf("Autorun saved")<0,"no false saved acknowledgment");
 }else{
  AsyncWebServerRequest req;
  std::promise<void> locked,release;auto future=release.get_future();std::thread holder;
  if(n=="web_save_busy"||n=="web_led_busy"){holder=std::thread([&]{execution::Guard guard;locked.set_value();future.wait();});locked.get_future().wait();}
  if(n.find("led")!=std::string::npos){if(n!="web_led_missing")req.parameters["color"]={String("000028")};handleSetLed(&req);}else handleSaveSettings(&req);
  if(holder.joinable()){release.set_value();holder.join();}
  int expected=n.find("busy")!=std::string::npos?409:n=="web_led_missing"?400:mock::settingsSaveOk?200:503;
  check(req.code==expected,"HTTP result matches persistence");if(expected!=200)check(mock::colors.empty(),"failed save never reports/updates LED as saved");
 }
 check(mock::reports.empty()&&mock::presses.empty(),"no HID from settings tests");
 std::cout<<"PASS "<<n<<" ("<<assertions<<" assertions)\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
