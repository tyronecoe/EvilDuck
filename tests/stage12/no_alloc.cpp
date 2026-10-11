#include "host.h"
#include "hid_backend.h"
#include "internal_vars.h"
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
  hid_backend::begin(); uint16_t value=0;
  tracking=true;
  for(unsigned i=0;i<10000;++i) {
    uint8_t leds=i&7;
    check(hid_backend::receiveLockReport(1,&leds,1,hid_backend::lockSession()));
    check(internal_vars::resolve("$_CAPSLOCK_ON",13,value)==duck_expr::Lookup::Number);
    check(value==bool(leds&2));
    check(internal_vars::reserved("$_JITTER_ENABLED",16));
    check(hid_backend::saveLockState());
  }
  tracking=false;
  check(!requests); check(!hid_backend::hasPersistent());
  std::printf("Feedback/registry hot path: %zu C++ allocations; fixed critical-section snapshots, no event queue\n",requests);
  std::printf("PASS feedback_registry_allocation_probe (%u assertions)\n",assertions);
}
