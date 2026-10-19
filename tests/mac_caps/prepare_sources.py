"""Pinned additive overlay on the selected custom Caps/Queue composition."""
import pathlib,sys,json,subprocess,importlib.util
sys.dont_write_bytecode=True
ROOT=pathlib.Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('mac_caps_base',ROOT/'tests/caps_duration/prepare_sources.py');B=importlib.util.module_from_spec(spec);spec.loader.exec_module(B)
prepare=B.prepare;native_sources=B.native_sources;manifest=B.manifest;frameworks=B.frameworks;sha=B.sha;load=B.load

def delta(s):
 m=json.loads((ROOT/'docs/mac-caps-source-manifest.json').read_text());p=ROOT/'tests/mac_caps/application.patch';assert sha(p)==m['patch_sha256']
 for r in m['before']:assert sha(s/r['file'])==r['sha256'],r['file']
 subprocess.run(['patch','--batch','--fuzz=0','-p0','-i',str(p)],cwd=s,check=True,capture_output=True)
 for r in m['after']:assert sha(s/r['file'])==r['sha256'],r['file']
 for r in m['additions']:
  f=ROOT/'tests/mac_caps'/r['file'];assert sha(f)==r['sha256'];(s/r['file']).write_bytes(f.read_bytes())
 return s
def overlay(s):B.overlay(s);return delta(s)
