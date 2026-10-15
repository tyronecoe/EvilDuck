#pragma once
#include "Arduino.h"
#include <memory>
#include <limits>

namespace mock {
inline size_t failReadAt = std::numeric_limits<size_t>::max();
inline size_t failSeekAt = std::numeric_limits<size_t>::max();
inline size_t bytesRead = 0, readCalls = 0, seekCalls = 0;
inline size_t sourceSizeIncrease = 0;
inline size_t readLimit = std::numeric_limits<size_t>::max();
}

class File {
  struct Handle { String content; size_t offset=0; bool open=true; };
  std::shared_ptr<Handle> handle;
  static inline std::weak_ptr<Handle> latest;
public:
  static bool opened(){auto p=latest.lock();return p&&p->open;}
  static void mutate(size_t i,char c){if(auto p=latest.lock()){if(i<p->content.length()){std::string s=p->content.c_str();s[i]=c;p->content=String(s);}}}
  File() = default;
  explicit File(const String &data) : handle(std::make_shared<Handle>()) { handle->content=data;latest=handle; }
  explicit operator bool() const { return handle && handle->open; }
  bool available() const { return bool(*this) && handle->offset < handle->content.length(); }
  size_t position() const { return handle ? handle->offset : 0; }
  size_t size() const { return handle ? handle->content.length() + mock::sourceSizeIncrease : 0; }
  bool isDirectory() const { return false; }
  bool seek(size_t position) {
    ++mock::seekCalls;
    if (!*this || position == mock::failSeekAt || position > handle->content.length()) return false;
    handle->offset=position; return true;
  }
  size_t read(uint8_t *buffer, size_t requested) {
    ++mock::readCalls;
    if (!*this || position() >= mock::failReadAt || position() > handle->content.length()) return 0;
    size_t count = std::min({mock::readLimit, requested, handle->content.length() - position(), mock::failReadAt - position()});
    memcpy(buffer, handle->content.c_str()+position(), count);
    handle->offset += count;
    mock::bytesRead += count;
    return count;
  }
  void close() { if(handle) handle->open=false; }
  String readStringUntil(char delimiter) {
    size_t start=position();
    while (available() && handle->content[handle->offset] != delimiter) ++handle->offset;
    String result=handle->content.substring(start,position());
    if(available()) ++handle->offset;
    return result;
  }
};
