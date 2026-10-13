// Pinned iterator/scanner/callback bodies, actual malloc/free; synthetic table/locks.
#include <cassert>
#include <cstdlib>
#include <cstring>
#include <cstdint>
#include <iostream>
#include <atomic>
#include <mutex>
#include <thread>
#include <vector>
#include <sys/queue.h>
using esp_err_t=int;
constexpr int ESP_OK=0, ESP_FAIL=-1,ESP_ERR_NOT_ALLOWED=0x10d,ESP_ERR_NOT_SUPPORTED=0x106;
using esp_partition_type_t=unsigned;using esp_partition_subtype_t=unsigned;
constexpr unsigned ESP_PARTITION_TYPE_ANY=255,ESP_PARTITION_SUBTYPE_ANY=255;
struct esp_partition_t{unsigned type,subtype,address,size;char label[17];bool readonly;};
#include "iterator_types.inc"
static SLIST_HEAD(partition_list_head_, partition_list_item_) s_partition_list = SLIST_HEAD_INITIALIZER(s_partition_list);
static std::mutex s_partition_list_lock,allocationLock;
static void _lock_acquire(std::mutex *m){m->lock();}static void _lock_release(std::mutex *m){m->unlock();}
using esp_partition_iterator_t=esp_partition_iterator_opaque_t*;
static std::atomic<unsigned> creates{0},released{0},allocFailed{0},advances{0},gets{0};
static bool failAllocation=false,failLoad=false;
static std::vector<void*> fixtureOwned;
static void *countMalloc(size_t n){if(failAllocation){++allocFailed;return nullptr;}void*p=std::malloc(n);if(p){++creates;std::lock_guard<std::mutex> g(allocationLock);fixtureOwned.push_back(p);}return p;}
static void countFree(void*p){if(p){++released;std::lock_guard<std::mutex> g(allocationLock);for(auto &q:fixtureOwned)if(q==p){q=nullptr;break;}}std::free(p);}
static esp_err_t ensure_partitions_loaded(){return failLoad?ESP_FAIL:ESP_OK;}
static esp_partition_iterator_t esp_partition_next(esp_partition_iterator_t);
static void esp_partition_iterator_release(esp_partition_iterator_t);
static const esp_partition_t *esp_partition_get(esp_partition_iterator_t);
#define malloc countMalloc
#define free countFree
#include "iterator_bodies.inc"
#undef malloc
#undef free
static esp_partition_iterator_t esp_partition_next(esp_partition_iterator_t it){++advances;return underlying_next(it);}
static const esp_partition_t *esp_partition_get(esp_partition_iterator_t it){++gets;return underlying_get(it);}
#include "scanner_body.inc"
#define CONFIG_SPI_FLASH_DANGEROUS_WRITE_ALLOWED 0
struct app_func_arg_t{bool no_protect=false;};
static bool esp_partition_main_flash_region_safe(size_t a,size_t n){return a>=0x9000 && n<=0xe000-a;}
#include "callback_body.inc"
static unsigned lowerCalls=0;
static unsigned assertions=0;
static void check(bool c,const char*m){++assertions;if(!c)throw std::runtime_error(m);}
static partition_list_item_t parts[4];
static void table(unsigned count){SLIST_INIT(&s_partition_list);for(unsigned i=count;i>0;--i){auto &p=parts[i-1];p={};p.info.type=1;p.info.subtype=2;p.info.address=0x9000+(i-1)*0x10000;p.info.size=0x5000;std::strcpy(p.info.label,"nvs");p.info.readonly=true;SLIST_INSERT_HEAD(&s_partition_list,&p,next);}}
int main(int argc,char**argv){try{
 check(argc==2,"case required");std::string name=argv[1];table(1);unsigned repetitions=1;bool allowed=false;size_t address=0x9000,size=1;
 if(name=="partial_start"){address=0x8fff;size=2;}
 if(name=="partial_end"){address=0xdfff;size=2;}
 if(name=="unprotected" || name=="exhausted"){address=0xe000;size=1;allowed=true;}
 if(name=="writable_table"){parts[0].info.readonly=false;allowed=true;}
 if(name=="multiple_protected"){table(3);address=0x29000;}
 if(name=="missing_table" || name=="null_iterator"){table(0);allowed=true;}
 if(name=="allocation_failure"){failAllocation=true;allowed=true;}
 if(name=="load_failure"){failLoad=true;allowed=true;}
 if(name=="invalid_metadata"){parts[0].info.size=0;allowed=true;}
 if(name=="metadata_overflow"){parts[0].info.address=0xfffffff0;parts[0].info.size=0x100;allowed=true;}
 if(name=="range_overflow"){address=0xfffffff0;size=0x100;allowed=true;}
 if(name=="wide_host_address"){address=static_cast<size_t>(UINT32_MAX)+1;allowed=true;}
 if(name=="zero_protected")size=0;
 if(name=="zero_writable"){address=0xe000;size=0;allowed=true;}
 if(name=="ota_metadata"){address=0xe000;size=0x2000;allowed=true;}
 if(name=="other_app"){address=0x750000;size=0x1000;allowed=true;}
 if(name=="fresh_spiffs"){address=0xe90000;size=0x1000;allowed=true;}
 if(name=="coredump"){address=0xff0000;size=0x1000;allowed=true;}
#if PATCHED
 if(name=="allocation_failure"||name=="load_failure"||name=="missing_table"||name=="null_iterator"||name=="invalid_metadata"||name=="metadata_overflow"||name=="range_overflow"||name=="wide_host_address")allowed=false;
#endif
 if(name=="repeated_write" || name=="repeated_erase" || name=="alias" || name=="leak_probe")repetitions=128;
 app_func_arg_t arg;
 if(name=="concurrent_immutable_table"){
  std::vector<std::thread> workers;std::atomic<unsigned> denied{0};
  for(unsigned t=0;t<4;++t)workers.emplace_back([&]{for(unsigned i=0;i<128;++i)if(main_flash_region_protected(&arg,0x9000,1)==ESP_ERR_NOT_ALLOWED)++denied;});
  for(auto &t:workers)t.join();check(denied==512,"immutable-table concurrent source path denies every call");repetitions=512;
 }else for(unsigned i=0;i<repetitions;++i){
  auto e=main_flash_region_protected(&arg,address,size);
  // Outside the synthetic safe NVS range callback returns NOT_SUPPORTED; scanner
  // decision is checked separately without creating an additional owned iterator.
  if(!allowed)check(e==ESP_ERR_NOT_ALLOWED,"readonly callback original denial unchanged");
  else check(e!=ESP_ERR_NOT_ALLOWED,"original nonoverlap/failure scanner decision unchanged");
  if(!PATCHED && (name=="allocation_failure" || name=="load_failure" || name=="missing_table" || name=="null_iterator"))check(e==ESP_OK,"actual source callback permits the synthetic safe NVS range on lookup/allocation failure; retained risk");
  if(i==0)std::cout<<"CALLBACK_RESULT "<<e<<"\n";
 }
 if(name!="concurrent_immutable_table") {
   bool result=esp_partition_is_flash_region_writable(address,size);
   check(result==allowed,"actual scanner permission matches specified boundary");
   if(result && size && address<0x1000000 && size<=0x1000000-address)++lowerCalls;
   check(lowerCalls==(allowed && size && address<0x1000000 && size<=0x1000000-address ? 1u:0u),"scanner-adapter lower dispatch accounting");
   std::cout<<"REQUEST "<<address<<" "<<size<<" "<<result<<" LOWER "<<lowerCalls<<"\n";
 }
 unsigned retained=creates-released;
#if PATCHED
 check(retained==0,"corrected scanner retains no iterator");
#else
 check(retained==(!allowed?repetitions+(name!="concurrent_immutable_table"):0),"unpatched ownership count");
#endif
 if(PATCHED)check(creates==released,"all successfully allocated iterators released");
 check(s_partition_list_lock.try_lock(),"iterator does not retain list lock");s_partition_list_lock.unlock();
 std::cout<<"COUNTERS "<<creates<<" "<<released<<" "<<retained<<" "<<allocFailed<<" "<<sizeof(esp_partition_iterator_opaque_t)<<" "<<advances<<" "<<gets<<"\n"<<std::flush;
 // Separate LSan process intentionally loses pointers to demonstrate ownership loss.
 if(name=="leak_probe"){
  for(auto&q:fixtureOwned)q=nullptr;fixtureOwned.clear();fixtureOwned.shrink_to_fit();
 }else{for(auto p:fixtureOwned)if(p)std::free(p);fixtureOwned.clear();}
 std::cout<<"PASS "<<name<<" ("<<assertions<<" assertions)\n"<<std::flush;
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
