// Included after the unchanged Stage27B helpers, using the candidate header copy.
int main(int argc,char**argv){if(argc!=2)return 2;try{std::string n=argv[1];
 if(n=="C01"){
  std::string s;for(size_t i=0;i<MaxFunctions;++i)s+="FUNCTION fn_"+std::to_string(i)+"()\nEND_FUNCTION\n";Program p;compile(p,s);rejected(s+"FUNCTION overflow()\nEND_FUNCTION\n",ErrorCode::FunctionLimit);
  for(unsigned depth:{8u,9u}){s="fn_0()\n";for(unsigned i=0;i<depth;++i){s+="FUNCTION fn_"+std::to_string(i)+"()\n";if(i+1<depth)s+="fn_"+std::to_string(i+1)+"()\n";s+="END_FUNCTION\n";}if(depth==8)output(s,"");else runtimeError(s,ErrorCode::CallLimit);}
  s.clear();for(size_t i=0;i<MaxSymbols;++i)s+="VAR $n"+std::to_string(i)+"=1\n";compile(p,s);rejected(s+"VAR $overflow=1\n",ErrorCode::SymbolLimit);
  s.clear();for(size_t i=0;i<MaxNesting;++i)s+="IF TRUE THEN\n";s+="COMMAND a\n";for(size_t i=0;i<MaxNesting;++i)s+="END_IF\n";compile(p,s);rejected("IF TRUE THEN\n"+s+"END_IF\n",ErrorCode::NestingLimit);
 }else if(n=="C02"){
  for(auto endings:{"\n","\r\n"}){Program p;std::string s=std::string("STRING benign")+endings+"CTRL CTRL a"+endings;CHECK(!p.compile(s.data(),s.size()));CHECK(p.error().line==2);CHECK(p.error().code==ErrorCode::Syntax);Runtime r;Capture c;CHECK(!r.start(p,Capture::sink,&c));CHECK(c.events.empty());}
  for(auto name:{"CTRL","COMMAND","HOME","F1","F24"})rejected(std::string("FUNCTION ")+name+"()\nEND_FUNCTION\n",ErrorCode::Identifier);
  for(auto s:{"STRING_BASH\ntext\nEND_STRING","HOLD SHIFT","ATTACKMODE HID","INJECT_VAR $n","FUNCTION F(x)\nEND_FUNCTION","UNKNOWN","STRINGLN café"})rejected(s);
 }else if(n=="C03"){
  const char source[]="DEFINE #K LEFT\nVAR $n=0\nWHILE $n < 3\nCOMMAND A\nSHIFT #K\n$n=$n+1\nEND_WHILE\n";Program p;Runtime r;unsigned count=0;auto sink=[](void* c,const Event& e){CHECK(e.type==EventType::KeyTap);CHECK(e.modifiers==10||e.modifiers==2);++*static_cast<unsigned*>(c);return Accept::Accepted;};allocationProbe=true;allocations=0;bool ok=p.compile(source,sizeof(source)-1);bool start=ok&&r.start(p,sink,&count);for(unsigned t=0;t<1000&&r.state()==State::Running;++t)r.tick(t);size_t heap=allocations;allocationProbe=false;CHECK(ok&&start&&r.state()==State::Completed);CHECK(count==6);CHECK(heap==0);
 }else CHECK(false);std::cout<<"PASS "<<n<<" ("<<assertions<<" assertions)\n";return 0;}catch(const std::exception&e){allocationProbe=false;std::cerr<<e.what()<<'\n';return 1;}}
