#include "engine.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static unsigned assertions, groups;
static void check(int value, const char *message) {
    ++assertions;
    if (!value) { fprintf(stderr, "FAIL: %s\n", message); exit(1); }
}
struct fake {
    uint64_t now;
    unsigned writes, waits, progress, fail_at, cancel_wait, fail_clock;
    unsigned timeout_write, backwards_write, cancelled;
    int current[2], elements[1024], values[1024];
};
static int clock_ms(void *raw, uint64_t *out) {
    struct fake *f = raw;
    if (f->fail_clock) return 0;
    *out = f->now;
    return 1;
}
static int write_value(void *raw, enum mf_element which, int value) {
    struct fake *f = raw;
    check(f->writes < 1024, "bounded test write journal");
    check((which == MF_NUM || which == MF_CAPS) && (value == 0 || value == 1), "only Boolean Num/Caps writes");
    f->elements[f->writes] = which;
    f->values[f->writes++] = value;
    f->current[which] = value; /* Refusal deliberately may have changed state. */
    if (f->timeout_write == f->writes) f->now += MF_PHASE_MS;
    if (f->backwards_write == f->writes) f->now = 0;
    return f->fail_at != f->writes;
}
static int wait_ms(void *raw, unsigned ms) {
    struct fake *f = raw;
    check(ms == 100, "unchanged100ms settling boundary");
    ++f->waits;
    f->now += ms;
    if (f->cancel_wait == f->waits) { f->cancelled = 1; return 0; }
    return 1;
}
static int cancelled(void *raw) { return ((struct fake *)raw)->cancelled != 0; }
static void progress(void *raw, unsigned n) {
    struct fake *f = raw;
    check(n == f->progress + 1 && n <= 25, "one monotonic byte progress event");
    ++f->progress;
}
static void initialize(struct fake *f, struct mf_engine *e, int num, int caps) {
    memset(f, 0, sizeof(*f));
    f->now = 1000;
    f->current[MF_NUM] = num; f->current[MF_CAPS] = caps;
    struct mf_ops ops = {f, clock_ms, write_value, wait_ms, cancelled, progress};
    check(mf_init(e, &ops, num, caps) == MF_OK, "healthy initialization");
}
static void prove_probe(struct fake *f, struct mf_engine *e) {
    check(mf_probe_begin(e) == MF_OK, "probe begin");
    for (unsigned i = 0; i < 4; ++i) check(mf_probe_step(e) == MF_OK, "probe one step");
    struct mf_restore r = mf_restore_values(e);
    check(r.attempted && r.caps && r.num && !e->dirty && e->restored, "probe independently restored");
    check(f->current[MF_NUM] == e->saved[MF_NUM] && f->current[MF_CAPS] == e->saved[MF_CAPS], "saved state restored");
}
static void frame_vector(void) {
    static const uint8_t expected[25] = {
        0x00,0x45,0x44,0x52,0x31,0x11,0x45,0x56,0x49,0x4c,0x44,0x55,0x43,
        0x4b,0x20,0x54,0x45,0x53,0x54,0x20,0x31,0x32,0x33,0xd6,0xcc
    };
    uint8_t frame[25];
    mf_frame(frame);
    check(!memcmp(frame, expected, sizeof(frame)), "canonical exact25-byte EDR1 frame");
    check(mf_crc16(frame + 5, 18) == 0xd6cc, "length+payload CRC16-CCITT-FALSE");
    check(frame[5] == 17 && !memcmp(frame + 6, "EVILDUCK TEST 123", 17), "fixed17-byte message no terminator");
    check(mf_crc16((const uint8_t *)"123456789", 9) == 0x29b1, "independent standard CRC check value");
    ++groups;
}
static void selection_and_shapes(void) {
    check(mf_led_shape(1, 1, 1, 0, 1), "one Boolean ID1 LED output shape");
    check(!mf_led_shape(0, 1, 1, 0, 1), "ID0 shape rejected");
    check(!mf_led_shape(2, 1, 1, 0, 1), "wrong ID shape rejected");
    check(!mf_led_shape(1, 8, 1, 0, 1), "byte array not silently treated as Boolean");
    check(!mf_led_shape(1, 1, 2, 0, 1), "non-scalar output rejected");
    check(!mf_led_shape(1, 1, 1, -1, 1) && !mf_led_shape(1, 1, 1, 0, 2), "logical range validated");
    const char *serials[] = {"SYNTHETIC_A", "SYNTHETIC_B"};
    const int usable[] = {1, 1}; size_t selected = 99;
    check(mf_select_target(serials, usable, 2, "SYNTHETIC_B", &selected) && selected == 1, "exact target rather than first match");
    check(!mf_select_target(serials, usable, 2, "SYNTHETIC_C", &selected), "missing target rejected");
    check(!mf_select_target(serials, usable, 2, "", &selected), "blank selection rejected");
    check(!mf_select_target(serials, usable, 0, "SYNTHETIC_A", &selected), "no devices rejected");
    check(!mf_select_target(NULL, usable, 2, "SYNTHETIC_A", &selected), "null source rejected");
    const char *duplicate[] = {"SYNTHETIC_A", "SYNTHETIC_A"};
    const int mixed[] = {1, 0};
    check(!mf_select_target(duplicate, usable, 2, "SYNTHETIC_A", &selected), "duplicate supported interfaces rejected");
    check(!mf_select_target(duplicate, mixed, 2, "SYNTHETIC_A", &selected), "supported+unsupported duplicate rejected");
    check(!mf_serial_unique(serials, 17, 0), "oversize enumeration fails before access");
    check(!mf_serial_unique(serials, 2, 2), "out-of-range identity index rejected");
    ++groups;
}
static void invalid_arguments(void) {
    struct fake f = {0}; struct mf_engine e;
    struct mf_ops ops = {&f, clock_ms, write_value, wait_ms, cancelled, progress};
    check(mf_init(NULL, &ops, 0, 0) == MF_ARGUMENT, "null engine");
    check(mf_init(&e, NULL, 0, 0) == MF_ARGUMENT, "null operations");
    check(mf_init(&e, &ops, 2, 0) == MF_ARGUMENT, "invalid Num value");
    check(mf_init(&e, &ops, 0, -1) == MF_ARGUMENT, "invalid Caps value");
    ops.write_value = NULL;
    check(mf_init(&e, &ops, 0, 0) == MF_ARGUMENT, "missing writer rejected");
    ops.write_value = write_value; f.fail_clock = 1;
    check(mf_init(&e, &ops, 0, 0) == MF_CLOCK && f.writes == 0, "initial clock failure is read-only");
    ++groups;
}
static void gray_states(void) {
    for (int num = 0; num <= 1; ++num) for (int caps = 0; caps <= 1; ++caps) {
        struct fake f; struct mf_engine e;
        initialize(&f, &e, num, caps);
        check(mf_probe_begin(&e) == MF_OK, "single probe admitted");
        unsigned masks = 0;
        for (unsigned i = 0; i < 4; ++i) {
            check(mf_probe_step(&e) == MF_OK, "Gray step admitted");
            check(f.writes == i + 1 && e.probe_steps == i + 1, "one API attempt per step");
            masks |= 1u << (e.current[MF_NUM] | (e.current[MF_CAPS] << 1));
            check(f.elements[i] == (int)(i % 2 ? MF_CAPS : MF_NUM), "Num/Caps/Num/Caps ordering");
        }
        check(masks == 15, "both values of both outputs observed by planned probe");
        check(e.current[MF_NUM] == num && e.current[MF_CAPS] == caps, "Gray cycle returns to original values");
        check(mf_probe_step(&e) == MF_STATE && f.writes == 4, "fifth step rejected without write");
        check(mf_probe_begin(&e) == MF_STATE, "repeated probe rejected");
        struct mf_restore r = mf_restore_values(&e);
        check(r.caps && r.num && r.attempted && f.writes == 6, "independent two-write cleanup");
    }
    ++groups;
}
static void read_only_cleanup(void) {
    struct fake f; struct mf_engine e;
    initialize(&f, &e, 0, 1);
    struct mf_restore r = mf_restore_values(&e);
    check(!r.attempted && r.caps && r.num && f.writes == 0, "no cleanup writes without an attempted write");
    check(mf_send(&e) == MF_STATE && f.writes == 0, "no send before capability sequence");
    check(mf_probe_step(&e) == MF_STATE && f.writes == 0, "no step before explicit probe");
    ++groups;
}
static void all_probe_failures(void) {
    for (unsigned n = 1; n <= 4; ++n) {
        struct fake f; struct mf_engine e;
        initialize(&f, &e, 0, 1);
        check(mf_probe_begin(&e) == MF_OK, "begin injected probe");
        f.fail_at = n;
        for (unsigned step = 1; step <= n; ++step)
            check(mf_probe_step(&e) == (step == n ? MF_IO : MF_OK), "probe failure returned honestly");
        check(f.writes == n && e.dirty, "refusal has no ordinary retry");
        struct mf_restore r = mf_restore_values(&e);
        check(r.attempted && r.caps && r.num && f.writes == n + 2, "both cleanup writes after uncertain mutation");
    }
    ++groups;
}
static void successful_send(void) {
    struct fake f; struct mf_engine e;
    initialize(&f, &e, 1, 1); prove_probe(&f, &e);
    unsigned start = f.writes;
    uint64_t began = f.now;
    check(mf_send(&e) == MF_OK, "fixed frame API sequence finishes");
    check(f.writes - start == 402 && f.waits == 400 && f.progress == 25, "bounded full frame writes/waits/progress");
    check(f.now - began == 40000, "40-second ideal settling budget");
    check(f.elements[start] == MF_CAPS && f.values[start] == 0 &&
          f.elements[start + 1] == MF_NUM && f.values[start + 1] == 0, "explicit zero training initialization");
    uint8_t frame[25]; mf_frame(frame);
    for (unsigned i = 0; i < 200; ++i) {
        unsigned n = start + 2 + i * 2;
        check(f.elements[n] == MF_NUM && f.values[n] == ((frame[i / 8] >> (7 - i % 8)) & 1), "MSB-first data before clock");
        check(f.elements[n + 1] == MF_CAPS && f.values[n + 1] == (int)((i + 1) & 1), "one alternating Caps output clock per bit");
    }
    check(mf_send(&e) == MF_STATE && f.writes == start + 402, "no frame retransmit");
    struct mf_restore r = mf_restore_values(&e);
    check(r.caps && r.num && f.current[0] == 1 && f.current[1] == 1, "both original outputs restored after send");
    ++groups;
}
static void all_send_write_failures(void) {
    for (unsigned n = 1; n <= 402; ++n) {
        struct fake f; struct mf_engine e;
        initialize(&f, &e, 0, 1); prove_probe(&f, &e);
        unsigned before = f.writes;
        f.fail_at = before + n;
        check(mf_send(&e) == MF_IO && f.writes == before + n, "every send write refusal stops exactly once");
        struct mf_restore r = mf_restore_values(&e);
        check(r.caps && r.num && f.writes == before + n + 2, "independent restoration after every partial send");
        check(f.current[0] == 0 && f.current[1] == 1, "partial send cannot silently change final saved outputs");
    }
    ++groups;
}
static void cancellation_boundaries(void) {
    struct fake f; struct mf_engine e;
    initialize(&f, &e, 0, 0);
    f.cancelled = 1;
    check(mf_probe_begin(&e) == MF_CANCELLED && f.writes == 0, "cancel before probe produces no output");
    for (unsigned wait = 1; wait <= 400; ++wait) {
        initialize(&f, &e, 1, 0); prove_probe(&f, &e);
        unsigned before = f.writes;
        f.cancel_wait = wait;
        check(mf_send(&e) == MF_CANCELLED, "cancel at every wait propagated");
        check(f.writes == before + 2 + wait, "cancelled wait never allows next ordinary write");
        unsigned calls = f.writes;
        struct mf_restore r = mf_restore_values(&e);
        check(r.caps && r.num && f.writes == calls + 2, "cancellation does not suppress independent cleanup");
    }
    ++groups;
}
static void cleanup_failures(void) {
    for (unsigned which = 1; which <= 2; ++which) {
        struct fake f; struct mf_engine e;
        initialize(&f, &e, 1, 0);
        check(mf_probe_begin(&e) == MF_OK && mf_probe_step(&e) == MF_OK, "dirty initial state");
        unsigned before = f.writes;
        f.fail_at = before + which;
        f.cancelled = 1;
        struct mf_restore r = mf_restore_values(&e);
        check(r.attempted && f.writes == before + 2, "both cleanup operations attempted despite cancellation/failure");
        check(r.caps == (which != 1) && r.num == (which != 2), "each restore outcome accurate");
        check(e.dirty && !e.restored, "failed cleanup not fabricated as restored");
    }
    ++groups;
}
static void clock_and_deadlines(void) {
    struct fake f; struct mf_engine e;
    initialize(&f, &e, 0, 0);
    f.now += MF_OVERALL_MS;
    check(mf_poll(&e) == MF_TIMEOUT && f.writes == 0, "overall timeout at equality");
    initialize(&f, &e, 0, 0); check(mf_probe_begin(&e) == MF_OK, "probe before timeout");
    f.now += MF_PHASE_MS;
    check(mf_probe_step(&e) == MF_TIMEOUT && f.writes == 0, "probe phase timeout before write");
    initialize(&f, &e, 0, 0); prove_probe(&f, &e);
    unsigned before = f.writes; f.timeout_write = before + 1;
    check(mf_send(&e) == MF_TIMEOUT && f.writes == before + 1, "time limit after uncertain write stops next write");
    initialize(&f, &e, 0, 0); f.now = 999;
    check(mf_poll(&e) == MF_CLOCK && f.writes == 0, "backward monotonic clock rejected");
    initialize(&f, &e, 0, 0); f.fail_clock = 1;
    check(mf_probe_begin(&e) == MF_CLOCK && f.writes == 0, "clock read failure does not write");
    initialize(&f, &e, 0, 0); prove_probe(&f, &e);
    before = f.writes; f.backwards_write = before + 1;
    check(mf_send(&e) == MF_CLOCK && f.writes == before + 1, "clock regression during send stops immediately");
    ++groups;
}
int main(void) {
    frame_vector(); selection_and_shapes(); invalid_arguments(); gray_states(); read_only_cleanup();
    all_probe_failures(); successful_send(); all_send_write_failures();
    cancellation_boundaries(); cleanup_failures(); clock_and_deadlines();
    printf("{\"PASS\":%u,\"FAIL\":0,\"assertions\":%u,\"write_failure_boundaries\":402,\"cancel_wait_boundaries\":400,\"native_iokit\":\"NOT_EXECUTED\"}\n", groups, assertions);
    return 0;
}
