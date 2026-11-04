// Native HTTP base/header/transport are inert mocks. Request forwarding,
// constructors, _fillBuffer, WString and handleStatic are extracted verbatim.
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <functional>
#include <iostream>
#include <map>
#include <memory>
#include <stdexcept>
#include <string>
#include <vector>
#include "WString.h"

static size_t quota=1000000, used=0, peak=0, refusals=0, largest_limit=1000000, largest_requested=0;
static size_t assertions=0, groups=0;
static std::map<void*,size_t> allocated;
extern "C" void *budget_realloc(void *old,size_t n) {
  size_t prior=old?allocated.at(old):0;
  largest_requested=std::max(largest_requested,n);
  if(n>largest_limit || used-prior+n>quota){++refusals;return nullptr;}
  void *p=std::realloc(old,n);if(!p)return nullptr;
  if(old)allocated.erase(old);allocated[p]=n;used=used-prior+n;peak=std::max(peak,used);return p;
}
extern "C" void budget_free(void *p) {
  if(!p)return;
  auto i=allocated.find(p);assert(i!=allocated.end());used-=i->second;allocated.erase(i);std::free(p);
}
static void check(bool condition,const char *message){++assertions;if(!condition)throw std::runtime_error(message);}
static void reset(size_t next_quota=1000000,size_t next_largest=1000000) {
  check(used==0&&allocated.empty(),"WString allocation survived prior group");
  quota=next_quota;largest_limit=next_largest;peak=refusals=largest_requested=0;
}
static void report(const std::string&name,size_t before) {
  ++groups;
  std::cout<<"{\"name\":\""<<name<<"\",\"status\":\"PASS\",\"assertions\":"<<(assertions-before)
    <<",\"simulated_WString_peak_bytes\":"<<peak<<",\"refused_WString_allocations\":"<<refusals
    <<",\"largest_WString_allocation_requested\":"<<largest_requested<<"}"<<std::endl;
}

using AwsTemplateProcessor=std::function<String(const String&)>;
namespace asyncsrv { static const char empty[]=""; }
const char *T_text_plain="text/plain",*T_Connection="Connection",*T_close="close";
struct AsyncWebServerResponse {
  int _code=0;
  String _contentType;
  size_t _contentLength=0;
  bool _sendContentLength=true;
  virtual ~AsyncWebServerResponse()=default;
  bool addHeader(const char*,const char*,bool){return true;}
};
struct AsyncAbstractResponse:AsyncWebServerResponse {
  AwsTemplateProcessor _callback;
  explicit AsyncAbstractResponse(AwsTemplateProcessor c):_callback(c){}
};
struct AsyncBasicResponse:AsyncWebServerResponse {
  String _content;
  AsyncBasicResponse(int,const char*,const char*);
};
struct AsyncProgmemResponse:AsyncAbstractResponse {
  const uint8_t *_content;
  size_t _index;
  AsyncProgmemResponse(int,const char*,const uint8_t*,size_t,AwsTemplateProcessor=nullptr);
  size_t _fillBuffer(uint8_t*,size_t);
};
struct AsyncWebServerRequest {
  String path;
  std::unique_ptr<AsyncWebServerResponse> response;
  size_t sends=0;
  explicit AsyncWebServerRequest(const char*p):path(p){}
  String url(){return path;}
  void send(AsyncWebServerResponse*r){++sends;response.reset(r);}
  AsyncWebServerResponse *beginResponse(int,const char*,const char*,AwsTemplateProcessor=nullptr);
  AsyncWebServerResponse *beginResponse(int,const char*,const uint8_t*,size_t,AwsTemplateProcessor=nullptr);
#include "request_inline.inc"
};
#include "actual_sdk.inc"
#include "webfiles.h"
#define EVILDUCK_PORTABLE_ROUTE_B 1
#include "actual_handlers.inc"

