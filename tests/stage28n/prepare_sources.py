#!/usr/bin/env python3
"""Read-only official-source retrieval to NEW external scratch. No installs/patches/builds."""
import argparse,hashlib,json,pathlib,urllib.request
ROOT=pathlib.Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output-dir',type=pathlib.Path,required=True);a=p.parse_args();out=a.output_dir.resolve()
if out.exists() or out.is_relative_to(ROOT):raise ValueError('Fresh external directory required')
manifest=json.loads((ROOT/'docs/stage28n-source-manifest.json').read_text());out.mkdir();rows=[]
for row in manifest['vendor_inputs']:
    relative=pathlib.Path(row['file']);url=row['official_url']
    if relative.is_absolute() or '..' in relative.parts or not url.startswith('https://raw.githubusercontent.com/hathach/tinyusb/8a78804ff91271fb32008288777fad9fe73f5735/'):raise ValueError('Unsafe/unpinned source input')
    with urllib.request.urlopen(url,timeout=30) as response:data=response.read()
    if hashlib.sha256(data).hexdigest()!=row['sha256']:raise ValueError('Official source mismatch: '+str(relative))
    target=out/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data);rows.append(row)
(out/'retrieval.json').write_text(json.dumps({'status':'PASS','files':rows,'scope':'source download only, no installation'},indent=2)+'\n')
print('PASS hash-verified official source inputs:',len(rows))
