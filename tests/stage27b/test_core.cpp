#include "../../language_preview/core.h"
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <fstream>
#include <new>
#include <stdexcept>
#include <string>
#include <vector>
using namespace ds_preview;
static unsigned assertions=0;
static bool allocationProbe=false;static size_t allocations=0;
void* operator new(std::size_t n){if(allocationProbe)++allocations;if(void* p=std::malloc(n?n:1))return p;throw std::bad_alloc();}
void operator delete(void* p) noexcept{std::free(p);}
void operator delete(void* p,std::size_t) noexcept{std::free(p);}
#define CHECK(x) do{++assertions;if(!(x))throw std::runtime_error(std::string("Assertion ")+ #x +" at "+std::to_string(__LINE__));}while(0)
struct Capture {
 std::vector<Event> events;unsigned retries=0,calls=0;int failAfter=-1;Runtime* reentrant=nullptr;bool cancelInside=false,throwInside=false;
 static Accept sink(void* ptr,const Event& e){auto& c=*static_cast<Capture*>(ptr);++c.calls;if(c.throwInside)throw std::runtime_error("Synthetic sink fault");
  if(c.reentrant){c.reentrant->tick(0);if(c.cancelInside)c.reentrant->cancel();}
  if(c.retries){--c.retries;return Accept::Retry;}if(c.failAfter>=0&&c.events.size()>=static_cast<size_t>(c.failAfter))return Accept::Failed;
  c.events.push_back(e);return Accept::Accepted;
 }
 std::string visible()const{std::string out;for(auto e:events)if(e.type==EventType::Character)out+=static_cast<char>(e.value);else if(e.type==EventType::KeyTap&&e.value==0x28)out+='\n';return out;}
};
void compile(Program& p,const std::string& source){bool ok=p.compile(source.data(),source.size(),"harmless.duck");if(!ok)std::cerr<<message(p.error().code)<<" line "<<p.error().line<<"\n";CHECK(ok);CHECK(p.ready());}
void drive(Runtime& r,uint32_t begin=0,unsigned count=20000){for(unsigned i=0;i<count&&r.state()==State::Running;++i)r.tick(begin+i);CHECK(r.state()!=State::Running);}
uint16_t variable(Runtime& r,const char* name){uint16_t out=0;CHECK(r.variable(name,out));return out;}
void expression(const std::string& expr,uint16_t expected){Program p;compile(p,"VAR $result = "+expr+"\n");Capture c;Runtime r;CHECK(r.start(p,Capture::sink,&c));drive(r);CHECK(r.state()==State::Completed);CHECK(variable(r,"$result")==expected);CHECK(c.events.empty());}
void rejected(const std::string& source,ErrorCode code=ErrorCode::None){Program p;CHECK(!p.compile(source.data(),source.size(),"rejected.duck"));CHECK(!p.ready());CHECK(p.error().code!=ErrorCode::None);if(code!=ErrorCode::None)CHECK(p.error().code==code);Runtime r;Capture c;CHECK(!r.start(p,Capture::sink,&c));r.tick(0);CHECK(c.events.empty());}
void output(const std::string& source,const std::string& expected){Program p;compile(p,source);Capture c;Runtime r;CHECK(r.start(p,Capture::sink,&c));drive(r);CHECK(r.state()==State::Completed);CHECK(c.visible()==expected);}
void runtimeError(const std::string& source,ErrorCode code){Program p;compile(p,source);Capture c;Runtime r;CHECK(r.start(p,Capture::sink,&c));drive(r);CHECK(r.state()==State::Error);CHECK(r.error().code==code);}
void run(const std::string& name){
 if(name=="harmless_fixture_files"){
  std::ifstream good(std::string(PREVIEW_FIXTURES)+"/harmless.duck"),bad(std::string(PREVIEW_FIXTURES)+"/invalid.duck");CHECK(good.good()&&bad.good());
  std::string source((std::istreambuf_iterator<char>(good)),{}),invalid((std::istreambuf_iterator<char>(bad)),{});
  output(source,"ready\nmiddle\nready\ncomplete\n");rejected(invalid,ErrorCode::Syntax);
 }else if(name=="empty_comments"){
  output("","");output("REM comment\nREM ordinary IF FALSE\nREM_BLOCK DOCUMENTATION\nIF nonsense THEN\nSTRINGLN hidden\nEND_REM\nSTRINGLN parser-ok", "parser-ok\n");
  rejected("REMINDER",ErrorCode::UnknownStatement);rejected("END_REM",ErrorCode::Structure);rejected("REM_BLOCK\nSTRING hidden",ErrorCode::Structure);
 }else if(name=="line_endings_whitespace"){
  output("\xef\xbb\xbf\r\n\tREM comment\r\n  STRINGLN   hello   \r\n\r\nSTRING world", "  hello\nworld");
  output("STRINGLN IF WHILE FUNCTION END_IF\nSTRINGLN $n", "IF WHILE FUNCTION END_IF\n$n\n");
  rejected("REM bad\rSTRING x",ErrorCode::InvalidSource);rejected(std::string("STRING a\0b",10),ErrorCode::InvalidSource);
 }else if(name=="all_numeric_operators"){
  const char* expr[]={"5 + 7","9 - 2","6 * 7","43 / 2","43 % 2","2 ^ 3","7 == 7","7 != 8","1 < 2","2 > 1","2 <= 2","3 >= 2","TRUE && 3","FALSE || 4","6 & 3","4 | 1","2 << 3","32 >> 2","0xFFFF","FALSE","TRUE"};
  const uint16_t value[]={12,7,42,21,1,8,1,1,1,1,1,1,1,1,2,5,16,8,65535,0,1};
  for(size_t i=0;i<sizeof(value)/sizeof(value[0]);++i)expression(expr[i],value[i]);
 }else if(name=="precedence_and_grouping"){
  expression("(4 * 10) + 2",42);expression("((100 * 13) + (42 - 5))",1337);
  expression("1 + 2 * 3",7);expression("2 ^ 3 ^ 2",512);expression("(2 ^ 3) ^ 2",64);
  expression("2 + 2 == 4 && TRUE || FALSE",1);expression("8 >> 1 + 1",2);expression("2 | 1 & 0",2);
  expression("\t ( 0x2A + 0 )\t",42);expression("0 ^ 1",0);expression("1 ^ 65535",1);
 }else if(name=="variables_global_redeclaration"){
  Program p;compile(p,"VAR $n = 5\nVAR $n = ($n + 1)\n$n=($n * 7)\n");Capture c;Runtime r;CHECK(r.start(p,Capture::sink,&c));drive(r);CHECK(variable(r,"$n")==42);CHECK(c.events.empty());
  rejected("$x = 2",ErrorCode::UndefinedSymbol);rejected("VAR $_LOCK = 1",ErrorCode::Identifier);rejected("VAR $1n = 1",ErrorCode::Identifier);rejected("VAR $text = \"word\"",ErrorCode::Syntax);
  runtimeError("IF FALSE THEN\nVAR $n = 5\nEND_IF\n$n = 2",ErrorCode::Uninitialized);
  runtimeError("VAR $n = $n",ErrorCode::Uninitialized);
 }else if(name=="constants_replacement"){
  output("DEFINE #N 2\nDEFINE #WORD ready\nVAR $n = (#N ^ 3)\n$n = ($n + 1)\nSTRINGLN #WORD\nSTRINGLN #WORD!", "ready\nready!\n");
  output("DEFINE word yes\nDEFINE #A a\nDEFINE #AB b\nSTRINGLN word word! sword word\nSTRINGLN #AB#A\nSTRINGLN word\tword", "yes word! sword yes\nba\nword\tword\n");
  output("STRINGLN #L\nDEFINE #L forward", "forward\n");
  output("DEFINE #A #B\nDEFINE #B done\nSTRINGLN #A", "#B\n");
  rejected("DEFINE #A 1\nDEFINE #A 1",ErrorCode::DuplicateConstant);
  rejected("DEFINE $A 1",ErrorCode::Identifier);rejected("DEFINE #A",ErrorCode::Syntax);
  rejected("DEFINE #C STRINGLN\n#C hi",ErrorCode::UnknownStatement);
 }else if(name=="if_else_chains"){
  output("IF TRUE THEN\nSTRINGLN yes\nELSE\nSTRINGLN no\nEND_IF", "yes\n");
  output("IF FALSE THEN\nSTRINGLN no\nELSE IF FALSE THEN\nSTRINGLN no\nELSE IF TRUE THEN\nSTRINGLN middle\nELSE\nSTRINGLN no\nEND_IF", "middle\n");
  output("IF FALSE THEN\nSTRING no\nELSE IF FALSE THEN\nSTRING no\nELSE\nSTRINGLN last\nEND_IF", "last\n");
  output("IF FALSE THEN\nSTRING no\nELSE IF FALSE THEN\nSTRING no\nEND_IF\nSTRINGLN after", "after\n");
  output("IF FALSE THEN\nIF TRUE THEN\nSTRING no\nEND_IF\nELSE\nIF FALSE THEN\nSTRING no\nELSE\nSTRINGLN nested\nEND_IF\nEND_IF", "nested\n");
 }else if(name=="while_and_mixed_flow"){
  Program p;compile(p,"VAR $n = 0\nWHILE $n < 3\nVAR $m = 0\nWHILE $m < 2\nIF $m == 1 THEN\n$n = ($n + 1)\nEND_IF\n$m = ($m + 1)\nEND_WHILE\nEND_WHILE\n");Capture c;Runtime r;CHECK(r.start(p,Capture::sink,&c));drive(r);CHECK(r.state()==State::Completed);CHECK(variable(r,"$n")==3);CHECK(variable(r,"$m")==2);CHECK(c.events.empty());
  output("WHILE FALSE\nSTRING wrong\nEND_WHILE\nIF FALSE THEN\nWHILE TRUE\nSTRING wrong\nEND_WHILE\nEND_IF\nSTRINGLN zero", "zero\n");
 }else if(name=="inactive_side_effects"){
  Program p;compile(p,"VAR $n = 1\nIF FALSE THEN\n$n=99\nDELAY 40\nENTER\nSTOP_PAYLOAD\nF()\nEND_IF\nFUNCTION F()\n$n = 77\nEND_FUNCTION\n");Capture c;Runtime r;CHECK(r.start(p,Capture::sink,&c));drive(r);CHECK(r.state()==State::Completed);CHECK(variable(r,"$n")==1);CHECK(c.events.empty());
 }else if(name=="functions_and_returns"){
  Program p;compile(p,"VAR $n = 0\nF()\nF()\nFUNCTION F()\n$n = ($n + 1)\nG()\nRETURN ($n + 40)\nEND_FUNCTION\nFUNCTION G()\nIF $n == 1 THEN\nWHILE $n < 2\n$n = ($n + 1)\nEND_WHILE\nEND_IF\nEND_FUNCTION\n");Capture c;Runtime r;CHECK(r.start(p,Capture::sink,&c));drive(r);CHECK(r.state()==State::Completed);CHECK(variable(r,"$n")==3);uint16_t out=0;CHECK(r.returned(out));CHECK(out==43);CHECK(c.events.empty());
  output("FUNCTION F()\nSTRINGLN hidden\nEND_FUNCTION\nSTRINGLN main", "main\n");
  Program b;compile(b,"FUNCTION F()\nRETURN TRUE\nSTRING wrong\nEND_FUNCTION\nF()");Runtime t;Capture d;CHECK(t.start(b,Capture::sink,&d));drive(t);CHECK(t.returned(out));CHECK(out==1);CHECK(d.events.empty());
  output("FUNCTION F()\nRETURN\nSTRING wrong\nEND_FUNCTION\nF()", "");
 }else if(name=="named_key_event_order"){
  Program p;compile(p,"STRING a\nENTER\nTAB\nSPACE\nESCAPE\nBACKSPACE\nDELETE\nUPARROW\nDOWNARROW\nLEFTARROW\nRIGHTARROW\nSTRINGLN z");Capture c;Runtime r;CHECK(r.start(p,Capture::sink,&c));drive(r);const uint16_t keys[]={0x28,0x2b,0x2c,0x29,0x2a,0x4c,0x52,0x51,0x50,0x4f};CHECK(c.events.size()==13);CHECK(c.events[0].type==EventType::Character&&c.events[0].value=='a');for(size_t i=0;i<10;++i)CHECK(c.events[i+1].type==EventType::KeyTap&&c.events[i+1].value==keys[i]);CHECK(c.events[11].value=='z');CHECK(c.events[12].value==0x28);
 }else if(name=="delay_clock_and_wrap"){
  Program p;compile(p,"DELAY 20\nSTRINGLN done");Capture c;Runtime r;uint32_t start=0xfffffff0;CHECK(r.start(p,Capture::sink,&c,start));uint32_t acceptedAt=start;for(unsigned i=0;i<64&&c.events.empty();++i){acceptedAt=start+i;r.tick(acceptedAt);}CHECK(c.events.size()==1);CHECK(c.events[0].type==EventType::Delay&&c.events[0].value==20);for(uint32_t i=1;i<20;++i)r.tick(acceptedAt+i);CHECK(c.events.size()==1);drive(r,acceptedAt+20);CHECK(c.visible()=="done\n");
  Program z;compile(z,"DELAY 0\nSTRING zero");Runtime q;Capture e;CHECK(q.start(z,Capture::sink,&e));drive(q);CHECK(e.visible()=="zero");
 }else if(name=="retry_does_not_duplicate"){
  Program p;compile(p,"STRINGLN hello\nDELAY 20\nTAB");Capture c;c.retries=5;Runtime r;CHECK(r.start(p,Capture::sink,&c));drive(r);CHECK(c.visible()=="hello\n");CHECK(c.events.size()==8);CHECK(c.calls==13);CHECK(c.events[6].type==EventType::Delay);CHECK(c.events[7].value==0x2b);
 }else if(name=="cancellation_and_sink_errors"){
  Program p;compile(p,"STRINGLN long\nSTRING no");Capture c;Runtime r;CHECK(r.start(p,Capture::sink,&c));r.tick(0);r.tick(1);CHECK(c.visible()=="l");r.cancel();for(int i=2;i<50;++i)r.tick(i);CHECK(r.state()==State::Cancelled);CHECK(c.visible()=="l");
  Program wait;compile(wait,"DELAY 100\nSTRING no");Runtime w;Capture d;CHECK(w.start(wait,Capture::sink,&d));for(unsigned i=0;i<64&&d.events.empty();++i)w.tick(i);w.cancel();w.tick(1000);CHECK(w.state()==State::Cancelled);CHECK(d.events.size()==1);
  Capture failed;failed.failAfter=1;Runtime f;CHECK(f.start(p,Capture::sink,&failed));drive(f);CHECK(f.state()==State::Error);CHECK(f.error().code==ErrorCode::SinkFailure);CHECK(failed.visible()=="l");
  output("IF FALSE THEN\nSTOP_PAYLOAD\nEND_IF\nSTRINGLN ok", "ok\n");
  Runtime s;Capture e;Program stop;compile(stop,"STRING ok\nSTOP_PAYLOAD\nSTRING no");CHECK(s.start(stop,Capture::sink,&e));drive(s);CHECK(s.state()==State::Cancelled);CHECK(e.visible()=="ok");
  Capture throwing;throwing.throwInside=true;Runtime exception;CHECK(exception.start(p,Capture::sink,&throwing));drive(exception);CHECK(exception.error().code==ErrorCode::SinkFailure);CHECK(throwing.events.empty());
 }else if(name=="budgets_and_no_progress"){
  Program p;compile(p,"WHILE TRUE\nEND_WHILE");Runtime r;Capture c;CHECK(r.start(p,Capture::sink,&c,0,30));drive(r);CHECK(r.error().code==ErrorCode::StepLimit);CHECK(r.steps()==30);CHECK(c.events.empty());
  Program rec;compile(rec,"FUNCTION F()\nF()\nEND_FUNCTION\nF()");Runtime q;CHECK(q.start(rec,Capture::sink,&c));drive(q);CHECK(q.error().code==ErrorCode::CallLimit);
  Program text;compile(text,"STRING blocked");Runtime b;Capture blocked;blocked.retries=1000000;CHECK(b.start(text,Capture::sink,&blocked,0,10000,20));drive(b);CHECK(b.error().code==ErrorCode::Timeout);CHECK(blocked.events.empty());
  Runtime frozen;Capture retry;retry.retries=1000000;CHECK(frozen.start(text,Capture::sink,&retry));for(uint32_t i=0;i<=MaxTicks&&frozen.state()==State::Running;++i)frozen.tick(0);CHECK(frozen.error().code==ErrorCode::TickLimit);CHECK(retry.events.empty());
 }else if(name=="clean_sessions_and_borrowing"){
  Program p;compile(p,"VAR $x=7\nSTRING x");Runtime r;Capture c;CHECK(r.start(p,Capture::sink,&c));CHECK(!r.start(p,Capture::sink,&c));CHECK(!p.compile("",0));CHECK(p.error().code==ErrorCode::Busy);drive(r);CHECK(variable(r,"$x")==7);
  c.events.clear();CHECK(r.start(p,Capture::sink,&c));uint16_t v=0;CHECK(!r.variable("$x",v));r.cancel();CHECK(p.compile("",0));CHECK(!r.variable("$x",v));CHECK(r.start(p,Capture::sink,&c));drive(r);CHECK(c.events.empty());CHECK(!r.returned(v));
  Program borrowed;compile(borrowed,"STRING a");{Runtime owner;CHECK(owner.start(borrowed,Capture::sink,&c));Runtime second;CHECK(!second.start(borrowed,Capture::sink,&c));CHECK(second.error().code==ErrorCode::Busy);CHECK(!borrowed.compile("",0));}CHECK(borrowed.compile("",0));
 }else if(name=="reentrant_callbacks"){
  Program p;compile(p,"STRINGLN ok");Runtime r;Capture c;c.reentrant=&r;CHECK(r.start(p,Capture::sink,&c));drive(r);CHECK(r.state()==State::Completed);CHECK(c.visible()=="ok\n");
  Runtime q;Capture d;d.reentrant=&q;d.cancelInside=true;CHECK(q.start(p,Capture::sink,&d));drive(q);CHECK(q.state()==State::Cancelled);CHECK(d.visible()=="o");
 }else if(name=="malformed_structure_zero_events"){
  const char* bad[]={"IF TRUE THEN\nSTRING x","END_IF","ELSE","IF TRUE THEN\nELSE\nELSE\nEND_IF","IF TRUE THEN\nELSE\nELSE IF TRUE THEN\nEND_IF","IF TRUE\nEND_IF","IF TRUE THEN\nELSE IF FALSE\nEND_IF","WHILE TRUE\nEND_IF","END_WHILE","RETURN 2","FUNCTION F()\nEND_IF","FUNCTION F()\nFUNCTION G()\nEND_FUNCTION\nEND_FUNCTION"};
  for(const char* s:bad)rejected(std::string("STRINGLN MUST-NOT-APPEAR\n")+s);
  Program p;std::string s="STRING safe\nVAR $x = (5 + )";CHECK(!p.compile(s.data(),s.size(),"bad.duck"));CHECK(p.error().line==2);CHECK(std::string(p.location())=="bad.duck");CHECK(p.error().column>0);
 }else if(name=="arithmetic_and_syntax_failures"){
  const char* bad[]={"65536","0x10000","0x","0xG","5 +","(5 + 2","5 + 2)","~5","!TRUE","-1","+1","1 / 0","1 % 0","65535 + 1","0 - 1","256 * 256","2 ^ 16","0 ^ 0","1 << 16","1 >> 16","65535 << 1","$unknown","TRUE && (1 / 0)"};
  for(const char* expr:bad)rejected(std::string("STRING no\nVAR $x = ")+expr);
  runtimeError("VAR $d = 0\nVAR $n = (2 / $d)",ErrorCode::Arithmetic);
  runtimeError("VAR $n = 65535\n$n = ($n + 1)",ErrorCode::Arithmetic);
  runtimeError("VAR $n = 0\n$n = ($n - 1)",ErrorCode::Arithmetic);
  runtimeError("VAR $s = 16\nVAR $n = (1 << $s)",ErrorCode::Arithmetic);
 }else if(name=="unsupported_explicit_rejection"){
  const char* bad[]={"STRING","STRINGLN","STRING_BASH\ntext\nEND_STRING","HOLD SHIFT","CTRL a","ATTACKMODE HID","INJECT_VAR $n","FUNCTION F(x)\nEND_FUNCTION","F(1)","UNKNOWN","STRINGLN café"};
  for(const char* s:bad)rejected(s);rejected("F()",ErrorCode::UndefinedFunction);rejected("FUNCTION F()\nEND_FUNCTION\nFUNCTION F()\nEND_FUNCTION",ErrorCode::DuplicateFunction);
 }else if(name=="source_and_table_limits"){
  Program api;CHECK(!api.compile(nullptr,1));CHECK(api.error().code==ErrorCode::InvalidSource);CHECK(!api.compile("",0,std::string(64,'x').c_str()));CHECK(api.error().code==ErrorCode::Identifier);CHECK(api.compile("",0));Runtime invalid;Capture dummy;CHECK(!invalid.start(api,Capture::sink,&dummy,0,0));CHECK(invalid.error().code==ErrorCode::InvalidBudget);CHECK(!invalid.start(api,nullptr,nullptr));CHECK(invalid.error().code==ErrorCode::SinkFailure);
  output(std::string(MaxSource,'\n'),"");rejected(std::string(MaxSource+1,' '),ErrorCode::InputLimit);rejected(std::string(MaxLine+1,'x'),ErrorCode::LineLimit);
  output("STRING "+std::string(MaxLine-7,'x'),std::string(MaxLine-7,'x'));
  std::string source;for(size_t i=0;i<MaxSymbols;++i)source+="VAR $n"+std::to_string(i)+"=1\n";Program p;compile(p,source);rejected(source+"VAR $overflow=1\n",ErrorCode::SymbolLimit);
  source.clear();for(size_t i=0;i<MaxFunctions;++i)source+="FUNCTION F"+std::to_string(i)+"()\nEND_FUNCTION\n";compile(p,source);rejected(source+"FUNCTION Overflow()\nEND_FUNCTION\n",ErrorCode::FunctionLimit);
  source.clear();for(size_t i=0;i<MaxConstants;++i)source+="DEFINE #N"+std::to_string(i)+" 1\n";compile(p,source);rejected(source+"DEFINE #OVER 1\n",ErrorCode::ConstantLimit);
  source.clear();for(size_t i=0;i<MaxCode;++i)source+="ENTER\n";compile(p,source);rejected(source+"ENTER\n",ErrorCode::CodeLimit);
  source="DEFINE #LONG "+std::string(63,'x')+"\nSTRING #LONG#LONG#LONG#LONG#LONG\n";rejected(source,ErrorCode::ConstantExpansion);
  std::string exactPool;for(int i=0;i<16;++i)exactPool+="STRING "+std::string(249,'x')+"\n";exactPool+="STRING "+std::string(95,'x')+"\n";compile(p,exactPool);rejected(exactPool+"ENTER",ErrorCode::TextLimit);
  expression(std::string("1"),1);rejected("VAR $"+std::string(23,'n')+"=1",ErrorCode::Identifier);
  source.clear();for(int i=0;i<20;++i)source+="STRING "+std::string(240,'x')+"\n";rejected(source,ErrorCode::TextLimit);
 }else if(name=="nesting_and_expression_boundaries"){
  std::string open,close;for(size_t i=0;i<MaxNesting;++i){open+="IF TRUE THEN\n";close+="END_IF\n";}output(open+"STRING ok\n"+close,"ok");rejected("IF TRUE THEN\n"+open+close+"END_IF\n",ErrorCode::NestingLimit);
  expression(std::string(MaxExprDepth-1,'(')+"1"+std::string(MaxExprDepth-1,')'),1);rejected("VAR $n = "+std::string(MaxExprDepth,'(')+"1"+std::string(MaxExprDepth,')'),ErrorCode::ExpressionLimit);
  std::string expr="1";for(int i=0;i<31;++i)expr+="+1";expression(expr,32);rejected("VAR $n = "+expr+"+1",ErrorCode::ExpressionLimit);
  std::string f;for(size_t i=0;i<MaxCalls;++i){f+="FUNCTION F"+std::to_string(i)+"()\n";if(i+1<MaxCalls)f+="F"+std::to_string(i+1)+"()\n";f+="END_FUNCTION\n";}output(f+"F0()","");
 }else if(name=="deterministic_source_mutations"){
  uint32_t seed=0x271b;auto random=[&](){seed=seed*1664525u+1013904223u;return seed;};
  const char* seeds[]={"VAR $n=1\nSTRINGLN safe", "IF TRUE THEN\nSTRING a\nEND_IF", "WHILE FALSE\nENTER\nEND_WHILE", "FUNCTION F()\nRETURN 1\nEND_FUNCTION\nF()"};
  for(unsigned i=0;i<500;++i){std::string text=seeds[random()%4];unsigned edits=1+random()%4;while(edits--){size_t pos=random()%(text.size()+1);if(random()%2&&pos<text.size())text.erase(pos,1);else text.insert(pos,1,static_cast<char>(random()%128));}
   Program p;bool ok=p.compile(text.data(),text.size());CHECK(ok==p.ready());Capture c;Runtime r;
   if(ok){CHECK(r.start(p,Capture::sink,&c,0,100,1000));drive(r,0,1100);CHECK(r.state()!=State::Running);}else{CHECK(!r.start(p,Capture::sink,&c));CHECK(c.events.empty());}
  }
 }else if(name=="no_core_heap_allocations"){
  Program p;std::string src="DEFINE #N 3\nVAR $n=0\nWHILE $n < #N\n$n=($n+1)\nEND_WHILE\nF()\nFUNCTION F()\nRETURN ($n ^ 2)\nEND_FUNCTION";Runtime r;auto sink=[](void*,const Event&){return Accept::Accepted;};
  allocationProbe=true;allocations=0;bool compiled=p.compile(src.data(),src.size());bool started=r.start(p,sink,nullptr);for(unsigned i=0;i<200&&r.state()==State::Running;++i)r.tick(i);size_t total=allocations;allocationProbe=false;
  CHECK(compiled&&started);CHECK(r.state()==State::Completed);uint16_t value=0;CHECK(r.returned(value)&&value==9);CHECK(total==0);
 }else throw std::runtime_error("Unknown case");
}
int main(int argc,char** argv){try{if(argc!=2)return 2;run(argv[1]);std::cout<<"PASS "<<argv[1]<<" ("<<assertions<<" assertions)\n";return 0;}catch(const std::exception& e){allocationProbe=false;std::cerr<<e.what()<<"\n";return 1;}}
