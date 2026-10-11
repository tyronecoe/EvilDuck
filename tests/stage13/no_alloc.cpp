#include "script_preprocessor.h"
#include <cstdio>
#include <cstdlib>
#include <new>
static size_t allocations = 0;
void *operator new(size_t n) { ++allocations; if(void *p=std::malloc(n?n:1))return p;throw std::bad_alloc(); }
void *operator new[](size_t n) { return ::operator new(n); }
void operator delete(void *p) noexcept { std::free(p); }
void operator delete[](void *p) noexcept { std::free(p); }
void operator delete(void *p,size_t) noexcept { std::free(p); }
void operator delete[](void *p,size_t) noexcept { std::free(p); }
int main() {
  script_preprocessor::Filter filter;
  String error;
  if(!filter.accept("REM selected",1,error) || !filter.accept("REM selected",DUCKSCRIPT_MAX_SOURCE_LINES,error))return 1;
  const size_t before=allocations;
  unsigned assertions=0;
  for(unsigned line=0;line<=DUCKSCRIPT_MAX_SOURCE_LINES+1;++line) {
    ++assertions;if(filter.contains(line)!=(line==1 || line==DUCKSCRIPT_MAX_SOURCE_LINES))return 1;
  }
  ++assertions;if(allocations!=before)return 1;
  std::printf("Filter fixed storage: %zu bytes; bitmap membership C++ allocations: %zu. String parsing is not allocation-free.\n",sizeof(filter),allocations-before);
  std::printf("PASS preprocessing_bitmap_allocation_probe (%u assertions)\n",assertions);
}
