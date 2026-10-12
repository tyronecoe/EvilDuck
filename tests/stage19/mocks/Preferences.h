#pragma once
#include "Arduino.h"
extern unsigned mocked_writes;
extern bool save_open_ok;
class Preferences {
public:
 bool begin(const char*,bool){return save_open_ok;}
 void end(){}
 size_t putBool(const char*,bool){++mocked_writes;return 1;}
 size_t putString(const char*,const String&s){++mocked_writes;return s.length();}
 size_t putUChar(const char*,uint8_t){++mocked_writes;return 1;}
 size_t putUShort(const char*,uint16_t){++mocked_writes;return 2;}
 size_t putUInt(const char*,uint32_t){++mocked_writes;return 4;}
};
