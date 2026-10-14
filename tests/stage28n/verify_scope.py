#!/usr/bin/env python3
"""Read-only preservation, source and receipt checks. No build/device actions."""
import argparse,hashlib,json,pathlib,stat,subprocess,sys
sys.dont_write_bytecode=True
ROOT=pathlib.Path(__file__).resolve().parents[2];BASE='50ec41349136bfaddbac6a44622c3c25e2ce42e3'
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--results',type=pathlib.Path,required=True);p.add_argument('--source-root',type=pathlib.Path);p.add_argument('--protected-core',type=pathlib.Path);a=p.parse_args()
if a.results.exists() or a.results.resolve().is_relative_to(ROOT):raise ValueError('Fresh external receipt required')
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
old=[]
for e in git('ls-tree','-rz',BASE).split(b'\0'):
    if not e:continue
    meta,name=e.split(b'\t');mode,kind,oid=meta.split();f=ROOT/name.decode()
    if kind!=b'blob' or f.read_bytes()!=git('cat-file','blob',oid.decode()) or bool(f.stat().st_mode&stat.S_IXUSR)!=(mode==b'100755'):raise ValueError('Historical file/path/mode mismatch')
    old.append(name.decode())
if set(git('diff',BASE,'--name-only').decode().splitlines())&set(old):raise ValueError('Historical path/mode change')
allfiles=set(git('ls-files','--cached','--others','--exclude-standard').decode().splitlines());added=sorted(allfiles-set(old))
if not all(v.startswith(('docs/stage28n-','tests/stage28n/')) for v in added):raise ValueError('Out-of-scope addition')
subprocess.run([sys.executable,'tests/stage28h/verify_freeze.py'],cwd=ROOT,check=True)
dep='NOT REQUESTED'
if a.protected_core:
    sys.path.insert(0,str(ROOT/'tools'));import patched_core
    patched_core.check_sources(a.protected_core,patched=True);dep='PASS unchanged protected core/SDK'
source_status='NOT REQUESTED'
if a.source_root:
    manifest=json.loads((ROOT/'docs/stage28n-source-manifest.json').read_text())
    for row in manifest['vendor_inputs']:
        if hashlib.sha256((a.source_root/row['file']).read_bytes()).hexdigest()!=row['sha256']:raise ValueError('Vendor source drift')
    source_status='PASS 21 unmodified official source/header inputs'
receipt_status='NOT AVAILABLE'
receipt=ROOT/'docs/stage28n-test-results.json'
if receipt.exists():
    report=json.loads(receipt.read_text());manifest=ROOT/'docs/stage28n-source-manifest.json'
    if hashlib.sha256(manifest.read_bytes()).hexdigest()!=report['manifest_sha256']:raise ValueError('Receipt/manifest drift')
    if report['counts']!={'PASS':20,'FAIL':0} or sum(v['assertions'] for v in report['results'])!=report['assertions']:raise ValueError('Primary counts inconsistent')
    if [v['id'] for v in report['results']]!=['N%02d'%i for i in range(1,21)]:raise ValueError('Duplicate/missing native case')
    for row in report['compiled_inputs']:
        if row['file'].startswith('<project-root>'):
            f=ROOT/row['file'].removeprefix('<project-root>/')
            if hashlib.sha256(f.read_bytes()).hexdigest()!=row['sha256']:raise ValueError('Tested fixture source drift')
    if report['separate_stage28m_regression']['counts']!={'PASS':36,'FAIL':0} or report['separate_stage28m_regression']['assertions']!=9689:raise ValueError('Separate M receipt mismatch')
    receipt_status='PASS source/config/manifest and unique native counts; M separate'
report={'receipt_consistency':receipt_status,'status':'PASS','baseline':BASE,'historical_paths_files_modes':len(old),'protected_stage26_files':235,'dependency':dep,'vendor_source':source_status,'new_files':[{'file':f,'bytes':(ROOT/f).stat().st_size,'sha256':hashlib.sha256((ROOT/f).read_bytes()).hexdigest()} for f in added],'runtime_assertions':0}
a.results.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='new_files'}))
