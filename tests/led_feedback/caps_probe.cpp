#include "probe_cases.inc"
#include "allocations.h"
int main(){try{
 mscMock::reset();mock::reset();setup();check(startupControlledReady&&route_u::bindOwner(),"controlled owner");lower::reset();
 put("/x.txt","CAPSLOCK\n");start();
 for(unsigned i=0;i<1000&&route_u::owned();++i){led_mock::nowUs=uint64_t(mock::now+1)*1000;tick();}
 check(!route_u::owned()&&route_u::status().reason==route_u::Reason::Completed,"single Caps completes");
 size_t down=lower::count,up=lower::count;for(size_t i=0;i<lower::count;++i){if(lower::calls[i].bytes[2]==0x39&&down==lower::count)down=i;else if(down!=lower::count&&lower::calls[i].bytes[2]==0&&up==lower::count)up=i;}
 check(down<up&&up<lower::count&&lower::calls[down].id==1&&lower::calls[up].id==1,"real submitted Caps and release bytes");
 tinyusb_hid_devices[0]={mockKeyboard,1,ids};uint8_t mask=2;tud_hid_set_report_cb(0,1,2,&mask,1);
 auto before=native_alloc::calls();for(unsigned i=0;i<1000;++i)tud_hid_set_report_cb(0,1,2,&mask,1);auto allocationDelta=native_alloc::calls()-before;
 check(allocationDelta==0,"no native C++ new allocations inside1000 actual dispatcher+receiver calls");
 auto d=feedback_diag::snapshot();check(d.capsDownQueued==1&&d.capsUpQueued==1,"one queued pair");
 std::cout<<"{\"status\":\"PASS\",\"assertions\":"<<assertions<<",\"mockPressMs\":"<<lower::calls[down].at<<",\"mockReleaseMs\":"<<lower::calls[up].at<<",\"mockPressToReleaseMs\":"<<uint32_t(lower::calls[up].at-lower::calls[down].at)<<",\"queueReturnDownUs\":"<<d.capsDownReturnUs<<",\"queueReturnUpUs\":"<<d.capsUpReturnUs<<",\"dispatcherReceiverCppAllocations1000Calls\":"<<allocationDelta<<",\"physicalDwellMeasured\":false}"<<std::endl;return 0;
 }catch(const std::exception&e){std::cerr<<e.what()<<std::endl;return 1;}}
