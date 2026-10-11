#include "host.h"
#include "FS.h"
#include "com.h"
#include "duckscript.h"
#include "cli.h"
#include "script_parser.h"
#include "script_source.h"
#include "script_log.h"
#include <iostream>
#include <stdexcept>
#include <string>
#include <limits>

static unsigned assertions = 0;
static void require(bool condition, const char *message) {
  ++assertions;
  if (!condition) throw std::runtime_error(message);
}
static void clean() {
  require(!duckscript::running() && !com::busy(), "execution must finish or cancel");
  require(mock::blockingDelays==0, "no blocking delay() is allowed");
  require(mock::heldKeys.empty() && !mock::heldModifiers, "no runtime-owned held keys may remain");
}
static void run(const std::string &script, const char *name="sd:parser.txt") {
  mock::file(name,script.c_str());
  require(duckscript::run(name), "valid script must start preflight");
  mock::drain();
  require(duckscript::lastError().length()==0, "valid script must complete without error");
  clean();
}
static void visible(const std::string &script,const char *expected,const char *name="sd:parser.txt") {
  mock::reset(); run(script,name);
  require(mock::text==expected, "visible output must exactly match expected fixture");
}
static void invalid(const std::string &script,const char *message,unsigned line=0) {
  mock::reset();
  mock::file("sd:invalid.txt",script.c_str());
  bool accepted=duckscript::run("sd:invalid.txt");
  if(accepted) mock::drain();
  require(duckscript::lastError().length()>0, "invalid script must report an error");
  require(duckscript::lastError().indexOf(message)>=0, "diagnostic must identify the expected error");
  require(duckscript::lastError().indexOf("sd:invalid.txt")>=0, "diagnostic must include source volume/name");
  if(line) require(duckscript::lastError().indexOf("line "+String(line)+":")>=0, "diagnostic must include correct source line");
  require(mock::text.length()==0 && mock::presses.empty(), "preflight errors must produce zero HID, including earlier valid lines");
  require(script_log::getText().indexOf(message)>=0, "preflight failure must be logged");
  clean();
}

