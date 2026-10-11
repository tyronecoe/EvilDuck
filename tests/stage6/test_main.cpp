#include "host.h"
#include "FS.h"
#include "com.h"
#include "duckscript.h"
#include "duck_vars.h"
#include "script_source.h"
#include "script_parser.h"
#include "control_flow.h"
#include "keyboard_locale.h"
#include "attackmode.h"
#include "cli.h"
#include "script_functions.h"
#include "duck_expr.h"
#include <iostream>
#include <stdexcept>
#include <string>
#include <algorithm>

static unsigned assertions=0;
// Record direct numeric reads while the run is alive. Stage 1 intentionally
// clears variables on EOF/error/STOP; never alter that behavior for a test.
static std::map<std::string,uint16_t> finalLiveValues;
static void observeVariables() {
  for(const char *name:{"$n","$o","$i","$j","$sum","$count","$v","$a","$b","$limit"}) {
    uint16_t value; if(duck_vars::getNumeric(name,value))finalLiveValues[name]=value;
  }
}
static void drain(unsigned limit=20000) {
  while((duckscript::running() || com::busy()) && limit--) {
    observeVariables();mock::tick();observeVariables();
  }
  if(duckscript::running() || com::busy())throw std::runtime_error("bounded drain exceeded");
}
static void require(bool condition,const char *message) {
  ++assertions; if(!condition) throw std::runtime_error(message);
}
static void clean() {
  require(!duckscript::running() && !com::busy(),"execution must finish or cancel");
  require(!mock::blockingDelays,"no blocking delays");
  require(mock::heldKeys.empty() && !mock::heldModifiers,"runtime keys must release");
}
static void start(const std::string &script,const char *file="stage6.txt") {
  mock::reset();finalLiveValues.clear();mock::file(file,script.c_str());require(duckscript::run(file),"start cooperative fixture");
}
static void visible(const std::string &script,const char *expected,const char *file="stage6.txt",unsigned ticks=20000) {
  start(script,file);drain(ticks);
  if(duckscript::lastError().length()) std::cerr<<duckscript::lastError().c_str()<<'\n';
  require(!duckscript::lastError().length(),"valid script must have no error");
  if(mock::text!=expected)std::cerr<<"Actual output: "<<mock::text.c_str()<<" Expected: "<<expected<<'\n';
  require(mock::text==expected,"exact harmless output");clean();
}
static void invalid(const std::string &script,const char *diagnostic,unsigned line) {
  start(script,"sd:bad-stage6.txt");drain();auto error=duckscript::lastError();
  if(error.indexOf(diagnostic)<0)std::cerr<<"Actual diagnostic: "<<error.c_str()<<'\n';
  require(error.indexOf(diagnostic)>=0,"useful preflight error");
  require(error.indexOf("sd:bad-stage6.txt: Error at line "+String(line)+":")>=0,"source/line error location");
  require(mock::presses.empty() && !mock::text.length(),"zero HID before structural rejection");clean();
}
static void pending(const std::string &script,unsigned line) {
  start(script);
  for(unsigned i=0;i<2000 && !(duckscript::currentLine()==line && com::busy());++i)mock::tick();
  require(duckscript::running() && duckscript::currentLine()==line && com::busy(),"reach pending loop command");
}
static void cancel() {
  auto count=mock::text.length();duckscript::stop();for(unsigned i=0;i<200;++i)mock::tick(1000);
  require(mock::text.length()==count,"no queued loop or tail output after cancel");clean();
}
static void runtimeError(const std::string &script,const char *diagnostic,const char *expected="",unsigned ticks=20000) {
  start(script);drain(ticks);
  if(duckscript::lastError().indexOf(diagnostic)<0)std::cerr<<"Error: "<<duckscript::lastError().c_str()<<'\n';
  require(duckscript::lastError().indexOf(diagnostic)>=0,"runtime error must match");require(mock::text==expected,"exact output before runtime failure");clean();
}
static const char *fixture="DEFINE #COUNT 2\nFUNCTION COUNTDOWN()\nWHILE $n>0\nSTRINGLN n=$n\n$n=$n-1\nEND_WHILE\nRETURN TRUE\nEND_FUNCTION\nVAR $n=#COUNT\nIF COUNTDOWN()==TRUE THEN\nSTRINGLN done\nEND_IF\nVAR $n=1\nCOUNTDOWN()\nSTRINGLN after\n";
static void test(const String &name) {
  if(name=="stage6_declarations_skipped")visible("FUNCTION hello()\nSTRINGLN hidden\nEND_FUNCTION\nSTRINGLN after\n","after\n");
  else if(name=="stage6_statement_invocation")visible("FUNCTION hello()\nSTRINGLN hello\nEND_FUNCTION\nhello()\nSTRINGLN after\n","hello\nafter\n");
  else if(name=="stage6_multiple_calls")visible("FUNCTION hello()\nSTRING x\nEND_FUNCTION\nhello()\nhello()\nhello()\n","xxx");
  else if(name=="stage6_forward_invocation_and_globals")visible("VAR $n=2\ncountdown()\nSTRINGLN after\nFUNCTION countdown()\nWHILE $n>0\nSTRING $n\n$n=$n-1\nEND_WHILE\nEND_FUNCTION\n","21after\n");
  else if(name=="stage6_fixture_spiffs_and_sd") {visible(fixture,"n=2\nn=1\ndone\nn=1\nafter\n");visible(fixture,"n=2\nn=1\ndone\nn=1\nafter\n","sd:stage6.txt");}
  else if(name=="stage6_explicit_void_return")visible("FUNCTION hello()\nSTRING x\nRETURN\nSTRING hidden\nEND_FUNCTION\nhello()\nSTRING after\n","xafter");
  else if(name=="stage6_implicit_void_return")visible("FUNCTION hello()\nEND_FUNCTION\nhello()\nSTRINGLN after\n","after\n");
  else if(name=="stage6_integer_return_assignment")visible("FUNCTION number()\nRETURN (2^3)+1\nEND_FUNCTION\nVAR $n=number()\nSTRINGLN n=$n\n","n=9\n");
  else if(name=="stage6_boolean_return_conditions")visible("FUNCTION yes()\nRETURN TRUE\nEND_FUNCTION\nFUNCTION nope()\nRETURN FALSE\nEND_FUNCTION\nIF yes() THEN\nSTRING y\nEND_IF\nIF nope() THEN\nSTRING hidden\nELSE\nSTRING n\nEND_IF\n","yn");
  else if(name=="stage6_statement_discards_return_value")visible("FUNCTION number()\nRETURN 65535\nEND_FUNCTION\nnumber()\nSTRINGLN after\n","after\n");
  else if(name=="stage6_void_value_rejected") {runtimeError("FUNCTION empty()\nEND_FUNCTION\nVAR $n=empty()\nSTRING hidden\n","without a value");runtimeError("FUNCTION empty()\nRETURN\nEND_FUNCTION\nIF empty() THEN\nSTRING hidden\nEND_IF\n","without a value");}
  else if(name=="stage6_top_level_and_live_return_compatibility") {visible("RETURN\nFUNCTION hello()\nRETURN\nEND_FUNCTION\nhello()\nRETURN\n","\n\n");require(com::executeNow("RETURN"),"live bare RETURN accepted");drain();require(mock::text=="\n\n\n","live RETURN still Enter");clean();}
  else if(name=="stage6_enter_and_modifier_return_inside_function") {visible("FUNCTION hello()\nENTER\nCTRL RETURN\nRETURN\nEND_FUNCTION\nhello()\n","\n");require(mock::presses.size()==2 && mock::presses[1].modifiers==1 && mock::presses[1].key==0x28,"Ctrl RETURN remains key chord");}
  else if(name=="stage6_return_unwinds_nested_control")visible("FUNCTION select()\nWHILE TRUE\nIF TRUE THEN\nRETURN 5\nEND_IF\nEND_WHILE\nSTRING hidden\nEND_FUNCTION\nVAR $n=select()\nIF $n==5 THEN\nSTRINGLN good\nEND_IF\n","good\n");
  else if(name=="stage6_caller_control_restored")visible("FUNCTION value()\nIF TRUE THEN\nRETURN 1\nEND_IF\nEND_FUNCTION\nVAR $n=0\nWHILE $n<2\nIF TRUE THEN\n$n=$n+value()\nELSE\nSTRING hidden\nEND_IF\nEND_WHILE\nSTRINGLN $n\n","2\n");
  else if(name=="stage6_nested_statement_calls")visible("FUNCTION inner()\nSTRING i\nEND_FUNCTION\nFUNCTION outer()\nSTRING o\ninner()\nSTRING t\nEND_FUNCTION\nouter()\n","oit");
  else if(name=="stage6_nested_return_expressions")visible("FUNCTION inner()\nRETURN 3\nEND_FUNCTION\nFUNCTION outer()\nRETURN inner()^2\nEND_FUNCTION\nVAR $n=outer()+inner()\nSTRINGLN $n\n","12\n");
  else if(name=="stage6_multiple_calls_in_expression")visible("FUNCTION next()\n$n=$n+1\nRETURN $n\nEND_FUNCTION\nVAR $n=0\nVAR $v=next()+next()*next()\nSTRINGLN n=$n v=$v\n","n=3 v=7\n");
  else if(name=="stage6_earlier_variable_operand_preserved")visible("FUNCTION change()\n$n=10\nRETURN 2\nEND_FUNCTION\nVAR $n=1\nVAR $v=$n+change()+$n\nSTRINGLN n=$n v=$v\n","n=10 v=13\n");
  else if(name=="stage6_eager_logical_calls")visible("FUNCTION next()\n$n=$n+1\nRETURN TRUE\nEND_FUNCTION\nVAR $n=0\nIF FALSE && next() THEN\nSTRING hidden\nEND_IF\nIF TRUE || next() THEN\nSTRING $n\nEND_IF\n","2");
  else if(name=="stage6_inactive_conditions_do_not_call")visible("FUNCTION bad()\nSTRING hidden\nRETURN TRUE\nEND_FUNCTION\nIF FALSE THEN\nIF bad() THEN\nSTOP\nEND_IF\nEND_IF\nIF TRUE THEN\nSTRING good\nELSE IF bad() THEN\nSTRING hidden\nEND_IF\nWHILE FALSE\nbad()\nEND_WHILE\n","good");
  else if(name=="stage6_while_condition_calls_reevaluate")visible("FUNCTION test()\nRETURN $n<3\nEND_FUNCTION\nVAR $n=0\nWHILE test()\n$n=$n+1\nSTRING $n\nEND_WHILE\nSTRINGLN done\n","123done\n");
  else if(name=="stage6_while_condition_changes_count_as_progress")visible("FUNCTION next_test()\n$n=$n-1\nRETURN $n>0\nEND_FUNCTION\nVAR $n=1100\nWHILE next_test()\nREM empty body\nEND_WHILE\nSTRINGLN $n\n","0\n");
  else if(name=="stage6_else_if_function_condition")visible("FUNCTION yes()\nSTRING side\nRETURN TRUE\nEND_FUNCTION\nIF FALSE THEN\nSTRING hidden\nELSE IF yes() THEN\nSTRINGLN selected\nELSE\nSTRING hidden\nEND_IF\n","sideselected\n");
  else if(name=="stage6_numeric_commands_with_calls") {visible("FUNCTION count()\nRETURN 2\nEND_FUNCTION\nDEFAULT_DELAY count()\nDEFAULTDELAY count()\nDELAY count()*3\nWAIT count()\nSTRING x\nREPEAT count()\nREPLAY count()\n","xxxxx");require(mock::now>=8,"function delay arguments scheduled");}
  else if(name=="stage6_function_globals_text_and_file_commands")visible("FUNCTION hello()\nSAVE value.txt STRING saved\nREAD value.txt $word\nVAR $n=7\nEND_FUNCTION\nhello()\nSTRINGLN $word $n\nIF $word == saved\nSTRINGLN global\nEND_IF\n","saved 7\nglobal\n");
  else if(name=="stage6_define_function_operands_and_names")visible("DEFINE #V 5\nDEFINE hello damaged\nDEFINE FUNCTION damaged\nDEFINE END_FUNCTION damaged\nDEFINE RETURN damaged\nFUNCTION hello()\nRETURN #V\nEND_FUNCTION\nVAR $n=hello()\nSTRINGLN $n\n","5\n");
  else if(name=="stage6_macro_structural_creation_rejected") {for(const char *line:{"FUNCTION hello()","END_FUNCTION","RETURN 1","hello()"})invalid("DEFINE #CONTROL "+std::string(line)+"\nSTRING hidden\n#CONTROL\n","cannot create",3);}
  else if(name=="stage6_rem_and_text_modes") {visible("REM_BLOCK\nFUNCTION fake()\nRETURN 1\nEND_FUNCTION\nEND_REM\nFUNCTION hello()\nREM_BLOCK\nEND_FUNCTION\nEND_IF\nEND_REM\nSTRINGLN good\nEND_FUNCTION\nhello()\n","good\n");invalid("STRING\nFUNCTION fake()\nEND_FUNCTION\nRETURN\nEND_STRING\n","deferred to Stage 7",1);}
  else if(name=="stage6_literal_text_does_not_invoke")visible("FUNCTION hello()\nSTRING hidden\nEND_FUNCTION\nSTRINGLN hello()\nSAVE value.txt STRING hello()\nREAD value.txt $word\nSTRINGLN $word\n","hello()\nhello()\n");
  else if(name=="stage6_names_case_sensitive") {visible("FUNCTION foo()\nRETURN 1\nEND_FUNCTION\nFUNCTION Foo()\nRETURN 2\nEND_FUNCTION\nVAR $n=foo()+Foo()\nSTRINGLN $n\n","3\n");invalid("FUNCTION foo()\nEND_FUNCTION\nFOO()\n","Undefined function",3);}
  else if(name=="stage6_malformed_names_parameters_and_collisions") {for(const char *declaration:{"FUNCTION","FUNCTION foo","FUNCTION 1foo()","FUNCTION foo($n)","FUNCTION foo(1)","FUNCTION foo ()","FUNCTION foo( )","FUNCTION foo() extra","FUNCTION STRING()","FUNCTION RETURN()","FUNCTION CTRL()","FUNCTION TRUE()","FUNCTION foo-bar()"})invalid("STRING hidden\n"+std::string(declaration)+"\n","",2);}
  else if(name=="stage6_unknown_calls_zero_hid") {invalid("STRING hidden\nmissing()\n","Undefined function",2);invalid("STRING hidden\nVAR $n=missing()\n","Undefined function",2);invalid("IF FALSE THEN\nmissing()\nEND_IF\n","Undefined function",2);}
  else if(name=="stage6_invalid_call_arguments_and_whitespace") {for(const char *call:{"hello(1)","hello($n)","hello ()","hello( )","hello() extra"})invalid("FUNCTION hello()\nEND_FUNCTION\nSTRING hidden\n"+std::string(call)+"\n","",4);}
  else if(name=="stage6_duplicate_and_nested_declarations") {invalid("FUNCTION hello()\nEND_FUNCTION\nFUNCTION hello()\nEND_FUNCTION\n","Duplicate",3);invalid("FUNCTION outer()\nFUNCTION inner()\nEND_FUNCTION\nEND_FUNCTION\n","Nested",2);invalid("IF TRUE THEN\nFUNCTION hello()\nEND_FUNCTION\nEND_IF\n","top level",2);}
  else if(name=="stage6_unterminated_and_unmatched_functions") {invalid("STRING hidden\nFUNCTION hello()\nSTRING hidden\n","Unterminated FUNCTION",2);invalid("STRING hidden\nEND_FUNCTION\n","Unmatched",2);invalid("FUNCTION hello()\nIF TRUE THEN\nEND_FUNCTION\nEND_IF\n","Mismatched",3);invalid("FUNCTION hello()\nEND_FUNCTION extra\n","takes no arguments",2);}
  else if(name=="stage6_return_syntax_and_context_errors") {invalid("STRING hidden\nRETURN 1\n","requires a function",2);invalid("FUNCTION hello()\nRETURN (5+)\nEND_FUNCTION\n","Expression",2);invalid("FUNCTION hello()\nRETURN \"text\"\nEND_FUNCTION\n","Expression",2);}
  else if(name=="stage6_unused_body_preflight_errors_zero_hid") {invalid("STRING hidden\nFUNCTION unused()\nVAR $n=(1+)\nEND_FUNCTION\n","Expression",3);invalid("FUNCTION unused()\nRETURN $missing\nEND_FUNCTION\nSTRING hidden\n","Undefined",2);invalid("FUNCTION unused()\nRETURN 1/0\nEND_FUNCTION\n","zero",2);}
  else if(name=="stage6_function_table_boundary") {std::string s;for(unsigned i=0;i<DUCKSCRIPT_MAX_FUNCTIONS;++i)s+="FUNCTION func"+std::to_string(i)+"()\nEND_FUNCTION\n";visible(s+"func15()\nSTRINGLN good\n","good\n");invalid("STRING hidden\n"+s+"FUNCTION too_many()\nEND_FUNCTION\n","table exhausted",34);}
  else if(name=="stage6_function_identifier_boundary") {std::string n(DUCKSCRIPT_MAX_IDENTIFIER_LEN,'a');visible("FUNCTION "+n+"()\nSTRINGLN good\nEND_FUNCTION\n"+n+"()\n","good\n");invalid("FUNCTION "+n+"a()\nEND_FUNCTION\n","Invalid function",1);}
  else if(name=="stage6_nested_call_depth_boundary") {std::string s;for(unsigned i=0;i<DUCKSCRIPT_MAX_CALL_DEPTH;++i)s+="FUNCTION func"+std::to_string(i)+"()\n"+(i+1<DUCKSCRIPT_MAX_CALL_DEPTH?"func"+std::to_string(i+1)+"()\n":"STRINGLN good\n")+"END_FUNCTION\n";visible(s+"func0()\n","good\n");}
  else if(name=="stage6_recursive_depth_exhaustion")runtimeError("FUNCTION recursive()\nrecursive()\nEND_FUNCTION\nrecursive()\nSTRING hidden\n","call depth/stack limit");
  else if(name=="stage6_recursive_expression_and_global_visibility")visible("FUNCTION sum()\nIF $n==0 THEN\nRETURN 0\nEND_IF\n$n=$n-1\nRETURN ($n+1)+sum()\nEND_FUNCTION\nVAR $n=5\nVAR $v=sum()\nSTRINGLN n=$n v=$v\n","n=0 v=15\n");
  else if(name=="stage6_shared_control_depth_exhaustion") {std::string s="FUNCTION recurse()\nIF TRUE THEN\nIF TRUE THEN\nrecurse()\nEND_IF\nEND_IF\nEND_FUNCTION\nrecurse()\n";runtimeError(s,"nesting limit");}
  else if(name=="stage6_runtime_undefined_initialization")runtimeError("FUNCTION read_global()\nRETURN $n\nEND_FUNCTION\nread_global()\nVAR $n=1\nSTRING hidden\n","Undefined numeric variable");
  else if(name=="stage6_runtime_arithmetic_after_calls") {runtimeError("FUNCTION zero()\nRETURN 0\nEND_FUNCTION\nVAR $n=1/zero()\nSTRING hidden\n","zero");runtimeError("FUNCTION width()\nRETURN 16\nEND_FUNCTION\nIF 1<<width() THEN\nSTRING hidden\nEND_IF\n","Shift count");}
  else if(name=="stage6_repeat_history_around_calls")visible("FUNCTION hello()\nSTRING x\nEND_FUNCTION\nhello()\nREPEAT 2\nFUNCTION empty()\nEND_FUNCTION\nempty()\nREPLAY 1\n","xxxx");
  else if(name=="stage6_stop_active_and_inactive_function_branches") {visible("FUNCTION hello()\nSTRING x\nSTOP\nRETURN 1\nEND_FUNCTION\nVAR $n=hello()\nSTRING hidden\n","x");visible("FUNCTION hello()\nIF FALSE THEN\nSTOP\nRETURN 9\nEND_IF\nRETURN 1\nEND_FUNCTION\nVAR $n=hello()\nSTRINGLN $n\n","1\n");}
  else if(name=="stage6_cancel_pending_function_delay") {pending("FUNCTION hello()\nDELAY 60000\nSTRING hidden\nEND_FUNCTION\nhello()\n",2);cancel();}
  else if(name=="stage6_cancel_nested_function_text") {pending("FUNCTION inner()\nSTRING "+std::string(200,'x')+"\nEND_FUNCTION\nFUNCTION outer()\ninner()\nEND_FUNCTION\nouter()\nSTRING hidden\n",2);for(unsigned i=0;i<30;++i)mock::tick();require(mock::text.length()>0 && mock::text.length()<200,"incremental text");cancel();}
  else if(name=="stage6_cancel_held_keys_in_call") {pending("FUNCTION hello()\nCTRL ALT a\nEND_FUNCTION\nhello()\n",2);for(unsigned i=0;i<20 && mock::heldKeys.empty();++i)mock::tick();require(!mock::heldKeys.empty(),"held report inside call");cancel();}
  else if(name=="stage6_cancel_call_under_usb_backpressure") {
    pending("FUNCTION hello()\nCTRL ALT a\nEND_FUNCTION\nhello()\nSTRING hidden\n",2);
    for(unsigned i=0;i<20 && mock::heldKeys.empty();++i)mock::tick();require(!mock::heldKeys.empty(),"held call report");
    mock::usbReady=false;duckscript::stop();require(!duckscript::running(),"cancel call immediately while USB busy");
    mock::usbReady=true;for(unsigned i=0;i<20;++i)mock::tick();require(mock::text.length()==0,"tail and pending caller cancelled");clean();
  }
  else if(name=="stage6_cancel_expression_then_clean_run") {pending("FUNCTION delay_value()\nDELAY 60000\nRETURN 1\nEND_FUNCTION\nVAR $n=delay_value()+delay_value()\n",2);cancel();visible("FUNCTION hello()\nRETURN 3\nEND_FUNCTION\nVAR $n=hello()\nSTRINGLN $n\n","3\n");}
  else if(name=="stage6_live_ownership_and_stop") {pending("FUNCTION hello()\nDELAY 60000\nEND_FUNCTION\nhello()\n",2);require(!com::executeNow("VAR $n=3"),"reject interfering live assignment");cli::parse("send STRING hidden",mock::print,false);cli::parse("stop",mock::print,false);clean();require(mock::text.length()==0,"live STOP cancels pending call");}
  else if(name=="stage6_seek_error_entering_function") {start("FUNCTION hello()\nSTRING hidden\nEND_FUNCTION\nhello()\n");mock::failSeekAt=std::string("FUNCTION hello()\n").size();drain();require(duckscript::lastError().indexOf("seek error")>=0 && mock::presses.empty(),"entry seek fault stops safely");clean();}
  else if(name=="stage6_seek_error_returning_to_caller") {pending("FUNCTION hello()\nSTRING x\nEND_FUNCTION\nhello()\nSTRING hidden\n",2);mock::failSeekAt=std::string("FUNCTION hello()\nSTRING x\nEND_FUNCTION\nhello()\n").size();drain();require(duckscript::lastError().indexOf("seek error")>=0 && mock::text=="x","return seek failure stops tail");clean();}
  else if(name=="stage6_read_error_and_source_change_in_function") {pending("FUNCTION hello()\nSTRING x\nRETURN 1\nEND_FUNCTION\nVAR $n=hello()\nSTRING hidden\n",2);mock::sourceSizeIncrease=1;drain();require(duckscript::lastError().indexOf("changed or unavailable")>=0 && mock::text=="x","changed body source stops");clean();}
  else if(name=="stage6_runtime_body_read_failure") {
    pending("FUNCTION hello()\nSTRING x\nREM "+std::string(120,'x')+"\nRETURN 1\nEND_FUNCTION\nVAR $n=hello()\nSTRING hidden\n",2);
    mock::failReadAt=std::string("FUNCTION hello()\n").size()+64;drain();
    require(duckscript::lastError().indexOf("read error before EOF")>=0 && duckscript::lastError().indexOf("in hello()")>=0,"body read error has function trace");require(mock::text=="x","no tail after body read failure");clean();
  }
  else if(name=="stage6_bom_crlf_header_and_final_newline")visible("\xEF\xBB\xBF" "FUNCTION hello()\r\nRETURN 4\r\nEND_FUNCTION\r\nVAR $n=hello()+hello()\r\nSTRINGLN $n","8\n","sd:stage6.txt");
  else if(name=="stage6_empty_function_loop_stalls")runtimeError("FUNCTION empty()\nEND_FUNCTION\nWHILE TRUE\nempty()\nEND_WHILE\nSTRING hidden\n","WHILE stalled");
  else if(name=="stage6_total_call_budget") {std::string s="FUNCTION empty()\nEND_FUNCTION\nVAR $n=0\nWHILE TRUE\n$n=$n+1\n";for(unsigned i=0;i<101;++i)s+="empty()\n";s+="END_WHILE\nSTRING hidden\n";runtimeError(s,"invocation budget","",2000000);}
  else if(name=="stage6_postfix_arithmetic_matches_existing_evaluator") {
    for(const char *expr:{"2+3*4","2^3^2","0-1","65535+1","0xFF&0x0F","(3|4)<<2","6/2%2","TRUE&&FALSE||TRUE","2<3","4>=4","5!=6","(5+3)>>1","(2^3)==8"}) {
      duck_expr::Program p;duck_expr::Error e;uint16_t a=0,b=0;require(duck_expr::evaluate(expr,strlen(expr),a,e),"baseline evaluator valid");require(p.compile(expr,strlen(expr),e),"same grammar emits postfix");auto result=p.step(b,e,duck_vars::resolve,nullptr,1);while(result==duck_expr::Step::Yield)result=p.step(b,e,duck_vars::resolve,nullptr,1);require(result==duck_expr::Step::Done && a==b,"identical operator implementation results");
    }
  } else if(name=="stage6_expression_bounds_and_postfix_errors") {
    invalid("FUNCTION hello()\nRETURN "+std::string(257,'1')+"\nEND_FUNCTION\n","byte limit",2);
    duck_expr::Program p;duck_expr::Error e;uint16_t value;
    require(!p.returned(1),"no return without pending function opcode");require(p.step(value,e,nullptr,nullptr)==duck_expr::Step::Error,"empty program rejects invalid result state");require(!p.compile("(1+)",4,e),"malformed compile fails");require(p.step(value,e,nullptr,nullptr)==duck_expr::Step::Error,"failed compile cannot execute partial postfix");
  } else if(name=="stage6_long_declaration_skip_is_cooperative") {std::string s="FUNCTION unused()\n";for(unsigned i=0;i<3000;++i)s+="REM body\n";s+="END_FUNCTION\nSTRINGLN good\n";start(s);for(unsigned i=0;i<20;++i)mock::tick();require(duckscript::running() && mock::presses.empty(),"inventory/preflight yield on large body");duckscript::stop();clean();visible(s,"good\n");}
  else throw std::runtime_error("unknown test name");
}
int main(int argc,char **argv) {
  if(argc!=2)return 2;
  try {mock::reset();test(argv[1]);std::cout<<"PASS "<<argv[1]<<" ("<<assertions<<" assertions)\n";return 0;}
  catch(const std::exception &e){std::cerr<<"FAIL "<<argv[1]<<": "<<e.what()<<'\n';return 1;}
}
