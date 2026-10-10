#pragma once
#include "config.h"
#include <stdint.h>

// Pure bounded state: conditions are evaluated by duck_expr outside this class.
namespace conditional_state {
static_assert(DUCKSCRIPT_MAX_BLOCK_DEPTH > 0 && DUCKSCRIPT_MAX_BLOCK_DEPTH < 256, "Invalid conditional depth limit");
class Stack {
  struct Frame { bool parent, active, taken, sawElse; };
  Frame frames[DUCKSCRIPT_MAX_BLOCK_DEPTH] = {};
  uint8_t depth = 0;
public:
  void clear() { depth = 0; }
  bool active() const { return !depth || frames[depth - 1].active; }
  bool enter(bool condition) {
    if (depth >= DUCKSCRIPT_MAX_BLOCK_DEPTH) return false;
    bool parent = active();
    frames[depth++] = {parent, parent && condition, parent && condition, false};
    return true;
  }
  bool eligible() const {
    return depth && frames[depth - 1].parent && !frames[depth - 1].taken && !frames[depth - 1].sawElse;
  }
  bool alternative(bool condition, bool finalElse) {
    if (!depth || frames[depth - 1].sawElse) return false;
    Frame &frame = frames[depth - 1];
    frame.active = eligible() && condition;
    frame.taken |= frame.active;
    frame.sawElse = finalElse;
    return true;
  }
  bool leave() { if (!depth) return false; --depth; return true; }
};
}
