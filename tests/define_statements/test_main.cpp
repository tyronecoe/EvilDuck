#include "core.h"
#include <cassert>
#include <cstdio>
#include <cstring>
#include <string>
using namespace ds_preview;
struct Capture { std::string text; unsigned delays=0,retries=0; bool retry=false; };
Accept sink(void* ctx,const Event& e){auto& c=*static_cast<Capture*>(ctx);if(c.retry&&c.retries++%2==0)return Accept::Retry;if(e.type==EventType::Character)c.text+=char(e.value);if(e.type==EventType::KeyTap&&e.value==0x28)c.text+='\n';if(e.type==EventType::Delay)++c.delays;return Accept::Accepted;}
unsigned cases=0;
void run(const std::string& source,const char* expected,bool retry=false,ErrorCode runtimeError=ErrorCode::None,unsigned delays=0){
 Program p;assert(p.compile(source.data(),source.size()));Runtime rt;Capture c;c.retry=retry;assert(rt.start(p,sink,&c));for(unsigned t=0;rt.state()==State::Running&&t<100000;++t)rt.tick(t/10);
 assert(rt.state()==(runtimeError==ErrorCode::None?State::Completed:State::Error));assert(rt.error().code==runtimeError);assert(c.text==expected);assert(c.delays==delays);++cases;
}
void reject(const std::string& source,unsigned line=0){Program p;assert(!p.compile(source.data(),source.size()));assert(!p.ready());if(line)assert(p.error().line==line);++cases;}
int main(){
 run("DEFINE #STEP $count = ($count + 1)\nDEFINE #MARK STRING PASS\nVAR $count = 0\nIF FALSE THEN\nSTRING FAIL\nELSE IF ($count == 0) THEN\n#STEP\nELSE\nSTRING FAIL\nEND_IF\nIF ($count == 1) THEN\n#MARK\nEND_IF\n","PASS",true);
 run("#M\nDEFINE #M STRINGLN hello\n","hello\n",true);
 run("DEFINE M STRING ok\nM\n","ok");
 run("DEFINE #M STRING #OTHER\nDEFINE #OTHER changed\n#M\n","#OTHER");
 run("DEFINE #D DELAY 1\n#D\nSTRING done\n","done",true,ErrorCode::None,1);
 run("DEFINE #M STRING fail\nIF FALSE THEN\n#M\nEND_IF\nFUNCTION unused()\n#M\nEND_FUNCTION\nSTRING ok\n","ok");
 run("DEFINE #M $x = next()\nVAR $x = 0\nVAR $calls = 0\nFUNCTION next()\n$calls = ($calls + 1)\nRETURN $calls\nEND_FUNCTION\n#M\nIF (($x == 1) && ($calls == 1)) THEN\nSTRING once\nEND_IF\n","once",true);
 run("DEFINE #M $x = 1\nIF FALSE THEN\nVAR $x = 0\nEND_IF\n#M\n","",false,ErrorCode::Uninitialized);
 for(const char* value:{"VAR $x = 1","IF TRUE THEN","$_JITTER_ENABLED = TRUE","#B","STRING","END_IF","FUNCTION f()","$x += 1","$x = (65535 + 1)"})reject(std::string("DEFINE #M ")+value+"\nVAR $x = 0\n#M\n",3);
 reject("DEFINE #M $missing = 1\n#M\n",2);
 reject("DEFINE #M DELAY 1\n#M 500\n",2);
 reject("DEFINE #M VAR $x = 0\nIF FALSE THEN\n#M\nEND_IF\n",3);
 run("DEFINE #M VAR $x = 0\nIF_DEFINED_TRUE #ABSENT\n#M\nEND_IF_DEFINED\nSTRING ok\n","ok");
 run("DEFINE ENTER STRING fail\nENTER\n","\n");
 run("DEFINE #M STRING replacement\nSTRING\n#M\nEND_STRING\n","STRING replacement");
 reject("DEFINE #M STRING a\nDEFINE #M STRING b\n#M\n");
 std::string name="#"+std::string(30,'a');run("DEFINE "+name+" STRING bound\n"+name+"\n","bound");reject("DEFINE "+name+"a STRING bad\n");
 run("DEFINE #M STRING "+std::string(56,'x')+"\n#M\n",std::string(56,'x').c_str());reject("DEFINE #M STRING "+std::string(57,'x')+"\n#M\n");
 run("DEFINE #M $x = ($x + 1)\nVAR $x = 65535\n#M\n","",false,ErrorCode::Arithmetic);
 reject("DEFINE #M STRING okay\nSTRING before\n#M\nREPEAT 1\n",4);
 reject("DEFINE #M $x = #N\nDEFINE #N 1\nVAR $x = 0\n#M\n",4);
 reject("DEFINE #M DELAY #N\nDEFINE #N 1\n#M\n",3);
 reject("DEFINE #M IF TRUE THEN\nFUNCTION unused()\n#M\nEND_FUNCTION\n",3);
 run("DEFINE #M STRING okay\nVAR $calls = 0\nIF TRUE THEN\nIF TRUE THEN\n#M\nEND_IF\nELSE IF next() THEN\nSTRING fail\nEND_IF\nIF ($calls == 0) THEN\nSTRING skipped\nEND_IF\nFUNCTION next()\n$calls = ($calls + 1)\nRETURN TRUE\nEND_FUNCTION\n","okayskipped");
 std::printf("PASS %u focused scenarios\n",cases);
}
