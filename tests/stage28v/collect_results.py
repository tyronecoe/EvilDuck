#!/usr/bin/env python3
"""Record existing successful runs without relabeling/duplicating comparisons."""
import pathlib,json,hashlib,sys
sys.dont_write_bytecode=True
from prepare_sources import ROOT,sha
p=pathlib.Path(sys.argv[1]);read=lambda name:json.loads((p/name).read_text())
r=dict(primary=read('stage28v-native-final.json'),stage28u=read('stage28v-u-results.json'),stage28t=read('stage28v-t-results.json'),production_comparison=read('stage28v-disabled-results.json'),startup_original=read('stage28v-startup-results.json'),startup_candidate=read('stage28v-startup-candidate-results.json'),preparation=read('stage28v-preparation-results.json'))
r['target_disabled']=read('stage28v-target-disabled/report.json')
r['tested_v_files']=[dict(file=str(f.relative_to(ROOT)),sha256=sha(f)) for f in sorted((ROOT/'tests/stage28v').rglob('*')) if f.is_file()]
r['classification']='56 primary + immutable U/T + original production/startup; disabled candidate runs are separate exact behavior comparisons, not new coverage'
r['superseded_runs']=[dict(run='native-dev',status='compile failure: duplicate platform declarations'),dict(run='native-dev2',status='compile failure: lower NeoPixel mock missing Arduino constrain declaration'),dict(run='native-dev3',status='ASan allocation/deallocation mismatch in inherited native probe; no sanitizer flags weakened'),dict(run='native-dev4',status='48 PASS/402 assertions; superseded by full-module 56-case run, not added'),dict(run='fullweb-dev',status='56 PASS/566 assertions; superseded only to verify final selector-off declaration guard; not added'),dict(run='disabled first invocation',status='runner import error before compilation; corrected import')]
r['primary']['scope']='Entire patched webserver.cpp is included in test_main.cpp; web_handlers.inc is unused symbol/body receipt output, not replacement logic. Lower network, NVS, File, USB, clock, NeoPixel and task primitives simulated.'
(ROOT/'docs/stage28v-native-results.json').write_text(json.dumps(r,indent=2)+'\n')
(ROOT/'docs/stage28v-target-object-results.json').write_bytes((p/'stage28v-target-verified/report.json').read_bytes())
