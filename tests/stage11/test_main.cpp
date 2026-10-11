#include "host.h"
#include "FS.h"
#include "USB.h"
#include "hid_backend.h"
#include "com.h"
#include "duckscript.h"
#include "script_parser.h"
#include "keyboard_locale.h"
#include "cli.h"
#include "execution_guard.h"
#include <thread>
#include <iostream>
#include <stdexcept>
#include <string>
#include <algorithm>

static unsigned assertions = 0;
static void check(bool ok, const char *why) { ++assertions; if (!ok) throw std::runtime_error(why); }
using Bytes = std::array<uint8_t, 8>;
static Bytes bytes(uint8_t mod, std::initializer_list<uint8_t> keys = {}) {
  Bytes b = {mod, 0, 0, 0, 0, 0, 0, 0}; size_t i = 2;
  for (auto k : keys) b[i++] = k;
  return b;
}
static void exact(size_t i, Bytes b) {
  check(i < mock::reports.size(), "accepted report exists");
  const auto &r = mock::reports[i];
  check(r.id == 1 && r.instance == 0, "keyboard ID1 endpoint0");
  if (r.bytes != b) { std::cerr << "report " << i << ':'; for (auto v:r.bytes) std::cerr << ' ' << unsigned(v); std::cerr << '\n'; }
  check(r.bytes == b, "exact eight-byte modifier/reserved/usages/padding");
}
static void idle() {
  check(!duckscript::running() && !com::busy(), "runtime idle");
  check(!hid_backend::hasPersistent(), "no logical persistent ownership");
  check(!mock::heldModifiers && mock::heldKeys.empty(), "mock host released");
  check(!mock::blockingDelays, "no whole-string/blocking delays");
}
static void start(const std::string &s, const char *source = "stage11.txt") {
  mock::reset(); hid_backend::begin(); com::update(); mock::reports.clear();
  mock::file(source, s.c_str()); check(duckscript::run(source), "script accepted");
}
static void run(const std::string &s, const char *source = "stage11.txt") {
  start(s, source); mock::drain(150000);
  if (duckscript::lastError().length()) std::cerr << duckscript::lastError().c_str() << '\n';
  check(!duckscript::lastError().length(), "no runtime error"); idle();
}
static void reject(const std::string &s, const char *message) {
  start("STRINGLN MUST-NOT-APPEAR\n" + s); mock::drain();
  check(duckscript::lastError().indexOf(message) >= 0, "useful preflight diagnostic");
  check(mock::reports.empty(), "whole-script preflight zero HID"); idle();
}
static void held(const std::string &s) {
  start(s);
  for (unsigned i=0; i<20000 && !hid_backend::hasPersistent(); ++i) mock::tick();
  check(hid_backend::hasPersistent(), "reach persistent key ownership");
}
static void local() { mock::reset(); hid_backend::begin(); com::update(); mock::reports.clear(); }
static void command(const char *s) { check(com::executeNow(s), "live accepted"); mock::drain(); }
static void test(const std::string &n) {
  if (n == "hold_release_key") {
    run("HOLD a\nDELAY 20\nRELEASE a\nSTRINGLN ok\n");
    exact(0, bytes(0,{4})); exact(1,{}); check(mock::reports[1].time-mock::reports[0].time >= 20,"hold spans delay");
  } else if (n == "all_eight_persistent_modifiers") {
    const char *mods[]={"CONTROL","SHIFT","ALT","WINDOWS","RCTRL","RSHIFT","RALT","RIGHTGUI"};
    for (unsigned i=0; i<8; ++i) {
      run(std::string("INJECT_MOD\nHOLD ")+mods[i]+"\nDELAY 10\nRELEASE "+mods[i]+"\n");
      exact(0,bytes(1<<i)); exact(1,{}); check(mock::reports.size()==2,"no output from prefix");
    }
  } else if (n == "selective_modifier_release") {
    run("HOLD CTRL\nHOLD SHIFT\nHOLD RIGHTALT\nRELEASE SHIFT\nRELEASE CTRL\nRELEASE RIGHTALT\n");
    exact(0,bytes(1)); exact(1,bytes(3)); exact(2,bytes(0x43)); exact(3,bytes(0x41)); exact(4,bytes(0x40)); exact(5,{});
  } else if (n == "selective_key_release_order") {
    run("HOLD a\nHOLD b\nHOLD c\nRELEASE b\nHOLD d\nRELEASE a\nRELEASE c\nRELEASE d\n");
    exact(2,bytes(0,{4,5,6})); exact(3,bytes(0,{4,6})); exact(4,bytes(0,{4,6,7})); exact(5,bytes(0,{6,7}));
  } else if (n == "idempotent_hold_release") {
    run("HOLD a\nHOLD A\nHOLD a\nRELEASE b\nRELEASE a\nRELEASE a\n");
    check(mock::reports.size()==2,"duplicates/unowned releases no extra transitions"); exact(0,bytes(0,{4})); exact(1,{});
  } else if (n == "six_persistent_keys") {
    run("HOLD a\nHOLD b\nHOLD c\nHOLD d\nHOLD e\nHOLD f\nRELEASE c\nHOLD g\nRESET\n");
    exact(5,bytes(0,{4,5,6,7,8,9})); exact(7,bytes(0,{4,5,7,8,9,10})); exact(8,{});
  } else if (n == "seventh_hold_fails_no_drop") {
    start("HOLD a\nHOLD b\nHOLD c\nHOLD d\nHOLD e\nHOLD f\nHOLD g\nSTRINGLN NEVER\n"); mock::drain();
    check(duckscript::lastError().indexOf("six distinct")>=0,"runtime rollover diagnostic");
    check(duckscript::lastError().indexOf("stage11.txt")>=0 && duckscript::lastError().indexOf("line 7")>=0,"source and line");
    check(mock::reports.size()==7,"six successful holds then cancellation zero only"); exact(5,bytes(0,{4,5,6,7,8,9})); exact(6,{}); idle();
  } else if (n == "transient_chord_merges_persistent") {
    run("HOLD ALT\nHOLD a\nCTRL b\nRELEASE a\nRELEASE ALT\n");
    exact(2,bytes(5,{4,5})); exact(3,bytes(4,{4})); exact(4,bytes(4)); exact(5,{});
  } else if (n == "all_modifier_masks_merge") {
    local(); uint8_t key=4;
    for (unsigned m=0; m<256; ++m) {
      check(hid_backend::hold(uint8_t(m),0),"hold mask");
      check(hid_backend::beginReport(0x22,&key,1),"transient accepted"); exact(mock::reports.size()-1,bytes(uint8_t(m|0x22),{4}));
      check(hid_backend::releaseReport(),"restore owned mask"); exact(mock::reports.size()-1,bytes(uint8_t(m)));
      hid_backend::cancelReport();
    } idle();
  } else if (n == "string_shift_punctuation_enter") {
    run("HOLD CTRL\nSTRINGLN A!\nRELEASE CTRL\n");
    exact(1,bytes(3,{4})); exact(2,bytes(1)); exact(3,bytes(3,{0x1e})); exact(4,bytes(1)); exact(5,bytes(1,{0x28})); exact(6,bytes(1));
  } else if (n == "de_altgr_and_dead_key_merge") {
    run("LOCALE DE\nHOLD RCTRL\nSTRING @^\nRELEASE RCTRL\n");
    exact(1,bytes(0x50,{0x14})); exact(2,bytes(0x10)); exact(3,bytes(0x10,{0x35})); exact(4,bytes(0x10)); exact(5,bytes(0x10,{0x2c})); exact(6,bytes(0x10));
  } else if (n == "held_shift_with_german_spacing") {
    run("LOCALE DE\nHOLD SHIFT\nSTRING `\nRELEASE SHIFT\n");
    exact(1,bytes(2,{0x2e})); exact(2,bytes(2)); exact(3,bytes(2,{0x2c})); exact(4,bytes(2));
  } else if (n == "persistent_duplicate_transient_no_edge") {
    run("HOLD a\na\nSTRING a\nRELEASE a\n");
    for (size_t i=0;i<5;++i) { exact(i,bytes(0,{4})); } exact(5,{});
  } else if (n == "merged_seventh_transient_fails") {
    start("HOLD a\nHOLD b\nHOLD c\nHOLD d\nHOLD e\nHOLD f\ng\nSTRINGLN NEVER\n"); mock::drain();
    check(duckscript::lastError().indexOf("six distinct")>=0,"merged transient saturation error"); check(mock::reports.size()==7,"no report silently missing seventh"); exact(6,{}); idle();
  } else if (n == "saturated_duplicate_and_modifier_allowed") {
    run("HOLD a\nHOLD b\nHOLD c\nHOLD d\nHOLD e\nHOLD f\nCTRL a\nRESET\n");
    exact(6,bytes(1,{4,5,6,7,8,9})); exact(7,bytes(0,{4,5,6,7,8,9}));
  } else if (n == "raw_modifier_keycode_merges") {
    run("HOLD SHIFT\nHOLD a\nKEYCODE 4 0xE4 5 5\nRESET\n"); exact(2,bytes(0x16,{4,5})); exact(3,bytes(2,{4}));
  } else if (n == "inject_mod_inline") {
    run("INJECT_MOD WINDOWS\nSTRINGLN ok\n"); exact(0,bytes(8)); exact(1,{});
  } else if (n == "inject_mod_restores_owned") {
    run("HOLD a\nINJECT_MOD RIGHTALT\nRELEASE a\n"); exact(1,bytes(0x40,{4})); exact(2,bytes(0,{4})); exact(3,{});
  } else if (n == "inject_mod_prefix_reference") {
    run("INJECT_MOD\nHOLD SHIFT\nHOLD a\nDELAY 10\nRELEASE a\nRESET\nSTRINGLN ok\n");
    exact(0,bytes(2)); exact(1,bytes(2,{4})); exact(2,bytes(2)); exact(3,{});
  } else if (n == "reset_continues_variables") {
    run("VAR $x = 2\nHOLD CTRL\nRESET\n$x = ($x+3)\nSTRINGLN x=$x\n");
    exact(0,bytes(1)); exact(1,{}); check(mock::text=="x=5\n","reset continues state, never reboot");
  } else if (n == "stop_payload_tail_and_release") {
    run("HOLD CTRL\nHOLD a\nSTOP_PAYLOAD\nSTRINGLN NEVER\n"); check(mock::reports.size()==3,"no tail after canonical stop"); exact(2,{});
  } else if (n == "stop_inside_function_loop") {
    run("FUNCTION stopit()\nHOLD CTRL\nSTOP_PAYLOAD\nEND_FUNCTION\nWHILE TRUE\nIF TRUE THEN\nstopit()\nEND_IF\nEND_WHILE\nSTRINGLN NEVER\n"); exact(0,bytes(1)); exact(1,{});
  } else if (n == "inactive_ownership_commands") {
    run("IF FALSE THEN\nHOLD CTRL\nINJECT_MOD SHIFT\nRESET\nSTOP_PAYLOAD\nEND_IF\nWHILE FALSE\nHOLD a\nEND_WHILE\nSTRINGLN ok\n");
    check(mock::text=="ok\n","inactive ownership/stop side effects absent"); check(mock::reports.size()==6,"only expected visible output");
  } else if (n == "functions_loops_share_ownership") {
    run("FUNCTION held()\nHOLD CTRL\nRETURN 1\nEND_FUNCTION\nVAR $n = held()\nWHILE $n < 3\nIF $n == 1 THEN\nHOLD a\nELSE\nRELEASE a\nEND_IF\n$n = ($n+1)\nEND_WHILE\nRELEASE CTRL\n");
    exact(0,bytes(1)); exact(1,bytes(1,{4})); exact(2,bytes(1)); exact(3,{});
  } else if (n == "define_repeat_ownership_and_text") {
    run("DEFINE #KEY CTRL\nHOLD #KEY\nREPEAT 2\nSTRING x\nREPLAY 1\nRELEASE #KEY\nREPEAT 2\n");
    check(mock::reports.size()==6,"idempotent repeated hold/release and text repeat"); exact(0,bytes(1)); exact(1,bytes(1,{0x1b})); exact(3,bytes(1,{0x1b})); exact(5,{});
  } else if (n == "default_delay_ownership") {
    run("DEFAULT_DELAY 25\nHOLD CTRL\nRELEASE CTRL\nSTRING x\n");
    check(mock::reports[1].time-mock::reports[0].time>=25,"default delay applies hold"); check(mock::reports[2].time-mock::reports[1].time>=25,"default delay applies release");
  } else if (n == "eof_releases_owned") {
    run("HOLD CTRL\nHOLD a\n"); exact(2,{});
  } else if (n == "cancel_during_delay") {
    held("HOLD CTRL\nDELAY 100000\nSTRINGLN NEVER\n"); mock::tick(40); duckscript::stop(); com::update(); idle(); exact(mock::reports.size()-1,{});
  } else if (n == "cancel_during_string") {
    held("HOLD CTRL\nSTRING abcdefghijklmnopqrstuvwxyz\nSTRINGLN NEVER\n");
    for (unsigned i=0;i<20000 && mock::reports.size()<3;++i) mock::tick();
    duckscript::stop(); size_t size=mock::reports.size(); for(unsigned i=0;i<30;++i)mock::tick();
    check(mock::reports.size()==size,"no text after cancellation"); idle(); exact(size-1,{});
  } else if (n == "cancel_dead_key_second_stroke") {
    held("LOCALE DE\nHOLD CTRL\nSTRING ^\n"); for(unsigned i=0;i<20000 && mock::reports.size()<2;++i) mock::tick();
    exact(1,bytes(1,{0x35})); duckscript::stop(); com::update(); check(mock::reports.size()==3,"spacing stroke cancelled"); idle();
  } else if (n == "runtime_error_releases_owned") {
    start("VAR $x=1\nVAR $d=0\nHOLD CTRL\n$x=($x/$d)\nSTRINGLN NEVER\n"); mock::drain();
    check(duckscript::lastError().indexOf("zero")>=0,"runtime divide diagnostic"); exact(1,{}); idle();
  } else if (n == "function_depth_error_releases") {
    start("FUNCTION again()\nHOLD CTRL\nagain()\nEND_FUNCTION\nagain()\n"); mock::drain();
    check(duckscript::lastError().length(),"bounded recursion failure"); exact(mock::reports.size()-1,{}); idle();
  } else if (n == "loop_budget_error_releases") {
    start("HOLD CTRL\nWHILE TRUE\nEND_WHILE\n"); mock::drain(150000);
    check(duckscript::lastError().indexOf("WHILE stalled")>=0,"bounded no-progress loop error"); exact(mock::reports.size()-1,{}); idle();
  } else if (n == "storage_read_error_releases") {
    held("HOLD CTRL\nWHILE TRUE\nDELAY 1\nEND_WHILE\nSTRINGLN NEVER\n"); mock::failReadAt=0; mock::drain();
    check(duckscript::lastError().indexOf("read")>=0,"source fault diagnostic"); exact(mock::reports.size()-1,{}); idle();
  } else if (n == "hold_queue_refusal_no_commit") {
    local(); mock::usbAccept=false; check(!hid_backend::hold(1,4),"hold refusal"); check(!hid_backend::hasPersistent(),"failed hold not logically owned");
    check(mock::reports.empty(),"no accepted report on refusal"); mock::usbAccept=true; check(hid_backend::hold(1,4),"hold retry"); exact(0,bytes(1,{4})); hid_backend::cancelReport(); idle();
  } else if (n == "release_refusal_clears_logical_owner") {
    local(); check(hid_backend::hold(1,4),"hold"); mock::usbAccept=false;
    check(!hid_backend::release(1,4),"release awaits endpoint"); check(!hid_backend::hasPersistent(),"logical owner cleared on refusal");
    uint8_t key=5; check(!hid_backend::beginReport(0,&key,1),"pending release priority"); check(mock::reports.size()==1,"no overtaking press");
    mock::usbAccept=true; com::update(); exact(1,{}); check(hid_backend::beginReport(0,&key,1),"press resumes after clearing"); hid_backend::cancelReport(); idle();
  } else if (n == "stop_release_refusal_priority") {
    held("HOLD CTRL\nDELAY 100000\n"); mock::usbAccept=false; duckscript::stop();
    check(!hid_backend::hasPersistent(),"STOP clears logical ownership"); check(hid_backend::clearing(),"zero obligation pending");
    check(com::executeNow("STRING x"),"new live work accepted but release priority"); for(unsigned i=0;i<40;++i) { mock::tick(); } check(mock::reports.size()==1,"no press overtakes zero");
    mock::usbAccept=true; mock::drain(); exact(1,{}); exact(2,bytes(0,{0x1b})); idle();
  } else if (n == "reset_refusal_waits_before_tail") {
    held("HOLD CTRL\nRESET\nSTRING x\n"); mock::usbAccept=false;
    for(unsigned i=0;i<40;++i) { mock::tick(); } check(!hid_backend::hasPersistent(),"RESET intent clears"); check(com::busy(),"RESET waits for accepted clearing"); check(mock::reports.size()==1,"tail cannot overtake");
    mock::usbAccept=true; mock::drain(); exact(1,{}); exact(2,bytes(0,{0x1b})); idle();
  } else if (n == "disconnect_poll_cancels_owned") {
    held("HOLD CTRL\nDELAY 100000\nSTRINGLN NEVER\n"); mock::usbMounted=false; mock::usbReady=false; mock::tick();
    check(!duckscript::running(),"disconnect cancels script"); check(!hid_backend::hasPersistent(),"disconnect clears logical ownership"); check(mock::reports.size()==1,"no claim of delivered disconnected release");
    check(duckscript::lastError().indexOf("disconnected")>=0,"transport diagnostic"); mock::usbMounted=mock::usbReady=true; com::update(); exact(1,{}); idle();
  } else if (n == "disconnect_event_reconnect_between_ticks") {
    held("HOLD CTRL\nDELAY 100000\n"); check(USB.stopped!=nullptr,"production USB callback registered");
    USB.stopped(nullptr,"USB",ARDUINO_USB_STOPPED_EVENT,nullptr); // No physical USB calls.
    mock::tick(); check(!duckscript::running(),"latched disconnect not missed when already remounted"); exact(1,{}); idle();
  } else if (n == "backpressure_is_not_disconnect") {
    held("HOLD CTRL\nSTRING x\nRELEASE CTRL\n"); mock::usbReady=false;
    for(unsigned i=0;i<40;++i) { mock::tick(); } check(duckscript::running() && hid_backend::hasPersistent(),"mounted endpoint refusal preserves eligible ownership");
    check(!duckscript::lastError().length(),"no false disconnect"); mock::usbReady=true; mock::drain(); idle();
  } else if (n == "live_disconnect_clears_idle_hold") {
    local(); command("HOLD CTRL"); check(hid_backend::hasPersistent() && !com::busy(),"live hold persists between commands");
    mock::usbReady=false; mock::usbMounted=false; com::update(); check(!hid_backend::hasPersistent(),"idle live owner cleared");
    mock::usbReady=mock::usbMounted=true; com::update(); exact(1,{}); idle();
  } else if (n == "new_script_clears_live_hold") {
    local(); command("HOLD CTRL"); mock::file("next.txt","STRINGLN x\n"); check(duckscript::run("next.txt"),"new script accepted"); mock::drain();
    exact(1,{}); exact(2,bytes(0,{0x1b})); idle();
  } else if (n == "web_cli_cannot_release_script_hold") {
    held("HOLD CTRL\nDELAY 100000\n"); check(!com::executeNow("RELEASE CTRL"),"web admission rejected");
    cli::parse("send RESET", mock::print); check(hid_backend::hasPersistent(),"CLI cannot mutate script");
    check(com::submissionError().indexOf("Busy")>=0,"ownership diagnostic"); duckscript::stop(); idle();
  } else if (n == "live_holds_survive_commands_until_reset") {
    local(); command("HOLD CTRL"); command("STRING x"); exact(1,bytes(1,{0x1b})); exact(2,bytes(1));
    command("RESET"); exact(3,{}); command("STRING x"); exact(4,bytes(0,{0x1b})); idle();
  } else if (n == "new_script_after_cancel_no_leak") {
    held("HOLD CTRL\nHOLD a\nDELAY 100000\n"); duckscript::stop(); mock::file("next.txt","STRINGLN x\n");
    check(duckscript::run("next.txt"),"new run after cancellation"); size_t i=mock::reports.size(); mock::drain(); exact(i,bytes(0,{0x1b})); idle();
  } else if (n == "hid_mode_off_releases_owner") {
    run("HOLD CTRL\nATTACKMODE OFF\nHOLD a\nSTRING NEVER\nATTACKMODE HID\nSTRINGLN x\n"); exact(1,{}); exact(2,bytes(0,{0x1b}));
  } else if (n == "multiline_owned_reports_spiffs_sd") {
    for(const char *source:{"stage11.txt","sd:stage11.txt"}) {
      run("HOLD CTRL\nSTRINGLN\nx\ny\nEND_STRINGLN\nRELEASE CTRL\n",source);
      exact(1,bytes(1,{0x1b})); exact(3,bytes(1,{0x28})); exact(5,bytes(1,{0x1c})); exact(7,bytes(1,{0x28})); exact(9,{});
    }
  } else if (n == "malformed_hold_zero_hid") {
    for(const char *s:{"HOLD\n","HOLD a b\n","HOLD CTRL-a\n","HOLD NO_SUCH_KEY\n","HOLD 0x04\n"}) reject(s,"HOLD");
  } else if (n == "malformed_release_zero_hid") {
    for(const char *s:{"RELEASE\n","RELEASE ALL\n","RELEASE CTRL SHIFT\n","RELEASE a()\n"}) reject(s,"RELEASE");
  } else if (n == "malformed_inject_mod_zero_hid") {
    for(const char *s:{"INJECT_MOD a\n","INJECT_MOD 1\n","INJECT_MOD CTRL SHIFT\n","INJECT_MOD ALT-CTRL\n"}) reject(s,"INJECT_MOD");
  } else if (n == "reset_stop_args_zero_hid") {
    for(const char *s:{"RESET now\n","STOP_PAYLOAD now\n"}) reject(s,"no arguments");
  } else if (n == "ownership_command_prefixes_rejected") {
    for(const char *s:{"HOLDER a\n","RELEASED a\n","INJECT_MODIFIER CTRL\n","RESETTING\n","STOP_PAYLOADS\n"}) reject(s,"Unsupported command");
  } else if (n == "new_command_function_collisions") {
    for(const char *s:{"FUNCTION HOLD()\nEND_FUNCTION\n","FUNCTION RELEASE()\nEND_FUNCTION\n","FUNCTION RESET()\nEND_FUNCTION\n","FUNCTION INJECT_MOD()\nEND_FUNCTION\n","FUNCTION STOP_PAYLOAD()\nEND_FUNCTION\n"}) reject(s,"collides");
  } else if (n == "comment_text_literals_not_ownership") {
    run("REM_BLOCK\nHOLD CTRL\nRESET\nEND_REM\nSTRINGLN\nHOLD CTRL\nSTOP_PAYLOAD\nEND_STRINGLN\n"); check(mock::text=="HOLD CTRL\nSTOP_PAYLOAD\n","block data remains text");
  } else if (n == "case_tabs_and_modifier_aliases") {
    run("\thold\tcommand\nrelease\tGUI\nINJECT_MOD\trightwindows\n"); exact(0,bytes(8)); exact(1,{}); exact(2,bytes(0x80)); exact(3,{});
  } else if (n == "direct_report_overflow_null_validation") {
    local(); uint8_t keys[7]={4,5,6,7,8,9,10}; check(!hid_backend::beginReport(0,keys,7),"too many raw arguments reject"); check(*hid_backend::reportError(),"error distinct from refusal");
    check(!hid_backend::beginReport(0,nullptr,1),"null nonzero reject"); check(mock::reports.empty(),"no invalid report queued"); idle();
  } else if (n == "repeated_ownership_stress") {
    local();
    for(unsigned i=0;i<2000;++i) {
      check(hid_backend::hold(1,4),"stress hold"); check(hid_backend::hold(1,4),"stress duplicate");
      check(hid_backend::release(1,4),"stress release"); check(hid_backend::release(1,4),"stress idempotent release");
    } check(mock::reports.size()==4000,"bounded one transition each"); idle();
  } else if (n == "transient_release_refusal_restores_owned") {
    held("HOLD CTRL\nSTRING x\nRELEASE CTRL\n");
    for(unsigned i=0;i<20000 && mock::reports.size()<2;++i) mock::tick();
    mock::usbAccept=false;
    for(unsigned i=0;i<30;++i) mock::tick();
    check(mock::reports.size()==2 && hid_backend::hasPersistent(),"refused transient release does not drop owner");
    mock::usbAccept=true; mock::drain(); exact(2,bytes(1)); exact(3,{}); idle();
  } else if (n == "eof_release_refusal_clears_logical_owner") {
    held("HOLD CTRL\n"); mock::usbAccept=false; mock::drain();
    check(!hid_backend::hasPersistent() && hid_backend::clearing(),"EOF clears immediately, release still pending");
    check(mock::reports.size()==1,"no false accepted release"); mock::usbAccept=true; com::update(); exact(1,{}); idle();
  } else if (n == "cancel_pending_hold_before_acceptance") {
    start("HOLD CTRL\nSTRINGLN NEVER\n"); mock::usbAccept=false;
    for(unsigned i=0;i<100;++i) mock::tick();
    check(com::busy() && !hid_backend::hasPersistent(),"refused HOLD pending but unowned");
    duckscript::stop(); mock::usbAccept=true; com::update(); check(mock::reports.empty(),"cancelled unaccepted HOLD produces no stale report"); idle();
  } else if (n == "disconnect_during_text_cancels_tail") {
    held("HOLD CTRL\nSTRING abcdef\nSTRINGLN NEVER\n");
    for(unsigned i=0;i<20000 && mock::reports.size()<2;++i) mock::tick();
    mock::usbMounted=mock::usbReady=false; mock::tick(); check(!hid_backend::hasPersistent() && !duckscript::running(),"loss cancels transient and persistent work");
    mock::usbMounted=mock::usbReady=true; com::update(); exact(mock::reports.size()-1,{}); size_t total=mock::reports.size();
    for(unsigned i=0;i<30;++i) { mock::tick(); } check(mock::reports.size()==total,"no stale reconnect text"); idle();
  } else if (n == "while_condition_runtime_error_releases") {
    start("VAR $d=1\nHOLD CTRL\nWHILE 1/$d\n$d=0\nEND_WHILE\nSTRINGLN NEVER\n"); mock::drain();
    check(duckscript::lastError().indexOf("zero")>=0,"reevaluation error"); exact(1,{}); idle();
  } else if (n == "function_return_seek_error_releases") {
    std::string source="FUNCTION own()\nHOLD CTRL\nRETURN\nEND_FUNCTION\nown()\nSTRINGLN NEVER\n";
    held(source); mock::failSeekAt=source.find("STRINGLN"); mock::drain();
    check(duckscript::lastError().indexOf("seek error")>=0,"failed return seek"); exact(1,{}); idle();
  } else if (n == "source_changed_while_owned_releases") {
    held("HOLD CTRL\nDELAY 30\nSTRINGLN NEVER\n"); mock::sourceSizeIncrease=1; mock::drain();
    check(duckscript::lastError().indexOf("changed or unavailable")>=0,"source mutation rejected"); exact(1,{}); idle();
  } else if (n == "next_script_after_disconnect_recovery") {
    held("HOLD CTRL\nDELAY 100000\n"); mock::usbReady=mock::usbMounted=false; mock::tick();
    mock::usbReady=mock::usbMounted=true; com::update(); mock::file("next.txt","STRINGLN x\n");
    check(duckscript::run("next.txt"),"new script after reconnect"); size_t i=mock::reports.size(); mock::drain(); exact(i,bytes(0,{0x1b})); idle();
  } else if (n == "atomic_event_callback_no_execution_lock") {
    held("HOLD CTRL\nDELAY 100000\n");
    { execution::Guard guard;
      std::thread event([] { for(unsigned i=0;i<1000;++i) USB.stopped(nullptr,"USB",ARDUINO_USB_STOPPED_EVENT,nullptr); });
      event.join(); check(hid_backend::hasPersistent(),"callback records loss without touching locked ownership");
    }
    mock::tick(); check(!duckscript::running(),"main loop processes coalesced loss"); exact(1,{}); idle();
  } else if (n == "implicit_function_return_owner_lifetime") {
    run("FUNCTION own()\nHOLD CTRL\nEND_FUNCTION\nown()\nSTRING x\n"); exact(1,bytes(1,{0x1b})); exact(2,bytes(1)); exact(3,{});
  } else if (n == "unsupported_inactive_hold_preflight") {
    reject("IF FALSE THEN\nHOLD UNKNOWN_KEY\nEND_IF\n","HOLD");
  } else if (n == "live_stop_payload_releases_idle_hold") {
    local(); command("HOLD CTRL"); command("STOP_PAYLOAD"); exact(1,{}); idle();
  } else if (n == "latched_disconnect_blocks_enqueue_before_update") {
    local(); check(hid_backend::hold(1,4),"owner acquired");
    USB.stopped(nullptr,"USB",ARDUINO_USB_STOPPED_EVENT,nullptr);
    uint8_t key=5;
    check(!hid_backend::beginReport(0,&key,1),"loss flag blocks stale enqueue before main-loop processing");
    check(mock::reports.size()==1,"no stale report after loss/reconnect");
    com::update(); exact(1,{}); idle();
  } else throw std::runtime_error("unknown test name");
}
int main(int argc,char **argv) {
  try { if(argc!=2)throw std::runtime_error("one test required"); test(argv[1]); std::cout<<"PASS "<<argv[1]<<" ("<<assertions<<" assertions)\n"; return 0; }
  catch(const std::exception &e) { std::cerr<<"FAIL "<<(argc>1?argv[1]:"args")<<": "<<e.what()<<'\n'; return 1; }
}
