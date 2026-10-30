#include "timeout_parent_cases.inc"
// H1 scalar values below are chosen experiment policy, NOT official runtime values.
// Expected usages/modifier bits are independently specified by USB HID Usage Tables
// keyboard page07 and the recorded US mapping vectors; no production codec is used.
struct H1Vector { unsigned char ascii;uint8_t usage,mods; };
static H1Vector h1Expected(unsigned char c){
 if(c>='a'&&c<='z')return {c,uint8_t(4+c-'a'),0};
 if(c>='A'&&c<='Z')return {c,uint8_t(4+c-'A'),2};
 if(c>='1'&&c<='9')return {c,uint8_t(30+c-'1'),0};if(c=='0')return {c,39,0};
 static const char* plain=" -=[]\\;'`,./";static const uint8_t usages[]={44,45,46,47,48,49,51,52,53,54,55,56};
 for(unsigned i=0;i<12;++i)if(c==uint8_t(plain[i]))return {c,usages[i],0};
 static const char* shifted="_+{}|:\"~<>?";static const uint8_t shiftedUsages[]={45,46,47,48,49,51,52,53,54,55,56};
 for(unsigned i=0;i<11;++i)if(c==uint8_t(shifted[i]))return {c,shiftedUsages[i],2};
 static const char* symbols="!@#$%^&*()";for(unsigned i=0;i<10;++i)if(c==uint8_t(symbols[i]))return {c,uint8_t(i==9?39:30+i),2};
 check(false,"test vector printable covered independently");return {0,0,0};
}
static uint16_t h1Scalar(H1Vector v){return uint16_t((uint16_t(v.mods)<<8)|v.usage);}
static std::string h1Source(uint16_t v){return "VAR $key="+std::to_string(v)+"\nINJECT_VAR $key\n";}
static void h1Group(const char* property,const char* alphabet){
 for(unsigned i=0;i<strlen(alphabet);++i){lower::reset();rng_mock::reset();rng_mock::fallback=i;std::string src="VAR $key="+std::string(property)+"\nVAR $copy=$key\nINJECT_VAR $copy\nINJECT_VAR $copy\n";completed(src.c_str());auto v=h1Expected(alphabet[i]);check(operations().size()==4&&rng_mock::calls==1,"one stored sample drives two complete taps");exactReport(0,v.mods,{v.usage});exactReport(1,0,{});exactReport(2,v.mods,{v.usage});exactReport(3,0,{});}
}
int main(int argc,char**argv){if(argc!=2)return 2;if(strncmp(argv[1],"AC",2))return lock_timeout_main(argc,argv);try{mscMock::reset();mock::reset();setup();check(startupControlledReady&&route_u::bindOwner(),"actual composed experimental startup");lower::reset();led_mock::nowUs=0;rng_mock::reset();auto r=req();std::string id=argv[1];
if(id=="AC01"){
 for(unsigned c=32;c<=126;++c){lower::reset();auto v=h1Expected(c);completed(h1Source(h1Scalar(v)).c_str());check(operations().size()==2,"each of95printables onepressrelease");exactReport(0,v.mods,{v.usage});exactReport(1,0,{});}
}else if(id=="AC02"){
 for(auto pair:{std::pair<unsigned,unsigned>(4,0),{516,2},{39,0},{544,2}}){lower::reset();completed(h1Source(pair.first).c_str());exactReport(0,pair.second,{uint8_t(pair.first&255)});exactReport(1,0,{});}
}else if(id=="AC03")h1Group("$_RANDOM_LOWER_LETTER_KEYCODE","abcdefghijklmnopqrstuvwxyz");
else if(id=="AC04")h1Group("$_RANDOM_UPPER_LETTER_KEYCODE","ABCDEFGHIJKLMNOPQRSTUVWXYZ");
else if(id=="AC05")h1Group("$_RANDOM_LETTER_KEYCODE","abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ");
else if(id=="AC06")h1Group("$_RANDOM_NUMBER_KEYCODE","0123456789");
else if(id=="AC07")h1Group("$_RANDOM_SPECIAL_KEYCODE","!@#$%^&*()");
else if(id=="AC08")h1Group("$_RANDOM_CHAR_KEYCODE","abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()");
else if(id=="AC09"){
 NumericHarness h;h.raw={0};ds_preview::Program p;ds_preview::Runtime rt;execute("VAR $key=$_RANDOM_UPPER_LETTER_KEYCODE\nVAR $copy=$key\nVAR $before=$key\nINJECT_VAR $copy\nVAR $middle=$copy\nINJECT_VAR $copy\nVAR $after=$key\n",p,rt,h);check(rt.state()==ds_preview::State::Completed&&h.draws==1&&variable(rt,"$key")==516&&variable(rt,"$copy")==516&&variable(rt,"$before")==516&&variable(rt,"$middle")==516&&variable(rt,"$after")==516,"assignment/copy/repeated injection never mutate scalars");check(h.events.size()==2&&h.events[0].type==ds_preview::EventType::KeyTap&&h.events[0].value==4&&h.events[0].modifiers==2,"stored scalar decoded only into existing KeyTap");
}else if(id=="AC10"){
 completed("VAR $key=4\nVAR $copy=$key\n$key=5\nINJECT_VAR $copy\nINJECT_VAR $key\n");exactReport(0,0,{4});exactReport(2,0,{5});
}else if(id=="AC11"){
 for(unsigned v:{0u,65535u,1u,3u,40u,224u,512u,1028u,772u,256u,1234u}){lower::reset();runSource(h1Source(v).c_str());check(route_u::status().reason==route_u::Reason::Runtime&&route_u::status().errorCode==unsigned(ds_preview::ErrorCode::InvalidExperimentalKeycode)&&operations().empty(),"invalid H1 encoding rejected before any keypress");check(!route_u::owned()&&!hid_backend::hasPersistent(),"invalid encoding cleanup completes");}
}else if(id=="AC12"){
 for(const char*s:{"INJECT_VAR\n","INJECT_VAR 4\n","INJECT_VAR $missing\n","VAR $k=4\nINJECT_VAR $k+1\n","VAR $k=4\nINJECT_VAR $k extra\n","INJECT_VAR $_RANDOM_LOWER_LETTER_KEYCODE\n","IF FALSE THEN\nINJECT_VAR $missing\nEND_IF\n","FUNCTION unused()\nINJECT_VAR 4\nEND_FUNCTION\n","VAR $k=4\nREPEAT 2 INJECT_VAR $k\n"}){lower::reset();rejected(s);}check(rng_mock::calls==0,"retained invalid grammar has no entropy or HID effect");
 NumericHarness h;ds_preview::Program p;ds_preview::Runtime rt;execute("IF FALSE THEN\nVAR $k=4\nEND_IF\nINJECT_VAR $k\n",p,rt,h);check(rt.state()==ds_preview::State::Error&&rt.error().code==ds_preview::ErrorCode::Uninitialized&&rt.error().line==4&&h.events.empty()&&h.draws==0,"new injection opcode rejects uninitialized retained variable before sink");
}else if(id=="AC13"){
 const char* props[]={"$_RANDOM_LOWER_LETTER_KEYCODE","$_RANDOM_UPPER_LETTER_KEYCODE","$_RANDOM_LETTER_KEYCODE","$_RANDOM_NUMBER_KEYCODE","$_RANDOM_SPECIAL_KEYCODE","$_RANDOM_CHAR_KEYCODE"};for(const char*prop:props){lower::reset();rejected((std::string(prop)+"=4\n").c_str());lower::reset();rejected((std::string("VAR ")+prop+"=4\n").c_str());}check(rng_mock::calls==0,"readonly properties reject write and shadow without drawing");
}else if(id=="AC14"){
 completed("IF_DEFINED_TRUE #ABSENT\nINJECT_VAR invalid extra\nEND_IF_DEFINED\nVAR $k=4\nINJECT_VAR $k\n");oneA();
}else if(id=="AC15"){
 NumericHarness h;h.raw={0,1};h.refuse=5;ds_preview::Program p;ds_preview::Runtime rt;execute("VAR $k=$_RANDOM_LOWER_LETTER_KEYCODE\nINJECT_VAR $k\n",p,rt,h);check(rt.state()==ds_preview::State::Completed&&h.draws==1&&h.events.size()==1&&h.attempts==6&&variable(rt,"$k")==4,"accepted output and cached selection survive backpressure without re-evaluation");
}else if(id=="AC16"){
 NumericHarness h;h.raw={0,1};ds_preview::Program p;ds_preview::Runtime rt;execute("FUNCTION change()\nRETURN $_RANDOM_LOWER_LETTER_KEYCODE\nEND_FUNCTION\nVAR $old=$_RANDOM_UPPER_LETTER_KEYCODE+change()\nVAR $k=4\nINJECT_VAR $k\n",p,rt,h);check(rt.state()==ds_preview::State::Completed&&h.draws==2&&variable(rt,"$old")==521&&h.events.size()==1,"getter operand cached through suspended function exactlyonce");
}else if(id=="AC17"){
 rng_mock::values={UINT32_MAX,0};completed("VAR $k=$_RANDOM_LOWER_LETTER_KEYCODE\nINJECT_VAR $k\n");oneA();check(rng_mock::calls==2,"bounded sampler rejects biased tail without selecting a new accepted operation");
}else if(id=="AC18"){
 rng_mock::fallback=UINT32_MAX;runSource("VAR $k=$_RANDOM_LOWER_LETTER_KEYCODE\nINJECT_VAR $k\n");check(route_u::status().errorCode==unsigned(ds_preview::ErrorCode::RandomUnavailable)&&rng_mock::calls==8&&operations().empty(),"getter exhaustion bounded and no key output");noReplay();
}else if(id=="AC19"){
 completed("HOLD SHIFT\nVAR $k=4\nINJECT_VAR $k\nRELEASE SHIFT\n");check(operations().size()==4,"persistent Shift restored after transient");exactReport(0,2,{});exactReport(1,2,{4});exactReport(2,2,{});exactReport(3,0,{});
}else if(id=="AC20"){
 completed("HOLD b\nVAR $k=516\nINJECT_VAR $k\nRELEASE b\n");exactReport(0,0,{5});exactReport(1,2,{5,4});exactReport(2,0,{5});exactReport(3,0,{});
}else if(id=="AC21"){
 runSource("HOLD a\nVAR $k=4\nINJECT_VAR $k\n");check(route_u::status().reason!=route_u::Reason::Completed&&operations().size()==1&&!hid_backend::hasPersistent()&&zero(lower::calls[lower::count-1]),"collision refuses instead of releasing owned key");noReplay();
}else if(id=="AC22"){
 runSource("HOLD a\nHOLD b\nHOLD c\nHOLD d\nHOLD e\nHOLD f\nVAR $k=10\nINJECT_VAR $k\n");check(route_u::status().reason!=route_u::Reason::Completed&&operations().size()==6&&!hid_backend::hasPersistent()&&zero(lower::calls[lower::count-1]),"sixheld limit refuses seventh transient without dropping held state");
}else if(id=="AC23"){
 rng_mock::values={0,0};put("/x.txt","VAR $k=$_RANDOM_LOWER_LETTER_KEYCODE\nINJECT_VAR $k\n");start();awaitPhase("Press");mock::usbReady=false;unsigned n=lower::count;for(unsigned i=0;i<25;++i)trialTick();check(lower::count==n&&rng_mock::calls==1,"transportretry leaves captured value unchanged");mock::usbReady=true;trialDone();oneA();noReplay();
}else if(id=="AC24"){
 put("/x.txt","HOLD SHIFT\nVAR $k=4\nINJECT_VAR $k\nSTRING BAD\n");start();reports(1);awaitPhase("Press");mock::usbReady=false;handleStop(&r);for(unsigned i=0;i<20;++i)trialTick();check(route_u::owned()&&operations().size()==1,"STOP holds lease while priorityclear blocked");mock::usbReady=true;trialDone();check(route_u::status().reason==route_u::Reason::Cancelled&&operations().size()==1&&!hid_backend::hasPersistent()&&zero(lower::calls[lower::count-1]),"STOP suppresses transient and clears heldShift");noReplay();
}else if(id=="AC25"){
 put("/x.txt","VAR $k=4\nINJECT_VAR $k\nSTRING BAD\n");start();awaitPhase("Press");mock::usbMounted=false;tud_umount_cb();trialDone();check(operations().empty()&&route_u::status().phase==route_u::Phase::Quarantined,"disconnect cannot replay queued scalar output");noReplay();
}else if(id=="AC26"){
 put("/x.txt","VAR $k=4\nINJECT_VAR $k\n");start();awaitPhase("Press");lower::next=lower::Outcome::FalseAfterPossibleAcceptance;trialTick();trialDone();check(route_u::status().phase==route_u::Phase::Quarantined,"ambiguous H1keypress acceptance quarantines");noReplay();
}else if(id=="AC27"){
 NumericHarness h;h.raw={0,20};h.refuse=3;ds_preview::Program p;ds_preview::Runtime rt;execute("VAR $k=$_RANDOM_UPPER_LETTER_KEYCODE\n$_JITTER_ENABLED=TRUE\nINJECT_VAR $k\n",p,rt,h);check(rt.state()==ds_preview::State::Completed&&h.draws==2&&h.events.size()==1&&h.attempts==4&&h.events[0].modifiers==2&&h.events[0].value==4,"key selection and ordinary jitter independently cached across retries");
}else if(id=="AC28"){
 runSource("HOLD SHIFT\nVAR $k=0\nINJECT_VAR $k\nSTRING BAD\n");check(route_u::status().errorCode==unsigned(ds_preview::ErrorCode::InvalidExperimentalKeycode)&&operations().size()==1&&!hid_backend::hasPersistent()&&zero(lower::calls[lower::count-1]),"invalid keyvalue triggers heldcleanup before subsequent text");lower::reset();completed("VAR $k=4\nINJECT_VAR $k\n");oneA();
}else if(id=="AC29"){
 NumericHarness h;h.raw={0,1};ds_preview::Program p;ds_preview::Runtime rt;execute("VAR $n=2\nWHILE $n>0\nVAR $k=$_RANDOM_LOWER_LETTER_KEYCODE\nINJECT_VAR $k\n$n=$n-1\nEND_WHILE\n",p,rt,h);check(rt.state()==ds_preview::State::Completed&&h.draws==2&&h.events.size()==2&&h.events[0].value==4&&h.events[1].value==5,"distinct runtime getter references select distinct operations while loops stay bounded");
}else if(id=="AC30"){
 ds_preview::Program p;const char*s="VAR $k=$_RANDOM_LOWER_LETTER_KEYCODE\nINJECT_VAR $k\n";check(p.compile(s,strlen(s)),"compile fixedstate probe");ds_preview::Runtime rt;UpperProvider q;rt.randomReader=UpperProvider::read;rt.randomContext=&q;check(rt.start(p,[](void*c,const ds_preview::Event&e){auto& q=*static_cast<UpperProvider*>(c);++q.tries;check(e.type==ds_preview::EventType::KeyTap&&e.value==4&&!e.modifiers,"cached exact H1 tap on every retry");return q.tries<5?ds_preview::Accept::Retry:ds_preview::Accept::Accepted;},&q),"start fixedstate probe");auto before=native_alloc::calls();for(unsigned i=0;i<100&&rt.state()==ds_preview::State::Running;++i)rt.tick(i);check(native_alloc::calls()==before&&rt.state()==ds_preview::State::Completed&&q.calls==1,"H1 scalar capture/injection does not allocate C++heap");
}else check(false,"unknown H1case");std::cout<<"PASS "<<id<<" ("<<assertions<<" assertions)\n";return 0;}catch(const std::exception&e){std::cerr<<"FAIL "<<argv[1]<<": "<<e.what()<<" ("<<assertions<<")\n";return 1;}}
