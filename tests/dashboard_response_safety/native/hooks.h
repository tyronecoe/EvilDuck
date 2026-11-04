#pragma once
#include <cstdlib>
#include <stdlib.h>
extern "C" void *budget_realloc(void *,size_t);
extern "C" void budget_free(void *);
#define realloc budget_realloc
#define free budget_free
