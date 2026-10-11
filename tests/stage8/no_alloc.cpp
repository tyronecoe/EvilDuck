#include "host.h"
#include "keyboard_locale.h"
#include "hid_backend.h"
#include <cstdio>
#include <cstdlib>
#include <new>
static bool tracking=false;static size_t requests=0;static unsigned assertions=0;
void *operator new(size_t n){if(tracking)++requests;if(auto p=std::malloc(n?n:1))return p;throw std::bad_alloc();}
void *operator new[](size_t n){return ::operator new(n);}
void operator delete(void *p)noexcept{std::free(p);}void operator delete[](void *p)noexcept{std::free(p);}
void operator delete(void *p,size_t)noexcept{std::free(p);}void operator delete[](void *p,size_t)noexcept{std::free(p);}
static void check(bool ok){++assertions;if(!ok){std::fprintf(stderr,"FAIL stage8_translation_report_allocation_probe\n");std::exit(1);}}
int main(){
  mock::reset();keyboard_locale::setLocaleByName("DE");
  mock::reports.reserve(2000);mock::presses.reserve(1000);mock::heldKeys.reserve(6);
  keyboard_locale::Stroke strokes[2];uint8_t count=0;tracking=true;
  for(unsigned i=0;i<10000;++i){check(keyboard_locale::translate("ä",2,strokes,count)==2 && count==1);check(keyboard_locale::translate("^",1,strokes,count)==1 && count==2);check(keyboard_locale::translate("🙂",4,strokes,count)==4 && !count);}
  const uint8_t key=0x68;
  for(unsigned i=0;i<1000;++i){check(hid_backend::beginReport(0xff,&key,1));check(hid_backend::releaseReport());}
  tracking=false;check(!requests);
  std::printf("Translation/report hot path: %zu allocations; Stroke[2]=%zu bytes; 8-byte payload, no firmware report queue\n",requests,sizeof(strokes));
  std::printf("PASS stage8_translation_report_allocation_probe (%u assertions)\n",assertions);
}
