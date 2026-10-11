#!/usr/bin/env python3
"""Observe audit fixtures offline; matched gaps are NOT compatibility passes."""
import argparse,json,re,subprocess,sys,tempfile
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tests/stage1'))
from run_tests import compile_target

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--build-dir',type=Path)
 p.add_argument('--results',type=Path)
 a=p.parse_args();build=a.build_dir or Path(tempfile.mkdtemp(prefix='evilduck-stage9-'))
 exe=compile_target(ROOT/'tests/stage9/observe.cpp',build,'stage9_observe')
 results=[];assertions=0
 for fixture in json.loads((ROOT/'tests/stage9/fixtures.json').read_text()):
  expected=build/'expected.txt';expected.write_text(fixture['observed_output'])
  for source in ['stage9.txt','sd:stage9.txt']:
   r=subprocess.run([str(exe),str(ROOT/'tests/stage9'/fixture['file']),str(expected),fixture['diagnostic_contains'],source],capture_output=True,text=True,timeout=25)
   matched=r.returncode==0
   count=re.search(r'OBSERVED (\d+) assertions',r.stdout)
   assertions+=int(count[1]) if count else 0
   results.append(dict(fixture=fixture['name'],source=source,canonical_status=fixture['canonical_status'],observation_matched=matched,assertions=int(count[1]) if count else 0,stdout=r.stdout,stderr=r.stderr))
   print(('OBSERVED' if matched else 'MISMATCH'),fixture['name'],source,fixture['canonical_status'],flush=True)
   if not matched:print(r.stdout,r.stderr,flush=True)
 probe=build/'stage9_attackmode'
 subprocess.run(['g++','-std=gnu++17','-g','-O1','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie','-I'+str(ROOT/'tests/stage1/mocks'),'-I'+str(ROOT/'EvilDuckS3'),str(ROOT/'tests/stage9/attackmode_probe.cpp'),str(ROOT/'EvilDuckS3/attackmode.cpp'),'-o',str(probe)],check=True)
 r=subprocess.run([str(probe)],capture_output=True,text=True,timeout=25)
 results.append(dict(fixture='production_attackmode_failure',canonical_status='GAP',observation_matched=r.returncode==0,assertions=2 if r.returncode==0 else 0,stdout=r.stdout,stderr=r.stderr))
 assertions+=2 if r.returncode==0 else 0
 print(r.stdout,r.stderr)
 mismatches=sum(not x['observation_matched'] for x in results)
 report=dict(observations=len(results),mismatches=mismatches,assertions=assertions,results=results,sanitizers='ASan/UBSan',hardware_access=False)
 if a.results:a.results.write_text(json.dumps(report,indent=2)+'\n')
 print(f"Audit: {len(results)} observations; {mismatches} mismatches; {assertions} assertions. Gaps remain gaps.")
 return bool(mismatches)
if __name__=='__main__':raise SystemExit(main())
