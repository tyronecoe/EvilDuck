#include "host.h"
#include "FS.h"
#include "SD.h"
#include "USBMSC.h"
#include "USB.h"
#include "USBHIDKeyboard.h"
#include "hid_backend.h"
#include "internal_vars.h"
#include "duck_vars.h"
#include "duckscript.h"
#include "com.h"
#include "cli.h"
#include "attackmode.h"
#include "usb_msc.h"
#include "execution_guard.h"
#include <iostream>
#include <stdexcept>
#include <thread>
#include <atomic>

static unsigned assertions = 0;
static void check(bool ok, const char *why) { ++assertions; if (!ok) throw std::runtime_error(why); }
static void local() {
  mock::reset(); usb_msc::end(); mscMock::reset(); mscMock::beginOk=true;
  hid_backend::begin(); com::update(); mock::reports.clear();
}
static bool feedback(uint8_t mask) {
  return hid_backend::receiveLockReport(1, &mask, 1, hid_backend::lockSession());
}
static uint16_t read(const char *name) {
  uint16_t v=999; check(duck_vars::getNumeric(name,v),"device-backed numeric read"); return v;
}
static void start(const std::string &text, const char *source="stage12.txt") {
  mock::file(source,text.c_str()); check(duckscript::run(source),"script accepted");
}
static void finish() {
  mock::drain(150000); check(!duckscript::lastError().length(),"no script error");
  check(!hid_backend::hasPersistent() && mock::heldKeys.empty() && !mock::heldModifiers,"safe key release");
  check(!mock::blockingDelays,"cooperative no blocking delays");
}
static void reject(const std::string &text, const char *message) {
  start("STRINGLN MUST-NOT-APPEAR\n"+text); mock::drain();
  check(duckscript::lastError().indexOf(message)>=0,"preflight diagnostic");
  check(mock::reports.empty(),"preflight zero HID including earlier output");
}
static void waitCommand() {
  for(unsigned i=0;i<2000;++i) { mock::tick(); if(com::busy()) { mock::tick(); return; } }
  check(false,"command reached");
}
static void error(const char *why) {
  mock::drain(150000); check(duckscript::lastError().indexOf(why)>=0,"useful runtime diagnostic");
  check(!hid_backend::hasPersistent() && mock::heldKeys.empty() && !mock::heldModifiers,"error releases keys");
  check(!mock::blockingDelays,"error path cooperative");
}
static void live(const char *command) { check(com::executeNow(command),"live command accepted"); mock::drain(); }
static void test(const std::string &n) {
  local();
  if (n == "initial_unknown_not_false") {
    check(!hid_backend::lockState().known,"initial unknown"); check(read("$_RECEIVED_HOST_LOCK_LED_REPLY")==0,"no reply yet");
    uint16_t v=999; check(!duck_vars::getNumeric("$_CAPSLOCK_ON",v) && v==999,"unknown does not overwrite with FALSE");
    duck_expr::Error e; check(!duck_expr::evaluate("$_CAPSLOCK_ON",13,v,e,duck_vars::resolve),"unknown expression rejected");
    check(String(e.message).indexOf("unknown")>=0,"unknown diagnosis");
  } else if (n == "all_led_masks_and_padding") {
    for(uint8_t mask=0;mask<32;++mask) {
      check(feedback(mask),"all five descriptor LED bits valid");
      check(read("$_NUMLOCK_ON")==bool(mask&1),"Num bit0"); check(read("$_CAPSLOCK_ON")==bool(mask&2),"Caps bit1");
      check(read("$_SCROLLLOCK_ON")==bool(mask&4),"Scroll bit2"); check(read("$_RECEIVED_HOST_LOCK_LED_REPLY")==1,"observed reply");
    }
  } else if (n == "invalid_ids_lengths_null_padding") {
    uint8_t mask=2; check(!hid_backend::receiveLockReport(0,&mask,1,hid_backend::lockSession()),"no ID0 payload hook");
    check(!hid_backend::receiveLockReport(2,&mask,1,hid_backend::lockSession()),"wrong ID");
    check(!hid_backend::receiveLockReport(1,nullptr,1,hid_backend::lockSession()),"null");
    for(uint16_t size:{uint16_t(0),uint16_t(2),uint16_t(65535)}) check(!hid_backend::receiveLockReport(1,&mask,size,hid_backend::lockSession()),"invalid size");
    for(uint8_t bit:{uint8_t(0x20),uint8_t(0x40),uint8_t(0x80)})check(!feedback(bit),"padding rejected");
    check(!hid_backend::lockState().known,"malformed reports do not invent state");
  } else if (n == "actual_keyboard_output_virtual_hook") {
    uint8_t mask=7; mockKeyboard->_onOutput(1,&mask,1); check(read("$_CAPSLOCK_ON")==1,"actual subclass receives interrupt output");
    mockKeyboard->_onOutput(1,nullptr,0); check(hid_backend::lockState().leds==7,"unsafe SDK read bypassed");
  } else if (n == "actual_keyboard_control_set_report_hook") {
    uint8_t mask=1; mockKeyboard->_onSetFeature(1,&mask,1); check(read("$_NUMLOCK_ON")==1,"control SET_REPORT normalized hook");
    mask=0;mockKeyboard->_onSetFeature(2,&mask,1); check(read("$_NUMLOCK_ON")==1,"wrong control ID ignored");
  } else if (n == "duplicates_do_not_count_changes") {
    check(feedback(2),"first"); const auto before=hid_backend::lockState();
    for(unsigned i=0;i<1000;++i)check(feedback(2),"duplicate valid");
    const auto after=hid_backend::lockState(); check(after.changes[1]==before.changes[1],"duplicate no toggle");
    check(after.saved==2,"attach saved first state");
  } else if (n == "per_key_transition_counters") {
    feedback(0); feedback(1);feedback(3);feedback(7);feedback(5);feedback(4);feedback(0);
    const auto s=hid_backend::lockState();for(auto count:s.changes)check(count==2,"each key counts changes independently");
  } else if (n == "first_report_auto_saves_attach_state") {
    feedback(3);feedback(4);check(read("$_SAVED_NUMLOCK_ON")==1,"saved initial Num");check(read("$_SAVED_CAPSLOCK_ON")==1,"saved initial Caps");
    check(read("$_SAVED_SCROLLLOCK_ON")==0,"saved initial Scroll");check(read("$_SCROLLLOCK_ON")==1,"current differs");
  } else if (n == "explicit_save_updates_saved_state") {
    feedback(0);feedback(7);start("SAVE_HOST_KEYBOARD_LOCK_STATE\n");finish();feedback(0);
    check(read("$_SAVED_CAPSLOCK_ON")==1&&read("$_SAVED_NUMLOCK_ON")==1&&read("$_SAVED_SCROLLLOCK_ON")==1,"explicit saved all");check(mock::reports.empty(),"SAVE no HID");
  } else if (n == "save_unknown_fails_truthfully") {
    start("SAVE_HOST_KEYBOARD_LOCK_STATE\nSTRINGLN NEVER\n");error("unknown");check(mock::reports.empty(),"unknown SAVE no HID");
  } else if (n == "saved_unknown_expression") {
    start("VAR $x=$_SAVED_CAPSLOCK_ON\nSTRINGLN NEVER\n");error("unknown");check(mock::reports.empty(),"unknown saved value fails before output");
  } else if (n == "readonly_assignment_preflight") {
    reject("$_CAPSLOCK_ON=TRUE\n","read-only");
  } else if (n == "fake_internal_declaration_preflight") {
    reject("VAR $_JITTER_ENABLED=TRUE\n","Reserved internal");
  } else if (n == "fake_internal_define_alias_preflight") {
    reject("DEFINE $_RECEIVED_HOST_LOCK_LED_REPLY=TRUE\n","Reserved internal");
  } else if (n == "read_cannot_shadow_internal") {
    reject("READ file.txt $_NUMLOCK_ON\n","Reserved internal");
  } else if (n == "unsupported_read_preflight") {
    reject("VAR $x=$_EXFIL_MODE_ENABLED\n","Unsupported internal variable"); // Stage14 implements jitter; retain unsupported-property coverage.
  } else if (n == "unsupported_write_preflight") {
    reject("$_CURRENT_ATTACKMODE=3\n","Reserved internal");
  } else if (n == "all_native_registry_names_reserved") {
    // Matrix also inventories long properties which exceed normal user-name size.
    const char *names[]={"$_BUTTON_ENABLED", "$_BUTTON_PUSH_RECEIVED", "$_BUTTON_TIMEOUT", "$_BUTTON_USER_DEFINED", "$_CAPSLOCK_ON", "$_CURRENT_ATTACKMODE", "$_CURRENT_PID", "$_CURRENT_VID", "$_EXFIL_LEDS_ENABLED", "$_EXFIL_MODE_ENABLED", "$_HOST_CONFIGURATION_REQUEST_COUNT", "$_INJECTING_LEDS_ENABLED", "$_JITTER_ENABLED", "$_JITTER_MAX", "$_LED_CONTINUOUS_SHOW_STORAGE_ACTIVITY", "$_LED_SHOW_CAPS", "$_LED_SHOW_NUM", "$_LED_SHOW_SCROLL", "$_NUMLOCK_ON", "$_RANDOM_CHAR_KEYCODE", "$_RANDOM_INT", "$_RANDOM_LETTER_KEYCODE", "$_RANDOM_LOWER_LETTER_KEYCODE", "$_RANDOM_MAX", "$_RANDOM_MIN", "$_RANDOM_NUMBER_KEYCODE", "$_RANDOM_SEED", "$_RANDOM_SPECIAL_KEYCODE", "$_RANDOM_UPPER_LETTER_KEYCODE", "$_RECEIVED_HOST_LOCK_LED_REPLY", "$_SAVED_CAPSLOCK_ON", "$_SAVED_NUMLOCK_ON", "$_SAVED_SCROLLLOCK_ON", "$_SCROLLLOCK_ON", "$_STORAGE_ACTIVITY_TIMEOUT", "$_STORAGE_LEDS_ENABLED", "$_SYSTEM_LEDS_ENABLED"};
    for(auto name:names) {check(internal_vars::reserved(name,strlen(name)),"native name protected");String e;duck_vars::Symbols symbols;
      check(symbols.declare(name,duck_vars::Type::Numeric,false,e)<0,"no fake native declaration");}
    check(!internal_vars::reserved("$_OS",4),"OS stays extension defined");
  } else if (n == "os_extension_and_user_variables_preserved") {
    start("VAR $_OS=7\nVAR $_CUSTOM=8\nSTRINGLN os=$_OS custom=$_CUSTOM\n");finish();check(mock::text=="os=7 custom=8\n","explicit extension/user globals preserved");
  } else if (n == "timeout_extension_assignment_and_limits") {
    String e; check(duck_vars::assign("$_EVILDUCK_LOCK_TIMEOUT","65535",false,e),"max timeout write");check(internal_vars::lockTimeout()==65535,"uint16 max");
    check(!duck_vars::assign("$_EVILDUCK_LOCK_TIMEOUT","0",false,e),"reject zero");check(internal_vars::lockTimeout()==65535,"invalid write atomic");
    check(!duck_vars::assign("$_EVILDUCK_LOCK_TIMEOUT","65536",false,e),"literal overflow");
    check(!duck_vars::assign("$_EVILDUCK_LOCK_TIMEOUT","1",true,e),"VAR cannot shadow writable internal");
  } else if (n == "timeout_assignment_expression_shared_evaluator") {
    start("VAR $t=5\n$_EVILDUCK_LOCK_TIMEOUT=($t^2)\nWAIT_FOR_CAPS_ON\nSTRINGLN NEVER\n");error("timeout");check(mock::now<5000,"expression25ms applied");
  } else if (n == "constant_invalid_timeout_preflight") {
    reject("$_EVILDUCK_LOCK_TIMEOUT=(5-5)\n", "1..65535");
  } else if (n == "live_wait_stop_cancellable") {
    check(com::executeNow("WAIT_FOR_CAPS_ON"), "live wait accepted");
    for (unsigned i=0;i<10;++i) { mock::tick(); }
    check(com::busy(), "live wait pending"); duckscript::stop(); com::update();
    check(!com::busy() && !hid_backend::hasPersistent(), "live STOP clears wait");
  } else if (n == "timeout_resets_between_scripts") {
    start("$_EVILDUCK_LOCK_TIMEOUT=20\n");finish();check(internal_vars::lockTimeout()==5000,"end run resets policy");
    start("DELAY 20\n");check(internal_vars::lockTimeout()==5000,"new run default");finish();
  } else if (n == "no_internal_symbol_table_consumption") {
    feedback(0); duck_vars::Symbols symbols;String e;
    for(unsigned i=0;i<DUCKSCRIPT_MAX_VARIABLES;++i)check(symbols.declare("$v"+String(i),duck_vars::Type::Numeric,false,e)>=0,"ordinary table fills");
    uint16_t v=99;check(duck_vars::Symbols::resolve("$_CAPSLOCK_ON",13,v,&symbols)==duck_expr::Lookup::Number,"internal read independent of full user table");
    check(symbols.declare("$_EVILDUCK_LOCK_TIMEOUT",duck_vars::Type::Numeric,true,e)>=0,"writable internal no slot");
  } else if (n == "canonical_on_off_waits_all_keys") {
    const char *names[]={"NUM","CAPS","SCROLL"};
    for(unsigned bit=0;bit<3;++bit)for(unsigned on=0;on<2;++on) {
      local();feedback(on?0:7);start(std::string("WAIT_FOR_")+names[bit]+(on?"_ON\n":"_OFF\n")+"STRINGLN ok\n");waitCommand();
      for(unsigned i=0;i<10;++i) { mock::tick(); }check(mock::text=="","wait no premature output");feedback(on?(1<<bit):0);finish();check(mock::text=="ok\n","observed desired state completes");
    }
  } else if (n == "wait_already_desired_is_immediate") {
    feedback(0); start("WAIT_FOR_CAPS_OFF\nWAIT_FOR_NUM_OFF\nWAIT_FOR_SCROLL_OFF\nSTRINGLN ok\n");finish();check(mock::now<1000,"known desired no wait timeout");
  } else if (n == "unknown_off_does_not_succeed") {
    start("$_EVILDUCK_LOCK_TIMEOUT=15\nWAIT_FOR_CAPS_OFF\nSTRINGLN NEVER\n");error("timeout");check(mock::text=="","unknown not falsely OFF");
  } else if (n == "wait_unknown_becomes_observed_off") {
    start("WAIT_FOR_CAPS_OFF\nSTRINGLN ok\n");waitCommand();check(mock::reports.empty(),"wait no HID");feedback(0);finish();check(mock::text=="ok\n","observed OFF valid");
  } else if (n == "change_unknown_first_report_is_baseline") {
    start("WAIT_FOR_CAPS_CHANGE\nSTRINGLN ok\n");waitCommand();feedback(2);for(unsigned i=0;i<10;++i) { mock::tick(); }
    check(mock::text=="","first report not imaginary toggle");feedback(0);finish();check(mock::text=="ok\n","second different report toggles");
  } else if (n == "change_duplicate_reports_do_not_finish") {
    feedback(0);start("$_EVILDUCK_LOCK_TIMEOUT=20\nWAIT_FOR_CAPS_CHANGE\nSTRINGLN NEVER\n");
    for(unsigned i=0;i<100&&duckscript::running();++i){feedback(0);mock::tick();}error("timeout");check(mock::text=="","duplicates no false change");
  } else if (n == "rapid_changes_between_ticks_not_lost") {
    feedback(0);start("WAIT_FOR_CAPS_CHANGE\nSTRINGLN ok\n");waitCommand();feedback(2);feedback(0);finish();check(mock::text=="ok\n","counter sees return-to-baseline toggle");
  } else if (n == "change_all_three_independent") {
    for(unsigned bit=0;bit<3;++bit){local();feedback(0);const char *name=bit==0?"NUM":bit==1?"CAPS":"SCROLL";
      start(std::string("WAIT_FOR_")+name+"_CHANGE\nSTRINGLN ok\n");waitCommand();feedback(1<<(bit==0?1:0));for(unsigned i=0;i<5;++i) { mock::tick(); }check(mock::text=="","other lock does not satisfy wait");
      feedback(1<<bit);finish();check(mock::text=="ok\n","correct lock transition");}
  } else if (n == "timeout_wrap_safe") {
    mock::now=UINT32_MAX-20;start("$_EVILDUCK_LOCK_TIMEOUT=40\nWAIT_FOR_SCROLL_ON\n");error("timeout");check(mock::now<200,"millis wrap survived");
  } else if (n == "malformed_lock_command_preflight") {
    reject("WAIT_FOR_CAPS_ON 20\n","take no arguments");
  } else if (n == "malformed_save_restore_preflight") {
    reject("RESTORE_HOST_KEYBOARD_LOCK_STATE 1\n","take no arguments");
  } else if (n == "lock_commands_function_collision") {
    reject("FUNCTION WAIT_FOR_CAPS_ON()\nEND_FUNCTION\n","collides");
  } else if (n == "inactive_branch_no_wait_or_save") {
    start("IF FALSE THEN\nWAIT_FOR_CAPS_ON\nSAVE_HOST_KEYBOARD_LOCK_STATE\nRESTORE_HOST_KEYBOARD_LOCK_STATE\nEND_IF\nSTRINGLN ok\n");finish();check(mock::text=="ok\n"&&mock::now<1000,"inactive operations no effects");
  } else if (n == "lock_variables_if_define_function_return") {
    feedback(2);start("DEFINE #ON 1\nFUNCTION check_lock()\nRETURN $_CAPSLOCK_ON\nEND_FUNCTION\nIF check_lock()==#ON THEN\nSTRINGLN yes\nELSE\nSTRINGLN no\nEND_IF\n");finish();check(mock::text=="yes\n","same evaluator in call/return/condition");
  } else if (n == "lock_variables_while_updates") {
    feedback(2);start("WHILE $_CAPSLOCK_ON\nDELAY 5\nEND_WHILE\nSTRINGLN done\n");for(unsigned i=0;i<100;++i) { mock::tick(); }check(duckscript::running(),"loop reads actual lock state");feedback(0);finish();check(mock::text=="done\n","loop observes transition");
  } else if (n == "wait_inside_nested_control_and_function") {
    feedback(0);start("FUNCTION wait_lock()\nIF TRUE THEN\nWAIT_FOR_NUM_ON\nEND_IF\nRETURN $_NUMLOCK_ON\nEND_FUNCTION\nVAR $n=0\nWHILE $n<1\nIF wait_lock() THEN\nSTRINGLN yes\nEND_IF\n$n=$n+1\nEND_WHILE\n");
    for(unsigned i=0;i<100;++i) { mock::tick(); }feedback(1);finish();check(mock::text=="yes\n","cooperative continuation through mixed control");
  } else if (n == "numeric_interpolation_observed_state") {
    feedback(5);start("STRINGLN n=$_NUMLOCK_ON c=$_CAPSLOCK_ON s=$_SCROLLLOCK_ON\n");finish();check(mock::text=="n=1 c=0 s=1\n","compatible text interpolation uses registry");
  } else if (n == "unknown_interpolation_runtime_error") {
    start("STRINGLN $_CAPSLOCK_ON\n");error("unknown");check(mock::reports.empty(),"unknown internal never typed literally or as zero");
  } else if (n == "unsupported_interpolation_runtime_error") {
    start("STRINGLN $_EXFIL_MODE_ENABLED\n");error("unsupported");check(mock::reports.empty(),"unsupported internal not inert text");
  } else if (n == "restore_noop_no_keyboard_output") {
    feedback(3);start("RESTORE_HOST_KEYBOARD_LOCK_STATE\n");finish();check(mock::reports.empty(),"already same acknowledged no output");
  } else if (n == "restore_unknown_current_saved_rejected") {
    start("RESTORE_HOST_KEYBOARD_LOCK_STATE\nSTRINGLN NEVER\n");error("unknown");check(mock::reports.empty(),"no guessed toggle");
  } else if (n == "restore_requires_hid_enabled") {
    feedback(0);start("ATTACKMODE OFF\nRESTORE_HOST_KEYBOARD_LOCK_STATE\n");error("HID enabled");check(mock::reports.empty(),"no mode-disabled injection");
  } else if (n == "restore_rejects_held_modifier") {
    feedback(0);feedback(2);start("HOLD CTRL\nRESTORE_HOST_KEYBOARD_LOCK_STATE\nSTRINGLN NEVER\n");error("persistent keys");check(mock::reports.size()==2,"hold then safety clear only");
  } else if (n == "restore_rejects_held_key") {
    feedback(0);feedback(2);start("HOLD CAPSLOCK\nRESTORE_HOST_KEYBOARD_LOCK_STATE\n");error("persistent keys");check(mock::reports.size()==2,"no duplicate held lock edge");
  } else if (n == "restore_three_keys_ack_exact_reports") {
    feedback(0);feedback(7);start("RESTORE_HOST_KEYBOARD_LOCK_STATE\nSTRINGLN restored\n");uint8_t observed=7;size_t handled=0;
    for(unsigned i=0;i<20000&&duckscript::running();++i){mock::tick();while(handled<mock::reports.size()){
      const auto r=mock::reports[handled++];if(r.bytes[2]==0x53)observed^=1;else if(r.bytes[2]==0x39)observed^=2;else if(r.bytes[2]==0x47)observed^=4;else continue;
      check(r.id==1&&r.instance==0&&r.bytes[0]==0&&r.bytes[1]==0,"restore exact report ID/zero modifiers/reserved");
      for(unsigned k=3;k<8;++k) { check(!r.bytes[k],"one key zero padding"); } check(feedback(observed),"mock real ACK");
    }}finish();check(observed==0&&mock::text=="restored\n","all three restored only with evidence");
    check(mock::reports[0].bytes[2]==0x53&&mock::reports[2].bytes[2]==0x39&&mock::reports[4].bytes[2]==0x47,"deterministic Num Caps Scroll order");
    for(unsigned i=1;i<6;i+=2)for(auto b:mock::reports[i].bytes)check(!b,"release zero report before next toggle");
  } else if (n == "restore_no_ack_times_out_no_retoggle") {
    feedback(0);feedback(2);start("$_EVILDUCK_LOCK_TIMEOUT=40\nRESTORE_HOST_KEYBOARD_LOCK_STATE\nSTRINGLN NEVER\n");error("timeout");
    unsigned taps=0;for(auto r:mock::reports)if(r.bytes[2]==0x39)++taps;check(taps==1&&mock::text=="","one attempt no fake ACK/repeated toggle");
  } else if (n == "restore_wrong_feedback_not_ack") {
    feedback(0);feedback(2);start("$_EVILDUCK_LOCK_TIMEOUT=40\nRESTORE_HOST_KEYBOARD_LOCK_STATE\nSTRINGLN NEVER\n");for(unsigned i=0;i<100&&duckscript::running();++i){mock::tick();feedback(2);}error("timeout");check(mock::text=="","wrong repeated state no ACK");
  } else if (n == "restore_rechecks_pending_toggle_after_backpressure") {
    feedback(0);feedback(2);mock::usbAccept=false;start("RESTORE_HOST_KEYBOARD_LOCK_STATE\nSTRINGLN restored\n");
    for(unsigned i=0;i<100;++i) { mock::tick(); }
    check(mock::reports.empty(), "endpoint refused planned tap");feedback(0);mock::usbAccept=true;finish();
    for(auto r:mock::reports) check(r.bytes[2]!=0x39, "no stale Caps toggle after host already restored");
    check(mock::text=="restored\n", "observed target completes without stale injection");
  } else if (n == "restore_default_delay_after_success") {
    feedback(0);start("$_EVILDUCK_LOCK_TIMEOUT=10\nDEFAULT_DELAY 30\nRESTORE_HOST_KEYBOARD_LOCK_STATE\nSTRINGLN ok\n");
    finish();check(mock::text=="ok\n", "completed restore deadline does not affect default delay");
  } else if (n == "restore_backpressure_timeout") {
    feedback(0);feedback(2);mock::usbAccept=false;start("$_EVILDUCK_LOCK_TIMEOUT=30\nRESTORE_HOST_KEYBOARD_LOCK_STATE\n");error("timeout");check(mock::reports.empty(),"refused enqueue no HID");mock::usbAccept=true;com::update();check(!hid_backend::clearing(),"clear retried");
  } else if (n == "stop_cancels_wait_and_releases_hold") {
    feedback(0);start("HOLD SHIFT\nWAIT_FOR_CAPS_ON\nSTRINGLN NEVER\n");for(unsigned i=0;i<100;++i) { mock::tick(); }check(hid_backend::hasPersistent(),"held during wait");duckscript::stop();com::update();
    check(!duckscript::running()&&!com::busy()&&!hid_backend::hasPersistent()&&!mock::heldModifiers,"STOP safe");feedback(2);mock::drain();check(mock::text=="","no pending tail");
  } else if (n == "stop_payload_inside_function_preserves_feedback") {
    feedback(2);start("FUNCTION quit()\nHOLD ALT\nSTOP_PAYLOAD\nEND_FUNCTION\nquit()\nSTRINGLN NEVER\n");finish();check(read("$_CAPSLOCK_ON")==1,"STOP does not erase host evidence");check(mock::text=="","tail stopped");
  } else if (n == "reset_preserves_observed_and_saved_state") {
    feedback(3);feedback(4);start("HOLD SHIFT\nRESET\nSTRINGLN c=$_CAPSLOCK_ON saved=$_SAVED_CAPSLOCK_ON\n");finish();check(mock::text=="c=0 saved=1\n","RESET clears ownership only");
  } else if (n == "runtime_timeout_releases_held_keys") {
    feedback(0);start("$_EVILDUCK_LOCK_TIMEOUT=15\nHOLD CTRL\nWAIT_FOR_CAPS_ON\n");error("timeout");check(mock::reports.back().bytes==std::array<uint8_t,8>{},"error accepted zero release");
  } else if (n == "cancel_restore_during_press") {
    feedback(0);feedback(2);start("RESTORE_HOST_KEYBOARD_LOCK_STATE\nSTRINGLN NEVER\n");
    for(unsigned i=0;i<2000&&mock::reports.empty();++i) { mock::tick(); }check(!mock::reports.empty(),"pressed lock key");duckscript::stop();com::update();
    check(mock::heldKeys.empty()&&!hid_backend::hasPersistent(),"cancel releases active tap");check(mock::text=="","restore tail cancelled");
  } else if (n == "disconnect_immediate_unknown_and_stale_token") {
    feedback(7);const auto old=hid_backend::lockSession();USB.stopped(nullptr,nullptr,ARDUINO_USB_STOPPED_EVENT,nullptr);
    check(!hid_backend::lockState().known&&!hid_backend::lockState().savedKnown,"callback immediate invalidation");uint8_t mask=0;
    check(!hid_backend::receiveLockReport(1,&mask,1,old),"old token rejects");com::update();check(read("$_RECEIVED_HOST_LOCK_LED_REPLY")==0,"reply reset");
    check(feedback(0),"new session observed");check(read("$_CAPSLOCK_ON")==0,"new evidence valid");
  } else if (n == "unmounted_reports_rejected") {
    feedback(2);mock::usbMounted=false;check(!feedback(0),"no observed disconnected report");check(!hid_backend::lockState().known,"unmounted read unknown without main tick");
    com::update();mock::usbMounted=true;com::update();check(!hid_backend::lockState().known,"reconnect not old feedback");
  } else if (n == "disconnect_cancels_wait_and_reconnect_clean") {
    feedback(0);start("HOLD ALT\nWAIT_FOR_CAPS_ON\nSTRINGLN NEVER\n");for(unsigned i=0;i<100;++i) { mock::tick(); }mock::usbMounted=false;USB.stopped(nullptr,nullptr,ARDUINO_USB_STOPPED_EVENT,nullptr);mock::tick();
    check(!duckscript::running()&&!hid_backend::hasPersistent(),"disconnect cancels ownership");check(duckscript::lastError().indexOf("disconnected")>=0,"transport diagnostic");
    mock::usbMounted=true;com::update();check(mock::heldKeys.empty()&&!mock::heldModifiers,"zero retry on reconnect");feedback(2);start("STRINGLN recovered\n");finish();check(mock::text=="recovered\n","new run no stale wait");
  } else if (n == "feedback_survives_separate_script_runs") {
    feedback(2);start("STRINGLN one=$_CAPSLOCK_ON\n");finish();start("STRINGLN two=$_CAPSLOCK_ON\n");finish();check(mock::text=="one=1\ntwo=1\n","device state distinct from script symbols");
  } else if (n == "live_cli_excluded_during_script_wait") {
    start("WAIT_FOR_CAPS_ON\n");waitCommand();check(!com::executeNow("SAVE_HOST_KEYBOARD_LOCK_STATE"),"live rejected while script owns");
    cli::parse("send RESTORE_HOST_KEYBOARD_LOCK_STATE", mock::print);check(mock::output.indexOf("Busy")>=0,"CLI truthful ownership");duckscript::stop();
  } else if (n == "live_save_restore_state") {
    feedback(2);live("SAVE_HOST_KEYBOARD_LOCK_STATE");check(hid_backend::lockState().saved==2,"live SAVE");live("RESTORE_HOST_KEYBOARD_LOCK_STATE");check(mock::reports.empty(),"live already desired no HID");
  } else if (n == "wait_command_backpressure_independent") {
    feedback(0);mock::usbReady=false;start("WAIT_FOR_NUM_ON\n");waitCommand();feedback(1);finish();check(mock::reports.empty(),"feedback wait independent of IN readiness");
  } else if (n == "feedback_during_input_preserves_reports") {
    feedback(0);start("HOLD ALT\nSTRINGLN ab\nRELEASE ALT\n");for(unsigned i=0;i<2000&&duckscript::running();++i){feedback(i&7);mock::tick();}finish();
    check(mock::reports.front().bytes[0]==4,"persistent modifier unaffected");check(!mock::heldModifiers,"release after OUT traffic");
  } else if (n == "callback_does_not_wait_on_executor_lock") {
    std::atomic<bool> complete{false};{execution::Guard guard;std::thread t([&]{uint8_t mask=2;complete=hid_backend::receiveLockReport(1,&mask,1,hid_backend::lockSession());});t.join();}
    check(complete&&read("$_CAPSLOCK_ON")==1,"OUT callback no executor lock");
  } else if (n == "concurrent_feedback_and_snapshot_reads") {
    std::atomic<bool> done{false};std::thread writer([&]{for(unsigned i=0;i<10000;++i){uint8_t mask=i&7;hid_backend::receiveLockReport(1,&mask,1,hid_backend::lockSession());}done=true;});
    for(unsigned i=0;i<10000;++i){const auto s=hid_backend::lockState();check(!s.known || s.leds<8,"snapshot bounded");}writer.join();check(hid_backend::lockState().known,"concurrent evidence retained");
  } else if (n == "concurrent_disconnect_never_revives_old_session") {
    for(unsigned i=0;i<100;++i){const auto token=hid_backend::lockSession();std::thread writer([&]{uint8_t mask=7;for(unsigned j=0;j<100;++j)hid_backend::receiveLockReport(1,&mask,1,token);});hid_backend::invalidateLockState();writer.join();
      check(!hid_backend::lockState().known&&!hid_backend::lockState().savedKnown,"stale concurrent callback cannot revive");}
  } else if (n == "transition_counter_crosses_16bit_boundary") {
    feedback(0);for(unsigned i=0;i<65537;++i)check(feedback(i%2?0:2),"bounded report path");check(hid_backend::lockState().changes[1]==65537,"32-bit counter does not alias after65536 transitions");
  } else if (n == "storage_requested_failed_registry_truthful") {
    mscMock::present=false;check(!attackmode::applyFromString("HID STORAGE"),"actual startup unavailable");
    check(read("$_EVILDUCK_STORAGE_REQUESTED")==1,"requested retained");check(read("$_EVILDUCK_STORAGE_ACTIVE")==0,"not false active");
    check(read("$_EVILDUCK_STORAGE_FAILED")==1&&read("$_EVILDUCK_STORAGE_STATE")==4,"actual failure reported");
  } else if (n == "storage_preparing_active_ejected_registry") {
    mscMock::put("/sys/usb_disk.img",4194304);check(attackmode::applyFromString("HID STORAGE"),"actual startup accepted");
    check(read("$_EVILDUCK_STORAGE_PREPARING")==1&&read("$_EVILDUCK_STORAGE_ACTIVE")==0,"preparing not ready");
    for(unsigned i=0;i<4;++i) { attackmode::update(); }check(read("$_EVILDUCK_STORAGE_ACTIVE")==1&&read("$_EVILDUCK_STORAGE_STATE")==2,"actual local media verified");
    check(mscMock::startCallback(0,false,true),"mock host eject");check(read("$_EVILDUCK_STORAGE_STATE")==3&&read("$_EVILDUCK_STORAGE_ACTIVE")==0,"ejected truth");
    check(read("$_EVILDUCK_STORAGE_REQUESTED")==1,"ejected request independent");
  } else if (n == "storage_retry_and_off_registry") {
    mscMock::present=false;attackmode::applyFromString("HID STORAGE");mscMock::present=true;mscMock::put("/sys/usb_disk.img",4194304);
    check(attackmode::applyFromString("HID STORAGE"),"actual retry accepted");for(unsigned i=0;i<4;++i) { attackmode::update(); }
    check(read("$_EVILDUCK_STORAGE_FAILED")==0&&read("$_EVILDUCK_STORAGE_ACTIVE")==1,"retry recovers");attackmode::setOff();
    check(read("$_EVILDUCK_HID_ENABLED")==0&&read("$_EVILDUCK_STORAGE_REQUESTED")==0&&read("$_EVILDUCK_STORAGE_STATE")==0,"logical off truthful not USB detach claim");
  } else if (n == "attackmode_does_not_fabricate_lock_state") {
    start("ATTACKMODE OFF\nATTACKMODE HID\nIF $_RECEIVED_HOST_LOCK_LED_REPLY THEN\nSTRINGLN wrong\nELSE\nSTRINGLN unknown\nEND_IF\n");finish();check(mock::text=="unknown\n","mode not guessed feedback");
  } else if (n == "storage_read_error_after_wait_releases_keys") {
    feedback(0);start("HOLD ALT\nWAIT_FOR_CAPS_ON\nWHILE TRUE\nEND_WHILE\n");for(unsigned i=0;i<100;++i) { mock::tick(); }mock::failSeekAt=mock::files["stage12.txt"].indexOf("WHILE");feedback(2);error("seek");
  } else if (n == "sd_spiffs_lock_fixture") {
    for(auto source:{"stage12.txt","sd:stage12.txt"}){local();feedback(2);start("IF $_CAPSLOCK_ON THEN\nSTRINGLN observed\nEND_IF\nWAIT_FOR_NUM_OFF\n",source);finish();check(mock::text=="observed\n","both mocked sources actual condition/wait");}
  } else if (n == "saved_state_invalidated_on_backend_begin") {
    feedback(7);hid_backend::begin();check(!hid_backend::lockState().known&&!hid_backend::lockState().savedKnown,"new USB initialization unknown");
  } else throw std::runtime_error("unknown test");
}
int main(int argc,char **argv) {
  try { if(argc!=2)return 2;test(argv[1]);std::cout<<"PASS "<<argv[1]<<" ("<<assertions<<" assertions)\n";return 0; }
  catch(const std::exception &e){std::cerr<<"FAIL "<<(argc>1?argv[1]:"?")<<": "<<e.what()<<"; "<<duckscript::lastError().c_str()<<"\n";return 1;}
}
