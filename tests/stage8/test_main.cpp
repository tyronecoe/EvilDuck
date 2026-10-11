#include "host.h"
#include "FS.h"
#include "com.h"
#include "duckscript.h"
#include "hid_backend.h"
#include "duck_keys.h"
#include "keyboard_locale.h"
#include "locale/locales.h"
#include "script_log.h"
#include <iostream>
#include <stdexcept>
#include <string>
#include <cstring>

static unsigned assertions=0;
static void check(bool ok,const char *message) {++assertions;if(!ok)throw std::runtime_error(message);}
using Bytes=std::array<uint8_t,8>;
static Bytes payload(uint8_t mod,std::initializer_list<uint8_t> keys) {
  Bytes b={mod,0,0,0,0,0,0,0};unsigned i=2;for(auto k:keys)b[i++]=k;return b;
}
static void exact(size_t index,Bytes expected) {
  check(index<mock::reports.size(),"expected accepted report exists");
  const auto &r=mock::reports[index];check(r.instance==0 && r.id==1,"correct endpoint instance and report ID");
  if(r.bytes!=expected){std::cerr<<"report "<<index<<" actual:";for(auto b:r.bytes)std::cerr<<' '<<unsigned(b);std::cerr<<'\n';}
  check(r.bytes==expected,"exact eight report bytes including reserved/padding");
}
static void clean() {
  check(!duckscript::running() && !com::busy(),"execution complete");
  check(!mock::blockingDelays,"nonblocking HID");check(mock::heldKeys.empty() && !mock::heldModifiers,"keys and modifiers released");
}
static void start(const std::string &s,const char *source="stage8.txt") {
  mock::reset();mock::file(source,s.c_str());check(duckscript::run(source),"start harmless mocked script");
}
static void run(const std::string &s,const char *source="stage8.txt") {
  start(s,source);mock::drain(100000);
  if(duckscript::lastError().length())std::cerr<<duckscript::lastError().c_str()<<'\n';
  check(!duckscript::lastError().length(),"valid script no runtime error");clean();
}
static void rejected(const std::string &s,const char *error) {
  start("STRINGLN MUST-NOT-APPEAR\n"+s);mock::drain();
  check(duckscript::lastError().indexOf(error)>=0,"clear preflight diagnostic");
  check(mock::reports.empty(),"malformed script zero HID");clean();
}
struct Expected {uint8_t mod,key,second=0;};
// Independent numeric reference: USB HUT page 0x07 + US and German PC/ISO
// physical rows (xkeyboard-config de(basic), NOT the firmware's table constants).
static Expected reference(unsigned c,bool de) {
  if(c==8)return{0,0x2a};
  if(c==9)return{0,0x2b};
  if(c==10||c==13)return{0,0x28};
  if(c==27)return{0,0x29};
  if(c==127)return{0,0x4c};
  if(c<32)return{0,0};
  if(c==' ')return{0,0x2c};
  if(c>='0'&&c<='9')return{0,uint8_t(c=='0'?0x27:0x1e + c-'1')};
  if((c>='a'&&c<='z')||(c>='A'&&c<='Z')) {
    bool upper=c<='Z';unsigned lower=upper?c+32:c;
    if(de && (lower=='y'||lower=='z'))lower=lower=='y'?'z':'y';
    return{uint8_t(upper?2:0),uint8_t(4+lower-'a')};
  }
  struct P {char c;uint8_t mod,key,second;};
  static const P us[]={
    {'!',2,0x1e,0},{'"',2,0x34,0},{'#',2,0x20,0},{'$',2,0x21,0},{'%',2,0x22,0},{'&',2,0x24,0},
    {'\'',0,0x34,0},{'(',2,0x26,0},{')',2,0x27,0},{'*',2,0x25,0},{'+',2,0x2e,0},{',',0,0x36,0},
    {'-',0,0x2d,0},{'.',0,0x37,0},{'/',0,0x38,0},{':',2,0x33,0},{';',0,0x33,0},{'<',2,0x36,0},
    {'=',0,0x2e,0},{'>',2,0x37,0},{'?',2,0x38,0},{'@',2,0x1f,0},{'[',0,0x2f,0},{'\\',0,0x31,0},
    {']',0,0x30,0},{'^',2,0x23,0},{'_',2,0x2d,0},{'`',0,0x35,0},{'{',2,0x2f,0},{'|',2,0x31,0},
    {'}',2,0x30,0},{'~',2,0x35,0}};
  static const P german[]={
    {'!',2,0x1e,0},{'"',2,0x1f,0},{'#',0,0x31,0},{'$',2,0x21,0},{'%',2,0x22,0},{'&',2,0x24,0},
    {'\'',2,0x31,0},{'(',2,0x25,0},{')',2,0x26,0},{'*',2,0x30,0},{'+',0,0x30,0},{',',0,0x36,0},
    {'-',0,0x38,0},{'.',0,0x37,0},{'/',2,0x24,0},{':',2,0x37,0},{';',2,0x36,0},{'<',0,0x64,0},
    {'=',2,0x27,0},{'>',2,0x64,0},{'?',2,0x2d,0},{'@',0x40,0x14,0},{'[',0x40,0x25,0},{'\\',0x40,0x2d,0},
    {']',0x40,0x26,0},{'^',0,0x35,0x2c},{'_',2,0x38,0},{'`',2,0x2e,0x2c},{'{',0x40,0x24,0},
    {'|',0x40,0x64,0},{'}',0x40,0x27,0},{'~',0x40,0x30,0}};
  if(de){for(auto p:german)if(unsigned(p.c)==c)return{p.mod,p.key,p.second};}
  else{for(auto p:us)if(unsigned(p.c)==c)return{p.mod,p.key,p.second};}
  throw std::runtime_error("incomplete independent ASCII reference");
}
static void translated(const std::string &s,Expected e) {
  keyboard_locale::Stroke strokes[2]={};uint8_t count=0;
  check(keyboard_locale::translate(s.data(),s.size(),strokes,count)==s.size(),"one entire reference character consumed");
  check(count==(e.key ? (e.second ? 2 : 1):0),"exact stroke count");
  if(e.key){check(strokes[0].modifiers==e.mod && strokes[0].key==e.key,"reference modifier and usage");}
  if(e.second)check(!strokes[1].modifiers && strokes[1].key==e.second,"dead key spacing stroke");
}
static void ascii(bool de,bool raw) {
  keyboard_locale::setLocaleByName(de?"DE":"US");auto l=keyboard_locale::getLocale();
  check(l->ascii_len==128,"exact ASCII table size");
  for(unsigned i=0;i<128;++i){auto e=reference(i,de);
    if(raw){check(l->ascii[i*2]==e.mod && l->ascii[i*2+1]==e.key,"exact indexed ASCII pair");}
    else translated(std::string(1,char(i)),e);
  }
}
static void pressReleasePairs() {
  check(mock::reports.size()%2==0,"every accepted press has a release");
  for(size_t i=0;i<mock::reports.size();i+=2){exact(i+1,{});check(mock::reports[i+1].time-mock::reports[i].time>=5,"minimum dwell time");}
}
static void pendingHeld(const std::string &s) {start(s);for(unsigned i=0;i<20000&&mock::heldKeys.empty();++i)mock::tick();
    check(!mock::heldKeys.empty(),"reach held runtime key");}
