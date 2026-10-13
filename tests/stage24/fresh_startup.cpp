static void esp_partition_iterator_release(const void*) {}
#include <fstream>
// Real plaintext NVS C initializer + exact patched initArduino + production setup/loop.
// Actual settings.cpp too; RTOS/USB and other application services are stand-ins.
#define main stage21_component_main
#include "nvs_readonly.cpp"
#undef main
#include "Arduino.h"
#include <algorithm>
static unsigned hooks=0;
static std::vector<std::string> services;
static esp_err_t diagnostic=ESP_OK;
constexpr int CONFIG_LOG_DEFAULT_LEVEL=0;
void esp_log_level_set(const char*,int){}
void init(){++hooks;}void initVariant(){++hooks;}
void logError(const char*,esp_err_t e){diagnostic=e;}
#define log_e(...) logError(__VA_ARGS__)
extern "C" {
#include "core_startup.inc"
}
#include "../../EvilDuckS3/settings.cpp"
#include "../../EvilDuckS3/EvilDuckS3.ino"
void delay(uint32_t){}uint32_t millis(){return 0;}
uint32_t esp_random(){return 0;}
namespace debug{void begin(){services.push_back("debug");}void info(const String&) {services.push_back("diagnostic");}}
namespace led{void begin(){services.push_back("led");}void setColor(int,int,int){}}
namespace hid_backend{void begin(){services.push_back("hid");}}
namespace keyboard_locale{void begin(){services.push_back("locale");}}
namespace attackmode{void begin(){services.push_back("msc");}}
namespace storage{bool begin(){services.push_back("filesystem");return true;}}
namespace script_library{void installIfNeeded(){services.push_back("file-write");}}
namespace cli{void begin(){services.push_back("cli");}void update(){services.push_back("cli-update");}}
namespace webserver{void begin(){services.push_back("web");}}
namespace duckscript{bool run(const String&){services.push_back("autorun-spy");return true;}void update(){services.push_back("script-update");}}
namespace com{void update(){services.push_back("com-update");}}
static bool called(const char*s){return std::find(services.begin(),services.end(),s)!=services.end();}
int main(int argc,char**argv){try{
 check(argc==3,"case and generated image required");std::string name=argv[1];Flash f;backend=&f;
 std::ifstream input(argv[2],std::ios::binary);check(bool(input),"fresh image opened");input.read(reinterpret_cast<char*>(f.data.data()),f.data.size());check(input.gcount()==static_cast<long>(f.data.size()),"exact fresh NVS bytes loaded");
 descriptor.readonly=name!="healthy_writable";
 if(name=="invalid_readonly")f.data[68]^=1;
 if(name=="missing_readonly")missing=true;
 if(name=="settings_corrupt_readonly")f.data[itemAt(f,0x21,"ap_ssid")+32]^=1;
 f.ops.clear();f.writes=f.erases=0;attempts.clear();auto before=f.data;
 check(evilduck_nvs_startup_error()==ESP_ERR_INVALID_STATE,"policy starts unknown before actual initializer");
 initArduino();auto e=evilduck_nvs_startup_error();setup();for(unsigned i=0;i<10000;++i)loop();
 const bool failed=name=="invalid_readonly" || name=="missing_readonly";
 if(failed){check(e!=ESP_OK && startupNvsError==e && diagnostic==e,"actual original init failure latched");check(hooks==0,"no variant hooks after actual init error");}
 else {check(e==ESP_OK && hooks==2,"actual successful core initialization unchanged");}
 const bool settingsFailed=name=="settings_corrupt_readonly" && !deployment::safeStart();
 if(settingsFailed)check(e==ESP_OK && !settings::ready() && settings::loadError()==ESP_ERR_NOT_ALLOWED && startupSettingsFailed,"actual settings corrupt read rejects mutation and latches app disabled");
 if(failed || deployment::safeStart() || settingsFailed){
  for(const char*s:{"hid","filesystem","file-write","settings-load-spy","msc","cli","web","autorun-spy","script-update","com-update","cli-update"})check(!called(s),"actual setup/loop keeps application services quiescent");
  check(services.size()==(settingsFailed?3:2),"bounded diagnostics, no automatic arming in repeated loop");
 }else {check(!called("autorun-spy")&&called("web")&&called("filesystem")&&called("msc"),"fresh normal profile starts services but never autorun (spies only)");check(settings::ready() && !settings::autorunEnabled() && settings::getAutorun()=="" && settings::getSSID()=="synthetic-ap","actual settings loaded through real SDK");if(descriptor.readonly)check(!settings::saveChecked() && settings::saveError()==ESP_ERR_NOT_ALLOWED,"actual checked save refuses SDK readonly partition");}
 if(deployment::safeStart() || failed)check(!settings::ready(),"actual safe/error profile never loaded settings");
 protectedBytes(f,before); // Healthy writable seed also needs no actual write in these paths.
 for(auto a:attempts)std::cout<<"ATTEMPT "<<a.kind<<" "<<a.address<<" "<<a.bytes<<" "<<a.error<<"\n";
 auto deinit=nvs_flash_deinit();check(deinit==ESP_OK || deinit==ESP_ERR_NVS_NOT_INITIALIZED,"bounded SDK deinit");
 protectedBytes(f,before);
 std::cout<<"PASS "<<name<<" ("<<assertions<<" assertions)\n";
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
