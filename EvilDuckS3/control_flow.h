#pragma once
#include "config.h"
#include <stdint.h>

// Source markers and branch state only. Expressions stay in duck_expr; no AST,
// recursion, cached source strings, heap allocation or unbounded loop metadata.
namespace control_flow {
static_assert(DUCKSCRIPT_MAX_BLOCK_DEPTH > 0 && DUCKSCRIPT_MAX_BLOCK_DEPTH < 256, "Invalid control-flow depth");
static_assert(DUCKSCRIPT_MAX_STALLED_ITERATIONS > 0 && DUCKSCRIPT_MAX_STALLED_ITERATIONS <= 65535,
              "Invalid stalled-loop limit");
static_assert(DUCKSCRIPT_MAX_LOOP_ITERATIONS > 0 && DUCKSCRIPT_MAX_LOOP_ITERATIONS < UINT32_MAX,
              "Invalid loop iteration limit");
enum class Kind : uint8_t { If, While };
struct Frame {
  uint32_t offset = 0, line = 0, variables = 0, actions = 0;
  uint16_t stalled = 0;
  Kind kind = Kind::If;
  bool parent = false, active = false, taken = false, sawElse = false;
};
class Stack {
  Frame frames[DUCKSCRIPT_MAX_BLOCK_DEPTH] = {};
  uint8_t depth = 0;
public:
  void clear() { depth = 0; }
  bool active() const { return !depth || frames[depth - 1].active; }
  const Frame *top() const { return depth ? &frames[depth - 1] : nullptr; }
  bool enterIf(bool condition) {
    if (depth >= DUCKSCRIPT_MAX_BLOCK_DEPTH) return false;
    bool parent = active();
    Frame &frame = frames[depth++]; frame = Frame();
    frame.kind = Kind::If; frame.parent = parent;
    frame.active = frame.taken = parent && condition;
    return true;
  }
  bool eligible() const {
    const Frame *frame = top();
    return frame && frame->kind == Kind::If && frame->parent && !frame->taken && !frame->sawElse;
  }
  bool alternative(bool condition, bool finalElse) {
    if (!depth || frames[depth - 1].kind != Kind::If || frames[depth - 1].sawElse) return false;
    Frame &frame = frames[depth - 1];
    frame.active = eligible() && condition;
    frame.taken |= frame.active; frame.sawElse = finalElse;
    return true;
  }
  bool leave(Kind kind) {
    if (!depth || frames[depth - 1].kind != kind) return false;
    --depth; return true;
  }
  bool enterWhile(bool condition, uint32_t offset, uint32_t line, uint32_t variables, uint32_t actions) {
    if (depth >= DUCKSCRIPT_MAX_BLOCK_DEPTH) return false;
    bool parent = active();
    Frame &frame = frames[depth++]; frame = Frame();
    frame.kind = Kind::While; frame.parent = parent; frame.active = parent && condition;
    frame.offset = offset; frame.line = line; frame.variables = variables; frame.actions = actions;
    return true;
  }
  bool reevaluateWhile(bool condition, uint32_t variables, uint32_t actions) {
    if (!depth || frames[depth - 1].kind != Kind::While) return false;
    Frame &frame = frames[depth - 1];
    frame.active = frame.parent && condition;
    frame.variables = variables; frame.actions = actions;
    return true;
  }
  bool completedIteration(uint32_t variables, uint32_t actions) {
    if (!depth || frames[depth - 1].kind != Kind::While || !frames[depth - 1].active) return false;
    Frame &frame = frames[depth - 1];
    if (frame.variables != variables || frame.actions != actions) frame.stalled = 0;
    else if (++frame.stalled >= DUCKSCRIPT_MAX_STALLED_ITERATIONS) return false;
    return true;
  }
};
}
