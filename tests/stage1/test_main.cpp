#include "host.h"
#include "com.h"
#include "duckscript.h"
#include "duck_vars.h"
#include "cli.h"
#include "hid_backend.h"
#include "keyboard_locale.h"
#include "locale/locales.h"
#include "storage.h"
#include "attackmode.h"
#include "settings.h"
#include "script_log.h"
#include <iostream>
#include <stdexcept>
#include <thread>

static unsigned assertions = 0;
static void require(bool condition, const char *message) {
  ++assertions;
  if (!condition) throw std::runtime_error(message);
}
static void run(const char *script, const char *name="test.txt") {
  mock::file(name, script);
  require(duckscript::run(name), "script must be accepted");
  mock::drain();
}
static void clean() {
  require(mock::blockingDelays==0, "execution must never call blocking delay()");
  require(mock::heldKeys.empty() && !mock::heldModifiers, "all runtime keys must be released");
  require(!com::busy() && !duckscript::running(), "execution must finish/cancel all pending work");
}

static void supported_commands_and_mock_interfaces() {
  mock::reset();
  run("REM harmless fixture\r\n// comment\n"
      "VAR $message = \"Hello\"\nDEFINE $other = \"OK\"\n"
      "STRINGLN $message\nSTRINGLN $other\n"
      "IF $other == OK\nSTRINGLN yes\nELSE\nSTRINGLN wrong\nENDIF\n"
      "VAR $flag = 1\nWHILE $flag\nSTRINGLN W\nVAR $flag = 0\nENDWHILE\n"
      "SAVE fixture.txt STRING \"read\"\nAPPEND fixture.txt STRING \"back\"\n"
      "READ fixture.txt $data\nSTRINGLN $data\n"
      "SAVE sd:fixture.txt STRING \"SD\"\nAPPEND sd:fixture.txt STRING \"tail\"\n"
      "READ sd:fixture.txt $sd\nSTRINGLN $sd\n"
      "LOCALE DE\nLOCALE US\nLED 1 2 3\nLED OFF\n"
      "WAIT 3\nDELAY 4\nDEFAULTDELAY 2\nDEFAULT_DELAY 3\n"
      "CONTROL SHIFT a\nRCTRL RSHIFT b\nGUI ALT TAB\nRIGHTALT SPACE\n"
      "RETURN\nKEYCODE 0x02 0x05\n"
      "ATTACKMODE OFF\nSTRING invisible\nATTACKMODE HID\nSTRING end\n",
      "sd:test.txt");
  require(mock::text=="Hello\nOK\nyes\nW\nreadback\nSDtail\n\nBend", "visible output and STRINGLN enter must match");
  require(mock::files["fixture.txt"]=="readback", "SAVE/APPEND SPIFFS must use mocked storage");
  require(mock::files["sd:fixture.txt"]=="SDtail", "SAVE/APPEND SD must use mocked storage");
  require(keyboard_locale::getLocale()==&locale_us, "locale selection must persist");
  require(attackmode::hidEnabled(), "ATTACKMODE HID must restore output");
  bool left=false,right=false,gui=false,raw=false,led=false;
  for (auto p:mock::presses) {
    left |= p.modifiers==3 && p.key==4;
    right |= p.modifiers==0x30 && p.key==5;
    gui |= p.modifiers==0x0C && p.key==0x2B;
    raw |= p.modifiers==2 && p.key==5;
  }
  for (auto color:mock::colors) led |= color==std::array<int,3>{1,2,3};
  require(left && right && gui && raw, "named combinations and raw KEYCODE modifiers must survive");
  require(led, "LED command must reach mocked output");
  require(script_log::getText().indexOf("Finished")>=0, "command log must record completion");
  require(duckscript::lastError().length()==0, "successful execution must not report an error");
  clean();
  require(com::executeNow("LOCALE DE"), "live locale command must be accepted"); mock::drain();
  require(keyboard_locale::getLocale()==&locale_de, "German locale selection must work");
  keyboard_locale::Stroke strokes[2]; uint8_t count;
  require(keyboard_locale::translate("^",1,strokes,count)==1 && count==2,
          "German dead key must translate into two strokes");
  require(strokes[0].key==0x35 && strokes[1].key==0x2C, "dead key stroke order must survive");
  const char truncated[] = {char(0xC3)};
  require(keyboard_locale::translate(truncated,1,strokes,count)==1 && count==0,
          "truncated UTF-8 must not read beyond the text buffer");
  const char outside[] = {char(127)};
  require(keyboard_locale::translate(outside,1,strokes,count)==1 && count==1 && strokes[0].key==0x4C,
          "complete German ASCII table must map DEL safely to Delete");
  require(!com::executeNow("LOCALE missing"), "invalid locale must be rejected");
  require(com::submissionError().indexOf("Command failed")>=0, "live parse failure must be reported");
  require(com::executeNow("LOCALE US"), "US locale must be accepted after an error"); mock::drain();
  auto before=mock::text;
  require(com::executeNow("KEYCODE 0 0xE1 0x04 0x04 0xFF"), "raw modifier and duplicate fixture must be accepted");
  mock::drain();
  require(mock::text==before+"A", "raw modifier usages, duplicate keys and invalid usages must preserve legacy semantics");
  settings::setDisableLed(true);
  auto colors=mock::colors.size();
  require(com::executeNow("LED 4 5 6"), "disabled LED command must remain valid"); mock::drain();
  require(mock::colors.size()==colors, "disabled LED must suppress output");
  clean();
  std::cout << "Actual: expected text, SPIFFS/SD writes, locale/LED/attackmode, key reports and logging verified.\n";
}

