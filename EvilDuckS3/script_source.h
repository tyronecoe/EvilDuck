#pragma once
#include <Arduino.h>
#include <FS.h>
#include "config.h"

namespace script_source {
static_assert(DUCKSCRIPT_MAX_LINE_LEN > 0 && DUCKSCRIPT_MAX_LINE_LEN <= 65535, "Line limit must fit the bounded reader");
enum class Result { Yield, Line, End, Error };

// Streaming reader: one bounded line and one small read-ahead buffer, regardless
// of script size/volume. No Stream::readStringUntil timeout or silent truncation.
class Reader {
  File *file = nullptr;
  uint32_t expectedSize = 0, offset = 0, nextRead = 0, number = 0;
  uint32_t lineStart = 0, completedLineStart = 0;
  char buffer[DUCKSCRIPT_MAX_LINE_LEN + 1] = {};
  uint8_t chunk[64] = {};
  uint16_t length = 0;
  uint8_t chunkLength = 0, chunkIndex = 0;
  bool cr = false;
  String errorText;
  Result fail(const char *message);
  Result finish(String &line);
public:
  bool begin(File &source);
  bool seek(uint32_t position, uint32_t previousLine);
  Result next(String &line, uint16_t &budget);
  uint32_t position() const { return offset; }
  uint32_t lineNumber() const { return number; }
  uint32_t lineStartPosition() const { return completedLineStart; }
  uint32_t errorLine() const { return number + 1; }
  String error() const { return errorText; }
};
}
