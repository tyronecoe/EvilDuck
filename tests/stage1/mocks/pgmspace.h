#pragma once
#include <cstdint>
inline uint8_t pgm_read_byte(const void *p) { return *static_cast<const uint8_t *>(p); }
