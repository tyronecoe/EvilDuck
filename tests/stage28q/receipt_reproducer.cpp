#include "model.h"
#include <cstdio>
int main(){q::Model m;q::Sequencer s(m,q::Premises::synthetic());
 for(unsigned i=0;i<25;i++){
  m.cpu_pending=false;m.fence_ack=true;m.visible=true;
  if(s.phase==q::Phase::NakWait)m.nak_ack();if(s.phase==q::Phase::DisableWait)m.disable_ack();if(s.phase==q::Phase::FlushWait)m.flush_ack();
  s.step(i);
 }
 if(s.source_acceptance()){std::fputs("DEFECT: retirement without correlated success became acceptance\n",stderr);return 1;}
 std::puts("PASS: retirement alone cannot accept source");return 0;
}
