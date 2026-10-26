#include "random_parent_cases.inc"

static const char* textSuffixes[]={"POWERSHELL","BATCH","BASH","JAVASCRIPT","PYTHON","RUBY","HTML"};
static std::string textEvents(const char* source){
 ds_preview::Program p;ds_preview::Runtime rt;NumericHarness h;execute(source,p,rt,h);
 check(rt.state()==ds_preview::State::Completed,"text-only runtime completed");std::string out;
 for(auto e:h.events){if(e.type==ds_preview::EventType::Character)out+=char(e.value);else {check(e.type==ds_preview::EventType::KeyTap&&e.value==40,"only explicit newline event besides characters");out+='\n';}}
 return out;
}
static void oneA(){check(operations().size()==2,"one lowercase a press/release");exactReport(0,0,{4});exactReport(1,0,{});}
static std::vector<lower::Call> clears(){std::vector<lower::Call> out;for(size_t i=0;i<lower::count;++i)if(lower::calls[i].clear)out.push_back(lower::calls[i]);return out;}
static void pendingReset(){put("/x.txt","HOLD SHIFT\nDELAY 50\nRESET\nSTRING BAD\n");start();reports(1);mock::usbReady=false;awaitPhase("Reset");}
static bool resetReentrantAccepted;

int main(int argc,char** argv){if(argc!=2)return 2;if(argv[1][0]!='V')return randomization_jitter_main(argc,argv);
try {mscMock::reset();mock::reset();setup();check(startupControlledReady&&route_u::bindOwner(),"actual controlled composed startup");lower::reset();led_mock::nowUs=0;rng_mock::reset();auto r=req();std::string id=argv[1];
if(id=="V01"){
 for(const char* suffix:textSuffixes)for(bool newline:{false,true}){lower::reset();std::string s=std::string(newline?"STRINGLN_":"STRING_")+suffix+"\na\n"+(newline?"END_STRINGLN\n":"END_STRING\n");completed(s.c_str());check(operations().size()==(newline?4u:2u),"all fourteen aliases use ordinary character/report path");exactReport(0,0,{4});exactReport(1,0,{});if(newline){exactReport(2,0,{40});exactReport(3,0,{});}}
}else if(id=="V02"){
 check(textEvents("STRING_PYTHON\n\t a  \n  b\nEND_STRING\n")=="a  b","STRING alias trims leading whitespace and concatenates exact retained bytes");
}else if(id=="V03"){
 check(textEvents("STRINGLN_HTML\n\t  a  \n\nb\nEND_STRINGLN\n")=="  a  \n\nb\n","STRINGLN alias strips one tab, preserves spaces and blank lines, emits exact enters");
}else if(id=="V04"){
 check(textEvents("STRINGLN_BASH\nRESET\nWHILE\nEND_IF\nDEFINE #X a\nEND_STRINGLN\n")=="RESET\nWHILE\nEND_IF\nDEFINE #X a\n","command-looking block lines remain literal text");
}else if(id=="V05"){
 for(const char* suffix:textSuffixes)for(bool newline:{false,true}){lower::reset();std::string s=std::string(newline?"STRINGLN_":"STRING_")+suffix+"\na\n"+(newline?"END_STRING\n":"END_STRINGLN\n");rejected(s.c_str());}
}else if(id=="V06"){
 for(const char* s:{"STRING_PYTHON\na\n","STRINGLN_HTML a\n","STRING_PYTHON a\n","STRING_UNRECOGNIZED\na\nEND_STRING\n","STRINGLN_RUBY\nSTRING_BASH\nEND_STRINGLN\n"}){lower::reset();rejected(s);}
}else if(id=="V07"){
 check(textEvents("STRINGLN_PYTHON\nEND_STRINGLN_PYTHON\nEND_STRINGLN\n")=="END_STRINGLN_PYTHON\n","only canonical terminator closes alias block");
}else if(id=="V08"){
 completed("DEFINE #X a\nSTRING_POWERSHELL\n#X\nEND_STRING\n");oneA();
}else if(id=="V09"){
 completed("IF_DEFINED_TRUE #ABSENT\nSTRING_PYTHON malformed\nUNSUPPORTED\nEND_IF_DEFINED\nSTRING a\n");oneA();
}else if(id=="V10"){
 completed("FUNCTION text()\nSTRING_BATCH\na\nEND_STRING\nRETURN 1\nEND_FUNCTION\nVAR $n=0\nWHILE $n<2\n$n=$n+text()\nEND_WHILE\n");check(operations().size()==4,"alias executes through function and loop");exactReport(0,0,{4});exactReport(2,0,{4});
}else if(id=="V11"){
 completed("STRING_RUBY\r\na\r\nEND_STRING");oneA();lower::reset();rejected("\xef\xbb\xbfSTRING_HTML\na\nEND_STRING\n");check(lower::count==0,"production adapter ASCII/BOM boundary remains unchanged");
}else if(id=="V12"){
 const char* s="FUNCTION unused()\nSTRINGLN_JAVASCRIPT\na\nEND_STRING\nEND_FUNCTION\nSTRING a\n";rejected(s);ds_preview::Program p;check(!p.compile(s,strlen(s))&&p.error().line!=0,"retained unused function malformed block has physical source diagnostic");
}else if(id=="V13"){
 completed("REPEAT 2 STRING a\n");check(operations().size()==4,"inline repeat executes exact two taps");exactReport(0,0,{4});exactReport(1,0,{});exactReport(2,0,{4});exactReport(3,0,{});
}else if(id=="V14"){
 completed("REPEAT 3 TAB\nREPEAT 2 CTRL a\nREPEAT 2 INJECT_MOD SHIFT\n");check(operations().size()==14,"keys chords and modifier taps repeat exactly");for(unsigned i=0;i<3;++i){exactReport(i*2,0,{43});exactReport(i*2+1,0,{});}for(unsigned i=6;i<10;i+=2){exactReport(i,1,{4});exactReport(i+1,0,{});}for(unsigned i=10;i<14;i+=2){exactReport(i,2,{});exactReport(i+1,0,{});}
 lower::reset();rng_mock::reset();rng_mock::fallback=3;completed("HOLD SHIFT\n$_JITTER_ENABLED=TRUE\n$_JITTER_MAX=3\nREPEAT 2 TAB\nRELEASE SHIFT\n");check(operations().size()==6&&rng_mock::calls==2,"each repeated key receives fresh jitter while RELEASE consumes no entropy");exactReport(0,2,{});exactReport(1,2,{43});exactReport(2,2,{});exactReport(3,2,{43});exactReport(4,2,{});exactReport(5,0,{});check(uint32_t(operations()[3].at-operations()[2].at)>=3,"repeat preserves cooperative jitter before next press and persistent modifier restoration");
}else if(id=="V15"){
 rng_mock::values={0,1,25};completed("REPEAT 3 RANDOM_LOWERCASE_LETTER\n");check(rng_mock::calls==3&&operations().size()==6,"fresh random character for every repeated operation");exactReport(0,0,{4});exactReport(2,0,{5});exactReport(4,0,{29});
}else if(id=="V16"){
 NumericHarness h;h.raw={1,2};ds_preview::Program p;ds_preview::Runtime rt;execute("REPEAT 2 DELAY $_RANDOM_INT\n",p,rt,h);check(rt.state()==ds_preview::State::Completed&&h.draws==2&&h.events.size()==2,"repeat expression evaluated once afresh per operation");check(h.events[0].type==ds_preview::EventType::Delay&&h.events[0].value==1&&h.events[1].value==2,"repeated delays retain exact independent sampled values");
}else if(id=="V17"){
 completed("REPEAT 128 TAB\n");check(operations().size()==256,"upper repeat and IR limit exactly 128 taps");for(unsigned i=0;i<256;i+=2){exactReport(i,0,{43});exactReport(i+1,0,{});}
}else if(id=="V18"){
 for(const char* s:{"REPEAT 0 TAB\n","REPEAT 1 TAB\n","REPEAT 129 TAB\n","REPEAT 65535 TAB\n","REPEAT -2 TAB\n","REPEAT 2\n","REPEAT $x TAB\n","DEFINE #N 2\nREPEAT #N TAB\n","REPLAY 2\n"}){lower::reset();rejected(s);}
}else if(id=="V19"){
 for(const char* body:{"REPEAT 2 TAB","IF TRUE THEN","VAR $x=1","$x=1","HOLD SHIFT","RELEASE SHIFT","RESET","WAIT_FOR_CAPS_ON","STRING_HTML","FUNCTION f()","STOP_PAYLOAD"}){lower::reset();std::string s=std::string("REPEAT 2 ")+body+"\n";rejected(s.c_str());}
}else if(id=="V20"){
 const char* s="STRING a\nREPEAT 128 TAB\n";rejected(s);ds_preview::Program p;check(!p.compile(s,strlen(s))&&p.error().code==ds_preview::ErrorCode::CodeLimit&&p.error().line==2,"expanded IR limit rejects at repeat source line before output");
}else if(id=="V21"){
 std::string s="REPEAT 128 STRING "+std::string(200,'a')+"\n";ds_preview::Program p;check(p.compile(s.c_str(),s.size())&&p.instructions()==128,"repeat shares bounded operand arena instead of cloning 25KiB text");
}else if(id=="V22"){
 const char* s="REPEAT 128 TAB\n";SourceProbe q;q.memory={s,strlen(s),0};ds_preview::Program p;ds_preview::CompileSession c;check(c.start(p,q.reader()),"cooperative repeat compile starts");unsigned steps=0;while(c.state()==ds_preview::CompileState::Compiling&&steps<20000){c.step();auto w=c.work();check(w.nodes<=1&&w.bytes<=32&&w.callbacks<=1&&w.lines<=1&&w.expressions<=1,"one clone or ordinary bounded work per compiler step");++steps;}check(c.state()==ds_preview::CompileState::Complete&&p.instructions()==128&&steps>=128,"repeat expansion cannot complete as one unbounded compiler step");check(ds_preview::CompileSession::compilerBytes()<=4096,"compiler workspace bound retained");
}else if(id=="V23"){
 completed("FUNCTION text()\nREPEAT 2 STRING a\nRETURN 1\nEND_FUNCTION\nVAR $n=0\nWHILE $n<2\n$n=$n+text()\nEND_WHILE\n");check(operations().size()==8,"repeat function body runs twice per call and twice per loop");for(unsigned i=0;i<8;i+=2)exactReport(i,0,{4});
}else if(id=="V24"){
 put("/x.txt","HOLD SHIFT\nREPEAT 100 DELAY 1000\nSTRING BAD\n");start();reports(1);auto before=mock::now;handleStop(&r);trialDone();check(route_u::status().reason==route_u::Reason::Cancelled&&mock::now-before<500,"STOP cooperatively interrupts repeated delay");check(operations().size()==1&&!hid_backend::hasPersistent()&&!route_u::owned(),"STOP priority cleanup releases persistent modifier without later text");noReplay();
}else if(id=="V25"){
 completed("HOLD SHIFT\nRESET\nSTRING a\n");check(operations().size()==3,"RESET is neutral clear, not an application keystroke");exactReport(0,2,{});exactReport(1,0,{4});exactReport(2,0,{});bool middle=false;for(size_t i=0;i<lower::count;++i)if(lower::calls[i].clear&&lower::calls[i].operation>operations()[0].operation&&lower::calls[i].operation<operations()[1].operation){check(zero(lower::calls[i]),"RESET exact all-zero eight-byte local report");check(lower::calls[i].session==operations()[0].session,"RESET retains current owner session");middle=true;}check(middle,"local RESET clear precedes subsequent lowercase press");
}else if(id=="V26"){
 completed("HOLD a\nHOLD b\nRESET\nSTRING c\n");check(operations().size()==4,"RESET removes held nonmodifiers without retyping them");exactReport(0,0,{4});exactReport(1,0,{4,5});exactReport(2,0,{6});exactReport(3,0,{});
}else if(id=="V27"){
 auto before=backend_b::status().clearSubmitted;completed("RESET\nRESET\n");auto cs=clears();check(operations().empty()&&cs.size()>=4,"repeated RESET each requires neutral submission plus session sync/cleanup");check(backend_b::status().clearSubmitted>=before+4,"distinct neutral clear counter for both resets");std::set<uint64_t> ids;for(auto c:cs){check(zero(c),"every local RESET/sync/cleanup report neutral");ids.insert(c.operation);}check(ids.size()>=3,"repeated reset cannot borrow stale operation acknowledgement");
}else if(id=="V28"){
 completed("VAR $v=7\n$_RANDOM_MIN=7\n$_RANDOM_MAX=7\n$_JITTER_ENABLED=TRUE\n$_JITTER_MAX=0\nHOLD SHIFT\nRESET\nIF $v==7&&$_RANDOM_INT==7&&$_RANDOM_MIN==7&&$_RANDOM_MAX==7&&$_JITTER_ENABLED==TRUE&&$_JITTER_MAX==0 THEN\nSTRING a\nEND_IF\n");check(operations().size()==3&&rng_mock::calls==0,"RESET preserves user variables and per-run random/jitter settings");exactReport(1,0,{4});
}else if(id=="V29"){
 for(const char* s:{"RESET extra\n","IF FALSE THEN\nRESET extra\nEND_IF\n","FUNCTION unused()\nRESET 1\nEND_FUNCTION\nSTRING a\n"}){lower::reset();rejected(s);}
}else if(id=="V30"){
 put("/x.txt","HOLD SHIFT\nDELAY 50\nRESET\nSTRING a\n");start();reports(1);mock::usbReady=false;awaitPhase("Reset");auto n=lower::count;auto s=backend_b::status();for(unsigned i=0;i<100;++i)trialTick();check(route_u::owned()&&lower::count==n&&!hid_backend::hasPersistent(),"not-ready RESET retains lease and never calls lower layer or restores held state");check(backend_b::status().clearSubmitted<s.clearRequest,"no false clear acknowledgement while transport not ready");mock::usbReady=true;trialDone();check(route_u::status().reason==route_u::Reason::Completed&&operations().size()==3,"RESET resumes once before following character");exactReport(1,0,{4});noReplay();
}else if(id=="V31"){
 pendingReset();handleStop(&r);for(unsigned i=0;i<10;++i)trialTick();check(route_u::owned()&&route_u::requestStart("/x.txt")==route_u::Reply::Busy,"STOP keeps cleanup lease exclusive during pending RESET");mock::usbReady=true;trialDone();check(route_u::status().reason==route_u::Reason::Cancelled&&operations().size()==1&&!hid_backend::hasPersistent(),"STOP suppresses text and completes only neutral cleanup");noReplay();
}else if(id=="V32"){
 pendingReset();lower::next=lower::Outcome::FalseAfterPossibleAcceptance;mock::usbReady=true;trialTick();trialDone();check(route_u::status().phase==route_u::Phase::Quarantined&&backend_b::status().quarantined,"ambiguous RESET submission quarantines");check(operations().size()==1,"no application report after ambiguous clear");noReplay();
}else if(id=="V33"){
 pendingReset();auto n=lower::count;mock::usbMounted=false;tud_umount_cb();trialDone();check(route_u::status().phase==route_u::Phase::Quarantined&&lower::count==n,"disconnect during RESET never submits or advances text");mock::usbMounted=true;tud_mount_cb();noReplay();
}else if(id=="V34"){
 pendingReset();auto s=backend_b::status();auto n=lower::count;route_b::Id id2{};check(route_u::requestStart("/x.txt")==route_u::Reply::Busy&&route_b::reset(s.session+1,id2)==route_b::Admission::Rejected,"pending RESET rejects competing owner or wrong session");check(lower::count==n&&route_u::owned(),"denied competing reset leaves current lease and output intact");route_u::stop();mock::usbReady=true;trialDone();
}else if(id=="V35"){
 completed("HOLD SHIFT\nRESET\n");auto first=route_u::status().request;auto firstSession=operations()[0].session;lower::reset();completed("STRING a\n");check(route_u::status().request!=first&&operations()[0].session!=firstSession,"fresh run obtains new request/session after RESET");oneA();noReplay();
}else if(id=="V36"){
 std::string s="HOLD SHIFT\nSTRINGLN_BASH\n"+std::string(200,'a')+"\n"+std::string(200,'a')+"\nEND_STRINGLN\nSTRING BAD\n";put("/x.txt",s.c_str());start();reports(2);handleStop(&r);trialDone();check(route_u::status().reason==route_u::Reason::Cancelled&&!hid_backend::hasPersistent(),"STOP interrupts streaming alias and clears persistent state");for(auto c:operations())check(!contains(c,5),"no following BAD command leaked through cancelled block");noReplay();
}else if(id=="V37"){
 rng_mock::values={0,25};put("/x.txt","REPEAT 2 RANDOM_LOWERCASE_LETTER\n");start();awaitPhase("Press");mock::usbReady=false;for(unsigned i=0;i<30;++i)trialTick();check(rng_mock::calls==1&&operations().empty(),"random repeat operand cached during first transport retry");mock::usbReady=true;trialDone();check(route_u::status().reason==route_u::Reason::Completed&&rng_mock::calls==2&&operations().size()==4,"each repeated random event selected once including retries");exactReport(0,0,{4});exactReport(2,0,{29});
}else if(id=="V38"){
 const char* s="REPEAT 128 TAB\n";SourceProbe q;q.memory={s,strlen(s),0};ds_preview::Program p;ds_preview::CompileSession c;check(c.start(p,q.reader()),"start cancelled compile");for(unsigned i=0;i<100&&c.state()==ds_preview::CompileState::Compiling;++i)c.step();check(c.state()==ds_preview::CompileState::Compiling,"cooperative expansion still interruptible");c.cancel();check(c.state()==ds_preview::CompileState::Cancelled&&!p.ready(),"cancelled clone expansion never publishes partial Program");check(p.compile("STRING a\n",strlen("STRING a\n")),"subsequent compile independent of cancelled pending copies");
}else if(id=="V39"){
 rng_mock::fallback=65535;completed("HOLD SHIFT\n$_JITTER_ENABLED=TRUE\n$_JITTER_MAX=65535\nRESET\n");check(rng_mock::calls==0&&operations().size()==1,"RESET and priority cleanup bypass typing jitter and do not consume entropy");
}else if(id=="V40"){
 pendingReset();resetReentrantAccepted=true;lower::hook=[](){auto s=backend_b::status();route_b::Id id2{};resetReentrantAccepted=route_b::reset(s.session,id2)!=route_b::Admission::Rejected;};mock::usbReady=true;trialTick();trialDone();check(!resetReentrantAccepted&&route_u::status().reason==route_u::Reason::Completed,"in-I/O reentrant RESET is refused without blocking current operation");check(operations().size()==7,"only intended held plus three BAD taps after one RESET");auto cs=clears();check(cs.size()==3,"reentrant RESET did not add clear, only initial sync/reset/terminal cleanup");
}else check(false,"unknown text/keyboard case");
std::cout<<"PASS "<<id<<" ("<<assertions<<" assertions)\n";return 0;
}catch(const std::exception& e){std::cerr<<"FAIL "<<argv[1]<<": "<<e.what()<<" ("<<assertions<<")\n";return 1;}}
