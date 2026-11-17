extern "C" void ds02mark(const char*);
extern "C" bool ds02Safety();
extern "C" bool ds02Controls();
#include "admission_parent.inc"
int main(int argc,char**argv){if(argc!=2)return 2;std::string id=argv[1];if(id.rfind("DS",0)!=0)return admission_parent_main(argc,argv);try{
 nvsMock::reset();mscMock::reset();mock::reset();setup();check(startupControlledReady&&route_u::bindOwner(),"controlled startup owner");lower::reset();led_mock::nowUs=0;rng_mock::reset();
 if(id=="DS01"){completed("DEFINE #STEP $count = ($count + 1)\nDEFINE #MARK STRING a\nVAR $count = 0\n#STEP\nIF ($count == 1) THEN\n#MARK\nEND_IF\n");oneA();}
 else if(id=="DS02"){put("/x.txt","DEFINE #WAIT DELAY 10000\n#WAIT\nSTRING BAD\n");ds02mark("before_start");start();ds02mark("after_start");for(unsigned n=0;n<100;++n)tick();ds02mark("cancellation_request_before_stop");route_u::stop();ds02mark("cancellation_request_after_stop");prCancelled();ds02mark("terminal_after_prCancelled_before_original_assertion");check(ds02Safety(),"DS02 exact synchronization and cleanup evidence with no payload or replay");check(ds02Controls(),"DS02 predicate rejects every inert negative control");completed("STRING a\n");oneA();}
 else if(id=="DS03"){put("/x.txt","DEFINE #WAIT DELAY 10000\nHOLD RSHIFT\n#WAIT\nSTRING BAD\n");start();reports(1);route_u::stop();prCancelled();check(!hid_backend::hasPersistent(),"STOP releases held ownership");lower::reset();completed("STRING a\n");oneA();}
 else if(id=="DS04"){native_b::Adapter a;adReady(a,"STRING a\n");adRun(a);lower::reset();std::string s="DEFINE #BAD VAR $x = 1\nREM line two\n#BAD\n";check(a.prepare(s.data(),s.size()),"bad label admitted for compilation");adDrain(a);check(a.state()==native_b::State::Error&&a.diagnostic().line==3&&lower::count==0,"invocation line and zero HID");completed("STRING a\n");oneA();}
 else throw std::runtime_error("unknown focused case");std::cout<<"PASS "<<id<<"\n";return 0;}catch(const std::exception&e){std::cerr<<e.what()<<"\n";return 1;}}
