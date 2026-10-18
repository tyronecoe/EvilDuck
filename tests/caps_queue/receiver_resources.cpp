#include "led_receiver.h"
#include <assert.h>
#include <stdio.h>
#include "allocations.h"
int main(){
 led_return::invalidate(1);auto before=native_alloc::calls();
 for(unsigned i=0;i<1000;++i){
#ifdef NEW_RECEIVER
  led_return::callback(1,1);
#endif
  led_return::observe(i&7,1,i);
 }
 auto after=native_alloc::calls();auto s=led_return::snapshot(1000);
 assert(before==after&&s.reports==1000);
#ifdef NEW_RECEIVER
 assert(s.callbacks==1000&&s.lastCallbackId==1&&s.lastCallbackSize==1);
#endif
 printf("{\"Snapshot_native_bytes\":%zu,\"receiver_native_bytes\":%zu,\"loop_allocations\":%llu}\n",sizeof(s),led_return::storageBytes(),(unsigned long long)(after-before));
}
