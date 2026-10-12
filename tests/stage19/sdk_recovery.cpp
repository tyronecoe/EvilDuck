#include "nvs_pagemanager.hpp"
#include "nvs_storage.hpp"
#include "esp_rom_crc.h"
#include <array>
#include <iostream>
#include <vector>
#include <stdexcept>
#include <string>
#include <cstring>
static unsigned assertions=0;
void check(bool x,const char*s){++assertions;if(!x)throw std::runtime_error(s);}
struct Operation {const char* kind;size_t address,bytes;bool success;};
class Flash:public nvs::Partition {
 public:
 std::array<uint8_t,0x5000> data;
 std::vector<Operation> ops;
 int reads=0,failRead=0,failWrite=0,failErase=0,writes=0,erases=0;
 Flash(){data.fill(255);}
 const char*get_partition_name()override{return "synthetic";}
 uint32_t get_address()override{return 0x9000;}
 uint32_t get_size()override{return data.size();}
 bool get_readonly()override{return false;}
 esp_err_t read_raw(size_t o,void*d,size_t n)override{++reads;if(o>data.size()||n>data.size()-o)return ESP_FAIL;if(reads==failRead){if(n)std::memcpy(d,data.data()+o,n/2);return ESP_FAIL;}std::memcpy(d,data.data()+o,n);return ESP_OK;}
 esp_err_t read(size_t o,void*d,size_t n)override{return read_raw(o,d,n);}
 esp_err_t write(size_t o,const void*s,size_t n)override{++writes;bool ok=o<=data.size()&&n<=data.size()-o&&writes!=failWrite;ops.push_back({"write",0x9000+o,n,ok});if(!ok)return ESP_FAIL;for(size_t i=0;i<n;++i)data[o+i]&=static_cast<const uint8_t*>(s)[i];return ESP_OK;}
 esp_err_t write_raw(size_t o,const void*s,size_t n)override{return write(o,s,n);}
 esp_err_t erase_range(size_t o,size_t n)override{++erases;bool ok=o<=data.size()&&n<=data.size()-o&&o%4096==0&&n%4096==0&&erases!=failErase;ops.push_back({"erase",0x9000+o,n,ok});if(!ok)return ESP_FAIL;std::fill(data.begin()+o,data.begin()+o+n,255);return ESP_OK;}
 void header(unsigned p,uint32_t state,uint32_t seq,uint8_t version=0xfe){size_t o=p*4096;std::memcpy(data.data()+o,&state,4);std::memcpy(data.data()+o+4,&seq,4);data[o+8]=version;uint32_t c=esp_rom_crc32_le(0xffffffff,data.data()+o+4,24);std::memcpy(data.data()+o+28,&c,4);}
 void item(unsigned p,unsigned i,bool good=true){nvs::Item x(1,nvs::ItemType::U8,1,"synthetic-key");x.data[0]=7;x.crc32=x.calculateCrc32();if(!good)x.crc32^=1;std::memcpy(data.data()+p*4096+64+32*i,&x,32);data[p*4096+32+i/4]&=~(1u<<((i%4)*2));}
};
int main(int argc,char**argv){try{check(argc==2,"case required");std::string n=argv[1];Flash f;
 if(n.rfind("storage_",0)==0){
  nvs::Page creator;check(creator.load(&f,0)==ESP_OK,"seed page load");
  uint8_t payload[4]={1,2,3,0};
  if(n=="storage_orphan_blob"||n=="storage_orphan_write_failure")check(creator.writeItem(1,nvs::ItemType::BLOB_DATA,"synthetic",payload,4,0)==ESP_OK,"seed orphan blob");
  if(n=="storage_mismatched_index") {uint8_t index[8]={4,0,0,0,1,0,255,255};check(creator.writeItem(1,nvs::ItemType::BLOB_IDX,"synthetic",index,8)==ESP_OK,"seed index");}
  if(n=="storage_corrupt_string_read"){check(creator.writeItem(1,nvs::ItemType::SZ,"synthetic",payload,4)==ESP_OK,"seed string");f.data[96]^=1;}
  f.ops.clear();f.writes=0;f.erases=0;auto before=f.data;
  if(n=="storage_orphan_write_failure")f.failWrite=1;
  nvs::Storage storage(&f);esp_err_t error=storage.init(0,5);
  check(error==ESP_OK,"storage init result");
  if(n=="storage_corrupt_string_read") {check(f.ops.empty(),"initialization does not validate payload CRC");uint8_t out[4];check(storage.readItem(1,nvs::ItemType::SZ,"synthetic",out,4)!=ESP_OK,"corrupt string rejected by read");check(f.writes>0&&f.data!=before,"read recovery writes erased entry bits");}
  else if(n=="storage_clean"||n=="storage_repeat_clean"){check(f.ops.empty()&&f.data==before,"clean storage no mutation");if(n=="storage_repeat_clean")check(storage.init(0,5)==ESP_OK&&f.ops.empty(),"same storage repeated init");}
  else {check(f.writes>0,"blob cleanup attempted write");if(n=="storage_orphan_write_failure")check(f.data==before,"failed cleanup ignored and no mutation simulated");else check(f.data!=before,"blob cleanup changed bits");}
  for(auto op:f.ops)check(op.address>=0x9000&&op.address+op.bytes<=0xe000,"storage operations bounded");
  std::cout<<"PASS "<<n<<" ("<<assertions<<" assertions)\n";for(auto op:f.ops)std::cout<<"OP "<<op.kind<<" "<<op.address<<" "<<op.bytes<<" "<<op.success<<"\n";return 0;
 }
 if(n!="erased_partition")f.header(0,0xfffffffe,1);
 if(n=="freeing_recovery"||n=="freeing_write_failure"||n=="freeing_erase_failure"){f.header(0,0xfffffff8,1);f.item(0,0);f.header(1,0xfffffffe,2);if(n=="freeing_write_failure")f.failWrite=1;if(n=="freeing_erase_failure")f.failErase=1;}
 else if(n=="incomplete_entry"||n=="incomplete_write_failure"){f.data[64]=0;if(n=="incomplete_write_failure")f.failWrite=1;}
 else if(n=="bad_entry_crc")f.item(0,0,false);
 else if(n=="valid_entry")f.item(0,0);
 else if(n=="duplicate_entries"){f.item(0,0);f.item(0,1);}
 else if(n=="corrupt_only"){f.header(0,0xfffffffe,1);f.data[28]^=1;for(unsigned p=1;p<5;++p){f.header(p,0xfffffffe,p+1);f.data[p*4096+28]^=1;}}
 else if(n=="new_version")f.header(0,0xfffffffe,1,0xfd);
 else if(n=="partial_header_read")f.failRead=1;
 else if(n=="partial_table_read")f.failRead=2;
 else if(n=="mutation_before_later_read_failure"){f.data[64]=0;f.failRead=6;}
 else if(n=="no_free_pages")for(unsigned p=0;p<5;++p)f.header(p,0xfffffffc,p+1);
 auto before=f.data;nvs::PageManager manager;esp_err_t e=manager.load(&f,0,5);
 for(auto op:f.ops)check(op.address>=0x9000&&op.address+op.bytes<=0xe000,"all SDK flash operations bounded to NVS");
 if(n=="freeing_recovery"){check(e==ESP_OK,"freeing succeeds");check(f.erases>=2&&f.writes>0,"recovery erases and writes");}
 else if(n=="freeing_erase_failure"){check(e!=ESP_OK&&f.erases==1,"erase failure returned");}
 else if(n=="freeing_write_failure"){check(e!=ESP_OK&&f.writes==1,"write failure returned after erase");check(f.erases==1,"erase already occurred");}
 else if(n=="incomplete_write_failure"){check(e!=ESP_OK&&f.writes==1,"entry recovery write failure returned");}
 else if(n=="incomplete_entry"||n=="bad_entry_crc"||n=="duplicate_entries"){check(e==ESP_OK&&f.writes>0,"entry recovery writes before success");check(f.data!=before,"bytes changed");}
 else if(n=="corrupt_only"){check(e==ESP_OK&&f.erases==1,"corrupt page erased on activation");}
 else if(n=="new_version"){check(e==ESP_ERR_NVS_NEW_VERSION_FOUND&&f.ops.empty(),"new version error no page ops");}
 else if(n=="partial_header_read"||n=="partial_table_read"){check(e!=ESP_OK&&f.ops.empty(),"read failure no preceding mutation in this case");}
 else if(n=="mutation_before_later_read_failure"){check(e!=ESP_OK&&f.writes>0,"mutation precedes later failure");}
 else if(n=="no_free_pages"){check(e==ESP_ERR_NVS_NO_FREE_PAGES,"no-free-pages error");}
 else {check(e==ESP_OK&&f.ops.empty()&&f.data==before,"clean source load no flash mutation");}
 if(n=="incomplete_entry"){auto after=f.data;auto opcount=f.ops.size();check(manager.load(&f,0,5)==ESP_OK&&f.data==after&&f.ops.size()==opcount,"second initialization observes repaired data");}
 std::cout<<"PASS "<<n<<" ("<<assertions<<" assertions)\n";
 for(auto op:f.ops)std::cout<<"OP "<<op.kind<<" "<<op.address<<" "<<op.bytes<<" "<<op.success<<"\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
