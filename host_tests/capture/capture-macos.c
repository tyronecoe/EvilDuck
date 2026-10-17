#ifdef __APPLE__
#include <ApplicationServices/ApplicationServices.h>
#include <CoreFoundation/CoreFoundation.h>
#include <signal.h>
#include <stdio.h>
#include <string.h>
#include <time.h>
static const char phrase[]="EVILDUCK TEST 123";
static unsigned matched;static int found,failed;static volatile sig_atomic_t stopped;
static struct timespec began;
static void stop_signal(int n){(void)n;stopped=1;}
static void check_time(CFRunLoopTimerRef timer,void*context){(void)timer;(void)context;struct timespec now;if(clock_gettime(CLOCK_MONOTONIC,&now)||stopped||now.tv_sec-began.tv_sec>=60)CFRunLoopStop(CFRunLoopGetCurrent());}
static CGEventRef observe(CGEventTapProxy proxy,CGEventType type,CGEventRef event,void*context){
 (void)proxy;(void)context;if(type==kCGEventTapDisabledByTimeout||type==kCGEventTapDisabledByUserInput){failed=1;CFRunLoopStop(CFRunLoopGetCurrent());return event;}
 if(type==kCGEventKeyDown&&!CGEventGetIntegerValueField(event,kCGKeyboardEventAutorepeat)){
  UniChar chars[8];UniCharCount count=0;CGEventKeyboardGetUnicodeString(event,8,&count,chars);
  for(UniCharCount i=0;i<count;i++){UniChar c=chars[i];if(c>='a'&&c<='z')c-=32;if(c==(unsigned char)phrase[matched])matched++;else matched=c=='E'?1:0;if(matched==sizeof(phrase)-1){found=1;matched=0;CFRunLoopStop(CFRunLoopGetCurrent());break;}}
 }
 return event; // Listen-only; never suppress or inject input.
}
int main(void){
 puts("VISIBLE FAKE-PHRASE diagnostic. No capture yet. Type START here, then type EVILDUCK TEST 123 manually in a second ordinary editor. Only that exact phrase is retained; other input discarded. Ctrl-C stops; 60-second limit. No delivery is active.");
 char answer[16];if(!fgets(answer,sizeof(answer),stdin)||strcmp(answer,"START\n"))return 2;
 if(clock_gettime(CLOCK_MONOTONIC,&began)){fputs("Monotonic clock unavailable.\n",stderr);return 1;}
 CFMachPortRef tap=CGEventTapCreate(kCGSessionEventTap,kCGHeadInsertEventTap,kCGEventTapOptionListenOnly,CGEventMaskBit(kCGEventKeyDown),observe,NULL);
 if(!tap){fputs("Capture unavailable/permission denied. Check normal owner-approved Accessibility permission; no bypass. Secure Input may prevent capture.\n",stderr);return 3;}
 CFRunLoopSourceRef source=CFMachPortCreateRunLoopSource(NULL,tap,0);if(!source){CFRelease(tap);return 1;}
 CFRunLoopTimerRef timer=CFRunLoopTimerCreate(NULL,CFAbsoluteTimeGetCurrent()+0.1,0.1,0,0,check_time,NULL);if(!timer){CFRelease(source);CFRelease(tap);return 1;}
 signal(SIGINT,stop_signal);signal(SIGTERM,stop_signal);CFRunLoopAddSource(CFRunLoopGetCurrent(),source,kCFRunLoopCommonModes);CFRunLoopAddTimer(CFRunLoopGetCurrent(),timer,kCFRunLoopCommonModes);CGEventTapEnable(tap,true);puts("ACTIVE — Stop with Ctrl-C; keep this terminal visible. No general key log or network transfer.");CFRunLoopRun();
 CGEventTapEnable(tap,false);CFMachPortInvalidate(tap);CFRunLoopRemoveTimer(CFRunLoopGetCurrent(),timer,kCFRunLoopCommonModes);CFRunLoopRemoveSource(CFRunLoopGetCurrent(),source,kCFRunLoopCommonModes);CFRelease(timer);CFRelease(source);CFRelease(tap);
 if(failed){fputs("Tap disabled; capture result unavailable.\n",stderr);return 1;}if(found){puts("FAKE PHRASE OBSERVED: EVILDUCK TEST 123");puts("Review this local result. Use the separate fixed sender only after a supported LED round trip is established.");return 0;}puts("Stopped/timed out; no fake-phrase match. Not evidence of antivirus prevention.");return 4;
}
#else
#error Requires native macOS SDK; Linux is not a macOS build test
#endif
