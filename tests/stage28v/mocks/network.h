#pragma once
#include "Arduino.h"
#include <map>
#include <vector>
struct Param {String text;String value()const{return text;}};
class AsyncWebServerRequest {
 public:std::map<std::string,Param> query,body;std::map<std::string,String> headers;unsigned replies=0;int code=0;String response;
 bool hasHeader(const char*k){return headers.count(k);}String header(const char*k){return headers[k];}
 bool hasParam(const char*k,bool post=false){return (post?body:query).count(k);}
 Param* getParam(const char*k,bool post=false){return &(post?body:query).at(k);}
 String url(){return "/";}
 void send_P(int c,const char*t,const char*s){send(c,t,s);}
 template<class FS>void send(FS&,const String&,const String&){++replies;code=200;}
 void send(int c,const char*,const String&s){++replies;code=c;response=s;}
};
class AsyncWebSocket{public:explicit AsyncWebSocket(const char*){}template<class F>void onEvent(F){}};
class AsyncWebSocketClient {public:String output;void text(const char*s){output+=s;}};
enum AwsEventType{WS_EVT_DATA,WS_EVT_DISCONNECT};
constexpr int WS_TEXT=1;
struct AwsFrameInfo{int opcode=WS_TEXT;bool final=true;size_t index=0;};
struct MockUpdate{unsigned calls=0;bool begin(size_t){++calls;return true;}size_t write(uint8_t*,size_t n){++calls;return n;}bool end(bool){++calls;return true;}void abort(){++calls;}};
inline MockUpdate Update;
constexpr size_t UPDATE_SIZE_UNKNOWN=0;
using WebHandler=void(*)(AsyncWebServerRequest*);
using UploadHandler=void(*)(AsyncWebServerRequest*,String,size_t,uint8_t*,size_t,bool);
constexpr int HTTP_GET=0,HTTP_POST=1;
namespace networkMock{inline unsigned begins=0,registrations=0,modes=0,aps=0;}
class AsyncWebServer {
 public:struct Route{WebHandler done;UploadHandler upload;};std::map<std::pair<std::string,int>,Route> routes;
 explicit AsyncWebServer(int){}
 void on(const char*p,int method,WebHandler h,UploadHandler u=nullptr){++networkMock::registrations;routes[{p,method}]={h,u};}
 void addHandler(AsyncWebSocket*){}void onNotFound(WebHandler){}void begin(){++networkMock::begins;}
 void dispatch(const char*p,int method,AsyncWebServerRequest*r){routes.at({p,method}).done(r);}
};