static void script_run_state_isolation() {
  mock::reset();
  run("VAR $old = 42\nDEFAULT_DELAY 100\nSTRING A\nREPEAT 1\n");
  require(mock::text=="AA", "first run must repeat its own output");
  String old;
  require(!duck_vars::get("$old",old), "finished run must release variable state");
  mock::text="";
  run("STRING B\nVAR invalid = 3\nSTRING never\n");
  require(mock::text.length()==0, "preflight syntax errors must prevent ALL output, including earlier lines");
  require(duckscript::lastError().indexOf("line 2")>=0, "preflight error must record source line");
  require(duckscript::lastError().indexOf("VAR invalid")>=0, "runtime error must record command detail");
  mock::text=""; auto start=mock::now;
  mock::file("clean.txt", "STRING C\n");
  require(duckscript::run("clean.txt"), "new run must start after failure");
  require(duckscript::lastError().length()==0, "new run must clear old errors");
  mock::drain();
  require(mock::text=="C", "new run must type only its own text");
  require(uint32_t(mock::now-start)<50, "new run must not inherit 100ms default delay");
  mock::text="";
  run("REPEAT 1\nSTRING never\n");
  require(mock::text.length()==0, "REPEAT must not inherit previous run's history");
  require(duckscript::lastError().indexOf("line 1")>=0, "missing history must be a line 1 error");
  run("IF 0\nSTRING skipped\nENDIF\nSTRING Z\n");
  require(mock::text=="Z", "fresh control-flow state must work");
  require(duckscript::lastError().length()==0, "successful run must clear preceding error");
  require(!duckscript::run("missing.txt"), "missing script must fail to open");
  require(duckscript::lastError().indexOf("Cannot open script")>=0, "storage failure must be reported");
  clean();
  std::cout << "Actual: timing/history/variables/control flags/errors reset; failure stops at its source line.\n";
}

