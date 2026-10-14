// New diagnostic only: unchanged Stage28N/vendor code, intended old failures.
#include "boundary.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define REQUIRE(v) do{if(!(v)){fprintf(stderr,"EXPECTED OLD CONTRACT VIOLATION: %s\n",#v);return 1;}}while(0)
int main(int argc,char** argv){
 if(argc!=2)return 2;fixture_init();uint8_t a[8]={0,0,4},b[8]={0,0,5};
 if(!strcmp(argv[1],"stale")){
  REQUIRE(tud_hid_n_report(0,1,a,8));inject_complete(0x81,9,XFER_RESULT_SUCCESS);fixture_dispatch();
  REQUIRE(tud_hid_n_report(0,1,b,8));inject_complete(0x81,9,XFER_RESULT_SUCCESS);fixture_dispatch();
  REQUIRE(usbd_edpt_busy(0,0x81)); // old tuple incorrectly clears newer endpoint
 }else if(!strcmp(argv[1],"refusal")){
  uint8_t oversized[65]={0};REQUIRE(!tud_hid_n_report(0,1,oversized,sizeof(oversized)));
  REQUIRE(tud_hid_n_report(0,1,a,8)); // old oversized refusal retained claim
 }else return 2;
 return 0;
}
