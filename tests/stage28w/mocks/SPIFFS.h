#pragma once
#include "SD.h"
#include <stdexcept>
namespace fsMock {inline bool mountOk=true,interrupted=false;inline unsigned mounts=0,formats=0;inline bool formatRequested=false;inline bool(*settingsReady)()=nullptr;}
class SPIFFSClass:public SDClass {
public:
 bool begin(bool format){++fsMock::mounts;fsMock::formatRequested=format;if(fsMock::settingsReady&&!fsMock::settingsReady())throw std::runtime_error("mount before validated settings");if(fsMock::interrupted)throw std::runtime_error("simulated interrupted mount");if(!fsMock::mountOk&&format){++fsMock::formats;return true;}return fsMock::mountOk;}
 bool format(){++fsMock::formats;return true;}
};
inline SPIFFSClass SPIFFS;