struct Route {const char*path;const char*name;const char*mime;const char*data;size_t bytes;int status;};
#define RESOURCE(path,name,mime,status) {path,#name,mime,name,sizeof(name)-1,status}
static const Route routes[]={
 RESOURCE("/",INDEX_HTML,"text/html",200),RESOURCE("/index.html",INDEX_HTML,"text/html",200),
 RESOURCE("/index.htm",INDEX_HTML,"text/html",200),RESOURCE("/settings.html",SETTINGS_HTML,"text/html",200),
 RESOURCE("/terminal.html",TERMINAL_HTML,"text/html",200),RESOURCE("/credits.html",CREDITS_HTML,"text/html",200),
 RESOURCE("/error404.html",ERROR404_HTML,"text/html",404),RESOURCE("/style.css",STYLE_CSS,"text/css",200),
 RESOURCE("/index.js",INDEX_JS,"application/javascript",200),RESOURCE("/script.js",INDEX_JS,"application/javascript",200),
 RESOURCE("/settings.js",SETTINGS_JS,"application/javascript",200),RESOURCE("/terminal.js",TERMINAL_JS,"application/javascript",200)};
static const Route&route(const char *path){for(const auto&r:routes)if(!std::strcmp(r.path,path))return r;throw std::runtime_error("Missing route fixture");}
static std::unique_ptr<AsyncWebServerResponse> response(const char*path,bool baseline=false) {
 AsyncWebServerRequest request(path);
 if(baseline)handleStaticBaseline(&request);else handleStatic(&request);
 check(request.sends==1,"Static handler did not produce exactly one response");
 check(bool(request.response),"No response captured");return std::move(request.response);
}
static void validate(AsyncWebServerResponse&r,const Route&e,bool progmem) {
 check(r._code==e.status,"Wrong status");check(std::strcmp(r._contentType.c_str(),e.mime)==0,"Wrong MIME");
 check(r._sendContentLength,"Content-Length disabled");check(r._contentLength==e.bytes,"Wrong explicit body length");
 check((dynamic_cast<AsyncProgmemResponse*>(&r)!=nullptr)==progmem,"Wrong SDK constructor/overload selected");
 if(progmem){auto&p=dynamic_cast<AsyncProgmemResponse&>(r);check(p._content==reinterpret_cast<const uint8_t*>(e.data),"Resource copied or pointer changed");check(!p._callback,"Unexpected template processing");}
}
static std::string drain(AsyncWebServerResponse&r) {
 if(auto*b=dynamic_cast<AsyncBasicResponse*>(&r))return std::string(b->_content.c_str(),b->_content.length());
 auto&p=dynamic_cast<AsyncProgmemResponse&>(r);
 const size_t chunks[]={0,1,7,0,1460,4096,23,0,8192};
 std::string output;size_t turn=0;const size_t remaining=p._contentLength-p._index;
 while(output.size()<remaining){
  size_t capacity=chunks[turn++%9];std::vector<uint8_t>buffer(capacity+2,0xA5);
  size_t n=p._fillBuffer(buffer.data()+1,capacity);
  check(n==std::min(capacity,remaining-output.size()),"Wrong chunk size or zero-capacity advance");
  check(buffer.front()==0xA5&&buffer.back()==0xA5,"Chunk buffer guard overwritten");
  output.append(reinterpret_cast<char*>(buffer.data()+1),n);
 }
 uint8_t eof[8]={};for(int i=0;i<3;++i)check(p._fillBuffer(eof,sizeof(eof))==0,"EOF not stable");
 return output;
}
static void equal(const std::string&body,const Route&e){check(body.size()==e.bytes,"Body truncated or extended");check(std::memcmp(body.data(),e.data,e.bytes)==0,"Response bytes differ from actual resource");}
static void write(const std::string&file,const std::string&body){std::ofstream f(file,std::ios::binary);check(bool(f),"Cannot create served body");f.write(body.data(),body.size());check(bool(f),"Cannot write served body");}

