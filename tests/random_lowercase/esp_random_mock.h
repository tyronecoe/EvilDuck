#pragma once
#include <stdint.h>
#include <vector>
namespace rng_mock {
inline std::vector<uint32_t> values;
inline size_t calls=0;
inline uint32_t fallback=0;
inline void reset(){values.clear();calls=0;fallback=0;}
}
#define esp_random random_character_test_draw
inline uint32_t random_character_test_draw(){auto n=rng_mock::calls++;return n<rng_mock::values.size()?rng_mock::values[n]:rng_mock::fallback;}
