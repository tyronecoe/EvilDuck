// Iterator adapter has no heap; actual ownership is tested separately.
static void esp_partition_iterator_release(const void*) {}
#include "../stage21/nvs_readonly.cpp"