static void test(const String &name) {
  if(name=="stage2_rem_comments") {
    visible("REM ordinary comment\nrem\nReM STRINGLN hidden\n// STRING hidden\nSTRINGLN ok\n", "ok\n");
  } else if(name=="stage2_required_rem_block_fixture") {
    const char *fixture="REM ordinary comment\nREM_BLOCK\nIF this is deliberately not executable\nSTRINGLN this-must-not-appear\nEND_REM\nSTRINGLN parser-ok\n";
    visible(fixture,"parser-ok\n");
    visible(fixture,"parser-ok\n","parser.txt"); // Identical SPIFFS and SD behavior.
  } else if(name=="stage2_comment_block_literal_commands") {
    visible("REM_BLOCK\nIF (bad) THEN\nWHILE 1 + 2\nSTRING\nSTRINGLN hidden\nFUNCTION fake()\nDELAY garbage\nEND_IF\nEND_STRING\nEND_REMINDER\nEND_REM\nSTRINGLN ok\n", "ok\n");
  } else if(name=="stage2_unterminated_rem_block_zero_hid") {
    invalid("STRINGLN this-must-not-appear\nREM_BLOCK\nSTRINGLN hidden\nEND_IF\n", "Unterminated REM_BLOCK",2);
  } else if(name=="stage2_unmatched_end_rem_zero_hid") {
    invalid("STRINGLN hidden\nEND_REM\n", "Unmatched comment/text",2);
  } else if(name=="stage2_lf_source") {
    visible("STRINGLN one\nSTRINGLN two\n", "one\ntwo\n");
  } else if(name=="stage2_crlf_source") {
    visible("REM x\r\nSTRINGLN one\r\nSTRINGLN two\r\n", "one\ntwo\n");
  } else if(name=="stage2_utf8_bom") {
    visible("\xEF\xBB\xBF" "STRINGLN bom\r\n", "bom\n");
    visible("\xEF\xBB\xBF", "");
    invalid("STRINGLN hidden\n\xEF\xBB\xBF" "STRINGLN bad\n", "Unsupported command",2);
  } else if(name=="stage2_missing_final_newline") {
    visible("REM x\nSTRINGLN final", "final\n");
    visible("REM_BLOCK\nSTRINGLN hidden\nEND_REM", "");
  } else if(name=="stage2_blank_lines") {
    visible("\n\n \t\r\nSTRINGLN blank\n\n", "blank\n");
    visible("", "");
  } else if(name=="stage2_spaces_tabs_and_payload_preservation") {
    visible(" \tREM\tcomment\n \tREM_BLOCK\t\n STRING hidden\n \tEND_REM \t\n"
            "\tVAR\t$name\t=\t\"OK\"\n\tIF\t$name == OK\n"
            " \tSTRINGLN\t$name  \t\n ELSE\nSTRING wrong\nEND\tIF\n"
            "SAVE\tvalue.txt\tStRiNg\t\"saved\"\nREAD\tvalue.txt\t$read\n"
            "DEFAULTDELAY\t1\nWAIT\t0\nLED\t1\t2\t3\nKEYCODE\t0x02\t0x04\n"
            "STRING  two spaces\nSTRINGLN\t$read\n", "OK\nA two spacessaved\n");
    require(mock::files["value.txt"]=="saved", "tab-separated SAVE/READ must preserve file payload");
  } else if(name=="stage2_maximum_line_length") {
    std::string payload(DUCKSCRIPT_MAX_LINE_LEN-7,'a');
    visible("STRING "+payload+"\n",payload.c_str());
    visible("\xEF\xBB\xBF" "STRING "+payload+"\r\n",payload.c_str());
  } else if(name=="stage2_overlong_line_zero_hid") {
    invalid("STRINGLN hidden\nSTRING "+std::string(DUCKSCRIPT_MAX_LINE_LEN-6,'a')+"\n", "line length limit",2);
    invalid("REM_BLOCK\n"+std::string(DUCKSCRIPT_MAX_LINE_LEN+1,'a')+"\nEND_REM\n", "line length limit",2);
  } else if(name=="stage2_source_byte_limits") {
    std::string line="REM "+std::string(DUCKSCRIPT_MAX_LINE_LEN-5,'x')+"\n";
    std::string script;
    while(script.size()+line.size()<=DUCKSCRIPT_MAX_SOURCE_BYTES) script+=line;
    script+=std::string(DUCKSCRIPT_MAX_SOURCE_BYTES-script.size(),'\n');
    require(script.size()==DUCKSCRIPT_MAX_SOURCE_BYTES, "fixture must exactly fill configured source limit");
    visible(script,"");
    invalid(script+"\n", "source byte limit",1);
  } else if(name=="stage2_source_line_limits") {
    visible(std::string(DUCKSCRIPT_MAX_SOURCE_LINES,'\n'),"");
    invalid(std::string(DUCKSCRIPT_MAX_SOURCE_LINES+1,'\n'), "source line limit",DUCKSCRIPT_MAX_SOURCE_LINES+1);
  } else if(name=="stage2_mismatched_control_blocks_zero_hid") {
    invalid("STRINGLN hidden\nIF 1\nWHILE FALSE\nEND_IF\nEND_WHILE\n", "Mismatched IF/WHILE",4);
    invalid("IF 1\nENDWHILE\n", "Mismatched IF/WHILE",2);
  } else if(name=="stage2_unterminated_control_blocks_zero_hid") {
    invalid("STRINGLN hidden\nIF 1\nSTRING hidden\n", "Unterminated IF/WHILE",2);
    invalid("WHILE FALSE\n", "Unterminated IF/WHILE",1);
    invalid("ENDIF\n", "Unmatched control-flow",1);
    invalid("END_WHILE\n", "Unmatched control-flow",1);
  } else if(name=="stage2_duplicate_else_zero_hid") {
    invalid("IF 1\nELSE\nELSE\nENDIF\n", "duplicate ELSE",3);
    invalid("ELSE\n", "Unmatched or duplicate ELSE",1);
  } else if(name=="stage2_block_depth_limit_zero_hid") {
    std::string script;
    for(unsigned i=0;i<=DUCKSCRIPT_MAX_BLOCK_DEPTH;++i) script+="IF 1\n";
    invalid(script,"nesting limit",DUCKSCRIPT_MAX_BLOCK_DEPTH+1);
  } else if(name=="stage2_text_blocks_literal_mode_and_deferred_runtime") {
    for(const auto *keyword:{"STRING","STRINGLN"}) {
      std::string script="STRINGLN hidden\n"+std::string(keyword)+"\nIF (not executable) THEN\nWHILE bad + 1\nREM_BLOCK\nUNKNOWN_COMMAND\nEND_IF\nEND_REM\nEND_"+keyword+"\n";
      invalid(script,"runtime support is deferred to Stage 7",2);
      script_parser::Lexer lexer; script_parser::Statement stmt; String diagnostic;
      require(lexer.scan(keyword,1,stmt,diagnostic), "text opener must be lexically recognized");
      for(const auto *body:{"IF (x) THEN","WHILE x","END_IF","REM_BLOCK","END_REM","UNKNOWN_COMMAND"}) {
        require(lexer.scan(body,2,stmt,diagnostic) && stmt.kind==script_parser::Kind::Empty,
                "control-looking text must remain literal inside a text block");
      }
      require(lexer.scan(("END_"+std::string(keyword)).c_str(),3,stmt,diagnostic), "matching text terminator must close mode");
      uint32_t line=3; require(lexer.finish(diagnostic,line), "matched text mode must be structurally complete");
    }
  } else if(name=="stage2_unterminated_text_blocks_zero_hid") {
    invalid("STRINGLN hidden\nSTRING\nIF fake\n", "Unterminated STRING block",2);
    invalid("STRINGLN\nEND_IF\n", "Unterminated STRINGLN block",1);
  } else if(name=="stage2_unmatched_text_terminators_zero_hid") {
    invalid("STRINGLN hidden\nEND_STRING\n", "Unmatched comment/text",2);
    invalid("END_STRINGLN\n", "Unmatched comment/text",1);
  } else if(name=="stage2_mismatched_text_terminators_zero_hid") {
    invalid("STRING\nEND_STRINGLN\n", "Mismatched STRING/STRINGLN",2);
    invalid("STRINGLN\nEND_STRING\n", "Mismatched STRING/STRINGLN",2);
    invalid("REM_BLOCK\nREM_BLOCK\nEND_REM\nEND_REM\n", "Unmatched comment/text",4);
  } else if(name=="stage2_unknown_commands_zero_hid") {
    invalid("STRINGLN hidden\nUNKNOWN_COMMAND\n", "Unsupported command",2);
    invalid("STRINGLN hidden\nFUNCTION fake()\n", "Unsupported command",2);
    invalid("RETURN 1\n", "Unsupported RETURN arguments",1);
  } else if(name=="stage2_keyword_prefixes_are_not_commands") {
    for(const auto *prefix:{"REMARK","REMINDER","REM_BLOCKED","END_REMINDER","DELAYED","WAITING","STRINGLNfoo",
                            "STRINGfoo","STOPPER","ENDIFfoo","DEFAULTDELAYED","KEYCODEfoo","LEDGER","F1garbage"})
      invalid("STRINGLN hidden\n"+std::string(prefix)+"\n","Unsupported command",2);
    require(!script_parser::hasKeyword("REMARK x","REM"), "REM must not match a prefix");
    require(script_parser::hasKeyword("REM\tx","REM"), "REM must accept a tab token boundary");
  } else if(name=="stage2_malformed_statements_zero_hid") {
    for(const auto *statement:{"DELAY","DELAY -1","DELAY 4294967296","WAIT 1 2","REPEAT $count","DEFAULT_DELAY abc",
                              "VAR invalid = 1","VAR $x","VAR $x = \"", "DEFINE #name", "LOCALE unknown",
                              "LED 1 2","LED 256 0 0","KEYCODE","KEYCODE 0x100","KEYCODE 0x0X01",
                              "KEYCODE 0 1 2 3 4 5 6 7","ATTACKMODE","ATTACKMODE OFF HID","STOP extra",
                              "SAVE file.txt STRINGIFY x","APPEND file.txt STRING \"bad","READ file.txt not_a_variable",
                              "IF","IF 1 < 2","IF ==","IF 1 ==","IF == 1","IF 1 === 1","IF 1 = 1","IF 1 AND 2",
                              "IF ($x == 1) Then","WHILE $x + 1","ELSE IF 1","END_REM extra"}) {
      mock::reset(); mock::file("bad.txt",("STRINGLN hidden\n"+std::string(statement)+"\n").c_str());
      require(duckscript::run("bad.txt"), "malformed statement should reach asynchronous preflight"); mock::drain();
      require(duckscript::lastError().indexOf("line 2")>=0, "malformed statement diagnostic must locate line 2");
      require(mock::presses.empty() && mock::text.length()==0, "malformed statement must be rejected before earlier output"); clean();
    }
  } else if(name=="stage2_supported_extensions_and_bare_keys") {
    visible("DEFINE $word = \"OK\"\nVAR $flag = 1\nIF $word == OK\nSTRINGLN $word\nEND_IF\n"
            "WHILE $flag\nSTRINGLN W\nVAR $flag = 0\nEND_WHILE\n"
            "SAVE sd:value.txt STRING \"saved\"\nAPPEND sd:value.txt STRING \"more\"\nREAD sd:value.txt $read\n"
            "LOCALE US\nLED 0 1 2\nATTACKMODE HID\nDELAY +0\nDEFAULT_DELAY 1\nWAIT 0\n"
            "STRING $read\nREPLAY 1\nRETURN\na\n!\nSHIFT b\nRIGHTSHIFT c\nF1 F2\nSTOP\nSTRING hidden\n",
            "OK\nW\nsavedmoresavedmore\na!BC");
    require(mock::files["sd:value.txt"]=="savedmore", "existing SD file extensions must remain functional");
    bool f1=false,f2=false; for(auto p:mock::presses) { f1|=p.key==0x3A; f2|=p.key==0x3B; }
    require(f1 && f2, "function-key tokens must be recognized exactly in combinations");
  } else if(name=="stage2_storage_read_seek_faults") {
    mock::reset(); mock::file("fault.txt","STRINGLN hidden\nREM end\n");
    mock::failReadAt=5;
    require(duckscript::run("fault.txt"), "read fault must start preflight"); mock::drain();
    require(duckscript::lastError().indexOf("read error before EOF")>=0, "early read failure must differ from EOF");
    require(mock::presses.empty(), "preflight read failure must emit no HID"); clean();
    mock::reset(); mock::file("fault.txt","STRINGLN hidden\n"); mock::failSeekAt=0;
    require(duckscript::run("fault.txt"), "seek fault must start preflight"); mock::drain();
    require(duckscript::lastError().indexOf("seek error")>=0, "preflight rewind failure must be reported");
    require(mock::presses.empty(), "preflight rewind failure must emit no HID"); clean();
    mock::reset(); mock::file("fault.txt","VAR $flag = 1\nWHILE $flag\nSTRING x\nENDWHILE\nSTRING hidden\n");
    require(duckscript::run("fault.txt"), "loop seek fault fixture must start");
    mock::failSeekAt=std::string("VAR $flag = 1\n").size(); mock::drain();
    require(duckscript::lastError().indexOf("seek error")>=0, "runtime loop seek failure must be reported");
    require(mock::text=="x", "runtime seek error must stop safely before later output"); clean();
    mock::reset(); mock::file("fault.txt","STRINGLN hidden\n");
    require(duckscript::run("fault.txt"), "position fault fixture must start");
    // Exercise Reader directly against a handle moved by an external caller.
    File file("REM x\n"); script_source::Reader reader; require(reader.begin(file), "reader must open");
    require(file.seek(1), "external seek must be simulated"); String line; uint16_t bytes=256;
    require(reader.next(line,bytes)==script_source::Result::Error && reader.error().indexOf("position error")>=0,
            "unexpected storage position must differ from EOF");
    duckscript::stop(); clean();
  } else if(name=="stage2_preflight_cooperative_stop_and_live_ownership") {
    mock::reset(); std::string script;
    for(unsigned i=0;i<2000;++i) script+="REM bounded preflight work\n";
    script+="STRINGLN not-yet\n";
    mock::file("sd:large.txt",script.c_str());
    require(duckscript::run("sd:large.txt"), "large SD script must start");
    mock::tick();
    require(duckscript::running() && mock::presses.empty(), "large preflight must yield before HID");
    require(mock::bytesRead<=DUCKSCRIPT_READ_BUDGET+64, "one update must obey bounded read work");
    require(mock::readCalls<=6, "one update must use bounded chunk reads");
    require(!com::executeNow("STRING interference"), "live commands must be rejected during preflight ownership");
    cli::parse("stopper",mock::print,false);
    require(duckscript::running(), "CLI keyword prefixes must not cancel an active run");
    require(mock::output=="Unknown command, type 'help'\n", "CLI typo must receive unknown-command output");
    mock::output="";
    cli::parse("STOP",mock::print,false);
    require(mock::output=="Stopped\n", "CLI STOP must acknowledge cancellation during preflight");
    for(unsigned i=0;i<50;++i) mock::tick();
    require(mock::presses.empty(), "cancelled preflight must never start queued output"); clean();
    visible("STRINGLN new\n","new\n");
  } else if(name=="stage2_live_validation_and_limits") {
    mock::reset();
    for(const auto *line:{"REMARK x","UNKNOWN_COMMAND","DELAY -1","IF 1","STRING","END_REM","F1garbage"}) {
      require(!com::executeNow(line), "invalid/unsupported live statement must be rejected");
      require(com::submissionError().length()>0, "live rejection must report diagnostic");
      require(mock::presses.empty() && !com::busy(), "live rejection must not queue keyboard output");
    }
    std::string oversized="STRING "+std::string(DUCKSCRIPT_MAX_LINE_LEN,'a');
    require(!com::executeNow(oversized.c_str()), "overlong live line must be rejected without copying into execution");
    require(com::submissionError().indexOf("line length limit")>=0, "live size violation must be diagnosed");
    require(com::executeNow("STRINGLN live-ok"), "valid live statement must remain accepted"); mock::drain();
    require(mock::text=="live-ok\n", "valid live STRINGLN behavior must remain intact"); clean();
    cli::parse("helpful",mock::print,false);
    require(mock::output=="Unknown command, type 'help'\n", "CLI helper names must recognize complete tokens");
    mock::output="";
    cli::parse("send\tSTRINGLN cli-ok",mock::print,false);
    require(mock::output=="Accepted\n", "tab-separated CLI send must remain functional");
    mock::drain();
    require(mock::text=="live-ok\ncli-ok\n", "tab-separated CLI send must preserve command output"); clean();
  } else throw std::runtime_error("unknown test name");
}

int main(int argc,char **argv) {
  if(argc!=2) return 2;
  try {
    test(argv[1]);
    std::cout << "PASS " << argv[1] << " (" << assertions << " assertions)\n";
    return 0;
  } catch(const std::exception &e) {
    std::cerr << "FAIL " << argv[1] << ": " << e.what() << "\n";
    return 1;
  }
}
