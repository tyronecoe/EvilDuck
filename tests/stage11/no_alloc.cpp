#include "host.h"
#include "hid_backend.h"
#include <cstdio>
#include <cstdlib>
#include <new>
static bool tracking = false;
static size_t requests = 0;
static unsigned assertions = 0;
[[gnu::noinline]] void *operator new(size_t n) {
  if (tracking) ++requests;
  if (void *p=std::malloc(n?n:1)) return p;
  throw std::bad_alloc();
}
[[gnu::noinline]] void *operator new[](size_t n) { return ::operator new(n); }
[[gnu::noinline]] void operator delete(void *p) noexcept { std::free(p); }
[[gnu::noinline]] void operator delete[](void *p) noexcept { std::free(p); }
[[gnu::noinline]] void operator delete(void *p,size_t) noexcept { std::free(p); }
[[gnu::noinline]] void operator delete[](void *p,size_t) noexcept { std::free(p); }
static void check(bool ok) { ++assertions; if(!ok) std::exit(1); }
int main() {
  mock::reset();
  mock::reports.reserve(10000); mock::presses.reserve(20000); mock::heldKeys.reserve(6);
  uint8_t key=5;
  tracking=true;
  for(unsigned i=0;i<1000;++i) {
    check(hid_backend::hold(1,4)); check(hid_backend::hold(1,4));
    check(hid_backend::beginReport(2,&key,1)); check(hid_backend::releaseReport());
    check(hid_backend::release(1,4)); check(hid_backend::release(1,4));
    mock::usbAccept=false;
    check(!hid_backend::hold(1,4));
    hid_backend::cancelReport(); check(hid_backend::clearing());
    mock::usbAccept=true; hid_backend::update(); check(!hid_backend::clearing());
  }
  tracking=false;
  check(!requests); check(!hid_backend::hasPersistent());
  std::printf("Ownership/merge/retry hot path: %zu C++ allocations; fixed 7-byte ownership, no report queue\n",requests);
  std::printf("PASS ownership_allocation_probe (%u assertions)\n",assertions);
}
