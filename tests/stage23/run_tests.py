#!/usr/bin/env python3
"""Exact pinned iterator/scanner source with actual native malloc/free and LSan."""
import argparse,hashlib,importlib.util,json,os,re,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools'))
from patched_core import sha
from startup_reference_prepare import verify
CASES='protected partial_start partial_end unprotected exhausted writable_table multiple_protected missing_table null_iterator allocation_failure load_failure invalid_metadata repeated_write repeated_erase alias concurrent_immutable_table leak_probe'.split()
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['partition-dir','reference-source','build-dir','results']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();verify(a.reference_source)
 for row in json.loads((ROOT/'docs/stage20-partition-reference.json').read_text()):
  if sha(a.partition_dir/row['url'].rsplit('/',1)[1])!=row['sha256']:raise ValueError('Partition source mismatch')
 if a.build_dir.exists() or a.results.exists() or ROOT in a.build_dir.resolve().parents:raise ValueError('Fresh external outputs required')
 a.build_dir.mkdir(parents=True)
 spec=importlib.util.spec_from_file_location('slice',ROOT/'tests/stage15/run_tests.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 source=(a.partition_dir/'partition.c').read_text();target=(a.partition_dir/'partition_target.c').read_text()
 begin=source.index('typedef struct partition_list_item_');end=source.index('static SLIST_HEAD(',begin)
 types=source[begin:end];(a.build_dir/'iterator_types.inc').write_text(types)
 bodies='\n'.join(m.body(source,prefix+name+'(') for prefix,name in [('static esp_partition_iterator_opaque_t *','iterator_create'),('esp_partition_iterator_t ','esp_partition_find'),('esp_partition_iterator_t ','esp_partition_next'),('void ','esp_partition_iterator_release'),('const esp_partition_t *','esp_partition_get')])
 bodies=bodies.replace('esp_partition_iterator_t esp_partition_next(', 'esp_partition_iterator_t underlying_next(').replace('const esp_partition_t *esp_partition_get(', 'const esp_partition_t *underlying_get(')
 (a.build_dir/'iterator_bodies.inc').write_text(bodies)
 os_source=(a.reference_source/'components/spi_flash/spi_flash_os_func_app.c').read_text();(a.build_dir/'callback_body.inc').write_text(m.body(os_source,'static esp_err_t main_flash_region_protected('))
 patch=ROOT/'proposals/esp-idf-5.5-readonly-iterator-cleanup.patch'
 copy=a.build_dir/'source/components/esp_partition';copy.mkdir(parents=True);(copy/'partition_target.c').write_text(target)
 subprocess.run(['patch','--batch','--forward','--fuzz=0','-p1','-i',str(patch)],cwd=a.build_dir/'source',check=True)
 patched=(copy/'partition_target.c').read_text()
 rows=[]
 for variant,text in [('unpatched',target),('proposal',patched)]:
  (a.build_dir/'scanner_body.inc').write_text(m.body(text,'bool esp_partition_is_flash_region_writable('))
  exe=a.build_dir/variant
  cmd=['g++','-std=gnu++17','-O1','-g','-pthread','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie','-DPATCHED='+str(int(variant=='proposal')),'-I'+str(a.build_dir),str(ROOT/'tests/stage23/iterator.cpp'),'-o',str(exe)]
  subprocess.run(cmd,check=True)
  for name in CASES:
   env=dict(os.environ,ASAN_OPTIONS='detect_leaks=1',LSAN_OPTIONS='exitcode=23')
   r=subprocess.run([str(exe),name],capture_output=True,text=True,timeout=60,env=env);match=re.search(r'PASS \w+ \((\d+) assertions\)',r.stdout);counts=re.search(r'COUNTERS (\d+) (\d+) (\d+) (\d+) (\d+) (\d+) (\d+)',r.stdout)
   expected_leak=variant=='unpatched' and name=='leak_probe'
   ok=bool(match and counts and ((r.returncode==23 and 'LeakSanitizer: detected memory leaks' in r.stderr) if expected_leak else r.returncode==0))
   status='XFAIL' if ok and expected_leak else ('OBSERVED' if ok and variant=='unpatched' and int(counts[3])>0 else ('PASS' if ok else 'FAIL'))
   if ok and name in ['allocation_failure','load_failure','invalid_metadata','missing_table','null_iterator']:status='OBSERVED'
   row=dict(variant=variant,name=name,status=status,assertions=int(match[1]) if match else 0,exit_code=r.returncode,stdout=r.stdout,stderr=r.stderr)
   if counts:row['iterator']=dict(zip(['allocations','sdk_releases','retained','allocation_failures','host_object_bytes','advances','gets'],map(int,counts.groups())))
   rows.append(row);print(status,variant,name,flush=True)
 out=dict(results=rows,counts={s:sum(r['status']==s for r in rows) for s in ['PASS','FAIL','XFAIL','OBSERVED']},assertions=sum(r['assertions'] for r in rows),sanitizers='ASan/UBSan + LSan detect_leaks=1; historical leak exit23 expected',source_commit='b66b5448e0dfac6be135e6f0ac21010aba231180',source_sha256=sha(a.partition_dir/'partition.c'),target_sha256=sha(a.partition_dir/'partition_target.c'),patch_sha256=sha(patch),patched_target_sha256=sha(copy/'partition_target.c'),native_malloc_free=True,loader_adapter=True,linux_mutex_adapter=True,hardware_access=False)
 a.results.write_text(json.dumps(out,indent=2)+'\n');return bool(out['counts']['FAIL'])
if __name__=='__main__':raise SystemExit(main())
