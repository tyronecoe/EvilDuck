#pragma once
#include "script_parser.h"

namespace script_preprocessor {
// One bit per bounded physical line. No source text or AST is retained, and
// membership is invariant across arbitrary function/WHILE reader seeks.
class Filter {
  struct Frame { uint32_t line; bool parent, selected, sawElse; };
  Frame frames[DUCKSCRIPT_MAX_PREPROCESS_DEPTH] = {};
  uint8_t depth = 0;
  uint8_t included[(DUCKSCRIPT_MAX_SOURCE_LINES + 7) / 8] = {};
  char extensions[DUCKSCRIPT_MAX_EXTENSIONS][DUCKSCRIPT_MAX_IDENTIFIER_LEN + 1] = {};
  uint8_t extensionCount = 0, extensionDepth = 0;
  bool extension = false, extensionIncluded = false, versionSeen = false, contentSeen = false;
  uint32_t extensionLine = 0;
  script_parser::RawBlocks blocks;
  bool active() const { return !depth || frames[depth - 1].selected; }
public:
  static_assert(DUCKSCRIPT_MAX_PREPROCESS_DEPTH > 0 && DUCKSCRIPT_MAX_PREPROCESS_DEPTH < 256, "Invalid preprocessing depth");
  static_assert(DUCKSCRIPT_MAX_EXTENSIONS > 0 && DUCKSCRIPT_MAX_EXTENSIONS < 256, "Invalid extension limit");
  bool accept(const String &line, uint32_t number, String &error);
  bool finish(String &error, uint32_t &number) const;
  bool contains(uint32_t number) const {
    return number && number <= DUCKSCRIPT_MAX_SOURCE_LINES &&
      (included[(number - 1) / 8] & (1U << ((number - 1) % 8)));
  }
};
}
