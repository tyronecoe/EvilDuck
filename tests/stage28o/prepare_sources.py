#!/usr/bin/env python3
"""Fresh external native copies only. Exact input, patch and output checks."""
import argparse,hashlib,json,pathlib,shutil,subprocess
ROOT=pathlib.Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--original',type=pathlib.Path,required=True);p.add_argument('--output',type=pathlib.Path,required=True);a=p.parse_args()
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
m=json.loads((ROOT/'docs/stage28o-input-and-patch-manifest.json').read_text());n=ROOT/'docs/stage28n-source-manifest.json'
assert sha(n)==m['original_manifest_sha256']
assert not a.output.exists() and not a.output.resolve().is_relative_to(ROOT)
assert not a.output.resolve().is_relative_to(a.original.resolve()), "Output must not nest inside source"
for r in json.loads(n.read_text())['vendor_inputs']:assert sha(a.original/r['file'])==r['sha256'],r['file']
patch=ROOT/'tests/stage28o/tinyusb-native.patch';assert sha(patch)==m['patch_sha256']
for r in m['patched_files']:
 if r['input_sha256']:assert sha(a.original/r['file'])==r['input_sha256']
 else:assert not (a.original/r['file']).exists()
shutil.copytree(a.original,a.output)
cmd=['patch','--batch','--fuzz=0','--no-backup-if-mismatch','-p1','-i',str(patch)]
r=subprocess.run(cmd,cwd=a.output,capture_output=True,text=True)
if r.returncode or 'offset' in r.stdout or 'fuzz' in r.stdout:raise RuntimeError('Patch not exact: '+r.stdout+r.stderr)
for row in m['patched_files']:assert sha(a.output/row['file'])==row['output_sha256'],row['file']
changed={r['file'] for r in m['patched_files']}
for row in json.loads(n.read_text())['vendor_inputs']:
 if row['file'] not in changed:assert sha(a.output/row['file'])==row['sha256']
print('PASS exact native-only transformation; installed dependencies untouched')
