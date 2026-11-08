#pragma once
// Actual handler/auth/state-name source is extracted verbatim; only lower APIs are mocks.
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <iostream>
#include <map>
#include <stdexcept>
#include <string>
#include "WString.h"
#include "hid_backend.h"
#include "feedback_diag.h"
static unsigned checks=0,groups=0;
static void check(bool value,const char* why){++checks;if(!value)throw std::runtime_error(why);}
static std::map<void*,size_t> allocated;
static size_t allocationLimit=1000000,largestRequest=0;
extern "C" void* budget_realloc(void* old,size_t bytes){largestRequest=std::max(largestRequest,bytes);if(bytes>allocationLimit)return nullptr;void* p=std::realloc(old,bytes);if(!p)return nullptr;if(old)allocated.erase(old);allocated[p]=bytes;return p;}
extern "C" void budget_free(void* p){if(p){check(allocated.erase(p)==1,"unknown WString allocation");std::free(p);}}
namespace execution{
 enum class Owner{HttpStatus};static bool busy=false,tryBusy=false;static int depth=0;
 class BoundedGuard{bool entered;public:explicit BoundedGuard(Owner):entered(!busy){if(entered)++depth;}~BoundedGuard(){if(entered)--depth;}explicit operator bool()const{return entered;}};
 class TryGuard{bool entered;public:TryGuard():entered(!tryBusy){if(entered)++depth;}~TryGuard(){if(entered)--depth;}explicit operator bool()const{return entered;}};
}
namespace settings{String getWebPassword(){return String("synthetic-password-only");}}
struct AsyncWebParameter{String data;String value()const{return data;}};
struct AsyncWebServerResponse{int status;std::string type,body;std::map<std::string,std::string> headers;AsyncWebServerResponse(int s,const char*t,const String& b):status(s),type(t),body(b.c_str()){}void addHeader(const char*n,const char*v){headers[n]=v;}};
struct AsyncWebServerRequest{
 std::map<std::string,String> headers;std::map<std::string,AsyncWebParameter> params;int status=0;std::string type,body;std::map<std::string,std::string> responseHeaders;bool refuseResponse=false;
 bool hasHeader(const char* n){return headers.count(n)!=0;}String header(const char*n){return headers.at(n);}bool hasParam(const char*n){return params.count(n)!=0;}AsyncWebParameter* getParam(const char*n){return &params.at(n);}
 void send(int s,const char*t,const char*b){status=s;type=t;body=b;}void send(int s,const char*t,const String&b){send(s,t,b.c_str());}
 AsyncWebServerResponse* beginResponse(int s,const char*t,const String&b){return refuseResponse?nullptr:new AsyncWebServerResponse(s,t,b);}
 void send(AsyncWebServerResponse*r){check(r!=nullptr,"null response");status=r->status;type=r->type;body=r->body;responseHeaders=r->headers;delete r;}
};
namespace caps_trial{constexpr const char* BuildId="MOCK-USB-CAPTURE-ONLY-v1";}
static uint32_t nowMs=7000;uint32_t millis(){return nowMs;}
static unsigned bootCalls=0;
namespace feedback_diag{Snapshot snapshot(){++bootCalls;Snapshot s;s.boot=0x1122334455667788ull;return s;}}
