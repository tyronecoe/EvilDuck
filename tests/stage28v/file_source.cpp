#include "file_source.h"
#include <cstring>
#include <algorithm>
namespace route_u {
bool FileSource::open(const char* path){
 close();storage::Ref ref;
 if(!storage::parseRef(String(path),ref)||!storage::exists(ref))return false;
 file_=storage::openRead(ref);if(!file_||file_.isDirectory()){close();return false;}
 expected_=file_.size();offset_=verified_=0;verifying_=false;
 if(expected_>ds_preview::MaxSource||!file_.seek(0)||file_.position()!=0){close();return false;}return true;
}
void FileSource::close(){file_.close();}
bool FileSource::seek(void* ctx,size_t at){auto& s=*static_cast<FileSource*>(ctx);if(!s.file_||s.file_.size()!=s.expected_||at>s.expected_||!s.file_.seek(at)||s.file_.position()!=at)return false;s.offset_=at;return true;}
ds_preview::ReadResult FileSource::read(void* ctx,char* out,size_t limit){
 using R=ds_preview::ReadStatus;auto& s=*static_cast<FileSource*>(ctx);
 if(!s.file_||s.file_.size()!=s.expected_||s.file_.position()!=s.offset_)return {R::Error,0};
 if(s.mayRead&&!s.mayRead())return {R::Retry,0};
 if(s.offset_==s.expected_)return {R::Eof,0};
 size_t n=std::min({limit,size_t(ds_preview::ReadChunk),s.expected_-s.offset_});
 size_t got=s.file_.read(reinterpret_cast<uint8_t*>(out),n);
 if(!got||got>n||s.file_.position()!=s.offset_+got||s.file_.size()!=s.expected_)return {R::Error,0};
 s.offset_+=got;return {R::Data,got};
}
FileSource::Verify FileSource::verify(const char* bytes,size_t n){
 if(!file_||n!=expected_||file_.size()!=expected_)return Verify::Error;
 if(!verifying_){if(!file_.seek(0)||file_.position()!=0)return Verify::Error;verifying_=true;}
 if(file_.position()!=verified_)return Verify::Error;
 if(verified_==expected_){close();return Verify::Complete;}
 uint8_t chunk[ds_preview::ReadChunk];size_t want=std::min(sizeof(chunk),expected_-verified_);
 size_t got=file_.read(chunk,want);
 if(!got||got>want||file_.position()!=verified_+got||file_.size()!=expected_||memcmp(chunk,bytes+verified_,got))return Verify::Error;
 verified_+=got;return Verify::Pending;
}
}
