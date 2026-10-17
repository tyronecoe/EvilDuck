// Native macOS IOHID output-element test; no raw report encoding guesses.
#ifdef __APPLE__
#include <IOKit/hid/IOHIDManager.h>
#include <IOKit/hid/IOHIDKeys.h>
#include <CoreFoundation/CoreFoundation.h>
#include <stdio.h>
#include <string.h>
#include <signal.h>
#include <unistd.h>
#include <time.h>
static volatile sig_atomic_t cancelled;
static void stop(int n){(void)n;cancelled=1;}
static void hard_timeout(int n){(void)n;const char msg[]="Sender hard timeout; lock restoration unconfirmed.\n";write(2,msg,sizeof(msg)-1);_exit(124);}
static int value(IOHIDDeviceRef d,IOHIDElementRef e,int n){IOHIDValueRef v=IOHIDValueCreateWithIntegerValue(kCFAllocatorDefault,e,0,n);if(!v)return 0;IOReturn r=IOHIDDeviceSetValue(d,e,v);CFRelease(v);return r==kIOReturnSuccess;}
static int read_value(IOHIDDeviceRef d,IOHIDElementRef e,int *out){IOHIDValueRef v=NULL;if(IOHIDDeviceGetValue(d,e,&v)!=kIOReturnSuccess||!v)return 0;*out=(int)IOHIDValueGetIntegerValue(v);return *out==0||*out==1;}
static unsigned short crc(const unsigned char*p,size_t n){unsigned short c=65535;for(size_t i=0;i<n;i++){c^=(unsigned short)p[i]<<8;for(int j=0;j<8;j++)c=(unsigned short)((c&32768)?(c<<1)^0x1021:c<<1);}return c;}
int main(int argc,char**argv){
 if(argc!=3||strcmp(argv[1],"--caps-num-confirmed")){fprintf(stderr,"Usage: send-macos --caps-num-confirmed EXACT_USB_SERIAL\nOnly after actual Caps+Num device reports have been observed. Unsupported APIs/permissions fail closed.\n");return 2;}
 puts("VISIBLE FIXED LED TEST. No key capture. API/cached values are not host feedback. Type SEND to proceed; Ctrl-C stops; maximum90 seconds.");char answer[16];if(!fgets(answer,sizeof(answer),stdin)||strcmp(answer,"SEND\n"))return 2;
 signal(SIGINT,stop);signal(SIGTERM,stop);signal(SIGALRM,hard_timeout);alarm(95);
 IOHIDManagerRef manager=IOHIDManagerCreate(kCFAllocatorDefault,kIOHIDOptionsTypeNone);if(!manager)return 1;
 int vendor=0x303a,product=0x1001;CFNumberRef vn=CFNumberCreate(NULL,kCFNumberIntType,&vendor),pn=CFNumberCreate(NULL,kCFNumberIntType,&product);CFStringRef serial=CFStringCreateWithCString(NULL,argv[2],kCFStringEncodingUTF8);const void*keys[]={CFSTR(kIOHIDVendorIDKey),CFSTR(kIOHIDProductIDKey),CFSTR(kIOHIDSerialNumberKey)};const void*vals[]={vn,pn,serial};CFDictionaryRef match=CFDictionaryCreate(NULL,keys,vals,3,&kCFTypeDictionaryKeyCallBacks,&kCFTypeDictionaryValueCallBacks);IOHIDManagerSetDeviceMatching(manager,match);CFRelease(match);CFRelease(vn);CFRelease(pn);CFRelease(serial);
 int result=1;if(IOHIDManagerOpen(manager,kIOHIDOptionsTypeNone)!=kIOReturnSuccess){fputs("Permission/open failure. No bypass.\n",stderr);goto done;}
 CFSetRef devices=IOHIDManagerCopyDevices(manager);if(!devices||CFSetGetCount(devices)!=1){fputs("Expected exactly one matching HID device; missing/ambiguous is unsupported.\n",stderr);if(devices)CFRelease(devices);goto done;}
 IOHIDDeviceRef device;CFSetGetValues(devices,(const void**)&device);CFArrayRef elements=IOHIDDeviceCopyMatchingElements(device,NULL,kIOHIDOptionsTypeNone);IOHIDElementRef num=NULL,caps=NULL;
 if(elements)for(CFIndex i=0;i<CFArrayGetCount(elements);i++){IOHIDElementRef e=(IOHIDElementRef)CFArrayGetValueAtIndex(elements,i);if(IOHIDElementGetType(e)!=kIOHIDElementTypeOutput||IOHIDElementGetUsagePage(e)!=8)continue;if(IOHIDElementGetUsage(e)==1){if(num){num=NULL;break;}num=e;}if(IOHIDElementGetUsage(e)==2){if(caps){caps=NULL;break;}caps=e;}}
 int oldNum=0,oldCaps=0;if(!num||!caps||!read_value(device,num,&oldNum)||!read_value(device,caps,&oldCaps)){fputs("Required writable/readable Num and Caps elements unavailable; method unsupported on this setup.\n",stderr);if(elements)CFRelease(elements);CFRelease(devices);goto done;}
 unsigned char frame[25]={0,0x45,0x44,0x52,0x31,17};memcpy(frame+6,"EVILDUCK TEST 123",17);unsigned short check=crc(frame+5,18);frame[23]=check>>8;frame[24]=check;struct timespec began,now;int clock=0;if(clock_gettime(CLOCK_MONOTONIC,&began))goto restore;
 if(!value(device,caps,0)||!value(device,num,0))goto restore;
 for(size_t i=0;i<sizeof(frame);i++)for(int bit=7;bit>=0;bit--){if(clock_gettime(CLOCK_MONOTONIC,&now))goto restore;if(cancelled||now.tv_sec-began.tv_sec>=90)goto restore;if(!value(device,num,(frame[i]>>bit)&1))goto restore;usleep(100000);clock=!clock;if(!value(device,caps,clock))goto restore;usleep(100000);}
 puts("Host API writes finished (17 payload bytes); device integrity/physical delivery remains unconfirmed.");result=0;
restore:if(!value(device,caps,oldCaps)||!value(device,num,oldNum)){fputs("LED restoration unconfirmed.\n",stderr);result=1;}CFRelease(elements);CFRelease(devices);
done:IOHIDManagerClose(manager,kIOHIDOptionsTypeNone);CFRelease(manager);alarm(0);return result;
}
#else
#error Build this attempted sender with the macOS SDK; a Linux build is not macOS verification
#endif
