#include "script_source.h"
#include <algorithm>

namespace script_source {
Result Reader::fail(const char *message) { errorText = message; return Result::Error; }

bool Reader::begin(File &source) {
  file = &source;
  number = offset = nextRead = 0;
  length = chunkLength = chunkIndex = 0;
  cr = false;
  errorText = "";
  if (!source || source.isDirectory()) { fail("Storage open error"); return false; }
  expectedSize = source.size();
  if (expectedSize > DUCKSCRIPT_MAX_SOURCE_BYTES) { fail("Script source byte limit exceeded"); return false; }
  if (source.position() != 0 && !seek(0, 0)) return false;
  return true;
}

bool Reader::seek(uint32_t position, uint32_t previousLine) {
  if (!file || !*file || file->size() != expectedSize) { fail("Storage source changed or unavailable"); return false; }
  if (position > expectedSize || !file->seek(position) || file->position() != position) {
    fail("Storage seek error"); return false;
  }
  offset = nextRead = position;
  number = previousLine;
  length = chunkLength = chunkIndex = 0;
  cr = false;
  errorText = "";
  return true;
}

Result Reader::finish(String &line) {
  if (number >= DUCKSCRIPT_MAX_SOURCE_LINES) return fail("Script source line limit exceeded");
  buffer[length] = '\0';
  line = buffer;
  length = 0;
  ++number;
  return Result::Line;
}

Result Reader::next(String &line, uint16_t &budget) {
  if (errorText.length()) return Result::Error;
  if (!file || !*file || file->size() != expectedSize) return fail("Storage source changed or unavailable");
  while (budget) {
    if (offset == expectedSize) {
      if (cr) return fail("Bare CR: expected CRLF line ending");
      return length ? finish(line) : Result::End;
    }
    if (chunkIndex == chunkLength) {
      if (file->position() != nextRead) return fail("Storage read position error");
      uint32_t requested = std::min<uint32_t>(sizeof(chunk), expectedSize - nextRead);
      size_t got = file->read(chunk, requested);
      if (got != requested || file->position() != nextRead + requested) return fail("Storage read error before EOF");
      nextRead += got;
      chunkIndex = 0;
      chunkLength = got;
    }
    uint8_t byte = chunk[chunkIndex++];
    ++offset;
    --budget;
    // Inspect the first read chunk before adding BOM bytes to the line buffer,
    // so even a configured line limit smaller than three bytes stays correct.
    if (offset <= 3 && nextRead == chunkLength && chunkLength >= 3 &&
        chunk[0] == 0xEF && chunk[1] == 0xBB && chunk[2] == 0xBF) continue;
    if (byte == '\n') { cr = false; return finish(line); }
    if (cr) return fail("Bare CR: expected CRLF line ending");
    if (byte == '\r') { cr = true; continue; }
    if (!byte) return fail("NUL byte in script source");
    if (length >= DUCKSCRIPT_MAX_LINE_LEN) return fail("Script line length limit exceeded");
    buffer[length++] = char(byte);
  }
  return Result::Yield;
}
}
