#define main historical_stage8_main
#include "../stage8/test_main.cpp"
#undef main
#include <fstream>
#include <sstream>
static std::string fixture(const char* name){std::ifstream f(std::string(COMPAT_FIXTURES)+"/"+name+".duck");check(f.good(),"fixture exists");std::ostringstream s;s<<f.rdbuf();return s.str();}
int main(int argc,char**argv){if(argc!=2)return 2;if(std::string(argv[1]).find("stage8_")==0)return historical_stage8_main(argc,argv);try{
 std::string n=argv[1];
 if(n=="legacy_variable_prefixes"){run(fixture("variable-prefixes"));check(mock::text=="variables-ok\n","exact identifier identity through assignments and conditions");}
 else if(n=="legacy_define_prefixes"){run(fixture("define-prefixes"));check(mock::text=="2/1 a b WORDx xWORD WORD! (WORD)\n","longest hash/bare-label matches with delimiters");}
 else if(n=="legacy_function_prefixes"){run(fixture("function-prefixes"));check(mock::text=="functions-ok\n","function identity and calls evaluated once");}
 else if(n=="legacy_interpolation_prefixes"){run("VAR $n=1\nVAR $nn=2\nVAR $n_1=3\nSTRINGLN $n:$nn:$n_1\n");check(mock::text=="1:2:3\n","text extension resolves whole names without substring capture");}
 else if(n=="legacy_unverified_aliases_rejected"){for(auto alias:{"RGUI","RWINDOWS","RCOMMAND","ROPTION"})rejected(std::string(alias)+" A\n","Unsupported command");}
 else throw std::runtime_error("unknown case");
 std::cout<<"PASS "<<n<<" ("<<assertions<<" assertions)\n";return 0;
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
