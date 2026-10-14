// Counts C++ new calls only, not all libc/SDK allocations or physical heap.
#include "journal_driver.h"
#include <cstdlib>
#include <cstdio>
#include <new>
static unsigned allocations=0;
void* operator new(size_t bytes){++allocations;if(void* p=std::malloc(bytes?bytes:1))return p;throw std::bad_alloc();}
void* operator new[](size_t bytes){return ::operator new(bytes);}
void operator delete(void* p) noexcept{std::free(p);}
void operator delete[](void* p) noexcept{std::free(p);}
void operator delete(void* p,size_t) noexcept{std::free(p);}
void operator delete[](void* p,size_t) noexcept{std::free(p);}
int main(){
 static stage28m::Driver d;
 unsigned before=allocations;
 constexpr char source[]="HOLD a\nRELEASE a\nSTRING b";
 if(!d.compileMemory(source,sizeof(source)-1))return 1;
 for(unsigned n=0;n<2000&&d.compiler().state()==ds_preview::CompileState::Compiling;++n)d.compileStep();
 if(!d.program().ready()||!d.begin())return 2;
 for(unsigned n=0;n<12&&d.state()==stage28m::State::Syncing;++n)d.step(0);if(!d.start())return 3;
 for(unsigned n=0;n<2000&&d.state()==stage28m::State::Running;++n)d.step(0);
 if(d.state()!=stage28m::State::TerminalUndrained||!d.drain())return 4;
 for(unsigned n=0;n<12&&d.state()==stage28m::State::DrainPending;++n)d.step(0);if(d.state()!=stage28m::State::Drained)return 5;
 if(!d.transport().fence(d.transport().epoch())||!d.canReclaim())return 7;
 unsigned difference=allocations-before;
 std::printf("{\"new_calls\":%u,\"scope\":\"healthy compile, run, synthetic tagged acceptance and drain; C++ new only\",\"host_only\":true}\n",difference);
 return difference?6:0;
}
