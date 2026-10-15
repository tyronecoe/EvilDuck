// Synthetic typed NVS boundary only; no SDK recovery or flash emulation claimed.
#include "nvs.h"
#include <string>
#include <cstring>
namespace nvsMock {unsigned reads=0,writes=0,opens=0,commits=0;bool fail=false;}
extern "C" esp_err_t nvs_open(const char*,nvs_open_mode_t,nvs_handle_t*h){++nvsMock::opens;*h=1;return nvsMock::fail?ESP_FAIL:ESP_OK;}
extern "C" void nvs_close(nvs_handle_t){}
extern "C" esp_err_t nvs_get_u8(nvs_handle_t,const char*,uint8_t*){++nvsMock::reads;return ESP_ERR_NVS_NOT_FOUND;}
extern "C" esp_err_t nvs_get_u16(nvs_handle_t,const char*,uint16_t*){++nvsMock::reads;return ESP_ERR_NVS_NOT_FOUND;}
extern "C" esp_err_t nvs_get_u32(nvs_handle_t,const char*,uint32_t*){++nvsMock::reads;return ESP_ERR_NVS_NOT_FOUND;}
extern "C" esp_err_t nvs_get_str(nvs_handle_t,const char*k,char*out,size_t*n){++nvsMock::reads;std::string s;
 if(std::string(k)=="ap_ssid")s=std::string(12,'s');else if(std::string(k)=="ap_password")s=std::string(16,'p');else if(std::string(k)=="web_pw")s=std::string(16,'w');else return ESP_ERR_NVS_NOT_FOUND;
 if(!out){*n=s.size()+1;return ESP_OK;}if(*n<s.size()+1)return ESP_ERR_NVS_INVALID_LENGTH;std::memcpy(out,s.c_str(),s.size()+1);*n=s.size()+1;return ESP_OK;}
extern "C" esp_err_t nvs_set_u8(nvs_handle_t,const char*,uint8_t){++nvsMock::writes;return ESP_OK;}
extern "C" esp_err_t nvs_set_u16(nvs_handle_t,const char*,uint16_t){++nvsMock::writes;return ESP_OK;}
extern "C" esp_err_t nvs_set_u32(nvs_handle_t,const char*,uint32_t){++nvsMock::writes;return ESP_OK;}
extern "C" esp_err_t nvs_set_str(nvs_handle_t,const char*,const char*){++nvsMock::writes;return ESP_OK;}
extern "C" esp_err_t nvs_commit(nvs_handle_t){++nvsMock::commits;return ESP_OK;}
