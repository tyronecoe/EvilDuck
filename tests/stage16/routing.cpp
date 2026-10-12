// Reuse exact-body routing harness and historical vectors without rewriting them.
#define main historical_main
#include "../stage15/routing.cpp"
#undef main
#include "execution_guard.h"
#include <thread>
#include <atomic>
static void integrated(const std::string &n) {
 setup();uint8_t data[]={1,2};
 if(n=="integrated_feature_cannot_change_known_led") {
  call(1,2,data+1,1);const auto before=hid_backend::lockState();uint8_t zero=0;call(1,3,&zero,1);
  check(hid_backend::lockState().leds==before.leds,"FEATURE cannot falsify observed LEDs");
 } else if(n=="integrated_all_report_types_and_ids") {
  for(unsigned type=0;type<256;++type)for(unsigned id=0;id<256;++id){
   hid_backend::invalidateLockState();call(id,type,data,2);
   check(!hid_backend::lockState().known || ((type==0||type==2)&&id==0),"only normalized typed OUTPUT can supply one-byte evidence");
  }
 } else if(n=="integrated_null_lengths_types") {
  for(unsigned type=0;type<256;++type){call(0,type,nullptr,0);call(1,type,nullptr,1);call(1,type,nullptr,65535);}
  check(!hid_backend::lockState().known,"null reports never become feedback");
 } else if(n=="integrated_empty_output_never_enters_stock_hook") {
  struct StockDevice:USBHIDDevice{void _onOutput(uint8_t id,const uint8_t *p,uint16_t s)override{StockOutput(id,p,s);}} stock;
  tinyusb_hid_devices[0].device=&stock;
  call(1,2,nullptr,1);call(1,2,data+2,0);call(0,2,nullptr,0);call(0,2,data+2,0);
  check(posts==0,"stock hook not invoked by invalid empty/null OUTPUT");
  call(1,2,data+1,1);check(posts==1,"valid stock dispatch retained; queue blocking policy is unchanged");
 } else if(n=="integrated_payload_boundaries") {
  uint8_t backing[64]={};for(unsigned size: {0U,1U,2U,63U,64U,65535U}){
   hid_backend::invalidateLockState();call(1,2,backing,size);
   check(hid_backend::lockState().known==(size==1),"exact LED payload only; pointer allocation length remains caller contract");
  }
 } else if(n=="integrated_bounded_callback_reentry") {
  struct ReentrantDevice:USBHIDDevice {
   bool entered=false;
   void _onOutput(uint8_t id,const uint8_t *p,uint16_t s) override {
    if(!entered){entered=true;call(id,HID_REPORT_TYPE_FEATURE,p,s);}
    USBHIDDevice::_onOutput(id,p,s);
   }
  } nested;
  tinyusb_hid_devices[0].device=&nested;call(1,2,data+1,1);
  check(outputs==1&&features==1,"one bounded nested dispatch preserves report type");
  check(hid_backend::lockState().known&&hid_backend::lockState().leds==2,"nested FEATURE cannot disturb actual OUTPUT evidence");
 } else if(n=="integrated_executor_lock_independent") {
  {execution::Guard guard;std::thread writer([&]{call(0,2,data,2);});writer.join();}
  check(hid_backend::lockState().known,"routing callback does not acquire executor lock");
 } else if(n=="integrated_concurrent_snapshots") {
  std::thread writer([&]{for(unsigned i=0;i<10000;++i){uint8_t mask=i&7;call(1,2,&mask,1);}});
  for(unsigned i=0;i<10000;++i){auto state=hid_backend::lockState();check(!state.known||state.leds<8,"bounded atomic snapshot");}
  writer.join();check(hid_backend::lockState().known,"all routing returns");
 } else if(n=="integrated_input_backpressure_feedback") {
  mock::usbReady=false;call(0,2,data,2);check(hid_backend::lockState().known,"OUT independent of IN readiness");
  mock::usbReady=true;call(1,2,data+1,1);check(hid_backend::lockState().leds==2,"recovery feedback");
 } else if(n=="integrated_disconnect_reconnect_unknown") {
  call(0,2,data,2);auto token=hid_backend::lockSession();mock::usbMounted=false;com::update();
  check(!hid_backend::lockState().known,"disconnect invalidates evidence");mock::usbMounted=true;com::update();
  check(!hid_backend::lockState().known,"reconnect not invented acknowledgment");check(!hid_backend::receiveLockReport(1,data+1,1,token),"old explicit session rejected");
  call(0,2,data,2);check(hid_backend::lockState().known,"new normalized report accepted");
 } else if(n=="integrated_no_led_event_queue_post") {
  for(unsigned i=0;i<1000;++i){uint8_t mask=i&7;call(1,2,&mask,1);}
  check(posts==0&&hid_backend::lockState().known,"actual derived hook bypasses stock indefinite event queue");
 } else {test(n);}
}
int main(int argc,char **argv){if(argc!=2)return 2;try{integrated(argv[1]);std::cout<<"PASS "<<argv[1]<<" ("<<assertions<<" assertions)\n";return 0;}catch(const std::exception&e){std::cerr<<"FAIL "<<argv[1]<<": "<<e.what()<<'\n';return 1;}}
