#pragma once
#include <stdint.h>
namespace mscMock {
inline int32_t (*readCallback)(uint32_t,uint32_t,void*,uint32_t)=nullptr;
inline int32_t (*writeCallback)(uint32_t,uint32_t,uint8_t*,uint32_t)=nullptr;
inline bool (*startCallback)(uint8_t,bool,bool)=nullptr;
inline bool media=false,writable=false,beginOk=true;
inline unsigned starts=0,ends=0;
inline uint32_t blocks=0;inline uint16_t blockSize=0;
}
class USBMSC {
public:
 void mediaPresent(bool b){mscMock::media=b;}
 void isWritable(bool b){mscMock::writable=b;}
 void vendorID(const char*){}void productID(const char*){}void productRevision(const char*){}
 void onRead(decltype(mscMock::readCallback) f){mscMock::readCallback=f;}
 void onWrite(decltype(mscMock::writeCallback) f){mscMock::writeCallback=f;}
 void onStartStop(decltype(mscMock::startCallback) f){mscMock::startCallback=f;}
 bool begin(uint32_t n,uint16_t s){++mscMock::starts;mscMock::blocks=n;mscMock::blockSize=s;
  return mscMock::beginOk&&n&&s&&mscMock::readCallback&&mscMock::writeCallback;}
 void end(){++mscMock::ends;mscMock::media=false;mscMock::writable=false;mscMock::blocks=mscMock::blockSize=0;
 mscMock::readCallback=nullptr;mscMock::writeCallback=nullptr;mscMock::startCallback=nullptr;}
};
