
#include "adapter.h"
#include "hid_backend.h"
#include "core.h"
#include "coordinator.h"
#include "lower.h"
#include "host.h"
#include <cstdio>
#include <cstdlib>
#include <cstring>
namespace {struct Row {const char* kind;unsigned at,state,phase,reason,count,instance,id,length;unsigned long long request,session,operation;bool clear;int outcome,sink,returned;unsigned char bytes[8];char scheduler[12];};Row rows[256]{};unsigned used=0,dropped=0;int adapterState=-1;}
static Row* add(const char*k){if(used==256){++dropped;return nullptr;}auto&r=rows[used++];r.kind=k;r.at=mock::now;r.state=unsigned(adapterState);auto s=route_u::status();r.phase=unsigned(s.phase);r.reason=unsigned(s.reason);r.request=s.request;r.count=lower::count;r.outcome=r.sink=r.returned=-1;return &r;}
extern "C" void ds02mark(const char*k){add(k);}
extern "C" void ds02report(const lower::Call*c,int sink,int returned,const char*k){auto*r=add(k);if(!r)return;r->instance=c->instance;r->id=c->id;r->length=8;r->session=c->session;r->operation=c->operation;r->clear=c->clear;r->outcome=int(c->outcome);r->sink=sink;r->returned=returned;memcpy(r->bytes,c->bytes,8);memcpy(r->scheduler,c->phase,12);r->scheduler[11]=0;}
extern "C" void __real__ZN8native_b7Adapter4stepEj(native_b::Adapter*,uint32_t);
extern "C" void __wrap__ZN8native_b7Adapter4stepEj(native_b::Adapter*a,uint32_t now){adapterState=int(a->state());static int last=-1;if(adapterState!=last){add("adapter_step_entry");last=adapterState;}int before=adapterState;__real__ZN8native_b7Adapter4stepEj(a,now);adapterState=int(a->state());if(before!=adapterState){add("adapter_state_transition");last=adapterState;}}
extern "C" void __real__ZN8native_b7Adapter6cancelEv(native_b::Adapter*);
extern "C" void __wrap__ZN8native_b7Adapter6cancelEv(native_b::Adapter*a){adapterState=int(a->state());add("cancellation_observed_adapter_cancel_entry");__real__ZN8native_b7Adapter6cancelEv(a);adapterState=int(a->state());add("adapter_cancel_return");}
extern "C" void __real__ZN10ds_preview7Runtime4tickEj(ds_preview::Runtime*,uint32_t);
extern "C" void __wrap__ZN10ds_preview7Runtime4tickEj(ds_preview::Runtime*a,uint32_t now){bool before=a->delayed_;__real__ZN10ds_preview7Runtime4tickEj(a,now);if(!before&&a->delayed_){auto*r=add("runtime_delay_entry");if(r){r->operation=a->event_.value;r->session=a->pc_;}}}
static void dump(){const char*path=getenv("DS02_JOURNAL_PATH");if(!path)return;FILE*f=fopen(path,"w");if(!f)return;for(unsigned i=0;i<used;++i){auto&r=rows[i];fprintf(f,"{\"seq\":%u,\"kind\":\"%s\",\"at_ms\":%u,\"adapter_state\":%u,\"coordinator_phase\":%u,\"reason\":%u,\"request\":%llu,\"lower_count\":%u,\"session_or_delay_pc\":%llu,\"operation_or_delay_ms\":%llu,\"clear\":%s,\"outcome\":%d,\"mock_sink_result\":%d,\"submit_return\":%d,\"scheduler\":\"%s\",\"bytes\":[",i,r.kind,r.at,r.state,r.phase,r.reason,r.request,r.count,r.session,r.operation,r.clear?"true":"false",r.outcome,r.sink,r.returned,r.scheduler);for(unsigned j=0;j<8;++j)fprintf(f,"%s%u",j?",":"",r.bytes[j]);fprintf(f,"],\"instance\":%u,\"report_id\":%u,\"length\":%u}\n",r.instance,r.id,r.length);}fprintf(f,"{\"kind\":\"journal_summary\",\"capacity\":256,\"entries\":%u,\"dropped\":%u}\n",used,dropped);fclose(f);}
struct Setup{Setup(){atexit(dump);}}setupJournal;

static bool validateDS02(const Row* v,unsigned n,unsigned lost){
 if(lost||n>256)return false;int delay=-1,request=-1,observe=-1,terminal=-1;unsigned attempts[2]={},returns[2]={},na=0,nr=0;
 for(unsigned i=0;i<n;++i){const Row&r=v[i];
  if(!strcmp(r.kind,"runtime_delay_entry")){if(delay!=-1||r.operation!=10000)return false;delay=int(i);}
  if(!strcmp(r.kind,"cancellation_request_before_stop"))request=int(i);
  if(!strcmp(r.kind,"cancellation_observed_adapter_cancel_entry"))observe=int(i);
  if(!strcmp(r.kind,"terminal_after_prCancelled_before_original_assertion"))terminal=int(i);
  if(!strcmp(r.kind,"report_submission_attempt")){if(na==2)return false;attempts[na++]=i;}
  if(!strcmp(r.kind,"report_submission_return")){if(nr==2)return false;returns[nr++]=i;}
 }
 if(na!=2||nr!=2||delay<0||request<=delay||observe<=request||terminal<=observe)return false;
 for(unsigned j=0;j<2;++j){const Row&a=v[attempts[j]],&b=v[returns[j]];if(attempts[j]>=returns[j]||a.instance!=0||b.instance!=0||a.id!=1||b.id!=1||a.length!=8||b.length!=8||!a.clear||!b.clear||a.outcome!=0||b.outcome!=0||b.sink!=1||b.returned!=1)return false;for(unsigned k=0;k<8;++k)if(a.bytes[k]||b.bytes[k])return false;if(a.request!=v[delay].request||b.request!=a.request||!a.session||b.session!=a.session||a.count!=j+1||b.count!=j+1)return false;}
 if(!(returns[0]<unsigned(delay)&&unsigned(observe)<attempts[1]&&returns[1]<unsigned(terminal)))return false;
 const Row&t=v[terminal];return t.state==8&&t.phase==0&&t.reason==2&&t.request==v[delay].request&&t.count==2&&t.at>=v[returns[1]].at+1000;
}
extern "C" bool ds02Safety(){auto t=route_u::status();return validateDS02(rows,used,dropped)&&lower::count==2&&t.reason==route_u::Reason::Cancelled&&!route_u::owned()&&!hid_backend::hasPersistent();}
extern "C" bool ds02Controls(){Row copy[256];unsigned cleanup=0;for(unsigned i=0;i<used;++i)if(!strcmp(rows[i].kind,"report_submission_return"))cleanup=i;
 for(unsigned test=0;test<10;++test){memcpy(copy,rows,sizeof(rows));unsigned n=used;if(test==0)copy[cleanup].bytes[0]=2;else if(test<=6)copy[cleanup].bytes[test+1]=4;else if(test==7)copy[cleanup].kind="missing_cleanup";else if(test==8){copy[cleanup].returned=0;copy[cleanup].sink=0;copy[cleanup].outcome=1;}else{if(n==256)return false;copy[n]=copy[cleanup];copy[n].at=copy[n-1].at+1;copy[n].count=3;++n;}bool rejected=!validateDS02(copy,n,dropped);printf("CONTROL %u %s\n",test,rejected?"REJECTED":"INCORRECTLY_ACCEPTED");if(!rejected)return false;}return true;}
