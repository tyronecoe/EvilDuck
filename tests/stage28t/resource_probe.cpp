#include "adapter.h"
#include "backend_lease.h"
#include <cstdio>
int main(){std::printf("{\"Adapter\":%zu,\"Program\":%zu,\"CompileSession\":%zu,\"Runtime\":%zu,\"Scope\":%zu,\"Observation\":%zu,\"Status\":%zu}\n",sizeof(native_b::Adapter),sizeof(ds_preview::Program),sizeof(ds_preview::CompileSession),sizeof(ds_preview::Runtime),sizeof(backend_b::Scope),sizeof(backend_b::Observation),sizeof(backend_b::Status));}
