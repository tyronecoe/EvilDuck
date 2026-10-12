#!/usr/bin/env python3
"""Private-value-free synthetic NVS checks; owner backups are never loaded."""
import argparse,hashlib,importlib.util,json,struct,subprocess,sys,tempfile,os
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools'))
from nvs_inspect import inspect,crc
from nvs_source_prepare import verify
ROWS=[];ASSERTIONS=0
def check(x,message):
 global ASSERTIONS
 ASSERTIONS+=1
 if not x:raise AssertionError(message)
def case(name,fn):
 before=ASSERTIONS
 try:fn();status='PASS';error=''
 except Exception as e:status='FAIL';error=str(e)
 ROWS.append(dict(name=name,status=status,assertions=ASSERTIONS-before,error=error));print(status,name,error,flush=True)
def header(data,p=0,state=0xfffffffe,seq=1,version=0xfe):
 o=p*4096;struct.pack_into('<II',data,o,state,seq);data[o+8]=version;struct.pack_into('<I',data,o+28,crc(data[o+4:o+28]))
def item(data,i,ns,typ,key,payload,span=1,p=0):
 o=p*4096+64+32*i;raw=bytearray(b'\xff'*32);raw[:4]=bytes([ns,typ,span,255]);raw[8:8+len(key)]=key;raw[8+len(key)]=0
 if typ==0x21:
  struct.pack_into('<H',raw,24,len(payload));struct.pack_into('<I',raw,28,crc(payload));data[o+32:o+32+len(payload)]=payload
 else:raw[24:24+len(payload)]=payload
 struct.pack_into('<I',raw,4,crc(raw[:4]+raw[8:]));data[o:o+32]=raw
 for j in range(i,i+span):data[p*4096+32+j//4]&=~(1<<((j%4)*2))
def healthy():
 d=bytearray(b'\xff'*0x5000);header(d);item(d,0,0,1,b'private-ns',b'\x01');item(d,1,1,1,b'private-key',b'\x01');return d

def main():
 p=argparse.ArgumentParser();p.add_argument('--sdk-source',type=Path,required=True);p.add_argument('--generator-dir',type=Path,required=True);p.add_argument('--results',type=Path,required=True);a=p.parse_args();verify(a.sdk_source)
 pin=json.loads((ROOT/'docs/stage19-generator-pin.json').read_text())
 for row in pin['files']:
  if hashlib.sha256((a.generator_dir/row['path']).read_bytes()).hexdigest()!=row['sha256']:raise ValueError('Generator source checksum mismatch')
 def run_mutate(fn,expected,code):
  d=healthy();fn(d);before=bytes(d);r=inspect(d);check(r['classification']==expected,'classification '+r['classification']);check(any(x['code']==code for x in r['issues']),'issue code');check(bytes(d)==before,'input unchanged')
 case('nvs_valid_numeric',lambda:check(inspect(healthy())['classification']=='compatible-within-verified-checks','healthy structure'))
 case('nvs_all_erased',lambda:check(inspect(b'\xff'*0x5000)['classification']=='compatible-within-verified-checks','fresh defaults structure only'))
 for size in [0,4096,0x4fff,0x5001]:case('nvs_size_'+str(size),lambda size=size:check(inspect(b'\xff'*size)['classification']=='invalid','exact size required'))
 case('nvs_header_crc',lambda:run_mutate(lambda d:d.__setitem__(28,d[28]^1),'invalid','page_header_crc'))
 case('nvs_future_version',lambda:run_mutate(lambda d:header(d,version=0xfd),'unsupported-format','page_version'))
 case('nvs_legacy_version_conservative',lambda:run_mutate(lambda d:header(d,version=0xff),'unsupported-format','page_version'))
 case('nvs_freeing',lambda:run_mutate(lambda d:header(d,state=0xfffffff8),'recovery-potentially-required','freeing_page'))
 case('nvs_incomplete_entry',lambda:run_mutate(lambda d:d.__setitem__(128,0),'recovery-potentially-required','incomplete_entry_write'))
 case('nvs_entry_crc',lambda:run_mutate(lambda d:d.__setitem__(100,d[100]^1),'recovery-potentially-required','entry_header_crc'))
 case('nvs_illegal_bitmap',lambda:run_mutate(lambda d:d.__setitem__(32,(d[32]&~12)|4),'recovery-potentially-required','illegal_entry_state'))
 case('nvs_reserved_bitmap',lambda:run_mutate(lambda d:d.__setitem__(63,d[63]&15),'invalid','bitmap_reserved_bits'))
 case('nvs_duplicate_live_record',lambda:run_mutate(lambda d:item(d,2,1,1,b'private-key',b'\x02'),'recovery-potentially-required','duplicate_live_record'))
 case('nvs_multiple_active',lambda:run_mutate(lambda d:header(d,p=1,seq=2),'recovery-potentially-required','multiple_active_pages'))
 case('nvs_sequence_duplicate',lambda:run_mutate(lambda d:header(d,p=1,state=0xfffffffc),'recovery-potentially-required','duplicate_page_sequence'))
 def no_free(d):
  for p in range(5):header(d,p=p,state=0xfffffffc,seq=p+1)
 case('nvs_no_free_page',lambda:run_mutate(no_free,'recovery-potentially-required','no_erased_free_page'))
 case('nvs_bad_namespace',lambda:run_mutate(lambda d:item(d,2,2,1,b'unknown-key',b'\x01'),'insufficient-evidence','namespace_reference_unresolved'))
 case('nvs_unknown_type',lambda:run_mutate(lambda d:item(d,2,1,0x77,b'private-key2',b'\x01'),'unsupported-format','entry_type'))
 case('nvs_numeric_span',lambda:run_mutate(lambda d:item(d,2,1,1,b'private-key2',b'\x01',span=2),'invalid','numeric_or_index_span'))
 case('nvs_blob_index_invalid_size',lambda:run_mutate(lambda d:item(d,2,1,0x48,b'private-key2',b'\x01'),'invalid','blob_index_size_limit'))
 case('nvs_dirty_erased_page',lambda:run_mutate(lambda d:d.__setitem__(4096+64,0),'recovery-potentially-required','dirty_uninitialized_page'))
 def string_fixture():
  d=healthy();item(d,2,1,0x21,b'private-secret',b'synthetic-password\0',span=2);return d
 case('nvs_valid_string_crc',lambda:check(inspect(string_fixture())['classification']=='compatible-within-verified-checks','checked string structure'))
 def string_crc():
  d=string_fixture();d[160]^=1;r=inspect(d);check(r['classification']=='recovery-potentially-required','data crc recovery');check(any(x['code']=='variable_data_crc' for x in r['issues']),'data crc code')
 case('nvs_string_data_crc',string_crc)
 def privacy():
  d=string_fixture();before=bytes(d);r=inspect(d);j=json.dumps(r);check(all(s not in j for s in ['private-ns','private-key','private-secret','synthetic-password']),'private strings absent');check(bytes(d)==before,'no mutation');check(r['settings_values_validated'] is False and r['sdk_immutability_verified'] is False,'no false guarantee')
 case('nvs_report_privacy',privacy)
 def generator():
  gen=a.sdk_source/'components/nvs_flash/nvs_partition_generator/nvs_partition_gen.py'
  with tempfile.TemporaryDirectory(prefix='evilduck-nvs-synthetic-') as t:
   t=Path(t);csv=t/'input.csv';csv.write_text('key,type,encoding,value\nsynthetic,namespace,,\nflag,data,u8,1\ntext,data,string,synthetic-secret\n')
   env=dict(os.environ);env['PYTHONPATH']=str(a.generator_dir);env['PYTHONDONTWRITEBYTECODE']='1'
   result=subprocess.run([sys.executable,str(gen),'generate',str(csv),str(t/'nvs.bin'),'0x5000'],env=env,capture_output=True,text=True)
   if result.returncode:raise RuntimeError('Official generator failed: '+result.stderr)
   r=inspect((t/'nvs.bin').read_bytes());check(r['classification']=='compatible-within-verified-checks','official generator CRC/geometry');check('synthetic-secret' not in json.dumps(r),'generator report private')
 case('nvs_official_generator_vector',generator)
 def cli_safety():
  with tempfile.TemporaryDirectory(prefix='evilduck-nvs-cli-') as t:
   t=Path(t);full=t/'full.bin';d=bytearray(b'\xff'*0x1000000);d[0x9000:0xe000]=healthy();full.write_bytes(d);digest=hashlib.sha256(d).hexdigest();output=t/'report.json'
   cmd=[sys.executable,str(ROOT/'tools/nvs_inspect.py'),'--full-backup',str(full),'--output',str(output)]
   check(subprocess.run(cmd,capture_output=True).returncode==0,'read-only CLI succeeds');check(subprocess.run(cmd,capture_output=True).returncode!=0,'existing output refused');check(hashlib.sha256(full.read_bytes()).hexdigest()==digest,'full input unchanged')
   full.write_bytes(d[:-1]);output.unlink();check(subprocess.run(cmd,capture_output=True).returncode!=0,'truncated full backup refused')
 case('nvs_cli_read_only_and_overwrite_guards',cli_safety)
 out=dict(results=ROWS,counts={s:sum(r['status']==s for r in ROWS) for s in ['PASS','FAIL']},assertions=ASSERTIONS,owner_files_inspected=False,hardware_access=False)
 a.results.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='results'},indent=2));return bool(out['counts']['FAIL'])
if __name__=='__main__':raise SystemExit(main())
