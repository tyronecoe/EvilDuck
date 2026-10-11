#include "host.h"
#include "FS.h"
#include "com.h"
#include "duckscript.h"
#include "duck_vars.h"
#include "script_parser.h"
#include "conditional_state.h"
#include "keyboard_locale.h"
#include "attackmode.h"
#include <iostream>
#include <stdexcept>
#include <string>
#include <algorithm>

static unsigned assertions = 0;
static void require(bool condition, const char *message) {
  ++assertions; if (!condition) throw std::runtime_error(message);
}
static void clean() {
  require(!duckscript::running() && !com::busy(), "execution must finish/cancel");
  require(!mock::blockingDelays, "no blocking delays");
  require(mock::heldKeys.empty() && !mock::heldModifiers, "keys must release");
}
static void visible(const std::string &script, const char *expected, const char *file="stage4.txt") {
  mock::reset(); mock::file(file,script.c_str());
  require(duckscript::run(file), "start streaming script"); mock::drain();
  require(!duckscript::lastError().length(), "valid script must have no error");
  require(mock::text==expected, "exact harmless output must match"); clean();
}
static void invalid(const std::string &script, const char *message, unsigned line) {
  mock::reset(); mock::file("sd:bad-stage4.txt",script.c_str());
  require(duckscript::run("sd:bad-stage4.txt"), "start cooperative preflight"); mock::drain();
  String error=duckscript::lastError();
  if (error.indexOf(message)<0) std::cerr << "Unexpected diagnostic: " << error.c_str() << '\n';
  require(error.indexOf(message)>=0, "diagnostic must identify error");
  require(error.indexOf("sd:bad-stage4.txt: Error at line "+String(line)+":")>=0, "source and line diagnostic");
  require(mock::presses.empty() && !mock::text.length(), "preflight must prevent all HID"); clean();
}
static void pending(const char *script, unsigned line) {
  mock::reset(); mock::file("pending.txt",script);
  require(duckscript::run("pending.txt"), "start pending fixture");
  for(unsigned i=0;i<2000 && !(duckscript::currentLine()==line && com::busy());++i) mock::tick();
  require(duckscript::running() && duckscript::currentLine()==line && com::busy(), "reach expected cooperative pending command");
}
static const char *fixture=
 "DEFINE #TARGET 5\nVAR $x = 5\nIF $x == #TARGET THEN\n"
 "    STRINGLN outer-true\n    IF ($x ^ 2) == 25 THEN\n"
 "        STRINGLN inner-true\n    ELSE\n        STRINGLN inner-false\n    END_IF\n"
 "ELSE\n    STRINGLN outer-false\nEND_IF\nIF $x > 10 THEN\n"
 "    STRINGLN wrong\nELSE\n    $x = ($x + 1)\n    STRINGLN x=$x\nEND_IF\n";