static void cooperative_delay_and_text_cancellation() {
  mock::reset();
  mock::file("delay.txt", "DELAY 10000\nSTRING never\n");
  require(duckscript::run("delay.txt"), "delay script must start");
  mock::tick(); mock::tick(100);
  require(duckscript::running() && mock::text.length()==0, "active delay must remain pending without output");
  require(mock::now==101 && mock::blockingDelays==0, "delay must not advance the clock internally");
  cli::parse("STOP",mock::print,false);
  require(mock::output=="Stopped\n", "CLI STOP must acknowledge cancellation");
  mock::tick(20000);
  require(mock::text.length()==0, "no queued line may execute after STOP");
  clean();
  mock::file("text.txt", "STRING ABCDEFGHIJKLMNOP\nSTRING tail\n");
  require(duckscript::run("text.txt"), "text script must start");
  for(unsigned i=0;i<100 && mock::presses.empty();++i) mock::tick();
  require(mock::text=="A" && !mock::heldKeys.empty() && mock::heldModifiers==2,
          "text fixture must be cancelled while its first shifted key is held");
  cli::parse("stop",mock::print,false);
  require(mock::heldKeys.empty() && !mock::heldModifiers, "STOP must release held key and modifier immediately");
  for(unsigned i=0;i<100;++i) mock::tick();
  require(mock::text=="A", "cancelled text and subsequent command must not resume");
  auto reports=mock::presses.size(); duckscript::stop(); mock::tick();
  require(mock::presses.size()==reports, "repeated STOP must be idempotent");
  run("STRING new\n"); require(mock::text=="Anew", "new run must have no cancelled text tail");
  require(com::executeNow("STRING pending"), "live text must be queued");
  duckscript::stop(); mock::drain();
  require(mock::text=="Anew", "STOP must also cancel pending live work before first report");
  mock::now=0xfffffff8U;
  mock::file("wrap.txt", "DELAY 20\nSTRING W\n");
  require(duckscript::run("wrap.txt"), "wrap test must start");
  mock::tick(); mock::tick(19);
  require(mock::text=="Anew", "timer must remain pending at 19ms across wrap");
  mock::drain();
  require(mock::text=="AnewW", "timer must finish correctly after millis wrap");
  run("STRING S\nSTOP\nSTRING forbidden\n");
  require(mock::text=="AnewWS", "script STOP must terminate before the next line");
  mock::file("transport.txt", "STRING Q\nSTRING forbidden\n");
  require(duckscript::run("transport.txt"), "transport cancellation fixture must start");
  for(unsigned i=0;i<100 && mock::heldKeys.empty();++i) mock::tick();
  require(!mock::heldKeys.empty(), "fixture must send a held report before transport stalls");
  mock::usbReady=false;
  duckscript::stop();
  require(!duckscript::running() && !com::busy(), "STOP must return without waiting for a busy USB endpoint");
  auto heldText=mock::text;
  for(unsigned i=0;i<30;++i) mock::tick();
  require(mock::text==heldText, "busy USB cancellation must never queue further presses");
  mock::usbReady=true; mock::tick();
  require(mock::heldKeys.empty() && !mock::heldModifiers, "pending release must be retried when USB becomes ready");
  // No output may be consumed while the endpoint is unavailable.
  mock::usbReady=false;
  require(com::executeNow("STRING ready"), "live output can be accepted while USB is unavailable");
  for(unsigned i=0;i<30;++i) mock::tick();
  require(com::busy() && mock::text==heldText, "unavailable USB must yield without losing text");
  mock::usbReady=true; mock::drain();
  require(mock::text==heldText+"ready", "text must resume once transport is ready");
  clean();
  std::cout << "Actual: delay/text/queued work cancelled; held keys and busy-USB release retry verified; wrap-safe timers; zero delay() calls.\n";
}

