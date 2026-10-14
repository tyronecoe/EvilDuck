// Metadata-only unlinked object. Never a firmware image or executable entry.
#include "journal_driver.h"
extern "C" const uint32_t stage28k_sizes[] __attribute__((used,section(".stage28k_sizes")))={
 sizeof(stage28k::Driver),sizeof(stage28k::Record),sizeof(stage28k::IntentRecord),
 sizeof(stage28k::Request),sizeof(stage28k::Diagnostic),sizeof(stage28k::Counters),
 sizeof(stage28k::Work),sizeof(ds_preview::MemoryReader)
};
