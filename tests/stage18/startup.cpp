#include "Arduino.h"
#include <array>
#include <vector>
#include <string>
#include <iostream>
#include <stdexcept>
#include <algorithm>
using esp_err_t=int32_t;
constexpr esp_err_t ESP_OK=0,ESP_FAIL=-1,ESP_ERR_INVALID_STATE=0x103;
constexpr esp_err_t ESP_ERR_NVS_NO_FREE_PAGES=0x110d,ESP_ERR_NVS_NEW_VERSION_FOUND=0x1110;
constexpr int CONFIG_LOG_DEFAULT_LEVEL=0,ESP_PARTITION_TYPE_DATA=1,ESP_PARTITION_SUBTYPE_DATA_NVS=2;
struct esp_partition_t{uint32_t address=0x9000,size=0x5000;};static esp_partition_t partition;
static std::array<uint8_t,0x5000> flash,original;
static unsigned asserts=0,inits=0,erases=0,writes=0,coreLogs=0,initHooks=0;
static esp_err_t initError=0,eraseError=0,lastLog=0;
static bool sdkMutation=false,missingPartition=false;
static std::vector<std::string> services;
void check(bool ok,const char *why){++asserts;if(!ok)throw std::runtime_error(why);}
esp_err_t esp_partition_erase_range(const esp_partition_t*,size_t,size_t){++erases;if(!eraseError)flash.fill(0xff);return eraseError;}
esp_err_t nvs_flash_erase(){++erases;flash.fill(0xff);return ESP_OK;}
esp_err_t esp_partition_write(const esp_partition_t*,size_t,const void*,size_t){++writes;flash[0]^=0xff;return ESP_OK;}
esp_err_t nvs_flash_init(){++inits;if(sdkMutation)esp_partition_write(&partition,0,nullptr,1);return inits>1&&!eraseError?ESP_OK:initError;}
const esp_partition_t *esp_partition_find_first(int,int,const char*){return missingPartition?nullptr:&partition;}
void esp_log_level_set(const char*,int){}void init(){++initHooks;}void initVariant(){++initHooks;}
void logError(const char*,esp_err_t error){++coreLogs;lastLog=error;}void logError(const char*){++coreLogs;}
#define log_e(...) logError(__VA_ARGS__)
extern "C" {
#include "core_startup.inc"
#ifndef PROTECTED_NVS
int32_t evilduck_nvs_startup_error(void){return ESP_ERR_INVALID_STATE;} // Never used by historical core-only tests.
#endif
}
#include "../../EvilDuckS3/EvilDuckS3.ino"
void delay(uint32_t){}uint32_t millis(){return 0;}
namespace debug{void begin(){services.push_back("debug");}void info(const String &s){services.push_back(s.c_str());}}
namespace led{void begin(){services.push_back("led");}void setColor(int,int,int){}}
namespace hid_backend{void begin(){services.push_back("hid");}}
namespace keyboard_locale{void begin(){services.push_back("locale");}}
namespace attackmode{void begin(){services.push_back("storage-activation-entry");}}
namespace storage{bool begin(){services.push_back("filesystem-mount");return true;}}
namespace script_library{void installIfNeeded(){services.push_back("example-writes");}}
namespace settings{void load(){services.push_back("nvs-load");}bool autorunEnabled(){return true;}String getAutorun(){return "never-opened-owner-script.txt";}uint32_t pickAutorunDelayMs(){return 0;}bool getStealthMode(){return false;}bool getDisableLed(){return false;}uint32_t getLedColor(){return 0;}}
namespace cli{void begin(){services.push_back("cli");}void update(){services.push_back("cli-update");}}
namespace webserver{void begin(){services.push_back("web");}}
namespace duckscript{bool run(const String&){services.push_back("autorun-request-only");return true;}void update(){services.push_back("script-update");}}
namespace com{void update(){services.push_back("com-update");}}
static bool called(const char*s){return std::find(services.begin(),services.end(),s)!=services.end();}
static void reset(){for(size_t i=0;i<flash.size();++i)flash[i]=i%251;original=flash;}
static void untouched(){check(erases==0&&writes==0,"no policy erase/write API invoked");check(flash==original,"entire protected NVS region unchanged");}
static void quiescent(){for(const char*s:{"hid","filesystem-mount","example-writes","nvs-load","storage-activation-entry","cli","web","autorun-request-only","script-update","com-update","cli-update"})check(!called(s),"no application service after failure/safe boot");}
static void test(const std::string &name){
 reset();
#ifndef PROTECTED_NVS
 if(name=="historical_no_free_pages_erase"||name=="historical_new_version_erase"){
  initError=name=="historical_no_free_pages_erase"?ESP_ERR_NVS_NO_FREE_PAGES:ESP_ERR_NVS_NEW_VERSION_FOUND;initArduino();
  check(erases==1&&inits==2,"unpatched erases/retries");check(flash!=original,"unpatched destroys protected bytes");check(initHooks==2,"unpatched proceeds after retry");
 }else if(name=="historical_erase_failure_error_replaced"){
  initError=ESP_ERR_NVS_NO_FREE_PAGES;eraseError=ESP_FAIL;initArduino();check(lastLog==ESP_FAIL,"unpatched original error overwritten");check(initHooks==2,"unpatched proceeds after failure");
 }else throw std::runtime_error("unknown historical test");
#else
 if(name=="protected_initial_unknown") {check(evilduck_nvs_startup_error()==ESP_ERR_INVALID_STATE,"not initialized is not success");setup();loop();quiescent();untouched();}
 else if(name=="protected_success") {initArduino();check(evilduck_nvs_startup_error()==0&&inits==1&&initHooks==2,"successful upstream initialization preserved");setup();loop();
  if(deployment::safeStart())quiescent();else check(called("autorun-request-only")&&called("web")&&called("nvs-load"),"normal services and preserved autorun policy unchanged");untouched();}
 else if(name=="protected_no_free_pages")initError=ESP_ERR_NVS_NO_FREE_PAGES;
 else if(name=="protected_new_version")initError=ESP_ERR_NVS_NEW_VERSION_FOUND;
 else if(name=="protected_invalid_metadata")initError=0x110b;
 else if(name=="protected_missing_partition") {initError=0x110f;missingPartition=true;}
 else if(name=="protected_flash_read_failure")initError=0x6001;
 else if(name=="protected_flash_initialization_failure")initError=ESP_FAIL;
 else if(name=="protected_flash_operation_failure")initError=0x6002;
 else if(name=="protected_no_memory")initError=0x101;
 else if(name=="protected_unexpected_positive")initError=0x7fffffff;
 else if(name=="protected_unexpected_negative")initError=-123456;
 else if(name=="protected_repeat_failure"){
  initError=ESP_ERR_NVS_NO_FREE_PAGES;eraseError=ESP_FAIL;
  // Each explicit call receives the same actual NVS error; no automatic retry.
  for(unsigned i=0;i<20;++i){inits=0;initArduino();check(evilduck_nvs_startup_error()==initError,"original error survives explicit attempts");}untouched();
 }else if(name=="protected_retry_never_arms_failed_app"){
  initError=ESP_ERR_NVS_NEW_VERSION_FOUND;initArduino();setup();initError=0;initArduino();check(evilduck_nvs_startup_error()==0,"explicit core retry can succeed");for(unsigned i=0;i<10000;++i)loop();setup();quiescent();untouched();check(startupNvsError==ESP_ERR_NVS_NEW_VERSION_FOUND,"application retains original failed boot error");
 }else if(name=="observed_sdk_side_effect_outside_policy"){
  sdkMutation=true;initError=0x6001;initArduino();setup();loop();check(erases==0&&writes==1&&flash!=original,"injected SDK write occurs before policy sees failure");quiescent();check(evilduck_nvs_startup_error()==initError,"SDK error still preserved; no total read-only guarantee");
 }else throw std::runtime_error("unknown protected test");
 if(initError && name!="observed_sdk_side_effect_outside_policy" && name!="protected_retry_never_arms_failed_app"){
  inits=0;initArduino();check(evilduck_nvs_startup_error()==initError&&inits==1,"original error/no automatic retry");check(initHooks==0,"variant hooks not called on error");check(lastLog==initError,"original diagnostic error retained");setup();for(unsigned i=0;i<10000;++i)loop();quiescent();untouched();
  check(services.size()==2&&services[1].find(std::to_string(initError))!=std::string::npos,"bounded exact error diagnostic");
 }
#endif
}
int main(int argc,char**argv){if(argc!=2)return 2;try{test(argv[1]);std::cout<<"PASS "<<argv[1]<<" ("<<asserts<<" assertions)\n";return 0;}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