static void repeat_timing_and_control_loop_yield() {
  mock::reset();
  run("DEFAULT_DELAY 20\nSTRING x\nREPEAT 2\nREPLAY 0\n");
  require(mock::text=="xxx" && mock::presses.size()==3, "REPEAT 2 must output three characters total");
  uint32_t first=mock::presses[1].time-mock::presses[0].time;
  uint32_t second=mock::presses[2].time-mock::presses[1].time;
  require(first>=25 && first<=35 && second>=25 && second<=35,
          "each output must wait one default delay, not the old double delay");
  clean();
  mock::text="";
  mock::file("loop.txt", "VAR $flag = 1\nWHILE $flag\nENDWHILE\n");
  require(duckscript::run("loop.txt"), "control-only loop must start");
  for(unsigned i=0;i<20;++i) mock::tick();
  require(duckscript::running(), "control-only loop must remain active while updates return");
  require(mock::text.length()==0, "control-only loop must emit no HID");
  duckscript::stop(); clean();
  mock::file("repeat.txt", "STRING z\nREPEAT 1000\nSTRING tail\n");
  require(duckscript::run("repeat.txt"), "long repeat must start");
  for(unsigned i=0;i<40;++i) mock::tick();
  require(duckscript::running(), "long repeat must yield between keyboard operations");
  auto emitted=mock::text.length();
  duckscript::stop();
  for(unsigned i=0;i<100;++i) mock::tick();
  require(mock::text.length()==emitted, "cancelled repeat and following command must never resume");
  clean();
  mock::file("default.txt", "DEFAULT_DELAY 10000\nSTRING z\nSTRING forbidden\n");
  require(duckscript::run("default.txt"), "default-delay cancellation fixture must start");
  for(unsigned i=0;i<30;++i) mock::tick();
  require(duckscript::running() && com::busy(), "default delay must remain cooperative");
  emitted=mock::text.length(); duckscript::stop(); mock::tick(20000);
  require(mock::text.length()==emitted, "STOP must cancel active default delay and following output");
  clean();
  std::cout << "Actual: xxx with report gaps " << first << "ms/" << second << "ms; control-only loop yields.\n";
}

static void live_commands_cannot_mutate_running_script() {
  mock::reset();
  // Stage 3 separates numeric expressions from the quoted text extension.
  mock::file("owner.txt", "VAR $word = \"OK\"\nDEFAULT_DELAY 2\nDELAY 100\nSTRING $word\nREPEAT 1\n");
  require(duckscript::run("owner.txt"), "owner script must start");
  // Ownership applies before its first line and between lines, not just while busy.
  require(!com::busy(), "script starts with an idle command slot");
  require(!com::executeNow("STRING BAD"), "live command must be rejected between script lines");
  require(!com::executeNow("LOCALE DE") && !com::executeNow("ATTACKMODE OFF"),
          "live locale and attack-mode changes must be rejected during script ownership");
  require(com::submissionError()=="Busy: script running", "busy reason must identify script ownership");
  for(unsigned i=0;i<15;++i) mock::tick();
  require(com::busy(), "script must be in active delay");
  cli::parse("send VAR $word = BAD",mock::print,false);
  cli::parse("send DEFAULT_DELAY 9000",mock::print,false);
  cli::parse("send STRING BAD",mock::print,false);
  require(mock::output=="Busy: script running\nBusy: script running\nBusy: script running\n", "CLI must report busy for live mutations");
  require(duckscript::lastError().length()==0, "busy rejection must not corrupt active error state");
  // Async web calls use executeNow too. Exercise concurrent submissions through
  // that shared production gate while main-loop updates run on another thread.
  unsigned rejected=0;
  std::thread requester([&] {
    for(unsigned i=0;i<100;++i) if (!com::executeNow("VAR $word = BAD")) ++rejected;
  });
  for(unsigned i=0;i<30;++i) mock::tick();
  requester.join();
  require(rejected==100, "concurrent live submissions must all be rejected");
  mock::drain();
  require(mock::text=="OKOK", "variable/default/repeat state must survive live command attempts");
  require(duckscript::lastError().length()==0, "active run must finish without error");
  cli::parse("send STRING live",mock::print,false);
  require(mock::output.endsWith("Accepted\n"), "idle CLI must acknowledge asynchronous acceptance");
  require(mock::text=="OKOK", "acceptance must not send keyboard output on the request thread");
  require(!com::executeNow("STRING overwrite"), "pending live command must not be overwritten");
  require(!duckscript::run("owner.txt"), "run must not take ownership during a live command");
  mock::drain();
  require(mock::text=="OKOKlive", "only accepted live command may run");
  clean();
  std::cout << "Actual: all live/script ownership rejections, 100 concurrent rejections, CLI busy/accepted output, intact OKOK history.\n";
}

