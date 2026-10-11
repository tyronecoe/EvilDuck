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
static void start(const std::string &script,const char *file="stage5.txt") {
  mock::reset();finalLiveValues.clear();mock::file(file,script.c_str());require(duckscript::run(file),"start cooperative fixture");
}
static void visible(const std::string &script,const char *expected,const char *file="stage5.txt",unsigned ticks=20000) {
  start(script,file);drain(ticks);
  if(duckscript::lastError().length()) std::cerr<<duckscript::lastError().c_str()<<'\n';
  require(!duckscript::lastError().length(),"valid script must have no error");
  if(mock::text!=expected)std::cerr<<"Actual output: "<<mock::text.c_str()<<" Expected: "<<expected<<'\n';
  require(mock::text==expected,"exact harmless output");clean();
}
static void numeric(const char *name,uint16_t expected) {
  require(finalLiveValues.count(name) && finalLiveValues[name]==expected,"expected final global value read while execution was live");
}
static void invalid(const std::string &script,const char *diagnostic,unsigned line) {
  start(script,"sd:bad-stage5.txt");drain();auto error=duckscript::lastError();
  if(error.indexOf(diagnostic)<0)std::cerr<<"Actual diagnostic: "<<error.c_str()<<'\n';
  require(error.indexOf(diagnostic)>=0,"useful preflight error");
  require(error.indexOf("sd:bad-stage5.txt: Error at line "+String(line)+":")>=0,"source/line error location");
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
static const char *fixture=
 "DEFINE #COUNT 2\nVAR $outer=0\nWHILE ($outer<#COUNT)\n"
 "VAR $inner=0\nWHILE ($inner<2)\nIF $inner==0 THEN\n"
 "STRINGLN o=$outer i=$inner\nELSE IF $outer==1 THEN\nSTRINGLN last\n"
 "ELSE\nSTRINGLN middle\nEND_IF\n$inner=($inner+1)\nEND_WHILE\n"
 "$outer=($outer+1)\nEND_WHILE\nSTRINGLN done=$outer\n";

static void test(const String &name) {
  if(name=="stage5_false_while_following_commands") visible("VAR $flag=0\nWHILE $flag\nSTRINGLN hidden\nEND_WHILE\nSTRINGLN after\n","after\n");
  else if(name=="stage5_zero_iteration_expressions") {
    for(const char *condition:{"FALSE","0","(2^3)==7","0x10<4","FALSE && TRUE","0>>1"})
      visible("WHILE "+std::string(condition)+"\nSTRINGLN hidden\nEND_WHILE\nSTRINGLN after\n","after\n");
  } else if(name=="stage5_single_iteration") {visible("VAR $n=0\nWHILE $n==0\n$n=1\nSTRINGLN once\nEND_WHILE\nSTRINGLN after\n","once\nafter\n");numeric("$n",1);}
  else if(name=="stage5_multiple_iterations") {visible("VAR $n=0\nWHILE ($n<3)\nSTRINGLN n=$n\n$n=$n+1\nEND_WHILE\nSTRINGLN n=$n\n","n=0\nn=1\nn=2\nn=3\n");numeric("$n",3);}
  else if(name=="stage5_decrementing_numeric_no_hid") {visible("VAR $n=5\nVAR $sum=0\nWHILE $n>0\n$sum=$sum+$n\n$n=$n-1\nEND_WHILE\n","");numeric("$n",0);numeric("$sum",15);require(mock::presses.empty(),"numeric-only loop produces no HID");}
  else if(name=="stage5_shared_expression_operators") {
    for(const char *condition:{"$n+1<=3","($n*2)/2<3","$n%4<3","2^$n<8","($n!=3)&&TRUE","($n<3)||FALSE","($n&3)<3","($n|0)<3","($n<<1)<6","(0x10>>$n)>2","$n>=0 && $n<=2","($n+65535)!=2"}) {
      visible("VAR $n=0\nWHILE "+std::string(condition)+"\n$n=$n+1\nEND_WHILE\n","");numeric("$n",3);
    }
  } else if(name=="stage5_condition_reevaluated_at_header") {visible("VAR $n=0\nVAR $limit=5\nWHILE $n<$limit\n$n=$n+1\n$limit=$limit-1\nEND_WHILE\n","");numeric("$n",3);numeric("$limit",2);}
  else if(name=="stage5_nested_two_loops") {visible("VAR $o=0\nVAR $count=0\nWHILE $o<3\nVAR $i=0\nWHILE $i<2\n$count=$count+1\n$i=$i+1\nEND_WHILE\n$o=$o+1\nEND_WHILE\nSTRINGLN count=$count\n","count=6\n");numeric("$o",3);numeric("$i",2);}
  else if(name=="stage5_nested_three_loops") {visible("VAR $o=0\nVAR $count=0\nWHILE $o<2\nVAR $i=0\nWHILE $i<3\nVAR $j=0\nWHILE $j<4\n$count=$count+1\n$j=$j+1\nEND_WHILE\n$i=$i+1\nEND_WHILE\n$o=$o+1\nEND_WHILE\n","");numeric("$count",24);}
  else if(name=="stage5_sequential_loops") {visible("VAR $a=0\nVAR $b=0\nWHILE $a<2\n$a=$a+1\nEND_WHILE\nWHILE FALSE\nSTRINGLN hidden\nEND_WHILE\nWHILE $b<3\n$b=$b+1\nEND_WHILE\nSTRINGLN $a,$b\n","2,3\n");}
  else if(name=="stage5_if_inside_while_else_if") visible("VAR $n=0\nWHILE $n<3\nIF $n==0 THEN\nSTRING first\nELSE IF $n==1 THEN\nSTRING middle\nELSE\nSTRING last\nEND_IF\n$n=$n+1\nEND_WHILE\n","firstmiddlelast");
  else if(name=="stage5_while_inside_if_else") visible("IF FALSE THEN\nWHILE TRUE\nSTRING hidden\nEND_WHILE\nELSE IF TRUE THEN\nVAR $n=0\nWHILE $n<2\n$n=$n+1\nSTRING $n\nEND_WHILE\nELSE\nSTRING hidden\nEND_IF\nSTRINGLN after\n","12after\n");
  else if(name=="stage5_mixed_nested_structures") visible(fixture,"o=0 i=0\nmiddle\no=1 i=0\nlast\ndone=2\n");
  else if(name=="stage5_fixture_spiffs_and_sd") {visible(fixture,"o=0 i=0\nmiddle\no=1 i=0\nlast\ndone=2\n","fixture.txt");visible(fixture,"o=0 i=0\nmiddle\no=1 i=0\nlast\ndone=2\n","sd:fixture.txt");}
  else if(name=="stage5_false_outer_suppresses_nested_conditions") visible("VAR $zero=0\nWHILE FALSE\nIF 1/$zero THEN\nWHILE 1/$zero\nSTRING hidden\nEND_WHILE\nELSE\nSTOP\nEND_IF\nEND_WHILE\nIF FALSE THEN\nWHILE 1/$zero\nSTRING hidden\nEND_WHILE\nEND_IF\nSTRINGLN after\n","after\n");
  else if(name=="stage5_inactive_side_effects_and_assignments") {
    visible("VAR $n=7\nWHILE FALSE\n$n=99\nDELAY 60000\nDEFAULT_DELAY 60000\nREPEAT 99\nKEYCODE 2 4\nLOCALE de\nLED 200 201 202\nATTACKMODE OFF\nSAVE absent STRING hidden\nAPPEND absent STRING hidden\nREAD missing $read\nSTOP\nEND_WHILE\nSTRINGLN n=$n\n","n=7\n");
    numeric("$n",7);require(mock::now<1000 && !mock::files.count("absent"),"inactive timer/file effects suppressed");
    require(attackmode::hidEnabled(),"inactive mode suppressed");require(std::find(mock::colors.begin(),mock::colors.end(),std::array<int,3>{200,201,202})==mock::colors.end(),"inactive LED suppressed");
  } else if(name=="stage5_nested_updates_outer_variable") {visible("VAR $o=0\nVAR $i=0\nWHILE $o<2\nWHILE $i<3\n$o=$o+1\n$i=$i+1\nEND_WHILE\nEND_WHILE\n","");numeric("$o",3);numeric("$i",3);}
  else if(name=="stage5_global_declarations_reused") {visible("VAR $n=0\nWHILE $n<3\nVAR $v=$n\n$n=$n+1\nEND_WHILE\nSTRINGLN v=$v\n","v=2\n");numeric("$v",2);}
  else if(name=="stage5_exact_loop_depth") {
    std::string s="VAR $n=0\n";for(unsigned i=0;i<DUCKSCRIPT_MAX_BLOCK_DEPTH;++i)s+="WHILE $n==0\n";
    s+="$n=1\nSTRINGLN boundary\n";for(unsigned i=0;i<DUCKSCRIPT_MAX_BLOCK_DEPTH;++i)s+="END_WHILE\n";visible(s,"boundary\n");
  } else if(name=="stage5_mixed_exact_depth") {
    std::string s="VAR $n=0\n";for(unsigned i=0;i<DUCKSCRIPT_MAX_BLOCK_DEPTH;++i)s+=(i%2?"IF TRUE THEN\n":"WHILE $n==0\n");
    s+="$n=1\nSTRINGLN boundary\n";for(int i=DUCKSCRIPT_MAX_BLOCK_DEPTH-1;i>=0;--i)s+=(i%2?"END_IF\n":"END_WHILE\n");visible(s,"boundary\n");
  } else if(name=="stage5_depth_plus_one_zero_hid") {
    for(bool mixed:{false,true}) {std::string s="STRINGLN hidden\n";for(unsigned i=0;i<=DUCKSCRIPT_MAX_BLOCK_DEPTH;++i)s+=(mixed && i%2?"IF TRUE THEN\n":"WHILE TRUE\n");invalid(s,"nesting limit",DUCKSCRIPT_MAX_BLOCK_DEPTH+2);}
  } else if(name=="stage5_malformed_conditions_zero_hid") {
    for(const char *condition:{"","THEN","TRUE THEN","(5+)","(TRUE","TRUE)","1===1","1 2","1=1","!TRUE","$bad+","0x10000","1/0","1<<16"})invalid("STRINGLN hidden\nWHILE "+std::string(condition)+"\nEND_WHILE\n","",2);
  } else if(name=="stage5_undefined_and_text_expression_rejection") {
    invalid("STRINGLN hidden\nWHILE $missing\nEND_WHILE\n","Undefined",2);
    invalid("VAR $text=\"5\"\nWHILE ($text)\nEND_WHILE\n","Text variable",2);
    invalid("VAR $text=\"5\"\nWHILE $text==5\nEND_WHILE\n","Text variable",2);
    invalid("WHILE FALSE\nWHILE $missing\nEND_WHILE\nEND_WHILE\n","Undefined",2);
  } else if(name=="stage5_missing_unmatched_and_crossed_terminators") {
    invalid("STRINGLN hidden\nWHILE TRUE\nSTRING hidden\n","Unterminated",2);
    invalid("STRINGLN hidden\nEND_WHILE\n","Unmatched",2);
    invalid("WHILE TRUE\nIF TRUE THEN\nEND_WHILE\nEND_IF\n","Mismatched",3);
    invalid("IF TRUE THEN\nWHILE TRUE\nEND_IF\nEND_WHILE\n","Mismatched",3);
    invalid("WHILE TRUE\nELSE\nEND_WHILE\n","Unmatched",2);
    invalid("WHILE TRUE\nEND_WHILE extra\n","",2);
  } else if(name=="stage5_keyword_boundaries_and_aliases") {
    for(const char *end:{"END_WHILE","ENDWHILE","END WHILE","end\twhile"})visible(" \tVAR $n=0\n\twhile\t($n<1)\n$n=1\n"+std::string(end)+"\nSTRINGLN ok\n","ok\n");
    for(const char *line:{"WHILEish TRUE","WHILETRUE","END_WHILEish","ENDWHILEish"})invalid("STRINGLN hidden\n"+std::string(line)+"\n","Unsupported",2);
  } else if(name=="stage5_legacy_bare_text_truthiness") {
    visible("VAR $text=\"true\"\nWHILE $text\nSTRINGLN once\nVAR $text=\"false\"\nENDWHILE\nSTRINGLN after\n","once\nafter\n");
    visible("VAR $text=\"false\"\nWHILE $text\nSTRING hidden\nEND WHILE\nSTRINGLN after\n","after\n");
  } else if(name=="stage5_define_conditions_and_protected_keywords") visible("DEFINE #LIMIT 2\nDEFINE WHILE damaged\nDEFINE END_WHILE damaged\nDEFINE ENDWHILE damaged\nVAR $n=0\nWHILE $n<#LIMIT\n$n=$n+1\nEND_WHILE\nSTRINGLN n=$n\n","n=2\n");
  else if(name=="stage5_macro_manufactured_loop_delimiters_rejected") {for(const char *line:{"WHILE TRUE","END_WHILE","ENDWHILE","END WHILE"})invalid("DEFINE #CONTROL "+std::string(line)+"\nSTRINGLN hidden\n#CONTROL\n","cannot create WHILE",3);}
  else if(name=="stage5_define_collection_inside_inactive_loop") visible("VAR $n=0\nWHILE $n<#LIMIT\n$n=$n+1\nEND_WHILE\nWHILE FALSE\nDEFINE #LIMIT 2\nEND_WHILE\nSTRINGLN $n\n","2\n");
  else if(name=="stage5_rem_block_loop_text_ignored") visible("VAR $n=0\nWHILE $n<1\nREM_BLOCK\nWHILE garbage\nEND_IF\nELSE\nEND_WHILE\nEND_REM\n$n=1\nEND_WHILE\nSTRINGLN ok\n","ok\n");
  else if(name=="stage5_text_blocks_keep_literal_modes") {for(const char *k:{"STRING","STRINGLN"})visible("STRINGLN hidden\n"+std::string(k)+"\nWHILE invalid\nIF fake\nEND_WHILE\nEND_IF\nEND_"+k+"\n",k==std::string("STRING") ? "hidden\nWHILE invalidIF fakeEND_WHILEEND_IF" : "hidden\nWHILE invalid\nIF fake\nEND_WHILE\nEND_IF\n");}
  else if(name=="stage5_bom_crlf_no_final_newline_backedges") visible("\xEF\xBB\xBFVAR $n=0\r\nWHILE $n<2\r\nSTRINGLN $n\r\n$n=$n+1\r\nEND_WHILE\r\nSTRINGLN done","0\n1\ndone\n","sd:crlf.txt");
  else if(name=="stage5_header_across_read_budgets") {
    std::string condition="WHILE "+std::string(280,' ') +"$n<2";
    visible("VAR $n=0\n"+condition+"\n$n=$n+1\nEND_WHILE\nSTRINGLN $n\n","2\n","sd:long-header.txt");
  } else if(name=="stage5_reader_marker_and_seek_boundaries") {
    const std::string prefix="\xEF\xBB\xBFREM first\r\n";const std::string header="WHILE "+std::string(280,' ')+"FALSE\r\n";
    File f((prefix+header+"END_WHILE").c_str());script_source::Reader r;require(r.begin(f),"begin reader");
    String line;for(unsigned i=0;i<3;++i){script_source::Result result;do{uint16_t bytes=7;result=r.next(line,bytes);}while(result==script_source::Result::Yield);require(result==script_source::Result::Line,"complete partial line");require(r.lineStartPosition()==(i==0?0:i==1?prefix.size():prefix.size()+header.size()),"exact byte marker including CRLF/BOM");}
    require(r.seek(prefix.size(),1),"seek true header marker");uint16_t bytes=512;require(r.next(line,bytes)==script_source::Result::Line && r.lineNumber()==2 && line==header.substr(0,header.size()-2).c_str(),"rewind invalidates read ahead and restores header/line");
    require(r.seek(0,0),"rewind BOM");bytes=512;require(r.next(line,bytes)==script_source::Result::Line && line=="REM first","BOM stripped again on rewind");
    f.close();bytes=512;require(r.next(line,bytes)==script_source::Result::Error && r.error().indexOf("unavailable")>=0,"closed source distinguished from EOF");
  } else if(name=="stage5_runtime_seek_error") {
    pending("VAR $n=0\nWHILE $n<2\nSTRING x\n$n=$n+1\nEND_WHILE\nSTRING hidden\n",3);mock::failSeekAt=std::string("VAR $n=0\n").size();drain();
    require(duckscript::lastError().indexOf("seek error")>=0 && duckscript::lastError().indexOf("line 5")>=0,"backedge seek error at terminator");require(mock::text=="x","stop after emitted body before tail");clean();
  } else if(name=="stage5_runtime_read_error_after_backedge") {
    pending("VAR $n=0\nWHILE $n<2\nSTRING x\n$n=$n+1\nEND_WHILE\nSTRING hidden\n",3);mock::failReadAt=std::string("VAR $n=0\n").size();drain();
    require(duckscript::lastError().indexOf("read error before EOF")>=0,"fresh header read failure is not EOF");require(mock::text=="x","no repeated or tail output after read error");clean();
  } else if(name=="stage5_runtime_source_size_changed") {
    pending("VAR $n=0\nWHILE $n<2\nSTRING x\n$n=$n+1\nEND_WHILE\n",3);mock::sourceSizeIncrease=1;drain();
    require(duckscript::lastError().indexOf("changed or unavailable")>=0,"source size change rejected");require(mock::text=="x","no further body output after size fault");clean();
  } else if(name=="stage5_runtime_condition_error_and_inactive_skip") {
    start("VAR $divisor=1\nWHILE 1/$divisor\nSTRING x\n$divisor=0\nEND_WHILE\nSTRING hidden\n");drain();require(duckscript::lastError().indexOf("zero")>=0 && duckscript::lastError().indexOf("line 2")>=0,"runtime condition error at WHILE header");require(mock::text=="x","runtime error stops after first body");clean();
    visible("VAR $zero=0\nIF FALSE THEN\nWHILE 1/$zero\nEND_WHILE\nEND_IF\nSTRINGLN safe\n","safe\n");
  } else if(name=="stage5_runtime_undefined_path_dependent_variable") {
    start("IF FALSE THEN\nVAR $n=1\nEND_IF\nWHILE $n\nSTRING hidden\nEND_WHILE\n");drain();require(duckscript::lastError().indexOf("Undefined")>=0 && duckscript::lastError().indexOf("line 4")>=0,"preflight metadata is not path simulation");require(mock::presses.empty(),"runtime failure before first output");clean();
  } else if(name=="stage5_repeat_structural_and_inactive_history") visible("VAR $n=0\nWHILE $n<2\n$n=$n+1\nSTRING $n\nEND_WHILE\nREPEAT 2\nWHILE FALSE\nSTRING hidden\nEND_WHILE\nREPLAY 1\n","12222");
  else if(name=="stage5_repeat_expression_in_loop") visible("VAR $n=0\nWHILE $n<2\n$n=$n+1\nSTRING x\nREPEAT $n\nEND_WHILE\n","xxxxx");
  else if(name=="stage5_keyboard_combinations_in_loop") {visible("VAR $n=0\nWHILE $n<2\n$n=$n+1\nCTRL ALT a\nSHIFT b\nEND_WHILE\n","BB");require(mock::presses.size()==4 && mock::presses[0].modifiers==5 && mock::presses[1].modifiers==2,"existing modifier reports preserved");}
  else if(name=="stage5_expression_delays_in_loop") {visible("VAR $n=0\nDEFAULT_DELAY 2\nWHILE $n<2\n$n=$n+1\nDELAY $n*10\nWAIT 1\nSTRING x\nEND_WHILE\n","xx");require(mock::presses[1].time>mock::presses[0].time+20,"cooperative expression delay applied per iteration");}
  else if(name=="stage5_stop_in_active_and_inactive_loops") {visible("WHILE TRUE\nSTRINGLN once\nSTOP\nSTRING hidden\nEND_WHILE\nSTRING hidden\n","once\n");visible("WHILE FALSE\nSTOP\nEND_WHILE\nSTRINGLN after\n","after\n");}
  else if(name=="stage5_cancel_delay_inside_mixed_loop") {pending("VAR $n=0\nWHILE $n<2\nIF TRUE THEN\nDELAY 60000\nSTRING hidden\nEND_IF\n$n=$n+1\nEND_WHILE\n",4);cancel();}
  else if(name=="stage5_cancel_text_inside_nested_loop") {pending("WHILE TRUE\nWHILE TRUE\nSTRING "+std::string(200,'x')+"\nEND_WHILE\nEND_WHILE\nSTRING hidden\n",3);for(unsigned i=0;i<30;++i)mock::tick();require(mock::text.length()>0 && mock::text.length()<200,"text remains incremental");cancel();}
  else if(name=="stage5_cancel_held_keys_and_usb_pressure") {pending("WHILE TRUE\nCTRL ALT a\nEND_WHILE\nSTRING hidden\n",2);for(unsigned i=0;i<20 && mock::heldKeys.empty();++i)mock::tick();require(!mock::heldKeys.empty(),"runtime report held");mock::usbReady=false;duckscript::stop();require(!duckscript::running(),"cancel immediately while USB busy");mock::usbReady=true;for(unsigned i=0;i<20;++i)mock::tick();require(!mock::text.length() || mock::text=="a","only initial mocked chord can appear");clean();}
  else if(name=="stage5_control_only_loop_cooperative_and_live_ownership") {
    start("WHILE TRUE\nEND_WHILE\nSTRING hidden\n");for(unsigned i=0;i<20;++i){size_t reads=mock::readCalls,bytes=mock::bytesRead;mock::tick();require(mock::readCalls-reads<=DUCKSCRIPT_LINE_BUDGET+4,"bounded read calls per update across seeks");require(mock::bytesRead-bytes<=DUCKSCRIPT_READ_BUDGET+64*DUCKSCRIPT_LINE_BUDGET,"bounded read ahead per update");}
    require(duckscript::running(),"control-only loop yields before stalled threshold");require(!com::executeNow("STRING hidden"),"live execution rejected");cli::parse("send STRING hidden",mock::print,false);require(mock::text.length()==0,"live commands cannot corrupt script ownership");cli::parse("stop",mock::print,false);clean();
  } else if(name=="stage5_stalled_empty_loop_boundary") {
    require(DUCKSCRIPT_MAX_STALLED_ITERATIONS==1024,"reviewed stalled limit");start("WHILE TRUE\nEND_WHILE\nSTRING hidden\n");drain();require(duckscript::lastError().indexOf("WHILE stalled")>=0 && duckscript::lastError().indexOf("line 1")>=0,"empty loop diagnosed at opening line");require(mock::presses.empty(),"no output after stalled loop");clean();
  } else if(name=="stage5_stalled_same_assignment_and_inactive_actions") {
    start("VAR $n=1\nWHILE $n\n$n=$n\nIF FALSE THEN\nSTRING hidden\nDELAY 1\nEND_IF\nEND_WHILE\nSTRING hidden\n");drain();require(duckscript::lastError().indexOf("WHILE stalled")>=0,"same value and inactive commands cannot fake progress");numeric("$n",1);require(mock::presses.empty(),"stalled fixture emits nothing");clean();
  } else if(name=="stage5_nested_stall_not_masked_by_outer_progress") {
    start("VAR $n=0\nWHILE TRUE\n$n=$n+1\nWHILE TRUE\nEND_WHILE\nEND_WHILE\nSTRING hidden\n");drain();require(duckscript::lastError().indexOf("stalled")>=0 && duckscript::lastError().indexOf("line 4")>=0,"inner stagnation cannot use outer prior progress");numeric("$n",1);clean();
  } else if(name=="stage5_variable_progress_beyond_stall_threshold") {visible("VAR $n=0\nWHILE $n<2000\n$n=$n+1\nEND_WHILE\n", "");numeric("$n",2000);require(mock::presses.empty(),"progress need not be HID");}
  else if(name=="stage5_total_iteration_limit_and_clean_restart") {
    require(DUCKSCRIPT_MAX_LOOP_ITERATIONS==100000,"reviewed total limit");start("VAR $n=0\nWHILE TRUE\n$n=$n+1\nEND_WHILE\nSTRING hidden\n");drain(1000000);
    require(duckscript::lastError().indexOf("total iteration limit")>=0 && duckscript::lastError().indexOf("line 2")>=0,"changing loop still has total bound");numeric("$n",static_cast<uint16_t>(100000));require(mock::presses.empty(),"limit stops before tail");clean();
    mock::file("next.txt","VAR $n=0\nWHILE $n<2\n$n=$n+1\nEND_WHILE\nSTRINGLN $n\n");require(duckscript::run("next.txt"),"restart after guard error");drain();require(!duckscript::lastError().length() && mock::text=="2\n","fresh loop stack/counters/error state");clean();
  } else if(name=="stage5_exact_total_iteration_boundary") {
    visible("VAR $o=0\nWHILE $o<500\nVAR $i=0\nWHILE $i<199\n$i=$i+1\nEND_WHILE\n$o=$o+1\nEND_WHILE\n","","stage5.txt",1000000);numeric("$o",500);numeric("$i",199);require(mock::presses.empty(),"100000 exact total entries numeric-only");
  } else if(name=="stage5_variable_revision_atomic_and_reset") {
    duck_vars::clear();String error;require(duck_vars::revision()==0,"empty revision");require(duck_vars::assign("$n","0",true,error) && duck_vars::revision()==1,"new zero symbol changes revision");require(duck_vars::assign("$n","0",false,error) && duck_vars::revision()==1,"same value no change");require(duck_vars::assign("$n","1",false,error) && duck_vars::revision()==2,"changed value recorded");require(!duck_vars::assign("$n","1/0",false,error) && duck_vars::revision()==2,"failed assignment atomic");require(duck_vars::setText("$t","x",true,error) && duck_vars::revision()==3,"new text changes revision");require(duck_vars::setText("$t","x",false,error) && duck_vars::revision()==3,"same text no change");require(duck_vars::setText("$t","y",false,error) && duck_vars::revision()==4,"changed text revision");duck_vars::clear();require(!duck_vars::revision(),"clear reset");
  } else if(name=="stage5_cancellation_then_new_source") {
    pending("WHILE TRUE\nDELAY 60000\nEND_WHILE\n",2);cancel();mock::file("sd:next.txt","WHILE FALSE\nSTRING hidden\nEND_WHILE\nSTRINGLN clean\n");require(duckscript::run("sd:next.txt"),"next source after cancelled active loop");drain();require(!duckscript::lastError().length() && mock::text=="clean\n","fresh inactive/loop history");clean();
  } else if(name=="stage5_large_inactive_region_cooperative") {
    std::string s="WHILE FALSE\n";for(unsigned i=0;i<4000;++i)s+="REM inactive\n";s+="END_WHILE\nSTRINGLN after\n";
    start(s);for(unsigned i=0;i<20;++i)mock::tick();require(duckscript::running() && mock::presses.empty(),"large source preflight yields");duckscript::stop();clean();visible(s,"after\n");
  } else if(name=="stage5_small_nested_loop_reference_cases") {
    for(unsigned a=0;a<5;++a)for(unsigned b=0;b<5;++b) {
      const std::string s="VAR $a=0\nVAR $sum=0\nWHILE $a<"+std::to_string(a)+"\nVAR $b=0\nWHILE $b<"+std::to_string(b)+"\nIF ($a+$b)%2==0 THEN\n$sum=$sum+2\nELSE\n$sum=$sum+1\nEND_IF\n$b=$b+1\nEND_WHILE\n$a=$a+1\nEND_WHILE\n";
      visible(s,"");unsigned sum=0;for(unsigned i=0;i<a;++i)for(unsigned j=0;j<b;++j)sum+=(i+j)%2==0?2:1;numeric("$sum",sum);
    }
  } else throw std::runtime_error("unknown test name");
}
int main(int argc,char **argv) {
  if(argc!=2)return 2;
  try {mock::reset();test(argv[1]);std::cout<<"PASS "<<argv[1]<<" ("<<assertions<<" assertions)\n";return 0;}
  catch(const std::exception &e){std::cerr<<"FAIL "<<argv[1]<<": "<<e.what()<<'\n';return 1;}
}
