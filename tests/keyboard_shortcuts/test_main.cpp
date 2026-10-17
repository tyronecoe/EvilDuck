#define main historical_w_main
#include "../stage28w/test_main.cpp"
#undef main
#include "shortcut_keys.h"
#include <vector>
static void runSource(const std::string& s){put("/x.txt",s);start();done();check(!route_u::owned()&&route_u::status().reason==route_u::Reason::Completed,"local completed");}
static void rejectSource(const std::string&s){put("/x.txt","STRINGLN MUST-NOT-APPEAR\n"+s);start();done();check(!route_u::owned()&&route_u::status().reason==route_u::Reason::Compiler,"preflight rejected");check(lower::count==0,"zero HID including sync before malformed source");}
static void phase(const char* p){for(unsigned i=0;i<20000;++i){if(route_u::status().phase==route_u::Phase::Running&&std::string(route_b::phase())==p)return;tick();}check(false,"bounded phase reached");}
static std::vector<size_t> presses(){std::vector<size_t> r;for(size_t i=0;i<lower::count;++i)if(lower::calls[i].bytes[2])r.push_back(i);return r;}
static void reports(const std::vector<std::pair<uint8_t,uint8_t>>& wanted){
 auto got=presses();check(got.size()==wanted.size(),"exact number of presses");
 for(size_t n=0;n<got.size();++n){auto i=got[n];const auto& c=lower::calls[i];check(c.bytes[0]==wanted[n].first&&c.bytes[1]==0&&c.bytes[2]==wanted[n].second,"modifier/usage/reserved exact");for(int j=3;j<8;++j)check(c.bytes[j]==0,"unused key slots zero");check(c.id==1&&c.instance==0&&c.outcome==lower::Outcome::True,"mock report id1 instance0 accepted");check(i+1<lower::count,"restoration follows");auto& q=lower::calls[i+1];for(auto b:q.bytes)check(b==0,"all eight restoration bytes neutral");check(q.operation==c.operation&&q.session==c.session,"same immutable operation restoration");}
}
int main(int argc,char**argv){if(argc!=2)return 2;if(argv[1][0]=='W')return historical_w_main(argc,argv);try{
 mscMock::reset();mock::reset();setup();check(startupControlledReady&&settings::ready(),"actual controlled startup");check(route_u::bindOwner(),"single owner");lower::reset();lower::count=0;mock::text="";mock::blockingDelays=0;auto id=std::string(argv[1]);
 if(id=="K01"){runSource("COMMAND a\n");reports({{8,4}});}
 else if(id=="K02"){runSource("SHIFT LEFTARROW\n");reports({{2,0x50}});}
 else if(id=="K03"){runSource("CONTROL a\nCTRL a\nCOMMAND a\nWINDOWS a\nGUI a\nALT a\nOPTION a\n");reports({{1,4},{1,4},{8,4},{8,4},{8,4},{4,4},{4,4}});}
 else if(id=="K04"){runSource("CTRL ALT DELETE\nCTRL-ALT-DELETE\nCOMMAND-OPTION-SHIFT LEFT\nCOMMAND CTRL SHIFT a\n");reports({{5,0x4c},{5,0x4c},{14,0x50},{11,4}});}
 else if(id=="K05"){std::string s;std::vector<std::pair<uint8_t,uint8_t>> w;for(int i=1;i<=24;++i){s+="F"+std::to_string(i)+"\n";w.push_back({0,static_cast<uint8_t>(i<=12?0x3a+i-1:0x68+i-13)});}runSource(s);reports(w);}
 else if(id=="K06"){runSource("HOME\nEND\nPAGEUP\nPAGEDOWN\nINSERT\nDELETE\nBACKSPACE\nUP\nDOWN\nLEFT\nRIGHT\nTAB\nSPACE\nESCAPE\nMENU\nAPP\nPRINTSCREEN\nPAUSE\nBREAK\nCAPSLOCK\nNUMLOCK\nSCROLLLOCK\n");std::vector<std::pair<uint8_t,uint8_t>> w;for(auto u:{0x4a,0x4d,0x4b,0x4e,0x49,0x4c,0x2a,0x52,0x51,0x50,0x4f,0x2b,0x2c,0x29,0x65,0x65,0x46,0x48,0x48,0x39,0x53,0x47})w.push_back({0,static_cast<uint8_t>(u)});reports(w);}
 else if(id=="K07"){runSource("CTRL !\nCOMMAND ?\nALT [\nCTRL +\nCTRL -\n");reports({{3,0x1e},{10,0x38},{4,0x2f},{3,0x2e},{1,0x2d}});}
 else if(id=="K08"){runSource("COMMAND A\nSHIFT a\nCTRL 0\nSHIFT TAB\n");reports({{10,4},{2,4},{1,0x27},{2,0x2b}});}
 else if(id=="K09"){for(auto s:{"CTRL CTRL a\n","CTRL CONTROL a\n","GUI COMMAND a\n","ALT OPTION a\n"})rejectSource(s);}
 else if(id=="K10"){for(auto s:{"CTRL\n","CTRL-SHIFT\n","CTRL--a\n","CTRL a b\n","CTRL-a-b\n","CTRL UNKNOWN\n","F0\n","F25\n","F01\n","SHIFT - a\n"})rejectSource(s);}
 else if(id=="K11"){rejectSource("IF FALSE THEN\nCTRL CTRL a\nEND_IF\n");rejectSource("FUNCTION unused()\nCTRL UNKNOWN\nEND_FUNCTION\n");}
 else if(id=="K12"){runSource("FUNCTION edit()\nSHIFT LEFT\nRETURN 1\nEND_FUNCTION\nVAR $n=0\nWHILE $n < 2\nIF edit() == 1 THEN\nCOMMAND a\nEND_IF\n$n=$n+1\nEND_WHILE\n");reports({{2,0x50},{8,4},{2,0x50},{8,4}});}
 else if(id=="K13"){runSource("DEFINE #K LEFTARROW\nDEFINE #KK RIGHTARROW\nSHIFT #K\nSHIFT #KK\n");reports({{2,0x50},{2,0x4f}});}
 else if(id=="K14"||id=="K15"){put("/x.txt","COMMAND a\n");start();phase(id=="K14"?"Press":"Release");auto n=lower::count;mock::usbReady=false;for(int i=0;i<20;++i)tick();check(lower::count==n,"not ready makes zero lower calls");mock::usbReady=true;done();check(!route_u::owned(),"recovered without replay");reports({{8,4}});}
 else if(id=="K16"){put("/x.txt","COMMAND a\nSTRING BAD\n");start();phase("Wait");route_u::stop();done();check(!route_u::owned()&&route_u::status().reason==route_u::Reason::Cancelled,"cancel clears local state");reports({{8,4}});}
 else if(id=="K17"){put("/x.txt","SHIFT LEFT\nSTOP_PAYLOAD\nCOMMAND a\n");start();done();check(route_u::status().reason==route_u::Reason::Cancelled,"STOP_PAYLOAD stops");reports({{2,0x50}});}
 else if(id=="K18"){put("/x.txt","COMMAND a\nVAR $zero=0\nVAR $bad=1/$zero\n");start();done();check(route_u::status().reason!=route_u::Reason::Completed&&!route_u::owned(),"runtime arithmetic error cleaned");reports({{8,4}});}
 else if(id=="K19"){put("/x.txt","COMMAND a\n");start();phase("Wait");auto n=lower::count;mock::usbMounted=false;USB.stopped(nullptr,nullptr,ARDUINO_USB_STOPPED_EVENT,nullptr);done();check(route_u::status().phase==route_u::Phase::Quarantined&&lower::count==n,"loss quarantines without claiming host release");}
 else if(id=="K20"||id=="K21"){put("/x.txt","COMMAND a\nSTRING BAD\n");start();phase(id=="K20"?"Press":"Release");auto n=lower::count;lower::next=lower::Outcome::FalseAfterPossibleAcceptance;tick();done();check(route_u::status().phase==route_u::Phase::Quarantined&&lower::count==n+1,"ambiguous report quarantined without resend");}
 else if(id=="K22"){put("/x.txt","COMMAND a\nSTRING BAD\n");start();phase("Press");route_u::stop();done();check(!route_u::owned(),"cancel before press cleaned");check(presses().empty(),"no keypress before cancelled press");runSource("SHIFT RIGHT\n");reports({{2,0x4f}});}
 else if(id=="K23"){for(auto s:{"RGUI a\n","RCOMMAND a\n","RWINDOWS a\n","ROPTION a\n","INJECT_MOD COMMAND\n","RESET\n"})rejectSource(s);put("/x.txt","IF FALSE THEN\nHOLD a\nEND_IF\n");start();done();check(route_u::status().reason==route_u::Reason::Capability&&lower::count==0,"persistent ownership gate unchanged");}
 else if(id=="K24"){rejectSource("FUNCTION COMMAND()\nRETURN 1\nEND_FUNCTION\n");rejectSource("FUNCTION HOME()\nRETURN 1\nEND_FUNCTION\n");rejectSource("DEFINE #M COMMAND\n#M a\n");runSource("VAR $COMMAND=1\nIF $COMMAND == 1 THEN\nSHIFT LEFT\nEND_IF\n");reports({{2,0x50}});}
 else if(id=="K25"){put("/x.txt","COMMAND a\n");start();phase("Press");auto state=backend_b::status();auto count=lower::count;bool scope=true,sent=true;std::thread other([&]{u_platform::taskForTest(2);backend_b::Scope permission(state.session,state.operation);scope=bool(permission);uint8_t key=4;sent=hid_backend::beginReport(8,&key,1);});other.join();check(!scope&&!sent&&lower::count==count,"foreign RTOS task cannot borrow shortcut owner");done();check(!route_u::owned(),"owner still progresses");reports({{8,4}});}
 else check(false,"unknown test");check(mock::blockingDelays==0,"no blocking HID helpers");std::cout<<"PASS "<<id<<" ("<<assertions<<" assertions)\n";return 0;
 }catch(const std::exception&e){std::cerr<<"FAIL "<<argv[1]<<": "<<e.what()<<" ("<<assertions<<")\n";return 1;}}
