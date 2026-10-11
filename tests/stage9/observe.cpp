// Audit observations use actual runtime with RAM-only storage/HID/clock.
#include "host.h"
#include "com.h"
#include "duckscript.h"
#include <fstream>
#include <sstream>
#include <iostream>
#include <stdexcept>
static unsigned assertions=0;
static void check(bool ok,const char *why){++assertions;if(!ok)throw std::runtime_error(why);}
int main(int argc,char **argv){
 try{
  if(argc!=5)throw std::runtime_error("fixture, expected output file, diagnostic, source required");
  std::ifstream in(argv[1],std::ios::binary),out(argv[2],std::ios::binary);
  check(in.good()&&out.good(),"offline fixture files readable");
  std::ostringstream script,expected;script<<in.rdbuf();expected<<out.rdbuf();
  mock::reset();mock::file(argv[4],script.str().c_str());
  check(duckscript::run(argv[4]),"mocked source accepted");
  mock::drain(100000);
  std::cout<<"DIAGNOSTIC "<<duckscript::lastError().c_str()<<'\n';
  if(argv[3][0])check(duckscript::lastError().indexOf(argv[3])>=0,"expected diagnostic observed");
  else check(!duckscript::lastError().length(),"no diagnostic expected");
  check(mock::text==expected.str().c_str(),"exact mocked text observation");
  check(!duckscript::running()&&!com::busy(),"execution finished");
  check(!mock::blockingDelays,"cooperative execution retained");
  check(mock::heldKeys.empty()&&!mock::heldModifiers,"released runtime-owned HID");
  if(argv[3][0]&&expected.str().empty())check(mock::reports.empty(),"zero HID observation");
  std::cout<<"OBSERVED "<<assertions<<" assertions\n";return 0;
 }catch(const std::exception &e){std::cerr<<"MISMATCH "<<e.what()<<'\n';return 1;}
}
