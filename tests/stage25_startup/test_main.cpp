#include "Arduino.h"
#include "nvs.h"
#include <iostream>
#include <map>
#include <vector>
#include <string>
#include <stdexcept>
struct Value{int type;std::vector<uint8_t> data;bool operator==(const Value&o)const{return type==o.type&&data==o.data;}};
static std::map<std::string,Value> values;
static esp_err_t open_error=ESP_OK,read_error=ESP_OK;
static std::string error_key;
static unsigned closes=0,opens=0,read_calls=0;
unsigned mocked_writes=0;
bool save_open_ok=true;
static std::vector<std::string> services;
static std::vector<std::string> logs;
static unsigned assertions=0;
static bool fail_buffer_allocation=false;
void *operator new[](std::size_t n,const std::nothrow_t&) noexcept {
 if(fail_buffer_allocation)return nullptr;
 try{return ::operator new[](n);}catch(...){return nullptr;}
}
void check(bool x,const char*s){++assertions;if(!x)throw std::runtime_error(s);}
uint32_t esp_random(){return 0;}
extern "C" esp_err_t nvs_open(const char*,nvs_open_mode_t mode,nvs_handle_t*h){++opens;if(mode==NVS_READWRITE)return save_open_ok?ESP_OK:ESP_FAIL;check(mode==NVS_READONLY,"read-only namespace");if(open_error)return open_error;*h=1;return ESP_OK;}
extern "C" void nvs_close(nvs_handle_t){++closes;}
static esp_err_t get(const char*k,int type,void*out,size_t size){++read_calls;if(k==error_key)return read_error;auto it=values.find(k);if(it==values.end())return ESP_ERR_NVS_NOT_FOUND;if(it->second.type!=type)return ESP_ERR_NVS_TYPE_MISMATCH;if(it->second.data.size()!=size)return ESP_ERR_NVS_INVALID_LENGTH;std::memcpy(out,it->second.data.data(),size);return ESP_OK;}
extern "C" esp_err_t nvs_get_u8(nvs_handle_t,const char*k,uint8_t*v){return get(k,NVS_TYPE_U8,v,1);}
extern "C" esp_err_t nvs_get_u16(nvs_handle_t,const char*k,uint16_t*v){return get(k,NVS_TYPE_U16,v,2);}
extern "C" esp_err_t nvs_get_u32(nvs_handle_t,const char*k,uint32_t*v){return get(k,NVS_TYPE_U32,v,4);}
extern "C" esp_err_t nvs_get_str(nvs_handle_t,const char*k,char*out,size_t*n){++read_calls;if(k==error_key)return read_error;auto it=values.find(k);if(it==values.end())return ESP_ERR_NVS_NOT_FOUND;if(it->second.type!=NVS_TYPE_STR)return ESP_ERR_NVS_TYPE_MISMATCH;if(!out){*n=it->second.data.size();return ESP_OK;}if(*n<it->second.data.size())return ESP_ERR_NVS_INVALID_LENGTH;std::memcpy(out,it->second.data.data(),it->second.data.size());*n=it->second.data.size();return ESP_OK;}
extern "C" esp_err_t nvs_set_u8(nvs_handle_t,const char*,uint8_t){++mocked_writes;return ESP_OK;}
extern "C" esp_err_t nvs_set_u16(nvs_handle_t,const char*,uint16_t){++mocked_writes;return ESP_OK;}
extern "C" esp_err_t nvs_set_u32(nvs_handle_t,const char*,uint32_t){++mocked_writes;return ESP_OK;}
extern "C" esp_err_t nvs_set_str(nvs_handle_t,const char*,const char*){++mocked_writes;return ESP_OK;}
extern "C" esp_err_t nvs_commit(nvs_handle_t){return ESP_OK;}
#include "SPIFFS.h"
#include "../../EvilDuckS3/spiffs.cpp"
#include "../../EvilDuckS3/storage.cpp"
#include "../../EvilDuckS3/settings.cpp"
#include "../../EvilDuckS3/EvilDuckS3.ino"
static int32_t coreError=0; extern "C" int32_t evilduck_nvs_startup_error(void){return coreError;}
void delay(uint32_t){} uint32_t millis(){return 0;}
namespace debug{void begin(){services.push_back("debug");}void info(const String&s){logs.push_back(s.c_str());} void error(const String&s){logs.push_back(s.c_str());}}
namespace led{void begin(){services.push_back("led");}void setColor(int,int,int){}}
namespace hid_backend{void begin(){services.push_back("hid");}}
namespace keyboard_locale{void begin(){services.push_back("locale");}}
namespace attackmode{void begin(){services.push_back("msc");}}
namespace sd_card{bool begin(){services.push_back("sd");return true;} bool ready(){return false;} String listScriptsJson(){return "[]";}}
namespace script_library{void installIfNeeded(){services.push_back("install");}}
namespace cli{void begin(){services.push_back("cli");}void update(){services.push_back("cli-update");}}
static bool networkOK=true; namespace webserver{bool prepareControlledNetwork(){check(settings::ready()&&fsMock::mounts==1&&fsMock::mountOk,"network starts after settings and mount");return networkOK;}void begin(){services.push_back("web");}}
namespace duckscript{bool run(const String&){services.push_back("autorun-request-stub");return true;}void update(){services.push_back("script-update");}}
namespace com{void update(){services.push_back("com-update");}}
static void str(const char*k,std::string v){std::vector<uint8_t>d(v.begin(),v.end());d.push_back(0);values[k]={NVS_TYPE_STR,d};}
static void num(const char*k,uint32_t v,int type=NVS_TYPE_U8){size_t len=type==NVS_TYPE_U32?4:type==NVS_TYPE_U16?2:1;std::vector<uint8_t>d(len);for(size_t i=0;i<len;++i)d[i]=v>>(8*i);values[k]={type,d};}

