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
#include "duck_constants.h"
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
static void start(const std::string &script,const char *file="stage7.txt") {
  mock::reset();finalLiveValues.clear();mock::file(file,script.c_str());require(duckscript::run(file),"start cooperative fixture");
}
static void visible(const std::string &script,const char *expected,const char *file="stage7.txt",unsigned ticks=20000) {
  start(script,file);drain(ticks);
  if(duckscript::lastError().length()) std::cerr<<duckscript::lastError().c_str()<<'\n';
  require(!duckscript::lastError().length(),"valid script must have no error");
  if(mock::text!=expected)std::cerr<<"Actual output: "<<mock::text.c_str()<<" Expected: "<<expected<<'\n';
  require(mock::text==expected,"exact harmless output");clean();
}
static void invalid(const std::string &script,const char *diagnostic,unsigned line) {
  start(script,"sd:bad-stage7.txt");drain();auto error=duckscript::lastError();
  if(error.indexOf(diagnostic)<0)std::cerr<<"Actual diagnostic: "<<error.c_str()<<'\n';
  require(error.indexOf(diagnostic)>=0,"useful preflight error");
  require(error.indexOf("sd:bad-stage7.txt: Error at line "+String(line)+":")>=0,"source/line error location");
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
static const char *fixture =
  "DEFINE #WORD ready\nFUNCTION print()\nSTRINGLN\n\t#WORD n=$n\n\tIF literal THEN\nEND_STRINGLN\nRETURN TRUE\nEND_FUNCTION\n"
  "VAR $n=2\nWHILE $n>0\nIF print() THEN\nSTRING\n  joined-\n\t$n\nEND_STRING\nENTER\nEND_IF\n$n=$n-1\nEND_WHILE\n";

static void test(const String &name) {
  if(name=="stage7_empty_blocks")visible("STRING\nEND_STRING\nSTRINGLN\nEND_STRINGLN\nSTRINGLN after\n","after\n");
  else if(name=="stage7_single_line_string")visible("STRING\n  one\nEND_STRING\nSTRING two\n","onetwo");
  else if(name=="stage7_single_line_stringln")visible("STRINGLN\n\tone\nEND_STRINGLN\nSTRINGLN two\n","one\ntwo\n");
  else if(name=="stage7_string_multiline_no_separators")visible("STRING\n a\n\tb\n c\nEND_STRING\n","abc");
  else if(name=="stage7_stringln_multiline_enters") {visible("STRINGLN\na\nb\nc\nEND_STRINGLN\n","a\nb\nc\n");require(std::count_if(mock::presses.begin(),mock::presses.end(),[](auto p){return p.key==0x28;})==3,"one Enter per body line");}
  else if(name=="stage7_string_blank_lines")visible("STRING\n\n  \n\t\n a\n\nEND_STRING\n","a");
  else if(name=="stage7_stringln_blank_lines")visible("STRINGLN\n\n\t\n  \nx\n\nEND_STRINGLN\n","\n\n  \nx\n\n");
  else if(name=="stage7_string_leading_and_trailing_whitespace")visible("STRING\n \t  a  \t\n\t\t b \nEND_STRING\n","a  \tb ");
  else if(name=="stage7_stringln_removes_one_leading_tab")visible("STRINGLN\n\t\t a \t\n \t b  \n    c\nEND_STRINGLN\n","\t a \t\n \t b  \n    c\n");
  else if(name=="stage7_internal_tabs_preserved")visible("STRING\n a\tb\nEND_STRING\nSTRINGLN\n\tc\td\nEND_STRINGLN\n","a\tbc\td\n");
  else if(name=="stage7_literal_command_keywords")visible("STRINGLN\nSTOP\nDELAY 999\nSAVE missing STRING bad\nATTACKMODE OFF\nFUNCTION fake()\nRETURN 5\nEND_FUNCTION\nEND_IF\nEND_WHILE\nREM_BLOCK\nEND_REM\nEND_STRINGLN\nSTRINGLN after\n","STOP\nDELAY 999\nSAVE missing STRING bad\nATTACKMODE OFF\nFUNCTION fake()\nRETURN 5\nEND_FUNCTION\nEND_IF\nEND_WHILE\nREM_BLOCK\nEND_REM\nafter\n");
  else if(name=="stage7_terminator_prefixes_are_literal")visible("STRINGLN\nEND_STRINGLN_more\nEND_STRINGLY\nEND_STRING_more\nEND_STRINGLN\n","END_STRINGLN_more\nEND_STRINGLY\nEND_STRING_more\n");
  else if(name=="stage7_case_and_indented_delimiters")visible(" \tStRiNgLn \t\n\t a\n\tEnD_sTrInGlN \t\n"," a\n");
  else if(name=="stage7_inline_compatibility_unchanged")visible("STRING   a\nSTRINGLN  b\nSTRINGLN after\n","  a b\nafter\n");
  else if(name=="stage7_lf_and_crlf_equivalent") {visible("STRINGLN\n\ta\n\tb\nEND_STRINGLN\n","a\nb\n");visible("STRINGLN\r\n\ta\r\n\tb\r\nEND_STRINGLN\r\n","a\nb\n");}
  else if(name=="stage7_bom_only_at_source_start")visible("\xEF\xBB\xBFSTRINGLN\r\n\ta\r\nEND_STRINGLN","a\n");
  else if(name=="stage7_no_final_newline")visible("STRING\na\nEND_STRING","a");
  else if(name=="stage7_quoted_text_no_unescaping")visible("STRINGLN\n\t\"a\" \\n \\t\nEND_STRINGLN\n","\"a\" \\n \\t\n");
  else if(name=="stage7_numeric_boolean_and_text_interpolation")visible("VAR $n=9\nVAR $yes=TRUE\nVAR $word=\"ready\"\nSTRINGLN\n\t$word n=$n yes=$yes\nEND_STRINGLN\n","ready n=9 yes=1\n");
  else if(name=="stage7_unknown_host_variables_are_literal")visible("VAR $n=9\nSTRINGLN\n$missing $n_suffix ${n} $n\nEND_STRINGLN\n","$missing $n_suffix ${n} 9\n");
  else if(name=="stage7_variable_replacement_is_single_pass")visible("VAR $a=\"$unknown\"\nVAR $unknown=5\nSTRINGLN\n$a\nEND_STRINGLN\n","$unknown\n");
  else if(name=="stage7_define_hash_and_word_replacement")visible("DEFINE #WORD ready\nDEFINE BARE yes\nSTRINGLN\n\t(#WORD) BARE BAREsuffix (BARE)\nEND_STRINGLN\n","(ready) yes BAREsuffix (BARE)\n");
  else if(name=="stage7_define_body_not_collected_or_expanded")visible("DEFINE #WORD good\nSTRINGLN\nDEFINE #WORD bad\nDEFINE #OTHER value\n#WORD #OTHER\nEND_STRINGLN\nSTRINGLN #WORD\n","DEFINE #WORD bad\nDEFINE #OTHER value\ngood #OTHER\ngood\n");
  else if(name=="stage7_define_single_pass_and_variable_order")visible("DEFINE #INNER ready\nDEFINE #OUTER #INNER\nDEFINE #VAR $n\nVAR $n=3\nSTRINGLN\n#OUTER #VAR\nEND_STRINGLN\n","#INNER 3\n");
  else if(name=="stage7_expansion_cannot_close_or_execute")visible("DEFINE #END END_STRINGLN\nDEFINE #CMD STOP\nVAR $text=\"END_STRINGLN\"\nSTRINGLN\n#END\n#CMD\n$text\nEND_STRINGLN\nSTRINGLN after\n","END_STRINGLN\nSTOP\nEND_STRINGLN\nafter\n");
  else if(name=="stage7_value_whitespace_after_source_dedent")visible("DEFINE #WORD  a \nVAR $text=\" b \"\nSTRING\n  #WORD$text\nEND_STRING\n"," a  b ");
  else if(name=="stage7_maximum_body_line") {std::string body(DUCKSCRIPT_MAX_LINE_LEN,'x');visible("STRING\n"+body+"\nEND_STRING\n",body.c_str());visible("STRINGLN\n"+body+"\nEND_STRINGLN\n",(body+"\n").c_str());}
  else if(name=="stage7_overlong_body_zero_hid")invalid("STRINGLN hidden\nSTRING\n"+std::string(DUCKSCRIPT_MAX_LINE_LEN+1,'x')+"\nEND_STRING\n","line length limit",3);
  else if(name=="stage7_define_expansion_boundary") {std::string body(256,'x');visible("DEFINE #X "+body+"\nSTRING\n#X#X\nEND_STRING\n",(body+body).c_str());invalid("STRINGLN hidden\nDEFINE #X "+body+"\nSTRING\n#X#Xx\nEND_STRING\n","expansion length limit",4);}
  else if(name=="stage7_interpolation_boundary_and_overflow") {std::string body(256,'x');visible("VAR $v=\""+body+"\"\nSTRING\n$v$v\nEND_STRING\n",(body+body).c_str());runtimeError("VAR $v=\""+body+"\"\nSTRING\n$v$vx\n$v$v!\nEND_STRING\n","Interpolation length limit",(body+"$vx").c_str());}
  else if(name=="stage7_inactive_interpolation_has_no_runtime_effect") {std::string body(256,'x');visible("VAR $v=\""+body+"\"\nIF FALSE THEN\nSTRINGLN\n$v$v!\nSTOP\nEND_STRINGLN\nEND_IF\nSTRINGLN after\n","after\n");}
  else if(name=="stage7_unterminated_after_output_zero_hid") {invalid("STRINGLN hidden\nSTRING\nbody\n","Unterminated STRING",2);invalid("STRINGLN hidden\nSTRINGLN\nEND_IF","Unterminated STRINGLN",2);}
  else if(name=="stage7_mismatched_or_argument_terminators_zero_hid") {invalid("STRINGLN hidden\nSTRING\na\nEND_STRINGLN\n","Mismatched",4);invalid("STRINGLN hidden\nSTRINGLN\na\nEND_STRING\n","Mismatched",4);invalid("STRINGLN hidden\nSTRINGLN\na\nEND_STRINGLN extra\n","takes no arguments",4);}
  else if(name=="stage7_unmatched_terminators_zero_hid") {invalid("STRINGLN hidden\nEND_STRING\n","Unmatched",2);invalid("STRINGLN hidden\nEND_STRINGLN\n","Unmatched",2);}
  else if(name=="stage7_literal_openers_inside_body")visible("STRINGLN\nSTRING\nSTRINGLN\nREM_BLOCK\nEND_REM\nEND_STRINGLN\n","STRING\nSTRINGLN\nREM_BLOCK\nEND_REM\n");
  else if(name=="stage7_fixture_spiffs_and_sd") {const char *out="ready n=2\nIF literal THEN\njoined-2\nready n=1\nIF literal THEN\njoined-1\n";visible(fixture,out);visible(fixture,out,"sd:stage7.txt");}
  else if(name=="stage7_if_else_active_inactive_blocks")visible("IF FALSE THEN\nSTRINGLN\nhidden\nSTOP\nEND_STRINGLN\nELSE\nSTRINGLN\nselected\nEND_STRINGLN\nEND_IF\n","selected\n");
  else if(name=="stage7_zero_iteration_loop_blocks")visible("WHILE FALSE\nSTRINGLN\nhidden\nEND_STRINGLN\nEND_WHILE\nSTRINGLN after\n","after\n");
  else if(name=="stage7_nested_loops_interpolate_current_values")visible("VAR $o=2\nWHILE $o>0\nVAR $i=2\nWHILE $i>0\nSTRINGLN\n$o:$i\nEND_STRINGLN\n$i=$i-1\nEND_WHILE\n$o=$o-1\nEND_WHILE\n","2:2\n2:1\n1:2\n1:1\n");
  else if(name=="stage7_function_repeat_calls_and_return")visible("FUNCTION show()\nSTRINGLN\nvalue=$n\nRETURN 99\nEND_STRINGLN\nRETURN $n\nEND_FUNCTION\nVAR $n=1\nVAR $v=show()\n$n=2\nVAR $v=show()\nSTRINGLN $v\n","value=1\nRETURN 99\nvalue=2\nRETURN 99\n2\n");
  else if(name=="stage7_nested_functions_with_blocks")visible("FUNCTION inner()\nSTRINGLN\ninner\nEND_STRINGLN\nEND_FUNCTION\nFUNCTION outer()\nSTRING\nouter-\nEND_STRING\ninner()\nEND_FUNCTION\nouter()\n","outer-inner\n");
  else if(name=="stage7_recursive_calls_with_blocks")visible("FUNCTION recurse()\nSTRINGLN\nn=$n\nEND_STRINGLN\nIF $n>1 THEN\n$n=$n-1\nrecurse()\nEND_IF\nEND_FUNCTION\nVAR $n=3\nrecurse()\n","n=3\nn=2\nn=1\n");
  else if(name=="stage7_repeat_literal_text_and_whitespace")visible("STRINGLN\n\tSTOP  \nEND_STRINGLN\nREPEAT 2\nSTRINGLN after\n","STOP  \nSTOP  \nSTOP  \nafter\n");
  else if(name=="stage7_repeat_blank_stringln")visible("STRINGLN\n\nEND_STRINGLN\nREPLAY 2\n","\n\n\n");
  else if(name=="stage7_empty_string_does_not_replace_history")visible("STRING x\nSTRING\n\n  \nEND_STRING\nREPEAT 1\n","xx");
  else if(name=="stage7_repeat_interpolates_again")visible("VAR $n=1\nSTRINGLN\n$n\nEND_STRINGLN\n$n=2\nREPEAT 1\n","1\n2\n");
  else if(name=="stage7_default_delays_per_body_line") {visible("DEFAULT_DELAY 50\nSTRINGLN\na\nb\nEND_STRINGLN\n","a\nb\n");auto a=mock::presses[0];auto b=*std::find_if(mock::presses.begin(),mock::presses.end(),[](auto p){return p.key==5;});require(b.time-a.time>=50,"body lines retain configured default delay");}
  else if(name=="stage7_cancel_default_delay") {pending("DEFAULT_DELAY 100000\nSTRINGLN\nx\ny\nEND_STRINGLN\n",3);for(unsigned i=0;i<100;++i)mock::tick();require(mock::text=="x\n","reach body-line default delay");cancel();}
  else if(name=="stage7_cancel_halfway_through_typing") {start("STRINGLN\n"+std::string(200,'x')+"\ny\nEND_STRINGLN\nSTRINGLN tail\n");while(mock::text.length()<50)mock::tick();require(mock::text.length()<200,"typing is incremental");cancel();}
  else if(name=="stage7_cancel_held_shift_and_usb_release_retry") {pending("STRINGLN\nABCDEF\nEND_STRINGLN\n",2);while(mock::heldKeys.empty())mock::tick();require(mock::heldModifiers,"shifted text owns modifier");mock::usbReady=false;duckscript::stop();auto count=mock::text.length();for(unsigned i=0;i<20;++i)mock::tick();mock::usbReady=true;for(unsigned i=0;i<20;++i)mock::tick();require(mock::text.length()==count,"cancel prevents queued characters");clean();}
  else if(name=="stage7_usb_backpressure_lossless_and_no_readahead") {pending("STRINGLN\nabc\nsecond\nEND_STRINGLN\n",2);auto reads=mock::bytesRead;mock::usbReady=false;for(unsigned i=0;i<200;++i)mock::tick();require(!mock::text.length(),"busy USB produces no output");require(mock::bytesRead==reads && duckscript::currentLine()==2,"typing gates reading next body line");mock::usbReady=true;drain();require(mock::text=="abc\nsecond\n","resume exactly once without loss");clean();}
  else if(name=="stage7_stop_command_after_block")visible("STRINGLN\nSTOP\nEND_STRINGLN\nSTOP\nSTRINGLN hidden\n","STOP\n");
  else if(name=="stage7_live_ownership_and_clean_run") {pending("STRINGLN\n"+std::string(50,'x')+"\nEND_STRINGLN\n",2);require(!com::executeNow("STRING stolen"),"live text rejects while owned");require(!com::executeNow("VAR $n=99"),"live mutation rejects");cancel();visible("STRINGLN\nclean\nEND_STRINGLN\n","clean\n");}
  else if(name=="stage7_live_block_opener_rejected") {mock::reset();require(!com::executeNow("STRINGLN"),"live commands cannot start streamed blocks");require(!mock::presses.size(),"live rejection has zero HID");clean();}
  else if(name=="stage7_preflight_source_errors_zero_hid") {start("STRINGLN hidden\nSTRINGLN\n"+std::string(200,'a')+"\nEND_STRINGLN\n");mock::failReadAt=64;drain();require(duckscript::lastError().indexOf("Storage read")>=0,"preflight distinguishes read failure");require(mock::presses.empty(),"read failure before HID");clean();}
  else if(name=="stage7_rewind_seek_error_zero_hid") {start("STRINGLN hidden\nSTRINGLN\nbody\nEND_STRINGLN\n");mock::failSeekAt=0;drain();require(duckscript::lastError().indexOf("Storage seek")>=0,"failed preflight rewind diagnoses");require(mock::presses.empty(),"seek rejection before HID");clean();}
  else if(name=="stage7_runtime_body_read_error_spiffs_and_sd") {for(const char *file:{"stage7.txt","sd:stage7.txt"}) {std::string s="STRINGLN\nfirst\n";for(unsigned i=0;i<10;++i)s+=std::string(50,'x')+"\n";s+="END_STRINGLN\nSTRINGLN hidden\n";start(s,file);while(!(duckscript::currentLine()==2 && com::busy()))mock::tick();mock::failReadAt=0;drain();require(duckscript::lastError().indexOf("Storage read")>=0,"runtime read error diagnosed");require(mock::text.startsWith("first\n") && mock::text.indexOf("hidden")<0,"only completed body prefix can appear");clean();}}
  else if(name=="stage7_runtime_source_change") {pending("STRINGLN\nfirst\nsecond\nEND_STRINGLN\n",2);mock::sourceSizeIncrease=1;drain();require(duckscript::lastError().indexOf("source changed")>=0,"source mutation fails safely");require(mock::text=="first\n","pending line finishes; no unread body executes");clean();}
  else if(name=="stage7_loop_backedge_seek_error") {pending("VAR $n=1\nWHILE $n>0\nSTRINGLN\nfirst\nEND_STRINGLN\n$n=0\nEND_WHILE\n",4);mock::failSeekAt=9;drain();require(duckscript::lastError().indexOf("Storage seek")>=0,"text loop backedge seek fails");clean();}
  else if(name=="stage7_function_return_seek_error") {const std::string s="FUNCTION show()\nSTRINGLN\nfirst\nEND_STRINGLN\nEND_FUNCTION\nshow()\nSTRINGLN hidden\n";pending(s,3);mock::failSeekAt=s.find("STRINGLN hidden");drain();require(duckscript::lastError().indexOf("Storage seek")>=0,"return seek error stops after body");require(mock::text=="first\n","return failure prevents tail");clean();}
  else if(name=="stage7_large_block_streamed_and_cooperative") {std::string s="STRING\n",out;for(unsigned i=0;i<4096;++i){s+="  abcdefghijklmnop\n";out+="abcdefghijklmnop";}s+="END_STRING\n";start(s);for(unsigned i=0;i<20;++i)mock::tick();require(duckscript::running() && mock::presses.empty(),"large preflight yields before HID");drain(2000000);require(mock::text==out.c_str(),"large streamed block exact output");require(!duckscript::lastError().length(),"large block completes");clean();}
  else if(name=="stage7_cancel_large_block_preflight") {std::string s="STRINGLN\n";for(unsigned i=0;i<4000;++i)s+="body\n";s+="END_STRINGLN\n";start(s);for(unsigned i=0;i<20;++i)mock::tick();require(mock::presses.empty(),"large block not emitted during preflight");cancel();}
  else if(name=="stage7_source_limits_zero_hid") {mock::reset();mock::file("stage7.txt",("STRING\n"+std::string(DUCKSCRIPT_MAX_SOURCE_BYTES,'x')+"\nEND_STRING\n").c_str());require(!duckscript::run("stage7.txt"),"oversized source refuses opening");require(!duckscript::running() && duckscript::lastError().indexOf("byte limit")>=0,"oversized source rejected");require(mock::presses.empty(),"oversized source zero HID");clean();std::string s="STRINGLN hidden\nSTRINGLN\n";for(unsigned i=0;i<DUCKSCRIPT_MAX_SOURCE_LINES;++i)s+="\n";s+="END_STRINGLN\n";invalid(s,"line limit",DUCKSCRIPT_MAX_SOURCE_LINES+1);}
  else if(name=="stage7_hid_disabled_block_has_no_output")visible("ATTACKMODE OFF\nSTRINGLN\nno-output\nEND_STRINGLN\nATTACKMODE HID\nSTRINGLN\nafter\nEND_STRINGLN\n","after\n");
  else if(name=="stage7_control_nesting_boundaries") {
    for(const char *opener:{"STRING","STRINGLN"}) {
      std::string s;
      for(unsigned i=0;i<DUCKSCRIPT_MAX_BLOCK_DEPTH;++i)s+="IF TRUE THEN\n";
      s+=std::string(opener)+"\ninside\nEND_"+opener+"\n";
      for(unsigned i=0;i<DUCKSCRIPT_MAX_BLOCK_DEPTH;++i)s+="END_IF\n";
      visible(s,opener==std::string("STRING") ? "inside" : "inside\n");
      invalid("IF TRUE THEN\n"+s+"END_IF\n","nesting limit",DUCKSCRIPT_MAX_BLOCK_DEPTH+1);
    }
  }
  else if(name=="stage7_malformed_later_control_zero_hid")invalid("STRINGLN\nMUST-NOT-APPEAR\nEND_STRINGLN\nIF TRUE THEN\nSTRINGLN hidden\n","Unterminated IF",4);
  else if(name=="stage7_text_blocks_do_not_execute_calls")visible("FUNCTION side()\nSTRINGLN hidden\nEND_FUNCTION\nSTRINGLN\nside()\nVAR $n=side()\nEND_STRINGLN\n","side()\nVAR $n=side()\n");
  else throw std::runtime_error("unknown test name");
}
int main(int argc,char **argv) {
  if(argc!=2)return 2;
  try {mock::reset();test(argv[1]);std::cout<<"PASS "<<argv[1]<<" ("<<assertions<<" assertions)\n";return 0;}
  catch(const std::exception &e){std::cerr<<"FAIL "<<argv[1]<<": "<<e.what()<<'\n';return 1;}
}
