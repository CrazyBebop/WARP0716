"""Build the import-free DX9Ex world-depth isolation payload for WARP.

Compiler outputs live only in TemporaryDirectory; the generated text payload
and its hashes are the maintained dependency, not copied test executables.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess
import tempfile

import pefile
from js_data_format import js_statement

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'tools/native/hat_effect_world_depth.cpp'
TEMPLATE = ROOT / 'Scripts/Runtime/HatEffectWorldDepth/patch.qjs.in'
PATCH = ROOT / 'Scripts/Patches/AllHatEffectsWorldDepthOracle.qjs'
ORIGINAL = ROOT / '2025-07-16_Ragexe_175220998_clientinfo/2025-07-16_Ragexe_175220998_clientinfo.exe'
COMPILER = Path('C:/Program Files/Microsoft Visual Studio/18/Community/VC/Tools/MSVC/14.51.36231/bin/Hostx64/x86/cl.exe')


def build(check=False):
    with tempfile.TemporaryDirectory(prefix='hat-depth-build-', dir=ROOT / 'Outputs') as folder:
        folder = Path(folder)
        obj, exe = folder / 'depth.obj', folder / 'depth.exe'
        for command in [
            [str(COMPILER), '/nologo', '/c', '/O2', '/Oi', '/GS-', '/GR-', '/Zl',
             '/W4', '/WX', '/EHs-c-', '/arch:SSE2', '/Fo' + str(obj), str(SOURCE)],
            [str(COMPILER.parent / 'link.exe'), '/nologo', '/nodefaultlib', '/machine:x86',
             '/safeseh:no', '/entry:HatDepthEntry', '/subsystem:windows', '/base:0x10000000',
             '/fixed:no', '/dynamicbase', '/opt:ref', '/incremental:no', '/brepro', '/out:' + str(exe), str(obj)],
        ]:
            subprocess.run(command, check=True, cwd=folder)
        pe = pefile.PE(data=exe.read_bytes())
        assert not getattr(pe, 'DIRECTORY_ENTRY_IMPORT', None)
        sections = [s for s in pe.sections if not s.Name.startswith(b'.reloc')]
        start = min(s.VirtualAddress for s in sections)
        end = max(s.VirtualAddress + s.Misc_VirtualSize for s in sections)
        data = bytearray(end - start)
        for section in sections:
            at = section.VirtualAddress - start
            raw_section = section.get_data()[:section.Misc_VirtualSize]
            data[at:at + len(raw_section)] = raw_section
        exports = {s.name.decode(): s.address - start for s in pe.DIRECTORY_ENTRY_EXPORT.symbols}
        for index in [0, 6]:
            directory = pe.OPTIONAL_HEADER.DATA_DIRECTORY[index]
            if directory.Size:
                at = directory.VirtualAddress - start
                assert 0 <= at <= len(data) - directory.Size
                data[at:at + directory.Size] = bytes(directory.Size)
        relocations = []
        image_base = pe.OPTIONAL_HEADER.ImageBase + start
        for block in pe.DIRECTORY_ENTRY_BASERELOC:
            for row in block.entries:
                if not row.type:
                    continue
                assert row.type == 3
                at = row.rva - start
                assert 0 <= at <= len(data) - 4
                value = int.from_bytes(data[at:at + 4], 'little')
                assert image_base <= value < image_base + len(data), (hex(at), hex(value), hex(image_base), len(data))
                relocations.append(at)
        payload = dict(imageBase=image_base, hex=data.hex(), relocations=relocations, exports=exports,
                       source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest())
    # Full neighboring WARP banner, normalized to the mandatory 76 columns.
    banner = TEMPLATE.read_text(encoding='utf-8').splitlines()
    end = next(i for i, line in enumerate(banner) if line.startswith('\\***'))
    banner = banner[:end + 1]
    for i, line in enumerate(banner):
        if 'Description   :' in line:
            first = i
        if 'Evidence      :' in line:
            last = i
            break
    replacement = [
        '*   Description   : 2025-07-16 DX9Ex: HatEffects test only world depth.',
        '*                   Native world passes replay without color writes;',
        '*                   actor depth and before/after queues stay original.',
        '*                   On capture failure and DX7, retain stock effects.',
        '*                   Replaces rejected sprite-plane workaround (#77).',
        '*   Generator     : tools/build_hat_effect_world_depth.py',
    ]
    banner[first:last] = [line.ljust(75) + '*' for line in replacement]
    banner = [line.replace('docs/sprite-quad-depth.md', 'tools/hat-effect-world-depth.md')
              .replace('tools/verify_uniform_sprite_rhw.py', 'tools/verify_hat_effect_world_depth.py')
              .replace('2026-10-12', '2026-11-04') for line in banner]
    banner = [line[:-1].rstrip().ljust(75) + line[-1] if line.startswith('*') else line for line in banner]
    original = pefile.PE(data=ORIGINAL.read_bytes(), fast_load=True)
    checks = [dict(name=name, va=va, bytes=original.get_data(va - 0x400000, size).hex(' ')) for name, va, size in [
        ('polygon tag hook', 0xAD9413, 5), ('world capture hook', 0x55E685, 6),
        ('device reset hook', 0x542B26, 6), ('renderer destructor hook', 0x55C189, 6),
        ('DX9Ex frame call', 0x55CA9C, 5), ('DX9Ex draw vtable slots', 0xFD6D98, 8),
        ('DX9Ex 32-byte draw', 0x55C830, 0x89), ('DX9Ex 40-byte draw', 0x55C8C0, 0x89),
        ('native world ground1', 0x55D680, 0x1D0), ('native world ground2', 0x55D850, 0x4C6),
        ('native opaque models', 0x55E120, 0x270), ('native polygon pool reset', 0x560190, 0x40),
        ('native before-character flags', 0xAEE91A, 0x13),
        ('native character prepass entry', 0x55E685, 0x50),
    ]]
    template = TEMPLATE.read_text(encoding='utf-8')
    end = template.index('const AllHatEffectsWorldDepthOracleStatic')
    patch_text = '\n'.join(banner) + '\n\n' + template[end:]
    patch_text += '\n' + js_statement('AllHatEffectsWorldDepthOracleStatic.WorldChecks', checks) + '\n'
    patch_text += '\n' + js_statement('AllHatEffectsWorldDepthOracleStatic.Payload', payload) + '\n'
    patch_raw = patch_text.replace('\r\n', '\n').replace('\n', '\r\n').encode('utf-8')
    if check:
        assert PATCH.read_bytes() == patch_raw, 'Generated patch is stale'
    else:
        PATCH.write_bytes(patch_raw)
        TEMPLATE.write_bytes(('\n'.join(banner) + '\n\n' + template[end:]).replace('\r\n', '\n').replace('\n', '\r\n').encode('utf-8'))
    print(json.dumps(dict(payload_bytes=len(data), relocations=len(relocations), exports=exports, check=check)))


def gpu_test(report=None):
    with tempfile.TemporaryDirectory(prefix='hat-depth-gpu-', dir=ROOT / 'Outputs') as directory:
        directory = Path(directory)
        exe, batch = directory / 'test.exe', directory / 'build.cmd'
        env = Path('C:/Program Files/Microsoft Visual Studio/18/Community/VC/Auxiliary/Build/vcvars32.bat')
        batch.write_text('@echo off\r\ncall "' + str(env) + '" >nul\r\ncl /nologo /EHsc /W4 /WX /O2 "' +
                         str(ROOT / 'tools/native/hat_effect_world_depth_test.cpp') + '" /Fo"' +
                         str(directory / 'test.obj') + '" /Fe"' + str(exe) + '" /link d3d9.lib user32.lib\r\n', encoding='ascii')
        compile_result = subprocess.run(['cmd.exe', '/c', str(batch)], cwd=directory, capture_output=True, timeout=120)
        assert compile_result.returncode == 0, (compile_result.stdout + compile_result.stderr).decode(errors='replace')
        result = subprocess.run([str(exe)], cwd=directory, capture_output=True, timeout=60)
        output = (result.stdout + result.stderr).decode(errors='replace')
        match = re.search(r'PASS (\d+) real DX9Ex', output)
        assert result.returncode == 0 and match, output
        receipt = dict(passed=True, gpu_pixel_cases=int(match[1]), backend='real DX9Ex HAL',
                       source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                       test_sha256=hashlib.sha256((ROOT / 'tools/native/hat_effect_world_depth_test.cpp').read_bytes()).hexdigest(),
                       stdout=output.strip(), game_live_accepted=False, temporary_artifacts_removed=True)
    if report:
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(receipt, indent=2))
    return receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--gpu-test', action='store_true')
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    build(args.check)
    if args.gpu_test:
        gpu_test(args.report)