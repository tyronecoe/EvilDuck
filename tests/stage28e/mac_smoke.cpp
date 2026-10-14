// Host-only memory smoke test. No USB, HID, filesystem, OS input or clocks.
#include "../../language_preview/bridge.h"
#include <cstdio>
#include <cstring>
struct Capture {
 ds_keyboard::Report reports[16]{};unsigned count=0;bool overflow=false;
 static ds_preview::Accept sink(void* ptr,const ds_keyboard::Report& report){
  Capture& c=*static_cast<Capture*>(ptr);if(c.count==16){c.overflow=true;return ds_preview::Accept::Failed;}c.reports[c.count++]=report;return ds_preview::Accept::Accepted;
 }
};
int main(){
 const char* source="STRING aa\nDELAY 1\nSTRINGLN A";
 ds_preview::Program program;ds_bridge::Bridge bridge;Capture capture;
 if(!program.compile(source,std::strlen(source))||!bridge.begin(Capture::sink,&capture))return 1;
 bridge.step(0);if(!bridge.start(program))return 2;
 for(unsigned now=0;now<1000&&bridge.state()==ds_bridge::State::Running;++now)bridge.step(now);
 const unsigned char expected[9][8]={{0,0,0,0,0,0,0,0},{0,0,4,0,0,0,0,0},{0,0,0,0,0,0,0,0},{0,0,4,0,0,0,0,0},{0,0,0,0,0,0,0,0},{2,0,4,0,0,0,0,0},{0,0,0,0,0,0,0,0},{0,0,0x28,0,0,0,0,0},{0,0,0,0,0,0,0,0}};
 if(bridge.state()!=ds_bridge::State::Completed||capture.overflow||capture.count!=9||bridge.keyboardAcks()!=4||bridge.delayAcks()!=1)return 3;
 for(unsigned i=0;i<9;++i)if(std::memcmp(capture.reports[i].bytes,expected[i],8))return 4;
 std::puts("PASS host-only bridge smoke: 9 exact mock reports, 4 keyboard acknowledgements, 1 delay");return 0;
}
