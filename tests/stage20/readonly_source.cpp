// Reuse the existing synthetic flash fixture, not its main or owner data.
#define main stage19_original_driver_main
#include "../stage19/sdk_recovery.cpp"
#undef main
#include "partition_api.h"
class ReadOnlyFlash:public Flash {
public:
 esp_partition_t partition{0x5000,0x9000,true,false,nullptr};
 bool get_readonly()override{return true;}
 esp_err_t write(size_t o,const void*s,size_t n)override{++writes;auto e=esp_partition_write(&partition,o,s,n);ops.push_back({"write",0x9000+o,n,e==ESP_OK});return e;}
 esp_err_t write_raw(size_t o,const void*s,size_t n)override{++writes;auto e=esp_partition_write_raw(&partition,o,s,n);ops.push_back({"write",0x9000+o,n,e==ESP_OK});return e;}
 esp_err_t erase_range(size_t o,size_t n)override{++erases;auto e=esp_partition_erase_range(&partition,o,n);ops.push_back({"erase",0x9000+o,n,e==ESP_OK});return e;}
};
int main(int argc,char**argv){try{check(argc==2,"case required");std::string n=argv[1];ReadOnlyFlash f;f.header(0,0xfffffffe,1);
 if(n=="readonly_incomplete_entry")f.data[64]=0;
 if(n=="readonly_bad_entry_crc")f.item(0,0,false);
 if(n=="readonly_freeing")f.header(0,0xfffffff8,1);
 if(n=="readonly_corrupt_activation"){for(unsigned p=0;p<5;++p){f.header(p,0xfffffffe,p+1);f.data[p*4096+28]^=1;}}
 if(n=="readonly_corrupt_string"||n=="corrupt_read_becomes_not_found"){
  Flash seed;nvs::Page creator;check(creator.load(&seed,0)==ESP_OK,"seed page");uint8_t input[4]={1,2,3,0};check(creator.writeItem(1,nvs::ItemType::SZ,"synthetic",input,4)==ESP_OK,"seed string");seed.data[96]^=1;
  if(n=="corrupt_read_becomes_not_found"){
   seed.ops.clear();seed.writes=0;auto before=seed.data;nvs::Storage storage(&seed);check(storage.init(0,5)==ESP_OK,"CRC not checked at init");uint8_t out[4];check(storage.readItem(1,nvs::ItemType::SZ,"synthetic",out,4)==ESP_ERR_NVS_NOT_FOUND,"corruption reported as missing after cleanup");check(seed.data!=before&&seed.writes>0,"read erases bitmap before NOT_FOUND");for(auto op:seed.ops)std::cout<<"OP "<<op.kind<<" "<<op.address<<" "<<op.bytes<<" "<<op.success<<"\n";
  }else{
   f.data=seed.data;auto before=f.data;nvs::Storage storage(&f);check(storage.init(0,5)==ESP_OK,"readonly init still does not check payload CRC");uint8_t out[4];check(storage.readItem(1,nvs::ItemType::SZ,"synthetic",out,4)==ESP_ERR_NOT_ALLOWED,"read cleanup denied");check(f.data==before&&lower_flash_calls==0,"readonly source blocks attempted mutation");for(auto op:f.ops)std::cout<<"OP "<<op.kind<<" "<<op.address<<" "<<op.bytes<<" "<<op.success<<"\n";
  }
  std::cout<<"PASS "<<n<<" ("<<assertions<<" assertions)\n";return 0;
 }
 auto before=f.data;nvs::PageManager manager;auto error=manager.load(&f,0,5);
 check(lower_flash_calls==0,"readonly target source never invokes lower flash writes/erase");
 check(f.data==before,"backend refusing mutations preserves synthetic bytes");
 if(n=="readonly_clean"||n=="readonly_freeing"){check(error==ESP_OK&&f.ops.empty(),"readonly source skips some manager recovery");}
 else{check(error==ESP_ERR_NOT_ALLOWED&&!f.ops.empty(),"read-only changes success behavior; attempted mutation rejected");}
 for(auto op:f.ops){check(op.address>=0x9000&&op.address+op.bytes<=0xe000,"attempt ranges bounded");std::cout<<"OP "<<op.kind<<" "<<op.address<<" "<<op.bytes<<" "<<op.success<<"\n";}
 std::cout<<"PASS "<<n<<" ("<<assertions<<" assertions)\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
