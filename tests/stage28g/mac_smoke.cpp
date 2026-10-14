// Fixed-buffer HOST-ONLY mock vectors. No device/OS input, real clocks or filesystem.
#include "../../language_preview/bridge.h"
#include <cstdio>
#include <cstring>
struct Capture{
 ds_keyboard::Report reports[16]{};unsigned count=0;bool overflow=false;
 static ds_preview::Accept sink(void* ptr,const ds_keyboard::Report& report){auto& c=*static_cast<Capture*>(ptr);if(c.count==16){c.overflow=true;return ds_preview::Accept::Failed;}c.reports[c.count++]=report;return ds_preview::Accept::Accepted;}
};
int main(){
 ds_preview::Program p;ds_bridge::Bridge bridge;Capture c;
 const char* src="HOLD a\nDELAY 1\nSTRING b\nRELEASE a\nRELEASE a";
 if(!p.compile(src,std::strlen(src))||!bridge.begin(Capture::sink,&c))return 1;
 bridge.step(0);if(!bridge.hold(0,0xe1))return 2;bridge.step(0);if(!bridge.start(p))return 3;
 for(unsigned now=0;now<1000&&bridge.state()==ds_bridge::State::Running;++now)bridge.step(now);
 if(bridge.state()!=ds_bridge::State::Completed||!bridge.planner().releaseRequired()||bridge.keyboardAcks()!=4||bridge.delayAcks()!=1)return 4;
 if(!bridge.drain(1000))return 5;bridge.step(1000);
 const unsigned char expected[8][8]={{0,0,0,0,0,0,0,0},{2,0,0,0,0,0,0,0},{2,0,4,0,0,0,0,0},{2,0,4,5,0,0,0,0},{2,0,4,0,0,0,0,0},{2,0,0,0,0,0,0,0},{2,0,0,0,0,0,0,0},{0,0,0,0,0,0,0,0}};
 if(c.overflow||c.count!=8||bridge.state()!=ds_bridge::State::Completed||!bridge.planner().neutralConfirmed())return 6;
 for(unsigned i=0;i<8;++i)if(std::memcmp(c.reports[i].bytes,expected[i],8))return 7;
 std::puts("PASS host-only ownership smoke: 8 exact mock reports, 4 keyboard acknowledgements, 1 delay");return 0;
}
