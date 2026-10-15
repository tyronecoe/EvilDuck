#!/usr/bin/env python3
"""Historical/new-file/publication audit; read-only except new external receipt."""
import argparse,hashlib,json,pathlib,stat,subprocess,sys
sys.dont_write_bytecode=True
ROOT=pathlib.Path(__file__).resolve().parents[2];BASE='134b295deaebcb93f94beb63f2d46f102a7d6555';BRANCH='stage28y-verified-artifact-package'
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
p=argparse.ArgumentParser();p.add_argument('--output',type=pathlib.Path,required=True);p.add_argument('--before',type=pathlib.Path);p.add_argument('--after',type=pathlib.Path);a=p.parse_args();assert not a.output.exists() and ROOT not in a.output.resolve().parents
assert git('branch','--show-current').decode().strip()==BRANCH
head=git('rev-parse','HEAD').decode().strip();assert head==BASE or git('rev-parse','HEAD^').decode().strip()==BASE
old=[]
for row in git('ls-tree','-rz',BASE).split(b'\0'):
 if not row:continue
 meta,name=row.split(b'\t');mode,kind,oid=meta.split();f=ROOT/name.decode();assert not f.is_symlink();data=f.read_bytes();assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==oid.decode();assert bool(f.stat().st_mode&stat.S_IXUSR)==(mode==b'100755');old.append(name.decode())
assert len(old)==1379
subprocess.run([sys.executable,'tests/stage28h/verify_freeze.py'],cwd=ROOT,check=True)
new=sorted(set(git('ls-files','--cached','--others','--exclude-standard').decode().splitlines())-set(old));assert all(n.startswith(('docs/stage28y-','tests/stage28y/')) and pathlib.Path(n).suffix not in ['.bin','.elf','.o','.pyc','.zip'] for n in new)
r=dict(status='PASS',baseline=BASE,head=head,historical_files_bytes_modes=len(old),frozen_stage26=235,hardware=False,new_files=[dict(file=n,bytes=(ROOT/n).stat().st_size,sha256=hashlib.sha256((ROOT/n).read_bytes()).hexdigest()) for n in new if n!='docs/stage28y-integrity.json'])
results=json.loads((ROOT/'docs/stage28y-results.json').read_text());assert results['tests']['counts']=={'PASS':41,'FAIL':0};archive=pathlib.Path('/workspace/outputs')/results['archive']['file'];assert archive.stat().st_size==results['archive']['bytes'] and hashlib.sha256(archive.read_bytes()).hexdigest()==results['archive']['sha256'];r['archive']=results['archive']
if a.before or a.after:
 assert a.before and a.after
 read=lambda p:dict(line.split()[::-1] for line in p.read_text().splitlines());before,after=read(a.before),read(a.after);assert len(before)==49 and all(after.get(k)==v for k,v in before.items());added=set(after)-set(before);assert added=={'refs/heads/'+BRANCH} and after[next(iter(added))]==head;r['publication']='PASS:49 previous remote refs unchanged; only Stage28Y added'
a.output.write_text(json.dumps(r,indent=2)+'\n');print('PASS:1379 historical files,235 frozen files, Y scope/archive/publication checks')
