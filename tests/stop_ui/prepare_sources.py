import pathlib,sys,json,subprocess,importlib.util
sys.dont_write_bytecode=True
ROOT=pathlib.Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('stop_http_sources',ROOT/'tests/http_snapshot/prepare_sources.py');H=importlib.util.module_from_spec(spec);spec.loader.exec_module(H)
sha=H.sha;prepare=H.prepare;native_sources=H.native_sources;frameworks=H.frameworks;manifest=H.manifest
def delta(s):
 pin=json.loads((ROOT/'docs/stop-ui-source-manifest.json').read_text());p=ROOT/'tests/stop_ui/stop.patch';assert sha(p)==pin['patch_sha256']
 for row in pin['before']:
  if not (s/row['file']).exists():
   original=ROOT/'EvilDuckS3'/row['file'];assert sha(original)==row['sha256'];(s/row['file']).write_bytes(original.read_bytes())
  assert sha(s/row['file'])==row['sha256'],row['file']
 subprocess.run(['patch','--batch','--fuzz=0','-p0','-i',str(p)],cwd=s,check=True,capture_output=True)
 for row in pin['after']:assert sha(s/row['file'])==row['sha256'],row['file']
 return s
def overlay(s):H.overlay(s);return delta(s)