static void test(const String &name) {
  if(name=="stage4_simple_true_if") visible("IF TRUE THEN\nSTRINGLN yes\nEND_IF\n","yes\n");
  else if(name=="stage4_simple_false_if") visible("IF FALSE THEN\nSTRINGLN no\nEND_IF\nSTRINGLN yes\n","yes\n");
  else if(name=="stage4_if_else_true_path") visible("IF 1 THEN\nSTRINGLN yes\nELSE\nSTRINGLN no\nEND_IF\n","yes\n");
  else if(name=="stage4_if_else_false_path") visible("IF 0 THEN\nSTRINGLN no\nELSE\nSTRINGLN yes\nEND_IF\n","yes\n");
  else if(name=="stage4_nested_true_true") visible("IF TRUE THEN\nIF TRUE THEN\nSTRINGLN inner\nELSE\nSTRINGLN no\nEND_IF\nSTRINGLN outer\nELSE\nSTRINGLN no\nEND_IF\n","inner\nouter\n");
  else if(name=="stage4_nested_true_false") visible("IF 1 THEN\nIF 0 THEN\nSTRINGLN no\nELSE\nSTRINGLN inner\nEND_IF\nELSE\nSTRINGLN no\nEND_IF\n","inner\n");
  else if(name=="stage4_outer_false_nested_inactive") visible("VAR $zero=0\nIF FALSE THEN\nIF 1/$zero THEN\nSTRINGLN no\nELSE IF TRUE THEN\nSTRINGLN no\nELSE\nSTRINGLN no\nEND_IF\nELSE\nSTRINGLN selected\nEND_IF\n","selected\n");
  else if(name=="stage4_multiple_nesting_levels") visible("IF 1 THEN\nIF 2 THEN\nIF 3 THEN\nIF 4 THEN\nSTRINGLN deep\nEND_IF\nELSE\nSTRINGLN no\nEND_IF\nEND_IF\nEND_IF\n","deep\n");
  else if(name=="stage4_exact_nesting_limit") {
    std::string script; for(unsigned i=0;i<DUCKSCRIPT_MAX_BLOCK_DEPTH;++i) script+="IF TRUE THEN\n";
    script+="STRINGLN boundary\n"; for(unsigned i=0;i<DUCKSCRIPT_MAX_BLOCK_DEPTH;++i) script+="END_IF\n";
    visible(script,"boundary\n"); require(DUCKSCRIPT_MAX_BLOCK_DEPTH==8,"reviewed conservative depth is eight");
  } else if(name=="stage4_nesting_limit_plus_one") {
    std::string script="STRINGLN hidden\n"; for(unsigned i=0;i<=DUCKSCRIPT_MAX_BLOCK_DEPTH;++i) script+="IF TRUE THEN\n";
    for(unsigned i=0;i<=DUCKSCRIPT_MAX_BLOCK_DEPTH;++i) script+="END_IF\n";
    invalid(script,"nesting limit",DUCKSCRIPT_MAX_BLOCK_DEPTH+2);
  } else if(name=="stage4_else_if_first_true") visible("VAR $zero=0\nIF TRUE THEN\nSTRINGLN first\nELSE IF 1/$zero THEN\nSTRINGLN no\nELSE\nSTRINGLN no\nEND_IF\n","first\n");
  else if(name=="stage4_else_if_middle_true") visible("IF FALSE THEN\nSTRINGLN no\nELSE IF TRUE THEN\nSTRINGLN middle\nELSE IF TRUE THEN\nSTRINGLN no\nELSE\nSTRINGLN no\nEND_IF\n","middle\n");
  else if(name=="stage4_else_if_final_else") visible("IF FALSE THEN\nSTRINGLN no\nELSE IF FALSE THEN\nSTRINGLN no\nELSE\nSTRINGLN final\nEND_IF\n","final\n");
  else if(name=="stage4_else_if_multiple_entries") visible("VAR $x=3\nIF $x==1 THEN\nSTRINGLN no\nELSE IF $x==2 THEN\nSTRINGLN no\nELSE IF $x==3 THEN\nSTRINGLN third\nELSE IF TRUE THEN\nSTRINGLN no\nEND_IF\n","third\n");
  else if(name=="stage4_nested_else_if_chains") visible("IF FALSE THEN\nSTRINGLN no\nELSE IF TRUE THEN\nIF FALSE THEN\nSTRINGLN no\nELSE IF TRUE THEN\nSTRINGLN nested\nELSE\nSTRINGLN no\nEND_IF\nELSE\nSTRINGLN no\nEND_IF\n","nested\n");
  else if(name=="stage4_no_branch_true_without_else") visible("IF FALSE THEN\nSTRINGLN no\nELSE IF FALSE THEN\nSTRINGLN no\nEND_IF\nSTRINGLN after\n","after\n");
  else if(name=="stage4_selected_assignments_and_later_conditions") visible("VAR $x=1\nIF $x==1 THEN\n$x=($x+4)\nELSE\n$x=99\nEND_IF\nSTRINGLN x=$x\nIF $x==5 THEN\nSTRINGLN later\nEND_IF\n","x=5\nlater\n");
  else if(name=="stage4_inactive_side_effects") {
    mock::reset(); auto locale=keyboard_locale::getLocale();
    mock::file("effects.txt","VAR $x=7\nVAR $zero=0\nIF FALSE THEN\n$x=99\nVAR $hidden=1\nVAR $bad=1/$zero\n"
      "DELAY 60000\nDEFAULT_DELAY 60000\nWAIT 60000\nREPEAT 99\nREPLAY 99\nKEYCODE 2 4\nCTRL ALT DELETE\n"
      "LOCALE de\nLED 200 201 202\nATTACKMODE OFF\nSAVE should-not-exist STRING bad\n"
      "APPEND should-not-exist STRING bad\nREAD missing $read\nSTOP\nSTRINGLN no\nEND_IF\nSTRINGLN x=$x\n");
    require(duckscript::run("effects.txt"),"start inactive effects fixture"); mock::drain();
    require(!duckscript::lastError().length() && mock::text=="x=7\n","inactive effects must not run");
    require(mock::now<1000,"inactive delays/default delay must not schedule");
    require(!mock::files.count("should-not-exist"),"inactive file operations must not mutate storage");
    require(keyboard_locale::getLocale()==locale && attackmode::hidEnabled(),"inactive locale/mode changes must not run");
    require(std::find(mock::colors.begin(),mock::colors.end(),std::array<int,3>{200,201,202})==mock::colors.end(),"inactive LED command must not run"); clean();
  } else if(name=="stage4_required_fixture_spiffs_and_sd") {
    visible(fixture,"outer-true\ninner-true\nx=6\n");visible(fixture,"outer-true\ninner-true\nx=6\n","sd:stage4.txt");
  } else if(name=="stage4_define_conditions_and_protected_keywords") {
    visible("DEFINE #TARGET 5\nDEFINE IF damaged\nDEFINE ELSE damaged\nDEFINE THEN damaged\nDEFINE END_IF damaged\n"
      "VAR $x=5\nIF $x==#TARGET THEN\nSTRINGLN match\nELSE IF TRUE THEN\nSTRINGLN no\nELSE\nSTRINGLN no\nEND_IF\n","match\n");
  } else if(name=="stage4_macro_manufactured_structures_rejected") {
    for(const char *marker:{"IF TRUE THEN","ELSE","ELSE IF TRUE THEN","END_IF","ENDIF","END IF"})
      invalid("DEFINE #CONTROL "+std::string(marker)+"\nSTRINGLN hidden\n#CONTROL\n","cannot create conditional",3);
    invalid("DEFINE #THEN THEN\nSTRINGLN hidden\nIF TRUE #THEN\n","cannot create conditional",3);
    invalid("DEFINE #TAIL TRUE THEN\nSTRINGLN hidden\nIF #TAIL\n","cannot create conditional",3);
  } else if(name=="stage4_compound_hex_boolean_conditions") {
    visible("VAR $x=5\nIF (($x+1)>=6) && TRUE THEN\nSTRINGLN yes\nELSE\nSTRINGLN no\nEND_IF\n"
      "IF (0x10>>2)==4 && ((3|4)&7)==7 THEN\nSTRINGLN hex\nEND_IF\nIF 65535 THEN\nSTRINGLN nonzero\nEND_IF\n","yes\nhex\nnonzero\n");
  } else if(name=="stage4_malformed_expressions_zero_hid") {
    for(const char *expr:{"(5 + )","(5+1","5+1)","1===1","1=1","1 2","!TRUE","0x10000","1/0","1<<16"})
      invalid("STRINGLN hidden\nIF "+std::string(expr)+" THEN\nEND_IF\n","Expression",2);
    invalid("IF FALSE THEN\nIF 1/0 THEN\nEND_IF\nEND_IF\n","zero",2);
  } else if(name=="stage4_undefined_and_text_variables") {
    invalid("STRINGLN hidden\nIF $missing THEN\nEND_IF\n","Undefined",2);
    invalid("VAR $text=\"5\"\nIF $text==5 THEN\nEND_IF\n","Text variable",2);
    invalid("IF FALSE THEN\nIF $missing THEN\nEND_IF\nEND_IF\n","Undefined",2);
    invalid("IF $missing\nEND_IF\n","Undefined",1);
  } else if(name=="stage4_missing_end_if") invalid("STRINGLN MUST-NOT-APPEAR\nVAR $x=1\nIF $x==1 THEN\nSTRINGLN ALSO-NOT\n","Unterminated",3);
  else if(name=="stage4_unexpected_end_if") invalid("STRINGLN hidden\nEND_IF\n","Unmatched",2);
  else if(name=="stage4_duplicate_else") invalid("STRINGLN hidden\nIF TRUE THEN\nELSE\nELSE\nEND_IF\n","duplicate ELSE",4);
  else if(name=="stage4_else_outside_if") {
    invalid("STRINGLN hidden\nELSE\n","Unmatched",2);
    invalid("STRINGLN hidden\nELSE IF TRUE THEN\n","Unmatched",2);
  } else if(name=="stage4_malformed_then_and_else_if") {
    for(const char *line:{"IF ($x==1)","IF 1<2","IF TRUE THEN garbage","IF THEN","IF TRUE THEN THEN",
        "ELSE IF TRUE","ELSE IF THEN","ELSE IF (1+) THEN","ELSE TRUE","ELSEIF TRUE THEN","ELIF TRUE THEN","END_IF extra"})
      invalid("STRINGLN hidden\n"+std::string(line)+"\n","",2);
  } else if(name=="stage4_invalid_branch_ordering") {
    invalid("IF TRUE THEN\nELSE\nELSE IF TRUE THEN\nEND_IF\n","duplicate ELSE",3);
    invalid("ELSE IF TRUE THEN\nEND_IF\n","Unmatched",1);
    invalid("IF TRUE THEN\nELSE IF TRUE THEN\nELSE\nELSE\nEND_IF\n","duplicate ELSE",4);
  } else if(name=="stage4_rem_block_conditional_text") visible("IF TRUE THEN\nREM_BLOCK\nIF fake THEN\nELSE IF fake THEN\nELSE\nEND_IF\nEND_REM\nSTRINGLN literal-safe\nEND_IF\n","literal-safe\n");
  else if(name=="stage4_text_blocks_preserve_literal_modes") {
    for(const char *kind:{"STRING","STRINGLN"}) {
      visible("STRINGLN hidden\nIF TRUE THEN\n"+std::string(kind)+"\nIF fake THEN\nELSE IF fake THEN\nEND_IF\nEND_"+kind+"\nEND_IF\n",kind==std::string("STRING") ? "hidden\nIF fake THENELSE IF fake THENEND_IF" : "hidden\nIF fake THEN\nELSE IF fake THEN\nEND_IF\n");
      invalid("IF TRUE THEN\n"+std::string(kind)+"\nEND_IF\n","Unterminated STRING",2);
    }
  } else if(name=="stage4_stop_active_and_inactive_branches") {
    visible("IF TRUE THEN\nSTRINGLN before\nSTOP\nSTRINGLN no\nELSE\nSTRINGLN no\nEND_IF\nSTRINGLN no\n","before\n");
    visible("IF FALSE THEN\nSTOP\nEND_IF\nSTRINGLN after\n","after\n");
  } else if(name=="stage4_external_cancel_delay_text_and_keys") {
    pending("IF TRUE THEN\nKEYCODE 2 4\nDELAY 10000\nSTRINGLN no\nEND_IF\n",3);
    String before=mock::text; duckscript::stop(); mock::drain();require(mock::text==before,"delay cancellation must suppress later branch commands");clean();
    pending("IF TRUE THEN\nSTRING ABCDEFGHIJKLMNOPQRSTUVWXYZ\nSTRINGLN no\nEND_IF\n",2);
    for(unsigned i=0;i<30 && mock::heldKeys.empty();++i)mock::tick();
    require(!mock::heldKeys.empty(),"reach held runtime key inside active text branch");
    before=mock::text; mock::usbReady=false; duckscript::stop();com::update();
    require(mock::text==before,"text cancellation suppresses pending characters");
    mock::usbReady=true;com::update();mock::drain();clean();
    mock::reset(); require(com::executeNow("KEYCODE 2 4"),"prepare held report");mock::drain();
    // Script ownership clears any previous live-owned state, then cancellation
    // under USB backpressure must leave no runtime-owned held keys.
    mock::file("cancel.txt","IF TRUE THEN\nSTRING abc\nEND_IF\n");require(duckscript::run("cancel.txt"),"start key cancellation fixture");
    mock::usbReady=false;for(unsigned i=0;i<30;++i)mock::tick();duckscript::stop();mock::usbReady=true;mock::drain();clean();
  } else if(name=="stage4_repeat_active_inactive_and_structural_history") {
    visible("STRING a\nIF TRUE THEN\nSTRING b\nELSE\nSTRING no\nEND_IF\nREPEAT 1\n","abb");
    visible("STRING a\nIF FALSE THEN\nSTRING no\nREPEAT 99\nELSE IF FALSE THEN\nSTRING no\nEND_IF\nREPLAY 1\n","aa");
    visible("STRING a\nIF TRUE THEN\nREPEAT 1\nEND_IF\nREPLAY 1\n","aaa");
  } else if(name=="stage4_clean_state_between_runs_and_live_ownership") {
    pending("IF TRUE THEN\nIF TRUE THEN\nDELAY 10000\nEND_IF\nEND_IF\n",3);
    require(!com::executeNow("VAR $x=9") && !com::executeNow("IF TRUE THEN"),"live commands cannot corrupt branch state");
    duckscript::stop(); mock::file("fresh.txt","IF FALSE THEN\nSTRING no\nELSE\nSTRINGLN clean\nEND_IF\n");
    require(duckscript::run("fresh.txt"),"new run starts clean");mock::drain();require(mock::text=="clean\n" && !duckscript::lastError().length(),"branch stack reset per run");clean();
    require(!com::executeNow("IF TRUE THEN"),"live control block cannot execute without script");
  } else if(name=="stage4_runtime_errors_only_in_eligible_conditions") {
    mock::reset(); mock::file("runtime.txt","VAR $zero=0\nSTRINGLN before\nIF FALSE THEN\nSTRING no\nELSE IF (1/$zero) THEN\nSTRING no\nEND_IF\nSTRINGLN after\n");
    require(duckscript::run("runtime.txt"),"runtime-only error reaches execution");mock::drain();
    require(mock::text=="before\n","only earlier eligible output may appear");
    require(duckscript::lastError().indexOf("line 5")>=0 && duckscript::lastError().indexOf("zero")>=0,"runtime condition error retains location");clean();
    mock::reset(); mock::file("skipped.txt","VAR $zero=0\nIF FALSE THEN\nVAR $n=1\nEND_IF\nIF $n==1 THEN\nSTRING no\nEND_IF\n");
    require(duckscript::run("skipped.txt"),"path-dependent symbols are not simulated");mock::drain();
    require(mock::text.length()==0 && duckscript::lastError().indexOf("Undefined")>=0,"missing runtime symbol stops safely");clean();
  } else if(name=="stage4_cooperative_large_inactive_region_and_preflight") {
    std::string script="IF FALSE THEN\n";for(unsigned i=0;i<1500;++i)script+="REM filler\n";script+="STRINGLN no\nEND_IF\nSTRINGLN after\n";
    mock::reset();mock::file("large.txt",script.c_str());require(duckscript::run("large.txt"),"large streaming conditional starts");
    duckscript::update();require(duckscript::running() && mock::text.length()==0,"collection yields before HID");duckscript::stop();clean();
    require(duckscript::run("large.txt"),"restart large script");
    unsigned previous=0, rewinds=0;bool executing=false;
    for(unsigned i=0;i<10000 && duckscript::running();++i) {
      unsigned line=duckscript::currentLine(); if(line<previous && previous>1000) ++rewinds;
      executing=rewinds>=2;previous=line;
      mock::tick();
      if(executing && duckscript::currentLine()>100 && duckscript::currentLine()<1400) break;
    }
    require(executing && duckscript::running() && mock::text.length()==0,"inactive execution region yields after both preflight rewinds");
    unsigned beforeLine=duckscript::currentLine();duckscript::update();
    require(duckscript::currentLine()<=beforeLine+DUCKSCRIPT_LINE_BUDGET,"one update skips at most its configured line budget");
    duckscript::stop();mock::drain();require(mock::text.length()==0,"STOP prevents output after inactive region");clean();
    visible(script,"after\n");
  } else if(name=="stage4_legacy_compatibility_aliases") {
    visible("VAR $word=\"OK\"\nIF $word == OK\nSTRINGLN text\nEND IF\nIF 1\nSTRINGLN one\nENDIF\nIF false\nSTRINGLN no\nELSE\nSTRINGLN false\nEND_IF\nIF 01==1\nSTRINGLN numeric\nEND_IF\n","text\none\nfalse\nnumeric\n");
    visible("VAR $text=\"false\"\nIF $text\nSTRINGLN no\nELSE\nSTRINGLN false-text\nEND_IF\n","false-text\n");
  } else if(name=="stage4_keyword_boundaries_whitespace_and_case") {
    visible(" \tVAR $x=1\n\tif\t($x==1)\tthen\nSTRINGLN yes\n\telse\tif FALSE then\nSTRINGLN no\nelse\nSTRINGLN no\nend\tif\n","yes\n");
    for(const char *line:{"IFF TRUE THEN","ELSEIF TRUE THEN","END_IFfy","IF TRUE THENfoo"})invalid("STRINGLN hidden\n"+std::string(line)+"\n","",2);
  } else if(name=="stage4_mixed_while_nesting") {
    visible("VAR $flag=1\nIF TRUE THEN\nWHILE $flag\n$flag=0\nENDWHILE\nSTRINGLN mixed\nEND_IF\n","mixed\n");
    visible("VAR $flag=1\nWHILE $flag\nIF TRUE THEN\n$flag=0\nSTRINGLN mixed\nEND_IF\nENDWHILE\n","mixed\n");
  } else throw std::runtime_error("unknown test name");
}
int main(int argc,char **argv) {
  if(argc!=2)return 2;
  try { mock::reset();test(argv[1]); std::cout<<"PASS "<<argv[1]<<" ("<<assertions<<" assertions)\n";return 0; }
  catch(const std::exception &e) {std::cerr<<"FAIL "<<argv[1]<<": "<<e.what()<<"\n";return 1;}
}
