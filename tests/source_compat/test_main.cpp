#include "lock_parent_cases.inc"
static void onlyA(){check(operations().size()==2,"only chosen a press/release");exactReport(0,0,{4});exactReport(1,0,{});}
static std::string nest(unsigned n){std::string s;for(unsigned i=0;i<n;++i)s+="IF_NOT_DEFINED_TRUE #MISSING\n";s+="STRING a\n";for(unsigned i=0;i<n;++i)s+="END_IF_DEFINED\n";return s;}
struct SourceProbe{
 ds_preview::MemoryReader memory{};unsigned seeks=0,reads=0,retries=0;bool badSeek=false,badRead=false,change=false;
 static ds_preview::ReadResult read(void* c,char* p,size_t n){auto& s=*static_cast<SourceProbe*>(c);++s.reads;if(s.retries){--s.retries;return {ds_preview::ReadStatus::Retry,0};}if(s.badRead)return {ds_preview::ReadStatus::Error,0};return ds_preview::MemoryReader::read(&s.memory,p,n);}
 static bool seek(void* c,size_t n){auto& s=*static_cast<SourceProbe*>(c);++s.seeks;if(s.badSeek&&s.seeks==2)return false;if(s.change&&s.seeks==2)const_cast<char*>(s.memory.source)[4]='x';return ds_preview::MemoryReader::seek(&s.memory,n);}
 ds_preview::Reader reader(){return {read,seek,this,memory.bytes};}
};
static ds_preview::CompileState compileProbe(ds_preview::Program& p,SourceProbe& probe){
 ds_preview::CompileSession c;check(c.start(p,probe.reader()),"start cooperative source compiler");
 for(unsigned i=0;i<20000&&c.state()==ds_preview::CompileState::Compiling;++i){c.step();auto w=c.work();check(w.callbacks<=1&&w.bytes<=32&&w.lines<=1&&w.nodes<=1&&w.expressions<=1,"compile per-step work remains bounded");}
 return c.state();
}
int main(int argc,char**argv){
 if(argc!=2)return 2;if(argv[1][0]!='P')return lock_feedback_main(argc,argv);
 try{
 mscMock::reset();mock::reset();setup();check(startupControlledReady&&route_u::bindOwner(),"actual controlled startup ready");lower::reset();led_mock::nowUs=0;auto r=req();std::string id=argv[1];
 if(id=="P01"){completed("DEFINE #Y TRUE\nIF_DEFINED_TRUE #Y\nSTRING a\nELSE_DEFINED\nSTRING BAD\nEND_IF_DEFINED\n");onlyA();}
 else if(id=="P02"){completed("DEFINE #N FALSE\nIF_DEFINED_TRUE #N\nSTRING BAD\nELSE_DEFINED\nSTRING a\nEND_IF_DEFINED\n");onlyA();}
 else if(id=="P03"){completed("IF_NOT_DEFINED_TRUE #ABSENT\nSTRING a\nELSE_DEFINED\nSTRING BAD\nEND_IF_DEFINED\n");onlyA();}
 else if(id=="P04"){completed("IF_DEFINED_TRUE #LATE\nSTRING BAD\nELSE_DEFINED\nSTRING a\nEND_IF_DEFINED\nDEFINE #LATE TRUE\n");onlyA();}
 else if(id=="P05"){completed("IF_DEFINED_TRUE #MISSING\nDEFINE #X TRUE\nVAR $hidden=1\nFUNCTION hidden()\nRETURN 1\nEND_FUNCTION\nEND_IF_DEFINED\nIF_NOT_DEFINED_TRUE #X\nSTRING a\nEND_IF_DEFINED\n");onlyA();}
 else if(id=="P06"){completed("IF_DEFINED_TRUE #NO\nUNSUPPORTED_SECRET_COMMAND\nVAR $_CAPSLOCK_ON = 1\nmalformed runtime (\nWHILE\nEND_IF_DEFINED\nSTRING a\n");onlyA();}
 else if(id=="P07"){rejected("STRING a\nIF_NOT_DEFINED_TRUE #NO\nUNKNOWN\nEND_IF_DEFINED\n");}
 else if(id=="P08"){completed(nest(8).c_str());onlyA();}
 else if(id=="P09"){rejected(nest(9).c_str());}
 else if(id=="P10"){for(const char* s:{"IF_DEFINED_TRUE #Y\n","ELSE_DEFINED\n","END_IF_DEFINED\n","IF_DEFINED_TRUE #Y THEN\nEND_IF_DEFINED\n","IF_DEFINED_TRUE Y\nEND_IF_DEFINED\n","IF_NOT_DEFINED_TRUE #Y\nELSE_DEFINED\nELSE_DEFINED\nEND_IF_DEFINED\n","IF_DEFINED_TRUE #Y\nELSE_DEFINED junk\nEND_IF_DEFINED\n","IF_DEFINED_TRUE #Y\nEND_IF_DEFINED junk\n"}){lower::reset();rejected(s);}}
 else if(id=="P11"){rejected("DEFINE #X 1\nIF_DEFINED_TRUE #X\nSTRING a\nEND_IF_DEFINED\n");lower::reset();completed("DEFINE #X 1\nIF_DEFINED_TRUE #NO\nIF_DEFINED_TRUE #X\nUNKNOWN\nEND_IF_DEFINED\nEND_IF_DEFINED\nSTRING a\n");onlyA();}
 else if(id=="P12"){const char* s="STRING\nIF_DEFINED_TRUE #NO\nEXTENSION literal\nEND_STRING\nREM_BLOCK\nEND_IF_DEFINED\nEXTENSION ignored\nEND_REM\n";completed(s);check(operations().size()==2*(strlen("IF_DEFINED_TRUE #NO")+strlen("EXTENSION literal")),"directives in literal/comment are never preprocessing");}
 else if(id=="P13"){completed("IF_DEFINED_TRUE #NO\nSTRING\nELSE_DEFINED\nEND_STRING\nEND_IF_DEFINED\nSTRING a\n");onlyA();lower::reset();rejected("IF_DEFINED_TRUE #NO\nSTRING\nEND_IF_DEFINED\n");}
 else if(id=="P14"){const char* bom="\xef\xbb\xbf" "DEFINE #Y TRUE\r\nIF_DEFINED_TRUE #Y\r\nSTRING a\r\nEND_IF_DEFINED";rejected(bom);check(route_u::status().reason==route_u::Reason::Capability,"existing composed ASCII admission rejects BOM before compiler");ds_preview::Program p;check(p.compile(bom,strlen(bom)),"compiler component independently accepts BOM/CRLF/no final newline");lower::reset();completed("DEFINE #Y TRUE\r\nIF_DEFINED_TRUE #Y\r\nSTRING a\r\nEND_IF_DEFINED");onlyA();}
 else if(id=="P15"){rejected("REM physical 1\nIF_DEFINED_TRUE #NO\nBAD\nEND_IF_DEFINED\nWAIT_FOR_CAPS_ON bad\n");check(route_u::status().line==5,"physical line survives exclusion");}
 else if(id=="P16"){std::string s(ds_preview::MaxSource+1,'\n');rejected(s.c_str());}
 else if(id=="P17"){completed("EXTENSION Sample\nVERSION 1.0.2\nDEFINE #Y TRUE\nFUNCTION pick()\nRETURN 1\nEND_FUNCTION\nEND_EXTENSION\nIF_DEFINED_TRUE #Y\nIF pick() == 1 THEN\nSTRING a\nEND_IF\nEND_IF_DEFINED\n");onlyA();}
 else if(id=="P18"){completed("EXTENSION Plain\nREM metadata optional\nSTRING a\nEND_EXTENSION\n");onlyA();}
 else if(id=="P19"){for(const char* s:{"EXTENSION A\nEND_EXTENSION\nEXTENSION A\nEND_EXTENSION\n","EXTENSION A\nEXTENSION B\nEND_EXTENSION\nEND_EXTENSION\n","VERSION 1.0\n","END_EXTENSION\n","EXTENSION\nEND_EXTENSION\n","EXTENSION A B\nEND_EXTENSION\n"}){lower::reset();rejected(s);}}
 else if(id=="P20"){for(const char* s:{"EXTENSION A\nVERSION 1.0\nVERSION 1.1\nEND_EXTENSION\n","EXTENSION A\nSTRING a\nVERSION 1.0\nEND_EXTENSION\n","EXTENSION A\nVERSION .1\nEND_EXTENSION\n","EXTENSION A\nVERSION 1.\nEND_EXTENSION\n","EXTENSION A\nVERSION 1.a\nEND_EXTENSION\n"}){lower::reset();rejected(s);}std::string s="EXTENSION A\nVERSION "+std::string(64,'1')+"\nEND_EXTENSION\n";lower::reset();rejected(s.c_str());}
 else if(id=="P21"){std::string s;for(unsigned i=0;i<16;++i)s+="EXTENSION E"+std::to_string(i)+"\nVERSION 1\nEND_EXTENSION\n";s+="STRING a\n";completed(s.c_str());onlyA();lower::reset();s+="EXTENSION E16\nEND_EXTENSION\n";rejected(s.c_str());}
 else if(id=="P22"){std::string s="EXTENSION "+std::string(23,'E')+"\nSTRING a\nEND_EXTENSION\n";completed(s.c_str());onlyA();lower::reset();s="EXTENSION "+std::string(24,'E')+"\nEND_EXTENSION\n";rejected(s.c_str());}
 else if(id=="P23"){for(const char* s:{"IF TRUE THEN\nEXTENSION A\nEND_EXTENSION\nEND_IF\n","EXTENSION A\nIF TRUE THEN\nEND_EXTENSION\nEND_IF\n","FUNCTION f()\nEXTENSION A\nEND_EXTENSION\nEND_FUNCTION\n"}){lower::reset();rejected(s);}}
 else if(id=="P24"){rejected("IF_NOT_DEFINED_TRUE #X\nEXTENSION A\nEND_IF_DEFINED\nEND_EXTENSION\n");}
 else if(id=="P25"){completed("IF_DEFINED_TRUE #X\nEXTENSION A\nVERSION 1\nUNSUPPORTED\nEND_EXTENSION\nEND_IF_DEFINED\nEXTENSION A\nSTRING a\nEND_EXTENSION\n");onlyA();}
 else if(id=="P26"){rejected("DEFINE #WRAP EXTENSION A\n#WRAP\nEND_EXTENSION\n");}
 else if(id=="P27"){std::string s="IF_NOT_DEFINED_TRUE #X\n";for(int i=0;i<600;++i)s+="REM pad\n";s+="STRING BAD\nEND_IF_DEFINED\n";put("/x.txt",s);start();handleStop(&r);trialDone();check(r.code==202&&!route_u::owned()&&operations().empty(),"STOP during preparation prevents later output");noReplay();}
 else if(id=="P28"){lockReport(2);completed("DEFINE #Y TRUE\nEXTENSION Controls\nVERSION 1\nFUNCTION work()\nVAR $n=2\nWHILE $n > 0\nIF_DEFINED_TRUE #Y\nWAIT_FOR_CAPS_ON\nEND_IF_DEFINED\n$n=$n-1\nEND_WHILE\nRETURN 1\nEND_FUNCTION\nEND_EXTENSION\nIF work() == 1 THEN\nHOLD SHIFT\nSTRING a\nRELEASE SHIFT\nINJECT_MOD CONTROL\nEND_IF\n");check(operations().size()==6,"existing wait/function/hold/release/inline-mod compose");exactReport(0,2,{});exactReport(1,2,{4});exactReport(3,0,{});exactReport(4,1,{});exactReport(5,0,{});}
 else if(id=="P29"){put("/x.txt","EXTENSION A\nHOLD SHIFT\nDELAY 5000\nSTRING BAD\nEND_EXTENSION\n");start();reports(1);handleStop(&r);trialDone();check(route_u::status().reason==route_u::Reason::Cancelled&&!hid_backend::hasPersistent()&&operations().size()==1,"STOP in included extension clears ownership and forbids later text");noReplay();}
 else if(id=="P30"){std::string s="IF_DEFINED_TRUE #X\nBAD\nEND_IF_DEFINED\nSTRING a\n";for(int failure=0;failure<3;++failure){SourceProbe q;q.memory={s.c_str(),s.size(),0};q.badRead=failure==0;q.badSeek=failure==1;q.change=failure==2;ds_preview::Program p;check(compileProbe(p,q)==ds_preview::CompileState::Error&&!p.ready(),"source read/seek/mutation fail before publication");check(p.error().code==(failure==1?ds_preview::ErrorCode::SeekError:ds_preview::ErrorCode::ReadError),"precise source failure code");}}
 else if(id=="P31"){const char* s="DEFINE #Y TRUE\nIF_DEFINED_TRUE #Y\nSTRING a\nEND_IF_DEFINED\n";SourceProbe q;q.memory={s,strlen(s),0};q.retries=3;ds_preview::Program p;check(compileProbe(p,q)==ds_preview::CompileState::Complete&&p.ready()&&q.seeks==2,"reader retry remains cooperative and hash-bound two passes");}
 else if(id=="P32"){const char* s="EXTENSION A\nVERSION 1\nIF_NOT_DEFINED_TRUE #X\nVAR $x=1\nEND_IF_DEFINED\nEND_EXTENSION\n";ds_preview::Program p;auto before=native_alloc::calls();bool ok=p.compile(s,strlen(s));auto after=native_alloc::calls();check(ok&&after==before,"new compiler profile does not allocate C++ heap");check(ds_preview::CompileSession::compilerBytes()<=4096,"fixed compiler workspace cap");std::cout<<"SIZES Program="<<sizeof(ds_preview::Program)<<" CompileSession="<<sizeof(ds_preview::CompileSession)<<" Compiler="<<ds_preview::CompileSession::compilerBytes()<<"\n";}
 else if(id=="P33"){const char* s="IF_NOT_DEFINED_TRUE #X\nSTRING a\nEND_IF_DEFINED\n";SourceProbe q;q.memory={s,strlen(s),0};ds_preview::Program p;ds_preview::CompileSession c;check(c.start(p,q.reader()),"cancel compilation starts");c.step();c.cancel();check(c.state()==ds_preview::CompileState::Cancelled&&!p.ready(),"cancel keeps unpublished program invalid");}
 else if(id=="P34"){completed("IF_NOT_DEFINED_TRUE #X\nDEFINE #TEXT a\nEND_IF_DEFINED\nSTRING #TEXT\n");onlyA();lower::reset();rejected("DEFINE #X TRUE\nIF_DEFINED_TRUE #X\nDEFINE #X FALSE\nEND_IF_DEFINED\n");}
 else if(id=="P35"){std::string s="IF_DEFINED_TRUE #NO\n";for(unsigned i=0;i<100;++i)s+="VAR $x"+std::to_string(i)+"=1\n";s+="END_IF_DEFINED\nSTRING a\n";completed(s.c_str());onlyA();}
 else if(id=="P36"){for(const char* s:{"FUNCTION EXTENSION()\nEND_FUNCTION\n","FUNCTION IF_DEFINED_TRUE()\nEND_FUNCTION\n","FUNCTION VERSION()\nEND_FUNCTION\n","EXTENSION A\nVERSION 1\n"}){lower::reset();rejected(s);}}
 else if(id=="P37"){rejected("IF_DEFINED_TRUE #NO\nEND_REM\nEND_IF_DEFINED\n");check(route_u::status().line==2,"excluded unmatched comment close remains structural error");}
 else check(false,"unknown source compatibility case");
 std::cout<<"PASS "<<id<<" ("<<assertions<<" assertions)\n";return 0;
 }catch(const std::exception& e){std::cerr<<"FAIL "<<argv[1]<<": "<<e.what()<<" ("<<assertions<<")\n";return 1;}
}
