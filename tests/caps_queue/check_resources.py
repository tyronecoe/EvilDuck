"""Production receiver native layout/allocation comparison, never target RAM claims."""
import argparse,json,pathlib,subprocess,os
ROOT=pathlib.Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--base',type=pathlib.Path,required=True);p.add_argument('--changed',type=pathlib.Path,required=True);p.add_argument('--output-dir',type=pathlib.Path,required=True);a=p.parse_args();assert not a.output_dir.exists();a.output_dir.mkdir();rows={};commands=[]
for name,src in [('before',a.base),('after',a.changed)]:
 cmd=['g++','-std=c++17','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie','-DEVILDUCK_HOST_TEST','-I'+str(src),'-I'+str(ROOT/'tests/stage28x'),'-I'+str(ROOT/'tests/stage28t'),str(ROOT/'tests/caps_queue/receiver_resources.cpp'),str(src/'led_receiver.cpp'),str(ROOT/'tests/stage28x/allocations.cpp'),'-o',str(a.output_dir/name)]
 if name=='after':cmd.insert(1,'-DNEW_RECEIVER')
 commands.append(cmd);subprocess.run(cmd,check=True);env=os.environ.copy();env.update(ASAN_OPTIONS='detect_leaks=1:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1');r=subprocess.run([str(a.output_dir/name)],capture_output=True,text=True,check=True,env=env);rows[name]=json.loads(r.stdout)
out=dict(PASS=2,FAIL=0,measurements=rows,commands=commands,scope='Linux native receiver module only; not Xtensa static RAM, hardware heap or task stack',sanitizers='ASan/UBSan/leak detection PASS',hardware=False);(a.output_dir/'results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out['measurements'],indent=2))
