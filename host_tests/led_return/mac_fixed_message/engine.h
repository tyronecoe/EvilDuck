#ifndef MF_ENGINE_H
#define MF_ENGINE_H
#include <stddef.h>
#include <stdint.h>

enum mf_element { MF_NUM = 0, MF_CAPS = 1 };
enum mf_status { MF_OK = 0, MF_ARGUMENT, MF_STATE, MF_IO, MF_CLOCK, MF_CANCELLED, MF_TIMEOUT };
enum { MF_FRAME_BYTES = 25, MF_SETTLE_MS = 100 };
#define MF_OVERALL_MS UINT64_C(600000)
#define MF_PHASE_MS UINT64_C(90000)

struct mf_ops {
    void *context;
    int (*now_ms)(void *, uint64_t *);
    int (*write_value)(void *, enum mf_element, int);
    int (*wait_ms)(void *, unsigned);
    int (*cancelled)(void *);
    void (*progress)(void *, unsigned);
};
struct mf_engine {
    struct mf_ops ops;
    uint64_t began, last, phase;
    int saved[2], current[2];
    unsigned probe_steps;
    int probe_started, probe_finished, restored, send_attempted, dirty;
};
struct mf_restore { int attempted, caps, num; };

uint16_t mf_crc16(const uint8_t *, size_t);
void mf_frame(uint8_t frame[MF_FRAME_BYTES]);
int mf_led_shape(uint32_t report_id, uint32_t bits, uint32_t count, int64_t minimum, int64_t maximum);
int mf_serial_unique(const char *const *serials, size_t count, size_t index);
int mf_select_target(const char *const *serials, const int *usable, size_t count, const char *wanted, size_t *index);
const char *mf_status_name(enum mf_status);
enum mf_status mf_init(struct mf_engine *, const struct mf_ops *, int num, int caps);
enum mf_status mf_poll(struct mf_engine *);
enum mf_status mf_probe_begin(struct mf_engine *);
enum mf_status mf_probe_step(struct mf_engine *);
enum mf_status mf_send(struct mf_engine *);
struct mf_restore mf_restore_values(struct mf_engine *);
#endif
