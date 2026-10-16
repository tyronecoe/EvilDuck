#define main historical_w_main
#include "../stage28w/test_main.cpp"
#undef main
#include <fstream>
#include <sstream>
static std::string fixture(const char* name){std::ifstream f(std::string(COMPAT_FIXTURES)+"/"+name+".duck");check(f.good(),"fixture exists");std::ostringstream s;s<<f.rdbuf();return s.str();}
int main(int argc,char**argv){if(argc!=2)return 2;if(argv[1][0]=='W')return historical_w_main(argc,argv);try{
 mscMock::reset();mock::reset();setup();check(startupControlledReady&&settings::ready(),"actual controlled setup");check(route_u::bindOwner(),"bind actual owner");lower::reset();lower::count=0;mock::text="";std::string n=argv[1];
 auto good=[&](const char* f,const char* expected){put("/x.txt",fixture(f));start();done();check(!route_u::owned()&&route_u::status().reason==route_u::Reason::Completed,"Route B completed without legacy fallback");check(mock::text==expected,"actual Route B backend visible output");};
 auto reject=[&](const std::string&s){put("/x.txt","STRINGLN MUST-NOT-APPEAR\n"+s);start();done();auto d=route_u::status();check(!route_u::owned()&&d.reason==route_u::Reason::Compiler,"Route B preflight rejects");check(route_u::selected()&&lower::count==0&&mock::text.length()==0,"no report/legacy fallback after rejection");};
 if(n=="route_b_variable_prefixes")good("variable-prefixes","variables-ok\n");
 else if(n=="route_b_define_prefixes")good("define-prefixes","2/1 a b WORDx xWORD WORD! (WORD)\n");
 else if(n=="route_b_function_prefixes")good("function-prefixes","functions-ok\n");
 else if(n=="route_b_unverified_aliases_rejected"){for(auto a:{"RGUI","RWINDOWS","RCOMMAND","ROPTION"})reject(std::string(a)+" A\n");}
 else if(n=="route_b_inactive_unsupported_rejected")reject("IF FALSE THEN\nRANDOM_CHAR\nEND_IF\n");
 else if(n=="route_b_bad_prefix_identifier_rejected")reject("VAR $n=1\nVAR $result=$nn+1\n");
 else if(n=="route_b_ownership_adapter_rejected"){put("/x.txt","STRINGLN MUST-NOT-APPEAR\nHOLD a\nRELEASE a\n");start();done();check(route_u::status().reason==route_u::Reason::Capability&&!route_u::owned()&&lower::count==0&&mock::text.length()==0,"preview grammar is not linked adapter capability; reject before neutral sync");}
 else throw std::runtime_error("unknown case");
 std::cout<<"PASS "<<n<<" ("<<assertions<<" assertions)\n";return 0;
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
