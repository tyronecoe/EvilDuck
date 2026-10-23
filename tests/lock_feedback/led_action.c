/* One explicitly invoked LED-output action, no keyboard input or raw reports.
 * Compile only on the owner's Mac after separate physical-test approval. */
#ifndef __APPLE__
#error Apple IOKit required; Linux tests do not establish native Mac behavior.
#else
#include <CoreFoundation/CoreFoundation.h>
#include <IOKit/hid/IOHIDManager.h>
#include <IOKit/hid/IOHIDKeys.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
static volatile sig_atomic_t stop;
static void interrupted(int s){(void)s;stop=1;}
static void watchdog(int s){(void)s;_exit(124);}
static int number(IOHIDDeviceRef d,CFStringRef k,int value){int32_t x=-1;CFTypeRef p=IOHIDDeviceGetProperty(d,k);return p&&CFGetTypeID(p)==CFNumberGetTypeID()&&CFNumberGetValue((CFNumberRef)p,kCFNumberSInt32Type,&x)&&x==value;}
static int set(IOHIDDeviceRef d,IOHIDElementRef e,int n){IOHIDValueRef v=IOHIDValueCreateWithIntegerValue(kCFAllocatorDefault,e,0,n);if(!v)return 0;IOReturn r=IOHIDDeviceSetValue(d,e,v);CFRelease(v);return r==kIOReturnSuccess;}
int main(int argc,char**argv){
 if(argc!=5||strcmp(argv[1],"--one-approved-action")||strlen(argv[2])<1||strlen(argv[2])>128||strlen(argv[3])!=1||!strchr("12",argv[3][0])||strlen(argv[4])!=1||!strchr("01",argv[4][0]))return 2;
 unsigned usage=(unsigned)(argv[3][0]-'0');int desired=argv[4][0]-'0';
 signal(SIGINT,interrupted);signal(SIGTERM,interrupted);signal(SIGALRM,watchdog);alarm(4);
 IOHIDManagerRef m=IOHIDManagerCreate(kCFAllocatorDefault,0);if(!m)return 3;
 int32_t vendor=0x303a,product=0x1001;CFNumberRef vn=CFNumberCreate(NULL,kCFNumberSInt32Type,&vendor),pn=CFNumberCreate(NULL,kCFNumberSInt32Type,&product);
 if(!vn||!pn){if(vn)CFRelease(vn);if(pn)CFRelease(pn);CFRelease(m);return 3;}
 const void*keys[]={CFSTR(kIOHIDVendorIDKey),CFSTR(kIOHIDProductIDKey)};const void*vals[]={vn,pn};
 CFDictionaryRef match=CFDictionaryCreate(NULL,keys,vals,2,&kCFTypeDictionaryKeyCallBacks,&kCFTypeDictionaryValueCallBacks);CFRelease(vn);CFRelease(pn);
 if(!match){CFRelease(m);return 3;}IOHIDManagerSetDeviceMatching(m,match);CFRelease(match);
 if(IOHIDManagerOpen(m,0)!=kIOReturnSuccess){CFRelease(m);return 3;}
 CFSetRef devices=IOHIDManagerCopyDevices(m);IOHIDDeviceRef selected=NULL;unsigned matches=0;CFArrayRef elements=NULL;IOHIDElementRef element=NULL;int old=-1,accepted=0,restored=0,result=3;
 if(devices){CFIndex count=CFSetGetCount(devices);if(count<=16){const void*list[16];CFSetGetValues(devices,list);for(CFIndex i=0;i<count;++i){IOHIDDeviceRef d=(IOHIDDeviceRef)list[i];char serial[256]={0};CFTypeRef s=IOHIDDeviceGetProperty(d,CFSTR(kIOHIDSerialNumberKey));if(number(d,CFSTR(kIOHIDVendorIDKey),0x303a)&&number(d,CFSTR(kIOHIDProductIDKey),0x1001)&&IOHIDDeviceConformsTo(d,1,6)&&s&&CFGetTypeID(s)==CFStringGetTypeID()&&CFStringGetCString((CFStringRef)s,serial,sizeof(serial),kCFStringEncodingUTF8)&&!strcmp(serial,argv[2])){selected=d;++matches;}}}}
 if(matches!=1)goto cleanup;
 elements=IOHIDDeviceCopyMatchingElements(selected,NULL,0);if(!elements||CFArrayGetCount(elements)>2048)goto cleanup;
 matches=0;for(CFIndex i=0;i<CFArrayGetCount(elements);++i){IOHIDElementRef e=(IOHIDElementRef)CFArrayGetValueAtIndex(elements,i);if(IOHIDElementGetType(e)==kIOHIDElementTypeOutput&&IOHIDElementGetUsagePage(e)==8&&IOHIDElementGetUsage(e)==usage){++matches;element=e;}}
 if(matches!=1||IOHIDElementGetReportID(element)!=1||IOHIDElementGetReportSize(element)!=1||IOHIDElementGetReportCount(element)!=1||IOHIDElementGetLogicalMin(element)!=0||IOHIDElementGetLogicalMax(element)!=1)goto cleanup;
 {IOHIDValueRef v=NULL;if(IOHIDDeviceGetValue(selected,element,&v)!=kIOReturnSuccess||!v)goto cleanup;old=(int)IOHIDValueGetIntegerValue(v);if(old!=0&&old!=1)goto cleanup;}
 if(stop)goto cleanup;
 accepted=set(selected,element,desired); /* API acceptance only; dashboard is authoritative evidence. */
 usleep(200000);
 restored=set(selected,element,old); /* Attempt even after uncertain SetValue failure. No retry. */
 result=accepted&&restored&&!stop?0:3;
cleanup:
 printf("{\"apiAccepted\":%s,\"restoreApiAccepted\":%s,\"hostGlobalRestorationProven\":false}\n",accepted?"true":"false",restored?"true":"false");fflush(stdout);
 if(elements)CFRelease(elements);if(devices)CFRelease(devices);IOHIDManagerClose(m,0);CFRelease(m);alarm(0);return result;
}
#endif
