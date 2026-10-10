#include "host.h"
#include "FS.h"
#include "com.h"
#include "duckscript.h"
#include "duck_expr.h"
#include "duck_vars.h"
#include "duck_constants.h"
#include "script_parser.h"
#include <iostream>
#include <stdexcept>
#include <string>

static unsigned assertions = 0;
static void require(bool condition, const char *message) {
  ++assertions;
  if (!condition) throw std::runtime_error(message);
}
static void value(const char *source, uint16_t expected) {
  uint16_t actual = 123;
  duck_expr::Error error;
  require(duck_expr::evaluate(source, strlen(source), actual, error, duck_vars::resolve), "expression must evaluate");
  require(actual == expected, "expression result must match expected uint16 value");
  require(!error.message, "successful expression must not report a diagnostic");
}
static void bad(const std::string &source, const char *expected) {
  uint16_t actual = 123;
  duck_expr::Error error;
  require(!duck_expr::evaluate(source.c_str(), source.size(), actual, error, duck_vars::resolve), "invalid expression must fail");
  require(error.message && std::string(error.message).find(expected) != std::string::npos, "expression error must identify failure");
  require(error.column > 0 && actual == 123, "failure must identify a column and leave result unchanged");
}
static void clean() {
  require(!duckscript::running() && !com::busy(), "execution must finish or cancel");
  require(mock::blockingDelays == 0, "scheduler must remain nonblocking");
  require(mock::heldKeys.empty() && !mock::heldModifiers, "runtime keys must be released");
}
static void visible(const std::string &script, const char *expected, const char *file="stage3.txt") {
  mock::reset(); mock::file(file, script.c_str());
  require(duckscript::run(file), "fixture must begin cooperative collection/preflight"); mock::drain();
  require(!duckscript::lastError().length(), "valid script must complete without error");
  require(mock::text == expected, "harmless mocked visible output must match exactly"); clean();
}
static void invalid(const std::string &script, const char *message, unsigned line=2) {
  mock::reset(); mock::file("sd:invalid-stage3.txt", script.c_str());
  require(duckscript::run("sd:invalid-stage3.txt"), "invalid script must reach cooperative preflight"); mock::drain();
  String error = duckscript::lastError();
  require(error.indexOf(message) >= 0, "diagnostic must identify expected syntax/type/boundary error");
  require(error.indexOf("sd:invalid-stage3.txt") >= 0 && error.indexOf("line " + String(line) + ":") >= 0,
          "diagnostic must contain source volume, filename and line");
  require(mock::presses.empty() && !mock::text.length(), "preflight error must prevent ALL HID output"); clean();
}
static void live(const char *line) {
  require(com::executeNow(line), "valid live statement must be accepted"); mock::drain();
}

struct OperatorCase { const char *name, *source; uint16_t expected; };
static const OperatorCase operators[] = {
 {"stage3_addition", "7 + 5", 12}, {"stage3_subtraction", "7 - 5", 2},
 {"stage3_multiplication", "7 * 5", 35}, {"stage3_division", "17 / 5", 3},
 {"stage3_modulo", "17 % 5", 2}, {"stage3_exponentiation", "2 ^ 6", 64},
 {"stage3_equality", "7 == 7", 1}, {"stage3_inequality", "7 != 5", 1},
 {"stage3_less_than", "5 < 7", 1}, {"stage3_greater_than", "7 > 5", 1},
 {"stage3_less_or_equal", "7 <= 7", 1}, {"stage3_greater_or_equal", "7 >= 7", 1},
 {"stage3_logical_and", "2 && 3", 1}, {"stage3_logical_or", "0 || 3", 1},
 {"stage3_bitwise_and", "0xAC05 & 0xFF00", 0xAC00},
 {"stage3_bitwise_or", "0xAC00 | 5", 0xAC05},
 {"stage3_left_shift", "1 << 15", 32768}, {"stage3_right_shift", "0xAC05 >> 8", 172},
};

