#!/usr/bin/env python3
"""Collect named fresh X receipts; never runs hardware or changes old reports."""
import pathlib,json,sys
sys.dont_write_bytecode=True
from prepare_sources import ROOT,sha
p=pathlib.Path(sys.argv[1]);read=lambda n:json.loads((p/n).read_text())
r=dict(primary=read('stage28x-native-verified.json'),framework=read('stage28x-framework/report.json'),stage28w=read('stage28x-reg-stage28w.json'),stage28v=read('stage28x-reg-stage28v.json'),stage28u=read('stage28x-reg-stage28u.json'),stage28t=read('stage28x-reg-stage28t.json'),production=read('stage28x-reg-production.json'),startup=read('stage28x-reg-startup.json'))
groups=[r['primary']['primary'],r['framework'],r['stage28w'],r['stage28v'],r['stage28u'],r['stage28t']['primary'],r['production']['suites']['original'],r['startup']]
assert all(x['counts']['FAIL']==0 for x in groups)
r['totals_unique_current_coverage']=dict(PASS=sum(x['counts']['PASS'] for x in groups),FAIL=0,assertions=sum(x['assertions'] for x in groups))
assert r['totals_unique_current_coverage']==dict(PASS=332,FAIL=0,assertions=72251)
r['comparisons_not_extra_coverage']={'instrumented_W':r['primary']['w_instrumented_comparison']['counts'],'selector_off_production':r['production']['suites']['disabled']['counts']}
r['classifications']=dict(historical='No historical classification or old report changed. Older language XPASS/USB XFAIL/Stage9 and watchdog observations not rerun or added to current counts.',scope='Relevant owner/backend/storage/startup/framework suites; not an unrelated all-history rerun',superseded='Initial native include layout errors corrected; a concurrent development rerun used older allocation shim with a newly edited test and failed negative linking. Final verified sources are stable. Earlier successful native run tightened X10 contention and was replaced; initial target link before final header/mock-clock refinement is superseded, not counted.',physical='NOT EXECUTED',SDK_resource_execution='Target SDK APIs linked/disassembled; native resources/clock/tasks are named mocks, not full SDK/FreeRTOS execution')
(ROOT/'docs/stage28x-test-results.json').write_text(json.dumps(r,indent=2)+'\n')
for src,dst in [('stage28x-linked-enabled-publication.json','docs/stage28x-linked-enabled.json'),('stage28x-linked-off-final-publication.json','docs/stage28x-linked-diagnostics-off.json')]:
 (ROOT/dst).write_bytes((p/src).read_bytes())
a=read('stage28x-audit-first.json')
(ROOT/'docs/stage28x-source-evidence.json').write_text(json.dumps(a['source_evidence'],indent=2)+'\n')
(ROOT/'docs/stage28x-artifact-plan.json').write_text(json.dumps(a['artifact_plan'],indent=2)+'\n')
(ROOT/'docs/stage28x-protected-refs.json').write_text(json.dumps(dict(line.split()[::-1] for line in (p/'stage28x-remote-before.txt').read_text().splitlines()),indent=2)+'\n')
print(r['totals_unique_current_coverage'])
