#include "core.h"
#include <cstring>
#include <cstdio>
using namespace ds_preview;
struct Probe{Runtime* runtime;unsigned tries=0;bool wrong=false;static Accept sink(void*c,const Event&e){auto& p=*static_cast<Probe*>(c);++p.tries;if(e.type!=EventType::KeyTap||e.value!=4||e.modifiers)p.wrong=true;p.runtime->values_[0]=5;return p.tries<4?Accept::Retry:Accept::Accepted;}};
int main(){
 const char* source="IF FALSE THEN\nVAR $k=4\nEND_IF\nINJECT_VAR $k\n";Program p;Runtime rt;unsigned events=0;
 if(!p.compile(source,strlen(source))||!rt.start(p,[](void*c,const Event&){++*static_cast<unsigned*>(c);return Accept::Accepted;},&events))return 1;
 for(unsigned i=0;i<100&&rt.state()==State::Running;++i)rt.tick(i);
 if(rt.state()!=State::Error||rt.error().code!=ErrorCode::Uninitialized||rt.error().line!=4||events)return 2;
 source="VAR $k=4\nINJECT_VAR $k\n";Probe probe{&rt};if(!p.compile(source,strlen(source))||!rt.start(p,Probe::sink,&probe))return 3;
 for(unsigned i=0;i<100&&rt.state()==State::Running;++i)rt.tick(i);
 uint16_t key=0;if(rt.state()!=State::Completed||probe.wrong||probe.tries!=4||!rt.variable("$k",key)||key!=5)return 4;
 std::puts("PASS core uninitialized runtime rejection and cached injection operand under synthetic variable mutation (2 checks)");
}
