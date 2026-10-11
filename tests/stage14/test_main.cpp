#include "host.h"
#include "FS.h"
#include "duck_random.h"
#include "duck_vars.h"
#include "internal_vars.h"
#include "duckscript.h"
#include "duck_expr.h"
#include "script_parser.h"
#include "com.h"
#include "hid_backend.h"
#include "keyboard_locale.h"
#include <iostream>
#include <stdexcept>
#include <vector>
#include <string>
#include <array>
#include <cstring>
#include <fstream>
#include <sstream>

static unsigned assertions=0;
static uint32_t draws=0, fixed=0x80000000U, prng=1;
static std::vector<uint32_t> script;
static size_t cursor=0;
static bool seeded=false;
static uint32_t raw() {
  ++draws;
  if(cursor<script.size())return script[cursor++];
  if(seeded){prng=1664525U*prng+1013904223U;return prng;}
  return fixed;
}
static void check(bool b,const char *why) {++assertions;if(!b)throw std::runtime_error(why);}
static void reset() {mock::reset();hid_backend::begin();com::update();mock::reports.clear();draws=0;fixed=0x80000000U;script.clear();cursor=0;seeded=false;duck_random::source(raw);}
static void start(const std::string &text,const char *name="stage14.txt") {mock::file(name,text.c_str());check(duckscript::run(name),"script accepted");}
static void clean() {check(!duckscript::running() && !com::busy(),"execution finished");check(!mock::blockingDelays,"cooperative no delay calls");check(mock::heldKeys.empty() && !mock::heldModifiers && !hid_backend::hasPersistent(),"keys released");}
static void finish() {mock::drain(200000);clean();if(duckscript::lastError().length())std::cerr<<duckscript::lastError().c_str()<<'\n';check(!duckscript::lastError().length(),"no error");}
static void visible(const std::string &s,const char *expected) {start(s);finish();if(mock::text!=expected)std::cerr<<"actual ["<<mock::text.c_str()<<"] expected ["<<expected<<"]\n";check(mock::text==expected,"exact visible output");}
static void invalid(const std::string &s,const char *message) {start("STRINGLN MUST-NOT-APPEAR\n"+s);mock::drain();clean();if(duckscript::lastError().indexOf(message)<0)std::cerr<<duckscript::lastError().c_str()<<'\n';check(duckscript::lastError().indexOf(message)>=0,"useful preflight diagnostic");check(mock::reports.empty(),"preflight zero HID");check(draws==0,"invalid preflight no entropy");}
static void runtimeError(const char *message) {mock::drain(200000);clean();check(duckscript::lastError().indexOf(message)>=0,"runtime diagnostic");check(duckscript::lastError().indexOf("Error at line")>=0,"source location");}
static void write(const char *name,uint16_t value) {String error;check(internal_vars::write(name,value,error),"validated internal write");}
static uint16_t read(const char *name) {uint16_t v;check(duck_vars::getNumeric(name,v),"numeric registry read");return v;}
static void pending(unsigned line) {for(unsigned i=0;i<10000 && !(duckscript::currentLine()==line && com::busy());++i)mock::tick();check(duckscript::currentLine()==line && com::busy(),"pending line reached");}
static std::vector<mock::Report> typing(const std::string &s,bool jitter) {
  reset();fixed=20;start(std::string(jitter?"$_JITTER_ENABLED=TRUE\n":"")+s);finish();return mock::reports;
}
static void test(const std::string &n) {
 reset();
 if(n == "checked_in_random_jitter_fixture") {
  std::string path=__FILE__;path=path.substr(0,path.find_last_of('/'))+"/fixtures/random-jitter.duck";
  std::ifstream in(path);check(bool(in),"fixture exists");std::ostringstream text;text<<in.rdbuf();fixed=20;
  visible(text.str(),"number=7\n0\n");check(draws==3,"random digit plus digit/Enter jitter, singleton interpolation no entropy");
 } else if(n == "default_registry_values") {
  check(read("$_RANDOM_MIN")==0 && read("$_RANDOM_MAX")==9,"range defaults");
  check(read("$_JITTER_ENABLED")==0 && read("$_JITTER_MAX")==20,"jitter defaults");check(draws==0,"setting reads no entropy");
 } else if(n == "inclusive_minimum_maximum") {
  uint16_t v;script={10,19};check(duck_random::range(20,29,v) && v==20,"minimum inclusive");check(duck_random::range(20,29,v) && v==29,"maximum inclusive");check(draws==2,"one accepted draw each");
 } else if(n == "equal_bounds_no_entropy") {
  for(uint16_t bound:{uint16_t(0),uint16_t(9),uint16_t(65535)}){uint16_t v;check(duck_random::range(bound,bound,v) && v==bound,"equal bound exact");}check(draws==0,"constant range no entropy");
 } else if(n == "full_uint16_range") {
  uint16_t v;script={0,65535,0xffffffffU};check(duck_random::range(0,65535,v) && v==0,"full-range zero");check(duck_random::range(0,65535,v) && v==65535,"full-range max");check(duck_random::range(0,65535,v) && v==65535,"32bit input conversion");
 } else if(n == "reversed_range_atomic_failure") {
  uint16_t v=123;check(!duck_random::range(10,9,v) && v==123,"reverse rejected preserving output");check(draws==0,"reverse no raw draw");
 } else if(n == "unbiased_rejection_then_acceptance") {
  uint16_t v;script={0,5,6};check(duck_random::range(0,9,v) && v==6,"incomplete low bucket rejected");check(draws==3,"precise rejected draws");
 } else if(n == "rejection_budget_exhaustion") {
  fixed=0;uint16_t v=42;check(!duck_random::range(0,9,v) && v==42,"source failure preserves result");check(draws==duck_random::MaxAttempts,"fixed attempts bound");
 } else if(n == "all_range_residues_balanced") {
  uint16_t counts[10]={};for(uint32_t i=10;i<1010;++i){fixed=i;uint16_t v;check(duck_random::range(0,9,v),"accepted complete buckets");++counts[v];}
  for(auto count:counts)check(count==100,"equal preimages in complete buckets; not statistical entropy certification");
 } else if(n == "every_uint16_singleton_boundary") {
  for(uint32_t b=0;b<=65535;++b){uint16_t v;check(duck_random::range(b,b,v) && v==b,"every singleton boundary");}check(draws==0,"no draws for singleton");
 } else if(n == "seeded_host_replay") {
  seeded=true;prng=1234;std::array<uint16_t,100> values;for(auto &v:values)check(duck_random::range(1,1000,v),"first seeded run");prng=1234;
  for(auto v:values){uint16_t again;check(duck_random::range(1,1000,again) && again==v,"host-source reproducibility");}
 } else if(n == "invalid_literal_range_preflight") {invalid("$_RANDOM_MIN=65536\n","exceeds 65535");
 } else if(n == "negative_literal_range_preflight") {invalid("$_RANDOM_MIN=-1\n","Unsupported operator");
 } else if(n == "jitter_boolean_validation") {invalid("$_JITTER_ENABLED=2\n","TRUE/FALSE");
 } else if(n == "atomic_internal_write_validation") {
  write("$_JITTER_ENABLED",1);String e;check(!internal_vars::write("$_JITTER_ENABLED",2,e) && duck_random::jitterEnabled(),"invalid Boolean leaves settings intact");
  write("$_RANDOM_MIN",65535);write("$_RANDOM_MAX",65535);check(read("$_RANDOM_INT")==65535,"max range supported");
 } else if(n == "numeric_bounds_follow_uint16_arithmetic") {
  visible("$_RANDOM_MIN=(0-1)\n$_RANDOM_MAX=65535\nSTRINGLN v=$_RANDOM_INT\n","v=65535\n");check(draws==0,"canonical underflow wraps to singleton max");
  reset();visible("$_JITTER_MAX=(65535+1)\n$_JITTER_ENABLED=TRUE\nSTRINGLN ok\n","ok\n");check(draws==0,"overflow wraps to zero jitter");
 } else if(n == "random_int_readonly") {invalid("$_RANDOM_INT=1\n","read-only");
 } else if(n == "random_reserved_declaration") {invalid("VAR $_RANDOM_MIN=1\n","Reserved internal variable");
 } else if(n == "unsupported_seed_and_encoding") {invalid("VAR $x=$_RANDOM_SEED\n","Unsupported internal variable");
 } else if(n == "unsupported_scancode_variable") {invalid("VAR $x=$_RANDOM_CHAR_KEYCODE\n","Unsupported internal variable");
 } else if(n == "inject_var_still_deferred") {invalid("INJECT_VAR $x\n","Unsupported command");
 } else if(n == "restart_still_deferred") {invalid("RESTART_PAYLOAD\n","Unsupported command");
 } else if(n == "random_character_prose_alias_unconfirmed") {invalid("RANDOM_CHARACTER\n","Unsupported command");
 } else if(n == "random_string_syntax_not_invented") {invalid("RANDOM_STRING 20\n","Unsupported command");
 } else if(n == "random_command_arguments_rejected") {invalid("RANDOM_NUMBER 2\n","take no arguments");
 } else if(n == "random_command_prefix_rejected") {invalid("RANDOM_NUMBER_MORE\n","Unsupported command");
 } else if(n == "random_command_function_collision") {invalid("FUNCTION RANDOM_NUMBER()\nEND_FUNCTION\n","collides with");
 } else if(n == "syntax_evaluator_never_draws") {
  uint16_t v;duck_expr::Error e;check(duck_expr::evaluate("$_RANDOM_INT + 1",strlen("$_RANDOM_INT + 1"),v,e,duck_vars::resolve,nullptr,duck_expr::Mode::Syntax),"syntax validation");check(draws==0,"syntax resolver no entropy");
 } else if(n == "compiled_program_never_draws") {
  duck_expr::Program p;duck_expr::Error e;check(p.compile("$_RANDOM_INT+$_RANDOM_INT",strlen("$_RANDOM_INT+$_RANDOM_INT"),e,duck_vars::resolve),"compile metadata only");check(draws==0,"compile no entropy");
 } else if(n == "preflight_invalid_after_random") {invalid("VAR $x=$_RANDOM_INT\nVAR $y=(3+)\n","operand");
 } else if(n == "random_expression_each_reference_once") {
  script={10,19};visible("VAR $x=$_RANDOM_INT+$_RANDOM_INT\nSTRINGLN x=$x\n","x=9\n");check(draws==2,"two operands two draws");
 } else if(n == "random_boolean_eager_expression") {
  fixed=10;visible("VAR $x=FALSE && $_RANDOM_INT\nSTRINGLN x=$x\n","x=0\n");check(draws==1,"preserve eager logical operands");
 } else if(n == "canonical_random_condition") {
  fixed=19;visible("IF $_RANDOM_INT == 9 THEN\nSTRINGLN yes\nEND_IF\n","yes\n");check(draws==1,"condition read once");
 } else if(n == "legacy_random_condition_once") {
  fixed=19;visible("IF $_RANDOM_INT\nSTRINGLN yes\nEND_IF\n","yes\n");check(draws==1,"legacy type probing no extra reads");
 } else if(n == "legacy_mixed_numeric_text_preserved") {
  visible("VAR $x=2\nIF $x == \"2\"\nSTRINGLN yes\nEND_IF\n",""); // Existing quoted atoms retain their quote bytes.
 } else if(n == "random_while_each_header_once") {
  script={19,10};visible("WHILE $_RANDOM_INT\nSTRINGLN once\nEND_WHILE\n","once\n");check(draws==2,"two header visits two samples");
 } else if(n == "function_suspension_preserves_random_operand") {
  script={11,12,13};visible("FUNCTION VALUE()\nRETURN $_RANDOM_INT\nEND_FUNCTION\nVAR $x=$_RANDOM_INT+VALUE()+$_RANDOM_INT\nSTRINGLN x=$x\n","x=6\n");check(draws==3,"no operand replay across call");
 } else if(n == "function_return_random_bounds") {
  visible("$_RANDOM_MIN=42\n$_RANDOM_MAX=42\nFUNCTION VALUE()\nRETURN $_RANDOM_INT\nEND_FUNCTION\nVAR $x=VALUE()\nSTRINGLN x=$x\n","x=42\n");check(draws==0,"constant function range");
 } else if(n == "excluded_preprocessing_no_rng") {
  visible("IF_DEFINED_TRUE #NONE\nVAR $x=$_RANDOM_INT\nRANDOM_NUMBER\n$_JITTER_ENABLED=TRUE\nEND_IF_DEFINED\nSTRINGLN ok\n","ok\n");check(draws==0,"excluded code inert");
 } else if(n == "inactive_runtime_branch_no_rng") {
  visible("IF FALSE THEN\nVAR $x=$_RANDOM_INT\nRANDOM_NUMBER\nEND_IF\nSTRINGLN ok\n","ok\n");check(draws==0,"inactive code no entropy");
 } else if(n == "reversed_bounds_runtime_safe_stop") {
  start("HOLD CTRL\n$_RANDOM_MIN=10\nVAR $x=$_RANDOM_INT\nSTRINGLN after\n");runtimeError("Random generation failed");check(draws==0,"reversal rejected before raw");
 } else if(n == "reversed_bounds_repaired_before_draw") {
  visible("$_RANDOM_MIN=42\n$_RANDOM_MAX=42\nSTRINGLN value=$_RANDOM_INT\n","value=42\n");
 } else if(n == "raw_failure_releases_ownership") {
  fixed=0;start("HOLD CTRL\nVAR $x=$_RANDOM_INT\nSTRINGLN after\n");runtimeError("source rejection limit");check(draws==32,"runtime fixed budget");
 } else if(n == "runtime_jitter_boolean_invalid") {
  start("HOLD CTRL\nVAR $x=2\n$_JITTER_ENABLED=$x\nSTRINGLN after\n");runtimeError("TRUE/FALSE");
 } else if(n == "settings_reset_between_runs") {
  visible("$_RANDOM_MAX=100\n$_JITTER_ENABLED=TRUE\n$_JITTER_MAX=0\n","");check(duck_random::maximum()==9 && !duck_random::jitterEnabled(),"EOF resets settings");visible("STRINGLN new\n","new\n");check(draws==0,"new run default jitter off");
 } else if(n == "random_command_all_sets_us") {
  const char *names[]={"RANDOM_LOWERCASE_LETTER","RANDOM_UPPERCASE_LETTER","RANDOM_LETTER","RANDOM_NUMBER","RANDOM_SPECIAL","RANDOM_CHAR"};
  for(unsigned k=0;k<6;++k){std::string expected;std::string s;auto set=duck_random::characters(k);for(unsigned i=0;i<strlen(set);++i){script.push_back(72*26*10+i);expected+=set[i];s+=names[k];s+='\n';}
   visible(s,expected.c_str());check(draws>=strlen(set),"characters sampled");reset();}
 } else if(n == "random_special_all_de_locale") {
  std::string s="LOCALE DE\n",expected=duck_random::characters(4);for(unsigned i=0;i<10;++i){script.push_back(100+i);s+="RANDOM_SPECIAL\n";}start(s);finish();
  const uint8_t mods[]={2,0x40,0,2,2,0,0,2,2,2,2};
  const uint8_t keys[]={0x1e,0x14,0x31,0x21,0x22,0x35,0x2c,0x24,0x30,0x25,0x26};
  check(mock::reports.size()==22,"DE ten chars include extra dead-key stroke");
  for(unsigned i=0;i<11;++i){check(mock::reports[2*i].bytes==std::array<uint8_t,8>{mods[i],0,keys[i],0,0,0,0,0},"independent DE exact press bytes");check(mock::reports[2*i+1].bytes==std::array<uint8_t,8>{},"DE release ordering");}
 } else if(n == "random_letters_all_de_report_bytes") {
  std::string s="LOCALE DE\n";for(unsigned i=0;i<52;++i){script.push_back(520+i);s+="RANDOM_LETTER\n";}start(s);finish();
  check(mock::reports.size()==104,"all German letters press/release");
  for(unsigned i=0;i<52;++i){unsigned letter=i%26;uint8_t key=4+(letter==24?25:letter==25?24:letter);
    check(mock::reports[2*i].bytes==std::array<uint8_t,8>{uint8_t(i>=26?2:0),0,key,0,0,0,0,0},"independent QWERTZ letter usage and shift");}
 } else if(n == "random_command_repeat_resamples") {
  script={10,11,12};visible("RANDOM_NUMBER\nREPEAT 2\n","012");check(draws==3,"repeat executes command anew");
 } else if(n == "random_interpolation_compatibility") {
  script={11,12};visible("STRINGLN $_RANDOM_INT\nSTRINGLN_HTML\n$_RANDOM_INT\nEND_STRINGLN\n","1\n2\n");check(draws==2,"one read per interpolation");
 } else if(n == "random_numeric_delay_consumer") {
  fixed=19;start("DELAY $_RANDOM_INT\nSTRINGLN ok\n");finish();check(draws==1 && mock::text=="ok\n","numeric command evaluates once");
 } else if(n == "random_function_argument_setting") {
  visible("FUNCTION VALUE()\nRETURN 7\nEND_FUNCTION\n$_RANDOM_MIN=VALUE()\n$_RANDOM_MAX=VALUE()\nSTRINGLN v=$_RANDOM_INT\n","v=7\n");check(draws==0,"bounded settings via shared suspended expression engine");
 } else if(n == "random_live_settings_persist_until_reset") {
  check(com::executeNow("$_RANDOM_MAX=100"),"live write accepted");mock::drain();check(duck_random::maximum()==100,"live settings persist");
  check(com::executeNow("$_JITTER_ENABLED=TRUE"),"live jitter enable");mock::drain();check(duck_random::jitterEnabled(),"live setting persists");
  duckscript::stop();check(duck_random::maximum()==9 && !duck_random::jitterEnabled(),"STOP resets execution controls");
 } else if(n == "jitter_disabled_exact_existing_timing") {
  auto a=typing("STRINGLN ab\n",false);auto b=typing("$_JITTER_ENABLED=FALSE\nSTRINGLN ab\n",false);
  check(a.size()==b.size(),"same report count");for(size_t i=1;i<a.size();++i)check(a[i].time-a[0].time==b[i].time-b[0].time && a[i].bytes==b[i].bytes,"disabled jitter exact relative timing/report bytes");check(draws==0,"disabled consumes no jitter entropy");
 } else if(n == "jitter_zero_max_no_entropy") {
  visible("$_JITTER_ENABLED=TRUE\n$_JITTER_MAX=0\nSTRINGLN ok\n","ok\n");check(draws==0,"zero max no sample");
 } else if(n == "jitter_additive_per_press_timing") {
  auto a=typing("STRINGLN ab\n",false);auto b=typing("STRINGLN ab\n",true);check(a.size()==b.size(),"same reports");
  unsigned press=0;for(size_t i=0;i<a.size();++i){if(a[i].bytes[2])++press;check(b[i].time-b[0].time==a[i].time-a[0].time+(press-1)*20,"one jitter interval per press, independent dwell");check(a[i].bytes==b[i].bytes,"identical HID bytes");}check(draws==3,"two characters plus Enter");
 } else if(n == "jitter_default_and_explicit_delay_independent") {
  auto a=typing("DEFAULT_DELAY 30\nSTRING a\nDELAY 50\nSTRING b\n",false);auto b=typing("DEFAULT_DELAY 30\nSTRING a\nDELAY 50\nSTRING b\n",true);
  check(b[2].time-b[0].time==a[2].time-a[0].time+20,"default/explicit delay retained; only second jitter added");check(draws==2,"delays no jitter draws");
 } else if(n == "jitter_multiline_enter_and_blank") {
  fixed=20;visible("$_JITTER_ENABLED=TRUE\nSTRINGLN_HTML\na\n\nb\nEND_STRINGLN\n","a\n\nb\n");check(draws==5,"three Enters and two characters");
 } else if(n == "jitter_named_chord_report_bytes") {
  fixed=20;start("$_JITTER_ENABLED=TRUE\nCTRL ALT DELETE\n");finish();check(draws==1,"one chord event");check(mock::reports[0].id==1 && mock::reports[0].bytes==std::array<uint8_t,8>{5,0,0x4c,0,0,0,0,0},"exact chord report");check(mock::reports[1].bytes==std::array<uint8_t,8>{},"release zero");
 } else if(n == "jitter_persistent_modifier_text") {
  fixed=20;start("$_JITTER_ENABLED=TRUE\nHOLD CTRL\nSTRING A\nRELEASE CTRL\n");finish();check(draws==2,"HOLD plus character, RELEASE no jitter");check(mock::reports[1].bytes[0]==3 && mock::reports[2].bytes[0]==1,"shift combines then transient release restores Ctrl");
 } else if(n == "jitter_german_deadkey_strokes") {
  fixed=20;start("LOCALE DE\n$_JITTER_ENABLED=TRUE\nSTRING ^\n");finish();check(draws==2,"two physical strokes each jittered");check(mock::reports[0].bytes[2]==0x35 && mock::reports[2].bytes[2]==0x2c,"DE circumflex then Space");
 } else if(n == "jitter_backpressure_no_redraw") {
  fixed=20;start("$_JITTER_ENABLED=TRUE\nSTRING a\n");mock::usbAccept=false;for(unsigned i=0;i<1000;++i)mock::tick();check(draws==1 && mock::reports.empty(),"wait sampled once then refused transport");mock::usbAccept=true;finish();check(draws==1 && mock::text=="a","retry unchanged event");
 } else if(n == "jitter_random_command_backpressure") {
  script={10,20};start("$_JITTER_ENABLED=TRUE\nRANDOM_NUMBER\n");mock::usbAccept=false;for(unsigned i=0;i<500;++i)mock::tick();check(draws==2,"one char plus one jitter");mock::usbAccept=true;finish();check(mock::text=="0" && draws==2,"no reroll on USB retries");
 } else if(n == "jitter_cancel_pending_interval") {
  fixed=65535;start("HOLD CTRL\n$_JITTER_MAX=65535\n$_JITTER_ENABLED=TRUE\nSTRING a\nSTRING after\n");pending(4);for(unsigned i=0;i<5;++i)mock::tick();check(draws==1,"pending jitter sample");duckscript::stop();mock::drain();clean();check(mock::text.length()==0,"pending press and future output cancelled");
 } else if(n == "jitter_runtime_source_failure") {
  fixed=0;start("HOLD CTRL\n$_JITTER_ENABLED=TRUE\n$_JITTER_MAX=10\nSTRING a\n");runtimeError("jitter source rejection limit");check(draws==32,"failed jitter bounded");
 } else if(n == "jitter_release_refusal_safe_retry") {
  fixed=20;start("$_JITTER_ENABLED=TRUE\nSTRING a\nSTRING after\n");for(unsigned i=0;i<500 && mock::reports.empty();++i)mock::tick();check(mock::reports.size()==1,"press delivered");mock::usbAccept=false;duckscript::stop();for(unsigned i=0;i<30;++i)mock::tick();check(!hid_backend::hasPersistent(),"ownership cleared despite refusal");auto count=draws;mock::usbAccept=true;mock::tick();mock::drain();clean();check(draws==count && mock::reports.back().bytes==std::array<uint8_t,8>{},"release no jitter and retries priority");
 } else if(n == "jitter_disconnect_reconnect") {
  fixed=65535;start("$_JITTER_ENABLED=TRUE\n$_JITTER_MAX=65535\nSTRING a\n");pending(3);mock::usbMounted=false;mock::tick();runtimeError("disconnected");mock::usbMounted=true;mock::tick();mock::drain();check(!mock::reports.empty(),"reconnect release report accepted");check(mock::reports.back().bytes==std::array<uint8_t,8>{},"reconnect zero release only");
 } else if(n == "jitter_clock_wrap_safe") {
  fixed=20;start("$_JITTER_ENABLED=TRUE\nSTRING a\n");mock::now=0xfffffff0U;finish();check(mock::text=="a" && draws==1,"wrap-safe jitter");
 } else if(n == "jitter_hold_release_idempotence") {
  fixed=20;start("$_JITTER_ENABLED=TRUE\nHOLD CTRL\nHOLD CTRL\nRELEASE CTRL\nRELEASE CTRL\n");finish();check(draws==2,"bounded plan samples, including duplicate HOLD");check(mock::reports.size()==2,"idempotent ownership avoids duplicate HID");
 } else if(n == "jitter_maximum_bound") {
  fixed=65535;visible("$_JITTER_ENABLED=TRUE\n$_JITTER_MAX=65535\nSTRING a\n","a");check(draws==1 && mock::now>=65535 && mock::now<66000,"bounded uint16 delay");
 } else if(n == "script_storage_read_fault_no_rng") {
  start("STRINGLN hidden\n"+std::string(400,'a')+"\n");mock::failReadAt=64;mock::drain();clean();check(duckscript::lastError().indexOf("read")>=0 && draws==0 && mock::reports.empty(),"source failure before execution entropy/HID");
 } else if(n == "script_seek_fault_no_rng") {
  start("RANDOM_NUMBER\n");mock::failSeekAt=0;mock::drain();clean();check(duckscript::lastError().indexOf("seek")>=0 && draws==0 && mock::reports.empty(),"rewind failure no entropy");
 } else if(n == "jitter_loop_runtime_seek_failure") {
  const std::string prefix="$_JITTER_ENABLED=TRUE\n$_JITTER_MAX=0\nHOLD CTRL\n";
  start(prefix+"WHILE TRUE\nSTRING a\nEND_WHILE\n");pending(5);mock::failSeekAt=prefix.size();runtimeError("seek");check(draws==0,"zero jitter remains deterministic during storage failure");
 } else if(n == "jitter_live_ownership_isolation") {
  fixed=65535;start("$_JITTER_ENABLED=TRUE\n$_JITTER_MAX=65535\nSTRING a\n");pending(3);check(!com::executeNow("$_JITTER_ENABLED=FALSE"),"live assignment rejected");check(duck_random::jitterEnabled(),"script state intact");duckscript::stop();mock::drain();clean();
 } else if(n == "long_seeded_randomized_loop") {
  seeded=true;prng=42;start("VAR $n=0\nWHILE $n<1000\nVAR $v=$_RANDOM_INT\nRANDOM_NUMBER\n$n=$n+1\nEND_WHILE\n");finish();check(mock::text.length()==1000,"streamed thousand single-character events");check(draws>=2000 && draws<2100,"bounded unbiased sampling overhead");
 } else if(n == "random_numeric_no_hid") {
  start("VAR $x=$_RANDOM_INT\nDELAY 100\n");pending(2);check(read("$x")==8 && draws==1,"inspect numeric result while run alive");finish();check(mock::reports.empty(),"numeric-only no HID");
 } else if(n == "random_source_null_default_adapter") {
  duck_random::source(nullptr);uint16_t v;check(duck_random::range(0,9,v) && v==8,"host adapter reset only, no fake device seed");
 } else throw std::runtime_error("unknown test");
}
int main(int argc,char **argv) {if(argc!=2)return 2;try{test(argv[1]);std::cout<<"PASS "<<argv[1]<<" ("<<assertions<<" assertions)\n";return 0;}catch(const std::exception &e){std::cerr<<"FAIL "<<argv[1]<<": "<<e.what()<<'\n';return 1;}}
