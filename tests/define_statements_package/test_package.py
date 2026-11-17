"""Focused new-package controls. Never invokes installer or target verifier."""
import argparse,ast,copy,hashlib,json,pathlib,re,shutil,subprocess,tempfile,zipfile
import package as P

def main(directory,output):
 v=P.load(directory/'preflight.py','package_controls');original=v.validate(directory);results=[]
 def case(name,action):
  observed=action();results.append(dict(case=name,status='PASS',observation=observed))
 def reject(change,resign=None):
  with tempfile.TemporaryDirectory(prefix='define-package-control-') as f:
   root=pathlib.Path(f)/'package';shutil.copytree(directory,root);pins=copy.deepcopy(v.RELEASE['pins']);change(root)
   m=json.loads((root/'manifest.json').read_text())
   if resign:
    for name in resign:
     data=(root/name).read_bytes();m['support_files'][name]=dict(bytes=len(data),sha256=hashlib.sha256(data).hexdigest());v.RELEASE['pins'][name]=hashlib.sha256(data).hexdigest()
    P.write(root/'manifest.json',m)
   try:
    try:v.validate(root)
    except (ValueError,AssertionError,KeyError,OSError) as e:return str(e)
    raise AssertionError('Mutation accepted')
   finally:v.RELEASE['pins']=pins
 def json_change(filename,fn):
  def change(root):
   value=json.loads((root/filename).read_text());fn(value);P.write(root/filename,value)
  return change
 def altered_image(root):
  p=root/'application.bin';b=bytearray(p.read_bytes());b[-1]^=1;p.write_bytes(b)
 case('altered application rejected',lambda:reject(altered_image))
 case('altered receipt rejected',lambda:reject(json_change('independent-gate-result.json',lambda d:d.update(status='PASS'))))
 case('wrong gate status even with consistent support hashes',lambda:reject(json_change('independent-gate-result.json',lambda d:d.update(status='PASS')),['independent-gate-result.json']))
 case('wrong policy label',lambda:reject(json_change('independent-gate-result.json',lambda d:d.update(policy='HISTORICAL_PASS')),['independent-gate-result.json']))
 case('historical gate cannot be relabelled',lambda:reject(json_change('manifest.json',lambda d:d.update(historical_gate='PASS'))))
 case('inventory digest cannot replace manifest hash',lambda:reject(json_change('post-build-attestation.json',lambda d:d.update(build_inputs_sha256=d['files_sha256'])),['post-build-attestation.json']))
 case('wrong original firmware revision',lambda:reject(json_change('manifest.json',lambda d:d.update(firmware_source_commit='0'*40))))
 case('wrong independent verifier revision',lambda:reject(json_change('manifest.json',lambda d:d.update(verification_source_commit='0'*40))))
 case('wrong attestation producer',lambda:reject(json_change('post-build-attestation.json',lambda d:d.update(produced_by_original_builder=True)),['post-build-attestation.json']))
 case('wrong target/attestation binding',lambda:reject(json_change('post-build-attestation.json',lambda d:d.update(usb_observer_target_binding={})),['post-build-attestation.json']))
 case('unsupported physical claim',lambda:reject(json_change('manifest.json',lambda d:d.update(physical_candidate_tested=True))))
 case('wrong rollback bytes',lambda:reject(lambda root:(root/'rollback-application.bin').write_bytes((root/'application.bin').read_bytes())))
 case('working kit cannot become older rollback',lambda:reject(json_change('manifest.json',lambda d:d['working_firmware_return'].update(role='OLDER_ROLLBACK'))))
 case('wrong working kit bytes',lambda:reject(lambda root:(root/'working-define-labels-macos-review-v1.zip').write_bytes(b'wrong')))
 case('unreviewed write range',lambda:reject(json_change('manifest.json',lambda d:d['proposed_writes'][0].update(offset=0))))
 case('installed metadata required',lambda:reject_required(v,directory))
 with zipfile.ZipFile(P.PARENT_ZIP) as z:
  old=z.read('installer.py').decode();new=(directory/'installer.py').read_text()
  normalize=lambda s:re.sub(r'^RELEASE_BINDING=.*$','RELEASE_BINDING=BOUND',s,flags=re.M)
  assert normalize(old)==normalize(new)
  for n in ['install-macos.sh','rollback-macos.sh']:assert z.read(n)==(directory/n).read_bytes()
 case('installer and shell bodies unchanged',lambda:None)
 old=(P.ROOT/'tests/admission_diagnostics_package/package_preflight.py').read_text();new=(directory/'preflight.py').read_text()
 def functions(text):return {n.name:ast.dump(n,include_attributes=False) for n in ast.parse(text).body if isinstance(n,ast.FunctionDef)}
 a,b=functions(old),functions(new)
 for n in ['read','image','rows','check_rows','table','ota','main']:assert a[n]==b[n],n
 case('original image/layout/OTA/CLI predicates unchanged',lambda:None)
 for p in directory.glob('*.py'):ast.parse(p.read_text(),feature_version=(3,8))
 case('Python 3.8 syntax inspected',lambda:None)
 result=dict(status='PASS',cases_executed=len(results),results=results,original_preflight=original,assertion_total='not emitted; not inferred',firmware_compilations=0,hardware_access=False,Mac_execution=False)
 P.write(output,result);print(json.dumps(result,indent=2))
def reject_required(v,d):
 try:v.validate(d,require_installed=True)
 except ValueError:return
 raise AssertionError('Missing installed metadata accepted')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--directory',type=pathlib.Path,required=True);p.add_argument('--output',type=pathlib.Path,required=True);a=p.parse_args();assert not a.output.exists();main(a.directory,a.output)
