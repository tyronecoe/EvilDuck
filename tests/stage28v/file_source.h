#pragma once
#include "core.h"
#include "storage.h"
namespace route_u {
class FileSource {
 File file_;size_t expected_=0,offset_=0,verified_=0;bool verifying_=false;
 static ds_preview::ReadResult read(void*,char*,size_t);static bool seek(void*,size_t);
 public:
 // Optional scheduling poll, not a claim that File has a retry/error API.
 bool(*mayRead)()=nullptr;
 bool open(const char* path);void close();bool opened()const{return bool(file_);}
 ds_preview::Reader reader(){return {read,seek,this,expected_};}
 enum class Verify{Pending,Complete,Error};
 Verify verify(const char* captured,size_t bytes);
};
}
