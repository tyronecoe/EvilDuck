#pragma once
#include <cstring>
inline size_t strlcpy(char*d,const char*s,size_t n){size_t size=std::strlen(s);if(n){size_t copy=size<n-1?size:n-1;std::memcpy(d,s,copy);d[copy]=0;}return size;}
