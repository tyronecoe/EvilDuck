#!/usr/bin/env python3
"""Build ONLY the pinned esptool argument parser from its real AST.
The function is truncated immediately after parse_args: no connect/flash code
is compiled into this harness. Input operations are argument data, not executed.
Run with the isolated esptool4.12.0 environment, never an attached device.
"""
import argparse,ast,hashlib,inspect,json,pathlib
import esptool
p=argparse.ArgumentParser();p.add_argument('--directory',type=pathlib.Path,required=True);p.add_argument('--results',type=pathlib.Path,required=True);a=p.parse_args();assert not a.results.exists();assert esptool.__version__=='4.12.0'
src=pathlib.Path(inspect.getfile(esptool)).read_bytes()
assert hashlib.sha256(src).hexdigest()=='96513abe8944836630610465e5fab03c4da9a4bc9d27f177413f6547f859430e'
mod=ast.parse(src);fn=next(x for x in mod.body if isinstance(x,ast.FunctionDef) and x.name=='main');body=[]
for statement in fn.body:
 body.append(statement)
 if isinstance(statement,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='args' for t in statement.targets):break
else:raise AssertionError('parse_args boundary absent')
assert isinstance(body[-1].value,ast.Call) and isinstance(body[-1].value.func,ast.Attribute) and body[-1].value.func.attr=='parse_args'
fn.body=body+[ast.Return(value=ast.Name(id='args',ctx=ast.Load()))];fn.name='parse_only';ns=dict(esptool.__dict__);exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),'parser-only','exec'),ns)
common=['--chip','esp32s3','--port','SYNTHETIC-NOT-A-DEVICE','--baud','115200','--before','no_reset','--after','no_reset','--no-stub']
commands=[['version'],['flash_id'],['get_security_info'],['read_flash','0x8000','0x1000','synthetic-table.bin'],['read_flash','0xe000','0x2000','synthetic-ota.bin'],['read_flash','0x0','0x1000000','synthetic-full.bin']]
for image in ['application.bin','rollback-application.bin']:
 for operation in ['write_flash','verify_flash']:
  args=[operation,'--flash_mode','keep','--flash_freq','keep','--flash_size','keep']
  if operation=='write_flash':args+=['--no-compress']
  args+=['0x10000',str(a.directory/image),'0x750000',str(a.directory/image)];commands.append(args)
  if operation=='verify_flash':
   for offset in ['0x10000','0x750000']:commands.append([operation,'--flash_mode','keep','--flash_freq','keep','--flash_size','keep',offset,str(a.directory/image)])
for args in commands:
 r=ns['parse_only'](common+args);assert r.chip=='esp32s3' and r.no_stub and r.before=='no_reset' and r.after=='no_reset';assert r.operation==args[0]
 if args[0] in ['write_flash','verify_flash']:
  assert [addr for addr,f in r.addr_filename]==[int(x,16) for x in args if x in ['0x10000','0x750000']]
  for addr,f in r.addr_filename:f.close()
  assert r.flash_size==r.flash_mode==r.flash_freq=='keep'
out=dict(parser_cases_pass=len(commands),unexpected_fail=0,scope='real esptool4.12.0 parser AST only; no connection or operation dispatcher included',esptool_source_sha256=hashlib.sha256(src).hexdigest(),hardware_access=False,flash_operation_executed=False,native_high_sierra='PENDING OWNER')
a.results.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
