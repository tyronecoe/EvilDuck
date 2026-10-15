#!/usr/bin/env python3
"""Collect actual completed receipts; no tests or hardware operations are run here."""
import json,pathlib,sys
sys.dont_write_bytecode=True
from prepare_sources import ROOT,sha
P=pathlib.Path(sys.argv[1]);read=lambda name:json.loads((P/name).read_text())
r=dict(primary=read('stage28w-native-verified.json'),framework_components=read('stage28w-framework-dev/report.json'),stage28v=read('stage28w-v-results.json'),stage28u=read('stage28w-u-results.json'),stage28t=read('stage28w-t-results.json'),production_comparison=read('stage28w-production-results.json'),startup=read('stage28w-startup-results.json'))
# The native runner snapshots all W files at completion; only C++/header inputs
# are native compilation evidence. Post-link/audit Python is verified separately.
r['primary']['tested_w_files']=[x for x in r['primary']['tested_w_files'] if pathlib.Path(x['file']).suffix in ['.cpp','.h','.inc']]
r['classifications']=dict(native_source='actual patched app bodies; named lower mocks',framework_source='selected exact pinned response class/constructor/read/destructor bodies; mocked abstract base/File; not request/TCP task execution',old_suites='unchanged expectations, separate V/U/T runs',comparisons='selector-off comparison is not extra coverage',superseded=['two32-case W runs (364 assertions each), before final settings-snapshot audit; not added','initial successful controlled links before final settings-snapshot guards; not added','post-link inspector initially expected unsigned-int rather than pinned target unsigned-long mangling; corrected against actual nm/disassembly','initial dump-section inspection rewrote scratch ELFs; corrected to an explicit inspection output; saved link commands restored exact original ELF hashes; final post-link checks verify unchanged artifacts'])
(ROOT/'docs/stage28w-test-results.json').write_text(json.dumps(r,indent=2)+'\n')
for src,dst in [('stage28w-link-enabled-publication.json','docs/stage28w-linked-enabled.json'),('stage28w-link-disabled-publication.json','docs/stage28w-linked-selector-off.json')]:
 (ROOT/dst).write_bytes((P/src).read_bytes())