int main(int argc,char**argv)try{
 check(argc==2,"Supply served output directory");const std::string served=argv[1];
 for(const auto&e:routes){
  reset();size_t before=assertions;{auto r=response(e.path);validate(*r,e,true);auto body=drain(*r);equal(body,e);write(served+"/"+e.name+".bin",body);check(refusals==0,"Unexpected WString allocation refusal");}report(std::string("route_explicit_flash_")+e.path,before);
 }
 for(const auto&e:routes){reset();size_t before=assertions;{auto r=response(e.path,true);validate(*r,e,false);equal(drain(*r),e);}report(std::string("control_baseline_copy_")+e.path,before);}
 for(bool reverse:{false,true}){
  reset(50000);size_t before=assertions;{const char*first=reverse?"/index.js":"/style.css";const char*second=reverse?"/style.css":"/index.js";
   auto a=response(first,true);validate(*a,route(first),false);auto b=response(second,true);
   check(b->_code==200&&b->_contentLength==0,"Old empty-200 allocation defect not reproduced");check(drain(*b).empty(),"Old failed body not empty");check(refusals>=1,"Old copy unexpectedly avoided allocation refusal");
  }report(reverse?"negative_old_JS_then_CSS_50k":"negative_old_CSS_then_JS_50k",before);
 }
 reset(50000);{size_t before=assertions;{auto css=response("/style.css");auto js=response("/index.js");validate(*css,route("/style.css"),true);validate(*js,route("/index.js"),true);equal(drain(*css),route("/style.css"));equal(drain(*js),route("/index.js"));check(refusals==0,"New concurrent responses refused allocation");check(largest_requested<1024,"New response allocated a complete body");}report("concurrent_new_CSS_JS_same_50k",before);}
 reset(50000);{size_t before=assertions;{auto css=response("/style.css",true);auto js=response("/index.js");validate(*css,route("/style.css"),false);validate(*js,route("/index.js"),true);equal(drain(*js),route("/index.js"));check(refusals==0,"New stream failed while old CSS copy retained");}report("new_JS_under_existing_old_CSS_pressure",before);}
 reset(50000,31935);{size_t before=assertions;{auto old=response("/index.js",true);check(old->_code==200&&old->_contentLength==0&&refusals>=1,"Old fragmentation defect not reproduced");}report("negative_old_largest_block_31935",before);}
 reset(50000,31935);{size_t before=assertions;{auto r=response("/index.js");validate(*r,route("/index.js"),true);equal(drain(*r),route("/index.js"));check(refusals==0,"Explicit stream requested forbidden full-body block");}report("new_stream_largest_block_31935",before);}
 reset(50000);{size_t before=assertions;{auto a=response("/index.js");auto b=response("/index.js");auto&pa=dynamic_cast<AsyncProgmemResponse&>(*a);auto&pb=dynamic_cast<AsyncProgmemResponse&>(*b);uint8_t first[11],other[5];check(pa._fillBuffer(first,sizeof(first))==sizeof(first),"First instance prefix");check(pb._fillBuffer(other,sizeof(other))==sizeof(other),"Second instance prefix");check(std::memcmp(first,INDEX_JS,sizeof(first))==0&&std::memcmp(other,INDEX_JS,sizeof(other))==0,"Per-instance cursor shared");a.reset();auto suffix=drain(*b);std::string complete(reinterpret_cast<char*>(other),sizeof(other));complete+=suffix;equal(complete,route("/index.js"));check(refusals==0,"Cancellation caused allocation failure");}report("per_instance_cursor_cancel_independent",before);}
 for(const char*p:{"/favicon.ico","/unrecognized.js"}){reset();size_t before=assertions;{auto r=response(p);check(r->_code==503,"Unknown static path fallback changed");check(dynamic_cast<AsyncBasicResponse*>(r.get())!=nullptr,"Unknown fallback overload changed");check(std::strcmp(r->_contentType.c_str(),"text/plain")==0,"Unknown fallback MIME changed");check(drain(*r)=="Dynamic filesystem responses disabled in Route B candidate","Unknown fallback body changed");}report(std::string("preserved_fallback_")+p,before);}
 reset();std::cout<<"{\"summary\":true,\"PASS\":"<<groups<<",\"FAIL\":0,\"assertions\":"<<assertions<<",\"WString_live_allocations\":"<<allocated.size()<<"}"<<std::endl;
 return 0;
}catch(const std::exception&e){std::cerr<<"FAIL: "<<e.what()<<std::endl;return 1;}
