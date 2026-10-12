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
extern "C" esp_err_t nvs_open(const char*,nvs_open_mode_t mode,nvs_handle_t*h){++opens;check(mode==NVS_READONLY,"read-only namespace");if(open_error)return open_error;*h=1;return ESP_OK;}
extern "C" void nvs_close(nvs_handle_t){++closes;}
static esp_err_t get(const char*k,int type,void*out,size_t size){++read_calls;if(k==error_key)return read_error;auto it=values.find(k);if(it==values.end())return ESP_ERR_NVS_NOT_FOUND;if(it->second.type!=type)return ESP_ERR_NVS_TYPE_MISMATCH;if(it->second.data.size()!=size)return ESP_ERR_NVS_INVALID_LENGTH;std::memcpy(out,it->second.data.data(),size);return ESP_OK;}
extern "C" esp_err_t nvs_get_u8(nvs_handle_t,const char*k,uint8_t*v){return get(k,NVS_TYPE_U8,v,1);}
extern "C" esp_err_t nvs_get_u16(nvs_handle_t,const char*k,uint16_t*v){return get(k,NVS_TYPE_U16,v,2);}
extern "C" esp_err_t nvs_get_u32(nvs_handle_t,const char*k,uint32_t*v){return get(k,NVS_TYPE_U32,v,4);}
extern "C" esp_err_t nvs_get_str(nvs_handle_t,const char*k,char*out,size_t*n){++read_calls;if(k==error_key)return read_error;auto it=values.find(k);if(it==values.end())return ESP_ERR_NVS_NOT_FOUND;if(it->second.type!=NVS_TYPE_STR)return ESP_ERR_NVS_TYPE_MISMATCH;if(!out){*n=it->second.data.size();return ESP_OK;}if(*n<it->second.data.size())return ESP_ERR_NVS_INVALID_LENGTH;std::memcpy(out,it->second.data.data(),it->second.data.size());*n=it->second.data.size();return ESP_OK;}
#include "../../EvilDuckS3/settings.cpp"
#include "../../EvilDuckS3/EvilDuckS3.ino"
extern "C" int32_t evilduck_nvs_startup_error(void){return 0;}
void delay(uint32_t){} uint32_t millis(){return 0;}
namespace debug{void begin(){services.push_back("debug");}void info(const String&s){logs.push_back(s.c_str());}}
namespace led{void begin(){services.push_back("led");}void setColor(int,int,int){}}
namespace hid_backend{void begin(){services.push_back("hid");}}
namespace keyboard_locale{void begin(){services.push_back("locale");}}
namespace attackmode{void begin(){services.push_back("msc");}}
namespace storage{bool begin(){services.push_back("filesystem");return true;}}
namespace script_library{void installIfNeeded(){services.push_back("install");}}
namespace cli{void begin(){services.push_back("cli");}void update(){services.push_back("cli-update");}}
namespace webserver{void begin(){services.push_back("web");}}
namespace duckscript{bool run(const String&){services.push_back("autorun-request-stub");return true;}void update(){services.push_back("script-update");}}
namespace com{void update(){services.push_back("com-update");}}
static void str(const char*k,std::string v){std::vector<uint8_t>d(v.begin(),v.end());d.push_back(0);values[k]={NVS_TYPE_STR,d};}
static void num(const char*k,uint32_t v,int type=NVS_TYPE_U8){size_t len=type==NVS_TYPE_U32?4:type==NVS_TYPE_U16?2:1;std::vector<uint8_t>d(len);for(size_t i=0;i<len;++i)d[i]=v>>(8*i);values[k]={type,d};}
int main(int argc,char**argv){try{check(argc==2,"case required");std::string n=argv[1];bool invalid=false;
 if(n=="allocation_failure"){str("autorun_script","fixture.txt");fail_buffer_allocation=true;invalid=true;}
 else if(n=="missing_namespace")open_error=ESP_ERR_NVS_NOT_FOUND;
 else if(n=="open_failure"){open_error=ESP_FAIL;invalid=true;}
 else if(n=="not_initialized"){open_error=ESP_ERR_NVS_NOT_INITIALIZED;invalid=true;}
 else if(n=="type_mismatch"){str("autorun_enabled","synthetic-secret");invalid=true;}
 else if(n=="read_failure"){error_key="autorun_enabled";read_error=ESP_FAIL;invalid=true;}
 else if(n=="string_read_failure"){error_key="ap_password";read_error=ESP_FAIL;invalid=true;}
 else if(n=="invalid_bool"){num("autorun_enabled",2);invalid=true;}
 else if(n=="invalid_channel"){num("ap_channel",14);invalid=true;}
 else if(n=="invalid_ssid"){str("ap_ssid",std::string(33,'x'));invalid=true;}
 else if(n=="invalid_password"){str("ap_password","short");invalid=true;}
 else if(n=="invalid_rgb"){num("led_color",0x1000000,NVS_TYPE_U32);invalid=true;}
 else if(n=="invalid_delay"){num("ar_dly_min",9,NVS_TYPE_U16);num("ar_dly_max",8,NVS_TYPE_U16);invalid=true;}
 else if(n=="autorun_without_script"){num("autorun_enabled",1);invalid=true;}
 else if(n=="oversized_string"){str("autorun_script",std::string(4000,'x'));invalid=true;}
 else if(n=="missing_nul"){values["autorun_script"]={NVS_TYPE_STR,{1,2,3}};invalid=true;}
 else if(n=="embedded_nul"){values["autorun_script"]={NVS_TYPE_STR,{1,0,1,0}};invalid=true;}
 else if(n=="zero_length_string"){values["autorun_script"]={NVS_TYPE_STR,{}};invalid=true;}
 else if(n=="valid_autorun"){num("autorun_enabled",1);str("autorun_script","harmless-fixture.txt");}
 else if(n=="maximum_string"){str("web_pw",std::string(3999,'x'));}
 if(n=="repeat_failure"||n=="save_after_failure"||n=="latched_failure"){open_error=ESP_FAIL;invalid=true;}
 auto snapshot=values;
 if(n=="save_open_failure")save_open_ok=false;
 setup();
 if(deployment::safeStart()){
  check(opens==0&&services.size()==1&&services[0]=="debug","safe start skips settings and services");
 }else{
  check(settings::ready()!=invalid,"readiness matches evidence");
  check(mocked_writes==0&&values==snapshot,"load never writes source settings");
  if(invalid){check(services.size()==1&&services[0]=="debug","failed settings stop before services");check(settings::loadError()!=ESP_OK,"error retained");settings::save();check(mocked_writes==0,"save blocked after load failure");}
  else {check(std::find(services.begin(),services.end(),"hid")!=services.end(),"valid settings normal startup");if(n=="valid_autorun")check(std::find(services.begin(),services.end(),"autorun-request-stub")!=services.end(),"valid autorun preserved as stub only");else check(!settings::autorunEnabled(),"defaults never autorun");}
  if(n=="repeat_failure"){for(int i=0;i<10;++i)settings::load();check(!settings::ready()&&mocked_writes==0,"repeated load no writes");}
  if(n=="latched_failure"){open_error=ESP_OK;settings::load();check(settings::ready(),"explicit recovery read succeeds");setup();check(services.size()==2,"latched setup cannot arm after successful retry");}
  if(n=="save_open_failure"){settings::save();check(mocked_writes==0,"failed write open never writes");}
 }
 if(invalid||deployment::safeStart()){auto count=services.size();for(int i=0;i<1000;++i)loop();check(services.size()==count,"quiescent loop no work");}
 for(auto &s:logs)check(s.find("synthetic-secret")==std::string::npos,"private values never logged");
 check(mocked_writes==0,"no unintended settings writes");
 std::cout<<"PASS "<<n<<" ("<<assertions<<" assertions)\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
