#include "duck_random.h"
#include <cstdio>
#include <cstdlib>
#include <new>
static size_t allocations=0;static uint32_t number=1;
void *operator new(size_t n){++allocations;if(void *p=std::malloc(n?n:1))return p;throw std::bad_alloc();}
void *operator new[](size_t n){return ::operator new(n);}
void operator delete(void *p) noexcept{std::free(p);}void operator delete[](void *p) noexcept{std::free(p);}
void operator delete(void *p,size_t) noexcept{std::free(p);}void operator delete[](void *p,size_t) noexcept{std::free(p);}
static uint32_t raw(){number=1664525U*number+1013904223U;return number;}
int main(){duck_random::source(raw);const auto before=allocations;unsigned assertions=0;for(unsigned i=0;i<10000;++i){uint16_t v;char c;++assertions;if(!duck_random::range(0,65535,v))return 1;++assertions;if(!duck_random::character(i%6,c))return 1;}++assertions;if(allocations!=before)return 1;std::printf("Random range/character hot path: %zu C++ allocations, fixed bounded sampler\n",allocations-before);std::printf("PASS random_range_allocation_probe (%u assertions)\n",assertions);}
