#include "control_flow.h"
#include "duck_expr.h"
#include "duck_vars.h"
#include <cstdio>
#include <cstdlib>
#include <new>
static size_t allocations=0;
static unsigned assertions=0;
void *operator new(size_t bytes){++allocations;if(void *p=std::malloc(bytes?bytes:1))return p;throw std::bad_alloc();}
void *operator new[](size_t bytes){return ::operator new(bytes);}
void operator delete(void *p)noexcept{std::free(p);}void operator delete[](void *p)noexcept{std::free(p);}
void operator delete(void *p,size_t)noexcept{std::free(p);}void operator delete[](void *p,size_t)noexcept{std::free(p);}
static void require(bool ok,const char *why){++assertions;if(!ok){std::fprintf(stderr,"FAIL stage5_mixed_control_stack_no_heap: %s\n",why);std::exit(1);}}
int main(){
  String error;require(duck_vars::assign("$n","7",true,error),"numeric lookup preparation");
  size_t before=allocations;control_flow::Stack stack;
  for(unsigned i=0;i<10000;++i){
    uint16_t value=0;duck_expr::Error failure;
    require(duck_expr::evaluate("$n==7",5,value,failure,duck_vars::resolve)&&value==1,"reuse evaluator");
    require(stack.enterWhile(value,123,5,1,0)&&stack.active(),"active loop marker");
    require(stack.enterIf(false)&&!stack.active(),"inactive nested IF");
    require(stack.enterWhile(true,200,7,1,0)&&!stack.active(),"inactive parent's nested loop");
    require(stack.leave(control_flow::Kind::While)&&stack.eligible(),"restore inactive IF");
    require(stack.alternative(true,false)&&stack.active(),"ELSE IF selection");
    require(stack.leave(control_flow::Kind::If)&&stack.top()->offset==123,"retain correct parent marker");
    require(stack.completedIteration(2,0)&&stack.reevaluateWhile(false,2,0)&&!stack.active(),"progress/reevaluation");
    require(stack.leave(control_flow::Kind::While)&&stack.active(),"pop loop restores parent");
  }
  for(unsigned i=0;i<DUCKSCRIPT_MAX_BLOCK_DEPTH;++i)require(i%2?stack.enterIf(true):stack.enterWhile(true,i,i+1,0,0),"exact combined depth");
  require(!stack.enterIf(true)&&!stack.enterWhile(true,0,1,0,0),"reject stack overflow");stack.clear();
  require(!stack.leave(control_flow::Kind::While)&&!stack.reevaluateWhile(true,0,0)&&!stack.completedIteration(0,0),"underflow safe");
  require(stack.enterWhile(true,0,1,0,0),"new stalled loop");
  for(unsigned i=1;i<DUCKSCRIPT_MAX_STALLED_ITERATIONS;++i)require(stack.completedIteration(0,0)&&stack.reevaluateWhile(true,0,0),"limit minus one accepted");
  require(!stack.completedIteration(0,0),"exact stalled threshold refused");stack.clear();
  require(stack.enterWhile(true,0,1,0,0)&&stack.completedIteration(1,0)&&stack.reevaluateWhile(true,1,0)&&stack.completedIteration(1,1),"variable/action progress resets stalled counter");
  require(!stack.leave(control_flow::Kind::If)&&!stack.alternative(true,true)&&!stack.eligible(),"typed terminator/ELSE guard");
  require(allocations==before,"no C++ heap in mixed control/evaluation hot path");
  std::printf("Observed C++ allocations during 10000 mixed chains: %zu; frame %zu bytes; stack %zu bytes; Reader markers add 8 bytes\n",allocations-before,sizeof(control_flow::Frame),sizeof(control_flow::Stack));
  std::printf("PASS stage5_mixed_control_stack_no_heap (%u assertions)\n",assertions);
}
