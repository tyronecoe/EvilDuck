// Native lower boot metadata only, never target firmware.
#include "esp_partition.h"
#include <cstring>
esp_flash_t chip;esp_flash_t *esp_flash_default_chip=&chip;
static esp_partition_t table[6];static unsigned index_=0;
extern "C" int32_t evilduck_nvs_startup_error(){return 0;}
namespace debug{void begin(){}}
static void initialize(){
 const char* names[]={"nvs","otadata","app0","app1","spiffs","coredump"};
 uint32_t offsets[]={0x9000,0xe000,0x10000,0x750000,0xe90000,0xff0000},sizes[]={0x5000,0x2000,0x740000,0x740000,0x160000,0x10000};
 uint8_t types[]={1,1,0,0,1,1},subtypes[]={2,0,0x10,0x11,0x82,3};
 for(unsigned i=0;i<6;++i){table[i]={&chip,types[i],subtypes[i],offsets[i],sizes[i],{},false,false};std::strcpy(table[i].label,names[i]);}
}
esp_partition_iterator_t esp_partition_find(unsigned,unsigned,const char*){initialize();index_=0;return &index_;}
esp_partition_iterator_t esp_partition_next(esp_partition_iterator_t it){if(++*it<6)return it;return nullptr;}
const esp_partition_t* esp_partition_get(esp_partition_iterator_t it){return &table[*it];}
void esp_partition_iterator_release(esp_partition_iterator_t){}
