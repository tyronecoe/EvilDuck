#include "caps_trial.h"
#include "feedback_diag.h"
#include "allocations.h"
#include <iostream>
namespace feedback_diag {
Snapshot snapshot(){Snapshot s;s.boot=1;s.session=1;return s;}
Transport transport(){return {true,true,false,true,1};}
}
int main(){
 caps_trial::begin(1,100);(void)caps_trial::snapshot();caps_trial::finish(1,1);
 auto before=native_alloc::calls();bool ok=true;
 for(unsigned i=2;i<10002;++i){caps_trial::begin(i,250);ok&=caps_trial::dwell()==250&&caps_trial::sessionValid();caps_trial::submitted(true,100);caps_trial::completed(true,101);caps_trial::submitted(false,250100);caps_trial::completed(false,250101);caps_trial::finish(i,1);auto s=caps_trial::snapshot();ok&=!s.active&&s.request==i&&s.up&&s.upComplete;}
 auto delta=native_alloc::calls()-before;
 std::cout<<"{\"PASS\":"<<(ok&&delta==0?1:0)<<",\"FAIL\":"<<(!ok||delta!=0?1:0)<<",\"iterations\":10000,\"nativeCppAllocations\":"<<delta<<",\"scope\":\"actual new helper with stubbed feedback state; not full firmware heap\"}\n";
 return !ok||delta!=0;
}
