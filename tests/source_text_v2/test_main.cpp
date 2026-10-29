#include "source_text_parent_cases.inc"
int main(int argc,char** argv){if(argc!=2)return 2;if(strncmp(argv[1],"AA",2))return source_text_main(argc,argv);
try{mscMock::reset();mock::reset();setup();check(startupControlledReady&&route_u::bindOwner(),"actual composed startup");lower::reset();led_mock::nowUs=0;rng_mock::reset();auto r=req();std::string id=argv[1];
if(id=="AA01"){
 for(const char* suffix:textSuffixes)for(bool ln:{false,true}){lower::reset();std::string s=std::string(ln?"STRINGLN_":"STRING_")+suffix+" a "+(ln?"END_STRINGLN":"END_STRING")+"\n";completed(s.c_str());check(operations().size()==(ln?4u:2u),"all14 aliases remove syntax and emit exact text/Enter only");exactReport(0,0,{4});exactReport(1,0,{});if(ln){exactReport(2,0,{40});exactReport(3,0,{});}}
}else if(id=="AA02"){
 check(textEvents("STRING hello END_STRING\nSTRINGLN bye END_STRINGLN\n")=="hello END_STRINGbye END_STRINGLN\n","ordinary commands retain literal closers");
}else if(id=="AA03"){
 check(textEvents("STRING_PYTHON a END_STRING\nSTRINGLN_HTML b END_STRINGLN\n")=="ab\n","single final matching closer has precedence over extension text");
}else if(id=="AA04"){
 check(textEvents("STRING_PYTHON a END_STRINGx END_STRING\nSTRINGLN_HTML b END_STRINGLNx END_STRINGLN\n")=="a END_STRINGxb END_STRINGLNx\n","whole-token match never strips a prefix lookalike");
}else if(id=="AA05"){
 check(textEvents("STRING_PYTHON a END_STRINGx\nSTRINGLN_HTML b END_STRINGLNx\n")=="a END_STRINGxb END_STRINGLNx\n","nonterminated extension and lookalikes retained");
}else if(id=="AA06"){
 check(textEvents("  STRING_PYTHON   a   END_STRING \t\n\tSTRINGLN_HTML b END_STRINGLN\t\n")=="  ab\n","existing leading/trailing horizontal whitespace normalization declared policy");
}else if(id=="AA07"){
 for(const char* s:{"STRING_PYTHON a END_STRINGLN\n","STRINGLN_PYTHON a END_STRING\n","STRING_PYTHON END_STRING\n","STRINGLN_HTML  END_STRINGLN\n","STRING_PYTHON a\tEND_STRING\n"}){lower::reset();rejected(s);check(lower::count==0,"mismatched/empty/tab-only syntax rejects before all output");}
}else if(id=="AA08"){
 for(const char* s:{"STRING_PYTHON a END_STRING b END_STRING\n","STRINGLN_PYTHON a END_STRINGLN END_STRINGLN\n","STRING_PYTHON a END_STRING x\n","STRING_PYTHON a END_STRINGLN x\n"}){lower::reset();rejected(s);}
}else if(id=="AA09"){
 check(textEvents("DEFINE #V a\nSTRING_PYTHON #V END_STRING\nSTRINGLN_HTML #V END_STRINGLN\n")=="aa\n","delimiter removed before normal DEFINE expansion");
}else if(id=="AA10"){
 check(textEvents("DEFINE #END END_STRING\nSTRING_PYTHON a #END\nSTRING_PYTHON #END END_STRING\n")=="a END_STRINGEND_STRING","DEFINE cannot fabricate raw grammar or reparse expanded text");
}else if(id=="AA11"){
 for(const char* suffix:textSuffixes){lower::reset();completed((std::string("REPEAT 2 STRING_")+suffix+" a END_STRING\n").c_str());sourceLettersA(2);lower::reset();completed((std::string("REPEAT 2 STRINGLN_")+suffix+" a END_STRINGLN\n").c_str());check(operations().size()==8,"repeated terminated newline aliases preserve count/order");exactReport(2,0,{40});exactReport(6,0,{40});}
}else if(id=="AA12"){
 for(const char* s:{"REPEAT 2 STRING_PYTHON a END_STRINGLN\n","REPEAT 2 STRING_HTML a END_STRING b END_STRING\n","STRING a\nIF FALSE THEN\nSTRING_PYTHON a END_STRINGLN\nEND_IF\n","FUNCTION unused()\nSTRING_PYTHON a END_STRING b\nEND_FUNCTION\nSTRING a\n"}){lower::reset();rejected(s);check(lower::count==0,"all retained malformed forms preflight before output");}
}else if(id=="AA13"){
 completed("IF_DEFINED_TRUE #ABSENT\nSTRING_PYTHON a END_STRINGLN\nEND_IF_DEFINED\nSTRING_HTML a END_STRING\n");oneA();
}else if(id=="AA14"){
 check(textEvents("STRINGLN_HTML\nSTRING_PYTHON a END_STRING\nEND_STRINGLN\n")=="STRING_PYTHON a END_STRING\n","inline syntax in an existing block remains literal");
}else if(id=="AA15"){
 for(size_t n=1;n<=4;++n){lower::reset();goodChunks(Bom+"STRING_PYTHON a END_STRING\r\n",n,true);oneA();}lower::reset();goodChunks(Bom+"STRING_PYTHON a END_STRING",1,true);oneA();
}else if(id=="AA16"){
 completed("HOLD SHIFT\nSTRING_PYTHON a END_STRING\nRELEASE SHIFT\nSTRING_HTML b END_STRING\n");check(operations().size()==6,"held restoration applies to terminated aliases");exactReport(0,2,{});exactReport(1,2,{4});exactReport(2,2,{});exactReport(3,0,{});exactReport(4,0,{5});exactReport(5,0,{});
}else if(id=="AA17"){
 put("/x.txt","STRING_PYTHON a END_STRING\n");start();awaitPhase("Press");mock::usbReady=false;auto n=lower::count;for(unsigned i=0;i<30;++i)trialTick();check(lower::count==n,"terminated text retries submit nothing when not ready");mock::usbReady=true;trialDone();oneA();noReplay();
}else if(id=="AA18"){
 put("/x.txt","HOLD SHIFT\nDELAY 5000\nSTRING_PYTHON BAD END_STRING\n");start();reports(1);handleStop(&r);trialDone();check(route_u::status().reason==route_u::Reason::Cancelled&&operations().size()==1&&!hid_backend::hasPersistent(),"STOP clears state and suppresses terminated text");noReplay();
}else if(id=="AA19"){
 put("/x.txt",(Bom+"STRING_PYTHON a END_STRING\nHOLD SHIFT\nDELAY 20\nRESTART_PAYLOAD\n").c_str());start();reports(5);exactReport(0,0,{4});exactReport(3,0,{4});restartStop();
}else if(id=="AA20"){
 const char* s="REM first\nSTRINGLN_HTML a END_STRING\n";rejected(s);ds_preview::Program p;check(!p.compile(s,strlen(s))&&p.error().line==2&&p.error().code==ds_preview::ErrorCode::Structure,"malformed delimiter source line preserved");
}else if(id=="AA21"){
 put("/x.txt","STRING_PYTHON a END_STRING\n");start();awaitPhase("Press");lower::next=lower::Outcome::FalseAfterPossibleAcceptance;trialTick();trialDone();check(route_u::status().phase==route_u::Phase::Quarantined,"ambiguous submit remains quarantined");noReplay();
}else if(id=="AA22"){
 completed("STRING_PYTHON a END_STRING\n");oneA();lower::reset();completed("STRINGLN_HTML a\n");check(operations().size()==4,"independent run preserves extension state isolation");noReplay();
}else check(false,"unknown v2 case");std::cout<<"PASS "<<id<<" ("<<assertions<<" assertions)\n";return 0;
}catch(const std::exception& e){std::cerr<<"FAIL "<<argv[1]<<": "<<e.what()<<" ("<<assertions<<")\n";return 1;}}
