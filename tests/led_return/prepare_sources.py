import pathlib,sys,json,subprocess,importlib.util
sys.dont_write_bytecode=True
ROOT=pathlib.Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('led_a_sources',ROOT/'tests/stop_ui/prepare_sources.py');A=importlib.util.module_from_spec(spec);spec.loader.exec_module(A)
H=A.H;load=H.load;sha=A.sha;prepare=A.prepare;native_sources=A.native_sources;frameworks=A.frameworks;manifest=A.manifest
def delta(s):
 pin=json.loads((ROOT/'docs/led-return-source-manifest.json').read_text());p=ROOT/'tests/led_return/receiver.patch';assert sha(p)==pin['patch_sha256']
 for row in pin['before']:assert sha(s/row['file'])==row['sha256'],row['file']
 subprocess.run(['patch','--batch','--fuzz=0','-p0','-i',str(p)],cwd=s,check=True,capture_output=True)
 for row in pin['after']:assert sha(s/row['file'])==row['sha256'],row['file']
 for row in pin['additions']:
  p=ROOT/'tests/led_return'/row['file'];assert sha(p)==row['sha256'];(s/row['file']).write_bytes(p.read_bytes())
 return s
def overlay(s):A.overlay(s);return delta(s)
