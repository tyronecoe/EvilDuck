#define main stage27b_main
#include "../stage27b/test_core.cpp"
#undef main
// Reuse only the mock/assertion helpers. Cases below execute the changed production preview.
void callRun(const std::string& name){
 if(name=="required_fixture"){
  std::ifstream input(std::string(PREVIEW_CALL_FIXTURES)+"/expression-calls.duck");CHECK(input.good());std::string source((std::istreambuf_iterator<char>(input)),{});output(source,"math-ok\n");
 }else if(name=="assignment_forward_nested_arithmetic"){
  Program p;compile(p,"VAR $result = ((F() + 1) * 3)\n$result = (G() + $result)\nFUNCTION F()\nRETURN 6\nEND_FUNCTION\nFUNCTION G()\nRETURN (F() ^ 2)\nEND_FUNCTION");Capture c;Runtime r;CHECK(r.start(p,Capture::sink,&c));drive(r);CHECK(r.state()==State::Completed);CHECK(variable(r,"$result")==57);CHECK(c.events.empty());
 }else if(name=="return_of_call_and_boolean"){
  Program p;compile(p,"VAR $v = OUTER()\nIF BOOL() THEN\nSTRINGLN true\nEND_IF\nFUNCTION OUTER()\nRETURN INNER() + 1\nEND_FUNCTION\nFUNCTION INNER()\nRETURN 40\nEND_FUNCTION\nFUNCTION BOOL()\nRETURN ((OUTER() == 41) && TRUE)\nEND_FUNCTION");Capture c;Runtime r;CHECK(r.start(p,Capture::sink,&c));drive(r);CHECK(r.state()==State::Completed);CHECK(variable(r,"$v")==41);CHECK(c.visible()=="true\n");
 }else if(name=="if_else_if_selected_calls_only"){
  output("IF TRUE THEN\nSTRING first\nELSE IF NO() THEN\nSTRING wrong\nEND_IF\nIF NO() THEN\nSTRING wrong\nELSE IF YES() THEN\nSTRING second\nELSE\nSTRING wrong\nEND_IF\nFUNCTION NO()\nSTRING N\nRETURN FALSE\nEND_FUNCTION\nFUNCTION YES()\nSTRING Y\nRETURN TRUE\nEND_FUNCTION", "firstNYsecond");
 }else if(name=="while_reevaluation_zero_iteration"){
  Program p;compile(p,"VAR $n=0\nWHILE CHECK()\n$n=($n+1)\nEND_WHILE\nWHILE NEVER()\nSTRING wrong\nEND_WHILE\nFUNCTION CHECK()\nSTRING c\nRETURN ($n < 3)\nEND_FUNCTION\nFUNCTION NEVER()\nRETURN FALSE\nEND_FUNCTION");Capture c;Runtime r;CHECK(r.start(p,Capture::sink,&c));drive(r);CHECK(r.state()==State::Completed);CHECK(variable(r,"$n")==3);CHECK(c.visible()=="cccc");
 }else if(name=="left_to_right_capture_eager_power"){
  Program p;compile(p,"VAR $n=1\nVAR $capture=($n + BUMP() + $n)\nVAR $order=(A() + B())\nVAR $eager=(FALSE && A())\nVAR $power=(A() ^ B() ^ C())\nFUNCTION BUMP()\n$n=2\nSTRING X\nRETURN 4\nEND_FUNCTION\nFUNCTION A()\nSTRING A\nRETURN 2\nEND_FUNCTION\nFUNCTION B()\nSTRING B\nRETURN 3\nEND_FUNCTION\nFUNCTION C()\nSTRING C\nRETURN 2\nEND_FUNCTION");Capture c;Runtime r;CHECK(r.start(p,Capture::sink,&c));drive(r);CHECK(r.state()==State::Completed);CHECK(variable(r,"$capture")==7);CHECK(variable(r,"$order")==5);CHECK(variable(r,"$eager")==0);CHECK(variable(r,"$power")==512);CHECK(c.visible()=="XABAABC");
 }else if(name=="delay_call_single_timing_owner"){
  Program p;compile(p,"DELAY WAIT_VALUE() + 5\nSTRING done\nFUNCTION WAIT_VALUE()\nSTRING start\nRETURN 15\nEND_FUNCTION");Capture c;c.retries=4;Runtime r;uint32_t now=0xffffffe0;CHECK(r.start(p,Capture::sink,&c,now));unsigned i=0;for(;i<200;++i){r.tick(now+i);if(c.events.size()==6&&c.events.back().type==EventType::Delay)break;}CHECK(i<200);CHECK(c.visible()=="start");CHECK(c.events.back().value==20);uint32_t acceptedAt=now+i;
  for(unsigned wait=1;wait<20;++wait)r.tick(acceptedAt+wait);CHECK(c.visible()=="start");drive(r,acceptedAt+20);CHECK(r.state()==State::Completed);CHECK(c.visible()=="startdone");unsigned delays=0;for(auto e:c.events)delays+=e.type==EventType::Delay;CHECK(delays==1);CHECK(c.calls==c.events.size()+4);
 }else if(name=="static_void_unknown_arity_zero_output"){
  const char* invalid[]={"VAR $x=F()\nFUNCTION F()\nRETURN\nEND_FUNCTION","VAR $x=F()\nFUNCTION F()\nEND_FUNCTION","VAR $x=F()\nFUNCTION F()\nRETURN\nRETURN 9\nEND_FUNCTION","VAR $x=F()\nFUNCTION F()\nIF FALSE THEN\nRETURN 1\nEND_IF\nEND_FUNCTION","VAR $x=MISSING()","FUNCTION F()\nRETURN 1\nEND_FUNCTION\nVAR $x=F(1)","FUNCTION F()\nRETURN 1\nEND_FUNCTION\nVAR $x=F( )","VAR $x=F(\nFUNCTION F()\nRETURN 1\nEND_FUNCTION"};
  for(const char* source:invalid)rejected(std::string("STRING MUST-NOT-APPEAR\n")+source);
  rejected("VAR $x=F()\nFUNCTION F()\nRETURN\nEND_FUNCTION",ErrorCode::VoidValue);
  rejected("VAR $x=MISSING()",ErrorCode::UndefinedFunction);
 }else if(name=="runtime_void_no_stale_return"){
  const char* source="VAR $flag=TRUE\nVAR $first=F()\n$flag=FALSE\nVAR $second=5 + F()\nFUNCTION F()\nIF $flag THEN\nRETURN 9\nELSE\nRETURN\nEND_IF\nEND_FUNCTION";
  Program p;compile(p,source);Capture c;Runtime r;CHECK(r.start(p,Capture::sink,&c));drive(r);CHECK(r.state()==State::Error);CHECK(r.error().code==ErrorCode::VoidValue);CHECK(r.error().line==4);CHECK(r.error().column==5);CHECK(variable(r,"$first")==9);uint16_t out=0;CHECK(!r.variable("$second",out));CHECK(!r.returned(out));CHECK(c.events.empty());
  runtimeError("VAR $flag=FALSE\nVAR $x=F()\nFUNCTION F()\nIF $flag THEN\nRETURN 3\nEND_IF\nEND_FUNCTION",ErrorCode::VoidValue);
 }else if(name=="depth_limit_cycles_and_frames"){
  auto chain=[](unsigned levels){std::string s="VAR $result=F0()\n";for(unsigned i=0;i<levels;++i){s+="FUNCTION F"+std::to_string(i)+"()\nRETURN ";s+=i+1<levels?"F"+std::to_string(i+1)+"() + 1":"1";s+="\nEND_FUNCTION\n";}return s;};
  Program p;compile(p,chain(MaxCalls));Capture c;Runtime r;CHECK(r.start(p,Capture::sink,&c));drive(r);CHECK(r.state()==State::Completed);CHECK(variable(r,"$result")==MaxCalls);
  runtimeError(chain(MaxCalls+1),ErrorCode::CallLimit);
  runtimeError("VAR $x=F()\nFUNCTION F()\nRETURN F()\nEND_FUNCTION",ErrorCode::CallLimit);
  runtimeError("VAR $x=F()\nFUNCTION F()\nRETURN G()\nEND_FUNCTION\nFUNCTION G()\nRETURN F()\nEND_FUNCTION",ErrorCode::CallLimit);
  Program rec;compile(rec,"VAR $n=3\nVAR $x=F()\nFUNCTION F()\nIF $n == 0 THEN\nRETURN 0\nEND_IF\n$n=($n-1)\nRETURN F() + 1\nEND_FUNCTION");Runtime q;Capture d;CHECK(q.start(rec,Capture::sink,&d));drive(q);CHECK(q.state()==State::Completed);CHECK(variable(q,"$x")==3);
 }else if(name=="arithmetic_results_and_source_mapping"){
  runtimeError("VAR $x=F() + 1\nFUNCTION F()\nRETURN 65535\nEND_FUNCTION",ErrorCode::Arithmetic);
  runtimeError("VAR $x=2 / F()\nFUNCTION F()\nRETURN 0\nEND_FUNCTION",ErrorCode::Arithmetic);
  runtimeError("VAR $x=1 << F()\nFUNCTION F()\nRETURN 16\nEND_FUNCTION",ErrorCode::Arithmetic);
  runtimeError("VAR $x=F() ^ 2\nFUNCTION F()\nRETURN 256\nEND_FUNCTION",ErrorCode::Arithmetic);
  Program p;compile(p,"VAR $x=4 / F()\nFUNCTION F()\nRETURN 0\nEND_FUNCTION");Capture c;Runtime r;CHECK(r.start(p,Capture::sink,&c));drive(r);CHECK(r.error().line==1);CHECK(r.error().column==3);CHECK(c.events.empty());
 }else if(name=="cancellation_stop_suspended_and_restart"){
  Program p;compile(p,"VAR $x=F()+1\nSTRING wrong\nFUNCTION F()\nSTRING abc\nRETURN 9\nEND_FUNCTION");Capture c;Runtime r;CHECK(r.start(p,Capture::sink,&c));for(unsigned i=0;i<100&&c.events.empty();++i)r.tick(i);CHECK(c.visible()=="a");CHECK(!p.compile("",0));r.cancel();for(unsigned i=100;i<120;++i)r.tick(i);CHECK(r.state()==State::Cancelled);CHECK(c.visible()=="a");uint16_t v=0;CHECK(!r.variable("$x",v));CHECK(!r.returned(v));CHECK(p.compile("",0));c.events.clear();CHECK(r.start(p,Capture::sink,&c));drive(r);CHECK(r.state()==State::Completed);CHECK(c.events.empty());
  Program stop;compile(stop,"VAR $flag=TRUE\nVAR $x=F()\nSTRING wrong\nFUNCTION F()\nIF $flag THEN\nSTOP_PAYLOAD\nEND_IF\nRETURN 2\nEND_FUNCTION");Runtime s;Capture d;CHECK(s.start(stop,Capture::sink,&d));drive(s);CHECK(s.state()==State::Cancelled);CHECK(d.events.empty());CHECK(!s.variable("$x",v));
 }else if(name=="retry_failure_timeout_and_budget_during_call"){
  Program p;compile(p,"VAR $x=F()+F()\nFUNCTION F()\nSTRING ok\nRETURN 1\nEND_FUNCTION");Capture c;c.retries=8;Runtime r;CHECK(r.start(p,Capture::sink,&c));drive(r);CHECK(r.state()==State::Completed);CHECK(variable(r,"$x")==2);CHECK(c.visible()=="okok");CHECK(c.calls==12);
  Runtime bad;Capture f;f.failAfter=1;CHECK(bad.start(p,Capture::sink,&f));drive(bad);CHECK(bad.error().code==ErrorCode::SinkFailure);CHECK(f.visible()=="o");uint16_t out=0;CHECK(!bad.variable("$x",out));CHECK(!bad.returned(out));
  Runtime timeout;Capture retry;retry.retries=1000000;CHECK(timeout.start(p,Capture::sink,&retry,0,10000,50));drive(timeout);CHECK(timeout.error().code==ErrorCode::Timeout);CHECK(retry.events.empty());
  Program loop;compile(loop,"VAR $flag=TRUE\nVAR $x=F()\nFUNCTION F()\nWHILE $flag\nEND_WHILE\nRETURN 1\nEND_FUNCTION");Runtime looping;Capture quiet;CHECK(looping.start(loop,Capture::sink,&quiet,0,200));drive(looping);CHECK(looping.error().code==ErrorCode::StepLimit);CHECK(looping.steps()==200);CHECK(quiet.events.empty());
 }else if(name=="bounded_work_cooperative_and_reentrant"){
  Program p;compile(p,"VAR $x=F()+G()\nFUNCTION F()\nSTRING a\nRETURN 1\nEND_FUNCTION\nFUNCTION G()\nSTRING b\nRETURN 2\nEND_FUNCTION");Capture c;Runtime r;c.reentrant=&r;CHECK(r.start(p,Capture::sink,&c));size_t before=0;for(unsigned i=0;i<1000&&r.state()==State::Running;++i){before=c.events.size();r.tick(i);CHECK(c.events.size()<=before+1);}CHECK(r.state()==State::Completed);CHECK(c.visible()=="ab");CHECK(variable(r,"$x")==3);
 }else if(name=="expression_function_token_limits"){
  std::string prefix="FUNCTION F()\nRETURN 1\nEND_FUNCTION\nVAR $n = ";
  std::string expression="F()";for(int i=0;i<15;++i)expression+="+F()";Program p;compile(p,prefix+expression);Capture c;Runtime r;CHECK(r.start(p,Capture::sink,&c));drive(r);CHECK(r.state()==State::Completed);CHECK(variable(r,"$n")==16);rejected(prefix+expression+"+F()",ErrorCode::ExpressionLimit);
  std::string deep(MaxExprDepth-1,'(');deep+="F()";deep+=std::string(MaxExprDepth-1,')');compile(p,prefix+deep);rejected(prefix+"("+deep+")",ErrorCode::ExpressionLimit);
 }else if(name=="operators_with_function_operands"){
  const char* expr[]={"F()+G()","F()-G()","F()*G()","F()/G()","F()%G()","G()^G()","F()==G()","F()!=G()","F()<G()","F()>G()","F()<=G()","F()>=G()","F()&&G()","F()||G()","F()&G()","F()|G()","G()<<G()","F()>>G()"};
  const uint16_t expected[]={10,6,16,4,0,4,0,1,0,1,0,1,1,1,0,10,8,2};
  for(size_t i=0;i<18;++i){Program p;compile(p,std::string("VAR $x=")+expr[i]+"\nFUNCTION F()\nRETURN 8\nEND_FUNCTION\nFUNCTION G()\nRETURN 2\nEND_FUNCTION");Capture c;Runtime r;CHECK(r.start(p,Capture::sink,&c));drive(r);CHECK(r.state()==State::Completed);CHECK(variable(r,"$x")==expected[i]);CHECK(c.events.empty());}
 }else if(name=="standalone_inside_value_call_no_leak"){
  Program p;compile(p,"VAR $x=OUTER()+OUTER()\nFUNCTION OUTER()\nVOID()\nRETURN 1+INNER()\nEND_FUNCTION\nFUNCTION INNER()\nRETURN 2\nEND_FUNCTION\nFUNCTION VOID()\nSTRING v\nRETURN\nEND_FUNCTION");Capture c;Runtime r;CHECK(r.start(p,Capture::sink,&c));drive(r);CHECK(r.state()==State::Completed);CHECK(variable(r,"$x")==6);CHECK(c.visible()=="vv");
 }else if(name=="cancel_called_delay_and_restart_same_program"){
  Program p;compile(p,"VAR $x=F()\nFUNCTION F()\nDELAY 20\nRETURN 7\nEND_FUNCTION");Runtime r;Capture c;CHECK(r.start(p,Capture::sink,&c));for(unsigned i=0;i<100&&c.events.empty();++i)r.tick(i);CHECK(c.events.size()==1);CHECK(c.events[0].type==EventType::Delay);r.cancel();r.tick(1000);CHECK(r.state()==State::Cancelled);CHECK(c.events.size()==1);uint16_t v=0;CHECK(!r.variable("$x",v));c.events.clear();CHECK(r.start(p,Capture::sink,&c));drive(r);CHECK(r.state()==State::Completed);CHECK(variable(r,"$x")==7);CHECK(c.events.size()==1);
  Runtime frozen;Capture d;CHECK(frozen.start(p,Capture::sink,&d));for(uint32_t i=0;i<=MaxTicks&&frozen.state()==State::Running;++i)frozen.tick(0);CHECK(frozen.error().code==ErrorCode::TickLimit);CHECK(d.events.size()==1);
 }else if(name=="static_invalid_inactive_and_void_control_flow"){
  rejected("STRING before\nIF FALSE THEN\nVAR $x=VOID()\nEND_IF\nFUNCTION VOID()\nRETURN\nEND_FUNCTION",ErrorCode::VoidValue);
  rejected("VAR $x=F()\nFUNCTION F()\nWHILE TRUE\nEND_WHILE\nRETURN 1\nEND_FUNCTION",ErrorCode::VoidValue);
  rejected("VAR $x=F()\nFUNCTION F()\nIF TRUE THEN\nRETURN\nELSE\nRETURN 1\nEND_IF\nEND_FUNCTION",ErrorCode::VoidValue);
 }else if(name=="define_call_and_mixed_function_control"){
  Program p;compile(p,"DEFINE #CALL F()\nVAR $n=0\nVAR $result=(#CALL+1)\nFUNCTION F()\nWHILE $n<2\nIF $n==0 THEN\n$n=($n+1)\nELSE\nRETURN G()\nEND_IF\nEND_WHILE\nRETURN 0\nEND_FUNCTION\nFUNCTION G()\nRETURN 4\nEND_FUNCTION");Capture c;Runtime r;CHECK(r.start(p,Capture::sink,&c));drive(r);CHECK(r.state()==State::Completed);CHECK(variable(r,"$result")==5);CHECK(variable(r,"$n")==1);CHECK(c.events.empty());
 }else if(name=="suspended_clock_timeout_and_sink_exception"){
  Program p;compile(p,"VAR $x=F()\nFUNCTION F()\nDELAY 100\nRETURN 2\nEND_FUNCTION");Runtime r;Capture c;CHECK(r.start(p,Capture::sink,&c,0,10000,30));drive(r);CHECK(r.error().code==ErrorCode::Timeout);CHECK(c.events.size()==1);uint16_t v=0;CHECK(!r.variable("$x",v));
  Program text;compile(text,"VAR $x=F()\nFUNCTION F()\nSTRING safe\nRETURN 2\nEND_FUNCTION");Runtime q;Capture throwing;throwing.throwInside=true;CHECK(q.start(text,Capture::sink,&throwing));drive(q);CHECK(q.error().code==ErrorCode::SinkFailure);CHECK(throwing.events.empty());CHECK(!q.variable("$x",v));
 }else if(name=="static_truth_facts_preserve_eager_calls"){
  rejected("STRING before\nVAR $x=F()\nFUNCTION F()\nIF FALSE && G() THEN\nRETURN 1\nEND_IF\nEND_FUNCTION\nFUNCTION G()\nRETURN 2\nEND_FUNCTION",ErrorCode::VoidValue);
  rejected("VAR $x=F()\nFUNCTION F()\nIF TRUE || G() THEN\nRETURN\nELSE\nRETURN 1\nEND_IF\nEND_FUNCTION\nFUNCTION G()\nRETURN 2\nEND_FUNCTION",ErrorCode::VoidValue);
  output("IF TRUE || G() THEN\nSTRING ok\nEND_IF\nFUNCTION G()\nSTRING g\nRETURN FALSE\nEND_FUNCTION", "gok");
 }else if(name=="no_heap_multiple_continuations"){
  Program p;std::string source="VAR $n=F()+G()\nFUNCTION F()\nRETURN G()+1\nEND_FUNCTION\nFUNCTION G()\nRETURN 2\nEND_FUNCTION";Runtime r;auto sink=[](void*,const Event&){return Accept::Accepted;};allocationProbe=true;allocations=0;bool ok=p.compile(source.data(),source.size());bool start=r.start(p,sink,nullptr);for(unsigned i=0;i<300&&r.state()==State::Running;++i)r.tick(i);size_t count=allocations;allocationProbe=false;CHECK(ok&&start);CHECK(r.state()==State::Completed);CHECK(variable(r,"$n")==5);CHECK(count==0);
 }else throw std::runtime_error("Unknown expression-call case");
}
int main(int argc,char** argv){try{if(argc!=2)return 2;callRun(argv[1]);std::cout<<"PASS "<<argv[1]<<" ("<<assertions<<" assertions)\n";return 0;}catch(const std::exception& e){allocationProbe=false;std::cerr<<e.what()<<"\n";return 1;}}
