#pragma once
#include <Arduino.h>
#include "duck_expr.h"

namespace script_functions {
static_assert(DUCKSCRIPT_MAX_FUNCTIONS > 0 && DUCKSCRIPT_MAX_FUNCTIONS < 256,"Invalid function limit");
static_assert(DUCKSCRIPT_MAX_CALL_DEPTH > 0 && DUCKSCRIPT_MAX_CALL_DEPTH < 256,"Invalid call depth");
static_assert(DUCKSCRIPT_MAX_FUNCTION_CALLS > 0 && DUCKSCRIPT_MAX_FUNCTION_CALLS < UINT32_MAX,"Invalid call budget");
struct Function {
  char name[DUCKSCRIPT_MAX_IDENTIFIER_LEN+1] = {};
  uint32_t body = 0, headerLine = 0, end = 0, endLine = 0;
};
bool name(const String &invocation, String &identifier, String &error);
class Table {
  Function entries[DUCKSCRIPT_MAX_FUNCTIONS] = {};
  uint8_t count = 0;
public:
  int find(const char *, size_t) const;
  const Function *get(uint16_t index) const { return index < count ? &entries[index] : nullptr; }
  bool add(const String &,uint32_t,uint32_t,String &);
  bool close(uint32_t end,uint32_t line);
  static duck_expr::Lookup resolve(const char *,size_t,uint16_t &,void *);
};
enum class Consumer : uint8_t { None, Discard, Assignment, Numeric, If, ElseIf, While, Return };
struct Evaluation {
  duck_expr::Program program;
  char target[DUCKSCRIPT_MAX_IDENTIFIER_LEN+1] = {};
  uint32_t offset = 0, line = 0, variables = 0, actions = 0;
  Consumer consumer = Consumer::None;
  uint8_t command = 0;
  bool declaration = false, reenter = false;
};
struct Call {
  Evaluation caller;
  uint32_t nextOffset = 0, nextLine = 0;
  uint16_t function = 0;
  uint8_t base = 0, callerBase = 0;
  bool valueRequired = false;
};
class Calls {
  Call frames[DUCKSCRIPT_MAX_CALL_DEPTH] = {};
  uint8_t depth = 0;
public:
  void clear() { depth=0; }
  uint8_t size() const { return depth; }
  Call *top() { return depth ? &frames[depth-1] : nullptr; }
  const Call *top() const { return depth ? &frames[depth-1] : nullptr; }
  bool push(const Call &frame) { if(depth >= DUCKSCRIPT_MAX_CALL_DEPTH)return false;frames[depth++]=frame;return true; }
  bool pop(Call &frame) { if(!depth)return false;frame=frames[--depth];return true; }
};
}
