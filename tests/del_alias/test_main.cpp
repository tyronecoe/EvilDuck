// The production composed compiler, scheduler, adapter and backend use RAM-only
// source, transport, NVS and clocks from the preserved parent native harness.
#include "previous_repeat_parent_cases.inc"

static void delTaps(unsigned count,uint8_t modifiers=0){
 check(operations().size()==2*count,"exact DEL transient report count");
 for(unsigned i=0;i<count;++i){exactReport(i*2,modifiers,{0x4c});exactReport(i*2+1,0,{});}
}
static void delReject(const std::string& source,unsigned line,ds_preview::ErrorCode code){
 ds_preview::Program p;check(!p.compile(source.c_str(),source.size()),"malformed retained DEL source rejects");
 check(p.error().line==line&&p.error().code==code,"matching physical DEL diagnostic");
 lower::reset();rejected(source.c_str());check(operations().empty(),"invalid DEL source never submits reports");
}
static void delCancelled(){
 trialDone();check(route_u::status().reason==route_u::Reason::Cancelled&&!route_u::owned()&&!hid_backend::hasPersistent(),"STOP clears and detaches DEL execution");
 check(lower::count&&zero(lower::calls[lower::count-1]),"STOP cleanup neutral");noReplay();
}

int main(int argc,char** argv){
 if(argc!=2)return 2;
 if(std::strncmp(argv[1],"DA",2))return previous_repeat_parent_main(argc,argv);
 try{
  nvsMock::reset();mscMock::reset();mock::reset();setup();
  check(startupControlledReady&&route_u::bindOwner(),"actual composed startup and owner bind");
  lower::reset();led_mock::nowUs=0;rng_mock::reset();auto request=req();std::string id=argv[1];
  if(id=="DA01"){
   completed("DEL\n");delTaps(1);auto del=operations();
   check(del[1].at-del[0].at>=5,"ordinary DEL key-down dwell preserved");
   lower::reset();completed("DELETE\n");delTaps(1);auto canonical=operations();
   for(unsigned i=0;i<2;++i)check(!memcmp(del[i].bytes,canonical[i].bytes,8)&&del[i].id==canonical[i].id&&del[i].instance==canonical[i].instance,"DEL and DELETE exact report parity");
  }else if(id=="DA02"){
   const char* names[]={"CTRL","CONTROL","SHIFT","ALT","OPTION","GUI","WINDOWS","COMMAND","RCTRL","RSHIFT","RALT","RGUI"};
   const uint8_t masks[]={1,1,2,4,4,8,8,8,16,32,64,128};
   for(unsigned i=0;i<12;++i){lower::reset();std::string source=std::string(names[i])+" DEL\n";completed(source.c_str());delTaps(1,masks[i]);}
  }else if(id=="DA03"){
   for(const char* source:{"CTRL SHIFT DEL\n","CTRL-SHIFT-DEL\n"}){lower::reset();completed(source);delTaps(1,3);}
   lower::reset();completed("RCTRL-RSHIFT-DEL\n");delTaps(1,48);
  }else if(id=="DA04"){
   completed("HOLD DEL\nRELEASE DELETE\nHOLD DELETE\nRELEASE DEL\n");
   check(operations().size()==4,"ownership aliases refer to same held usage");
   exactReport(0,0,{0x4c});exactReport(1,0,{});exactReport(2,0,{0x4c});exactReport(3,0,{});
  }else if(id=="DA05"){
   completed("HOLD RSHIFT\nDEL\nRELEASE RSHIFT\n");check(operations().size()==4,"right held modifier surrounds one DEL tap");
   exactReport(0,32,{});exactReport(1,32,{0x4c});exactReport(2,32,{});exactReport(3,0,{});
  }else if(id=="DA06"){
   completed("HOLD a\nDEL\nRELEASE a\n");check(operations().size()==4,"held ordinary key preserved across DEL");
   exactReport(0,0,{4});exactReport(1,0,{4,0x4c});exactReport(2,0,{4});exactReport(3,0,{});
  }else if(id=="DA07"){
   runSource("HOLD DELETE\nDEL\nSTRING BAD\n");
   check(route_u::status().reason!=route_u::Reason::Completed&&operations().size()==1&&!hid_backend::hasPersistent(),"same-usage alias collision refuses without dropping held key into a transient");
   check(zero(lower::calls[lower::count-1]),"collision error performs neutral cleanup");noReplay();
  }else if(id=="DA08"){
   runSource("HOLD a\nHOLD b\nHOLD c\nHOLD d\nHOLD e\nHOLD f\nDEL\nSTRING BAD\n");
   check(route_u::status().reason!=route_u::Reason::Completed&&operations().size()==6&&!hid_backend::hasPersistent(),"DEL obeys six-key rollover refusal and suffix suppression");
   exactReport(5,0,{4,5,6,7,8,9});check(zero(lower::calls[lower::count-1]),"rollover error clears persistent state");noReplay();
  }else if(id=="DA09"){
   completed("REPEAT 3 DEL\n");delTaps(3);lower::reset();completed("DEL\nREPEAT 2\n");delTaps(3);
  }else if(id=="DA10"){
   completed("DEFINE #K DEL\nCTRL #K\nHOLD #K\nRELEASE #K\n");check(operations().size()==4,"existing supported DEFINE operand positions accept alias");
   exactReport(0,1,{0x4c});exactReport(1,0,{});exactReport(2,0,{0x4c});exactReport(3,0,{});
   delReject("DEFINE #CMD DEL\n#CMD\n",2,ds_preview::ErrorCode::UnknownStatement);
  }else if(id=="DA11"){
   check(textEvents("STRING DEL\nSTRINGLN DELETE\nSTRING\nDEL\nEND_STRING\nSTRINGLN\nDEL\nEND_STRINGLN\n")=="DELDELETE\nDELDEL\n","ordinary STRING and block content remain literal");
   for(const char* suffix:textSuffixes){std::string source=std::string("STRING_")+suffix+" DEL END_STRING\nSTRINGLN_"+suffix+" DEL END_STRINGLN\n";check(textEvents(source.c_str())=="DELDEL\n","all fourteen terminated aliases keep DEL text literal");}
  }else if(id=="DA12"){
   completed("FUNCTION DEL()\nSTRING a\nRETURN 3\nEND_FUNCTION\nVAR $DEL=DEL()\nIF $DEL==3 THEN\nDEL\nEND_IF\n");
   check(operations().size()==4,"DEL function value, variable and bare key coexist");exactReport(0,0,{4});exactReport(2,0,{0x4c});
  }else if(id=="DA13"){
   NumericHarness h;h.refuse=3;ds_preview::Program p;ds_preview::Runtime rt;
   execute("VAR $counter=0\nFUNCTION DEL()\n$counter=$counter+1\nRETURN $counter\nEND_FUNCTION\nVAR $DEL=DEL()+DEL()\nDEL\nIF $DEL==3 THEN\nSTRING ok\nEND_IF\n",p,rt,h);
   check(rt.state()==ds_preview::State::Completed&&variable(rt,"$counter")==2&&variable(rt,"$DEL")==3,"unambiguous numeric DEL calls evaluated once despite sink retry");
   check(h.events.size()==3&&h.events[0].type==ds_preview::EventType::KeyTap&&h.events[0].value==0x4c&&h.attempts==6,"DEL event retains value through retries");
  }else if(id=="DA14"){
   for(const char* source:{"del\n","Del\n","DEL extra\n","DEL1\n","DEL-\n"})delReject(source,1,ds_preview::ErrorCode::UnknownStatement);
   delReject("CTRL DEL extra\n",1,ds_preview::ErrorCode::Syntax);delReject("HOLD DEL extra\n",1,ds_preview::ErrorCode::Unsupported);
  }else if(id=="DA15"){
   delReject("STRING SHOULD_NOT_APPEAR\nIF FALSE THEN\nDEL extra\nEND_IF\n",3,ds_preview::ErrorCode::UnknownStatement);
   delReject("STRING SHOULD_NOT_APPEAR\nFUNCTION unused()\nDEL extra\nEND_FUNCTION\n",3,ds_preview::ErrorCode::UnknownStatement);
   lower::reset();completed("IF_DEFINED_TRUE #ABSENT\nDEL extra\nEND_IF_DEFINED\nDEL\n");delTaps(1);
  }else if(id=="DA16"){
   completed("VAR $n=0\nFUNCTION take()\nDEL\nRETURN 1\nEND_FUNCTION\nWHILE $n<3\n$n=$n+take()\nEND_WHILE\n");delTaps(3);
  }else if(id=="DA17"){
   put("/x.txt","DEL\n");start();awaitPhase("Press");mock::usbReady=false;auto before=lower::count;
   for(unsigned i=0;i<75;++i)trialTick();check(lower::count==before,"backpressure submits no DEL report");
   mock::usbReady=true;trialDone();check(route_u::status().reason==route_u::Reason::Completed,"pending DEL completes after transport resumes");delTaps(1);noReplay();
  }else if(id=="DA18"){
   put("/x.txt","HOLD RSHIFT\nDEL\nSTRING BAD\n");start();reports(1);awaitPhase("Press");mock::usbReady=false;
   handleStop(&request);for(unsigned i=0;i<20;++i)trialTick();check(route_u::owned()&&operations().size()==1,"STOP retains cleanup lease and suppresses unaccepted DEL");
   mock::usbReady=true;delCancelled();check(operations().size()==1,"STOP emitted no pending key or suffix");
  }else if(id=="DA19"){
   put("/x.txt","HOLD RSHIFT\nDEL\nSTRING BAD\n");start();reports(2);mock::usbReady=false;
   handleStop(&request);for(unsigned i=0;i<20;++i)trialTick();check(route_u::owned()&&operations().size()==2,"accepted DEL press waits only for priority cleanup");
   mock::usbReady=true;delCancelled();check(operations().size()==2,"no ordinary restoration or suffix overtakes STOP cleanup");
  }else if(id=="DA20"){
   put("/x.txt","DEL\nSTRING BAD\n");start();awaitPhase("Press");mock::usbMounted=false;tud_umount_cb();trialDone();
   check(operations().empty()&&route_u::status().phase==route_u::Phase::Quarantined,"disconnect before DEL submission quarantines without replay");mock::usbMounted=true;tud_mount_cb();noReplay();
  }else if(id=="DA21"){
   put("/x.txt","DEL\nSTRING BAD\n");start();awaitPhase("Press");lower::next=lower::Outcome::FalseAfterPossibleAcceptance;trialTick();trialDone();
   check(route_u::status().phase==route_u::Phase::Quarantined,"ambiguous DEL acceptance quarantines");noReplay();
  }else if(id=="DA22"){
   put("/x.txt","HOLD RSHIFT\nDEL\nRESTART_PAYLOAD\n");start();reports(6);auto op=operations();
   check(route_u::owned()&&op[0].session==op[3].session,"restart preserves original request lease");
   exactReport(0,32,{});exactReport(1,32,{0x4c});exactReport(2,32,{});exactReport(3,32,{});exactReport(4,32,{0x4c});exactReport(5,32,{});
   check(!clears().empty(),"restart performed a held-state clear before rewind");restartStop();
  }else if(id=="DA23"){
   put("/x.txt","HOLD DEL\nDELAY 5000\n");start();reports(1);auto priorRequest=route_u::status().request;auto priorSession=operations()[0].session;
   route_u::stop();delCancelled();lower::reset();completed("DEL\n");delTaps(1);
   check(route_u::status().request!=priorRequest&&operations()[0].session!=priorSession,"new DEL run has fresh request, lease and neutral held state");
  }else if(id=="DA24"){
   for(const char* source:{"DEL\r\n","DEL","\xef\xbb\xbf" "DEL\n"}){lower::reset();completed(source);delTaps(1);}
   lower::reset();for(size_t n=1;n<=4;++n){goodChunks(Bom+"DEL\n",n,true);delTaps(n);}
  }else if(id=="DA25"){
   ds_preview::Program p;check(p.compile("DEL\nREPEAT 127\n",strlen("DEL\nREPEAT 127\n"))&&p.instructions()==128,"DEL shares unchanged IR bound");
   delReject("DEL\nREPEAT 128\n",2,ds_preview::ErrorCode::CodeLimit);
   lower::reset();std::string invalid="STRING SHOULD_NOT_APPEAR\n";invalid+=char(0x7f);invalid+='\n';rejected(invalid.c_str());check(lower::count==0,"DEL alias does not admit raw DEL control byte");
  }else if(id=="DA26"){
   const char* source="DEL\n";ds_preview::Program p;check(p.compile(source,strlen(source)),"DEL allocation fixture compiles");
   ds_preview::Runtime rt;unsigned events=0;check(rt.start(p,[](void* c,const ds_preview::Event&e){check(e.type==ds_preview::EventType::KeyTap&&e.value==0x4c,"only expected DEL event");++*static_cast<unsigned*>(c);return ds_preview::Accept::Accepted;},&events),"DEL allocation fixture starts");
   auto before=native_alloc::calls();for(unsigned i=0;i<100&&rt.state()==ds_preview::State::Running;++i)rt.tick(i);
   check(rt.state()==ds_preview::State::Completed&&events==1&&native_alloc::calls()==before,"DEL adds no runtime C++ allocation");
   check(ds_preview::CompileSession::compilerBytes()<=4096,"existing compiler workspace bound preserved");
  }else if(id=="DA27"){
   for(const char* name:{"DELETE","ENTER","CTRL","RSHIFT","F1","F24","STRING","REPEAT","RESET"}){
    std::string source=std::string("FUNCTION ")+name+"()\nRETURN 1\nEND_FUNCTION\n";
    delReject(source,1,ds_preview::ErrorCode::Identifier);
   }
   check(textEvents("FUNCTION DEL()\nSTRING a\nEND_FUNCTION\nDEL()\n")=="a","DEL exception preserves existing void function calls");
  }else check(false,"unknown DEL alias case");
  std::cout<<"PASS "<<id<<" ("<<assertions<<" assertions)\n";return 0;
 }catch(const std::exception& error){std::cerr<<"FAIL "<<argv[1]<<": "<<error.what()<<" ("<<assertions<<")\n";return 1;}
}
