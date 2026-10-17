#!/usr/bin/env python3
"""Read-only scope, frozen source, rollback artifact and publication checks."""
import pathlib,sys,subprocess,json,hashlib,stat,argparse
sys.dont_write_bytecode=True
ROOT=pathlib.Path(__file__).resolve().parents[2];BASE='6280b1d7b465f5d29800fa230ab60f3b04bf77c4'
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--output',type=pathlib.Path,required=True);p.add_argument('--before',type=pathlib.Path);p.add_argument('--after',type=pathlib.Path);a=p.parse_args();assert not a.output.exists();assert git('merge-base','--is-ancestor',BASE,'HEAD')==b''
old=[]
for row in git('ls-tree','-rz',BASE).split(b'\0'):
 if not row:continue
 meta,name=row.split(b'\t');mode,kind,oid=meta.split();f=ROOT/name.decode();assert kind==b'blob' and not f.is_symlink();d=f.read_bytes();assert hashlib.sha1(b'blob '+str(len(d)).encode()+b'\0'+d).hexdigest()==oid.decode(),name;assert bool(f.stat().st_mode&stat.S_IXUSR)==(mode==b'100755');old.append(name.decode())
subprocess.run([sys.executable,str(ROOT/'tests/stage28h/verify_freeze.py')],check=True)
new=sorted(set(git('ls-files','--cached','--others','--exclude-standard').decode().splitlines())-set(old));assert all(n.startswith(('docs/keyboard-shortcuts-','tests/keyboard_shortcuts/')) and pathlib.Path(n).suffix not in ['.bin','.elf','.pyc','.o'] for n in new),new
archive=ROOT/'downloads/evilduck-stage28y-public.zip';assert archive.stat().st_size==4837000 and sha(archive)=='6cfe4b33bda853004f6af4672b553700e1756a6feeda9bd4579dd27cbf3a705f'
x=pathlib.Path('/workspace/tooling/stage28x-linked-enabled-final/build/EvilDuckS3.ino.bin');original_x=None
if x.exists():
 assert sha(x)=='a0cefdbb8ff9915e58b9142841b4c015dd738406c6861ef5f8e4c3f9105cffc4';original_x=dict(bytes=x.stat().st_size,sha256=sha(x))
r=dict(status='PASS',base=BASE,historical_files_unchanged_bytes_modes=len(old),frozen_stage26=235,original_x_workspace_artifact=original_x,unchanged_public_archive=dict(bytes=archive.stat().st_size,sha256=sha(archive)),new_files=[dict(file=n,bytes=(ROOT/n).stat().st_size,sha256=sha(ROOT/n)) for n in new if n!='docs/keyboard-shortcuts-integrity.json'],hardware=False)
if a.before or a.after:
 assert a.before and a.after
 read=lambda f:dict(line.split()[::-1] for line in f.read_text().splitlines())
 before,after=read(a.before),read(a.after);assert all(after.get(k)==v for k,v in before.items());assert set(after)-set(before)=={'refs/heads/routeb-transient-keyboard-shortcuts'};assert after['refs/heads/routeb-transient-keyboard-shortcuts']==git('rev-parse','HEAD').decode().strip();r['publication']=dict(prior_refs_unchanged=len(before),new_ref='refs/heads/routeb-transient-keyboard-shortcuts',commit=after['refs/heads/routeb-transient-keyboard-shortcuts'])
a.output.write_text(json.dumps(r,indent=2)+'\n');print('PASS',len(old),'historical files/modes and 235 frozen files preserved')
