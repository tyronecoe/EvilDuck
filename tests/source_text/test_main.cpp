#include "payload_restart_parent_cases.inc"

static const std::string Bom="\xef\xbb\xbf";
struct ChunkSource {
 std::string data,observed;size_t pos=0,limit=32;std::vector<size_t> chunks;size_t turn=0;unsigned reads=0,seeks=0;bool interleave=false,retry=false;
 static ds_preview::ReadResult read(void* c,char* out,size_t cap){auto& s=*static_cast<ChunkSource*>(c);++s.reads;
  if(s.retry){s.retry=false;return {ds_preview::ReadStatus::Retry,0};}
  if(s.pos==s.data.size())return {ds_preview::ReadStatus::Eof,0};
  size_t n=std::min(cap,std::min(s.limit,s.data.size()-s.pos));if(s.turn<s.chunks.size())n=std::min(n,s.chunks[s.turn++]);
  memcpy(out,s.data.data()+s.pos,n);s.observed.append(out,n);s.pos+=n;if(s.interleave)s.retry=true;return {ds_preview::ReadStatus::Data,n};
 }
 static bool seek(void* c,size_t pos){auto& s=*static_cast<ChunkSource*>(c);++s.seeks;if(pos>s.data.size())return false;s.pos=pos;s.turn=0;s.retry=false;return true;}
 ds_preview::Reader reader(){return {read,seek,this,data.size()};}
};
static bool sourceReady(native_b::Adapter& a,ChunkSource& q){
 if(!a.prepare(q.reader()))return false;
 for(unsigned i=0;i<100000&&(a.state()==native_b::State::Loading||a.state()==native_b::State::Compiling);++i)a.step(mock::now++);
 return a.state()==native_b::State::Ready;
}
static void sourceRun(native_b::Adapter& a){check(a.start(mock::now),"captured source starts explicit adapter lease");for(unsigned i=0;i<10000&&(a.state()!=native_b::State::Completed&&a.state()!=native_b::State::Error&&a.state()!=native_b::State::Quarantined);++i)a.step(mock::now++);check(a.state()==native_b::State::Completed&&!a.leased(),"streamed source completed with cleanup");}
static void goodChunks(const std::string& s,size_t chunk,bool retry=false,std::vector<size_t> first={}){ChunkSource q;q.data=s;q.limit=chunk;q.interleave=retry;q.chunks=first;native_b::Adapter a;check(sourceReady(a,q),"BOM/source accepted through actual streamed adapter");check(q.observed==s&&q.data==s,"reader bytes and marker preserved, no caller normalization");auto reads=q.reads;sourceRun(a);check(q.reads==reads&&q.seeks==1,"runtime uses captured Program without rereading source");}
static void badChunks(const std::string& s,size_t chunk=1,bool retry=false){ChunkSource q;q.data=s;q.limit=chunk;q.interleave=retry;native_b::Adapter a;check(!sourceReady(a,q)&&a.state()==native_b::State::Error,"invalid encoding/source rejected before lease");check(lower::count==0&&!a.leased(),"invalid source submits no sync/key/clear report");}
static std::string padded(std::string s,size_t bytes){while(bytes-s.size()>5){size_t n=std::min(size_t(180),bytes-s.size()-5);s+="REM "+std::string(n,'p')+"\n";}s+=std::string(bytes-s.size(),'\n');return s;}
static void sourceLettersA(unsigned n){check(operations().size()==2*n,"exact count of lowercase a taps");for(unsigned i=0;i<n;++i){exactReport(i*2,0,{4});exactReport(i*2+1,0,{});}}

