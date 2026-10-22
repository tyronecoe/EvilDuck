/* Shared execution logic. Native IOKit and offline fake operations use this file. */
#include "engine.h"
#include <string.h>

int mf_led_shape(uint32_t report_id, uint32_t bits, uint32_t count, int64_t minimum, int64_t maximum) {
    return report_id == 1 && bits == 1 && count == 1 && minimum == 0 && maximum == 1;
}
int mf_serial_unique(const char *const *serials, size_t count, size_t index) {
    if (!serials || count > 16 || index >= count || !serials[index] || !serials[index][0]) return 0;
    for (size_t i = 0; i < count; ++i)
        if (i != index && serials[i] && !strcmp(serials[index], serials[i])) return 0;
    return 1;
}
int mf_select_target(const char *const *serials, const int *usable, size_t count, const char *wanted, size_t *index) {
    if (!serials || !usable || !wanted || !wanted[0] || !index || count > 16) return 0;
    for (size_t i = 0; i < count; ++i) {
        if (usable[i] && serials[i] && !strcmp(serials[i], wanted) && mf_serial_unique(serials, count, i)) {
            *index = i;
            return 1;
        }
    }
    return 0;
}
uint16_t mf_crc16(const uint8_t *p, size_t n) {
    uint16_t crc = UINT16_C(0xffff);
    for (size_t i = 0; i < n; ++i) {
        crc ^= (uint16_t)((uint16_t)p[i] << 8);
        for (unsigned bit = 0; bit < 8; ++bit)
            crc = (uint16_t)((crc & UINT16_C(0x8000)) ?
                  ((uint32_t)crc << 1) ^ UINT32_C(0x1021) : (uint32_t)crc << 1);
    }
    return crc;
}
void mf_frame(uint8_t frame[MF_FRAME_BYTES]) {
    static const uint8_t fixed[] = "EVILDUCK TEST 123";
    _Static_assert(sizeof(fixed) == 18, "fixed payload is exactly17 bytes");
    frame[0] = 0;
    memcpy(frame + 1, "EDR1", 4);
    frame[5] = 17;
    memcpy(frame + 6, fixed, 17);
    uint16_t crc = mf_crc16(frame + 5, 18);
    frame[23] = (uint8_t)(crc >> 8);
    frame[24] = (uint8_t)crc;
}
const char *mf_status_name(enum mf_status s) {
    static const char *const names[] = {
        "OK", "INVALID_ARGUMENT", "INVALID_STATE", "IOKIT_WRITE_REFUSED",
        "CLOCK_FAILURE", "CANCELLED", "TIMEOUT"
    };
    return (unsigned)s < sizeof(names) / sizeof(names[0]) ? names[s] : "UNKNOWN_ERROR";
}
enum mf_status mf_init(struct mf_engine *e, const struct mf_ops *ops, int num, int caps) {
    if (!e || !ops || !ops->now_ms || !ops->write_value || !ops->wait_ms ||
        !ops->cancelled || (num != 0 && num != 1) || (caps != 0 && caps != 1)) return MF_ARGUMENT;
    memset(e, 0, sizeof(*e));
    e->ops = *ops;
    e->saved[MF_NUM] = e->current[MF_NUM] = num;
    e->saved[MF_CAPS] = e->current[MF_CAPS] = caps;
    if (!ops->now_ms(ops->context, &e->began)) return MF_CLOCK;
    e->last = e->began;
    return MF_OK;
}
enum mf_status mf_poll(struct mf_engine *e) {
    uint64_t now;
    if (e->ops.cancelled(e->ops.context)) return MF_CANCELLED;
    if (!e->ops.now_ms(e->ops.context, &now) || now < e->last) return MF_CLOCK;
    e->last = now;
    if (now - e->began >= MF_OVERALL_MS) return MF_TIMEOUT;
    return MF_OK;
}
static enum mf_status active(struct mf_engine *e) {
    enum mf_status s = mf_poll(e);
    if (s != MF_OK) return s;
    return e->last - e->phase >= MF_PHASE_MS ? MF_TIMEOUT : MF_OK;
}
static enum mf_status ordinary_write(struct mf_engine *e, enum mf_element which, int value) {
    enum mf_status s = active(e);
    if (s != MF_OK) return s;
    e->dirty = 1; /* Even a refused/uncertain API write warrants best-effort restoration. */
    e->restored = 0;
    if (!e->ops.write_value(e->ops.context, which, value)) return MF_IO;
    e->current[which] = value;
    return active(e);
}
static enum mf_status settle(struct mf_engine *e) {
    enum mf_status s = active(e);
    if (s != MF_OK) return s;
    if (!e->ops.wait_ms(e->ops.context, MF_SETTLE_MS)) {
        s = active(e);
        return s == MF_OK ? MF_CLOCK : s;
    }
    return active(e); /* A cancelled/interrupted wait must not clock another bit. */
}
enum mf_status mf_probe_begin(struct mf_engine *e) {
    enum mf_status s = mf_poll(e);
    if (s != MF_OK) return s;
    if (e->probe_started || e->send_attempted || e->dirty) return MF_STATE;
    e->probe_started = 1;
    e->phase = e->last;
    return MF_OK;
}
enum mf_status mf_probe_step(struct mf_engine *e) {
    if (!e->probe_started || e->probe_finished || e->probe_steps >= 4 || e->send_attempted) return MF_STATE;
    enum mf_element which = e->probe_steps % 2 ? MF_CAPS : MF_NUM;
    enum mf_status s = ordinary_write(e, which, e->current[which] ^ 1);
    if (s != MF_OK) return s;
    ++e->probe_steps;
    if (e->probe_steps == 4) e->probe_finished = 1;
    return MF_OK;
}
enum mf_status mf_send(struct mf_engine *e) {
    enum mf_status s = mf_poll(e);
    if (s != MF_OK) return s;
    if (!e->probe_finished || !e->restored || e->dirty || e->send_attempted) return MF_STATE;
    e->send_attempted = 1;
    e->phase = e->last;
    uint8_t frame[MF_FRAME_BYTES];
    mf_frame(frame);
    s = ordinary_write(e, MF_CAPS, 0);
    if (s != MF_OK) return s;
    s = ordinary_write(e, MF_NUM, 0);
    if (s != MF_OK) return s;
    int clock = 0;
    for (size_t i = 0; i < sizeof(frame); ++i) {
        for (int bit = 7; bit >= 0; --bit) {
            s = ordinary_write(e, MF_NUM, (frame[i] >> bit) & 1);
            if (s != MF_OK) return s;
            s = settle(e);
            if (s != MF_OK) return s;
            clock ^= 1;
            s = ordinary_write(e, MF_CAPS, clock);
            if (s != MF_OK) return s;
            s = settle(e);
            if (s != MF_OK) return s;
        }
        if (e->ops.progress) e->ops.progress(e->ops.context, (unsigned)i + 1);
    }
    return MF_OK;
}
struct mf_restore mf_restore_values(struct mf_engine *e) {
    struct mf_restore r = {e->dirty, 1, 1};
    if (!e->dirty) return r; /* Identification/check never produces cleanup writes. */
    /* Deliberately do not short-circuit, consult cancellation or fabricate success. */
    r.caps = e->ops.write_value(e->ops.context, MF_CAPS, e->saved[MF_CAPS]);
    r.num = e->ops.write_value(e->ops.context, MF_NUM, e->saved[MF_NUM]);
    if (r.caps && r.num) {
        e->current[MF_CAPS] = e->saved[MF_CAPS];
        e->current[MF_NUM] = e->saved[MF_NUM];
        e->dirty = 0;
        e->restored = 1;
    }
    return r;
}
