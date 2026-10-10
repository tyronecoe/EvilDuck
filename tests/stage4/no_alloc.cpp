// Host-only allocation observation of the real evaluator and numeric resolver.
#include "duck_expr.h"
#include "conditional_state.h"
#include "duck_vars.h"
#include <cstdio>
#include <cstdlib>
#include <new>

static size_t allocations = 0;
static unsigned assertions = 0;
void *operator new(size_t bytes) {
  ++allocations;
  if (void *pointer = std::malloc(bytes ? bytes : 1)) return pointer;
  throw std::bad_alloc();
}
void *operator new[](size_t bytes) { return ::operator new(bytes); }
void operator delete(void *pointer) noexcept { std::free(pointer); }
void operator delete[](void *pointer) noexcept { std::free(pointer); }
void operator delete(void *pointer, size_t) noexcept { std::free(pointer); }
void operator delete[](void *pointer, size_t) noexcept { std::free(pointer); }
static void require(bool condition, const char *message) {
  ++assertions;
  if (!condition) { std::fprintf(stderr,"FAIL stage4_conditional_stack_no_heap: %s\n",message); std::exit(1); }
}
int main() {
  String error;
  require(duck_vars::assign("$n","7",true,error),"initialize numeric lookup outside allocation observation");
  const size_t before = allocations;
  conditional_state::Stack stack;
  for (unsigned i=0;i<10000;++i) {
    uint16_t value=0; duck_expr::Error failure;
    require(duck_expr::evaluate("$n==7",5,value,failure,duck_vars::resolve) && value==1,"reuse Stage 3 evaluator");
    require(stack.enter(value!=0) && stack.active(),"enter active frame");
    require(stack.enter(false) && !stack.active(),"enter inactive nested frame");
    require(stack.alternative(true,false) && stack.active(),"select nested ELSE IF");
    require(stack.alternative(true,true) && !stack.active(),"skip final ELSE after match");
    require(stack.leave() && stack.active() && stack.leave(),"restore parent then empty stack");
  }
  for(unsigned i=0;i<DUCKSCRIPT_MAX_BLOCK_DEPTH;++i) require(stack.enter(false),"exact fixed stack limit");
  require(!stack.enter(true),"stack overflow must reject without mutation");stack.clear();
  require(stack.active() && !stack.leave() && !stack.alternative(true,true),"clear/underflow guards");
  require(allocations == before,"evaluator/resolver allocated C++ heap storage");
  std::printf("Observed C++ heap allocations during 10000 condition/branch chains: %zu; Conditional stack: %zu bytes\n",
              allocations-before,sizeof(conditional_state::Stack));
  std::printf("PASS stage4_conditional_stack_no_heap (%u assertions)\n",assertions);
}
