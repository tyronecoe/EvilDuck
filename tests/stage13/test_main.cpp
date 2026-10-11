#include "host.h"
#include "FS.h"
#include "duckscript.h"
#include "com.h"
#include "hid_backend.h"
#include "duck_vars.h"
#include "script_preprocessor.h"
#include "settings.h"
#include <iostream>
#include <stdexcept>
#include <string>
#include <fstream>
#include <sstream>

static unsigned assertions = 0;
static void check(bool ok, const char *why) { ++assertions; if (!ok) throw std::runtime_error(why); }
static void start(const std::string &script, const char *source="stage13.txt") {
  mock::reset(); mock::file(source,script.c_str()); check(duckscript::run(source),"start bounded script");
}
static void clean() {
  check(!duckscript::running() && !com::busy(),"finished/cancelled");
  check(!mock::blockingDelays,"no blocking delays");
  check(mock::heldKeys.empty() && !mock::heldModifiers && !hid_backend::hasPersistent(),"no held ownership");
}
static void drain(unsigned limit=150000) { mock::drain(limit); clean(); }
static void visible(const std::string &script, const char *expected, const char *source="stage13.txt") {
  start(script,source); drain();
  if(duckscript::lastError().length())std::cerr<<duckscript::lastError().c_str()<<'\n';
  if(mock::text!=expected)std::cerr<<"actual text ["<<mock::text.c_str()<<"] expected ["<<expected<<"]\n";
  check(!duckscript::lastError().length(),"no runtime/preflight error"); check(mock::text==expected,"exact mocked text/Enter");
}
static void invalid(const std::string &script, const char *message, unsigned line=0) {
  start("STRINGLN MUST-NOT-APPEAR\n"+script,"sd:stage13-bad.txt"); drain();
  if(duckscript::lastError().indexOf(message)<0)std::cerr<<duckscript::lastError().c_str()<<'\n';
  check(duckscript::lastError().indexOf(message)>=0,"specific diagnostic");
  check(duckscript::lastError().indexOf("sd:stage13-bad.txt: Error at line ")>=0,"source diagnostic");
  if(line)check(duckscript::lastError().indexOf("line "+String(line)+":")>=0,"physical line diagnostic");
  check(mock::reports.empty() && mock::text.length()==0,"preflight zero HID");
}
static std::string fixture() {
  return "DEFINE #ON TRUE\nEXTENSION harmless\nVERSION 1.0\nREM_BLOCK DOCUMENTATION\nIF_DEFINED_TRUE #NO\nEND_REM\nFUNCTION SHOW()\nIF_DEFINED_TRUE #ON\nSTRINGLN_PYTHON\n\tIF literal\nEND_STRINGLN\nELSE_DEFINED\nUNSUPPORTED ignored\nEND_IF_DEFINED\nEND_FUNCTION\nEND_EXTENSION\nVAR $n = 0\nWHILE $n < 2\nIF_DEFINED_TRUE #ON\nIF TRUE THEN\nSHOW()\nEND_IF\nEND_IF_DEFINED\n$n = $n + 1\nEND_WHILE\nSTRINGLN done\n";
}
static std::string fileFixture(const char *name) {
  const std::string source=__FILE__;
  std::ifstream in(source.substr(0,source.find_last_of('/'))+"/fixtures/"+name);
  check(bool(in),"fixture file exists"); std::ostringstream out; out<<in.rdbuf(); return out.str();
}
static void test(const std::string &n) {
  if(n.rfind("alias_",0)==0 && ((n[6]>='A' && n[6]<='Z') || (n.substr(6,3)=="ln_" && n[9]>='A' && n[9]<='Z'))) {
    const std::string language=n.substr(6); bool ln=language.rfind("ln_",0)==0;
    const std::string suffix=ln?language.substr(3):language;
    visible(std::string(ln?"STRINGLN_":"STRING_")+suffix+"\n\t  literal  \n\n\tENDIF\n"+(ln?"END_STRINGLN\n":"END_STRING\n"),ln?"  literal  \n\nENDIF\n":"literal  ENDIF");
  } else if(n == "new_keyword_prefixes_rejected") {
    for(const char *statement:{"IF_DEFINED_TRUE_EXTRA #NONE", "REM_BLOCK_DOCUMENTATION", "STRINGLN_PYTHONIC", "LED_GREEN"})
      invalid(std::string(statement)+"\n","Unsupported command");
  } else if(n == "documentation_heading") {
    visible("REM_BLOCK DOCUMENTATION\nIF nonsense\nDEFINE #BAD TRUE\nSTRINGLN hidden\nEND_REM\nSTRINGLN ok\n","ok\n");
  } else if(n == "ordinary_comment_forms") {
    visible("REM ordinary\n// compat\nREM_BLOCK\nEND_IF_DEFINED\nEND_REM\nSTRINGLN ok\n","ok\n");
  } else if(n == "invalid_comment_heading") {
    invalid("REM_BLOCK OTHER\nEND_REM\n","DOCUMENTATION",2);
  } else if(n == "unterminated_documentation") {
    invalid("REM_BLOCK DOCUMENTATION\nEND_IF\n","Unterminated REM_BLOCK",2);
  } else if(n == "alias_cross_terminator") {
    invalid("STRING_PYTHON\nhello\nEND_STRINGLN\n","Mismatched",4);
  } else if(n == "alias_suffixed_terminator") {
    invalid("STRINGLN_PYTHON\nhello\nEND_STRINGLN_PYTHON\n","Unterminated STRINGLN",2);
  } else if(n == "alias_suffixed_end_is_literal_data") {
    visible("STRINGLN_PYTHON\nEND_STRINGLN_PYTHON\nEND_STRINGLN_more\nEND_STRINGLN\n","END_STRINGLN_PYTHON\nEND_STRINGLN_more\n");
  } else if(n == "alias_inline_rejected") {
    invalid("STRING_BASH hello\n","block-only",2);
  } else if(n == "alias_unknown_rejected") {
    invalid("STRING_SQL\n","Unsupported",2);
  } else if(n == "alias_unterminated") {
    invalid("STRINGLN_RUBY\nhello\n","Unterminated STRINGLN",2);
  } else if(n == "alias_define_interpolation_order") {
    visible("DEFINE #WORD ready\nVAR $n = 3\nSTRINGLN_HTML\n\t#WORD $n\nEND_STRINGLN\n","ready 3\n");
  } else if(n == "alias_literal_preprocessing") {
    visible("STRINGLN_JAVASCRIPT\nIF_DEFINED_TRUE #MISSING\nEXTENSION fake\nEND_EXTENSION\nEND_IF_DEFINED\nEND_STRINGLN\n","IF_DEFINED_TRUE #MISSING\nEXTENSION fake\nEND_EXTENSION\nEND_IF_DEFINED\n");
  } else if(n == "alias_empty_block") {
    visible("STRINGLN_HTML\nEND_STRINGLN\nSTRING_BASH\nEND_STRING\n","");
  } else if(n == "alias_bom_crlf_no_newline") {
    visible("\xEF\xBB\xBFSTRINGLN_BATCH\r\n\tready\r\nEND_STRINGLN","ready\n","sd:stage13.txt");
  } else if(n == "alias_lowercase_tabs") {
    visible(" \tstringln_python \t\n\thello \t\n end_stringln\t\n","hello \t\n");
  } else if(n == "extension_functions") {
    visible("EXTENSION test\nVERSION 1.0\nFUNCTION SAY()\nSTRINGLN ok\nEND_FUNCTION\nEND_EXTENSION\nSAY()\nSAY()\n","ok\nok\n");
  } else if(n == "extension_sequential_body") {
    visible("EXTENSION test\nVERSION 1.0.2\nSTRINGLN body\nEND_EXTENSION\nSTRINGLN after\n","body\nafter\n");
  } else if(n == "extension_version_optional") {
    visible("EXTENSION test\nREM VERSION 1.0\nEND_EXTENSION\nSTRINGLN ok\n","ok\n");
  } else if(n == "extension_duplicate") {
    invalid("EXTENSION test\nEND_EXTENSION\nEXTENSION test\nEND_EXTENSION\n","Duplicate EXTENSION",4);
  } else if(n == "extension_nested") {
    invalid("EXTENSION test\nEXTENSION inner\nEND_EXTENSION\nEND_EXTENSION\n","Nested EXTENSION",3);
  } else if(n == "extension_invalid_name") {
    invalid("EXTENSION bad-name\nEND_EXTENSION\n","Invalid EXTENSION",2);
  } else if(n == "extension_missing_end") {
    invalid("EXTENSION test\nVERSION 1.0\n","Unterminated EXTENSION",2);
  } else if(n == "extension_unmatched_end") {
    invalid("END_EXTENSION\n","Mismatched EXTENSION",2);
  } else if(n == "extension_end_arguments") {
    invalid("EXTENSION test\nEND_EXTENSION extra\n","takes no arguments",3);
  } else if(n == "extension_version_duplicate") {
    invalid("EXTENSION test\nVERSION 1.0\nVERSION 1.1\nEND_EXTENSION\n","Duplicate or misplaced VERSION",4);
  } else if(n == "extension_version_misplaced") {
    invalid("EXTENSION test\nVAR $x = 1\nVERSION 1.0\nEND_EXTENSION\n","misplaced VERSION",4);
  } else if(n == "extension_version_outside") {
    invalid("VERSION 1.0\n","extension header",2);
  } else if(n == "extension_version_malformed") {
    invalid("EXTENSION test\nVERSION 1..0\nEND_EXTENSION\n","dotted decimal",3);
  } else if(n == "extension_control_boundary") {
    invalid("EXTENSION test\nIF TRUE THEN\nEND_EXTENSION\nEND_IF\n","Mismatched extension",4);
  } else if(n == "extension_function_boundary") {
    invalid("EXTENSION test\nFUNCTION TEST()\nEND_EXTENSION\nEND_FUNCTION\n","Mismatched extension",4);
  } else if(n == "extension_not_top_level") {
    invalid("IF TRUE THEN\nEXTENSION test\nEND_EXTENSION\nEND_IF\n","top level",3);
  } else if(n == "extension_exact_limit") {
    std::string s; for(unsigned i=0;i<DUCKSCRIPT_MAX_EXTENSIONS;++i)s+="EXTENSION E"+std::to_string(i)+"\nEND_EXTENSION\n";
    visible(s+"STRINGLN ok\n","ok\n");
  } else if(n == "extension_limit_plus_one") {
    std::string s; for(unsigned i=0;i<=DUCKSCRIPT_MAX_EXTENSIONS;++i)s+="EXTENSION E"+std::to_string(i)+"\nEND_EXTENSION\n";
    invalid(s,"Extension table exhausted");
  } else if(n == "preprocess_true_false_else") {
    visible("DEFINE #A TRUE\nDEFINE #B FALSE\nIF_DEFINED_TRUE #A\nSTRINGLN A\nELSE_DEFINED\nSTRINGLN wrong\nEND_IF_DEFINED\nIF_DEFINED_TRUE #B\nUNKNOWN\nELSE_DEFINED\nSTRINGLN B\nEND_IF_DEFINED\n","A\nB\n");
  } else if(n == "preprocess_not_true_undefined") {
    visible("IF_NOT_DEFINED_TRUE #MISSING\nSTRINGLN missing\nEND_IF_DEFINED\nIF_DEFINED_TRUE #MISSING\nUNKNOWN\nEND_IF_DEFINED\n","missing\n");
  } else if(n == "preprocess_bare_label") {
    visible("DEFINE FLAG TRUE\nIF_DEFINED_TRUE FLAG\nSTRINGLN yes\nEND_IF_DEFINED\n","yes\n");
  } else if(n == "preprocess_order_forward_definition") {
    visible("IF_DEFINED_TRUE #FLAG\nSTRINGLN wrong\nEND_IF_DEFINED\nDEFINE #FLAG TRUE\nIF_DEFINED_TRUE #FLAG\nSTRINGLN yes\nEND_IF_DEFINED\n","yes\n");
  } else if(n == "preprocess_excluded_define_inert") {
    visible("IF_DEFINED_TRUE #MISSING\nDEFINE #FLAG TRUE\nEND_IF_DEFINED\nIF_NOT_DEFINED_TRUE #FLAG\nSTRINGLN yes\nEND_IF_DEFINED\n","yes\n");
  } else if(n == "preprocess_included_define_global_expansion") {
    visible("STRINGLN #WORD\nIF_NOT_DEFINED_TRUE #MISSING\nDEFINE #WORD ready\nEND_IF_DEFINED\n","ready\n");
  } else if(n == "preprocess_text_flag_ambiguous_rejected") {
    invalid("DEFINE #FLAG yes\nIF_DEFINED_TRUE #FLAG\nEND_IF_DEFINED\n","literal TRUE or FALSE",3);
  } else if(n == "preprocess_recursive_flag_rejected") {
    invalid("DEFINE #A TRUE\nDEFINE #FLAG #A\nIF_DEFINED_TRUE #FLAG\nEND_IF_DEFINED\n","literal TRUE or FALSE",4);
  } else if(n == "preprocess_invalid_label") {
    invalid("IF_DEFINED_TRUE #BAD-NAME\nEND_IF_DEFINED\n","one DEFINE label",2);
  } else if(n == "preprocess_extra_condition_tokens") {
    invalid("IF_DEFINED_TRUE #FLAG THEN\nEND_IF_DEFINED\n","one DEFINE label",2);
  } else if(n == "preprocess_missing_end") {
    invalid("IF_NOT_DEFINED_TRUE #MISSING\nSTRINGLN hidden\n","Unterminated conditional preprocessing",2);
  } else if(n == "preprocess_unmatched_end") {
    invalid("END_IF_DEFINED\n","Unmatched preprocessing",2);
  } else if(n == "preprocess_unmatched_else") {
    invalid("ELSE_DEFINED\n","Unmatched preprocessing",2);
  } else if(n == "preprocess_duplicate_else") {
    invalid("IF_DEFINED_TRUE #MISSING\nELSE_DEFINED\nELSE_DEFINED\nEND_IF_DEFINED\n","Duplicate ELSE_DEFINED",4);
  } else if(n == "preprocess_marker_arguments") {
    invalid("IF_DEFINED_TRUE #MISSING\nEND_IF_DEFINED extra\n","takes no arguments",3);
  } else if(n == "preprocess_nested_parent_exclusion") {
    visible("DEFINE #BAD arbitrary\nIF_DEFINED_TRUE #MISSING\nIF_DEFINED_TRUE #BAD\nSTRINGLN wrong\nELSE_DEFINED\nUNKNOWN\nEND_IF_DEFINED\nELSE_DEFINED\nSTRINGLN ok\nEND_IF_DEFINED\n","ok\n");
  } else if(n == "preprocess_exact_depth") {
    std::string s; for(unsigned i=0;i<DUCKSCRIPT_MAX_PREPROCESS_DEPTH;++i)s+="IF_NOT_DEFINED_TRUE #NONE\n";
    s+="STRINGLN yes\n";for(unsigned i=0;i<DUCKSCRIPT_MAX_PREPROCESS_DEPTH;++i)s+="END_IF_DEFINED\n";
    visible(s,"yes\n");
  } else if(n == "preprocess_depth_plus_one") {
    std::string s;for(unsigned i=0;i<=DUCKSCRIPT_MAX_PREPROCESS_DEPTH;++i)s+="IF_DEFINED_TRUE #NONE\n";
    invalid(s,"Preprocessing nesting limit",DUCKSCRIPT_MAX_PREPROCESS_DEPTH+2);
  } else if(n == "preprocess_excluded_runtime_not_validated") {
    visible("IF_DEFINED_TRUE #NONE\nWHILE garbage !\nIF ??\nFUNCTION bad parameters\nUNSUPPORTED host_command\nVAR $oops = (4 + )\nSAVE nonsense\nHOLD invalid\nEND_IF_DEFINED\nSTRINGLN ok\n","ok\n");
  } else if(n == "preprocess_excluded_function_not_inventoried") {
    invalid("IF_DEFINED_TRUE #NONE\nFUNCTION HIDDEN()\nEND_FUNCTION\nEND_IF_DEFINED\nHIDDEN()\n","Undefined function");
  } else if(n == "preprocess_excluded_variable_not_inventoried") {
    invalid("IF_DEFINED_TRUE #NONE\nVAR $x = 1\nEND_IF_DEFINED\nVAR $y = $x\n","Undefined numeric variable");
  } else if(n == "preprocess_excluded_storage_hid_inert") {
    visible("IF_DEFINED_TRUE #NONE\nHOLD CTRL\nLED_R\nATTACKMODE OFF\nSAVE spiffs:output.txt STRING hidden\nSTOP\nEND_IF_DEFINED\nSTRINGLN ok\n","ok\n");
    check(mock::files.find("output.txt")==mock::files.end(),"excluded storage not written");
  } else if(n == "preprocess_comment_directives_literal") {
    visible("REM_BLOCK DOCUMENTATION\nELSE_DEFINED\nDEFINE #FLAG TRUE\nEND_IF_DEFINED\nEND_REM\nIF_NOT_DEFINED_TRUE #FLAG\nSTRINGLN ok\nEND_IF_DEFINED\n","ok\n");
  } else if(n == "preprocess_excluded_text_structural_error") {
    invalid("IF_DEFINED_TRUE #NONE\nSTRINGLN_PYTHON\nEND_STRING\nEND_IF_DEFINED\n","Mismatched",4);
  } else if(n == "preprocess_excluded_comment_missing_end") {
    invalid("IF_DEFINED_TRUE #NONE\nREM_BLOCK DOCUMENTATION\nEND_IF_DEFINED\n","Unterminated REM_BLOCK",3);
  } else if(n == "preprocess_wrapper_crossing") {
    invalid("IF_NOT_DEFINED_TRUE #NONE\nEXTENSION test\nEND_IF_DEFINED\nEND_EXTENSION\n","crosses EXTENSION",4);
  } else if(n == "preprocess_wrapper_end_crossing") {
    invalid("EXTENSION test\nIF_NOT_DEFINED_TRUE #NONE\nEND_EXTENSION\nEND_IF_DEFINED\n","Mismatched EXTENSION",4);
  } else if(n == "macro_cannot_create_wrapper") {
    invalid("DEFINE #WRAP EXTENSION test\n#WRAP\nEND_EXTENSION\n","Mismatched EXTENSION");
  } else if(n == "macro_cannot_create_preprocessor") {
    invalid("DEFINE #CONTROL IF_NOT_DEFINED_TRUE #NONE\n#CONTROL\n","Unsupported command");
  } else if(n == "macro_cannot_create_alias") {
    invalid("DEFINE #BLOCK STRINGLN_PYTHON\n#BLOCK\n","cannot create DEFINE or comment/text");
  } else if(n == "checked_in_source_fixture") {
    visible(fileFixture("source-compatibility.duck"),"literal IF/WHILE text\n");
  } else if(n == "checked_in_exclusion_fixture") {
    visible(fileFixture("excluded-source.duck"),"included-only\n","sd:stage13.txt");
  } else if(n == "integration_spiffs") {
    visible(fixture(),"IF literal\nIF literal\ndone\n");
  } else if(n == "integration_sd") {
    visible(fixture(),"IF literal\nIF literal\ndone\n","sd:stage13.txt");
  } else if(n == "frozen_flags_after_function_seek") {
    visible("FUNCTION SHOW()\nIF_NOT_DEFINED_TRUE #LATE\nSTRINGLN yes\nEND_IF_DEFINED\nEND_FUNCTION\nDEFINE #LATE TRUE\nSHOW()\nSHOW()\n","yes\nyes\n");
  } else if(n == "frozen_flags_after_loop_seek") {
    visible("VAR $n = 0\nWHILE $n < 2\nIF_NOT_DEFINED_TRUE #LATE\nSTRINGLN yes\nEND_IF_DEFINED\n$n = $n + 1\nEND_WHILE\nDEFINE #LATE TRUE\n","yes\nyes\n");
  } else if(n == "selected_structure_validated_before_hid") {
    invalid("IF_NOT_DEFINED_TRUE #NONE\nIF TRUE THEN\nEND_IF_DEFINED\n","Unterminated IF/WHILE");
  } else if(n == "preprocess_repeat_history") {
    visible("STRINGLN ok\nIF_DEFINED_TRUE #NONE\nSTRINGLN hidden\nEND_IF_DEFINED\nEXTENSION empty\nVERSION 1.0\nEND_EXTENSION\nREPEAT 1\n","ok\nok\n");
  } else if(n == "maximum_line_inside_exclusion") {
    visible("IF_DEFINED_TRUE #NONE\n"+std::string(DUCKSCRIPT_MAX_LINE_LEN,'z')+"\nEND_IF_DEFINED\nSTRINGLN ok\n","ok\n");
  } else if(n == "overlong_line_inside_exclusion") {
    invalid("IF_DEFINED_TRUE #NONE\n"+std::string(DUCKSCRIPT_MAX_LINE_LEN+1,'z')+"\nEND_IF_DEFINED\n","line length limit",3);
  } else if(n == "source_limit_inside_exclusion") {
    std::string s="IF_DEFINED_TRUE #NONE\n";while(s.size()<=DUCKSCRIPT_MAX_SOURCE_BYTES)s+=std::string(500,'z')+"\n";
    mock::reset(); mock::file("stage13.txt",s.c_str()); check(!duckscript::run("stage13.txt"),"oversized source rejected at open"); check(duckscript::lastError().indexOf("source byte limit")>=0,"bounded source diagnostic"); check(mock::reports.empty(),"zero HID for source bound"); clean();
  } else if(n == "exact_line_bitmap_boundary") {
    std::string s="IF_DEFINED_TRUE #NONE\n";s.append(DUCKSCRIPT_MAX_SOURCE_LINES-3,'\n');s+="END_IF_DEFINED\nSTRINGLN last\n";
    visible(s,"last\n");
  } else if(n == "bitmap_boundary_plus_one") {
    std::string s(DUCKSCRIPT_MAX_SOURCE_LINES,'\n');s+="STRINGLN hidden\n";
    invalid(s,"source line limit");
  } else if(n == "excluded_read_fault") {
    start("IF_DEFINED_TRUE #NONE\n"+std::string(400,'z')+"\nEND_IF_DEFINED\nSTRINGLN after\n","sd:stage13.txt");
    mock::failReadAt=128;drain();check(duckscript::lastError().indexOf("read")>=0,"read error not EOF");check(mock::reports.empty(),"zero HID on first-pass error");
  } else if(n == "preprocessing_rewind_fault") {
    start("STRINGLN hidden\n"); mock::failSeekAt=0;drain();check(duckscript::lastError().indexOf("seek")>=0,"rewind error");check(mock::reports.empty(),"zero HID on rewind error");
  } else if(n == "cancellation_during_preprocessing") {
    start("IF_DEFINED_TRUE #NONE\n"+std::string(400,'z')+"\nEND_IF_DEFINED\nSTRINGLN after\n");
    mock::tick(); check(duckscript::running(),"first pass yields");check(mock::bytesRead<=320,"bounded read-ahead plus budget");
    duckscript::stop();drain();check(mock::reports.empty(),"cancel before HID");
  } else if(n == "cancellation_during_alias_typing") {
    start("HOLD CTRL\nSTRINGLN_HTML\n"+std::string(500,'a')+"\nEND_STRINGLN\nSTRINGLN after\n");
    for(unsigned i=0;i<10000 && mock::reports.size()<24;++i)mock::tick();
    check(mock::reports.size()>=24 && duckscript::running(),"typing started");duckscript::stop();auto size=mock::text.length();drain();check(mock::text.length()==size,"no queued output after STOP");
  } else if(n == "alias_usb_backpressure") {
    start("STRINGLN_HTML\nready\nEND_STRINGLN\n");mock::usbAccept=false;for(unsigned i=0;i<500;++i)mock::tick();
    check(mock::reports.empty() && duckscript::running(),"transport refusal keeps pending bounded work");mock::usbAccept=true;drain();check(mock::text=="ready\n","retry exact output");
  } else if(n == "large_streamed_alias") {
    std::string s="STRING_BASH\n";for(unsigned i=0;i<400;++i)s+=std::string(500,'a')+"\n";s+="END_STRING\n";
    start(s);for(unsigned i=0;i<10000 && mock::text.length()<100;++i)mock::tick();check(mock::text.length()>=100,"large source streams after bounded preflight");
    duckscript::stop();drain();check(mock::text.length()<200000,"does not buffer/type whole block before cancellation");
  } else if(n == "canonical_led_colors_and_override") {
    visible("LED_R\nLED_G\nLED_OFF\n","");
    bool red=false,green=false;for(auto c:mock::colors){red|=c==std::array<int,3>{255,0,0};green|=c==std::array<int,3>{0,255,0};}
    check(red && green && mock::colors.back()==std::array<int,3>{0,0,0},"RGB red/green/off; default idle suppressed");
  } else if(n == "canonical_led_arguments_rejected") {
    invalid("LED_R 1\n","take no arguments",2);
  } else if(n == "canonical_led_inactive_branch") {
    visible("IF FALSE THEN\nLED_R\nEND_IF\nSTRINGLN ok\n","ok\n");check(!com::statusLedOverridden(),"inactive command cannot set override");
  } else if(n == "canonical_led_error_priority") {
    start("LED_G\nVAR $x = 1 / 0\n");drain();check(duckscript::lastError().indexOf("zero")>=0,"runtime arithmetic error");
    check(mock::colors.back()==std::array<int,3>{50,0,0},"existing red error priority");
  } else if(n == "canonical_led_new_script_defaults") {
    visible("LED_OFF\n","");check(com::statusLedOverridden(),"override survives EOF");visible("STRINGLN new\n","new\n");check(!com::statusLedOverridden(),"new script resets override");
  } else if(n == "canonical_led_open_error_priority") {
    visible("LED_OFF\n","");check(!duckscript::run("missing-stage13.txt"),"missing script rejected");
    check(mock::colors.back()==std::array<int,3>{50,0,0},"open error overrides explicit LED-off");
  } else if(n == "new_command_function_names_reserved") {
    for(const char *name:{"LED_G", "EXTENSION", "END_EXTENSION", "VERSION", "IF_DEFINED_TRUE", "STRINGLN_PYTHON"})
      invalid(std::string("FUNCTION ")+name+"()\nEND_FUNCTION\n","collides with");
  } else if(n == "live_metadata_rejected") {
    mock::reset();check(!com::executeNow("EXTENSION test"),"live wrappers rejected");check(mock::reports.empty(),"no metadata HID");
  } else if(n == "excluded_duplicate_constants_ignored") {
    visible("DEFINE #WORD ready\nIF_DEFINED_TRUE #NONE\nDEFINE #WORD ignored\nEND_IF_DEFINED\nSTRINGLN #WORD\n","ready\n");
  } else if(n == "included_duplicate_constants_rejected") {
    invalid("DEFINE #WORD ready\nIF_NOT_DEFINED_TRUE #NONE\nDEFINE #WORD ignored\nEND_IF_DEFINED\n","Duplicate DEFINE label",4);
  } else if(n == "excluded_extension_names_do_not_exhaust") {
    std::string s="IF_DEFINED_TRUE #NONE\n";
    for(unsigned i=0;i<DUCKSCRIPT_MAX_EXTENSIONS+2;++i)s+="EXTENSION same\nVERSION 1.0\nEND_EXTENSION\n";
    visible(s+"END_IF_DEFINED\nEXTENSION same\nVERSION 1.0\nSTRINGLN yes\nEND_EXTENSION\n","yes\n");
  } else if(n == "macro_cannot_create_version") {
    invalid("DEFINE #META VERSION 1.0\nEXTENSION test\n#META\nEND_EXTENSION\n","cannot create extension metadata");
  } else if(n == "macro_cannot_create_wrapper_direct") {
    invalid("DEFINE #META EXTENSION test\n#META\n","cannot create extension metadata");
  } else if(n == "constant_text_cannot_escape_alias") {
    visible("DEFINE #END END_STRINGLN\nSTRINGLN_HTML\n#END\nEND_STRINGLN\n","END_STRINGLN\n");
  } else if(n == "comment_define_not_collected_in_alias") {
    visible("STRINGLN_PYTHON\nDEFINE #WORD ready\nEND_STRINGLN\nSTRINGLN #WORD\n","DEFINE #WORD ready\n#WORD\n");
  } else if(n == "combined_preprocess_runtime_depth") {
    std::string s;for(unsigned i=0;i<DUCKSCRIPT_MAX_PREPROCESS_DEPTH;++i)s+="IF_NOT_DEFINED_TRUE #NONE\n";
    for(unsigned i=0;i<DUCKSCRIPT_MAX_BLOCK_DEPTH;++i)s+="IF TRUE THEN\n";
    s+="STRINGLN ok\n";for(unsigned i=0;i<DUCKSCRIPT_MAX_BLOCK_DEPTH;++i)s+="END_IF\n";
    for(unsigned i=0;i<DUCKSCRIPT_MAX_PREPROCESS_DEPTH;++i)s+="END_IF_DEFINED\n";
    visible(s,"ok\n");
  } else if(n == "preprocess_no_expansion_of_flag_name") {
    visible("DEFINE #FLAG TRUE\nIF_DEFINED_TRUE #FLAG\nSTRINGLN ok\nEND_IF_DEFINED\n","ok\n");
  } else if(n == "preprocess_define_whitespace_literal_boolean") {
    visible("DEFINE #FLAG  TRUE \nIF_DEFINED_TRUE\t#FLAG\nSTRINGLN ok\nEND_IF_DEFINED\n","ok\n");
  } else if(n == "canonical_led_disabled_setting") {
    start("LED_R\nLED_G\nLED_OFF\n");settings::setDisableLed(true);mock::colors.clear();drain();check(mock::colors.empty(),"disabled setting suppresses canonical RGB output");
  } else if(n == "canonical_led_stop_retains_override") {
    visible("LED_R\nSTOP_PAYLOAD\nLED_G\n","");check(mock::colors.back()==std::array<int,3>{255,0,0},"STOP retains explicit LED and prevents queued command");
  } else if(n == "legacy_rgb_behavior_retained") {
    start("LED 12 34 56\n");settings::setLedColor(0x010203);drain();
    bool rgb=false;for(auto c:mock::colors)rgb|=c==std::array<int,3>{12,34,56};
    check(rgb && mock::colors.back()==std::array<int,3>{1,2,3},"legacy RGB keeps default idle behavior");
  } else if(n == "function_seek_fault_after_preprocessing") {
    std::string s="FUNCTION SHOW()\nIF_NOT_DEFINED_TRUE #NONE\nSTRINGLN text\nEND_IF_DEFINED\nEND_FUNCTION\nHOLD CTRL\nSHOW()\n";
    start(s,"sd:stage13.txt");for(unsigned i=0;i<3000 && !hid_backend::hasPersistent();++i)mock::tick();
    check(hid_backend::hasPersistent(),"active runtime reached");mock::failSeekAt=std::string("FUNCTION SHOW()\n").size();drain();
    check(duckscript::lastError().indexOf("seek")>=0,"failed call seek safely stops and releases");
  } else if(n == "preflight_cancellation_live_isolation") {
    start("IF_DEFINED_TRUE #NONE\n"+std::string(400,'z')+"\nEND_IF_DEFINED\nSTRINGLN after\n");mock::tick();
    check(!com::executeNow("LED_R"),"script owns preprocessing phase");check(!com::statusLedOverridden(),"rejected live command does not alter status");
    duckscript::stop();drain();check(mock::reports.empty(),"cancelled preflight no output");
  } else if(n == "run_state_inclusion_isolation") {
    visible("IF_DEFINED_TRUE #MISSING\nSTRINGLN hidden\nEND_IF_DEFINED\n","");visible("STRINGLN new\n","new\n");
  } else throw std::runtime_error("unknown Stage13 test");
}
int main(int argc,char **argv) {
  if(argc!=2)return 2;
  try {test(argv[1]);std::cout<<"PASS "<<argv[1]<<" ("<<assertions<<" assertions)\n";return 0;}
  catch(const std::exception &e){std::cerr<<"FAIL "<<argv[1]<<": "<<e.what()<<'\n';return 1;}
}