esp_flash_t chip;esp_flash_t *esp_flash_default_chip=&chip;
static esp_partition_t table[7];static unsigned tableCount=6,tableIndex=0,allocated=0,released=0;static bool failLookup=false;
esp_partition_iterator_t esp_partition_find(unsigned,unsigned,const char*){if(failLookup)return nullptr;++allocated;tableIndex=0;return &tableIndex;}
esp_partition_iterator_t esp_partition_next(esp_partition_iterator_t it){if(++*it<tableCount)return it;esp_partition_iterator_release(it);return nullptr;}
const esp_partition_t *esp_partition_get(esp_partition_iterator_t it){return &table[*it];}
void esp_partition_iterator_release(esp_partition_iterator_t){++released;}
static void seedTable(){
 const char*names[]={"nvs","otadata","app0","app1","spiffs","coredump"};
 uint32_t offsets[]={0x9000,0xe000,0x10000,0x750000,0xe90000,0xff0000};
 uint32_t sizes[]={0x5000,0x2000,0x740000,0x740000,0x160000,0x10000};
 uint8_t types[]={1,1,0,0,1,1},subtypes[]={2,0,0x10,0x11,0x82,3};
 for(unsigned i=0;i<6;++i){table[i]={&chip,types[i],subtypes[i],offsets[i],sizes[i],{},false,false};std::strcpy(table[i].label,names[i]);}
}
static bool called(const char *s){return std::find(services.begin(),services.end(),s)!=services.end();}

