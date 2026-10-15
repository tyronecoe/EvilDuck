// Native C++ allocation accounting only; includes mock/fixture allocations.
#include "allocations.h"
#include <atomic>
#include <cstdlib>
#include <new>
static std::atomic<uint64_t> allocations{0},allocatedBytes{0};
namespace native_alloc {uint64_t calls(){return allocations.load();}uint64_t bytes(){return allocatedBytes.load();}}
void* operator new(std::size_t n){void*p=std::malloc(n?n:1);if(!p)throw std::bad_alloc();allocations.fetch_add(1);allocatedBytes.fetch_add(n);return p;}
void* operator new[](std::size_t n){return ::operator new(n);}
void operator delete(void*p)noexcept{std::free(p);}void operator delete[](void*p)noexcept{std::free(p);}
void operator delete(void*p,std::size_t)noexcept{std::free(p);}void operator delete[](void*p,std::size_t)noexcept{std::free(p);}