int main(int argc,char** argv){if(argc!=2)return 2;if(argv[1][0]!='Z')return payload_restart_main(argc,argv);
try{mscMock::reset();mock::reset();setup();check(startupControlledReady&&route_u::bindOwner(),"actual composed controlled startup");lower::reset();led_mock::nowUs=0;rng_mock::reset();auto r=req();std::string id=argv[1];
if(id=="Z01"){
 for(size_t n=1;n<=32;++n){lower::reset();goodChunks(Bom+"STRING a\n",n);oneA();}
}else if(id=="Z02"){
 for(auto first:{std::vector<size_t>{1,1,1},std::vector<size_t>{1,2},std::vector<size_t>{2,1},std::vector<size_t>{3}}){lower::reset();goodChunks(Bom+"STRING a\n",32,true,first);oneA();}
}else if(id=="Z03"){
 for(const auto& s:{std::string("\xef"),std::string("\xef\xbb"),std::string("\xef\xbc\xbf"),std::string("\xef\xbb\xbe"),std::string("\xbb\xbf")}){lower::reset();badChunks(s,1,true);}
}else if(id=="Z04"){
 for(const auto& s:{Bom+Bom+"STRING a\n",std::string(" ")+Bom+"STRING a\n",std::string("REM x\n")+Bom+"STRING a\n",std::string("STRING ")+Bom+"a\n"}){lower::reset();badChunks(s,2,true);}
}else if(id=="Z05"){
 for(const auto& s:{std::string("\xff\xfeS\0",4),std::string("\xfe\xff\0S",4),std::string("STRING \xc3\xa9\n"),std::string("STRING a\0b\n",11),std::string("STRING a\x7f\n")}){lower::reset();badChunks(s);}
}else if(id=="Z06"){
 for(size_t n:{size_t(8191),size_t(8192)}){lower::reset();goodChunks(padded(Bom+"STRING a\n",n),32);oneA();}
 lower::reset();badChunks(padded(Bom+"STRING a\n",8193),32);
}else if(id=="Z07"){
 for(const auto& end:{std::string("\n"),std::string("\r\n"),std::string("")}){lower::reset();goodChunks(Bom+"REM first"+(end.empty()?"\n":end)+"STRING a"+end,1,true);oneA();}
}else if(id=="Z08"){
 lower::reset();badChunks(Bom+"STRING a\r",1);lower::reset();badChunks(Bom+"STRING a\rX",2);
}else if(id=="Z09"){
 for(const char* suffix:textSuffixes)for(bool newline:{false,true}){lower::reset();completed((std::string(newline?"STRINGLN_":"STRING_")+suffix+" a\n").c_str());check(operations().size()==(newline?4u:2u),"all14 inline aliases emit ordinary text plus exact optional ENTER");exactReport(0,0,{4});exactReport(1,0,{});if(newline){exactReport(2,0,{40});exactReport(3,0,{});}}
}else if(id=="Z10"){
 for(const char* suffix:textSuffixes)for(bool newline:{false,true}){std::string stem=newline?"STRINGLN":"STRING";std::string alias=stem+"_"+suffix;check(textEvents((alias+"   a  \n").c_str())==textEvents((stem+"   a  \n").c_str()),"all inline aliases preserve ordinary leading/trailing whitespace contract");check(textEvents((alias+"\ta\t \n").c_str())==textEvents((stem+"\ta\t \n").c_str()),"tab separator matches ordinary operand handling");}
}else if(id=="Z11"){
 for(const char* suffix:textSuffixes){lower::reset();completed((std::string("DEFINE #X a\nSTRING_")+suffix+" #X\n").c_str());oneA();}
}else if(id=="Z12"){
 check(textEvents("STRINGLN_PYTHON RESET\nSTRINGLN_HTML RESTART_PAYLOAD\nSTRING_BASH VAR $x=1\n")=="RESET\nRESTART_PAYLOAD\nVAR $x=1","inline alias contents are literal, never embedded language or control execution");check(textEvents("STRING_HTML a END_STRING\nSTRINGLN_HTML b END_STRINGLN\n")=="a END_STRINGb END_STRINGLN\n","ordinary inline alias extension does not strip official-looking terminator text");
}else if(id=="Z13"){
 for(const char* suffix:textSuffixes)for(bool newline:{false,true}){lower::reset();std::string s=std::string(newline?"STRINGLN_":"STRING_")+suffix+"   \n"+"a\n"+(newline?"END_STRINGLN\n":"END_STRING\n");completed(s.c_str());exactReport(0,0,{4});check(operations().size()==(newline?4u:2u),"whitespace-only arguments retain block behavior");}
}else if(id=="Z14"){
 check(textEvents("STRINGLN_HTML\nSTRING_PYTHON a\nSTRINGLN_BASH b\nEND_STRINGLN\n")=="STRING_PYTHON a\nSTRINGLN_BASH b\n","inline-command-looking lines within an active block remain literal");
}else if(id=="Z15"){
 for(const char* suffix:textSuffixes){lower::reset();completed((std::string("REPEAT 2 STRING_")+suffix+" a\n").c_str());sourceLettersA(2);lower::reset();completed((std::string("REPEAT 2 STRINGLN_")+suffix+" a\n").c_str());check(operations().size()==8,"inline STRINGLN alias repeat emits two text/enter pairs");exactReport(2,0,{40});exactReport(6,0,{40});}
}else if(id=="Z16"){
 for(const char* s:{"STRING_HTMLa a\n","STRINGLN_UNSUPPORTED a\n","STRING_ PYTHON a\n","STRINGLN_ HTML a\n","REPEAT 2 STRING_PYTHON\na\nEND_STRING\n","STRING_PYTHON\na\nEND_STRINGLN\n"}){lower::reset();rejected(s);}
}else if(id=="Z17"){
 completed("IF_DEFINED_TRUE #ABSENT\nSTRING_UNSUPPORTED a\nUNSUPPORTED\nEND_IF_DEFINED\nSTRING_HTML a\n");oneA();lower::reset();rejected("IF FALSE THEN\nSTRING_UNSUPPORTED a\nEND_IF\nSTRING_HTML a\n");
}else if(id=="Z18"){
 put("/x.txt",(Bom+"REM first\nSTRINGLN_PYTHON\na\nEND_STRING\n").c_str());start();trialDone();check(route_u::status().reason!=route_u::Reason::Completed&&lower::count==0&&route_u::status().line==4,"BOM is not a physical line; mismatched terminator diagnostics remain physical");
}else if(id=="Z19"){
 const char* s="FUNCTION STRING_HTML()\nEND_FUNCTION\n";rejected(s);lower::reset();completed("FUNCTION text()\nSTRING_PYTHON a\nRETURN 1\nEND_FUNCTION\nVAR $n=0\nWHILE $n<2\n$n=$n+text()\nEND_WHILE\n");sourceLettersA(2);
}else if(id=="Z20"){
 completed("HOLD SHIFT\nSTRING_PYTHON a\nSTRINGLN_HTML b\nRELEASE SHIFT\nSTRING_RUBY c\n");check(operations().size()==10,"inline aliases restore held Shift through text and newline");exactReport(0,2,{});exactReport(1,2,{4});exactReport(2,2,{});exactReport(3,2,{5});exactReport(4,2,{});exactReport(5,2,{40});exactReport(6,2,{});exactReport(7,0,{});exactReport(8,0,{6});exactReport(9,0,{});
}else if(id=="Z21"){
 put("/x.txt",(Bom+"STRING_PYTHON a\n").c_str());start();awaitPhase("Press");mock::usbReady=false;auto n=lower::count;for(unsigned i=0;i<50;++i)trialTick();check(lower::count==n&&operations().empty(),"inline BOM text retries do not submit or duplicate while unavailable");mock::usbReady=true;trialDone();check(route_u::status().reason==route_u::Reason::Completed,"retry resumes exactly once");oneA();noReplay();
}else if(id=="Z22"){
 put("/x.txt",(Bom+"HOLD SHIFT\nDELAY 5000\nSTRINGLN_PYTHON BAD\n").c_str());start();reports(1);handleStop(&r);trialDone();check(route_u::status().reason==route_u::Reason::Cancelled&&!hid_backend::hasPersistent()&&operations().size()==1,"STOP suppresses later alias and clears held Shift");noReplay();
}else if(id=="Z23"){
 put("/x.txt",(Bom+"STRING_PYTHON a\nHOLD SHIFT\nDELAY 20\nRESTART_PAYLOAD\nSTRING_HTML BAD\n").c_str());start();reports(5);exactReport(0,0,{4});exactReport(2,2,{});exactReport(3,0,{4});exactReport(4,0,{});restartStop();
}else if(id=="Z24"){
 put("/x.txt",(Bom+"STRINGLN_HTML a\n").c_str());start();awaitPhase("Press");lower::next=lower::Outcome::FalseAfterPossibleAcceptance;trialTick();trialDone();check(route_u::status().phase==route_u::Phase::Quarantined,"inline alias ambiguous acceptance quarantines without replay");noReplay();
}else if(id=="Z25"){
 auto save=req();save.body["name"]={"bom-portability.txt"};std::string bytes=Bom+"STRING_PYTHON a\r\n";save.body["content"]={String(bytes)};handleSaveScript(&save);check(save.code==200,"actual authenticated POST script saves BOM fixture");auto get=req();get.query["s"]={"bom-portability.txt"};handleGetScript(&get);check(get.code==200&&std::string(get.response.c_str(),get.response.length())==bytes,"actual authenticated GET preserves every byte including EFBBBF");check(operations().empty(),"save and readback never execute fixture");check(route_u::requestStart("/bom-portability.txt")==route_u::Reply::Accepted,"explicit RouteB launch consumes same byte-verified stored file");trialDone();check(route_u::status().reason==route_u::Reason::Completed,"stored BOM launch completes");oneA();
}else if(id=="Z26"){
 auto save=req();save.headers.clear();save.body["name"]={"bom-portability.txt"};save.body["content"]={String(Bom+"STRING a\n")};handleSaveScript(&save);check(save.code==401&&operations().empty(),"BOM storage path remains authenticated and nonexecuting");auto get=req();get.headers.clear();get.query["s"]={"bom-portability.txt"};handleGetScript(&get);check(get.code==401,"readback remains authenticated");
}else if(id=="Z27"){
 ChunkSource q;q.data=Bom+"STRING_HTML a\n";q.limit=1;q.interleave=true;native_b::Adapter a;check(sourceReady(a,q),"BOM capture ready");auto reads=q.reads;q.data.assign(q.data.size(),'x');sourceRun(a);check(q.reads==reads,"no mutable source callback after captured preflight");oneA();
}else if(id=="Z28"){
 ChunkSource bad;bad.data="\xef\xbb";bad.limit=1;native_b::Adapter a;check(!sourceReady(a,bad),"partial BOM fails");ChunkSource good;good.data="STRING a\n";good.limit=1;check(sourceReady(a,good),"new prepare resets failed BOM prefix state");sourceRun(a);oneA();
}else if(id=="Z29"){
 check(textEvents("DEFINE #T a\nSTRINGLN_POWERSHELL\n#T\nEND_STRINGLN\nSTRINGLN_POWERSHELL #T\n")=="a\na\n","block and inline DEFINE modes remain separate with same expansion");
}else if(id=="Z30"){
 for(size_t n=1;n<3;++n){lower::reset();badChunks(Bom.substr(0,n)+"STRING a\n",1,true);}
}else if(id=="Z31"){
 completed((Bom+"EXTENSION Text\nVERSION 1\nFUNCTION content()\nSTRINGLN_JAVASCRIPT a\nRETURN 1\nEND_FUNCTION\nEND_EXTENSION\nVAR $v=content()\n").c_str());check(operations().size()==4,"BOM inline aliases compose with extension/function evaluation");exactReport(0,0,{4});exactReport(2,0,{40});
}else if(id=="Z32"){
 const std::string base="STRINGLN_PYTHON a\n";lower::reset();goodChunks(base,1,true);check(operations().size()==4,"no-BOM streamed ordinary admission remains working");lower::reset();completed("STRING_HTML a\n");oneA();noReplay();
}else check(false,"unknown source/text case");std::cout<<"PASS "<<id<<" ("<<assertions<<" assertions)\n";return 0;
}catch(const std::exception& e){std::cerr<<"FAIL "<<argv[1]<<": "<<e.what()<<" ("<<assertions<<")\n";return 1;}}
