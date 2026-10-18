"""Read-only inventories with the historical tree_hash semantics; no input edits."""
import argparse,hashlib,json,pathlib,os

def inventory(root):
 root=pathlib.Path(root);records=[(str(p.relative_to(root)),hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(root.rglob('*')) if p.is_file() and p.relative_to(root)!=pathlib.Path('installed.json')]
 links=[dict(path=str(p.relative_to(root)),target=os.readlink(p),resolves_to_file=p.is_file()) for p in sorted(root.rglob('*')) if p.is_symlink()]
 return dict(tree_sha256=hashlib.sha256(json.dumps(records,separators=(',',':')).encode()).hexdigest(),files=records,links=links,semantics='sorted Path.rglob; Path.is_file/read_bytes (follows file symlinks); exclude only root installed.json; compact JSON relative path/SHA pairs; no mode or mtime hashing')

def compare(a,b):
 left=dict(a['files']);right=dict(b['files']);return dict(added=sorted(right.keys()-left.keys()),removed=sorted(left.keys()-right.keys()),content_changed=[dict(path=n,before=left[n],after=right[n]) for n in sorted(left.keys()&right.keys()) if left[n]!=right[n]],links_before=a['links'],links_after=b['links'])
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=pathlib.Path,required=True);p.add_argument('--compare',type=pathlib.Path);p.add_argument('--output',type=pathlib.Path,required=True);a=p.parse_args();assert not a.output.exists();out=dict(first=inventory(a.root));
 if a.compare:out.update(second=inventory(a.compare),comparison=compare(out['first'],inventory(a.compare)))
 a.output.write_text(json.dumps(out,indent=2)+'\n')
