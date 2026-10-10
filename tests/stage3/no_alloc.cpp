// Host-only allocation observation of the real evaluator and numeric resolver.
#include "duck_expr.h"
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
  if (!condition) { std::fprintf(stderr,"FAIL stage3_expression_hot_path_no_heap: %s\n",message); std::exit(1); }
}
int main() {
  String error;
  require(duck_vars::assign("$n","7",true,error),"initialize numeric lookup outside allocation observation");
  const size_t before = allocations;
  for (unsigned i = 0; i < 10000; ++i) {
    uint16_t value = 0; duck_expr::Error failure;
    require(duck_expr::evaluate("$n*3+1",6,value,failure,duck_vars::resolve) && value == 22,
            "numeric resolver and expression hot path must work");
  }
  for (unsigned i = 0; i < 20; ++i) {
    uint16_t value = 0; duck_expr::Error failure;
    require(!duck_expr::evaluate("1/0",3,value,failure) && failure.message,
            "error reporting inside evaluator must remain allocation-free");
  }
  require(allocations == before,"evaluator/resolver allocated C++ heap storage");
  std::printf("Observed C++ heap allocations during 10020 evaluations: %zu; Symbols metadata: %zu bytes\n",
              allocations-before,sizeof(duck_vars::Symbols));
  std::printf("PASS stage3_expression_hot_path_no_heap (%u assertions)\n",assertions);
}