static void test(const String &name) {
  if(name=="stage8_f1_f24_reference") {
    for(unsigned i=1;i<=24;++i){uint8_t k=0;check(hid_backend::keyNameToHid("F"+String(i),k),"F key recognized");check(k==(i<=12?0x39+i:0x5b+i),"HUT function key usage");
      run("F"+std::to_string(i)+"\n");exact(0,payload(0,{k}));exact(1,{});}
    run("F12\nF13\nF24\nPRINTSCREEN\n");exact(0,payload(0,{0x45}));exact(2,payload(0,{0x68}));exact(4,payload(0,{0x73}));exact(6,payload(0,{0x46}));pressReleasePairs();
  } else if(name=="stage8_invalid_f_names") {
    for(const char *s:{"F0","F25","F-1","F+1","F1x","F123"}){uint8_t k=0;check(!hid_backend::keyNameToHid(s,k),"invalid F mapping rejected");}
    rejected("F25\n","Unsupported command");
  } else if(name=="stage8_navigation_editing_aliases") {
    struct N{const char *s;uint8_t k;};const N entries[]={
      {"ENTER",0x28},{"RETURN",0x28},{"ESC",0x29},{"ESCAPE",0x29},{"BACKSPACE",0x2a},{"TAB",0x2b},{"SPACE",0x2c},
      {"CAPSLOCK",0x39},{"PRINTSCREEN",0x46},{"SCROLLLOCK",0x47},{"PAUSE",0x48},{"BREAK",0x48},{"INSERT",0x49},
      {"HOME",0x4a},{"PAGEUP",0x4b},{"DELETE",0x4c},{"DEL",0x4c},{"END",0x4d},{"PAGEDOWN",0x4e},
      {"RIGHT",0x4f},{"RIGHTARROW",0x4f},{"LEFT",0x50},{"LEFTARROW",0x50},{"DOWN",0x51},{"DOWNARROW",0x51},
      {"UP",0x52},{"UPARROW",0x52},{"MENU",0x65},{"APP",0x65}};
    for(auto e:entries){run(std::string(e.s)+"\n");exact(0,payload(0,{e.k}));exact(1,{});}
    run("END A\nCTRL END\n");exact(0,payload(0,{0x4d,4}));exact(2,payload(1,{0x4d}));
  } else if(name=="stage8_named_punctuation_keys") {
    struct N{const char *s;uint8_t k;};const N entries[]={{"MINUS",0x2d},{"EQUAL",0x2e},{"LBRACE",0x2f},{"LEFTBRACE",0x2f},
      {"RBRACE",0x30},{"RIGHTBRACE",0x30},{"BACKSLASH",0x31},{"SEMICOLON",0x33},{"APOSTROPHE",0x34},{"QUOTE",0x34},
      {"GRAVE",0x35},{"BACKTICK",0x35},{"COMMA",0x36},{"DOT",0x37},{"PERIOD",0x37},{"SLASH",0x38}};
    for(auto e:entries){run(std::string(e.s)+"\n");exact(0,payload(0,{e.k}));exact(1,{});}
  } else if(name=="stage8_keypad_reference") {
    struct N{const char *s;uint8_t k;};const N entries[]={{"NUMLOCK",0x53},{"NUM_SLASH",0x54},{"NUM_ASTERIX",0x55},
      {"NUM_ASTERISK",0x55},{"NUM_MINUS",0x56},{"NUM_PLUS",0x57},{"NUM_ENTER",0x58},{"NUM_DOT",0x63}};
    for(auto e:entries){run(std::string(e.s)+"\n");exact(0,payload(0,{e.k}));}
    for(unsigned i=0;i<10;++i){run("NUM_"+std::to_string(i)+"\n");exact(0,payload(0,{uint8_t(i?0x58+i:0x62)}));}
  } else if(name=="stage8_all_modifier_masks") {
    static const char *mods[]={"CTRL","SHIFT","ALT","GUI","RIGHTCTRL","RIGHTSHIFT","RIGHTALT","RIGHTGUI"};
    for(unsigned mask=0;mask<256;++mask){std::string line;for(unsigned i=0;i<8;++i)if(mask&(1<<i))line+=std::string(mods[i])+" ";run(line+"a\n");check(mock::reports.size()==2,"exact chord pair");exact(0,payload(mask,{4}));exact(1,{});}
  } else if(name=="stage8_modifier_aliases") {
    struct N{const char *s;uint8_t m;};const N entries[]={{"CONTROL",1},{"WINDOWS",8},{"WIN",8},{"CMD",8},{"COMMAND",8},
      {"OPTION",4},{"RCTRL",16},{"RSHIFT",32},{"RALT",64},{"RIGHTWINDOWS",128}};
    for(auto e:entries){run(std::string(e.s)+" A\n");exact(0,payload(e.m,{4}));exact(1,{});}
  } else if(name=="stage8_hyphen_combinations") {
    run("CTRL-ALT DELETE\nCOMMAND-OPTION-SHIFT a\nRIGHTCTRL-RIGHTSHIFT-RIGHTALT-RIGHTGUI F13\n-\n");
    exact(0,payload(5,{0x4c}));exact(2,payload(14,{4}));exact(4,payload(0xf0,{0x68}));exact(6,payload(0,{0x2d}));pressReleasePairs();
  } else if(name=="stage8_malformed_hyphens_zero_hid") {
    for(const char *s:{"CTRL--ALT A\n","CTRL- A\n","-CTRL A\n","CTRL-unknown A\n"})rejected(s,s[0]=='-'||strstr(s,"--")||strstr(s,"CTRL- ") ? "Empty key":"Unsupported command");
  } else if(name=="stage8_case_tabs_and_order") {
    run("a\tShIfT\tCoNtRoL\nCTRL CTRL SHIFT A A\n");exact(0,payload(3,{4}));exact(2,payload(3,{4}));check(mock::reports.size()==4,"duplicate modifiers/keys not duplicated");
  } else if(name=="stage8_modifier_only_release") {
    run("CTRL SHIFT ALT GUI RIGHTCTRL RIGHTSHIFT RIGHTALT RIGHTGUI\nSTRING a\n");exact(0,payload(255,{}));exact(1,{});exact(2,payload(0,{4}));pressReleasePairs();
  } else if(name=="stage8_six_key_limit_and_duplicates") {
    run("CTRL A A A A A A B C D E F\n");exact(0,payload(1,{4,5,6,7,8,9}));check(mock::reports.size()==2,"duplicate keys do not consume report slots");
    rejected("A B C D E F G\n","six distinct");
  } else if(name=="stage8_literal_punctuation_chord_us") {
    run("CTRL !\nCOMMAND ?\nSHIFT -\n");exact(0,payload(3,{0x1e}));exact(2,payload(10,{0x38}));exact(4,payload(2,{0x2d}));check(mock::reports.size()==6,"no stray modifier-only report");
  } else if(name=="stage8_literal_punctuation_chord_de") {
    run("LOCALE DE\nCTRL @\nCOMMAND ^\n");exact(0,payload(0x41,{0x14}));exact(2,payload(8,{0x35}));exact(4,payload(8,{0x2c}));pressReleasePairs();
  } else if(name=="stage8_all_literal_punctuation_chords") {
    for(bool de:{false,true}) for(unsigned c=33;c<=126;++c) {
      if((c>='0'&&c<='9')||(c>='A'&&c<='Z')||(c>='a'&&c<='z'))continue;
      auto e=reference(c,de);
      run(std::string("LOCALE ")+(de?"DE":"US")+"\nCTRL "+char(c)+"\n");
      exact(0,payload(e.mod|1,{e.key}));exact(1,{});
      if(e.second){exact(2,payload(1,{e.second}));exact(3,{});}
      check(mock::reports.size()==(e.second?4:2),"one locale sequence retains chord modifier");
    }
    run("CTRL-(\nCTRL )\n(\n)\n");
    exact(0,payload(3,{0x26}));exact(2,payload(3,{0x27}));exact(4,payload(2,{0x26}));exact(6,payload(2,{0x27}));
  } else if(name=="stage8_report_filter_and_raw_modifiers") {
    run("KEYCODE 1 0xE1 0x04 0x04 0x00 0xFF 0x05\n");exact(0,payload(3,{4,5}));exact(1,{});
    for(unsigned i=0;i<8;++i){run("KEYCODE 0 "+std::to_string(0xe0+i)+"\n");exact(0,payload(1<<i,{}));exact(1,{});}
  } else if(name=="stage8_keycode_bounds_zero_hid") {
    rejected("KEYCODE 256 4\n","KEYCODE expects");rejected("KEYCODE 0 4 5 6 7 8 9 10\n","KEYCODE expects");
  } else if(name=="stage8_us_ascii_table")ascii(false,true);
  else if(name=="stage8_de_ascii_table")ascii(true,true);
  else if(name=="stage8_us_ascii_translation")ascii(false,false);
  else if(name=="stage8_de_ascii_translation")ascii(true,false);
  else if(name=="stage8_printable_ascii_runtime_all_locales") {
    std::string input;for(unsigned c=32;c<=126;++c)input+=char(c);
    for(bool de:{false,true}){run(std::string("LOCALE ")+(de?"DE":"US")+"\nSTRING "+input+"\n");size_t at=0;
      for(unsigned c=32;c<=126;++c){auto e=reference(c,de);exact(at++,payload(e.mod,{e.key}));exact(at++,{});if(e.second){exact(at++,payload(0,{e.second}));exact(at++,{});}}
      check(at==mock::reports.size(),"entire printable alphabet exact report sequence");pressReleasePairs();}
  } else if(name=="stage8_de_utf8_reference") {
    struct U{const char *s;uint8_t mod,key;};const U entries[]={{"§",2,0x20},{"°",2,0x35},{"²",64,0x1f},{"³",64,0x20},
      {"Ä",2,0x34},{"Ö",2,0x33},{"Ü",2,0x2f},{"ß",0,0x2d},{"ä",0,0x34},{"ö",0,0x33},{"ü",0,0x2f},{"€",64,8}};
    keyboard_locale::setLocaleByName("DE");for(auto e:entries)translated(e.s,{e.mod,e.key});
    run("LOCALE DE\nSTRING ÄÖÜßäöü€\n");uint8_t keys[]={0x34,0x33,0x2f,0x2d,0x34,0x33,0x2f,8};
    for(unsigned i=0;i<8;++i){exact(i*2,payload(i<3?2:i==7?64:0,{keys[i]}));exact(i*2+1,{});}
  } else if(name=="stage8_de_dead_keys") {
    keyboard_locale::setLocaleByName("DE");translated("^",{0,0x35,0x2c});translated("`",{2,0x2e,0x2c});translated("´",{0,0x2e,0x2c});translated("~",{64,0x30});
    run("LOCALE DE\nSTRING ^`´~\n");exact(0,payload(0,{0x35}));exact(2,payload(0,{0x2c}));exact(4,payload(2,{0x2e}));exact(6,payload(0,{0x2c}));exact(8,payload(0,{0x2e}));exact(10,payload(0,{0x2c}));exact(12,payload(64,{0x30}));pressReleasePairs();
  } else if(name=="stage8_locale_registration_and_switching") {
    mock::reset();check(keyboard_locale::supportsLocale("uS") && keyboard_locale::supportsLocale("dE"),"only registered locales supported");
    for(const char *s:{"GB","ES","FR","RU","DE_MAC",""})check(!keyboard_locale::supportsLocale(s),"undeclared layout not claimed");
    check(!keyboard_locale::setLocaleByName("FR") && keyboard_locale::getLocale()==&locale_us,"failed selection preserves locale");
    run("STRING y\nLOCALE DE\nSTRING y\nLOCALE US\nSTRING y\n");exact(0,payload(0,{28}));exact(2,payload(0,{29}));exact(4,payload(0,{28}));
    rejected("LOCALE FR\n","unsupported LOCALE");
  } else if(name=="stage8_named_keys_are_physical_not_locale_text") {
    run("LOCALE DE\ny\nSTRING y\nZ\nSTRING Z\n");exact(0,payload(0,{28}));exact(2,payload(0,{29}));exact(4,payload(0,{29}));exact(6,payload(2,{28}));
  } else if(name=="stage8_unsupported_unicode_skip_warning") {
    run("STRING a🙂é中b\nSTRINGLN c\n");check(mock::text=="abc\n","unsupported scalars skipped without corruption");
    String logs=script_log::getText();check(logs.indexOf("[WARN] stage8.txt:1 Unsupported text character")>=0,"warning source and line");
    auto first=logs.indexOf("Unsupported text");check(logs.indexOf("Unsupported text",first+1)<0,"one warning per text operation");
    run("LOCALE DE\nSTRING ä🙂ö\n");check(mock::reports.size()==4,"supported German neighbors survive unsupported Unicode");
  } else if(name=="stage8_utf8_bounds_and_invalid_sequences") {
    keyboard_locale::Stroke strokes[2]={};uint8_t count=0;
    for(const std::string &s:{std::string("🙂"),std::string("é"),std::string("中")}){
      check(keyboard_locale::translate(s.data(),s.size(),strokes,count)==s.size() && !count,"unsupported scalar consumed once");
      for(size_t n=1;n<s.size();++n)check(keyboard_locale::translate(s.data(),n,strokes,count)==1 && !count,"truncated input stays bounded");}
    const std::string invalid[]={"\xc0\xaf","\xe0\x80\x80","\xed\xa0\x80","\xf4\x90\x80\x80","\xf5\x80\x80\x80","\x80"};
    for(auto &s:invalid)check(keyboard_locale::translate(s.data(),s.size(),strokes,count)==1 && !count,"invalid scalar skips byte safely");
    check(!keyboard_locale::translate("",0,strokes,count) && !count,"empty span no read");
  } else if(name=="stage8_no_warn_supported_controls") {
    run("STRINGLN abc\n");check(script_log::getText().indexOf("[WARN]")<0,"supported ASCII silent");
  } else if(name=="stage8_repeat_define_and_stringln_reports") {
    run("DEFINE #KEY F13\nDEFINE #TEXT A!\n#KEY\nREPEAT 1\nSTRINGLN #TEXT\nREPLAY 1\n");
    exact(0,payload(0,{0x68}));exact(2,payload(0,{0x68}));
    for(unsigned base:{4u,10u}){exact(base,payload(2,{4}));exact(base+2,payload(2,{0x1e}));exact(base+4,payload(0,{0x28}));}
    check(mock::reports.size()==16,"exact replayed reports");pressReleasePairs();
  } else if(name=="stage8_multiline_control_function_keyboard") {
    const char *s="LOCALE DE\nFUNCTION type()\nSTRINGLN\n\tÄ&\nEND_STRINGLN\nRETURN TRUE\nEND_FUNCTION\nVAR $n=1\nWHILE $n>0\nIF type() THEN\nF13\nELSE\nF14\nEND_IF\n$n=0\nEND_WHILE\n";
    for(const char *source:{"stage8.txt","sd:stage8.txt"}){run(s,source);exact(0,payload(2,{0x34}));exact(2,payload(2,{0x24}));exact(4,payload(0,{0x28}));exact(6,payload(0,{0x68}));check(mock::reports.size()==8,"no inactive branch HID");}
  } else if(name=="stage8_queue_refusal_press_and_release") {
    start("CTRL A\nSTRING b\n");mock::usbAccept=false;for(unsigned i=0;i<200;++i)mock::tick();
    check(mock::reports.empty() && duckscript::running(),"queue refusal yields");
    mock::usbAccept=true;while(mock::heldKeys.empty())mock::tick();exact(0,payload(1,{4}));mock::usbAccept=false;
    for(unsigned i=0;i<200;++i)mock::tick();
    check(mock::reports.size()==1 && mock::heldModifiers==1,"refused release keeps phase and ownership");
    mock::usbAccept=true;mock::drain();exact(1,{});exact(2,payload(0,{5}));check(mock::reports.size()==4,"accepted reports never duplicated");clean();
  } else if(name=="stage8_disconnect_mid_chord_recovery") {
    pendingHeld("CTRL SHIFT A\nSTRING b\n");mock::usbReady=false;for(unsigned i=0;i<500;++i)mock::tick();
    check(mock::reports.size()==1,"disconnected endpoint no additional reports");
    mock::usbReady=true;mock::drain();exact(0,payload(3,{4}));exact(1,{});exact(2,payload(0,{5}));clean();
  } else if(name=="stage8_cancel_held_modifier_all_masks") {
    for(unsigned mask=1;mask<256;++mask){pendingHeld("KEYCODE "+std::to_string(mask)+" 4\nSTRING tail\n");duckscript::stop();for(unsigned i=0;i<50;++i)mock::tick();exact(0,payload(mask,{4}));exact(1,{});check(mock::reports.size()==2,"cancel drops queued tail");clean();}
  } else if(name=="stage8_cancel_release_priority_new_live_command") {
    pendingHeld("COMMAND a\nSTRING tail\n");mock::usbAccept=false;duckscript::stop();check(com::executeNow("STRING b"),"new live command accepted cooperatively");
    for(unsigned i=0;i<100;++i)mock::tick();
    check(mock::reports.size()==1,"new press cannot bypass pending release");
    mock::usbAccept=true;mock::drain();exact(1,{});exact(2,payload(0,{5}));check(mock::reports.size()==4,"one canceled release before next press");clean();
  } else if(name=="stage8_stop_and_runtime_error_release") {
    run("CTRL SHIFT a\nSTOP\nSTRING hidden\n");check(mock::reports.size()==2,"STOP prevents queued HID");
    start("VAR $z=0\nCTRL SHIFT a\nVAR $v=1/$z\nSTRING hidden\n");mock::drain();check(duckscript::lastError().indexOf("zero")>=0,"runtime fault diagnosed");check(mock::reports.size()==2,"fault prevents tail and retains release");exact(1,{});clean();
  } else if(name=="stage8_cancel_between_dead_key_strokes") {
    pendingHeld("LOCALE DE\nSTRING ^tail\n");duckscript::stop();for(unsigned i=0;i<100;++i)mock::tick();exact(0,payload(0,{0x35}));exact(1,{});check(mock::reports.size()==2,"cancel drops pending space/tail strokes");clean();
  } else if(name=="stage8_storage_fault_after_chord_release") {
    std::string s="CTRL SHIFT a\n"+std::string(100,'\n')+"STRING tail\n";pendingHeld(s);mock::failReadAt=0;mock::drain();check(duckscript::lastError().indexOf("Storage read")>=0,"source read failure stops");check(mock::reports.size()==2,"fault no tail HID");exact(1,{});clean();
  } else if(name=="stage8_hid_disabled_and_live_ownership") {
    run("ATTACKMODE OFF\nKEYCODE 255 4\nCTRL A\nSTRINGLN hidden\nATTACKMODE HID\nSTRING a\n");check(mock::reports.size()==2,"disabled HID suppressed");exact(0,payload(0,{4}));
    pendingHeld("CTRL SHIFT A\n");check(!com::executeNow("RIGHTALT b"),"live commands cannot steal ownership");duckscript::stop();clean();
  } else if(name=="stage8_new_run_no_modifier_leak") {
    pendingHeld("RIGHTALT a\nSTRING tail\n");duckscript::stop();run("STRING b\n");exact(0,payload(0,{5}));check(mock::reports.size()==2,"fresh run clean report");
  } else throw std::runtime_error("unknown Stage 8 test");
}
int main(int argc,char **argv){if(argc!=2)return 2;try{mock::reset();test(argv[1]);std::cout<<"PASS "<<argv[1]<<" ("<<assertions<<" assertions)\n";return 0;}catch(const std::exception &e){std::cerr<<"FAIL "<<argv[1]<<": "<<e.what()<<'\n';return 1;}}
