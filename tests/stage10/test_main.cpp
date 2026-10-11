#include "host.h"
#include "FS.h"
#include "SD.h"
#include "USBMSC.h"
#include "usb_msc.h"
#include "attackmode.h"
#include "sd_card.h"
#include "duckscript.h"
#include "com.h"
#include "cli.h"
#include "execution_guard.h"
#include <iostream>
#include <stdexcept>
#include <thread>
#include <atomic>
#include <cstdlib>
#include <new>

static bool trackAlloc=false;
static unsigned allocations=0,assertions=0;
[[gnu::noinline]] void *operator new(std::size_t n){if(trackAlloc)++allocations;if(void *p=std::malloc(n?n:1))return p;throw std::bad_alloc();}
[[gnu::noinline]] void *operator new[](std::size_t n){return ::operator new(n);}
[[gnu::noinline]] void operator delete(void *p)noexcept{std::free(p);}
[[gnu::noinline]] void operator delete[](void *p)noexcept{std::free(p);}
[[gnu::noinline]] void operator delete(void *p,std::size_t)noexcept{std::free(p);}
[[gnu::noinline]] void operator delete[](void *p,std::size_t)noexcept{std::free(p);}
static void check(bool ok,const char *message){++assertions;if(!ok)throw std::runtime_error(message);}
constexpr size_t bytes=4194304;
static void reset(bool image=true){
 mock::reset();usb_msc::end();mscMock::reset();mscMock::beginOk=true;mscMock::starts=mscMock::ends=0;
 if(image){mscMock::put("/sys/usb_disk.img",bytes);auto &b=mscMock::nodes["/sys/usb_disk.img"]->bytes;
  for(size_t i=0;i<b.size();++i)b[i]=uint8_t((i*17+3)%251);}
}
static void finish(){for(unsigned i=0;i<4&&usb_msc::preparing();++i)attackmode::update();}
static void active(){check(attackmode::applyFromString("HID STORAGE"),"startup accepted");finish();check(usb_msc::active(),"validated raw media active");check(mscMock::media&&mscMock::writable,"SDK present/writable");}
static int32_t read(uint32_t l,uint32_t o,void *b,uint32_t n){auto f=mscMock::readCallback;return f?f(l,o,b,n):-1;}
static int32_t write(uint32_t l,uint32_t o,uint8_t *b,uint32_t n){auto f=mscMock::writeCallback;return f?f(l,o,b,n):-1;}
static void failed(const char *why){check(!usb_msc::active()&&!usb_msc::preparing(),"not falsely ready/preparing");check(usb_msc::state()==usb_msc::State::Failed,"failed state");check(!mscMock::media&&!mscMock::writable,"media removed after failure");check(String(usb_msc::lastError()).indexOf(why)>=0,"useful reason");}
static void script(const char *s){mock::file("stage10.txt",s);check(duckscript::run("stage10.txt"),"mocked script starts");}
static void waitPreparing(){for(unsigned i=0;i<2000&&!usb_msc::preparing();++i)mock::tick();check(usb_msc::preparing(),"reached pending startup");}
static void released(){check(!duckscript::running()&&!com::busy(),"runtime idle");check(mock::heldKeys.empty()&&!mock::heldModifiers,"runtime keys released");check(!mock::blockingDelays,"no blocking firmware delay");}
static void test(const std::string &n){
 reset();uint8_t buffer[4096]={};uint8_t data[4096];for(unsigned i=0;i<4096;++i)data[i]=uint8_t(i+19);
 if(n=="startup_success_truthful"){
  check(attackmode::applyFromString("HID STORAGE"),"request accepted");check(attackmode::storageRequested(),"wanted true");check(!attackmode::storageEnabled()&&attackmode::storagePreparing(),"pending != active");
  finish();check(attackmode::storageEnabled(),"active after validation");check(mscMock::blocks==8192&&mscMock::blockSize==512,"correct geometry");check(!mscMock::writes&&!mscMock::creates&&!mscMock::truncates,"no preparation writes or formatting");
 }else if(n=="startup_missing_card"){
  mscMock::present=false;check(!attackmode::applyFromString("STORAGE"),"reject unavailable card");failed("SD unavailable");check(attackmode::storageRequested()&&!attackmode::storageEnabled(),"request retained but active false");
 }else if(n=="startup_missing_image_no_create"){
  reset(false);check(usb_msc::begin(),"pending validation accepted");finish();failed("no image created");check(!mscMock::creates&&!mscMock::writes,"no implicit image creation");
 }else if(n=="startup_wrong_size_no_truncate"){
  for(size_t size:{size_t(0),bytes-1,bytes+1}){reset();auto node=mscMock::nodes["/sys/usb_disk.img"];node->bytes.resize(size);check(usb_msc::begin(),"request queued");finish();failed("exactly");check(node->bytes.size()==size&&!mscMock::truncates&&!mscMock::writes,"existing wrong-sized file unchanged");}
  reset();mscMock::nodes["/sys/usb_disk.img"]->directory=true;usb_msc::begin();finish();failed("exactly");
 }else if(n=="startup_open_failure"){mscMock::openFail=true;usb_msc::begin();finish();failed("existing writable");}
 else if(n=="startup_probe_seek_failure"){mscMock::seekFail=true;usb_msc::begin();finish();failed("preparation seek");check(!mscMock::reads,"no read after seek failure");}
 else if(n=="startup_probe_short_read"){mscMock::shortRead=511;usb_msc::begin();finish();failed("preparation read");}
 else if(n=="startup_sdk_failure_cleanup"){
  mscMock::beginOk=false;usb_msc::begin();finish();failed("USBMSC.begin");attackmode::update();check(read(0,0,buffer,1)==-1&&!mscMock::media,"stable callbacks reject partial startup access");check(mscMock::closes==1,"handle closed once");
 }else if(n=="retry_failed_startup"){
  mscMock::present=false;check(!attackmode::applyFromString("STORAGE"),"first failure propagated");mscMock::present=true;check(attackmode::applyFromString("STORAGE"),"same requested mode retry");finish();check(attackmode::storageEnabled()&&!attackmode::storageError()[0],"retry succeeds and clears old error");
 }else if(n=="repeated_begin_idempotent"){
  check(usb_msc::begin()&&usb_msc::begin(),"pending requests idempotent");finish();auto opens=mscMock::opens;check(usb_msc::begin()&&usb_msc::active(),"active begin stays active");check(mscMock::starts==1&&mscMock::opens==opens,"no duplicate start or reopen");
 }else if(n=="retry_ejected_media"){
  active();check(mscMock::startCallback(0,false,true),"eject accepted");check(!attackmode::storageEnabled()&&attackmode::storageRequested(),"ejected != requested state");check(attackmode::applyFromString("HID STORAGE"),"same requested mode retries eject");finish();check(usb_msc::active(),"reload validated");
 }else if(n=="stale_host_load_after_off"||n=="stale_host_load_after_cancel"){
  active();auto cb=mscMock::startCallback;
  if(n=="stale_host_load_after_off")attackmode::setOff();
  else {cb(0,false,true);attackmode::applyFromString("HID STORAGE");attackmode::cancelPendingStorage();}
  check(!cb(0,true,true),"stale host load cannot undo explicit cancellation");finish();
  check(!usb_msc::active()&&!usb_msc::preparing()&&!attackmode::storageRequested(),"disabled media stays disabled");
 }else if(n=="writable_reset_after_end"){active();usb_msc::end();check(!mscMock::writable,"SDK end resets write protection");active();check(mscMock::writable,"new activation explicitly restores writable");}
 else if(n=="read_nonzero_offset"){
  active();check(read(2,37,buffer,83)==83,"nonzero read transfer accepted");check(mscMock::lastSeek==1061,"correct byte address");check(!memcmp(buffer,mscMock::nodes["/sys/usb_disk.img"]->bytes.data()+1061,83),"exact offset bytes");
 }else if(n=="write_nonzero_offset"){
  active();auto &b=mscMock::nodes["/sys/usb_disk.img"]->bytes;uint8_t before=b[1542],after=b[1607];check(write(3,7,data,64)==64,"write accepted");check(mscMock::lastSeek==1543,"correct write address");check(!memcmp(b.data()+1543,data,64)&&b[1542]==before&&b[1607]==after,"only intended range changed");check(mscMock::flushes==1,"flush requested");
 }else if(n=="cross_sector_unaligned"){
  active();check(write(1,511,data,1025)==1025,"unaligned cross-sector accepted");check(read(1,511,buffer,1025)==1025&&!memcmp(buffer,data,1025),"cross-sector data exact");check(read(0,1023,buffer,1)==1&&buffer[0]==data[0],"formula allows normalized multi-sector offsets");
 }else if(n=="last_byte_and_exact_end"){
  active();check(write(8191,511,data,1)==1,"last byte write");check(read(8191,511,buffer,1)==1&&buffer[0]==data[0],"last byte read");auto seeks=mscMock::seeks;check(read(8192,0,nullptr,0)==0,"end-position zero-length no-op");check(seeks==mscMock::seeks,"zero-length no seek");
 }else if(n=="invalid_range_and_overflow"){
  active();auto b=mscMock::nodes["/sys/usb_disk.img"]->bytes;auto seeks=mscMock::seeks;
  for(auto l:{8192u,UINT32_MAX,8388608u}){check(write(l,0,data,1)==-1,"invalid LBA rejected");check(read(l,UINT32_MAX,buffer,1)==-1,"overflow offset rejected");}
  check(write(8191,511,data,2)==-1&&read(8191,510,buffer,3)==-1,"overrun rejected");check(mscMock::seeks==seeks&&mscMock::nodes["/sys/usb_disk.img"]->bytes==b,"bad range no seek or file change");check(usb_msc::active(),"bad request does not poison healthy media");
 }else if(n=="zero_length_null"){
  active();auto seeks=mscMock::seeks;check(read(0,0,nullptr,0)==0&&write(3,4,nullptr,0)==0,"null zero requests safe");check(mscMock::seeks==seeks&&!mscMock::writes,"no zero-length I/O");
 }else if(n=="null_nonzero"){active();auto seeks=mscMock::seeks;check(read(0,0,nullptr,1)==-1&&write(0,0,nullptr,1)==-1,"nonzero null rejected");check(mscMock::seeks==seeks,"no null seek");}
 else if(n=="transfer_limit"){active();check(read(0,0,buffer,4096)==4096,"configured buffer limit accepted");auto seeks=mscMock::seeks;check(read(0,0,buffer,4097)==-1&&write(0,0,data,UINT32_MAX)==-1,"oversize rejected before access");check(mscMock::seeks==seeks,"no oversize I/O");}
 else if(n=="read_seek_failure_no_wrong_read"){active();auto reads=mscMock::reads;mscMock::seekFail=true;check(read(2,9,buffer,8)==-1,"failed seek read rejected");failed("read seek");check(mscMock::reads==reads,"no fallback read at stale cursor");}
 else if(n=="write_seek_failure_no_wrong_write"){active();auto b=mscMock::nodes["/sys/usb_disk.img"]->bytes;mscMock::seekFail=true;check(write(0,12,data,15)==-1,"seek failed write rejected");failed("write seek");check(!mscMock::writes&&mscMock::nodes["/sys/usb_disk.img"]->bytes==b,"no fallback write elsewhere");}
 else if(n=="short_read_quarantines"){active();mscMock::shortRead=3;check(read(1,2,buffer,8)==-1,"short read fails request");failed("short read");auto reads=mscMock::reads;check(read(0,0,buffer,8)==-1&&mscMock::reads==reads,"quarantined media no further reads");}
 else if(n=="short_write_prefix_and_quarantine"){
  active();auto &b=mscMock::nodes["/sys/usb_disk.img"]->bytes;uint8_t before=b[699],after=b[703];mscMock::shortWrite=3;check(write(1,188,data,8)==-1,"short write fails request");failed("partial prefix");check(!memcmp(b.data()+700,data,3)&&b[699]==before&&b[703]==after,"only actual prefix within approved range changed");auto writes=mscMock::writes;check(write(0,0,data,8)==-1&&writes==mscMock::writes,"no retry at stale cursor");
 }else if(n=="card_removal_callback"){active();mscMock::present=false;auto seeks=mscMock::seeks;check(write(0,0,data,1)==-1,"removed SD fails");failed("SD unavailable");check(seeks==mscMock::seeks,"no seek to removed media");}
 else if(n=="card_removal_main_loop"){active();mscMock::present=false;attackmode::update();failed("SD unavailable");}
 else if(n=="backing_size_changed"){active();mscMock::nodes["/sys/usb_disk.img"]->bytes.resize(bytes-1);check(read(0,0,buffer,1)==-1,"changed size rejected");failed("size changed");}
 else if(n=="fault_cleanup_and_explicit_recovery"){
  active();mscMock::seekFail=true;read(0,0,buffer,1);attackmode::update();check(read(0,0,buffer,1)==-1&&!mscMock::media,"callbacks reject faulted media");mscMock::seekFail=false;check(attackmode::applyFromString("HID STORAGE"),"explicit retry accepted");finish();check(read(0,0,buffer,1)==1,"recovery usable");
 }else if(n=="eject_load_and_power_stop"){
  active();auto cb=mscMock::startCallback;check(cb(0,false,true),"eject callback");check(usb_msc::state()==usb_msc::State::Ejected&&!mscMock::media,"no media after eject");check(cb(0,true,true),"load queues validation");check(!usb_msc::active(),"load doesn't prematurely advertise");finish();check(usb_msc::active(),"load active");check(mscMock::startCallback(0,false,false)&&!usb_msc::active(),"power stop closes media too");
 }else if(n=="cancel_before_open"||n=="cancel_after_open"){
  attackmode::applyFromString("HID STORAGE");if(n=="cancel_after_open")attackmode::update();attackmode::cancelPendingStorage();finish();check(!usb_msc::active()&&!usb_msc::preparing()&&!attackmode::storageRequested(),"cancelled pending request");check(!mscMock::media&&!mscMock::writes,"no advertised or changed media");check(mscMock::closes==(n=="cancel_after_open"?1u:0u),"opened handle closed on interruption");
 }else if(n=="timeout_wrap_safe"){
  mock::now=UINT32_MAX-100;usb_msc::begin();mock::now+=4999;attackmode::update();check(usb_msc::preparing(),"before deadline even over clock wrap");++mock::now;attackmode::update();failed("timed out");check(!mscMock::writes&&mscMock::closes==1,"timeout closes handle no writes");
 }else if(n=="media_absent_until_validated"){
  usb_msc::begin();for(unsigned i=0;i<2;++i){attackmode::update();check(usb_msc::preparing()&&!mscMock::media,"open/probe not ready");}attackmode::update();check(usb_msc::active()&&mscMock::media,"only activation advertises");check(mscMock::reads==1&&!mscMock::writes,"one bounded512-byte probe only");
 }else if(n=="script_waits_for_storage"){
  script("ATTACKMODE HID STORAGE\nSTRINGLN ready\n");waitPreparing();check(mock::text.length()==0&&com::busy(),"tail waits for validated activation");mock::drain();check(mock::text=="ready\n"&&usb_msc::active(),"tail runs after ready");released();
 }else if(n=="script_startup_failure_stops_tail"){
  mscMock::openFail=true;script("ATTACKMODE HID STORAGE\nSTRINGLN MUST-NOT-APPEAR\n");mock::drain();check(mock::text.length()==0&&duckscript::lastError().indexOf("line 1")>=0&&duckscript::lastError().indexOf("existing writable")>=0,"source-located startup failure stops tail");check(!attackmode::storageEnabled(),"not false success");released();
 }else if(n=="stop_pending_startup"){
  script("ATTACKMODE HID STORAGE\nSTRINGLN hidden\n");waitPreparing();duckscript::stop();for(unsigned i=0;i<10;++i)mock::tick();check(!usb_msc::active()&&!mscMock::media&&!mock::text.length(),"STOP prevents activation and tail");released();
 }else if(n=="stop_preserves_active_media"){
  active();script("DELAY 60000\nSTRING hidden\n");for(unsigned i=0;i<20;++i)mock::tick();duckscript::stop();check(usb_msc::active(),"STOP leaves preexisting active media intact");released();
 }else if(n=="live_cli_ownership_while_preparing"){
  script("ATTACKMODE HID STORAGE\nSTRINGLN good\n");waitPreparing();check(!com::executeNow("ATTACKMODE OFF"),"web/com live admission rejects busy");cli::parse("send ATTACKMODE OFF",mock::print);check(usb_msc::preparing()&&attackmode::storageRequested(),"CLI cannot mutate owned pending mode");mock::drain();check(mock::text=="good\n","script survives live conflict");cli::parse("status",mock::print);check(mock::output.indexOf("storage_usb=1")>=0&&mock::output.indexOf("storage_state=active")>=0,"truthful CLI status");released();
 }else if(n=="script_and_host_activity"){
  active();script("VAR $n=0\nWHILE $n<3\nSTRING x\n$n=$n+1\nEND_WHILE\nSTRINGLN done\n");unsigned ops=0;while(duckscript::running()||com::busy()){mock::tick();check(read(1,7,buffer,8)==8,"host storage read alongside script");++ops;check(ops<1000,"bounded script execution");}check(mock::text=="xxxdone\n","control/keyboard behavior unchanged");released();
 }else if(n=="function_condition_storage_startup"){
  script("FUNCTION mount()\nIF TRUE THEN\nATTACKMODE HID STORAGE\nEND_IF\nRETURN TRUE\nEND_FUNCTION\nIF mount() THEN\nVAR $n=0\nWHILE $n<2\nSTRING x\n$n=$n+1\nEND_WHILE\nEND_IF\nSTRINGLN done\n");
  waitPreparing();check(com::busy()&&!mock::text.length(),"call continuation waits for storage");mock::drain();
  check(mock::text=="xxdone\n"&&usb_msc::active(),"function return/condition/loop continue correctly");released();
 }else if(n=="live_cli_failure_status_and_retry"){
  mscMock::openFail=true;cli::parse("send ATTACKMODE HID STORAGE",mock::print);check(com::busy(),"CLI live storage startup queued");mock::drain();
  check(com::lastError().indexOf("existing writable")>=0&&!usb_msc::active(),"async live failure reported");
  cli::parse("status",mock::print);check(mock::output.indexOf("storage_usb=0")>=0&&mock::output.indexOf("storage_state=failed")>=0&&mock::output.indexOf("storage_error=MSC:")>=0,"CLI reports failed requested mode truthfully");
  mscMock::openFail=false;cli::parse("send ATTACKMODE HID STORAGE",mock::print);mock::drain();check(usb_msc::active(),"same CLI mode retries successfully");released();
 }else if(n=="callback_lock_contention_busy"){
  active();std::atomic<bool> locked{false},release{false};std::thread web([&]{execution::Guard g;locked=true;while(!release)std::this_thread::yield();});while(!locked)std::this_thread::yield();auto seeks=mscMock::seeks;auto r=read(0,0,buffer,8),w=write(0,0,data,8);release=true;web.join();check(r==0&&w==0,"USB busy instead of blocking behind web/CLI lock");check(seeks==mscMock::seeks,"busy no cursor mutation");check(read(0,0,buffer,8)==8,"retry after contention works");
 }else if(n=="callback_error_storm_no_io"){
  active();auto seeks=mscMock::seeks;for(unsigned i=0;i<1000;++i)check(write(UINT32_MAX,i,data,1)==-1,"invalid repeated requests rejected");check(mscMock::seeks==seeks&&usb_msc::active(),"no I/O or healthy-media corruption after storm");
 }else if(n=="concurrent_callback_mode_stop"){
  active();auto cb=mscMock::readCallback;std::atomic<bool> go{false};std::thread usb([&]{while(!go)std::this_thread::yield();uint8_t b;for(unsigned i=0;i<1000;++i)cb(0,0,&b,1);});go=true;attackmode::setOff();usb.join();check(!usb_msc::active()&&!mscMock::media,"mode stop wins safely over concurrent callbacks");check(!mscMock::writes,"no writes from reads/stop");
 }else if(n=="sd_adapter_interleaving"){
  active();check(sd_card::begin(),"real adapter mounts mocked SD");check(sd_card::writeFile("scripts/test.txt","safe")&&sd_card::appendFile("scripts/test.txt"," output"),"real adapter writes different file");check(sd_card::readFile("scripts/test.txt")=="safe output","adapter content preserved");check(read(0,0,buffer,1)==1&&mscMock::nodes["/sys/usb_disk.img"]->bytes.size()==bytes,"MSC file remains intact");
 }else if(n=="sd_adapter_removal_and_remount"){
  check(sd_card::begin()&&sd_card::ready(),"adapter mounted");mscMock::present=false;check(!sd_card::ready()&&!sd_card::writeFile("scripts/test.txt","hidden"),"removed adapter unavailable");mscMock::present=true;check(sd_card::begin()&&sd_card::ready(),"explicit remount");
 }else if(n=="off_cancels_pending"){attackmode::applyFromString("HID STORAGE");attackmode::setOff();finish();check(!usb_msc::preparing()&&!usb_msc::active()&&!attackmode::storageRequested()&&!attackmode::hidEnabled(),"OFF cancels pending no USB detach claim");}
 else if(n=="repeated_failure_recovery"){
  for(unsigned i=0;i<20;++i){mscMock::openFail=true;attackmode::applyFromString("STORAGE");finish();check(!usb_msc::active(),"repeated failed open not success");mscMock::openFail=false;active();usb_msc::end();}check(mscMock::closes==20,"exact open/close lifecycle after recovery");
 }else if(n=="no_callback_heap_allocation"){
  active();allocations=0;trackAlloc=true;bool ok=true;for(unsigned i=0;i<1000;++i){ok&=read(0,13,buffer,64)==64;ok&=write(0,13,data,64)==64;}trackAlloc=false;check(ok,"all hot-path operations accepted");check(!allocations,"production callback/mock hot path no allocations");std::cout<<"Callback allocation probe: 2000 transfers,0 allocations; underlying ESP SD/USB allocations unmeasured\n";
 }else throw std::runtime_error("unknown test name");
}
int main(int argc,char **argv){try{if(argc!=2)throw std::runtime_error("one test name required");test(argv[1]);std::cout<<"PASS "<<argv[1]<<" ("<<assertions<<" assertions)\n";return 0;}catch(const std::exception &e){trackAlloc=false;std::cerr<<"FAIL "<<(argc>1?argv[1]:"args")<<": "<<e.what()<<'\n';return 1;}}
