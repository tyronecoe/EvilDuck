#!/usr/bin/env python3
"""EXPERIMENTAL — REVIEW ONLY — NOT AUTHORIZED FOR FLASHING. Offline only."""
import argparse, json, re, shutil, subprocess, sys, tempfile
from pathlib import Path
sys.dont_write_bytecode = True
from patched_core import prepare, check_sources, sha, tree_hash
from s3_validation import ROOT, FQBN, APP_BYTES, LAYOUT, partition_tool, require, validate_properties, validate_image
LABEL = 'EXPERIMENTAL — REVIEW ONLY — NOT AUTHORIZED FOR FLASHING'
BASE = ROOT/'experimental/stage22'
PATCH = ROOT/'proposals/arduino-esp32-3.3.0-stage22-nvs-gate.patch'
PIN = ROOT/'docs/stage22-candidate-pin.json'

def candidate_table(core, path=BASE/'partitions.csv'):
    table = partition_tool(core).PartitionTable.from_csv(Path(path).read_text())
    table.verify()
    require(tuple((p.name,p.type,p.subtype,p.offset,p.size) for p in table)==LAYOUT,'Experimental geometry mismatch')
    require(all(not p.encrypted and p.readonly==(p.name=='nvs') for p in table),'Experimental flags mismatch')
    binary=table.to_binary()
    decoded=partition_tool(core).PartitionTable.from_binary(binary)
    require(decoded.to_binary()==binary,'Table integrity/MD5 mismatch')
    return binary

def check_candidate(core):
    core=Path(core); pin=json.loads(PIN.read_text())
    sdk=core.parents[2]/'tools/esp32-arduino-libs/idf-release_v5.5-b66b5448-v1/esp32s3'
    for name,expected in pin['sdk_inputs'].items():
        require(sha(sdk/name)==expected,'Candidate SDK input mismatch: '+name)
    for name,path in [('patch',PATCH),('gate',BASE/'nvs_gate.h'),('table_header',BASE/'expected_table.h'),('csv',BASE/'partitions.csv')]:
        require(sha(path)==pin[name+'_sha256'],'Candidate input pin mismatch: '+name)
    require(tree_hash(core)==pin['candidate_tree_sha256'],'Candidate core tree mismatch')
    require(sha(core/'cores/esp32/esp32-hal-misc.c')==pin['candidate_misc_sha256'],'Candidate startup source mismatch')
    # Recheck every original dependency pin with a disposable *verification* copy,
    # reverting exactly this one extra patch/header pair, never the installed core.
    with tempfile.TemporaryDirectory(prefix='evilduck-candidate-attest-') as directory:
        checked=Path(directory)/'data/packages/esp32/hardware/esp32/3.3.0'
        checked.parent.mkdir(parents=True);shutil.copytree(core,checked)
        tools=checked.parents[2]/'tools';tools.symlink_to(core.parents[2]/'tools',target_is_directory=True)
        subprocess.run(['patch','--batch','--fuzz=0','-R','-p1','-i',str(PATCH)],cwd=checked,check=True,capture_output=True)
        for name in ['evilduck_nvs_gate.h','evilduck_expected_table.h']:(checked/'cores/esp32'/name).unlink()
        check_sources(checked,True)
    require(sha(core/'cores/esp32/evilduck_nvs_gate.h')==pin['gate_sha256'],'Copied gate mismatch')
    require(sha(core/'cores/esp32/evilduck_expected_table.h')==pin['table_header_sha256'],'Copied table header mismatch')
    binary=candidate_table(core)
    require(bytes(int(x,16) for x in re.findall(r'0x[0-9a-f]{2}', (BASE/'expected_table.h').read_text()))==binary,'Compiled expected-table bytes differ from CSV')
    require(__import__('hashlib').sha256(binary).hexdigest()==pin['partition_sha256'],'Candidate partition pin mismatch')
    return pin

