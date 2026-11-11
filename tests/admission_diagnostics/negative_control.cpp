#include "observer_v1_parent.inc"
static void drainAdmission(native_b::Adapter& a){for(unsigned i=0;i<100000&&(a.state()==native_b::State::Loading||a.state()==native_b::State::Compiling);++i)a.step(++mock::now);}
int main(int argc,char**argv){if(argc!=2)return 2;try{
 nvsMock::reset();mscMock::reset();mock::reset();setup();check(startupControlledReady&&route_u::bindOwner(),"actual composed startup");lower::reset();native_b::Adapter a;
 auto before=lower::count;unsigned priorCode=0,priorLine=0;
 if(std::string(argv[1])=="N02"){
  const char* s="REM prior line one\nREM prior line two\nVAR $old =\n";
  check(a.prepare(s,strlen(s)),"prior compile request accepted");drainAdmission(a);
  auto e=a.diagnostic();priorCode=unsigned(e.code);priorLine=e.line;
  check(a.state()==native_b::State::Error&&a.fault()==native_b::Fault::Compiler&&priorCode!=0&&priorLine==3,"prior deliberate compiler error on line3");
 }
 std::string bad="STRING ";bad.push_back(char(0x80));bad+='\n';
 check(a.prepare(bad.data(),bad.size()),"new invalid request accepted for loading");drainAdmission(a);
 auto e=a.diagnostic();check(a.state()==native_b::State::Error&&a.fault()==native_b::Fault::Capability&&!a.leased(),"invalid source still rejected before lease");check(lower::count==before,"zero request attributable reports");
 if(std::string(argv[1])=="N01")check(e.code==ds_preview::ErrorCode::None&&e.line==0,"fresh original diagnostic defect reproduced");
 else check(unsigned(e.code)==priorCode&&e.line==priorLine,"reused original stale diagnostic defect reproduced");
 std::cout<<"OBSERVATION {\"case\":\""<<argv[1]<<"\",\"expected_code\":2,\"expected_line\":1,\"observed_code\":"<<unsigned(e.code)<<",\"observed_line\":"<<e.line<<",\"prior_code\":"<<priorCode<<",\"prior_line\":"<<priorLine<<",\"rejected\":true,\"report_delta\":"<<lower::count-before<<"}\n";
 std::cout<<"PASS "<<argv[1]<<" ("<<assertions<<" assertions)\n";return 0;
 }catch(const std::exception&e){std::cerr<<e.what()<<"\n";return 1;}}
