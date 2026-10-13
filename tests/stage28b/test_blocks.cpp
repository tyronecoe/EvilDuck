#define main stage27b_main
#include "../stage27b/test_core.cpp"
#undef main
struct BlockSink {
 std::vector<Event> events;unsigned calls=0,retries=0;bool retryEnter=false,failEnter=false,throwEnter=false;
 Runtime* runtime=nullptr;const Program* program=nullptr;bool reenter=false,cancelEvent=false;
 static Accept sink(void* ptr,const Event& e){auto& s=*static_cast<BlockSink*>(ptr);++s.calls;
  if(s.reenter){s.runtime->tick(0);CHECK(!s.runtime->start(*s.program,sink,ptr));}
  if(s.cancelEvent){s.runtime->cancel();return Accept::Retry;}
  if(s.retries){--s.retries;return Accept::Retry;}
  if(e.type==EventType::KeyTap){if(s.throwEnter)throw std::runtime_error("mock Enter fault");if(s.failEnter)return Accept::Failed;if(s.retryEnter){s.retryEnter=false;return Accept::Retry;}}
  s.events.push_back(e);return Accept::Accepted;
 }
 std::string visible()const{std::string out;for(auto e:events)out+=e.type==EventType::Character?static_cast<char>(e.value):'\n';return out;}
};
std::string block(const std::string& body,bool enter=false){return std::string(enter?"STRINGLN\n":"STRING\n")+body+(enter?"END_STRINGLN":"END_STRING");}
void atError(const std::string& s,ErrorCode code,uint16_t line,uint16_t column=1){Program p;CHECK(!p.compile(s.data(),s.size(),"body.duck"));CHECK(p.error().code==code);CHECK(p.error().line==line);CHECK(p.error().column==column);CHECK(std::string(p.location())=="body.duck");Capture c;Runtime r;CHECK(!r.start(p,Capture::sink,&c));r.tick(0);CHECK(c.events.empty());}
void blockRun(const std::string& name){
 if(name=="official_fixture_files"){
  for(auto stem:{"string","stringln"}){std::ifstream file(std::string(PREVIEW_BLOCK_FIXTURES)+"/"+stem+".duck");CHECK(file.good());std::string source((std::istreambuf_iterator<char>(file)),{});output(source,std::string(stem)=="string"?"abc":"a\nb\nc\n");}
 }else if(name=="inline_commands_unchanged"){
  output("STRING a\nSTRINGLN b\n  STRINGLN   c  \nSTRING d", "ab\n  c\nd");output("STRINGLN $n\nSTRING #unknown", "$n\n#unknown");
 }else if(name=="empty_blank_adjacent"){
  output(block("")+"\n"+block("",true),"");output(block("\n\t \n"),"");output(block("\n\t \n",true),"\n \n");
  output(block("a\n")+"\n"+block("b\n",true)+"\n"+block("c\n"),"ab\nc");
 }else if(name=="whitespace_preservation"){
  output(block(" \t a \t\n\t\tb  \n"),"a \tb  ");
  output(block("\ta \t\n\t\tb  \n  c\t \n \td\n",true),"a \t\n\tb  \n  c\t \n \td\n");
  output(" \tSTRINGLN \t\n\tx\n \tEND_STRINGLN \t","x\n");
 }else if(name=="source_endings_bom_eof"){
  output("\xef\xbb\xbfSTRINGLN\r\n\ta\r\n\r\n\tb\r\nEND_STRINGLN", "a\n\nb\n");
  output("STRING\r\n a\n b\r\nEND_STRING\r\n", "ab");
  atError("STRING\nabc\rEND_STRING",ErrorCode::InvalidSource,2);
  atError(std::string("STRING\na\0b\nEND_STRING",21),ErrorCode::InvalidSource,2);
  atError("STRING\n\xc3\xa4\nEND_STRING",ErrorCode::InvalidSource,2);
 }else if(name=="raw_commands_not_declarations"){
  output(block("REM comment\nREM_BLOCK\nEND_REM\nDEFINE #A 1\nVAR $n = 1\nFUNCTION F()\nEND_FUNCTION\nIF invalid THEN\nEND_IF\nWHILE x\nEND_WHILE\nRETURN\nSTOP_PAYLOAD\n",true),"REM comment\nREM_BLOCK\nEND_REM\nDEFINE #A 1\nVAR $n = 1\nFUNCTION F()\nEND_FUNCTION\nIF invalid THEN\nEND_IF\nWHILE x\nEND_WHILE\nRETURN\nSTOP_PAYLOAD\n");
  rejected(block("VAR $x = 1\n")+"\nVAR $y=$x",ErrorCode::UndefinedSymbol);
  rejected(block("FUNCTION G()\nRETURN 1\nEND_FUNCTION\n")+"\nG()",ErrorCode::UndefinedFunction);
  output(block("DEFINE #A hidden\n#A\n"),"DEFINE #A hidden#A");
 }else if(name=="terminator_lookalikes_literal"){
  output(block("foo END_STRING bar\nEND_STRING_EXTRA\nEND_STRINGLN_EXTRA\nSTRING text\nSTRINGLN text\n",true),"foo END_STRING bar\nEND_STRING_EXTRA\nEND_STRINGLN_EXTRA\nSTRING text\nSTRINGLN text\n");
  output("REM_BLOCK\nSTRING\nEND_STRINGLN\nEND_REM\n"+block("ok\n"),"ok");
 }else if(name=="malformed_structure_zero_events"){
  atError("STRING before\nSTRING\nx",ErrorCode::Structure,2);
  atError("STRING before\nSTRINGLN\nx",ErrorCode::Structure,2);
  atError("STRING\nx\nEND_STRING\nEND_STRING",ErrorCode::Structure,4);
  atError("STRING before\nSTRINGLN\nx\nEND_STRING",ErrorCode::Structure,4);
  atError("STRING before\n  END_STRINGLN",ErrorCode::Structure,2,3);
  atError("STRING\nx\n END_STRING extra",ErrorCode::Structure,3,2);
  atError("STRINGLN\nx\nEND_STRINGLN extra",ErrorCode::Structure,3);
  atError("STRING\nSTRINGLN\nEND_STRING",ErrorCode::Structure,2);
  atError("STRINGLN\nSTRING\nEND_STRINGLN",ErrorCode::Structure,2);
  rejected("IF FALSE THEN\nSTRING\nx\nEND_IF",ErrorCode::Structure);
 }else if(name=="forward_constants_boundaries_literal_hash"){
  output(block("#WORD! # WORD WORD! SWORD WORD\n\tWORD\tWORD\n",true)+"\nDEFINE #WORD yes\nDEFINE WORD ok", "yes! # ok WORD! SWORD ok\nWORD\tWORD\n");
  output("DEFINE #A #B\nDEFINE #B expanded\n"+block("#A\n"),"#B");
  output("DEFINE #C END_STRING\n"+block("#C\n"),"END_STRING");
  output(block("#A\nDEFINE #B raw\n",true)+"\nDEFINE #A done", "done\nDEFINE #B raw\n");
 }else if(name=="if_else_selection_and_inactive"){
  output("IF FALSE THEN\n"+block("bad\n",true)+"\nELSE IF TRUE THEN\n"+block("yes\n",true)+"\nELSE IF F() THEN\n"+block("bad2\n")+"\nELSE\n"+block("bad3\n")+"\nEND_IF\nFUNCTION F()\n"+block("badcall\n")+"\nRETURN 1\nEND_FUNCTION", "yes\n");
  output("IF TRUE THEN\nIF FALSE THEN\n"+block("bad\n")+"\nELSE\n"+block("inner\n")+"\nEND_IF\nELSE\n"+block("bad2\n")+"\nEND_IF", "inner");
 }else if(name=="while_zero_one_many"){
  for(unsigned n:{0u,1u,4u}){std::string source="VAR $n=0\nWHILE $n < "+std::to_string(n)+"\n"+block(" a\n b\n",true)+"\n$n=$n+1\nEND_WHILE";std::string expected;for(unsigned i=0;i<n;++i)expected+=" a\n b\n";output(source,expected);}
 }else if(name=="forward_nested_expression_function_blocks"){
  Program p;compile(p,"VAR $n=F()+G()\nFUNCTION F()\n"+block("f\n",true)+"\nRETURN G()+1\nEND_FUNCTION\nFUNCTION G()\n"+block("g\n")+"\nRETURN 2\nEND_FUNCTION");Capture c;Runtime r;CHECK(r.start(p,Capture::sink,&c));drive(r);CHECK(r.state()==State::Completed);CHECK(c.visible()=="f\ngg");CHECK(variable(r,"$n")==5);
  output("F()\nF()\nFUNCTION F()\n"+block("one\n",true)+"\nRETURN\nEND_FUNCTION", "one\none\n");
  output("VAR $n=0\nVAR $result=F()+1\nFUNCTION F()\nWHILE $n<2\nIF $n==0 THEN\n"+block("a\n")+"\nELSE\n"+block("b\n")+"\nEND_IF\n$n=$n+1\nEND_WHILE\nRETURN 2\nEND_FUNCTION", "ab");
  output("VAR $n=0\nWHILE C()\nSTRING body\n$n=$n+1\nEND_WHILE\nFUNCTION C()\n"+block("c\n")+"\nRETURN $n<2\nEND_FUNCTION", "cbodycbodyc");
 }else if(name=="source_line_arena_code_exact_limits"){
  output(block(std::string(256,'x')+"\n"),std::string(256,'x'));atError(block(std::string(257,'x')+"\n"),ErrorCode::LineLimit,2);
  std::string source=block("x\n");source+='\n';source.append(MaxSource-source.size(),'\n');output(source,"x");rejected(source+"\n",ErrorCode::InputLimit);
  std::string body;for(unsigned i=0;i<15;++i)body+=std::string(256,'x')+"\n";body+=std::string(192,'y')+"\n";output(block(body),std::string(3840,'x')+std::string(192,'y'));rejected(block(body+"\n"),ErrorCode::TextLimit);
  std::string code;for(unsigned i=0;i<128;++i)code+=block("")+"\n";Program p;compile(p,code);CHECK(p.instructions()==128);rejected(code+block(""),ErrorCode::CodeLimit);
 }else if(name=="constant_expansion_exact_overflow_locations"){
  std::string prefix="DEFINE #A "+std::string(63,'a')+"\n";
  output(prefix+block("#A#A#A#Axxxx\n"),std::string(252,'a')+"xxxx");
  atError(prefix+block("#A#A#A#Axxxxx\n"),ErrorCode::ConstantExpansion,3);
  std::string body;for(unsigned i=0;i<15;++i)body+="#A#A#A#Axxxx\n";body+=std::string(192,'y')+"\n";Program p;compile(p,prefix+block(body));rejected(prefix+block(body+"\n"),ErrorCode::TextLimit);
 }else if(name=="compact_instruction_and_blank_metadata_limits"){
  Program p;compile(p,block(std::string(1024,'\n'),true));CHECK(p.instructions()==1);Capture c;Runtime r;CHECK(r.start(p,Capture::sink,&c));drive(r);CHECK(c.events.size()==1024);CHECK(r.steps()==1);
  rejected(block(std::string(1025,'\n')),ErrorCode::TextLimit);
 }else if(name=="retry_character_and_enter_exactly_once"){
  Program p;compile(p,block("ab\nc\n",true));Runtime r;BlockSink c;c.retries=3;c.retryEnter=true;CHECK(r.start(p,BlockSink::sink,&c));drive(r);CHECK(r.state()==State::Completed);CHECK(c.visible()=="ab\nc\n");CHECK(c.calls==9);
 }else if(name=="cancellation_at_every_output_boundary"){
  for(unsigned stop=0;stop<=5;++stop){Program p;compile(p,block("ab\nc\n",true)+"\nSTRING after");Capture c;Runtime r;CHECK(r.start(p,Capture::sink,&c));for(unsigned i=0;i<100&&c.events.size()<stop;++i)r.tick(i);CHECK(c.events.size()==stop);r.cancel();unsigned before=c.calls;for(unsigned i=0;i<20;++i)r.tick(i);CHECK(r.state()==State::Cancelled);CHECK(c.calls==before);Capture clean;CHECK(r.start(p,Capture::sink,&clean));drive(r);CHECK(clean.visible()=="ab\nc\nafter");}
 }else if(name=="stop_after_block_and_inactive_stop"){
  output(block("done\n",true)+"\nIF FALSE THEN\nSTOP_PAYLOAD\nEND_IF\nSTRING yes", "done\nyes");
  Program p;compile(p,block("done\n",true)+"\nSTOP_PAYLOAD\nSTRING no");Capture c;Runtime r;CHECK(r.start(p,Capture::sink,&c));drive(r);CHECK(r.state()==State::Cancelled);CHECK(c.visible()=="done\n");
 }else if(name=="sink_failure_exception_body_locations"){
  for(bool throws:{false,true}){Program p;compile(p,block("a\nb\n",true));Runtime r;BlockSink c;c.failEnter=!throws;c.throwEnter=throws;CHECK(r.start(p,BlockSink::sink,&c));drive(r);CHECK(r.error().code==ErrorCode::SinkFailure);CHECK(r.error().line==2);CHECK(c.visible()=="a");unsigned calls=c.calls;r.tick(0);CHECK(c.calls==calls);Capture clean;CHECK(r.start(p,Capture::sink,&clean));drive(r);CHECK(clean.visible()=="a\nb\n");}
  Program p;compile(p,block("a\nb\n"));Capture c;c.failAfter=1;Runtime r;CHECK(r.start(p,Capture::sink,&c));drive(r);CHECK(r.error().line==3);CHECK(c.visible()=="a");
 }else if(name=="reentrant_and_cancel_inside_callback"){
  Program p;compile(p,block("a\n",true));BlockSink c;Runtime r;c.runtime=&r;c.program=&p;c.reenter=true;CHECK(r.start(p,BlockSink::sink,&c));drive(r);CHECK(c.visible()=="a\n");CHECK(c.calls==2);
  c.events.clear();c.cancelEvent=true;CHECK(r.start(p,BlockSink::sink,&c));drive(r);CHECK(r.state()==State::Cancelled);CHECK(c.events.empty());
 }else if(name=="borrow_simultaneous_restart_revision"){
  Program p;std::string s=block("a\n",true);compile(p,s);Capture c,d;Runtime a,b;CHECK(a.start(p,Capture::sink,&c));a.tick(0);CHECK(!p.compile(s.data(),s.size()));CHECK(p.error().code==ErrorCode::Busy);CHECK(!b.start(p,Capture::sink,&d));CHECK(b.error().code==ErrorCode::Busy);drive(a);CHECK(c.visible()=="a\n");CHECK(b.start(p,Capture::sink,&d));drive(b);CHECK(d.visible()=="a\n");compile(p,block("b\n"));Capture e;CHECK(a.start(p,Capture::sink,&e));drive(a);CHECK(e.visible()=="b");
 }else if(name=="clock_wrap_stuck_tick_timeout_steps"){
  Program p;compile(p,block("ab\n",true));Capture c;Runtime r;CHECK(r.start(p,Capture::sink,&c,0xfffffffcu));drive(r,0xfffffffcu);CHECK(c.visible()=="ab\n");
  Capture retry;retry.retries=200000;CHECK(r.start(p,Capture::sink,&retry));for(unsigned i=0;i<=MaxTicks+1&&r.state()==State::Running;++i)r.tick(0);CHECK(r.error().code==ErrorCode::TickLimit);CHECK(retry.events.empty());CHECK(r.error().line==2);
  CHECK(r.start(p,Capture::sink,&retry,0,MaxSteps,3));r.tick(0);r.tick(1);r.tick(3);CHECK(r.error().code==ErrorCode::Timeout);CHECK(r.error().line==2);
  Program timed;compile(timed,"WHILE TRUE\n"+block("x\n")+"\nEND_WHILE");Capture tc;Runtime tr;CHECK(tr.start(timed,Capture::sink,&tc,0,MaxSteps,30));drive(tr);CHECK(tr.error().code==ErrorCode::Timeout);
  Program loop;compile(loop,"WHILE TRUE\n"+block("x\n")+"\nEND_WHILE");Capture lc;Runtime lr;CHECK(lr.start(loop,Capture::sink,&lc,0,10));drive(lr);CHECK(lr.error().code==ErrorCode::StepLimit);
 }else if(name=="one_attempt_per_tick_large_loop_text"){
  Program p;std::string body;for(unsigned i=0;i<8;++i)body+=std::string(200,'a')+"\n";compile(p,"VAR $n=0\nWHILE $n<2\n"+block(body,true)+"\n$n=$n+1\nEND_WHILE");Capture c;Runtime r;CHECK(r.start(p,Capture::sink,&c));for(unsigned i=0;i<10000&&r.state()==State::Running;++i){unsigned calls=c.calls;r.tick(i);CHECK(c.calls-calls<=1);}CHECK(r.state()==State::Completed);CHECK(c.events.size()==3216);CHECK(variable(r,"$n")==2);
 }else if(name=="nested_structure_and_call_boundaries"){
  std::string s;for(unsigned i=0;i<16;++i)s+="IF TRUE THEN\n";s+=block("x\n");for(unsigned i=0;i<16;++i)s+="\nEND_IF";output(s,"x");rejected("IF TRUE THEN\n"+s+"\nEND_IF",ErrorCode::NestingLimit);
  for(unsigned count:{8u,9u}){std::string chain="F0()\n";for(unsigned i=0;i<count;++i){chain+="FUNCTION F"+std::to_string(i)+"()\n"+block("x\n")+"\n";if(i+1<count)chain+="F"+std::to_string(i+1)+"()\n";chain+="RETURN\nEND_FUNCTION\n";}if(count==8)output(chain,std::string(8,'x'));else runtimeError(chain,ErrorCode::CallLimit);}
 }else if(name=="bounded_seeded_block_mutations"){
  uint32_t seed=0x28b;const std::string good="VAR $x=F()\nFUNCTION F()\n"+block("\tREM #x\nEND_STRING_EXTRA\n",true)+"\nRETURN 2\nEND_FUNCTION";
  for(unsigned n=0;n<400;++n){seed=seed*1664525u+1013904223u;std::string s=good;s[seed%s.size()]=static_cast<char>(32+(seed>>16)%95);Program p;bool ok=p.compile(s.data(),s.size());Runtime r;Capture c;if(ok){CHECK(r.start(p,Capture::sink,&c,0,100));drive(r,0,20000);CHECK(r.state()!=State::Running);}else{CHECK(!r.start(p,Capture::sink,&c));CHECK(c.events.empty());}}
 }else if(name=="no_heap_block_and_suspended_expressions"){
  Program p;Runtime r;std::string source="VAR $n=F()+F()\nFUNCTION F()\n"+block(" x\n\t y\n",true)+"\nRETURN 2\nEND_FUNCTION";
  auto sink=[](void*,const Event&){return Accept::Accepted;};allocationProbe=true;allocations=0;bool ok=p.compile(source.data(),source.size());bool start=r.start(p,sink,nullptr);for(unsigned i=0;i<200&&r.state()==State::Running;++i)r.tick(i);size_t count=allocations;allocationProbe=false;CHECK(ok&&start);CHECK(r.state()==State::Completed);CHECK(variable(r,"$n")==4);CHECK(count==0);
 }else throw std::runtime_error("Unknown block test");
}
int main(int argc,char** argv){try{if(argc!=2)return 2;blockRun(argv[1]);std::cout<<"PASS "<<argv[1]<<" ("<<assertions<<" assertions)\n";return 0;}catch(const std::exception& e){allocationProbe=false;std::cerr<<e.what()<<"\n";return 1;}}
