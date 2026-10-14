#define main stage27b_main
#include "../stage27b/test_core.cpp"
#undef main
struct MockReader {
 const std::string* source;size_t position=0,chunk=1;unsigned reads=0,seeks=0,pass=0,retries=0;
 int errorPass=0;size_t errorAt=0;bool seekFail=false,throwRead=false,throwSeek=false,zero=false,earlyEof=false,badCount=false,change=false,mixed=false;
 CompileSession* session=nullptr;Program* program=nullptr;bool reenter=false,cancelCallback=false;
 Reader reader(){return {read,seek,this,source->size()};}
 static bool seek(void* v,size_t at){auto& m=*static_cast<MockReader*>(v);++m.seeks;if(m.throwSeek)throw std::runtime_error("mock seek");if(m.seekFail&&m.seeks==2)return false;m.position=at;++m.pass;return true;}
 static ReadResult read(void* v,char* out,size_t cap){auto& m=*static_cast<MockReader*>(v);++m.reads;
  if(m.reenter){m.session->step();CHECK(!m.session->start(*m.program,m.reader()));CHECK(!m.program->compile(m.source->data(),m.source->size()));}
  if(m.cancelCallback){m.session->cancel();CompileSession other;CHECK(!other.start(*m.program,m.reader()));return {ReadStatus::Retry,0};}
  if(m.throwRead)throw std::runtime_error("mock read");if(m.badCount)return {ReadStatus::Data,cap+1};if(m.zero)return {ReadStatus::Data,0};if(m.retries){--m.retries;return {ReadStatus::Retry,0};}
  if(m.errorPass==int(m.pass)&&m.position>=m.errorAt)return {ReadStatus::Error,0};
  if(m.earlyEof||m.position==m.source->size())return {ReadStatus::Eof,0};
  size_t n=m.source->size()-m.position;if(n>cap)n=cap;size_t chunk=m.mixed?1+m.reads%7:m.chunk;if(n>chunk)n=chunk;
  memcpy(out,m.source->data()+m.position,n);if(m.change&&m.pass==2&&n&&m.position+n==m.source->size())out[n-1]='y';m.position+=n;return {ReadStatus::Data,n};
 }
};
void complete(CompileSession& s){for(unsigned n=0;n<=MaxCompileSteps+1&&s.state()==CompileState::Compiling;++n){s.step();CompileWork w=s.work();CHECK(w.bytes<=ReadChunk&&w.callbacks<=1&&w.lines<=1&&w.nodes<=1&&w.expressions<=1);CHECK(!(w.callbacks&&w.bytes));}CHECK(s.state()!=CompileState::Compiling);}
void unusable(Program& p){CHECK(!p.ready());Runtime r;Capture c;CHECK(!r.start(p,Capture::sink,&c));r.tick(0);CHECK(c.events.empty());}
std::string fixture(){return "\xef\xbb\xbf" "DEFINE #W ready\r\nVAR $n=F()+2\r\nIF $n==5 THEN\r\nSTRINGLN\r\n\t#W \r\n\r\nEND_STRINGLN\r\nEND_IF\r\nFUNCTION F()\r\nSTRING\r\n a\r\n b\r\nEND_STRING\r\nRETURN 3\r\nEND_FUNCTION";}
void equal(const std::string& source,size_t chunk,bool mixed=false){Program a,b;bool ok=a.compile(source.data(),source.size(),"equal.duck");MockReader m{&source};m.chunk=chunk;m.mixed=mixed;CompileSession s;CHECK(s.start(b,m.reader(),"equal.duck"));complete(s);CHECK(b.ready()==ok);CHECK(b.error().code==a.error().code);CHECK(b.error().line==a.error().line);CHECK(b.error().column==a.error().column);if(ok){CHECK(s.state()==CompileState::Complete);CHECK(b.instructions()==a.instructions());Capture ac,bc;Runtime ar,br;CHECK(ar.start(a,Capture::sink,&ac)&&br.start(b,Capture::sink,&bc));drive(ar);drive(br);CHECK(ar.state()==br.state());CHECK(ac.events.size()==bc.events.size());for(size_t i=0;i<ac.events.size();++i)CHECK(ac.events[i].type==bc.events[i].type&&ac.events[i].value==bc.events[i].value);}else{CHECK(s.state()==CompileState::Error);unusable(b);}}
void compileRun(const std::string& name){
 if(name=="memory_mock_chunk_equivalence"){
  for(size_t chunk:{1u,2u,3u,7u,16u,64u,256u})equal(fixture(),chunk);equal(fixture(),7,true);
 }else if(name=="empty_eof_bom_crlf_boundaries"){
  for(const std::string s:{"","\xef\xbb\xbf","STRING x","STRING x\n","STRINGLN\r\n\ta\r\nEND_STRINGLN","\xef\xbb\xbfSTRING x","REM\r","\xef\xbb","STRING\na\nEND_STRING_EXTRA"})equal(s,1);
 }else if(name=="source_line_expansion_boundaries"){
  equal(std::string(MaxSource,'\n'),1);equal(std::string(MaxSource,'\n'),32);Program p;CompileSession s;std::string large(MaxSource+1,'\n');MockReader m{&large};CHECK(!s.start(p,m.reader()));CHECK(s.error().code==ErrorCode::InputLimit);CHECK(m.reads==0&&m.seeks==0);unusable(p);
  equal("STRING\n"+std::string(256,'x')+"\nEND_STRING",3);equal("STRING\n"+std::string(257,'x')+"\nEND_STRING",2);
  equal("DEFINE #A "+std::string(63,'a')+"\nSTRING\n#A#A#A#Axxxx\nEND_STRING",1);equal("DEFINE #A "+std::string(63,'a')+"\nSTRING\n#A#A#A#Axxxxx\nEND_STRING",1);
 }else if(name=="table_and_arena_boundaries"){
  for(unsigned limit:{32u,33u}){std::string s;for(unsigned i=0;i<limit;++i)s+="VAR $v"+std::to_string(i)+"=1\n";equal(s,7);}
  for(unsigned n:{16u,17u}){std::string s;for(unsigned i=0;i<n;++i)s+="DEFINE #C"+std::to_string(i)+" 1\n";equal(s,2);s.clear();for(unsigned i=0;i<n;++i)s+="FUNCTION F"+std::to_string(i)+"()\nRETURN 1\nEND_FUNCTION\n";equal(s,3);s.clear();for(unsigned i=0;i<n;++i)s+="IF TRUE THEN\n";s+="STRING x\n";for(unsigned i=0;i<n;++i)s+="END_IF\n";equal(s,1);}
  for(unsigned n:{128u,129u}){std::string s;for(unsigned i=0;i<n;++i)s+="ENTER\n";equal(s,16);}for(unsigned n:{1024u,1025u})equal("STRINGLN\n"+std::string(n,'\n')+"END_STRINGLN",1);
 }else if(name=="read_errors_pass_one_two_seek_exception"){
  std::string source=fixture();for(int pass:{1,2}){Program p;CompileSession s;MockReader m{&source};m.errorPass=pass;m.errorAt=20;CHECK(s.start(p,m.reader(),"fault.duck"));complete(s);CHECK(s.error().code==ErrorCode::ReadError);CHECK(s.error().line>0);unusable(p);unsigned reads=m.reads;s.step();CHECK(m.reads==reads);}
  for(unsigned mode=0;mode<3;++mode){Program p;CompileSession s;MockReader m{&source};m.seekFail=mode==0;m.throwRead=mode==1;m.throwSeek=mode==2;CHECK(s.start(p,m.reader()));complete(s);CHECK(s.error().code==(mode==1?ErrorCode::ReadError:ErrorCode::SeekError));unusable(p);}
 }else if(name=="zero_progress_retry_invalid_counts"){
  std::string source="STRING x";for(unsigned mode=0;mode<4;++mode){Program p;CompileSession s;MockReader m{&source};m.zero=mode==0;m.earlyEof=mode==1;m.badCount=mode==2;m.retries=mode==3?100:0;CHECK(s.start(p,m.reader(),"stalled.duck",20));complete(s);CHECK(s.error().code==(mode==3?ErrorCode::CompileLimit:ErrorCode::ReadError));unusable(p);}
  Program p;CompileSession s;MockReader m{&source};m.retries=3;CHECK(s.start(p,m.reader()));complete(s);CHECK(p.ready());
 }else if(name=="cancel_every_phase_and_restart"){
  std::string source=fixture();for(auto phase:{CompilePhase::SeekFirst,CompilePhase::Read,CompilePhase::Consume,CompilePhase::Line,CompilePhase::EndPass,CompilePhase::Rewind,CompilePhase::Structure,CompilePhase::InventoryStart,CompilePhase::InventoryNode,CompilePhase::Validate,CompilePhase::Publish}){
   Program p;CompileSession s;MockReader m{&source};CHECK(s.start(p,m.reader()));unsigned n=0;while(s.phase()!=phase&&s.state()==CompileState::Compiling&&n++<MaxCompileSteps)s.step();CHECK(s.phase()==phase);s.cancel();CHECK(s.state()==CompileState::Cancelled);unsigned reads=m.reads,seeks=m.seeks;s.step();CHECK(m.reads==reads&&m.seeks==seeks);unusable(p);std::string changed="VAR $fresh=7\nSTRING new";MockReader fresh{&changed};CHECK(s.start(p,fresh.reader()));complete(s);CHECK(p.ready());Runtime r;Capture c;CHECK(r.start(p,Capture::sink,&c));drive(r);CHECK(c.visible()=="new");CHECK(variable(r,"$fresh")==7);uint16_t v;CHECK(!r.variable("$n",v));
  }
 }else if(name=="partial_line_block_cancel_boundaries"){
  std::string source="DEFINE #A value\nSTRINGLN\n\t#A \nEND_STRINGLN";for(unsigned cutoff=0;cutoff<160;++cutoff){Program p;CompileSession s;MockReader m{&source};CHECK(s.start(p,m.reader()));for(unsigned i=0;i<cutoff&&s.state()==CompileState::Compiling;++i)s.step();if(s.state()!=CompileState::Compiling)continue;s.cancel();unsigned before=m.reads;s.step();CHECK(m.reads==before);unusable(p);}
 }else if(name=="incremental_inventory_validation_work"){
  std::string source="VAR $x=F()\nFUNCTION F()\n";for(unsigned i=0;i<50;++i)source+="IF $x==1 THEN\nEND_IF\n";source+="RETURN 1\nEND_FUNCTION";
  Program p;CompileSession s;MockReader m{&source};m.chunk=256;CHECK(s.start(p,m.reader()));s.step();CHECK(!p.ready());CHECK(s.state()==CompileState::Compiling);unsigned nodes=0,expressions=0,lines=0;for(unsigned i=0;i<10000&&s.state()==CompileState::Compiling;++i){s.step();auto w=s.work();CHECK(w.bytes<=32&&w.callbacks<=1&&w.lines<=1&&w.nodes<=1&&w.expressions<=1);nodes+=w.nodes;expressions+=w.expressions;lines+=w.lines;if(s.phase()==CompilePhase::Publish&&s.state()==CompileState::Compiling)CHECK(!p.ready());}CHECK(p.ready());CHECK(nodes>=50&&expressions>=100&&lines==208);
 }else if(name=="reentrancy_and_callback_cancellation"){
  std::string source="STRING x";Program p;CompileSession s;MockReader m{&source};m.session=&s;m.program=&p;m.reenter=true;CHECK(s.start(p,m.reader()));complete(s);CHECK(p.ready());
  MockReader c{&source};c.session=&s;c.program=&p;c.cancelCallback=true;CHECK(s.start(p,c.reader()));complete(s);CHECK(s.state()==CompileState::Cancelled);unusable(p);
 }else if(name=="runtime_borrow_multiple_sessions_destructor"){
  Program p;compile(p,"STRING x");Capture c;Runtime r;CHECK(r.start(p,Capture::sink,&c));std::string source="STRING y";MockReader m{&source};CompileSession a,b;CHECK(!a.start(p,m.reader()));CHECK(a.error().code==ErrorCode::Busy);CHECK(p.ready());r.cancel();CHECK(a.start(p,m.reader()));CHECK(!b.start(p,m.reader()));CHECK(b.error().code==ErrorCode::Busy);a.cancel();CHECK(b.start(p,m.reader()));complete(b);CHECK(p.ready());{CompileSession dying;CHECK(dying.start(p,m.reader()));}unusable(p);
 }else if(name=="stable_source_contract_and_failed_reuse"){
  std::string source="STRING x";Program p;CompileSession s;MockReader m{&source};m.change=true;CHECK(s.start(p,m.reader()));complete(s);CHECK(s.state()==CompileState::Error);CHECK(s.error().code==ErrorCode::ReadError);unusable(p);m.change=false;CHECK(s.start(p,m.reader()));complete(s);CHECK(p.ready());
  std::string invalid="VAR $n = (2+)";MockReader wrong{&invalid};CHECK(s.start(p,wrong.reader()));complete(s);CHECK(s.error().code==ErrorCode::Syntax);unusable(p);CHECK(s.start(p,m.reader()));complete(s);CHECK(p.ready());
 }else if(name=="reader_lifetime_release_after_terminal"){
  Program p;CompileSession s;{std::string source="STRING x";MockReader m{&source};CHECK(s.start(p,m.reader()));complete(s);}s.step();s.cancel();Capture c;Runtime r;CHECK(r.start(p,Capture::sink,&c));drive(r);CHECK(c.visible()=="x");
 }else if(name=="invalid_api_budgets_and_full_retry_limit"){
  Program p;CompileSession s;CHECK(!s.start(p,Reader{}));unusable(p);std::string source="";MockReader m{&source};CHECK(!s.start(p,m.reader(),"ok",0));CHECK(s.error().code==ErrorCode::InvalidBudget);CHECK(!s.start(p,m.reader(),"ok",MaxCompileSteps+1));m.retries=MaxCompileSteps+2;CHECK(s.start(p,m.reader()));complete(s);CHECK(s.error().code==ErrorCode::CompileLimit);unusable(p);
 }else if(name=="seeded_chunk_mutations"){
  std::string base=fixture();uint32_t seed=0x28c;for(unsigned i=0;i<150;++i){seed=seed*1664525u+1013904223u;std::string text=base;text[seed%text.size()]=static_cast<char>(32+(seed>>16)%95);equal(text,1+seed%32,true);}
 }else if(name=="atomic_line_and_expression_worst_bounds"){
  std::string source;for(unsigned i=0;i<16;++i)source+="DEFINE #CONST"+std::to_string(i)+" "+std::string(63,'q')+"\n";
  source+="STRING\n"+std::string(256,'x')+"\nEND_STRING\nVAR $x=";for(unsigned i=0;i<32;++i){if(i)source+='+';source+='1';}
  source+="\nVAR $y="+std::string(15,'(')+"1"+std::string(15,')');
  Program p;CompileSession s;MockReader m{&source};m.chunk=256;CHECK(s.start(p,m.reader()));unsigned maxBytes=0,maxLines=0,maxExpressions=0,maxCallbacks=0;
  while(s.state()==CompileState::Compiling){s.step();auto w=s.work();if(w.bytes>maxBytes)maxBytes=w.bytes;if(w.lines>maxLines)maxLines=w.lines;if(w.expressions>maxExpressions)maxExpressions=w.expressions;if(w.callbacks>maxCallbacks)maxCallbacks=w.callbacks;CHECK(w.bytes<=32&&w.lines<=1&&w.nodes<=1&&w.expressions<=1&&w.callbacks<=1);}
  CHECK(p.ready());CHECK(maxBytes==32&&maxLines==1&&maxExpressions==1&&maxCallbacks==1);Capture c;Runtime r;CHECK(r.start(p,Capture::sink,&c));drive(r);CHECK(variable(r,"$x")==32);CHECK(variable(r,"$y")==1);CHECK(c.visible()==std::string(256,'x'));
 }else if(name=="no_heap_compiler_read_and_inventory"){
  std::string source=fixture();Program p;CompileSession s;MockReader m{&source};allocationProbe=true;allocations=0;bool ok=s.start(p,m.reader());for(unsigned i=0;i<10000&&s.state()==CompileState::Compiling;++i)s.step();size_t count=allocations;allocationProbe=false;CHECK(ok&&s.state()==CompileState::Complete);CHECK(count==0);CHECK(CompileSession::compilerBytes()<=CompileStorage);
 }else throw std::runtime_error("Unknown compile test");
}
int main(int argc,char** argv){try{if(argc!=2)return 2;compileRun(argv[1]);std::cout<<"PASS "<<argv[1]<<" ("<<assertions<<" assertions)\n";return 0;}catch(const std::exception& e){allocationProbe=false;std::cerr<<e.what()<<"\n";return 1;}}
