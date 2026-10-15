#pragma once
#include <stdint.h>
#include "Arduino.h"
#define NEO_GRB 0
#define NEO_KHZ800 0
namespace pixelMock {inline unsigned begins=0,shows=0;}
class Adafruit_NeoPixel{public:Adafruit_NeoPixel(int,int,int){}void begin(){++pixelMock::begins;}void setBrightness(int){}void show(){++pixelMock::shows;}uint32_t Color(uint8_t r,uint8_t g,uint8_t b){return (r<<16)|(g<<8)|b;}void setPixelColor(int,uint32_t){}static uint8_t gamma8(uint8_t v){return v;}};
