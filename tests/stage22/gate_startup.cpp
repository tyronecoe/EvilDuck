// Actual SDK plaintext C API + exact candidate gate/initArduino/setup/loop.
// Descriptor/flash/iterator/USB/RTOS adapters remain synthetic.
#define esp_partition_find stage21_find
#define esp_partition_next stage21_next
#define esp_partition_get stage21_get
#define esp_flash_read stage21_read
#define main stage21_component_main
#include "../stage21/nvs_readonly.cpp"
#undef main
#undef esp_partition_find
#undef esp_partition_next
#undef esp_partition_get
#undef esp_flash_read
#include "esp_flash.h"
#include "Arduino.h"
#include <algorithm>
static esp_flash_os_functions_t gateOs{recordMainRegion};
static esp_flash_t gateChip{&gateOs,&mainArg};
esp_flash_t *esp_flash_default_chip=&gateChip;
static esp_partition_t table[7];
static unsigned tableCount=6, cursor=0, iteratorLive=0, releases=0, initCalls=0;
static bool iterationFails=false, getFails=false, verifyFails=false, tableReadFails=false;
static std::vector<unsigned char> tableBytes;
static esp_partition_iterator_t esp_partition_find(unsigned,unsigned,const char*){
 if(iterationFails)return nullptr;check(iteratorLive==0,"no overlapping iterator ownership");++iteratorLive;cursor=0;return table;
}
static const esp_partition_t *esp_partition_get(esp_partition_iterator_t it){return getFails?nullptr:it;}
static void esp_partition_iterator_release(esp_partition_iterator_t it){if(it){check(iteratorLive==1,"release owned iterator");--iteratorLive;++releases;}}
static esp_partition_iterator_t esp_partition_next(esp_partition_iterator_t it){if(++cursor<tableCount)return table+cursor;esp_partition_iterator_release(it);return nullptr;}
static const esp_partition_t *esp_partition_verify(const esp_partition_t *p){return verifyFails?nullptr:p;}
static esp_err_t esp_flash_read(void *chip,void *dst,size_t address,size_t size){
 if(address>=0x8000 && address+size<=0x8c00){if(tableReadFails)return ESP_FAIL;std::memcpy(dst,tableBytes.data()+address-0x8000,size);return ESP_OK;}
 return stage21_read(chip,dst,address,size);
}
#include "evilduck_nvs_gate.h"
static esp_err_t counted_initializer(){++initCalls;return nvs_flash_init();}
static unsigned hooks=0;static std::vector<std::string> services;static esp_err_t diagnostic=ESP_OK;
constexpr int CONFIG_LOG_DEFAULT_LEVEL=0;
void esp_log_level_set(const char*,int){}void init(){++hooks;}void initVariant(){++hooks;}
void logError(const char*,esp_err_t e){diagnostic=e;}
#define log_e(...) logError(__VA_ARGS__)
#define nvs_flash_init counted_initializer
extern "C" {
#include "candidate_startup.inc"
}
#undef nvs_flash_init
#include "../../EvilDuckS3/settings.cpp"
#include "../../EvilDuckS3/EvilDuckS3.ino"
void delay(uint32_t){}uint32_t millis(){return 0;}uint32_t esp_random(){return 0;}
static bool diagnosticsUnavailable=false;
namespace debug{void begin(){if(!diagnosticsUnavailable)services.push_back("debug");}void info(const String&){if(!diagnosticsUnavailable)services.push_back("diagnostic");}}
namespace led{void begin(){services.push_back("led");}void setColor(int,int,int){}}
namespace hid_backend{void begin(){services.push_back("hid");}}
namespace keyboard_locale{void begin(){services.push_back("locale");}}
namespace attackmode{void begin(){services.push_back("msc");}}
namespace storage{bool begin(){services.push_back("filesystem");return true;}}
namespace script_library{void installIfNeeded(){services.push_back("file-write");}}
namespace cli{void begin(){services.push_back("cli");}void update(){services.push_back("cli-update");}}
namespace webserver{void begin(){services.push_back("web");}}
namespace duckscript{bool run(const String&){services.push_back("payload-spy");return true;}void update(){services.push_back("script-update");}}
namespace com{void update(){services.push_back("com-update");}}
static esp_err_t permissive(void*,size_t,size_t){return ESP_OK;}
int main(int argc,char**argv){try{
 check(argc==2,"case required");std::string name=argv[1];Flash f;backend=&f;seed(f,name=="cross_page_blob");
 tableBytes.assign(evilduck_expected_table,evilduck_expected_table+sizeof(evilduck_expected_table));
 const char* labels[]={"nvs","otadata","app0","app1","spiffs","coredump"};unsigned types[]={1,1,0,0,1,1},subtypes[]={2,0,0x10,0x11,0x82,3};unsigned offsets[]={0x9000,0xe000,0x10000,0x750000,0xe90000,0xff0000},sizes[]={0x5000,0x2000,0x740000,0x740000,0x160000,0x10000};
 for(unsigned i=0;i<6;++i){table[i]=descriptor;table[i].flash_chip=&gateChip;table[i].type=types[i];table[i].subtype=subtypes[i];table[i].address=offsets[i];table[i].size=sizes[i];std::strcpy(table[i].label,labels[i]);table[i].readonly=i==0;}
 descriptor.flash_chip=&gateChip;
 const bool rejected=name.rfind("reject_",0)==0;
 if(name=="reject_missing_descriptor"){table[0]=table[1];}
 if(name=="reject_writable" || name=="reject_altered_flag")table[0].readonly=false;
 if(name=="reject_offset")table[0].address+=0x1000;
 if(name=="reject_size")table[0].size-=0x1000;
 if(name=="reject_type")table[0].type=0;
 if(name=="reject_subtype")table[0].subtype=0;
 if(name=="reject_duplicate"){tableCount=7;table[6]=table[0];}
 if(name=="reject_conflicting"){table[1]=table[0];table[1].address+=4096;}
 if(name=="reject_missing_table" || name=="reject_oom")iterationFails=true;
 if(name=="reject_get_failure")getFails=true;
 if(name=="reject_short_iteration")tableCount=5;
 if(name=="reject_canonical")verifyFails=true;
 if(name=="reject_wrong_chip")table[0].flash_chip=nullptr;
 if(name=="reject_no_chip")esp_flash_default_chip=nullptr;
 if(name=="reject_no_callback")gateOs.region_protected=nullptr;
 if(name=="reject_no_os")gateChip.os_func=nullptr;
 if(name=="reject_permissive_callback")gateOs.region_protected=permissive;
 if(name=="reject_table_bytes")tableBytes[32]^=1;
 if(name=="reject_integrity_md5")tableBytes[208]^=1;
 if(name=="reject_table_read")tableReadFails=true;
 if(name=="reject_encrypted")table[0].encrypted=true;
 if(name=="reject_erase_geometry")table[0].erase_size=65536;
 if(name=="reject_other_partition_flags")table[2].readonly=true;
 if(name=="reject_old_slots")table[2].size=0x140000;
 if(name=="bad_page")f.data[28]^=1;
 if(name=="future_version")f.header(0,0xfffffffe,1,0xfd);
 if(name=="freeing")f.header(0,0xfffffff8,1);
 if(name=="interrupted")f.data[64+32*4]=0;
 if(name=="read_error")f.failRead=f.reads+1;
 if(name=="corrupt_string")f.data[itemAt(f,0x21,"text")+32]^=1;
 if(name=="diagnostics_unavailable")diagnosticsUnavailable=true;
 f.ops.clear();f.writes=f.erases=0;attempts.clear();auto before=f.data;
 initArduino();auto error=evilduck_nvs_startup_error();
 std::cout<<"SDK_STARTUP_RESULT "<<error<<"\n";
 if(error!=ESP_OK)check(hooks==0,"no variant hooks after any startup failure");
 check(initCalls==(rejected?0u:1u),"rejected metadata never invokes actual NVS C initializer");
 if(rejected){check(error!=ESP_OK && evilduck_nvs_gate_failure()!=0,"meaningful gate failure latched");check(hooks==0,"variant hooks suppressed");}
 if(!rejected && error==ESP_OK){check(hooks==2,"healthy native core hook path");if(name=="corrupt_string"){nvs_handle_t h;check(nvs_open("fixture",NVS_READONLY,&h)==ESP_OK,"open actual readonly namespace");char text[32];size_t n=sizeof(text);check(nvs_get_str(h,"text",text,&n)==ESP_ERR_NOT_ALLOWED,"read cleanup cannot write");nvs_close(h);}}
 setup();check(startupNvsError==error,"application retains exact gate/SDK error without successful substitution");
 for(unsigned i=0;i<10000;++i)loop();
 check(services==(diagnosticsUnavailable?std::vector<std::string>{}:std::vector<std::string>{"debug","diagnostic"}),"production safe setup/loop quiescence, no mounts/HID/settings/payload");check(!settings::ready(),"settings never loaded");check(iteratorLive==0,"gate iterator ownership released");
 if(!rejected && error==ESP_OK && name=="write_erase"){
  uint8_t value=1;check(esp_partition_write(&descriptor,0,&value,1)==ESP_ERR_NOT_ALLOWED,"partition write blocked");check(esp_partition_erase_range(&descriptor,0,4096)==ESP_ERR_NOT_ALLOWED,"partition erase blocked");
  check(esp_flash_write(&gateChip,&value,0x9000,1)==ESP_ERR_NOT_ALLOWED,"main write blocked");check(esp_flash_erase_region(&gateChip,0x9000,4096)==ESP_ERR_NOT_ALLOWED,"main erase blocked");
  auto alias=descriptor;alias.readonly=false;check(esp_partition_write(&alias,0,&value,1)==ESP_ERR_NOT_ALLOWED,"alias main callback blocked");
 }
 initArduino();check(initCalls==(rejected?0u:1u) && evilduck_nvs_gate_failure()==1,"no repeated initialization or unbounded retry");check(evilduck_nvs_startup_error()==ESP_ERR_INVALID_STATE,"repeat fails closed");
 protectedBytes(f,before);
 for(auto a:attempts)std::cout<<"ATTEMPT "<<a.kind<<" "<<a.address<<" "<<a.bytes<<" "<<a.error<<"\n";
 std::cout<<"INIT_CALLS "<<initCalls<<"\n";std::cout<<"PASS "<<name<<" ("<<assertions<<" assertions)\n";
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
