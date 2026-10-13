#!/usr/bin/env python3
"""Exact production AP helper body with Wi-Fi result adapters; no network access."""
import argparse,importlib.util,json,re,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--build-dir',type=Path,required=True);p.add_argument('--results',type=Path,required=True);a=p.parse_args()
if a.build_dir.exists() or a.results.exists():raise ValueError('Fresh outputs required')
a.build_dir.mkdir()
spec=importlib.util.spec_from_file_location('slice',ROOT/'tests/stage15/run_tests.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
source=(ROOT/'EvilDuckS3/webserver.cpp').read_text();body=m.body(source,'bool prepareControlledNetwork()')
(a.build_dir/'actual_helper.inc').write_text(body)
code=r'''
#include "Arduino.h"
#include <vector>
#include <iostream>
#include <stdexcept>
static bool eligible=true,loaded=true,modeOK=true,apOK=true,offOK=true;static bool controlledNetworkReady=false;
static unsigned assertions=0,starts=0;static std::vector<int> modes;
static void check(bool ok,const char *s){++assertions;if(!ok)throw std::runtime_error(s);}
namespace deployment{bool controlledStart(){return eligible;}}
namespace settings{bool ready(){return loaded;}String getSSID(){return String(std::string(12,'s'));}String getPassword(){return String(std::string(16,'p'));}int getChannel(){return 1;}bool getHiddenAp(){return false;}}
constexpr int WIFI_AP=2,WIFI_OFF=0;
struct Wifi{bool mode(int m){modes.push_back(m);return m==WIFI_OFF?offOK:modeOK;}bool softAP(const char*s,const char*p,int channel,int hidden){++starts;check(std::strlen(s)==12&&std::strlen(p)==16&&channel==1&&hidden==0,"validated parameters, private values omitted");return apOK;}} WiFi;
#include "actual_helper.inc"
int main(int argc,char**argv){try{check(argc==2,"case required");std::string name=argv[1];
 if(name=="settings_failure")loaded=false;if(name=="wrong_profile")eligible=false;if(name=="mode_failure")modeOK=false;if(name=="ap_failure")apOK=false;if(name=="shutdown_failure"){apOK=false;offOK=false;}
 bool ok=prepareControlledNetwork();
 if(name=="valid"){check(ok&&controlledNetworkReady&&starts==1,"AP success represented truthfully");}
 else{check(!ok&&!controlledNetworkReady,"failure never sets readiness");if(!eligible||!loaded)check(modes.empty()&&starts==0,"no network APIs before prerequisites");else{check(modes.back()==WIFI_OFF,"best effort shutdown attempted");check(starts==(modeOK?1u:0u),"short-circuit failed mode before AP");}}
 std::cout<<"PASS "<<name<<" ("<<assertions<<" assertions)\n";
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
'''
(a.build_dir/'network.cpp').write_text(code);exe=a.build_dir/'network'
subprocess.run(['g++','-std=c++17','-O1','-g','-fsanitize=address,undefined','-fno-pie','-no-pie','-I'+str(ROOT/'tests/stage1/mocks'),str(a.build_dir/'network.cpp'),'-o',str(exe)],check=True)
rows=[]
for name in ['valid','settings_failure','wrong_profile','mode_failure','ap_failure','shutdown_failure']:
 r=subprocess.run([str(exe),name],capture_output=True,text=True);match=re.search(r'PASS \w+ \((\d+) assertions\)',r.stdout);row=dict(name=name,status='PASS' if not r.returncode and match else 'FAIL',assertions=int(match[1]) if match else 0,stdout=r.stdout,stderr=r.stderr);rows.append(row);print(row['status'],name)
a.results.write_text(json.dumps(dict(results=rows,counts={s:sum(r['status']==s for r in rows) for s in ['PASS','FAIL']},assertions=sum(r['assertions'] for r in rows),sanitizers='ASan/UBSan',actual_helper_source_executed=True,whole_webserver_executed=False,physical_network_verified=False),indent=2)+'\n');raise SystemExit(any(r['status']=='FAIL' for r in rows))
