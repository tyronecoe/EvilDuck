/* Foreground passive IOHID observer: Caps/modifiers only, two explicit services.
 * No event injection, set-report/value, persistence, key text or serial collection.
 */
#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
static int allowed(uint32_t vendor,uint32_t product,uint32_t page,uint32_t usage){
 return ((vendor==0x303a&&product==0x1001)||(vendor==0x05ac&&product==0x0259))&&page==7&&(usage==0x39||(usage>=0xe0&&usage<=0xe7));
}
#ifdef FILTER_TEST
int main(void){int ok=allowed(0x303a,0x1001,7,0x39)&&allowed(0x05ac,0x0259,7,0xe1)&&!allowed(0x303a,0x1001,7,4)&&!allowed(0x1234,0x5678,7,0x39)&&!allowed(0x303a,0x1001,8,2)&&!allowed(0x303a,0x1001,7,0);puts(ok?"PASS six privacy-filter vectors":"FAIL privacy filter");return !ok;}
#elif defined(__APPLE__)
#include <CoreFoundation/CoreFoundation.h>
#include <IOKit/hid/IOHIDManager.h>
#include <mach/mach_time.h>
struct Context{unsigned observed;uint64_t start;mach_timebase_info_data_t scale;};
static uint32_t number(IOHIDDeviceRef d,CFStringRef key){CFTypeRef v=IOHIDDeviceGetProperty(d,key);int32_t n=0;if(v&&CFGetTypeID(v)==CFNumberGetTypeID())CFNumberGetValue((CFNumberRef)v,kCFNumberSInt32Type,&n);return (uint32_t)n;}
static void value(void* raw,IOReturn result,void* sender,IOHIDValueRef v){
 (void)sender;if(result!=kIOReturnSuccess||!v)return;struct Context* c=raw;IOHIDElementRef e=IOHIDValueGetElement(v);IOHIDDeviceRef d=IOHIDElementGetDevice(e);
 uint32_t vendor=number(d,CFSTR(kIOHIDVendorIDKey)),product=number(d,CFSTR(kIOHIDProductIDKey));uint32_t page=IOHIDElementGetUsagePage(e),usage=IOHIDElementGetUsage(e);
 if(!allowed(vendor,product,page,usage))return; /* Do not read values for other keys. */
 uint64_t ticks=mach_absolute_time()-c->start;uint64_t us=(uint64_t)((long double)ticks*c->scale.numer/c->scale.denom/1000.0L);
 CFIndex n=IOHIDValueGetIntegerValue(v);printf("host-monotonic-us=%llu service=%s usage=%s%02x value=%ld\n",(unsigned long long)us,vendor==0x303a?"evilduck-303a:1001":"builtin-05ac:0259",usage==0x39?"caps-":"modifier-",(unsigned)usage,(long)n);fflush(stdout);
 if(++c->observed>=2000)CFRunLoopStop(CFRunLoopGetCurrent());
}
static CFMutableDictionaryRef match(int vendor,int product){
 CFMutableDictionaryRef d=CFDictionaryCreateMutable(NULL,0,&kCFTypeDictionaryKeyCallBacks,&kCFTypeDictionaryValueCallBacks);if(!d)return NULL;
 const char* keys[]={kIOHIDVendorIDKey,kIOHIDProductIDKey,kIOHIDDeviceUsagePageKey,kIOHIDDeviceUsageKey};int values[]={vendor,product,1,6};
 for(int i=0;i<4;++i){CFStringRef k=CFStringCreateWithCString(NULL,keys[i],kCFStringEncodingUTF8);CFNumberRef n=CFNumberCreate(NULL,kCFNumberIntType,&values[i]);if(!k||!n){if(k)CFRelease(k);if(n)CFRelease(n);CFRelease(d);return NULL;}CFDictionarySetValue(d,k,n);CFRelease(k);CFRelease(n);}return d;
}
int main(int argc,char**argv){
 char* end=NULL;long seconds=argc==2?strtol(argv[1],&end,10):30;if(argc>2||seconds<1||seconds>120||(argc==2&&(!*argv[1]||*end))){fputs("Usage: observer [1..120 seconds]\n",stderr);return 2;}
 IOHIDManagerRef m=IOHIDManagerCreate(kCFAllocatorDefault,kIOHIDOptionsTypeNone);CFMutableDictionaryRef a=match(0x303a,0x1001),b=match(0x05ac,0x0259);if(!m||!a||!b){fputs("Allocation failure\n",stderr);if(m)CFRelease(m);if(a)CFRelease(a);if(b)CFRelease(b);return 1;}
 const void* dictionaries[]={a,b};CFArrayRef list=CFArrayCreate(NULL,dictionaries,2,&kCFTypeArrayCallBacks);if(!list){CFRelease(a);CFRelease(b);CFRelease(m);return 1;}IOHIDManagerSetDeviceMatchingMultiple(m,list);CFRelease(list);CFRelease(a);CFRelease(b);
 struct Context c={0};mach_timebase_info(&c.scale);c.start=mach_absolute_time();IOHIDManagerRegisterInputValueCallback(m,value,&c);IOHIDManagerScheduleWithRunLoop(m,CFRunLoopGetCurrent(),kCFRunLoopDefaultMode);
 IOReturn result=IOHIDManagerOpen(m,kIOHIDOptionsTypeNone);if(result!=kIOReturnSuccess){fprintf(stderr,"Open failed:0x%x. No sudo/permission changes attempted.\n",(unsigned)result);IOHIDManagerUnscheduleFromRunLoop(m,CFRunLoopGetCurrent(),kCFRunLoopDefaultMode);CFRelease(m);return 1;}
 puts("Passive foreground Caps/modifier values only. No matching values is NOT proof of no USB events. Ctrl-C stops. No letters retained.");CFRunLoopRunInMode(kCFRunLoopDefaultMode,(CFTimeInterval)seconds,false);
 IOHIDManagerClose(m,kIOHIDOptionsTypeNone);IOHIDManagerUnscheduleFromRunLoop(m,CFRunLoopGetCurrent(),kCFRunLoopDefaultMode);CFRelease(m);printf("Finished; filtered observations=%u; native transport/host state attribution remains limited.\n",c.observed);return 0;
}
#else
int main(void){fputs("MACOS_ONLY: native IOKit branch not tested here\n",stderr);return 2;}
#endif