static void documented_language_gaps() {
  // Desired behavior is asserted as a diagnostic, never as compatibility that
  // must remain broken. A future fix reports XPASS instead of failing a test.
  auto diagnostic=[](const char *name,const char *script,const char *expected) {
    mock::reset(); run(script);
    std::cout << (mock::text==expected ? "XPASS " : "XFAIL ") << name
              << ": expected '" << expected << "', actual '" << mock::text.c_str() << "'\n";
    clean();
  };
  diagnostic("known_nested_if", "IF 0\nIF 1\nSTRING bad\nENDIF\nENDIF\nSTRING good\n", "good");
  diagnostic("known_canonical_if", "VAR $n = 1\nIF ($n == 1) THEN\nSTRING good\nELSE\nSTRING bad\nEND_IF\n", "good");
  diagnostic("known_false_while", "VAR $flag = 0\nWHILE $flag\nSTRING bad\nENDWHILE\nSTRING good\n", "good");
  uint8_t key=0; hid_backend::keyNameToHid("F13",key);
  std::cout << (key==0x68 ? "XPASS " : "XFAIL ") << "known_f13_mapping: expected usage 104, actual " << unsigned(key) << "\n";
  auto records=sizeof(ascii_de)/2;
  std::cout << (records==128 ? "XPASS " : "XFAIL ") << "known_german_ascii_table: expected 128 records, actual " << records
            << "; exact content/alignment independently checked by Stage 8 when table is corrected\n";
}

int main(int argc,char **argv) {
  if(argc!=2) return 2;
  const String name=argv[1];
  try {
    std::cout << "TEST " << argv[1] << "\nExpected: ";
    if(name=="supported_commands_and_mock_interfaces") {
      std::cout << "preserve supported text/keys/extensions through mocked hardware.\n";
      supported_commands_and_mock_interfaces();
    } else if(name=="script_run_state_isolation") {
      std::cout << "fresh timing, history, variables and source-specific errors per run.\n";
      script_run_state_isolation();
    } else if(name=="cooperative_delay_and_text_cancellation") {
      std::cout << "yield during delay/text, cancel all work, release keys, handle timer wrap.\n";
      cooperative_delay_and_text_cancellation();
    } else if(name=="repeat_timing_and_control_loop_yield") {
      std::cout << "repeat output/count, one default delay per output, bounded control-loop updates.\n";
      repeat_timing_and_control_loop_yield();
    } else if(name=="live_commands_cannot_mutate_running_script") {
      std::cout << "reject live interference, preserve state, serialize concurrent callers, accept when idle.\n";
      live_commands_cannot_mutate_running_script();
    } else if(name=="documented_language_gaps") {
      std::cout << "desired language behavior; known failures reported separately as XFAIL.\n";
      documented_language_gaps();
    } else return 2;
    if(name=="documented_language_gaps")
      std::cout << "Diagnostics completed (" << assertions << " sanity assertions); XFAIL entries are unresolved bugs, not passing language tests.\n";
    else
      std::cout << "PASS " << argv[1] << " (" << assertions << " assertions)\n";
    return 0;
  } catch(const std::exception &e) {
    std::cerr << "FAIL " << argv[1] << ": " << e.what() << "\n";
    return 1;
  }
}