static void test(const String &name) {
  mock::reset();
  for (const auto &entry : operators) if (name == entry.name) { value(entry.source, entry.expected); return; }
  if (name == "stage3_precedence_and_grouping") {
    value("2+3*4",14); value("(2+3)*4",20); value("2^3^2",512); value("(2^3)^2",64);
    value("10-3-2",5); value("24/3/2",4); value("1<<1+2",8); value("16>>1>>1",4);
    value("1<<2 < 5",1); value("1<2==1",1); value("1 & 2==0",0); value("(1&2)==0",1);
    value("3|4&1",3); value("1|0 && 0",0); value("1||0&&0",1); value("2*3^2",18);
    value("((100*13)+(42-5))",1337); value("((0x05AC>>8)&0x00FF)|((0x05AC<<8)&0xFF00)",0xAC05);
  } else if (name == "stage3_literals_booleans_and_whitespace") {
    value("0",0); value("65535",65535); value("0xffff",65535); value("0X00AC",172); value("0010",10);
    value("TRUE",1); value("FALSE",0); value("TRUE+TRUE",2); value("FALSE*65535",0);
    value("TRUE == 1",1); value("FALSE == 0",1); value("TRUE < 2",1);
    value("0&&3",0); value("0||0",0); value("2&&65535",1); value("FALSE||TRUE",1);
    value(" \t( 2\t+ 3 ) \t*\t4 ",20); value("(( (5)))",5);
  } else if (name == "stage3_arithmetic_boundaries") {
    value("65535+1",0); value("0-1",65535); value("65535*65535",1); value("256^2",0);
    value("0^0",1); value("1^65535",1); value("65535^65535",65535); value("65535<<15",32768);
    value("65535/2",32767); value("65535%2",1); value("(0-1)>0",1); value("1<<0",1); value("1>>0",1);
    bad("1/0","zero"); bad("1%0","zero"); bad("1<<16","Shift"); bad("1>>65535","Shift");
    bad("FALSE && (1/0)","zero"); bad("TRUE || (1/0)","zero");
  } else if (name == "stage3_invalid_literals_and_unsupported_operators") {
    bad("65536","exceeds"); bad("0x10000","exceeds"); bad("999999999999999999","exceeds");
    bad("0x","hexadecimal"); bad("0xG1","numeric literal"); bad("1abc","numeric literal");
    bad("0b10","numeric literal"); bad("12_3","numeric literal"); bad("1.5","Unexpected");
    bad("-1","Unsupported"); bad("+1","Unsupported"); bad("!TRUE","Unsupported"); bad("~1","Unsupported");
    bad("2 ** 3","Unsupported"); bad("1 XOR 2","Unexpected"); bad("TRUE AND FALSE","Unexpected");
    bad("true","Expected number"); bad("FALSE OR TRUE","Unexpected");
  } else if (name == "stage3_malformed_expressions_and_limits") {
    bad("","operand"); bad("(5 + )","operand"); bad("(5+1","parenthesis"); bad("5+1)","parenthesis");
    bad("()","operand"); bad("1 2","Unexpected"); bad("1=2","Unexpected"); bad("1===2","Unsupported");
    bad("5+","operand"); bad("#MISSING","constant");
    std::string maximum="1"+std::string(DUCKSCRIPT_MAX_EXPR_BYTES-1,' ');
    value(maximum.c_str(),1); bad(maximum+" ","byte limit");
    std::string nested(DUCKSCRIPT_MAX_EXPR_DEPTH,'('); nested += "1"; nested += std::string(DUCKSCRIPT_MAX_EXPR_DEPTH,')');
    value(nested.c_str(),1); bad("("+nested+")","nesting limit");
    std::string chain="1"; for (unsigned i=1;i<64;++i) chain+="+1";
    value(chain.c_str(),64); bad(chain+"+1","token limit");
    std::string powers="1"; for (unsigned i=0;i<DUCKSCRIPT_MAX_EXPR_DEPTH;++i) powers+="^1";
    value(powers.c_str(),1); bad(powers+"^1","nesting limit");
  } else if (name == "stage3_numeric_declarations_assignment_and_no_hid") {
    mock::file("numeric.txt","VAR $x = 2\n$x=($x+3)\n$x = ($x*4)\nVAR $yes = ($x == 20)\nVAR $wrap = (0-1)\nVAR $x = ($x+1)\nDELAY 1000\n");
    require(duckscript::run("numeric.txt"),"numeric fixture must start");
    for (unsigned i=0;i<500 && !(duckscript::currentLine()==7 && com::busy());++i) mock::tick();
    uint16_t actual;
    require(duck_vars::getNumeric("$x",actual) && actual==21,"inspect numeric assignment/redeclaration value directly");
    require(duck_vars::getNumeric("$yes",actual) && actual==1,"inspect canonical boolean representation directly");
    require(duck_vars::getNumeric("$wrap",actual) && actual==65535,"inspect underflow value directly");
    require(mock::presses.empty() && !mock::text.length(),"numeric fixture must produce zero HID");
    duckscript::stop(); require(!duck_vars::getNumeric("$x",actual),"STOP must discard run variables"); clean();
  } else if (name == "stage3_required_fixture_spiffs_and_sd") {
    const char *script="DEFINE #COUNT 2\nDEFINE #WORD ready\nVAR $n = (#COUNT ^ 3)\n$n = ($n + 1)\nSTRINGLN #WORD\nSTRINGLN n=$n\n";
    visible(script,"ready\nn=9\n"); visible(script,"ready\nn=9\n","sd:stage3.txt");
  } else if (name == "stage3_variable_references_types_and_atomic_failure") {
    live("VAR $n = 7"); value("$n*3",21); value("$n==$n",1); bad("$missing","Undefined");
    live("VAR $text = \"7\""); bad("$text+1","Text variable");
    require(!com::executeNow("$n = (1/0)"),"failed assignment must reject");
    uint16_t actual;
    require(duck_vars::getNumeric("$n",actual) && actual==7,"failed assignment must not change value");
    require(!com::executeNow("$missing = 1"),"assignment must not implicitly declare");
    require(!com::executeNow("VAR $n = \"text\""),"type change must reject");
    require(duck_vars::getNumeric("$n",actual) && actual==7,"type failure must leave value intact");
    live("$n = ($n+1)"); require(duck_vars::getNumeric("$n",actual) && actual==8,"live assignment must use evaluator");
    clean();
  } else if (name == "stage3_text_compatibility_alias_and_read") {
    visible("VAR $n = 5\nVAR $text = \"ready\"\nDEFINE $other = \"OK\"\n$text = \"done\"\n"
            "SAVE value.txt STRING \"from-file\"\nREAD value.txt $read\nSTRINGLN $text $other n=$n $read $unknown\n",
            "done OK n=5 from-file $unknown\n");
    invalid("STRINGLN hidden\nVAR $word = OK\n","Expected number");
    invalid("STRINGLN hidden\nVAR $word = (5 + )\n","operand");
    invalid("STRINGLN hidden\nVAR $word = \"a\" + \"b\"\n","quoted text");
    invalid("VAR $n=1\nREAD value.txt $n\n","type cannot change");
    invalid("VAR $s=\"5\"\nVAR $n=$s+1\n","Text variable");
  } else if (name == "stage3_identifier_validation_and_table_exhaustion") {
    for (const auto *statement:{"VAR $ = 1","VAR $a-b = 1","VAR $a.b = 1","VAR $a b = 1","$x += 1","VAR $x = $"})
      invalid("STRINGLN hidden\n"+std::string(statement)+"\n","identifier");
    invalid("STRINGLN hidden\nVAR $"+std::string(DUCKSCRIPT_MAX_IDENTIFIER_LEN,'a')+" = 1\n","assignment");
    live("VAR $1 = 1"); live("VAR $_mine = 2"); live("VAR $N = 3"); live("VAR $n = 4"); value("$1+$_mine+$N+$n",10);
    std::string longest = "$" + std::string(DUCKSCRIPT_MAX_IDENTIFIER_LEN-1,'a');
    live(("VAR " + longest + " = 1").c_str()); value(longest.c_str(),1);
    mock::reset(); std::string script="STRINGLN hidden\n";
    for (unsigned i=0;i<=DUCKSCRIPT_MAX_VARIABLES;++i) script+="VAR $v"+std::to_string(i)+" = 1\n";
    invalid(script,"table exhausted",DUCKSCRIPT_MAX_VARIABLES+2);
    mock::reset(); for (unsigned i=0;i<DUCKSCRIPT_MAX_VARIABLES;++i) live(("VAR $v"+std::to_string(i)+" = 1").c_str());
    require(!com::executeNow("VAR $extra = 1"),"runtime/live exhaustion must reject");
    live("VAR $v0 = ($v0+1)"); value("$v0",2); clean();
  } else if (name == "stage3_preflight_zero_hid_and_runtime_errors") {
    invalid("STRINGLN MUST-NOT-APPEAR\nVAR $x = (5 + )\nSTRINGLN ALSO-MUST-NOT-APPEAR\n","operand");
    invalid("STRINGLN hidden\nVAR $x=1/0\n","zero");
    invalid("STRINGLN hidden\nVAR $x=1<<16\n","Shift");
    invalid("STRINGLN hidden\nVAR $x=$undefined+1\n","Undefined");
    invalid("STRINGLN hidden\n$undefined=1\n","undefined variable");
    mock::reset(); mock::file("sd:runtime.txt","VAR $zero=0\nSTRINGLN before\nVAR $x=5/$zero\nSTRINGLN after\n");
    require(duckscript::run("sd:runtime.txt"),"runtime-only failure must begin"); mock::drain();
    require(mock::text=="before\n","preflight must not execute variable-dependent expressions");
    require(duckscript::lastError().indexOf("sd:runtime.txt: Error at line 3:")>=0 && duckscript::lastError().indexOf("zero")>=0,
            "runtime failure must retain useful source diagnostic"); clean();
    mock::reset(); mock::file("branch.txt","IF 0\nVAR $n=1\nENDIF\nSTRINGLN before\n$n=2\nSTRINGLN after\n");
    require(duckscript::run("branch.txt"),"preflight cannot assume legacy branch declaration executes"); mock::drain();
    require(mock::text=="before\n" && duckscript::lastError().indexOf("undefined variable")>=0,
            "runtime assignment to skipped declaration must fail safely"); clean();
  } else if (name == "stage3_define_global_forward_and_word_matching") {
    visible("STRINGLN #WORD\nDEFINE #WORD ready\nDEFINE WORD other\nSTRINGLN a#WORDz WORD WORDx xWORD (WORD)\nSTRINGLN WORD\nSTRINGLN WORD\tWORD\n",
            "ready\nareadyz other WORDx xWORD (WORD)\nother\nother\tother\n");
    visible("DEFINE OUTPUT STRINGLN\nOUTPUT harmless\n","harmless\n");
    visible("DEFINE #NAME $n\nVAR #NAME = 2\n#NAME = (#NAME + 1)\nSTRINGLN #NAME\n","3\n");
    visible("DEFINE #N 2\nIF 0\nDEFINE #WORD ready\nENDIF\nSTRINGLN #WORD\n","ready\n");
  } else if (name == "stage3_define_single_pass_and_declaration_exemption") {
    visible("DEFINE #A 1\nDEFINE #AB #A\nSTRINGLN #AB:#A:#ABC\n","#A:1:#AC\n");
    visible("DEFINE #X changed\nDEFINE $text = \"#X\"\nSTRINGLN $text\n","#X\n");
    visible("DEFINE #X  ready \nSTRINGLN a#Xb\n","a ready b\n");
    invalid("STRINGLN hidden\nDEFINE #C REM_BLOCK\n#C\nEND_REM\n","cannot create",3);
    invalid("DEFINE #C DEFINE #X 1\n#C\n","cannot create");
  } else if (name == "stage3_define_comment_and_text_modes") {
    visible("REM DEFINE #X bad\nREM_BLOCK\nDEFINE #X bad\nIF fake\nEND_REM\nDEFINE #X good\nSTRINGLN #X\n","good\n");
    invalid("STRINGLN hidden\nStRiNg\nDEFINE #X bad\nEND_STRING\nDEFINE #X good\n","deferred to Stage 7");
    visible("DEFINE REM_BLOCK STRINGLN\nREM_BLOCK\nSTRINGLN hidden\nEND_REM\nSTRINGLN good\n","good\n");
    mock::reset(); live("DEFINE REM STRINGLN"); live("REM hidden");
    require(mock::presses.empty(),"live comments cannot be rewritten into executable statements"); clean();
  } else if (name == "stage3_define_duplicates_invalid_and_table_limits") {
    invalid("STRINGLN hidden\nDEFINE #X one\nDEFINE #X two\n","Duplicate DEFINE",3);
    invalid("DEFINE #X one\nDEFINE #X one\n","Duplicate DEFINE");
    invalid("STRINGLN hidden\nDEFINE #N 2\n#N = 3\n","constants cannot be assigned",3);
    std::string longest = "#" + std::string(DUCKSCRIPT_MAX_IDENTIFIER_LEN-1,'a');
    visible("DEFINE " + longest + " good\nSTRINGLN " + longest + "\n","good\n");
    for (const auto *definition:{"DEFINE # 1","DEFINE #bad-name 1","DEFINE #bad.name 1","DEFINE #X","DEFINE"})
      invalid("STRINGLN hidden\n"+std::string(definition)+"\n","DEFINE");
    invalid("STRINGLN hidden\nDEFINE #"+std::string(DUCKSCRIPT_MAX_IDENTIFIER_LEN,'a')+" 1\n","label");
    std::string script="STRINGLN hidden\n";
    for (unsigned i=0;i<=DUCKSCRIPT_MAX_CONSTANTS;++i) script+="DEFINE #C"+std::to_string(i)+" x\n";
    invalid(script,"table exhausted",DUCKSCRIPT_MAX_CONSTANTS+2);
  } else if (name == "stage3_define_expansion_and_pool_boundaries") {
    std::string contents(250,'a');
    visible("DEFINE #W "+contents+"\nSTRING #W#Wabcde\n",(contents+contents+"abcde").c_str());
    invalid("DEFINE #W "+contents+"\nSTRING #W#Wabcdef\n","expansion length");
    mock::reset(); String error, output;
    require(duck_constants::define(("DEFINE #W "+std::string(DUCKSCRIPT_MAX_EXPANDED_LINE,'a')).c_str(),1,error),"maximum constant value accepted by bounded table API");
    require(duck_constants::expand("#W",output,error) && output.length()==DUCKSCRIPT_MAX_EXPANDED_LINE,"maximum expansion accepted");
    require(!duck_constants::expand("#Wx",output,error),"one extra byte rejected");
    require(!duck_constants::define(("DEFINE #L "+std::string(DUCKSCRIPT_MAX_EXPANDED_LINE+1,'a')).c_str(),2,error),"oversized value rejected");
    require(!duck_constants::define("NOTDEF #L value",2,error),"definition API must validate its keyword");
    mock::reset();
    for (unsigned i=0;i<5;++i) require(duck_constants::define(("DEFINE #P"+std::to_string(i)+" "+std::string(400,'b')).c_str(),i+1,error),"pool prefix must fit");
    require(duck_constants::define(("DEFINE #LAST "+std::string(42,'b')).c_str(),6,error),"exactly full 2048-byte pool must fit");
    require(!duck_constants::define("DEFINE #EXTRA x",7,error) && error.indexOf("pool exhausted")>=0,"pool overflow must reject");
    invalid("STRINGLN hidden\n"+std::string("DEFINE #BIG ")+std::string(501,'x')+"\n","line length limit");
  } else if (name == "stage3_expression_timing_counts_and_cancellation") {
    visible("DEFINE #C 2\nVAR $wait=20\nDEFAULT_DELAY ($wait/2)\nSTRING x\nREPEAT #C\nWAIT ($wait-19)\n"
            "DEFAULTDELAY FALSE\nDELAY $wait\nSTRING y\nREPLAY (TRUE+FALSE)\n","xxxyy");
    uint32_t actual; String error;
    require(script_parser::numericArgument("4294967295",actual,error) && actual==UINT32_MAX,"legacy uint32 literal retained");
    require(script_parser::numericArgument("+65536",actual,error) && actual==65536,"legacy plus-prefixed literal retained");
    require(script_parser::numericArgument("(65535+1)",actual,error) && actual==0,"expression results remain uint16");
    require(!script_parser::numericArgument("(65536)",actual,error),"grouping cannot bypass literal range");
    mock::reset(); mock::file("wait.txt","VAR $wait=10000\nDELAY $wait\nSTRING forbidden\n");
    require(duckscript::run("wait.txt"),"variable delay must start");
    for(unsigned i=0;i<500 && !(duckscript::currentLine()==2 && com::busy());++i) mock::tick();
    require(com::busy() && mock::presses.empty(),"delay must remain pending without HID");
    require(!com::executeNow("DEFINE #X bad"),"live definitions cannot interfere with active delay");
    duckscript::stop(); mock::drain(); require(mock::presses.empty(),"STOP cancels expression delay and queued output"); clean();
  } else if (name == "stage3_collection_preflight_stop_and_state_isolation") {
    std::string script; for(unsigned i=0;i<2000;++i) script+="REM cooperative collection\n";
    script+="DEFINE #W ready\nSTRINGLN #W\n";
    mock::file("large.txt",script.c_str()); require(duckscript::run("large.txt"),"large source must begin collection"); mock::tick();
    require(duckscript::running() && mock::presses.empty(),"collection must yield with zero HID");
    require(mock::bytesRead<=DUCKSCRIPT_READ_BUDGET+64,"collection read budget retained");
    require(!com::executeNow("VAR $n=1"),"live ownership must apply during collection");
    duckscript::stop(); for(unsigned i=0;i<50;++i)mock::tick(); clean();
    visible("DEFINE #W ready\nSTRINGLN #W\nSTOP\n","ready\n");
    visible("STRINGLN #W\n","#W\n");
    mock::reset(); live("DEFINE #W live"); live("VAR $n=7");
    visible("STRINGLN #W $n\n","#W $n\n");
  } else if (name == "stage3_interpolation_overflow_runtime_safe_stop") {
    mock::files["large.txt"] = std::string(600,'x');
    mock::file("interpolation.txt","READ large.txt $text\nSTRINGLN $text\nSTRINGLN after\n");
    require(duckscript::run("interpolation.txt"),"READ variable value is runtime-only"); mock::drain();
    require(duckscript::lastError().indexOf("Interpolation length limit")>=0,"oversized runtime interpolation must diagnose");
    require(mock::presses.empty() && !mock::text.length(),"overflow must not type a truncated value"); clean();
  } else if (name == "stage3_syntax_mode_does_not_evaluate_runtime_values") {
    uint16_t actual=0; duck_expr::Error error; duck_vars::Symbols symbols; String diagnostic;
    require(symbols.declare("$zero",duck_vars::Type::Numeric,false,diagnostic)>=0,"syntax symbol metadata must initialize");
    require(duck_expr::evaluate("5/$zero",7,actual,error,duck_vars::Symbols::resolve,&symbols,duck_expr::Mode::Syntax),"preflight must not invent a zero value");
    require(!duck_expr::evaluate("$zero/0",7,actual,error,duck_vars::Symbols::resolve,&symbols,duck_expr::Mode::Syntax),"known zero denominator must still reject");
  } else if (name == "stage3_bounded_expression_fuzz") {
    const char alphabet[] = "0123456789abcdef$()<>!=+*/%-^&| \t#";
    uint32_t seed=0x51A3; unsigned accepted=0, rejected=0;
    for(unsigned i=0;i<3000;++i) {
      std::string source;
      seed=seed*1664525U+1013904223U;
      unsigned length=seed%97;
      for(unsigned n=0;n<length;++n) { seed=seed*1664525U+1013904223U; source+=alphabet[seed%(sizeof(alphabet)-1)]; }
      uint16_t actual=0; duck_expr::Error error;
      bool ok=duck_expr::evaluate(source.c_str(),source.size(),actual,error,duck_vars::resolve);
      if(ok) { ++accepted; require(!error.message,"valid fuzz expression has no error"); }
      else { ++rejected; require(error.message && error.column && error.column<=source.size()+1,"malformed fuzz input fails with bounded diagnostic"); }
    }
    require(accepted && rejected,"fuzz cases must exercise successful and rejected parsing");
  } else throw std::runtime_error("unknown test name");
}

int main(int argc,char **argv) {
  if(argc != 2) return 2;
  try {
    test(argv[1]);
    std::cout << "PASS " << argv[1] << " (" << assertions << " assertions)\n";
    return 0;
  } catch(const std::exception &error) {
    std::cerr << "FAIL " << argv[1] << ": " << error.what() << "\n";
    return 1;
  }
}
