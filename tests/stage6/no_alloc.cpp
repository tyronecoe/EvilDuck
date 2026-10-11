#include "duck_expr.h"
#include "duck_vars.h"
#include "script_functions.h"
#include <cstdio>
#include <cstdlib>
#include <new>
static unsigned assertions=0;static size_t allocations=0;
void *operator new(size_t n){++allocations;if(auto p=std::malloc(n?n:1))return p;throw std::bad_alloc();}
void *operator new[](size_t n){return ::operator new(n);}void operator delete(void *p)noexcept{std::free(p);}void operator delete[](void *p)noexcept{std::free(p);}void operator delete(void *p,size_t)noexcept{std::free(p);}void operator delete[](void *p,size_t)noexcept{std::free(p);}
static void check(bool c,const char *message){++assertions;if(!c){std::fprintf(stderr,"FAIL stage6_postfix_call_state_no_heap: %s\n",message);std::exit(1);}}
static duck_expr::Lookup resolve(const char *,size_t,uint16_t &index,void *){index=0;return duck_expr::Lookup::Number;}
int main(){
  String error;check(duck_vars::assign("$n","7",true,error),"numeric setup");duck_expr::functions(resolve);
  size_t before=allocations;script_functions::Calls calls;
  for(unsigned i=0;i<10000;++i){
    script_functions::Call frame;duck_expr::Error e;uint16_t value=0;
    check(frame.caller.program.compile("$n+value()",10,e,duck_vars::resolve),"compile bounded program with call");
    check(frame.caller.program.step(value,e,duck_vars::resolve,nullptr)==duck_expr::Step::Call && value==0,"yield pending function index");
    check(calls.push(frame),"save fixed caller frame");script_functions::Call resumed;check(calls.pop(resumed),"restore bounded frame");
    check(resumed.caller.program.returned(3),"inject result once");check(resumed.caller.program.step(value,e,duck_vars::resolve,nullptr)==duck_expr::Step::Done && value==10,"resume without replay");
  }
  script_functions::Call frame;for(unsigned i=0;i<DUCKSCRIPT_MAX_CALL_DEPTH;++i)check(calls.push(frame),"exact call depth");check(!calls.push(frame),"call overflow rejects");calls.clear();check(!calls.pop(frame),"underflow rejects");check(allocations==before,"postfix/call hot path allocates no C++ heap");duck_expr::functions(nullptr);
  std::printf("Program %zu bytes; evaluation %zu; call frame %zu; fixed call stack %zu; function table %zu; observed C++ allocations %zu\n",sizeof(duck_expr::Program),sizeof(script_functions::Evaluation),sizeof(script_functions::Call),sizeof(script_functions::Calls),sizeof(script_functions::Table),allocations-before);
  std::printf("PASS stage6_postfix_call_state_no_heap (%u assertions)\n",assertions);
}
