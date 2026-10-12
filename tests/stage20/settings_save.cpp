#include "Arduino.h"
#include "nvs.h"
#include <map>
#include <vector>
#include <stdexcept>
#include <iostream>
#include <future>
#include <thread>
static unsigned assertions=0,opens=0,closes=0,sets=0,commits=0;
static unsigned fail_set=0;static esp_err_t write_error=ESP_FAIL,open_error=ESP_OK,commit_error=ESP_OK;
static bool apply_failed_set=false,fail_read=false,interrupt_save=false;
static std::map<std::string,std::vector<uint8_t>> persisted;
static std::vector<std::string> order,diagnostics;
void check(bool x,const char*s){++assertions;if(!x)throw std::runtime_error(s);}
uint32_t esp_random(){return 0;}
extern "C" esp_err_t nvs_open(const char*,nvs_open_mode_t mode,nvs_handle_t*h){++opens;if(open_error)return open_error;*h=1;return ESP_OK;}
extern "C" void nvs_close(nvs_handle_t){++closes;}
extern "C" esp_err_t nvs_get_u8(nvs_handle_t,const char*,uint8_t*){return fail_read?ESP_FAIL:ESP_ERR_NVS_NOT_FOUND;}
extern "C" esp_err_t nvs_get_u16(nvs_handle_t,const char*,uint16_t*){return ESP_ERR_NVS_NOT_FOUND;}
extern "C" esp_err_t nvs_get_u32(nvs_handle_t,const char*,uint32_t*){return ESP_ERR_NVS_NOT_FOUND;}
extern "C" esp_err_t nvs_get_str(nvs_handle_t,const char*,char*,size_t*){return ESP_ERR_NVS_NOT_FOUND;}
static esp_err_t put(const char*k,std::vector<uint8_t> v){++sets;order.push_back(k);if(interrupt_save&&sets==4){std::cout<<"SIMULATED_POWER_LOSS sets=4 commits=0"<<std::endl;std::_Exit(77);}if(sets==fail_set){if(apply_failed_set)persisted[k]=v;return write_error;}persisted[k]=v;return ESP_OK;}
extern "C" esp_err_t nvs_set_u8(nvs_handle_t,const char*k,uint8_t v){return put(k,{v});}
extern "C" esp_err_t nvs_set_u16(nvs_handle_t,const char*k,uint16_t v){return put(k,{uint8_t(v),uint8_t(v>>8)});}
extern "C" esp_err_t nvs_set_u32(nvs_handle_t,const char*k,uint32_t v){return put(k,{uint8_t(v),uint8_t(v>>8),uint8_t(v>>16),uint8_t(v>>24)});}
extern "C" esp_err_t nvs_set_str(nvs_handle_t,const char*k,const char*v){std::vector<uint8_t>b(v,v+std::strlen(v)+1);return put(k,b);}
extern "C" esp_err_t nvs_commit(nvs_handle_t){++commits;return commit_error;}
namespace debug{void begin(){} void info(const String&s){diagnostics.push_back(s.c_str());}}
#include "../../EvilDuckS3/settings.cpp"
int main(int argc,char**argv){try{check(argc==2,"case required");std::string n=argv[1];
 if(n!="unloaded_save"&&n!="unloaded_reset"){settings::load();check(settings::ready(),"fresh typed load valid");}
 opens=closes=0;
 if(n=="read_failure_save"){fail_read=true;settings::load();opens=closes=0;}
 if(n=="interrupted_save")interrupt_save=true;
 if(n=="open_failure")open_error=ESP_FAIL;
 if(n=="open_full")open_error=ESP_ERR_NVS_NOT_ENOUGH_SPACE;
 if(n=="commit_failure")commit_error=ESP_FAIL;
 if(n=="invalid_delay")settings::setAutorunDelay(2,1);
 if(n=="invalid_web_length")settings::setWebPassword(String(std::string(4000,'x')));
 if(n=="embedded_nul")settings::setWebPassword(String(std::string("a\0b",3)));
 if(n=="valid_autorun"||n=="mixed_autorun_after_failure"){settings::setAutorun("harmless-fixture.txt");}
 if(n.rfind("set_failure_",0)==0)fail_set=std::stoi(n.substr(12));
 if(n=="set_full"){fail_set=2;write_error=ESP_ERR_NVS_NOT_ENOUGH_SPACE;}
 if(n=="set_flash_error"){fail_set=3;write_error=0x6001;}
 if(n=="failed_set_may_change_bytes"){fail_set=3;apply_failed_set=true;}
 if(n=="mixed_autorun_after_failure"){fail_set=2;persisted["autorun_script"]={'o','l','d',0};}
 if(n=="reset_failure")fail_set=2;
 std::promise<void> locked,release;auto future=release.get_future();std::thread holder;
 if(n=="busy_save"||n=="busy_reset"){holder=std::thread([&]{execution::Guard g;locked.set_value();future.wait();});locked.get_future().wait();}
 bool reset=n=="busy_reset"||n=="valid_reset"||n=="reset_failure"||n=="unloaded_reset";
 bool result=reset?settings::resetChecked():settings::saveChecked();
 if(holder.joinable()){release.set_value();holder.join();}
 if(n=="healthy_save"||n=="valid_autorun"||n=="valid_reset"){
  check(result&&settings::saveError()==ESP_OK,"healthy result");check(sets==12&&commits==1&&closes==1,"all keys and checked commit/close");check(persisted.size()==12,"schema preserved");
  if(n=="valid_autorun")check(persisted["autorun_enabled"][0]==1,"autorun healthy persistence");
 }else{
  check(!result&&settings::saveError()!=ESP_OK,"failure not fake success");
  if(fail_set){check(sets==fail_set&&commits==0&&closes==1,"stop immediately and close");check(persisted.size()>0||fail_set==1,"prefix may persist");}
  else if(n=="commit_failure"){check(sets==12&&commits==1&&closes==1&&persisted.size()==12,"commit failure not rollback");}
  else {check(sets==0&&commits==0&&closes==0,"no writes/commit after precondition/open failure");}
 }
 if(n=="failed_set_may_change_bytes")check(persisted.size()==3,"failed SDK call may have effects; not undone");
 if(n=="mixed_autorun_after_failure")check(persisted["autorun_enabled"][0]==1&&persisted["autorun_script"][0]=='o',"mixed valid-looking autorun remains possible");
 if(n=="set_flash_error")check(settings::saveError()==0x6001,"exact original failure retained");
 if(n=="set_full"||n=="open_full")check(settings::saveError()==ESP_ERR_NVS_NOT_ENOUGH_SPACE,"NVS full original error");
 for(const auto&s:diagnostics)check(s.find("harmless-fixture")==std::string::npos,"no setting values in diagnostics");
 std::cout<<"PASS "<<n<<" ("<<assertions<<" assertions)\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
