#include "host.h"
#include "USBHIDKeyboard.h"
#include "USBHID.h"
#include "USB.h"
#include "hid_backend.h"
#include "keyboard_locale.h"
#include "duckscript.h"
#include "com.h"
#include <iostream>
#include <stdexcept>
#include <cstring>
#include <array>
static unsigned assertions=0, outputs=0, features=0, posts=0;
static uint8_t routedId=0, ledPosted=0;
static uint16_t routedSize=0;
static uint32_t waitPosted=0;
static const uint8_t *routedBuffer=nullptr;
static bool debugLogs=false;
static void check(bool ok,const char *why){++assertions;if(!ok)throw std::runtime_error(why);}
using hid_report_type_t=uint8_t;
constexpr uint8_t HID_REPORT_TYPE_INPUT=1,HID_REPORT_TYPE_OUTPUT=2,HID_REPORT_TYPE_FEATURE=3;
#define CFG_TUD_HID 1
struct USBHIDDevice {
  virtual void _onOutput(uint8_t id,const uint8_t *data,uint16_t size) {
    ++outputs;routedId=id;routedSize=size;routedBuffer=data;mockKeyboard->_onOutput(id,data,size);
  }
  virtual void _onSetFeature(uint8_t id,const uint8_t *data,uint16_t size) {
    ++features;routedId=id;routedSize=size;routedBuffer=data;mockKeyboard->_onSetFeature(id,data,size);
  }
};
struct tinyusb_hid_device_t{USBHIDDevice *device;uint8_t reports_num;uint8_t *report_ids;};
static tinyusb_hid_device_t tinyusb_hid_devices[10]={};
static uint8_t tinyusb_loaded_hid_devices_num=0;
static const char *tinyusb_hid_device_report_types[4]={"INVALID","INPUT","OUTPUT","FEATURE"};
static const char *volatile debugType=nullptr;
static void debugLog(const char *,unsigned,unsigned,const char *type,unsigned){debugType=type;}
#define log_d(...) do { if(debugLogs) debugLog(__VA_ARGS__); } while(0)
// Exact selected source bodies are generated from pinned core, never hand-copied.
#include "routing_slice.inc"
struct arduino_usb_hid_keyboard_event_data_t{uint8_t leds;};
constexpr uint32_t portMAX_DELAY=0xffffffffU;
constexpr const char *ARDUINO_USB_HID_KEYBOARD_EVENTS="keyboard";
constexpr int ARDUINO_USB_HID_KEYBOARD_LED_EVENT=1;
static int arduino_usb_event_post(const char *,int,void *data,size_t,uint32_t wait){++posts;ledPosted=static_cast<arduino_usb_hid_keyboard_event_data_t *>(data)->leds;waitPosted=wait;return 0;}
#include "stock_keyboard_slice.inc"
static USBHIDDevice device;
static uint8_t keyboardIds[]={1},zeroIds[]={0};
static void setup(){mock::reset();hid_backend::begin();com::update();mock::reports.clear();tinyusb_loaded_hid_devices_num=1;tinyusb_hid_devices[0]={&device,1,keyboardIds};}
static void call(uint8_t id,uint8_t type,const uint8_t *data,uint16_t size,uint8_t instance=0){tud_hid_set_report_cb(instance,id,type,data,size);}
static void test(const std::string &n){
 setup();uint8_t data[]={1,2};
 if(n=="known_hid_vectors_no_numeric_encoding") {
  struct Vector{const char *locale,*text;uint8_t count,m1,k1,m2,k2;};
  const Vector vectors[]={{"US","a",1,0,4,0,0},{"US","Z",1,2,29,0,0},{"US","0",1,0,39,0,0},{"US","#",1,2,32,0,0},{"DE","@",1,64,20,0,0},{"DE","^",2,0,53,0,44},{"DE","Z",1,2,28,0,0}};
  for(auto v:vectors){check(keyboard_locale::setLocaleByName(v.locale),"known locale");keyboard_locale::Stroke strokes[2]={};uint8_t count=0;
    check(keyboard_locale::translate(v.text,strlen(v.text),strokes,count)==strlen(v.text) && count==v.count,"known translation stroke count");
    check(strokes[0].modifiers==v.m1 && strokes[0].key==v.k1,"USB usage vector independent of packed encoding");
    if(count==2)check(strokes[1].modifiers==v.m2 && strokes[1].key==v.k2,"known dead-key continuation");}
 }
 else if(n=="normalized_interrupt_output") {call(0,2,data,2);check(outputs==1 && features==0,"interrupt routes OUTPUT");check(routedId==1 && routedSize==1 && routedBuffer==data+1,"ID byte stripped once");check(hid_backend::lockState().known && hid_backend::lockState().leds==2,"actual production feedback received");}
 else if(n=="legacy_type_zero_interrupt") {call(0,0,data,2);check(outputs==1 && hid_backend::lockState().leds==2,"pinned legacy type0 normalization");}
 else if(n=="nonzero_control_output") {call(1,2,data+1,1);
#ifdef PAIRED_PROPOSAL
 check(outputs==1 && features==0,"typed OUTPUT dispatch");
#else
 check(features==1 && outputs==0,"unpatched OUTPUT misroutes through FEATURE workaround");
#endif
 check(hid_backend::lockState().known && hid_backend::lockState().leds==2,"actual control LED data reaches receiver");}
 else if(n=="feature_led_type_separation") {call(1,3,data+1,1);check(features==1 && outputs==0,"FEATURE routed to feature hook");
#ifdef PAIRED_PROPOSAL
 check(!hid_backend::lockState().known,"paired backend does not treat FEATURE as LED output");
#else
 check(hid_backend::lockState().known,"unpatched workaround accepts indistinguishable FEATURE");
#endif
 }
 else if(n=="input_type_rejected") {call(1,1,data+1,1);
#ifdef PAIRED_PROPOSAL
 check(!outputs && !features && !hid_backend::lockState().known,"INPUT SET_REPORT rejected");
#else
 check(features==1 && hid_backend::lockState().known,"unpatched invalid INPUT accepted as feedback");
#endif
 }
 else if(n=="invalid_type_rejected") {call(1,255,data+1,1);
#ifdef PAIRED_PROPOSAL
 check(!outputs && !features && !hid_backend::lockState().known,"invalid type rejected before dispatch");
#else
 check(features==1 && hid_backend::lockState().known,"invalid type routed to feature hook");
#endif
 }
 else if(n=="invalid_instance") {call(1,2,data+1,1,255);
#ifdef PAIRED_PROPOSAL
 check(!outputs && !features && !hid_backend::lockState().known,"instance bounds guard");
#else
 check(features==1 && hid_backend::lockState().known,"pinned callback ignores instance");
#endif
 }
 else if(n=="null_zero_interrupt") {call(0,2,nullptr,0);check(!outputs && !features,"proposal null guard");}
 else if(n=="empty_onepast_interrupt") {call(0,2,data+sizeof(data),0);check(!outputs && !features,"proposal zero-length guard before read");}
 else if(n=="null_nonzero_interrupt") {call(0,2,nullptr,1);check(!outputs && !features,"null nonempty guard");}
 else if(n=="zero_transfer_backed_buffer") {uint8_t backing[64]={1,2};call(0,2,backing,0);check(!hid_backend::lockState().known,"no zero-transfer evidence");
#ifdef PAIRED_PROPOSAL
 check(!outputs,"proposal rejects before prefix read");
#else
 check(outputs==1 && routedSize==65535,"unpatched uint16 length underflows even with valid allocated backing buffer");
#endif
 }
 else if(n=="report_id_only_interrupt") {call(0,2,data,1);check(!hid_backend::lockState().known,"ID-only data never considered valid evidence");}
 else if(n=="zero_length_control_output") {call(1,2,data,0);check(!hid_backend::lockState().known,"zero control data rejected");}
 else if(n=="null_control_output") {call(1,2,nullptr,1);check(!hid_backend::lockState().known,"downstream null rejection vs proposed early guard");}
 else if(n=="unknown_report_id") {uint8_t raw[]={99,2};call(0,2,raw,2);check(!outputs && !features,"unknown ID no dispatch");}
 else if(n=="zero_id_device_no_prefix_stripping") {tinyusb_hid_devices[0].report_ids=zeroIds;call(0,2,data+1,1);check(outputs==1 && routedBuffer==data+1 && routedSize==1 && routedId==0,"report0 registry keeps payload intact");check(!hid_backend::lockState().known,"keyboard still expects report1");}
 else if(n=="all_led_masks_through_actual_route") {for(uint8_t mask=0;mask<32;++mask){uint8_t raw[]={1,mask};call(0,2,raw,2);check(hid_backend::lockState().known && hid_backend::lockState().leds==(mask&7),"descriptor LED masks observed");}check(outputs==32,"one dispatch each");}
 else if(n=="padding_and_length_rejection") {uint8_t raw[]={1,0xe0,0};call(0,2,raw,2);check(!hid_backend::lockState().known,"padding invalid");call(0,2,raw,3);check(!hid_backend::lockState().known,"extra payload invalid");}
 else if(n=="repeated_report_not_transition") {call(0,2,data,2);const auto first=hid_backend::lockState();call(0,2,data,2);check(hid_backend::lockState().changes[1]==first.changes[1],"repeat no phantom transition");}
 else if(n=="detached_feedback_rejection") {mock::usbMounted=false;call(0,2,data,2);check(!hid_backend::lockState().known,"no detached evidence");}
 else if(n=="stale_explicit_token_rejection") {auto session=hid_backend::lockSession();hid_backend::invalidateLockState();check(!hid_backend::receiveLockReport(1,data+1,1,session),"stale captured token rejected");call(0,2,data,2);check(hid_backend::lockState().known,"new delivery has no intrinsic wire epoch");}
 else if(n=="routing_during_owned_injection") {mock::file("route.txt","HOLD CTRL\nDELAY 100\n");check(duckscript::run("route.txt"),"start mocked ownership");for(unsigned i=0;i<1000 && !hid_backend::hasPersistent();++i)mock::tick();check(hid_backend::hasPersistent(),"held Ctrl");call(0,2,data,2);check(hid_backend::hasPersistent() && hid_backend::lockState().known,"OUT evidence independent of IN ownership");duckscript::stop();mock::tick();check(mock::heldModifiers==0,"cancel releases");}
 else if(n=="debug_invalid_type_unknown_id") {debugLogs=true;call(99,255,data+1,1);check(!outputs && !features,"proposal rejects before debug type indexing");}
 else if(n=="stock_output_null") {StockOutput(1,nullptr,1);check(false,"stock callback unexpectedly safe");}
 else if(n=="stock_output_empty_onepast") {StockOutput(1,data+sizeof(data),0);check(false,"stock callback unexpectedly safe");}
 else if(n=="stock_output_queue_wait_policy") {StockOutput(1,data+1,1);check(posts==1 && ledPosted==2 && waitPosted==portMAX_DELAY,"stock callback posts with indefinite queue deadline; runtime blocking not simulated");}
 else throw std::runtime_error("unknown routing test");
}
int main(int argc,char **argv){if(argc!=2)return 2;try{test(argv[1]);std::cout<<"PASS "<<argv[1]<<" ("<<assertions<<" assertions)\n";return 0;}catch(const std::exception&e){std::cerr<<"FAIL "<<argv[1]<<": "<<e.what()<<'\n';return 1;}}
