// Pinned C NVS API + lookup/manager/handle/partition/Storage/Page implementations.
// Flash/descriptors/iterator/chip dispatch/ROM CRC are adapters. The actual Linux
// lock branch is no-op; there is no RTOS/driver/global-constructor execution.
#pragma push_macro("main")
#undef main
#define main historical_stage19_main
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wreturn-type"
#include "../stage19/sdk_recovery.cpp"
#pragma GCC diagnostic pop
#undef main
#pragma pop_macro("main")
#include "esp_partition.h"
#include "nvs.h"
#include "nvs_flash.h"
#include "nvs_partition.hpp"
#include "nvs_partition_manager.hpp"

static Flash *backend;
static bool missing=false;
static esp_partition_t descriptor{nullptr,0x9000,0x5000,"nvs",false,true};
struct Attempt {const char *kind;size_t address,bytes;esp_err_t error;};
static std::vector<Attempt> attempts;
static unsigned lowerCalls=0;
static bool mainCallbackEnabled=true;
struct app_func_arg_t {bool no_protect=false;};
static app_func_arg_t mainArg;
using esp_partition_iterator_t = const esp_partition_t*;
constexpr unsigned ESP_PARTITION_TYPE_ANY=255,ESP_PARTITION_SUBTYPE_ANY=255;
static esp_partition_iterator_t esp_partition_find(unsigned,unsigned,const char*){return missing?nullptr:&descriptor;}
static esp_partition_iterator_t esp_partition_next(esp_partition_iterator_t){return nullptr;}
static const esp_partition_t *esp_partition_get(esp_partition_iterator_t it){return it;}
// NVS is outside bootloader/table/running app for this fixed reviewed geometry.
static bool esp_partition_main_flash_region_safe(size_t start,size_t n){return start>=0x9000 && start+n<=0xe000;}
#include "main_region_bodies.inc"
// Exact pinned esp_flash_api.c dispatch macro. Other unsafe ranges abort in the
// pinned configuration; these tests use the reviewed NVS range or direct checks.
#define UNSAFE_WRITE_ADDRESS std::abort()
#include "check_write_address.inc"
struct PolicyOs {esp_err_t (*region_protected)(void*,size_t,size_t);};
struct PolicyChip {PolicyOs *os_func;void *os_func_data;};
static esp_err_t recordMainRegion(void *arg,size_t address,size_t size){
 auto error=main_flash_region_protected(arg,address,size);
 if(error!=ESP_OK)attempts.push_back({"main_region",address,size,error});
 return error;
}
static esp_err_t checkMainRegion(size_t address,size_t size){
 PolicyOs os{mainCallbackEnabled?recordMainRegion:nullptr};PolicyChip value{&os,&mainArg};
 auto *chip=&value;CHECK_WRITE_ADDRESS(chip,address,size);return ESP_OK;
}
const esp_partition_t *esp_partition_find_first(unsigned type,unsigned subtype,const char *name){
 return !missing && type==1 && subtype==2 && std::string(name)=="nvs" ? &descriptor : nullptr;
}
uint32_t esp_partition_get_main_flash_sector_size(){return 4096;}
static esp_err_t esp_flash_read(void*,void *dst,size_t address,size_t size){
 if(address<0x9000)return ESP_ERR_INVALID_ARG;
 return backend->read_raw(address-0x9000,dst,size);
}
static esp_err_t esp_flash_write(void*,const void *src,size_t address,size_t size){
 auto error=checkMainRegion(address,size);if(error!=ESP_OK)return error;
 ++lowerCalls;if(address<0x9000)return ESP_ERR_INVALID_ARG;
 return backend->write(address-0x9000,src,size);
}
static esp_err_t esp_flash_erase_region(void*,size_t address,size_t size){
 auto error=checkMainRegion(address,size);if(error!=ESP_OK)return error;
 ++lowerCalls;if(address<0x9000)return ESP_ERR_INVALID_ARG;
 return backend->erase_range(address-0x9000,size);
}
#define SPI_FLASH_SEC_SIZE 4096
// Exact pinned target API bodies, symbol-renamed only for attempt recording.
#define esp_partition_write guarded_write_body
#define esp_partition_write_raw guarded_raw_body
#define esp_partition_erase_range guarded_erase_body
#include "partition_bodies.inc"
#undef esp_partition_write
#undef esp_partition_write_raw
#undef esp_partition_erase_range
esp_err_t esp_partition_write(const esp_partition_t *p,size_t off,const void *src,size_t n){
 auto e=guarded_write_body(p,off,src,n);attempts.push_back({"write",p->address+off,n,e});return e;
}
esp_err_t esp_partition_write_raw(const esp_partition_t *p,size_t off,const void *src,size_t n){
 auto e=guarded_raw_body(p,off,src,n);attempts.push_back({"write_raw",p->address+off,n,e});return e;
}
esp_err_t esp_partition_erase_range(const esp_partition_t *p,size_t off,size_t n){
 auto e=guarded_erase_body(p,off,n);attempts.push_back({"erase",p->address+off,n,e});return e;
}
static void seed(Flash &f,bool blob=false){
 nvs::Storage storage(&f);check(storage.init(0,5)==ESP_OK,"prepare synthetic storage");
 uint8_t ns=0;check(storage.createOrOpenNamespace("fixture",true,ns)==ESP_OK,"prepare namespace");
 uint8_t v=7;check(storage.writeItem(ns,nvs::ItemType::U8,"flag",&v,1)==ESP_OK,"prepare scalar");
 const char text[]="synthetic";check(storage.writeItem(ns,nvs::ItemType::SZ,"text",text,sizeof(text))==ESP_OK,"prepare string");
 if(blob){std::vector<uint8_t> value(8000,0x5a);check(storage.writeItem(ns,nvs::ItemType::BLOB,"blob",value.data(),value.size())==ESP_OK,"prepare cross-page blob");}
}
static size_t itemAt(Flash &f,unsigned type,const char *key=nullptr){
 for(unsigned p=0;p<5;++p)for(unsigned i=0;i<126;){
  size_t o=p*4096+64+i*32;unsigned bits=(f.data[p*4096+32+i/4]>>(i%4*2))&3;
  if(bits!=2){++i;continue;}
  unsigned span=f.data[o+2];check(span && span<=126-i,"fixture span");
  if(f.data[o+1]==type && (!key || std::strcmp(reinterpret_cast<const char*>(f.data.data()+o+8),key)==0))return o;i+=span;
 }
 throw std::runtime_error("fixture item absent");
}
static void protectedBytes(const Flash &f,const std::array<uint8_t,0x5000> &before){
 check(f.data==before,"entire synthetic NVS preserved");check(lowerCalls==0,"no lower flash write/erase reached");
 check(f.ops.empty(),"no physical-layer adapter operations");
 for(const auto &a:attempts){check(a.error==ESP_ERR_NOT_ALLOWED,"original NOT_ALLOWED propagated at partition boundary");check(a.address>=0x9000 && a.address<=0xe000 && a.bytes<=0xe000-a.address,"attempt inside protected region");}
}
int main(int argc,char **argv){try{
 check(argc==2,"case required");std::string name=argv[1];Flash f;backend=&f;
 bool blob=name=="readonly_cross_page_blob" || name=="readonly_corrupt_blob" || name=="readonly_blob_gap";
 seed(f,blob);
 if(name=="readonly_interrupted_entry")f.data[64+32*4]=0; // First empty entry after seed.
 if(name=="readonly_backend_write_error"){f.data[64+32*4]=0;f.failWrite=1;f.failErase=1;}
 if(name=="readonly_retry_failure")f.data[68]^=1;
 if(name=="readonly_bad_entry_crc")f.data[68]^=1;
 if(name=="readonly_bad_page_crc")f.data[28]^=1;
 if(name=="readonly_invalid_state")f.header(0,0x12345678,1);
 if(name=="readonly_freeing")f.header(0,0xfffffff8,1);
 if(name=="readonly_future_version")f.header(0,0xfffffffe,1,0xfd);
 if(name=="readonly_read_failure")f.failRead=f.reads+1;
 if(name=="readonly_partial_read")f.failRead=f.reads+2;
 if(name=="readonly_missing_partition")missing=true;
 if(name=="readonly_encrypted_partition")descriptor.encrypted=true;
 if(name=="readonly_empty_partition")f.data.fill(255);
 if(name=="readonly_no_free_page")for(unsigned p=0;p<5;++p)f.header(p,0xfffffffc,p+1);
 if(name=="readonly_gc_request")for(unsigned p=0;p<4;++p)f.header(p,0xfffffffc,p+1);
 if(name=="readonly_orphan_blob" || name=="readonly_mismatched_index"){
  nvs::Page p;check(p.load(&f,0)==ESP_OK,"load synthetic seed page");
  uint8_t value[8]={4,0,0,0,1,0,255,255};
  auto type=name=="readonly_orphan_blob"?nvs::ItemType::BLOB_DATA:nvs::ItemType::BLOB_IDX;
  check(p.writeItem(1,type,"orphan",value,type==nvs::ItemType::BLOB_DATA?4:8,type==nvs::ItemType::BLOB_DATA?0:255)==ESP_OK,"seed malformed relationship");
 }
 if(name=="readonly_corrupt_string" || name=="writable_readonly_handle_corrupt_string")f.data[itemAt(f,0x21)+32]^=1;
 if(name=="readonly_corrupt_blob")f.data[itemAt(f,0x42)+32]^=1;
 if(name=="readonly_blob_gap"){
  auto off=itemAt(f,0x42);f.data[off+3]=3;uint32_t c=esp_rom_crc32_le(0xffffffff,f.data.data()+off,4);c=esp_rom_crc32_le(c,f.data.data()+off+8,24);std::memcpy(f.data.data()+off+4,&c,4);
 }
 if(name=="writable_readonly_handle_corrupt_string")descriptor.readonly=false;
 f.ops.clear();f.writes=f.erases=0;attempts.clear();auto before=f.data;
 if(name=="region_scan_missing_table"){missing=true;check(esp_partition_is_flash_region_writable(0x9000,4),"exact readonly scanner returns writable on empty iterator; not a flash permission proof");protectedBytes(f,before);}
 else if(name=="main_region_no_protect"){mainArg.no_protect=true;check(main_flash_region_protected(&mainArg,0x9000,4)==ESP_ERR_NOT_ALLOWED,"dangerous-write switch cannot disable readonly region check");protectedBytes(f,before);}
 else if(name=="main_region_boundaries"){
  check(!esp_partition_is_flash_region_writable(0x9000,4),"NVS start protected");check(!esp_partition_is_flash_region_writable(0x8fff,2),"crossing NVS start protected");check(!esp_partition_is_flash_region_writable(0xdfff,2),"crossing NVS end protected");check(esp_partition_is_flash_region_writable(0xe000,1),"outside NVS not mistaken for NVS");protectedBytes(f,before);
 }else if(name=="readonly_partition_ptr" || name=="main_partition_ptr_alias_rejected"){
  auto alias=descriptor;alias.readonly=name=="readonly_partition_ptr";
  check(nvs_flash_init_partition_ptr(&alias)==ESP_OK,"actual caller-supplied partition API initialized");
  nvs_handle_t handle=0;auto open=nvs_open("fixture",NVS_READWRITE,&handle);
  if(alias.readonly){check(open==ESP_ERR_NOT_ALLOWED,"readonly supplied descriptor denies writable handle");protectedBytes(f,before);}
  else {check(open==ESP_OK,"supplied alias bypasses upper-layer readonly handle gate");check(nvs_set_u8(handle,"flag",9)==ESP_ERR_NOT_ALLOWED,"main-flash canonical table region rejects aliased backend");nvs_close(handle);protectedBytes(f,before);}
  // Pinned source's pointer initializer does not add this allocated Partition to
  // the manager-owned partition list. Explicit fixture-only cleanup after deinit.
  auto *part=const_cast<nvs::Partition*>(nvs::NVSPartitionManager::get_instance()->lookup_storage_from_name("nvs")->getPart());
  check(nvs_flash_deinit()==ESP_OK,"deinitialize synthetic pointer API storage");delete part;
 }else if(name=="main_direct_write_rejected" || name=="main_direct_erase_rejected" || name=="main_descriptor_alias_rejected" || name=="callback_missing_write" || name=="callback_missing_erase" || name=="canonical_flag_changed"){
  if(name=="callback_missing_write" || name=="callback_missing_erase")mainCallbackEnabled=false;
  if(name=="canonical_flag_changed")descriptor.readonly=false;
  uint8_t zeros[4]={};esp_err_t e;
  if(name=="main_direct_write_rejected" || name=="callback_missing_write" || name=="canonical_flag_changed")e=esp_flash_write(nullptr,zeros,0x9000,4);
  else if(name=="main_direct_erase_rejected" || name=="callback_missing_erase")e=esp_flash_erase_region(nullptr,0x9000,4096);
  else {auto alias=descriptor;alias.readonly=false;e=esp_partition_write(&alias,0,zeros,4);}
  if(name=="callback_missing_write" || name=="callback_missing_erase" || name=="canonical_flag_changed")check(e==ESP_OK && f.data!=before && lowerCalls==1,"missing callback or mutable canonical metadata permits synthetic mutation");
  else {check(e==ESP_ERR_NOT_ALLOWED,"actual main region callback rejects lower/alias access");protectedBytes(f,before);}
 }else if(name=="partition_api_write" || name=="partition_api_raw" || name=="partition_api_erase"){
  uint8_t zeros[16]={};auto e=name=="partition_api_write"?esp_partition_write(&descriptor,0,zeros,16):name=="partition_api_raw"?esp_partition_write_raw(&descriptor,0,zeros,16):esp_partition_erase_range(&descriptor,0,4096);
  check(e==ESP_ERR_NOT_ALLOWED,"ordinary target partition API denies readonly");protectedBytes(f,before);
 }else if(name=="readonly_gc_request"){
  nvs::NVSPartition part(&descriptor);nvs::PageManager manager;check(manager.load(&part,0,5)==ESP_OK,"load source manager");
  auto e=manager.requestNewPage();std::cout<<"RESULT "<<e<<"\n";check(e==ESP_ERR_NOT_ALLOWED && !attempts.empty(),"actual GC state transition denied");protectedBytes(f,before);
 }else {
  auto e=nvs_flash_init();std::cout<<"RESULT "<<e<<"\n";
  if(name=="readonly_clean" || name=="readonly_repeat" || name=="readonly_cross_page_blob" || name=="readonly_corrupt_string" || name=="readonly_corrupt_blob" || name=="readonly_blob_gap" || name=="readonly_orphan_blob" || name=="readonly_mismatched_index" || name=="readonly_freeing" || name=="readonly_no_free_page" || name=="readonly_empty_partition" || name=="readonly_open_write" || name=="readonly_set" || name=="readonly_erase_api" || name=="writable_readonly_handle_corrupt_string"){
   check(e==ESP_OK,"documented source init result");
   nvs_handle_t handle=0;
   if(name=="readonly_open_write")check(nvs_open("fixture",NVS_READWRITE,&handle)==ESP_ERR_NOT_ALLOWED,"API rejects writable handle");
   else if(name=="readonly_erase_api")check(nvs_flash_erase()==ESP_ERR_NOT_ALLOWED,"API denies partition erase");
   else if(name!="readonly_empty_partition" && name!="readonly_mismatched_index" && name!="readonly_orphan_blob"){
    check(nvs_open("fixture",NVS_READONLY,&handle)==ESP_OK,"API opens existing namespace");
    if(name=="readonly_set")check(nvs_set_u8(handle,"flag",9)==ESP_ERR_NVS_READ_ONLY,"API denies readonly handle setter");
    else if(name=="readonly_corrupt_string" || name=="writable_readonly_handle_corrupt_string"){
     char buffer[10];size_t size=sizeof(buffer);auto r=nvs_get_str(handle,"text",buffer,&size);std::cout<<"READ_RESULT "<<r<<"\n";
     check(r== (descriptor.readonly?ESP_ERR_NOT_ALLOWED:ESP_ERR_NVS_NOT_FOUND),"read cleanup status source evidence");
    }else if(blob){std::vector<uint8_t> value(8000);size_t n=value.size();auto r=nvs_get_blob(handle,"blob",value.data(),&n);std::cout<<"READ_RESULT "<<r<<"\n";if(name=="readonly_cross_page_blob")check(r==ESP_OK && n==8000 && std::all_of(value.begin(),value.end(),[](uint8_t b){return b==0x5a;}),"exact cross-page blob read");else check(r!=ESP_OK,"corrupt blob not accepted");}
    else {uint8_t value=0;check(nvs_get_u8(handle,"flag",&value)==ESP_OK && value==7,"API reads healthy setting");}
    nvs_close(handle);
   }
   if(name=="readonly_repeat")for(unsigned i=0;i<10;++i)check(nvs_flash_init()==ESP_OK,"repeat initialized API");
  }else {check(e!=ESP_OK,"failed initialization not fabricated as success");if(name=="readonly_retry_failure")for(unsigned i=0;i<10;++i)check(nvs_flash_init()==e,"repeated failed API initialization preserves original result");}
  if(name=="writable_readonly_handle_corrupt_string")check(f.data!=before && lowerCalls>0,"readonly handle permits SDK read mutation on writable partition");
  else protectedBytes(f,before);
  auto deinit=nvs_flash_deinit();check(deinit==ESP_OK || deinit==ESP_ERR_NVS_NOT_INITIALIZED,"bounded deinitialization result");
  if(descriptor.readonly)protectedBytes(f,before);
 }
 for(auto a:attempts)std::cout<<"ATTEMPT "<<a.kind<<" "<<a.address<<" "<<a.bytes<<" "<<a.error<<"\n";
 for(auto op:f.ops)std::cout<<"LOWER "<<op.kind<<" "<<op.address<<" "<<op.bytes<<" "<<op.success<<"\n";
 std::cout<<"PASS "<<name<<" ("<<assertions<<" assertions)\n";
 return 0;
}catch(const std::exception &e){std::cerr<<e.what()<<'\n';return 1;}}
