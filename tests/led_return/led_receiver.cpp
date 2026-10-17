#include "led_receiver.h"
#include <string.h>
#ifdef EVILDUCK_HOST_TEST
#include <mutex>
namespace {std::mutex mux;struct Lock{std::lock_guard<std::mutex> l{mux};};}
#else
#include <freertos/FreeRTOS.h>
namespace {portMUX_TYPE mux=portMUX_INITIALIZER_UNLOCKED;struct Lock{Lock(){portENTER_CRITICAL(&mux);}~Lock(){portEXIT_CRITICAL(&mux);}};}
#endif
namespace led_return {namespace {
struct Event{uint64_t at;uint32_t session;uint8_t mask;};
struct Storage{Snapshot s;Event ring[64]{};unsigned head=0,count=0;uint64_t started=0,lastService=0;uint32_t window=0;uint8_t frame[1+sizeof(Message)-1+2]{},byte=0,bits=0,used=0;bool clockKnown=false,clock=false,sync=false;} data;
void inc(uint32_t& n){if(n!=UINT32_MAX)++n;}
void resetDecoder(){data.window=0;data.byte=data.bits=data.used=0;data.clockKnown=false;data.sync=false;}
void consume(const Event&e){
 bool clock=(e.mask&2)!=0;if(!data.clockKnown){data.clockKnown=true;data.clock=clock;return;}if(clock==data.clock)return;data.clock=clock;
 uint8_t bit=e.mask&1;
 if(!data.sync){data.window=(data.window<<1)|bit;if(data.window==0x45445231){data.sync=true;data.byte=data.bits=data.used=0;}return;}
 data.byte=uint8_t((data.byte<<1)|bit);if(++data.bits!=8)return;
 data.frame[data.used++]=data.byte;data.byte=data.bits=0;
 if(data.used==1&&data.frame[0]!=sizeof(Message)-1){data.s.state=State::InvalidFrame;return;}
 if(data.used==sizeof(data.frame)){
  const size_t n=sizeof(data.frame)-2;uint16_t crc=crc16(data.frame,n);uint16_t received=uint16_t(data.frame[n])<<8|data.frame[n+1];
  if(crc!=received||memcmp(data.frame+1,Message,sizeof(Message)-1)){data.s.state=State::InvalidFrame;return;}
  memcpy(data.s.text,Message,sizeof(Message));data.s.integrity=true;data.s.state=State::Complete;
 }
}
}
uint16_t crc16(const uint8_t*p,size_t n){uint16_t crc=0xffff;for(size_t i=0;i<n;++i){crc^=uint16_t(p[i])<<8;for(int j=0;j<8;++j)crc=(crc&0x8000)?uint16_t((crc<<1)^0x1021):uint16_t(crc<<1);}return crc;}
void observe(uint8_t mask,uint32_t session,uint64_t at){Lock l;if(session!=data.s.session){inc(data.s.rejected);return;}inc(data.s.reports);data.s.mask=mask&7;data.s.lastReportUs=at;data.s.observed=data.s.connected=true;data.s.disconnected=false;
 if(data.s.state!=State::Receiving)return;
 if(data.count==64){inc(data.s.overflow);data.s.state=State::Overflow;data.count=0;return;}
 data.ring[(data.head+data.count)%64]={at,session,uint8_t(mask&7)};++data.count;
}
void rejected(){Lock l;inc(data.s.rejected);}
void invalidate(uint32_t session){Lock l;data.s.session=session;data.s.disconnected=data.s.disconnected||data.s.connected;data.s.connected=data.s.observed=false;data.count=data.head=0;if(data.s.state==State::Receiving)data.s.state=State::Disconnected;resetDecoder();}
bool start(uint64_t now){Lock l;if(data.s.state==State::Receiving)return false;data.s.state=State::Receiving;data.s.text[0]=0;data.s.integrity=false;data.started=data.lastService=now;data.count=data.head=0;resetDecoder();return true;}
void stop(){Lock l;if(data.s.state==State::Receiving)data.s.state=State::Stopped;data.count=data.head=0;}
void clear(){Lock l;data.s.state=State::Idle;data.s.text[0]=0;data.s.integrity=false;data.count=data.head=0;resetDecoder();}
void service(uint64_t now){Lock l;if(data.s.state!=State::Receiving)return;if(now<data.lastService){data.s.state=State::ClockError;data.count=0;return;}data.lastService=now;if(now-data.started>=TimeoutUs){data.s.state=State::Timeout;data.count=0;return;}
 for(unsigned i=0;i<16&&data.count&&data.s.state==State::Receiving;++i){Event e=data.ring[data.head];data.head=(data.head+1)%64;--data.count;if(e.session!=data.s.session||e.at<data.started)continue;if(e.at>now){data.s.state=State::ClockError;break;}consume(e);}
 if(data.s.state!=State::Receiving)data.count=0;
}
Snapshot snapshot(uint64_t now){Lock l;Snapshot s=data.s;s.capturedAtUs=now;s.queued=data.count;s.stale=s.observed&&(now<s.lastReportUs||now-s.lastReportUs>StaleUs);return s;}
size_t storageBytes(){return sizeof(data);}
}
