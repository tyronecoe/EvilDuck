// Actual composed compiler/runtime/adapter/scheduler/backend with RAM-only mocks.
// Historical parent bodies remain available but this driver executes only DL cases.
#include "del_alias_parent_cases.inc"

static std::string label(size_t bytes,bool hash=true,char fill='A'){
 return std::string(hash?"#":"")+std::string(bytes-(hash?1:0),fill);
}
static void defineReject(const std::string& source,unsigned line,ds_preview::ErrorCode code){
 ds_preview::Program p;check(!p.compile(source.c_str(),source.size()),"retained malformed DEFINE source rejects");
 check(p.error().line==line&&p.error().code==code,"exact physical DEFINE diagnostic");
 lower::reset();rejected(source.c_str());check(operations().empty(),"whole-source rejection precedes HID output");
}
static std::string defineText(const std::string& name,const char* value="a"){
 return "DEFINE "+name+" "+value+"\nSTRING "+name+"\n";
}
int main(int argc,char**argv){
 if(argc!=2)return 2;if(std::strncmp(argv[1],"DL",2))return del_alias_parent_main(argc,argv);
 try{
  nvsMock::reset();mscMock::reset();mock::reset();setup();
  check(startupControlledReady&&route_u::bindOwner(),"actual composed controlled startup and owner bind");
  lower::reset();led_mock::nowUs=0;rng_mock::reset();std::string id=argv[1];
  const std::string official="#WINDOWS_HOST_REQUEST_COUNT",maximum="#ABCDEFGHIJKLMNOPQRSTUVWXYZ1234",over="#ABCDEFGHIJKLMNOPQRSTUVWXYZ12345";
  check(official.size()==27&&maximum.size()==31&&over.size()==32,"fixture byte lengths include hash");
  if(id=="DL01"){
   for(bool hash:{false,true})for(size_t n:{size_t(1)+(hash?1:0),size_t(23),size_t(24)}){
    auto name=label(n,hash);check(textEvents(defineText(name).c_str())=="a","short and old-boundary labels substitute whole name");
   }
  }else if(id=="DL02"){
   NumericHarness h;ds_preview::Program p;ds_preview::Runtime rt;
   auto s="DEFINE "+official+" 2\nVAR $v="+official+"+3\nIF $v==5 THEN\nSTRING ok\nEND_IF\n";execute(s.c_str(),p,rt,h);
   check(rt.state()==ds_preview::State::Completed&&variable(rt,"$v")==5,"official27byte label expands as complete numeric operand");
   check(h.events.size()==2&&h.events[0].value=='o'&&h.events[1].value=='k',"numeric condition selects harmless output");
  }else if(id=="DL03"){
   check(textEvents(("DEFINE "+official+" DEFINE27OK\nSTRINGLN "+official+"\n").c_str())=="DEFINE27OK\n","owner27byte marker exact");
   check(textEvents(("DEFINE "+maximum+" DEFINE31OK\nSTRINGLN "+maximum+"\n").c_str())=="DEFINE31OK\n","owner31byte marker exact");
   check(textEvents(defineText(label(31,false),"bare31").c_str())=="bare31","optional bare31byte label retained");
  }else if(id=="DL04"){
   for(bool hash:{false,true})defineReject(defineText(label(32,hash)),1,ds_preview::ErrorCode::Identifier);
   defineReject("DEFINE "+over+" BAD\nSTRING SHOULD_NOT_APPEAR\n",1,ds_preview::ErrorCode::Identifier);
  }else if(id=="DL05"){
   auto a=label(30)+"A",b=label(30)+"B";check(a.size()==31&&b.size()==31&&a.substr(0,23)==b.substr(0,23),"distinct accepted names share old23byte prefix");
   check(textEvents(("DEFINE "+a+" left\nDEFINE "+b+" right\nSTRING "+a+":"+b+"\n").c_str())=="left:right","no prefix truncation or collision");
  }else if(id=="DL06"){
   defineReject("DEFINE "+maximum+" a\nDEFINE "+maximum+" b\nSTRING BAD\n",2,ds_preview::ErrorCode::DuplicateConstant);
  }else if(id=="DL07"){
   std::string s;std::vector<std::string> names;
   for(unsigned n=0;n<16;++n){auto k=label(30)+char('A'+n);names.push_back(k);s+="DEFINE "+k+" "+char('a'+n)+"\n";}
   auto full=s;for(const auto& k:names)full+="STRING "+k+"\n";
   check(textEvents(full.c_str())=="abcdefghijklmnop","all16long label cells remain independently addressable");
   defineReject(s+"DEFINE "+label(30)+"Q q\nSTRING BAD\n",17,ds_preview::ErrorCode::ConstantLimit);
  }else if(id=="DL08"){
   check(textEvents(("STRING "+maximum+"\nDEFINE "+maximum+" late\n").c_str())=="late","existing global collection before emission retained");
   defineReject("STRING SHOULD_NOT_APPEAR\nDEFINE "+maximum+" a\nDEFINE "+maximum+" b\n",3,ds_preview::ErrorCode::DuplicateConstant);
  }else if(id=="DL09"){
   auto k=label(31,false);auto s="DEFINE "+k+" x\nSTRING "+k+" "+k+"Z Z"+k+" "+k+"\n";
   check(textEvents(s.c_str())=="x "+k+"Z Z"+k+" x","bare label expansion retains literal-space token boundaries");
   check(textEvents(("DEFINE "+k+" x\nSTRING "+k+"\t"+k+"\n").c_str())==k+"\t"+k,"tab boundaries not newly normalized");
  }else if(id=="DL10"){
   auto shorter=label(27),longer=shorter+"BBBB";
   check(textEvents(("DEFINE "+shorter+" short\nDEFINE "+longer+" long\nSTRING "+longer+"_suffix "+shorter+"\n").c_str())=="long_suffix short","hash labels retain longest-match and prefix substitution policy");
  }else if(id=="DL11"){
   auto a=label(30)+"A",b=label(30)+"B";
   check(textEvents(("DEFINE "+a+" "+b+"\nDEFINE "+b+" x\nSTRING "+a+"\n").c_str())==b,"replacement values remain nonrecursive");
  }else if(id=="DL12"){
   auto s="DEFINE "+maximum+" TRUE\nIF_DEFINED_TRUE "+maximum+"\nSTRING a\nELSE_DEFINED\nSTRING BAD\nEND_IF_DEFINED\nIF_NOT_DEFINED_TRUE "+maximum+"\nSTRING BAD\nELSE_DEFINED\nSTRING b\nEND_IF_DEFINED\n";
   check(textEvents(s.c_str())=="ab","long Boolean label resolves in both conditional directive forms");
  }else if(id=="DL13"){
   auto s="IF_DEFINED_TRUE "+maximum+"\nBAD excluded\nELSE_DEFINED\nSTRING a\nEND_IF_DEFINED\nIF_NOT_DEFINED_TRUE "+maximum+"\nSTRING b\nEND_IF_DEFINED\n";
   check(textEvents(s.c_str())=="ab","undefinedlong label preserves falseflag semantics and exclusions");
  }else if(id=="DL14"){
   auto s="IF_DEFINED_TRUE "+maximum+"\nBAD excluded\nEND_IF_DEFINED\nDEFINE "+maximum+" TRUE\nIF_DEFINED_TRUE "+maximum+"\nSTRING a\nEND_IF_DEFINED\n";
   check(textEvents(s.c_str())=="a","preprocessor lookups remain sequential despite global emission collection");
  }else if(id=="DL15"){
   check(textEvents(("IF_DEFINED_TRUE #ABSENT\nDEFINE "+over+" BAD\nEND_IF_DEFINED\nSTRING a\n").c_str())=="a","preprocessor-excluded overlong DEFINE remains excluded");
   defineReject("STRING SHOULD_NOT_APPEAR\nIF FALSE THEN\nDEFINE "+over+" BAD\nEND_IF\n",3,ds_preview::ErrorCode::Identifier);
   defineReject("STRING SHOULD_NOT_APPEAR\nFUNCTION unused()\nDEFINE "+over+" BAD\nEND_FUNCTION\n",3,ds_preview::ErrorCode::Identifier);
  }else if(id=="DL16"){
   defineReject("IF_DEFINED_TRUE #ABSENT\nIF_DEFINED_TRUE "+over+"\nEND_IF_DEFINED\nEND_IF_DEFINED\n",2,ds_preview::ErrorCode::PreprocessorSyntax);
   defineReject("IF_NOT_DEFINED_TRUE "+over+"\nSTRING BAD\nEND_IF_DEFINED\n",1,ds_preview::ErrorCode::PreprocessorSyntax);
  }else if(id=="DL17"){
   auto good=std::string("$")+std::string(22,'v'),bad=good+"v";
   NumericHarness h;ds_preview::Program p;ds_preview::Runtime rt;execute(("VAR "+good+"=2\n").c_str(),p,rt,h);
   check(rt.state()==ds_preview::State::Completed&&variable(rt,good.c_str())==2,"existing23byte ordinary variable limit unchanged");
   defineReject("VAR "+bad+"=2\n",1,ds_preview::ErrorCode::Identifier);
  }else if(id=="DL18"){
   auto good=std::string(23,'f'),bad=good+"f";
   NumericHarness h;ds_preview::Program p;ds_preview::Runtime rt;execute(("FUNCTION "+good+"()\nRETURN 2\nEND_FUNCTION\nVAR $v="+good+"()\n").c_str(),p,rt,h);
   check(rt.state()==ds_preview::State::Completed&&variable(rt,"$v")==2,"existing23byte function limit unchanged");
   defineReject("FUNCTION "+bad+"()\nRETURN 2\nEND_FUNCTION\n",1,ds_preview::ErrorCode::Identifier);
  }else if(id=="DL19"){
   for(const auto& k:{std::string("#"),std::string("#2BAD"),std::string("#BAD-NAME"),std::string("2BAD"),std::string("#BAD.NAME")})defineReject("DEFINE "+k+" a\nSTRING BAD\n",1,ds_preview::ErrorCode::Identifier);
   check(textEvents(defineText("#_Long_Name_1234567890123456789").c_str())=="a","existing identifier grammar still admits underscores and noninitialdigits");
  }else if(id=="DL20"){
   check(textEvents(defineText(maximum,std::string(63,'x').c_str()).c_str())==std::string(63,'x'),"63byte value capacity unchanged");
   defineReject(defineText(maximum,std::string(64,'x').c_str()),1,ds_preview::ErrorCode::Identifier);
   auto s="DEFINE "+maximum+" "+std::string(63,'x')+"\nSTRING ";for(unsigned n=0;n<5;++n)s+=maximum;s+='\n';
   defineReject(s,2,ds_preview::ErrorCode::ConstantExpansion);
  }else if(id=="DL21"){
   auto s="DEFINE "+maximum+" TRUE\nIF_DEFINED_TRUE #ABSENT\nDEFINE "+maximum+" FALSE\nEND_IF_DEFINED\nIF_DEFINED_TRUE "+maximum+"\nSTRING a\nEND_IF_DEFINED\n";
   check(textEvents(s.c_str())=="a","excluded duplicate never changes selected longconstant");
  }else if(id=="DL22"){
   NumericHarness h;ds_preview::Program p;ds_preview::Runtime rt;auto s="FUNCTION value()\nDEFINE "+maximum+" 7\nRETURN "+maximum+"\nEND_FUNCTION\nVAR $v=value()\n";execute(s.c_str(),p,rt,h);
   check(rt.state()==ds_preview::State::Completed&&variable(rt,"$v")==7,"longconstants retain collection inside functions and RETURN expansion");
  }else if(id=="DL23"){
   auto s=defineText(official);completed(s.c_str());oneA();
   NumericHarness h;h.refuse=4;ds_preview::Program p;ds_preview::Runtime rt;execute(defineText(maximum).c_str(),p,rt,h);
   check(rt.state()==ds_preview::State::Completed&&h.events.size()==1&&h.events[0].value=='a'&&h.attempts==5,"expandedlong constant emits exactlyonce through sink retries");
  }else if(id=="DL24"){
   auto s=defineText(maximum);ds_preview::Program p;ds_preview::MemoryReader reader{s.c_str(),s.size(),0};ds_preview::CompileSession c;
   check(c.start(p,reader.reader()),"longsource compile session starts");c.step();c.cancel();check(c.state()==ds_preview::CompileState::Cancelled&&!p.ready(),"cancel leaves no partially publishedlong program");
   lower::reset();completed(s.c_str());oneA();
  }else if(id=="DL25"){
   ds_preview::Program p;ds_preview::Runtime rt;NumericHarness first;execute(defineText(maximum).c_str(),p,rt,first);check(rt.state()==ds_preview::State::Completed,"firstlonglabel run completes");
   NumericHarness next;execute(defineText(maximum,"b").c_str(),p,rt,next);check(rt.state()==ds_preview::State::Completed&&next.events.size()==1&&next.events[0].value=='b',"new compilation has cleanlongname table with no duplicate/stalevalue");
   check(textEvents(("STRING "+maximum+"\n").c_str())==maximum,"constantcollection doesnotleak betweenprograms");
  }else if(id=="DL26"){
   check(ds_preview::MaxSource==8192&&ds_preview::MaxLine==256&&ds_preview::MaxCode==128&&ds_preview::MaxText==4096&&ds_preview::MaxSymbols==32&&ds_preview::MaxFunctions==16&&ds_preview::MaxConstants==16,"allpublishedsource/resourcecounts unchanged");
   check(ds_preview::CompileStorage==4096&&ds_preview::CompileSession::compilerBytes()<=4096,"compiler remains within originalworkspace");
   auto s=defineText(maximum);ds_preview::Program p;auto before=native_alloc::calls();check(p.compile(s.c_str(),s.size()),"allocationfixture compiles");check(native_alloc::calls()==before,"compiler adds no C++heapallocation");
  }else if(id=="DL27"){
   auto lf=defineText(official),crlf=lf;size_t at=0;while((at=crlf.find('\n',at))!=std::string::npos){crlf.insert(at,"\r");at+=2;}
   for(const auto& s:{lf,crlf,std::string("\xef\xbb\xbf")+lf,lf.substr(0,lf.size()-1)}){lower::reset();completed(s.c_str());oneA();}
  }else if(id=="DL28"){
   defineReject("VAR $v=$_HOST_CONFIGURATION_REQUEST_COUNT\n",1,ds_preview::ErrorCode::Identifier);
   defineReject("$_HOST_CONFIGURATION_REQUEST_COUNT=0\n",1,ds_preview::ErrorCode::UndefinedSymbol);
   defineReject("VAR $_OS=2\n",1,ds_preview::ErrorCode::Identifier);
   defineReject("DEFINE "+maximum+" 2\nIF_DEFINED_TRUE "+maximum+"\nSTRING BAD\nEND_IF_DEFINED\n",2,ds_preview::ErrorCode::CompileFlag);
  }else check(false,"unknown DEFINElabel case");
  std::cout<<"PASS "<<id<<" ("<<assertions<<" assertions)\n";return 0;
 }catch(const std::exception& e){std::cerr<<"FAIL "<<argv[1]<<": "<<e.what()<<" ("<<assertions<<")\n";return 1;}
}
