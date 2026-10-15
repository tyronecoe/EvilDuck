// Exact extracted pinned response classes/bodies, with File and abstract base mocks.
#include "Arduino.h"
#include "SD.h"
#include <memory>
#include <stdexcept>
#include <iostream>
namespace fs{using File=::File;using FS=SDClass;}
namespace asyncsrv{constexpr const char*empty="";}
using AwsTemplateProcessor=void*;
class AsyncAbstractResponse {
 public:int _code=0;String _contentType;size_t _contentLength=0;bool _sendContentLength=false,_chunked=false;AwsTemplateProcessor _callback;
 explicit AsyncAbstractResponse(AwsTemplateProcessor c=nullptr):_callback(c){}virtual ~AsyncAbstractResponse()=default;
 virtual bool _sourceValid()const{return false;}virtual size_t _fillBuffer(uint8_t*,size_t){return 0;}
 void addHeader(const String&,const String&,bool){}
};
static const char T__gz[]=".gz",T_gzip[]="gzip",T_Content_Encoding[]="Content-Encoding",T_attachment[]="attachment; filename=\"",T_Content_Disposition[]="Content-Disposition",T_inline[]="inline";
#define memcpy_P std::memcpy
#include "framework_bodies.inc"
// This non-exercised MIME lookup branch must not simulate successful support.
void AsyncFileResponse::_setContentTypeFromPath(const String&){throw std::runtime_error("unexecuted MIME lookup");}
static unsigned assertions=0;static void check(bool b,const char*m){++assertions;if(!b)throw std::runtime_error(m);}
static std::unique_ptr<AsyncFileResponse> create(){File f=SD.open("/x.txt",FILE_READ);return std::make_unique<AsyncFileResponse>(f,"/x.txt","text/plain",false,nullptr);}
int main(int argc,char**argv){try{check(argc==2,"case");std::string id=argv[1];mscMock::reset();mscMock::put("/x.txt",4);mscMock::nodes["/x.txt"]->bytes={'a','b','c','d'};
 if(id=="F01"){auto r=create();check(r->_sourceValid()&&mscMock::closes==0,"File retained after constructor caller returns");uint8_t b[4]{};check(r->_fillBuffer(b,2)==2&&b[0]=='a'&&b[1]=='b',"actual fill after handler scope");r.reset();check(mscMock::closes==1,"actual destructor closes File");}
 else if(id=="F02"){auto r=create();bool disconnectHookSeesRetainedFile=r->_sourceValid();check(disconnectHookSeesRetainedFile&&mscMock::closes==0,"source-derived request callback ordering: disconnect hook alone is not cleanup");r.reset();check(mscMock::closes==1,"cleanup only at real response destructor");}
 else if(id=="F03"){for(unsigned i=0;i<100;++i){auto r=create();check(r->_sourceValid(),"repeated response has source");}check(mscMock::closes==100,"one close per destroyed response");}
 else if(id=="F04"){static const uint8_t bytes[]={'a','b','c','d'};AsyncProgmemResponse r(200,"text/plain",bytes,4);uint8_t out[8]{};check(r._sourceValid(),"immutable source valid");check(r._fillBuffer(out,2)==2&&out[0]=='a',"first immutable chunk");check(r._fillBuffer(out,8)==2&&out[0]=='c'&&out[1]=='d',"bounded remaining chunk");check(r._fillBuffer(out,8)==0&&mscMock::opens==0,"EOF no File");}
 else if(id=="F05"){AsyncFileResponse r(File{},"/none.txt","text/plain",false,nullptr);uint8_t b[4]{};check(!r._sourceValid()&&r._fillBuffer(b,4)==0,"missing File stays invalid");}
 else check(false,"unknown");std::cout<<"PASS "<<id<<" ("<<assertions<<" assertions)\n";
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
