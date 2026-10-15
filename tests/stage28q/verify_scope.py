#!/usr/bin/env python3
"""Read-only scope, references, exact-source and native receipt validation."""
import argparse,hashlib,json,pathlib,stat,subprocess,sys,re
sys.dont_write_bytecode=True
ROOT=pathlib.Path(__file__).resolve().parents[2];BASE='f1ca7ffdfc5499a1ffd7dff4b126b0024e022c25'
p=argparse.ArgumentParser();p.add_argument('--output',type=pathlib.Path,required=True);p.add_argument('--references',type=pathlib.Path,required=True);p.add_argument('--p-source',type=pathlib.Path,required=True);p.add_argument('--protected-core',type=pathlib.Path);p.add_argument('--remote-before',type=pathlib.Path);p.add_argument('--remote-after',type=pathlib.Path);a=p.parse_args();assert not a.output.exists() and not a.output.resolve().is_relative_to(ROOT)
def git(*v):return subprocess.check_output(['git',*v],cwd=ROOT)
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
old=[]
for e in git('ls-tree','-rz',BASE).split(b'\0'):
 if not e:continue
 meta,name=e.split(b'\t');mode,kind,oid=meta.split();f=ROOT/name.decode();assert kind==b'blob' and f.read_bytes()==git('cat-file','blob',oid.decode());assert bool(f.stat().st_mode&stat.S_IXUSR)==(mode==b'100755');old.append(name.decode())
assert len(old)==1139 and not set(git('diff',BASE,'--name-only').decode().splitlines())&set(old)
new=sorted(set(git('ls-files','--cached','--others','--exclude-standard').decode().splitlines())-set(old));assert all(f.startswith(('docs/stage28q-','tests/stage28q/')) for f in new)
subprocess.run([sys.executable,'tests/stage28h/verify_freeze.py'],cwd=ROOT,check=True)
m=json.loads((ROOT/'docs/stage28q-source-and-model-manifest.json').read_text());assert sha(ROOT/'docs/stage28p-source-and-boundary-manifest.json')==m['p_manifest_sha256']
for row in m['references']:assert sha(a.references/row['file'])==row['sha256']
pin=json.load(open(ROOT/'docs/stage28p-source-and-boundary-manifest.json'));driver=a.p_source/'builder/dcd_dwc2.c';assert sha(driver)==next(r['sha256'] for r in pin['new_inputs'] if r['file']=='dcd_dwc2.c')
text=driver.read_text();start=text.index('static void edpt_disable(');end=text.index('// Since this function returns void',start);body=text[start:end]
positions=[body.index(v) for v in ['dep->diepctl |= DIEPCTL_SNAK;','while ((dep->diepint & DIEPINT_INEPNE)','dep->diepctl |= DIEPCTL_EPDIS','while ((dep->diepint & DIEPINT_EPDISD_Msk)','dep->diepint = DIEPINT_EPDISD;','dfifo_flush_tx(dwc2, epnum);']];assert positions==sorted(positions)
types=(a.p_source/'src/portable/synopsys/dwc2/dwc2_type.h').read_text()
for name,bit in [('XFRC',0),('EPDISD',1),('INEPNE',6),('TXFE',7)]:assert re.search(r'#define DIEPINT_'+name+r'_Pos\s+\('+str(bit)+r'U\)',types)
core='NOT REQUESTED'
if a.protected_core:
 sys.path.insert(0,str(ROOT/'tools'));import patched_core
 patched_core.check_sources(a.protected_core,patched=True);core='PASS unchanged pinned protected core/SDK'
f=ROOT/'docs/stage28q-test-results.json';receipt='NOT PRESENT'
if f.exists():
 r=json.loads(f.read_text());assert r['manifest_sha256']==sha(ROOT/'docs/stage28q-source-and-model-manifest.json');rows=r['primary']['results'];assert [v['id'] for v in rows]==['Q%02d'%i for i in range(1,38)];assert r['primary']['counts']=={'PASS':37,'FAIL':0} and sum(v['assertions'] for v in rows)==r['primary']['assertions']
 for row in r['fixtures']:assert sha(ROOT/row['file'])==row['sha256'],row['file']
 assert r['separate_unchanged_P']['primary']['counts']=={'PASS':33,'FAIL':0} and r['separate_unchanged_P']['primary']['assertions']==167
 receipt='PASS unique cases, tested model/manifest hashes and separate P counts'
remote='NOT REQUESTED'
if a.remote_before and a.remote_after:
 def refs(f):return dict(line.split()[::-1] for line in f.read_text().splitlines())
 before,after=refs(a.remote_before),refs(a.remote_after);assert len(before)==41 and all(after.get(k)==v for k,v in before.items());extra=set(after)-set(before);assert extra=={'refs/heads/stage28q-endpoint-retirement-fence'} and after[next(iter(extra))]==git('rev-parse','HEAD').decode().strip();remote='PASS41 old refs unchanged; new Q ref only'
x={'status':'PASS','baseline':BASE,'historical_paths_files_modes':len(old),'frozen_stage26_files':235,'references_verified':len(m['references']),'core_sdk':core,'receipt':receipt,'remote':remote,'source_order_and_bit_crosscheck':'PASS; establishes source syntax/order, NOT silicon handshake semantics','new_file_count':len(new),'new_files':[dict(file=f,size=(ROOT/f).stat().st_size,sha256=sha(ROOT/f)) for f in new if f!='docs/stage28q-integrity.json'],'integrity_self_excluded':True,'runtime_assertions':0};a.output.write_text(json.dumps(x,indent=2)+'\n');print(json.dumps({k:v for k,v in x.items() if k!='new_files'}))