int main(int argc,char**argv){try{
 check(argc==2,"case required");std::string name=argv[1];mscMock::reset();seedTable();fsMock::settingsReady=settings::ready;
 // Deterministic dummy bytes for mocks only; never owner credentials or published images.
 str("ap_ssid",std::string(12,'s'));str("ap_password",std::string(16,'p'));str("web_pw",std::string(16,'w'));num("autorun_enabled",0);
 bool deny=false;
 if(name=="missing_namespace"){open_error=ESP_ERR_NVS_NOT_FOUND;deny=true;}
 if(name=="missing_ssid"){values.erase("ap_ssid");deny=true;}
 if(name=="missing_password"){values.erase("ap_password");deny=true;}
 if(name=="missing_web_password"){values.erase("web_pw");deny=true;}
 if(name=="blank_password"){str("ap_password","");deny=true;}
 if(name=="blank_web_password"){str("web_pw","");deny=true;}
 if(name=="legacy_password"){str("ap_password",WIFI_PASSWORD);deny=true;}
 if(name=="short_password"){str("ap_password",std::string(7,'p'));deny=true;}
 if(name=="long_password"){str("ap_password",std::string(64,'p'));deny=true;}
 if(name=="long_ssid"){str("ap_ssid",std::string(33,'s'));deny=true;}
 if(name=="newline_credentials"){str("web_pw",std::string(8,'w')+'\n');deny=true;}
 if(name=="credential_type_mismatch"){num("ap_password",9);deny=true;}
 if(name=="credential_read_failure"){error_key="web_pw";read_error=ESP_FAIL;deny=true;}
 if(name=="allocation_failure"){fail_buffer_allocation=true;deny=true;}
 if(name=="corrupt_nul"){values["ap_password"].data.back()='x';deny=true;}
 if(name=="nvs_open_failure"){open_error=ESP_FAIL;deny=true;}
 if(name=="nvs_startup_failure"){coreError=ESP_FAIL;deny=true;}
 if(name=="stored_autorun"){num("autorun_enabled",1);str("autorun_script",std::string(8,'a')+".txt");deny=true;}
 if(name=="mount_failure"||name=="missing_filesystem"){fsMock::mountOk=false;deny=true;}
 if(name=="network_failure"){networkOK=false;deny=true;}
 if(name=="interrupted_mount"){fsMock::interrupted=true;deny=true;}
 if(name=="wrong_layout"){table[4].address=0x290000;table[4].size=0x170000;deny=true;}
 if(name=="readonly_layout"){table[0].readonly=true;deny=true;}
 if(name=="partition_lookup_failure"){failLookup=true;deny=true;}
 if(name=="duplicate_partition"){table[6]=table[0];tableCount=7;deny=true;}
 if(name=="missing_partition"){tableCount=5;deny=true;}
 if(name=="wrong_chip"){table[0].flash_chip=nullptr;deny=true;}
 auto snapshot=values;
 loop();check(services.empty(),"loop before setup is quiescent");
 try{setup();}catch(const std::runtime_error&){check(name=="interrupted_mount","only synthetic mount interruption allowed");}
 const auto serviceCount=services.size();setup();check(services.size()==serviceCount,"second setup cannot re-arm or reinitialize");
 for(unsigned i=0;i<1000;++i)loop();
 check(allocated==released,"bounded partition iterators always released");
 check(mocked_writes==0&&values==snapshot,"startup never writes settings");
 check(fsMock::formats==0&&!fsMock::formatRequested,"no automatic formatting");
 check(!called("install")&&!called("autorun-request-stub"),"no example installation or payload execution");
 check(mscMock::writes==0&&mscMock::creates==0,"fresh media contains no created scripts");
 if(deny && name!="mount_failure" && name!="missing_filesystem" && name!="interrupted_mount" && name!="network_failure")check(fsMock::mounts==0&&!called("sd"),"config/layout failure never mounts either filesystem");
 if(deny && (name=="mount_failure" || name=="missing_filesystem" || name=="interrupted_mount"))check(fsMock::mounts==1&&!called("sd"),"required mount failure prevents optional SD initialization");
 if(deny){for(const char*s:{"hid","msc","cli","web","script-update","com-update","cli-update"})check(!called(s),"failed boot keeps application services off");}
 else{
  check(settings::ready()&&called("hid")&&called("web")&&called("sd"),"valid startup after checked layout/settings/mount");
  check(fsMock::mounts==1,"only one mount attempt");check(!settings::autorunEnabled(),"autorun remains disabled");
  check(storage::listAllScriptsJson()=="[]","fresh user library has zero scripts");
 }
 if(name=="settings_controls"){
  auto password=settings::getPassword(),web=settings::getWebPassword();
  settings::setPassword(WIFI_PASSWORD);settings::setWebPassword("");settings::setAutorun("unused.txt");
  check(settings::getPassword()==password&&settings::getWebPassword()==web&&!settings::autorunEnabled(),"controlled setters cannot enable legacy/blank credentials or autorun");
  check(!settings::resetChecked()&&settings::getPassword()==password&&settings::getWebPassword()==web,"legacy reset is refused without mutation");check(mocked_writes==0,"reset refusal never persists");
 }
 for(const auto&log:logs){check(log.find(std::string(16,'p'))==std::string::npos,"AP credential absent from diagnostics");check(log.find(std::string(16,'w'))==std::string::npos,"web credential absent from diagnostics");}
 std::cout<<"PASS "<<name<<" ("<<assertions<<" assertions)\n";
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
