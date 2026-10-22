/* Foreground fixed-message worker. No key input, raw report packing or device seizure. */
#ifndef __APPLE__
#error Native IOKit helper requires the Apple SDK; Linux engine tests are not native macOS validation.
#else
#include "engine.h"
#include <CoreFoundation/CoreFoundation.h>
#include <IOKit/hid/IOHIDManager.h>
#include <IOKit/hid/IOHIDKeys.h>
#include <errno.h>
#include <signal.h>
#include <stdio.h>
#include <string.h>
#include <sys/select.h>
#include <time.h>
#include <unistd.h>

enum { MAX_DEVICES = 16, MAX_ELEMENTS = 2048, SERIAL_BYTES = 256, COMMAND_BYTES = 32 };
struct candidate {
    IOHIDDeviceRef device;
    CFArrayRef elements;
    IOHIDElementRef num, caps;
    char serial[SERIAL_BYTES];
    const char *reason;
    int usable, old_num, old_caps;
};
static volatile sig_atomic_t interrupted;
static void interrupt_handler(int signum) { (void)signum; interrupted = 1; }
static void watchdog_handler(int signum) {
    (void)signum;
    static const char message[] = "{\"event\":\"error\",\"code\":\"WATCHDOG_EXIT_RESTORATION_UNCONFIRMED\"}\n";
    (void)write(STDERR_FILENO, message, sizeof(message) - 1);
    _exit(124); /* Forced exit is not a successful cleanup or a real-time guarantee. */
}
static int emit(const char *event) {
    int ok = puts(event) >= 0 && fflush(stdout) == 0;
    if (!ok) interrupted = 1;
    return ok;
}
static void json_string(const char *s) {
    putchar('"');
    for (const unsigned char *p = (const unsigned char *)s; *p; ++p) {
        if (*p == '"' || *p == '\\') { putchar('\\'); putchar(*p); }
        else if (*p < 32) printf("\\u%04x", (unsigned)*p);
        else putchar(*p);
    }
    putchar('"');
}
static int get_integer(IOHIDDeviceRef device, CFStringRef key, int32_t *out) {
    CFTypeRef p = IOHIDDeviceGetProperty(device, key);
    return p && CFGetTypeID(p) == CFNumberGetTypeID() &&
           CFNumberGetValue((CFNumberRef)p, kCFNumberSInt32Type, out);
}
static int get_serial(IOHIDDeviceRef device, char *out) {
    CFTypeRef p = IOHIDDeviceGetProperty(device, CFSTR(kIOHIDSerialNumberKey));
    out[0] = 0;
    if (!p || CFGetTypeID(p) != CFStringGetTypeID()) return 0;
    CFIndex length = CFStringGetLength((CFStringRef)p);
    if (length < 1 || length >= SERIAL_BYTES) return 0;
    for (CFIndex i = 0; i < length; ++i) {
        UniChar ch = CFStringGetCharacterAtIndex((CFStringRef)p, i);
        if (ch < 32 || ch == 127) return 0;
    }
    if (!CFStringGetCString((CFStringRef)p, out, SERIAL_BYTES, kCFStringEncodingUTF8)) {
        out[0] = 0;
        return 0;
    }
    return 1;
}
static int read_value(IOHIDDeviceRef device, IOHIDElementRef element, int *out) {
    IOHIDValueRef value = NULL;
    if (IOHIDDeviceGetValue(device, element, &value) != kIOReturnSuccess || !value) return 0;
    CFIndex n = IOHIDValueGetIntegerValue(value);
    if (n != 0 && n != 1) return 0;
    *out = (int)n;
    return 1;
}
static int valid_element(IOHIDElementRef e) {
    return mf_led_shape(IOHIDElementGetReportID(e), IOHIDElementGetReportSize(e),
                        IOHIDElementGetReportCount(e), IOHIDElementGetLogicalMin(e),
                        IOHIDElementGetLogicalMax(e));
}
static void inspect(struct candidate *c, IOHIDDeviceRef device) {
    memset(c, 0, sizeof(*c));
    c->device = device;
    c->reason = "UNSUPPORTED_DEVICE";
    int32_t vendor = 0, product = 0;
    if (!get_integer(device, CFSTR(kIOHIDVendorIDKey), &vendor) ||
        !get_integer(device, CFSTR(kIOHIDProductIDKey), &product) ||
        vendor != 0x303a || product != 0x1001) return;
    if (!get_serial(device, c->serial)) { c->reason = "MISSING_OR_INVALID_SERIAL"; return; }
    if (!IOHIDDeviceConformsTo(device, 1, 6)) { c->reason = "NOT_KEYBOARD_INTERFACE"; return; }
    c->elements = IOHIDDeviceCopyMatchingElements(device, NULL, kIOHIDOptionsTypeNone);
    if (!c->elements) { c->reason = "ELEMENT_ENUMERATION_FAILED"; return; }
    CFIndex count = CFArrayGetCount(c->elements);
    if (count > MAX_ELEMENTS) { c->reason = "ELEMENT_LIMIT"; return; }
    unsigned nums = 0, caps = 0;
    int valid = 1;
    for (CFIndex i = 0; i < count; ++i) {
        IOHIDElementRef e = (IOHIDElementRef)CFArrayGetValueAtIndex(c->elements, i);
        if (IOHIDElementGetType(e) != kIOHIDElementTypeOutput || IOHIDElementGetUsagePage(e) != 8) continue;
        uint32_t usage = IOHIDElementGetUsage(e);
        if (usage == 1) { ++nums; c->num = e; valid = valid && valid_element(e); }
        if (usage == 2) { ++caps; c->caps = e; valid = valid && valid_element(e); }
    }
    if (nums != 1 || caps != 1) { c->reason = "MISSING_OR_AMBIGUOUS_NUM_CAPS_ELEMENTS"; return; }
    if (!valid) { c->reason = "UNSUPPORTED_LED_ELEMENT_SHAPE"; return; }
    if (!read_value(device, c->num, &c->old_num) || !read_value(device, c->caps, &c->old_caps)) {
        c->reason = "INITIAL_OUTPUT_VALUES_UNAVAILABLE"; return;
    }
    c->usable = 1;
    c->reason = "READY_FOR_EXPLICIT_PROBE";
}
static IOHIDManagerRef manager_create(void) {
    IOHIDManagerRef manager = IOHIDManagerCreate(kCFAllocatorDefault, kIOHIDOptionsTypeNone);
    if (!manager) return NULL;
    int32_t vendor = 0x303a, product = 0x1001;
    CFNumberRef vn = CFNumberCreate(NULL, kCFNumberSInt32Type, &vendor);
    CFNumberRef pn = CFNumberCreate(NULL, kCFNumberSInt32Type, &product);
    if (!vn || !pn) { if (vn) CFRelease(vn); if (pn) CFRelease(pn); CFRelease(manager); return NULL; }
    const void *keys[] = {CFSTR(kIOHIDVendorIDKey), CFSTR(kIOHIDProductIDKey)};
    const void *values[] = {vn, pn};
    CFDictionaryRef matching = CFDictionaryCreate(NULL, keys, values, 2,
                                   &kCFTypeDictionaryKeyCallBacks, &kCFTypeDictionaryValueCallBacks);
    CFRelease(vn); CFRelease(pn);
    if (!matching) { CFRelease(manager); return NULL; }
    IOHIDManagerSetDeviceMatching(manager, matching);
    CFRelease(matching);
    return manager;
}
static int now_ms(void *context, uint64_t *out) {
    (void)context;
    struct timespec t;
    if (clock_gettime(CLOCK_MONOTONIC, &t) || t.tv_sec < 0) return 0;
    *out = (uint64_t)t.tv_sec * UINT64_C(1000) + (uint64_t)t.tv_nsec / UINT64_C(1000000);
    return 1;
}
static int cancelled(void *context) { (void)context; return interrupted != 0; }
static int write_value(void *context, enum mf_element which, int value) {
    struct candidate *c = context;
    IOHIDElementRef e = which == MF_CAPS ? c->caps : c->num;
    IOHIDValueRef v = IOHIDValueCreateWithIntegerValue(kCFAllocatorDefault, e, 0, value);
    if (!v) return 0;
    IOReturn result = IOHIDDeviceSetValue(c->device, e, v);
    CFRelease(v);
    return result == kIOReturnSuccess;
}
static int wait_ms(void *context, unsigned milliseconds) {
    (void)context;
    struct timespec remaining = {(time_t)(milliseconds / 1000), (long)(milliseconds % 1000) * 1000000L};
    while (nanosleep(&remaining, &remaining)) {
        if (interrupted || errno != EINTR) return 0;
    }
    return !interrupted;
}
static void progress(void *context, unsigned bytes) {
    (void)context;
    if (printf("{\"event\":\"progress\",\"bytes\":%u,\"total\":25}\n", bytes) < 0 || fflush(stdout)) interrupted = 1;
}
static void emit_error(const char *name) {
    printf("{\"event\":\"error\",\"code\":\"%s\"}\n", name);
    (void)fflush(stdout);
}
static struct mf_restore restore(struct mf_engine *e) {
    alarm(95);
    struct mf_restore r = mf_restore_values(e);
    alarm(0);
    printf("{\"event\":\"restored\",\"caps\":%s,\"num\":%s,\"attempted\":%s}\n",
           r.caps ? "true" : "false", r.num ? "true" : "false", r.attempted ? "true" : "false");
    (void)fflush(stdout);
    return r;
}
static int command(struct mf_engine *e, char *line, size_t capacity) {
    size_t used = 0;
    for (;;) {
        if (mf_poll(e) != MF_OK) return -1;
        fd_set input;
        FD_ZERO(&input); FD_SET(STDIN_FILENO, &input);
        struct timeval timeout = {0, 100000};
        int ready = select(STDIN_FILENO + 1, &input, NULL, NULL, &timeout);
        if (ready < 0) { if (errno == EINTR) continue; return -1; }
        if (!ready) continue;
        char ch;
        ssize_t got = read(STDIN_FILENO, &ch, 1);
        if (got == 0) return used ? -1 : 0;
        if (got < 0) { if (errno == EINTR) continue; return -1; }
        if (ch == '\n') { line[used] = 0; return 1; }
        if (ch < 32 || (unsigned char)ch == 127 || used + 1 >= capacity) return -1;
        line[used++] = ch;
    }
}
static int worker(struct candidate *c) {
    struct mf_ops ops = {c, now_ms, write_value, wait_ms, cancelled, progress};
    struct mf_engine engine;
    enum mf_status status = mf_init(&engine, &ops, c->old_num, c->old_caps);
    if (status != MF_OK) { emit_error(mf_status_name(status)); return 1; }
    printf("{\"event\":\"ready\",\"num\":%d,\"caps\":%d,\"reportId\":1}\n", c->old_num, c->old_caps);
    if (fflush(stdout)) return 1;
    int result = 0, restoration_attempted = 0;
    for (unsigned commands = 0; commands < 32; ++commands) {
        char line[COMMAND_BYTES];
        int got = command(&engine, line, sizeof(line));
        if (got <= 0) {
            if (got < 0) { status = mf_poll(&engine); emit_error(status == MF_OK ? "INVALID_OR_INCOMPLETE_COMMAND" : mf_status_name(status)); result = 1; }
            break;
        }
        if (!strcmp(line, "QUIT")) break;
        if (!strcmp(line, "PROBE")) {
            status = mf_probe_begin(&engine);
            if (status == MF_OK) emit("{\"event\":\"probe_ready\"}");
        } else if (!strcmp(line, "STEP")) {
            restoration_attempted = 0;
            alarm(95);
            status = mf_probe_step(&engine);
            alarm(0);
            if (status == MF_OK) {
                printf("{\"event\":\"probe_step\",\"index\":%u,\"num\":%d,\"caps\":%d,\"ok\":true}\n",
                       engine.probe_steps, engine.current[MF_NUM], engine.current[MF_CAPS]);
                if (fflush(stdout)) { interrupted = 1; status = MF_CANCELLED; }
            }
        } else if (!strcmp(line, "SEND")) {
            restoration_attempted = 0;
            alarm(95);
            status = mf_send(&engine);
            alarm(0);
            if (status == MF_OK) emit("{\"event\":\"frame_api_finished\",\"ok\":true}");
        } else if (!strcmp(line, "RESTORE")) {
            restoration_attempted = 1;
            struct mf_restore r = restore(&engine);
            status = r.caps && r.num ? MF_OK : MF_IO;
        } else status = MF_ARGUMENT;
        if (status != MF_OK) { emit_error(mf_status_name(status)); result = 1; break; }
        if (commands == 31) { emit_error("COMMAND_LIMIT"); result = 1; }
    }
    if (engine.dirty && !restoration_attempted) {
        struct mf_restore r = restore(&engine);
        if (!r.caps || !r.num) result = 1;
    }
    return result;
}
int main(int argc, char **argv) {
    int check = argc == 2 && !strcmp(argv[1], "--check");
    int run = argc == 3 && !strcmp(argv[1], "--worker") && argv[2][0] && strlen(argv[2]) < SERIAL_BYTES;
    if (!check && !run) { fputs("Use the guided run-mac.sh launcher, or --check for read-only identification.\n", stderr); return 2; }
    signal(SIGINT, interrupt_handler); signal(SIGTERM, interrupt_handler);
    signal(SIGALRM, watchdog_handler); signal(SIGPIPE, SIG_IGN);
    alarm(95); /* Also bounds synchronous discovery calls on a best-effort basis. */
    int result = 1, opened = 0;
    IOHIDManagerRef manager = manager_create();
    CFSetRef devices = NULL;
    struct candidate candidates[MAX_DEVICES];
    memset(candidates, 0, sizeof(candidates));
    CFIndex count = 0;
    if (!manager) { emit_error("ALLOCATION_FAILURE"); goto done; }
    if (IOHIDManagerOpen(manager, kIOHIDOptionsTypeNone) != kIOReturnSuccess) {
        emit_error("IOKIT_OPEN_REFUSED"); goto done;
    }
    opened = 1;
    devices = IOHIDManagerCopyDevices(manager);
    if (!devices) {
        if (check) result = emit("{\"devices\":[]}") ? 0 : 1;
        else emit_error("SELECTED_TARGET_MISSING_OR_ENUMERATION_UNAVAILABLE");
        goto done;
    }
    count = CFSetGetCount(devices);
    if (count > MAX_DEVICES) { emit_error("DEVICE_LIMIT_OR_AMBIGUITY"); goto done; }
    const void *values[MAX_DEVICES];
    CFSetGetValues(devices, values);
    for (CFIndex i = 0; i < count; ++i) inspect(&candidates[i], (IOHIDDeviceRef)values[i]);
    const char *serials[MAX_DEVICES];
    int usable[MAX_DEVICES];
    for (CFIndex i = 0; i < count; ++i) serials[i] = candidates[i].serial;
    for (CFIndex i = 0; i < count; ++i) {
        if (candidates[i].serial[0] && !mf_serial_unique(serials, (size_t)count, (size_t)i)) {
            candidates[i].usable = 0;
            candidates[i].reason = "AMBIGUOUS_SERIAL";
        }
        usable[i] = candidates[i].usable;
    }
    alarm(0);
    if (check) {
        printf("{\"devices\":[");
        for (CFIndex i = 0; i < count; ++i) {
            struct candidate *c = &candidates[i];
            if (i) putchar(',');
            printf("{\"serial\":"); json_string(c->serial);
            printf(",\"usable\":%s,\"reason\":\"%s\",\"reportId\":%d}", c->usable ? "true" : "false", c->reason, c->usable ? 1 : 0);
        }
        printf("]}\n");
        result = fflush(stdout) ? 1 : 0;
    } else {
        size_t selected = 0;
        if (!mf_select_target(serials, usable, (size_t)count, argv[2], &selected))
            emit_error("SELECTED_TARGET_MISSING_AMBIGUOUS_OR_UNSUPPORTED");
        else result = worker(&candidates[selected]);
    }
done:
    alarm(0);
    for (CFIndex i = 0; i < count && i < MAX_DEVICES; ++i)
        if (candidates[i].elements) CFRelease(candidates[i].elements);
    if (devices) CFRelease(devices);
    if (manager) { if (opened) IOHIDManagerClose(manager, kIOHIDOptionsTypeNone); CFRelease(manager); }
    return result;
}
#endif
