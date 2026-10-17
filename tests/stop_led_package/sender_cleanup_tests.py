#!/usr/bin/env python3
"""Execute only the extracted macOS cleanup statements with fake value(), never HID.
C# is a focused source-structure check, NOT native Windows execution.
"""
import argparse,hashlib,json,pathlib,re,subprocess,tempfile
ROOT=pathlib.Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--results',type=pathlib.Path,required=True);a=p.parse_args();assert not a.results.exists()
mac=(ROOT/'host_tests/led_return/send-macos.c').read_text();windows=(ROOT/'host_tests/led_return/WindowsSender.cs').read_text()
block=mac.split('restore:{',1)[1].split('}CFRelease(elements)',1)[0]
assert block.count('value(device,caps,oldCaps)')==1 and block.count('value(device,num,oldNum)')==1
harness='''#include <assert.h>
#include <stdio.h>
static int capsOK,numOK,calls[2],order[2],next;
static int value(int d,int e,int n){assert(d==7 && n==1);assert(next<2);order[next++]=e;calls[e]++;return e==0?capsOK:numOK;}
static int cleanup(int result){int device=7,caps=0,num=1,oldCaps=1,oldNum=1;
''' + block + '''
return result;}
int main(void){for(int prior=0;prior<2;prior++)for(int c=0;c<2;c++)for(int n=0;n<2;n++){
capsOK=c;numOK=n;calls[0]=calls[1]=next=0;
int r=cleanup(prior);assert(calls[0]==1 && calls[1]==1 && order[0]==0 && order[1]==1);assert(r==(prior||!c||!n));}
puts("8 cleanup combinations PASS");return 0;}
'''
with tempfile.TemporaryDirectory(prefix='no-hid-cleanup-') as tmp:
 t=pathlib.Path(tmp);(t/'test.c').write_text(harness)
 subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer',str(t/'test.c'),'-o',str(t/'test')],check=True)
 import os
 env=os.environ.copy();env['ASAN_OPTIONS']='detect_leaks=1:halt_on_error=1';env['UBSAN_OPTIONS']='halt_on_error=1'
 subprocess.run([str(t/'test')],check=True,env=env)
# Review exact cleanup shape, independent try/catch paths and post-finally return.
finally_body=windows.split('  finally{',1)[1].split('  return result;',1)[0]
pattern=r'try\{Set\(0x14,caps\);\}catch\(Exception e\)\{Console.Error.WriteLine\("Caps restore unconfirmed: "\+e.Message\);result=1;\}\s*try\{Set\(0x90,num\);\}catch\(Exception e\)\{Console.Error.WriteLine\("Num restore unconfirmed: "\+e.Message\);result=1;\}'
assert re.search(pattern,finally_body)
active=windows.split('  int result=0;',1)[1];assert 'return 0' not in active and 'return 1' not in active and 'return result;' in active
assert 'catch(Exception e){Console.Error.WriteLine(e.Message);result=1;}' in active
out=dict(mac_cleanup_combinations_pass=8,mac_executed_scope='extracted production cleanup block only; fake value API, not IOKit',windows_source_contract_checks_pass=3,windows_native_compilation='NOT TESTED; compiler unavailable',mac_native_compilation='NOT TESTED; Apple SDK unavailable',sanitizers='ASan/UBSan/leak detection PASS for cleanup block harness',hardware_access=False,host_sender_executed=False,source_sha256={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in ['host_tests/led_return/send-macos.c','host_tests/led_return/WindowsSender.cs']})
a.results.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