def verify_candidate(core,build):
    core,build=Path(core),Path(build);pin=check_candidate(core)
    props=json.loads((build/'s3-build-properties.json').read_text());validate_properties(props)
    require(Path(props['runtime.platform.path']).resolve()==core.resolve(),'Wrong candidate core selected')
    require((build/'EvilDuckS3.ino.partitions.bin').read_bytes()==candidate_table(core),'Candidate binary table identity mismatch')
    require(candidate_table(core,build/'partitions.csv')==candidate_table(core),'Candidate build CSV mismatch')
    validate_image(build/'EvilDuckS3.ino.bin');validate_image(build/'EvilDuckS3.ino.bootloader.bin',False)
    entries=json.loads((build/'compile_commands.json').read_text())
    misc=next(e for e in entries if Path(e['file']).name=='esp32-hal-misc.c')
    require(Path(misc['file']).resolve()==core/'cores/esp32/esp32-hal-misc.c','Wrong linked startup source')
    cpp=[e for e in entries if Path(e['file']).name=='EvilDuckS3.ino.cpp'][0]
    for flag in ['-DEVILDUCK_DEPLOYMENT_SAFE_START=1','-DEVILDUCK_VERIFIED_HID_ROUTING=1','-DEVILDUCK_VERIFIED_NVS_PRESERVATION=1']:
        require(flag in cpp['arguments'],'Candidate compiler profile mismatch')
    source=(ROOT/'EvilDuckS3/EvilDuckS3.ino').read_text()
    require(source[source.index('void setup() {'):] in Path(cpp['file']).read_text(),'Candidate startup differs from production safe behavior')
    for entry in entries:
        name=Path(entry['file']).name
        if name.endswith('.cpp') and (ROOT/'EvilDuckS3'/name).exists():
            require(Path(entry['file']).read_bytes().endswith((ROOT/'EvilDuckS3'/name).read_bytes()),'Candidate source changed: '+name)
    compiler=Path(cpp['arguments'][0]);prefix=str(compiler).rsplit('g++',1)[0];elf=build/'EvilDuckS3.ino.elf'
    def dis(symbol):return subprocess.run([prefix+'objdump','-d','--disassemble='+symbol,str(elf)],capture_output=True,text=True,check=True).stdout
    init=dis('initArduino');gate=dis('evilduck_nvs_preinit_gate')
    require('evilduck_nvs_preinit_gate' in init and 'nvs_flash_init' in init,'Linked gate/initializer absent')
    require(init.index('evilduck_nvs_preinit_gate')<init.index('nvs_flash_init'),'Gate does not precede initializer')
    between=init[init.index('evilduck_nvs_preinit_gate'):init.index('nvs_flash_init')]
    require(re.search(r'\b(?:bnez|beqz|beq|bne)(?:\.n)?\b',between),'No linked conditional branch between gate and initializer')
    require('nvs_flash_erase' not in init and 'esp_partition_erase_range' not in init,'Erase recovery found')
    require('esp_partition_find' in gate and 'esp_flash_read' in gate and 'esp_partition_verify' in gate,'Linked gate checks absent')
    symbols=subprocess.run([prefix+'nm','-C','--defined-only',str(elf)],capture_output=True,text=True,check=True).stdout
    for s in ['evilduck_nvs_gate_failure','evilduck_nvs_startup_error','tud_hid_set_report_cb','tud_cdc_rx_cb','tud_msc_read10_cb','tud_msc_write10_cb']:
        require(s in symbols,'Missing linked safeguard/integration: '+s)
    require('FeedbackKeyboard::_onOutput(' in symbols and 'FeedbackKeyboard::_onSetFeature(' not in symbols,'Companion mismatch')
    with tempfile.TemporaryDirectory(prefix='candidate-elf-proof-') as t:
        t=Path(t);esptool=Path(props['runtime.tools.esptool_py.path'])/'esptool'
        subprocess.run([str(esptool),'--chip','esp32s3','elf2image','--flash-mode','dio','--flash-freq','80m','--flash-size','16MB','--elf-sha256-offset','0xb0','-o',str(t/'app.bin'),str(elf)],check=True,capture_output=True)
        require((t/'app.bin').read_bytes()==(build/'EvilDuckS3.ino.bin').read_bytes(),'Candidate ELF/bin mismatch')
        subprocess.run([prefix+'objcopy','--dump-section','.flash.rodata='+str(t/'rodata'),str(elf),str(t/'copy.elf')],check=True,capture_output=True)
        data=(t/'rodata').read_bytes()
        require(b'STAGE22_READONLY_QUIESCENT_EXPERIMENTAL_REVIEW_ONLY_NOT_AUTHORIZED_FOR_FLASHING' in data,'Candidate linked identifier absent')
        require(b'DEPLOYMENT SAFE START: application services and payload execution disabled' in data,'Safe-start linked marker absent')
    (build/'EXPERIMENTAL-linked-gate.txt').write_text(LABEL+'\n'+gate)
    (build/'EXPERIMENTAL-linked-initArduino.txt').write_text(LABEL+'\n'+init)
    report=dict(label=LABEL,profile='experimental-readonly-quiescent',pin=pin,base_dependency_pin=json.loads((ROOT/'docs/stage18-dependency-pin.json').read_text()),compiler_sha256=sha(compiler),compiler_version=subprocess.run([str(compiler),'--version'],capture_output=True,text=True,check=True).stdout,fqbn=FQBN,elf_sha256=sha(elf),application_sha256=sha(build/'EvilDuckS3.ino.bin'),partition_sha256=sha(build/'EvilDuckS3.ino.partitions.bin'),gate_precedes_initializer=True,source_pinned=True,physical_authorization=False,hardware_access=False)
    (build/'EXPERIMENTAL-provenance.json').write_text(json.dumps(report,indent=2)+'\n');return report

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['core-dir','user-dir','isolation-dir','build-dir','arduino-cli']:p.add_argument('--'+n,required=True,type=Path)
    p.add_argument('--experimental-readonly-quiescent',action='store_true',required=True)
    p.add_argument('--jobs',type=int,default=2);a=p.parse_args()
    require(a.jobs>0,'jobs must be positive')
    build=a.build_dir.resolve();require(ROOT not in build.parents and build!=ROOT and not build.exists(),'Fresh external build required')
    receipt=prepare(a.core_dir,a.isolation_dir,a.user_dir);core=Path(receipt['core'])
    subprocess.run(['patch','--batch','--forward','--fuzz=0','-p1','-i',str(PATCH)],cwd=core,check=True)
    for src,dst in [('nvs_gate.h','evilduck_nvs_gate.h'),('expected_table.h','evilduck_expected_table.h')]:shutil.copyfile(BASE/src,core/'cores/esp32'/dst)
    check_candidate(core)
    # Byte-identical source snapshot, separate experimental CSV; no production edits.
    sketch=a.isolation_dir/'EXPERIMENTAL-source/EvilDuckS3';sketch.parent.mkdir()
    shutil.copytree(ROOT/'EvilDuckS3',sketch);shutil.copyfile(BASE/'partitions.csv',sketch/'partitions.csv')
    build.mkdir();(build/'EXPERIMENTAL-NOT-AUTHORIZED-FOR-FLASHING.txt').write_text(LABEL+'\n')
    cli=[str(a.arduino_cli),'--config-file',receipt['config']]
    flags='-DEVILDUCK_VERIFIED_HID_ROUTING=1 -DEVILDUCK_VERIFIED_NVS_PRESERVATION=1 -DEVILDUCK_DEPLOYMENT_SAFE_START=1'
    args=['compile','--fqbn',FQBN,'--build-path',str(build),'--build-property','upload.maximum_size='+str(APP_BYTES),'--build-property','compiler.cpp.extra_flags='+flags,'--jobs',str(a.jobs)]
    result=subprocess.run(cli+args+['--show-properties=expanded',str(sketch)],check=True,capture_output=True,text=True)
    props=dict(l.split('=',1) for l in result.stdout.splitlines() if '=' in l);validate_properties(props)
    require(Path(props['runtime.platform.path']).resolve()==core.resolve(),'Unpatched core fallback refused')
    result=subprocess.run(cli+args+['--clean',str(sketch)],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
    print(result.stdout,flush=True);(build/'s3-build.log').write_text(result.stdout)
    (build/'EXPERIMENTAL-NOT-AUTHORIZED-FOR-FLASHING.txt').write_text(LABEL+'\n')
    require(result.returncode==0,'Candidate compiler failed')
    (build/'s3-build-properties.json').write_text(json.dumps(props,indent=2)+'\n')
    program=re.search(r'Sketch uses (\d+) bytes .*Maximum is (\d+) bytes',result.stdout);ram=re.search(r'Global variables use (\d+) bytes',result.stdout)
    require(program and ram and int(program[2])==APP_BYTES,'Compiler resource/slot measurements missing')
    size=(build/'EvilDuckS3.ino.bin').stat().st_size
    report=dict(label=LABEL,core_version='3.3.0',fqbn=FQBN,compiler_program_bytes=int(program[1]),static_ram_bytes=int(ram[1]),application_bytes=size,application_sha256=sha(build/'EvilDuckS3.ino.bin'),free_bytes_per_slot=APP_BYTES-size,free_percent_per_slot=100*(APP_BYTES-size)/APP_BYTES,deployment_safe_start=True,experimental_readonly=True,physical_authorization=False)
    (build/'s3-build-report.json').write_text(json.dumps(report,indent=2)+'\n')
    (build/'EvilDuckS3.ino.merged.bin').unlink(missing_ok=True)
    verify_candidate(core,build);check_sources(a.core_dir)
    # Arduino emits a padded merged image even for compile-only. It is not a candidate artifact.
    (build/'EvilDuckS3.ino.merged.bin').unlink(missing_ok=True)
    (build/'EXPERIMENTAL-NOT-AUTHORIZED-FOR-FLASHING.txt').write_text(LABEL+'\n')
    print(json.dumps(report,indent=2));print(LABEL)
if __name__=='__main__':
    try:main()
    except (ValueError,OSError,subprocess.CalledProcessError) as e:sys.exit('FAIL: '+str(e))
