#pragma once
#include "FS.h"
#define FILE_READ "r"
#define FILE_WRITE "w"
#define FILE_APPEND "a"
#define CARD_NONE 0
namespace mscMock {
inline bool mountOk=true;
inline unsigned mounts=0;
inline void put(const std::string &path,size_t size,bool directory=false){
 auto n=std::make_shared<Node>();n->path=path;n->directory=directory;n->bytes.resize(size);nodes[path]=n;
}
inline void reset(){
 nodes.clear();present=true;mountOk=true;openFail=seekFail=false;shortRead=shortWrite=SIZE_MAX;
 opens=closes=seeks=reads=writes=flushes=creates=truncates=mounts=0;lastSeek=0;
 put("/",0,true);put("/scripts",0,true);put("/sys",0,true);
}
}
class SDClass {
public:
 template<class... T>bool begin(T...){++mscMock::mounts;return mscMock::present&&mscMock::mountOk;}
 uint8_t cardType()const{return mscMock::present?1:0;}
 uint64_t totalBytes()const{return 64*1024*1024;}
 uint64_t usedBytes()const{return 4*1024*1024;}
 bool exists(const String &p)const{return mscMock::present&&mscMock::nodes.count(p.c_str());}
 bool mkdir(const String &p){if(!mscMock::present)return false;mscMock::put(p.c_str(),0,true);return true;}
 bool remove(const String &p){return mscMock::present&&mscMock::nodes.erase(p.c_str());}
 bool rename(const String &a,const String &b){if(!exists(a))return false;auto n=mscMock::nodes[a.c_str()];mscMock::nodes.erase(a.c_str());n->path=b.c_str();mscMock::nodes[b.c_str()]=n;return true;}
 File open(const String &p,const char *mode=FILE_READ){
  ++mscMock::opens;if(!mscMock::present||mscMock::openFail)return {};
  auto i=mscMock::nodes.find(p.c_str());bool writable=std::string(mode)!="r";
  if(i==mscMock::nodes.end()){
   if(std::string(mode)=="r"||std::string(mode)=="r+")return {};
   ++mscMock::creates;mscMock::put(p.c_str(),0);i=mscMock::nodes.find(p.c_str());
  }
  if(std::string(mode)=="w"){++mscMock::truncates;i->second->bytes.clear();}
  File f(i->second,writable);if(std::string(mode)=="a")f.seek(f.size());return f;
 }
};
inline SDClass SD;
