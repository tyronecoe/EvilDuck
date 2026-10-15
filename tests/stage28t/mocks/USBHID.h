#pragma once
#include <cstddef>
#include <cstdint>
struct hid_keyboard_report_t {uint8_t modifier,reserved,keycode[6];};
constexpr uint8_t HID_REPORT_ID_KEYBOARD=1;
namespace mock {bool report(const hid_keyboard_report_t&,uint8_t,uint8_t,size_t);}
namespace lower {bool ready();bool submit(uint8_t,uint8_t,const void*,size_t);}
struct USBHID {void begin(){}bool ready(){return lower::ready();}};
inline bool tud_hid_n_report(uint8_t instance,uint8_t id,const void* data,size_t size){return lower::submit(instance,id,data,size);}
