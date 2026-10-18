"""Compose the unchanged published STOP/LED source, then one pinned review delta."""
import pathlib,importlib.util,sys,json,subprocess
sys.dont_write_bytecode=True
ROOT=pathlib.Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('caps_led_base',ROOT/'tests/led_return/prepare_sources.py');B=importlib.util.module_from_spec(spec);spec.loader.exec_module(B)
prepare=B.prepare;native_sources=B.native_sources;manifest=B.manifest;sha=B.sha;frameworks=B.frameworks;load=B.load

def delta(s):
 pin=json.loads((ROOT/'docs/caps-queue-source-manifest.json').read_text());patch=ROOT/'tests/caps_queue/fixes.patch';assert sha(patch)==pin['patch_sha256']
 for row in pin['before']:assert sha(s/row['file'])==row['sha256'],row['file']
 subprocess.run(['patch','--batch','--fuzz=0','-p0','-i',str(patch)],cwd=s,check=True,capture_output=True)
 for row in pin['after']:assert sha(s/row['file'])==row['sha256'],row['file']
 return s

def overlay(s):B.overlay(s);return delta(s)
