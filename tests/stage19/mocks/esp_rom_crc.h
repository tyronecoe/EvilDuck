#pragma once
#include <cstdint>
#include <cstddef>
// ROM CRC API convention: complement on entry and exit, matching Python zlib.
inline uint32_t esp_rom_crc32_le(uint32_t initial,const uint8_t *p,size_t n) {
  uint32_t crc=~initial;
  for(size_t i=0;i<n;++i){crc^=p[i];for(unsigned j=0;j<8;++j)crc=(crc>>1)^((crc&1)?0xedb88320:0);}
  return ~crc;
}
