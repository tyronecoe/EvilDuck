#pragma once
#include "Arduino.h"
#include <memory>
#include <map>
#include <vector>
#include <limits>
namespace mock {
inline size_t failReadAt=SIZE_MAX,failSeekAt=SIZE_MAX,bytesRead=0,readCalls=0,seekCalls=0,sourceSizeIncrease=0;
}
namespace mscMock {
struct Node { std::vector<uint8_t> bytes; std::string path; bool directory=false; };
inline std::map<std::string,std::shared_ptr<Node>> nodes;
inline bool present=true,openFail=false,seekFail=false;
inline size_t shortRead=SIZE_MAX,shortWrite=SIZE_MAX;
inline unsigned opens=0,closes=0,seeks=0,reads=0,writes=0,flushes=0,creates=0,truncates=0;
inline uint32_t lastSeek=0;
}
class File {
  struct Handle {std::shared_ptr<mscMock::Node> node;size_t offset=0,next=0;bool open=true,sd=false,writable=false;};
  std::shared_ptr<Handle> h;
public:
  File()=default;
  explicit File(const String &s):h(std::make_shared<Handle>()) {
    h->node=std::make_shared<mscMock::Node>();
    h->node->bytes.assign(s.c_str(),s.c_str()+s.length());
  }
  File(std::shared_ptr<mscMock::Node> n,bool writable):h(std::make_shared<Handle>()) {h->node=n;h->sd=true;h->writable=writable;}
  explicit operator bool()const{return h&&h->open;}
  size_t size()const{return *this ? h->node->bytes.size()+(h->sd?0:mock::sourceSizeIncrease):0;}
  size_t position()const{return h?h->offset:0;}
  bool available()const{return *this&&position()<size();}
  bool isDirectory()const{return *this&&h->node->directory;}
  const char *name()const{return h?h->node->path.c_str():"";}
  bool seek(size_t p){
    if(h&&h->sd){++mscMock::seeks;mscMock::lastSeek=p;}
    else ++mock::seekCalls;
    if(!*this||p>size()||(h->sd?(mscMock::seekFail||!mscMock::present):p==mock::failSeekAt))return false;
    h->offset=p;return true;
  }
  size_t read(uint8_t *buffer,size_t size){
    if(!*this)return 0;
    if(h->sd){++mscMock::reads;if(!mscMock::present)return 0;}
    else {++mock::readCalls;if(position()>=mock::failReadAt)return 0;}
    size_t n=std::min(size,h->node->bytes.size()-position());
    n=std::min(n,h->sd?mscMock::shortRead:mock::failReadAt-position());
    if(n)memcpy(buffer,h->node->bytes.data()+position(),n);
    h->offset+=n;if(!h->sd)mock::bytesRead+=n;return n;
  }
  size_t readBytes(char *buffer,size_t size){return read(reinterpret_cast<uint8_t*>(buffer),size);}
  size_t write(const uint8_t *buffer,size_t size){
    ++mscMock::writes;
    if(!*this||!h->writable||!mscMock::present)return 0;
    size_t n=std::min(size,mscMock::shortWrite);
    if(position()+n>h->node->bytes.size())h->node->bytes.resize(position()+n);
    if(n)memcpy(h->node->bytes.data()+position(),buffer,n);
    h->offset+=n;return n;
  }
  size_t print(const String &s){return write(reinterpret_cast<const uint8_t *>(s.c_str()),s.length());}
  void flush(){++mscMock::flushes;}
  void close(){if(*this){if(h->sd)++mscMock::closes;h->open=false;}}
  String readString(){
    std::string s;while(available()){uint8_t b;if(read(&b,1)!=1)break;s+=char(b);}return String(s);
  }
  String readStringUntil(char delimiter){
    std::string s;while(available()){uint8_t b;if(read(&b,1)!=1)break;if(b==delimiter)break;s+=char(b);}return String(s);
  }
  File openNextFile(){
    if(!isDirectory())return {};
    size_t i=0;std::string prefix=h->node->path=="/"?"/":h->node->path+"/";
    for(auto &entry:mscMock::nodes){if(entry.first.find(prefix)!=0||entry.first==h->node->path)continue;
      if(i++<h->next)continue;
      ++h->next;
      return File(entry.second,false);
    }
    return {};
  }
};
