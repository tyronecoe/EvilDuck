#include "caps_cases.inc"
#include "feedback_diag.h"
using hid_report_type_t=uint8_t;
constexpr uint8_t HID_REPORT_TYPE_OUTPUT=2,HID_REPORT_TYPE_FEATURE=3;
#define CFG_TUD_HID 1
using USBHIDDevice=USBHIDKeyboard;
struct tinyusb_hid_device_t{USBHIDDevice* device;uint8_t reports_num;uint8_t* report_ids;};
static tinyusb_hid_device_t tinyusb_hid_devices[10]{};
static uint8_t tinyusb_loaded_hid_devices_num=1,tinyusb_interface_protocol=0,protocolMode=1;
static uint8_t ids[]={1};
static uint8_t tud_hid_n_get_protocol(uint8_t){return protocolMode;}
extern "C" void* evilduck_hid_keyboard_identity();
using tud_hid_report_complete_cb_len_t=uint16_t;
static void* tinyusb_hid_device_input_sem=nullptr;
static void xSemaphoreGive(void*){}
#include "routing_slice.inc"
static bool tinyusb_device_mounted=false,tinyusb_device_suspended=false;
struct arduino_usb_event_data_t{struct{bool remote_wakeup_en;}suspend;};
constexpr const char* ARDUINO_USB_EVENTS="mock-usb";
constexpr int ARDUINO_USB_STARTED_EVENT=0,ARDUINO_USB_SUSPEND_EVENT=2,ARDUINO_USB_RESUME_EVENT=3;
#ifndef portMAX_DELAY
#define portMAX_DELAY 0xffffffffu
#endif
static unsigned eventPosts=0;
static int arduino_usb_event_post(const char*,int,void*,size_t,uint32_t){++eventPosts;return 0;}
#include "lifecycle_slice.inc"
static void input(bool caps){uint8_t report[9]={1,0,0,0,0,0,0,0,0};report[3]=caps?0x39:0;tud_hid_report_complete_cb(0,report,9);}
int main(int argc,char**argv){if(argc!=2)return 2;if(argv[1][0]!='D')return historical_caps_main(argc,argv);try{
 mscMock::reset();mock::reset();setup();check(startupControlledReady,"controlled setup");check(route_u::bindOwner(),"owner");lower::reset();led_mock::nowUs=100;
 tinyusb_hid_devices[0]={mockKeyboard,1,ids};auto r=req();std::string id=argv[1];uint8_t raw[]={1,2};
 auto call=[&](uint8_t report,uint8_t type,const uint8_t* data,uint16_t size,uint8_t instance=0){tud_hid_set_report_cb(instance,report,type,data,size);};
 if(id=="D01"){call(1,2,raw+1,1);auto d=feedback_diag::snapshot();auto s=led_return::snapshot(100);check(d.raw==1&&d.attempts==1&&d.keyboardDispatches==1&&d.receiver[0]==1&&s.callbacks==1&&s.reports==1&&s.mask==2,"actual core dispatch to actual derived receiver");}
 else if(id=="D02"){call(0,2,raw,2);check(feedback_diag::snapshot().keyboardDispatches==1&&led_return::snapshot(100).mask==2,"prefixed ID once");}
 else if(id=="D03"){call(0,0,raw,2);check(led_return::snapshot(100).reports==1,"legacy endpoint type0 supported");}
 else if(id=="D04"){call(0,2,raw+1,1);auto d=feedback_diag::snapshot();check(d.raw==1&&d.reasons[4]==1&&d.reasons[5]==1&&led_return::snapshot(100).callbacks==0,"one byte ID0 remains unresolved without guessed dispatch");}
 else if(id=="D05"){call(1,3,raw+1,1);auto d=feedback_diag::snapshot();check(d.raw==1&&d.features==1&&d.attempts==0&&led_return::snapshot(100).callbacks==0,"FEATURE never masquerades as LED OUTPUT");}
 else if(id=="D06"){call(1,2,nullptr,0);call(1,2,nullptr,1);call(1,1,raw,1);call(1,255,raw,1);call(1,2,raw,1,255);auto d=feedback_diag::snapshot();check(d.raw==5&&d.reasons[0]==1&&d.reasons[1]==1&&d.reasons[2]==1&&d.reasons[3]==2&&led_return::snapshot(100).callbacks==0,"raw counts before each rejected boundary");}
 else if(id=="D07"){call(99,2,raw+1,1);auto d=feedback_diag::snapshot();check(d.raw==1&&d.attempts==1&&d.reasons[4]==1&&d.keyboardDispatches==0,"unknown route separate");}
 else if(id=="D08"){call(1,2,raw,2);raw[1]=0xe0;call(1,2,raw+1,1);auto d=feedback_diag::snapshot();check(d.keyboardDispatches==2&&d.receiver[2]==1&&d.receiver[3]==1&&led_return::snapshot(100).reports==0,"routed receiver size and padding rejection");}
 else if(id=="D09"){mock::usbMounted=false;call(1,2,raw+1,1);check(feedback_diag::snapshot().receiver[4]==1&&!led_return::snapshot(100).observed,"not configured rejected independently");}
 else if(id=="D10"){call(1,2,raw+1,1);auto session=hid_backend::lockSession();tud_suspend_cb(false);check(!hid_backend::receiveLockReport(1,raw+1,1,session)&&!led_return::snapshot(100).observed,"suspend invalidates previous evidence");call(1,2,raw+1,1);check(feedback_diag::snapshot().receiver[6]>=1,"suspended rejection");tud_resume_cb();call(1,2,raw+1,1);check(led_return::snapshot(100).observed&&feedback_diag::snapshot().lifecycle[3]==1,"resume new evidence");}
 else if(id=="D11"){call(1,2,raw+1,1);auto session=hid_backend::lockSession();tud_umount_cb();check(!hid_backend::receiveLockReport(1,raw+1,1,session)&&feedback_diag::snapshot().receiver[5]==1,"stale session tracked");tud_mount_cb();call(1,2,raw+1,1);check(feedback_diag::snapshot().lifecycle[0]==1&&led_return::snapshot(100).observed,"mount new session");}
 else if(id=="D12"){handleLedTest(&r,0);check(r.code==200&&r.response.indexOf("\"usbConfiguredSample\":true")>=0&&r.response.indexOf("\"connected\":false")>=0&&r.response.indexOf("LED-FEEDBACK-BOUNDARY-")>=0,"unknown feedback does not mean unconfigured USB");auto a=feedback_diag::snapshot();handleLedTest(&r,0);auto b=feedback_diag::snapshot();check(a.raw==b.raw&&a.session==b.session&&a.receiver[0]==b.receiver[0]&&lower::count==0&&led_return::snapshot(100).state==led_return::State::Idle,"refresh no report/reset/start/injection side effect");}
 else if(id=="D13"){call(1,2,raw+1,1);led_mock::nowUs=led_return::StaleUs+101;handleLedTest(&r,0);check(r.response.indexOf("\"ledEvidenceValid\":false")>=0&&r.response.indexOf("\"caps\":null")>=0,"freshness exact5sec stale not false/off");}
 else if(id=="D14"){protocolMode=0;call(0,2,raw+1,1);check(!led_return::snapshot(100).observed&&feedback_diag::snapshot().protocol==0&&feedback_diag::snapshot().interfaceProtocol==0,"boot protocol does not invent absent boot descriptor support");call(1,2,raw+1,1);check(led_return::snapshot(100).observed,"unchanged registered route in protocol observation");}
 else if(id=="D15"){tinyusb_loaded_hid_devices_num=0;call(1,2,raw+1,1);check(!feedback_diag::snapshot().registeredKeyboard&&feedback_diag::snapshot().reasons[4]==1,"missing keyboard registration visible");}
 else if(id=="D16"){uint8_t zero=0;tinyusb_hid_devices[0].report_ids=&zero;call(0,2,raw+1,1);check(feedback_diag::snapshot().dispatches==1&&feedback_diag::snapshot().receiver[1]==1&&!led_return::snapshot(100).observed,"registered ID0 route preserved but not keyboard ID1");}
 else if(id=="D17"){for(unsigned i=0;i<10000;++i){uint8_t mask=i&7;call(1,2,&mask,1);}auto d=feedback_diag::snapshot();check(d.raw==10000&&d.keyboardDispatches==10000&&d.receiver[0]==10000&&led_return::snapshot(100).reports==10000,"bounded repeated feedback");}
 else if(id=="D18"){put("/x.txt","CAPSLOCK\nSTRING a\n");start();done();auto p=presses();check(lower::calls[p[0]].bytes[2]==0x39&&feedback_diag::snapshot().capsDownQueued==1&&feedback_diag::snapshot().capsUpQueued==1,"unchangedcaps usage and down/up submission metadata");input(true);led_mock::nowUs=300;input(false);check(feedback_diag::snapshot().capsDownCompleted==1&&feedback_diag::snapshot().capsUpCompleted==1,"actual completion slice caps-only metadata");}
 else if(id=="D19"){r.headers.clear();handleLedTest(&r,0);check(r.code==401,"diagnostics remain authenticated");}
 else if(id=="D20"){for(unsigned i=0;i<4;++i)evilduck_usb_feedback_lifecycle(uint8_t(i));auto d=feedback_diag::snapshot();check(d.session>=4&&d.rawUs==0&&!d.registeredKeyboard&&d.boot==0x1122334455667788ULL,"bootmarker stable lifecycle invalidates current metadata");}
 else if(id=="D21"){std::thread producer([&]{for(unsigned i=0;i<2000;++i){uint8_t mask=i&7;tud_hid_set_report_cb(0,1,2,&mask,1);}});for(unsigned i=0;i<200;++i){handleLedTest(&r,0);check(r.code==200&&r.response.indexOf("rawArrivals")>=0,"authenticated snapshot progress independent of OUT callbacks");}producer.join();check(feedback_diag::snapshot().raw==2000&&led_return::snapshot(100).reports==2000,"concurrent metadata and receiver counts exact");}
 else if(id=="D22"){input(true);tud_umount_cb();input(false);check(feedback_diag::snapshot().capsUpCompleted==0&&eventPosts==1,"old session completion pairing not reused after invalidation");uint8_t malformed[2]={1,0x39};tud_hid_report_complete_cb(0,nullptr,0);tud_hid_report_complete_cb(0,malformed,2);check(feedback_diag::snapshot().capsDownCompleted==1,"no arbitrary malformed input capture");}
 else check(false,"unknown case");std::cout<<"PASS "<<id<<" ("<<assertions<<" assertions)\n";return 0;
 }catch(const std::exception&e){std::cerr<<"FAIL "<<argv[1]<<": "<<e.what()<<" ("<<assertions<<")\n";return 1;}}
