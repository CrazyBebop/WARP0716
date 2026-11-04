"""Export HatEffect depth through real WARP and execute its x86 with Unicorn.

Requires the existing pefile/capstone/unicorn environment, an original
2025-07-16 client and WARP_console.exe. Does not launch or deploy the game.
All fixture clients/runtime copies are removed even if verification fails.
"""
from pathlib import Path
import argparse
import hashlib
import itertools
import json
import math
import os
import shutil
import struct
import subprocess
import tempfile

import pefile
from capstone import Cs, CS_ARCH_X86, CS_MODE_32
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32, UC_HOOK_CODE
from unicorn import x86_const as reg


ROOT = Path(__file__).resolve().parents[1]
PATCH = 'AllHatEffectsWorldDepthOracle'
ORIGINAL = ROOT / '2025-07-16_Ragexe_175220998_clientinfo/2025-07-16_Ragexe_175220998_clientinfo.exe'
SOURCE_HASH = 'ead7c0a316bc6c27705a5a6876daf5093abec31677f3c1af7525c1709b201bff'
HOOK, STOCK, CONVERTED = 0xAD93D4, 0xAD93D9, 0xAD93E2
CALLS = (0xAFE41C, 0xAFE52B)
LOOP, CONVERT = 0xAD8750, 0x554040
BASE = 0x400000
MEM, STOP = 0x30000000, 0x3000F000
EBP, ESP, VERTEX = MEM + 0x8000, MEM + 0x7000, MEM + 0x1000
MATRIX, CONTEXT = MEM + 0x2000, MEM + 0x3000
BIAS = struct.unpack('<f', struct.pack('<I', 0x3827C5AC))[0]


def f32(value):
    return struct.unpack('<f', struct.pack('<f', value))[0]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify_source():
    raw = (ROOT / f'Scripts/Patches/{PATCH}.qjs').read_bytes()
    assert raw.startswith(b'/*') and b'\n' not in raw.replace(b'\r\n', b''), 'QJS encoding/line endings'
    lines = raw.decode('utf-8').splitlines()
    end = lines.index('\\' + '*' * 74 + '/')
    assert all(len(line) == 76 for line in lines[:end + 1]), 'WARP banner alignment'
    assert all(not line.startswith(' ') and line == line.rstrip() for line in lines[end + 1:]), 'QJS indentation/whitespace'
    for label in ['Author(s)', 'Last Modified', 'Description', 'Evidence', 'Verifier']:
        assert any(label in line for line in lines[:end]), label


class Image:
    def __init__(self, path):
        self.pe = pefile.PE(data=Path(path).read_bytes(), fast_load=True)
        self.data = self.pe.get_memory_mapped_image()

    def read(self, va, size):
        return self.pe.get_data(va - BASE, size)

    def target(self, va, opcode):
        code = self.read(va, 5)
        assert code[0] == opcode, f'Unexpected branch at {va:08X}: {code.hex()}'
        return va + 5 + struct.unpack_from('<i', code, 1)[0]


class Machine:
    def __init__(self, image):
        self.image = image
        self.uc = Uc(UC_ARCH_X86, UC_MODE_32)
        self.uc.mem_map(BASE, (len(image.data) + 4095) & ~4095)
        self.uc.mem_write(BASE, image.data)
        self.uc.mem_map(MEM, 0x10000)
        self.uc.hook_add(UC_HOOK_CODE, self.hook)
        self.wrapper = image.target(CALLS[0], 0xE8)
        assert image.target(CALLS[1], 0xE8) == self.wrapper
        self.cave = self.wrapper - 8
        self.bridge = image.target(HOOK, 0xE9)
        self.stop_at = set()
        self.loop_callback = None

    def hook(self, uc, address, size, _):
        if address in self.stop_at:
            uc.emu_stop()
        elif address == LOOP and self.loop_callback:
            self.loop_callback()

    def u32(self, va):
        return struct.unpack('<I', self.uc.mem_read(va, 4))[0]

    def float(self, va):
        return struct.unpack('<f', self.uc.mem_read(va, 4))[0]

    def write_float(self, va, value):
        self.uc.mem_write(va, struct.pack('<f', value))

    def write_u32(self, va, value):
        self.uc.mem_write(va, struct.pack('<I', value))

    def run(self, start, stops):
        self.stop_at = set(stops)
        self.uc.emu_start(start, STOP, count=1000)
        assert self.uc.reg_read(reg.UC_X86_REG_EIP) in self.stop_at, 'Bridge did not return'

    def depth(self, distance, row, layer=1, active=True, anchor_y=400.0, check_abi=True):
        uc = self.uc
        self.write_u32(self.cave, int(active))
        self.write_float(EBP - 0x64, f32(1.0 / distance))
        self.write_float(EBP - 0x3C, anchor_y)
        self.write_u32(EBP + 0x10, MATRIX)
        # Give the historical implementation a valid nondegenerate camera.
        self.write_u32(0x12515F8, CONTEXT)
        self.write_u32(CONTEXT + 0x24, 384)
        self.write_float(CONTEXT + 8, -1200.0)
        self.write_float(MATRIX + 0x10, math.cos(math.radians(45)))
        self.write_float(MATRIX + 0x14, -math.sin(math.radians(45)))
        uc.mem_write(VERTEX - 0x20, bytes(range(64)))
        self.write_float(VERTEX - 0x18, anchor_y + row)
        self.write_float(VERTEX - 0x14, f32(0.0000310212207))
        preserved = {r: 0x12340000 + i * 0x100 for i, r in enumerate([
            reg.UC_X86_REG_EAX, reg.UC_X86_REG_EBX, reg.UC_X86_REG_ECX,
            reg.UC_X86_REG_ESI, reg.UC_X86_REG_EDI])}
        for r, value in preserved.items():
            uc.reg_write(r, value)
        uc.reg_write(reg.UC_X86_REG_EDX, VERTEX)
        uc.reg_write(reg.UC_X86_REG_EBP, EBP)
        uc.reg_write(reg.UC_X86_REG_ESP, ESP)
        xmm = {}
        for i in range(1, 8):
            value = int.from_bytes(struct.pack('<4f', i + .25, i + .5, i + .75, i + 1.), 'little')
            if i == 3:
                value = (value & ~0xFFFFFFFF) | int.from_bytes(struct.pack('<f', f32(layer * 1e-5)), 'little')
            xmm[getattr(reg, f'UC_X86_REG_XMM{i}')] = value
            uc.reg_write(getattr(reg, f'UC_X86_REG_XMM{i}'), value)
        before = bytes(uc.mem_read(VERTEX - 0x20, 64))
        self.run(HOOK, {STOCK, CONVERTED} if not active else {CONVERTED})
        if not active:
            assert uc.reg_read(reg.UC_X86_REG_EIP) == STOCK
            assert bytes(uc.mem_read(VERTEX - 0x20, 64)) == before
            assert uc.reg_read(reg.UC_X86_REG_XMM0) & 0xFFFFFFFF == int.from_bytes(struct.pack('<f', f32(1 / distance)), 'little')
        else:
            after = bytes(uc.mem_read(VERTEX - 0x20, 64))
            assert after[:12] == before[:12] and after[20:] == before[20:], 'XY/UV/color modified'
            expected_rhw = f32(f32(1 / distance) - f32(layer * 1e-5))
            assert self.float(VERTEX - 0x10) == expected_rhw, 'Stock texture RHW changed'
        assert uc.reg_read(reg.UC_X86_REG_ESP) == ESP, 'Stack unbalanced'
        assert uc.reg_read(reg.UC_X86_REG_EBP) == EBP
        assert uc.reg_read(reg.UC_X86_REG_EDX) == VERTEX
        if check_abi:
            assert all(uc.reg_read(r) == v for r, v in preserved.items()), 'GPR clobbered'
            assert all(uc.reg_read(r) == v for r, v in xmm.items()), 'Live XMM lanes clobbered'
        return self.float(VERTEX - 0x14)

    def native_sprite_rhw(self, distance, row):
        # Execute the original row-tilt/divide instructions, stopping before
        # native per-layer and actor-specific bias additions.
        self.write_float(CONTEXT + 8, f32(1 / f32(1 / distance)))
        self.uc.reg_write(reg.UC_X86_REG_ESI, CONTEXT)
        self.uc.reg_write(reg.UC_X86_REG_XMM1, int.from_bytes(struct.pack('<f', 1.), 'little'))
        self.uc.reg_write(reg.UC_X86_REG_XMM4, int.from_bytes(struct.pack('<f', min(row, 0.)), 'little'))
        self.run(0xC4102B, {0xC4103C})
        bits = self.uc.reg_read(reg.UC_X86_REG_XMM1) & 0xFFFFFFFF
        return struct.unpack('<f', struct.pack('<I', bits))[0]


def normalized(rhw):
    # Exact SSE float32 order of native 00554040, also executed by Unicorn.
    return f32(f32(f32(f32(1 / rhw) - 10.0) * f32(1.0067113637924194)) * rhw)


def expected_depth(distance, row):
    anchor = f32(1 / distance)
    denominator = f32(f32(1 / anchor) + f32(f32(min(row, 0.0)) * f32(.16)))
    rhw = f32(1 / denominator) if denominator > 0 else anchor
    return normalized(f32(rhw + BIAS))


def verify_depth(image):
    cpu = Machine(image)
    cases = 0
    for distance, row, layer in itertools.product(
            [80., 120., 200., 350., 600., 1000.],
            [-240., -160., -96., -48., -1., 0., 1., 32., 96.], [0, 1, 7, 31]):
        actual = cpu.depth(distance, row, layer)
        assert abs(actual - expected_depth(distance, row)) <= 2e-7, (distance, row, actual)
        # A foreground wall remains nearer; geometry behind the effect does not
        # win. This checks depth values, not a claim about D3D rasterization.
        sprite_rhw = cpu.native_sprite_rhw(distance, row)
        assert actual < normalized(sprite_rhw), 'Effect crossed behind sprite plane'
        assert normalized(f32(sprite_rhw + BIAS + .0002)) < actual
        assert normalized(f32(sprite_rhw - .0002)) > actual
        cases += 1
    for distance, row in [(80., -500.), (80., float('nan')), (1000., 0.)]:
        result = cpu.depth(distance, row)
        assert math.isfinite(result), 'Degenerate row lost fallback'
    for row in [-96., 0., 96.]:
        cpu.depth(120., row, active=False)
    return dict(depth_cases=cases, fallback_cases=3, non_hat_effect_cases=3)


def verify_wrapper(image):
    cpu = Machine(image)
    invocations = []
    for site in CALLS:
        cpu.write_u32(cpu.cave, 0)
        cpu.write_u32(ESP, MATRIX)
        cpu.uc.reg_write(reg.UC_X86_REG_ECX, CONTEXT)
        cpu.uc.reg_write(reg.UC_X86_REG_ESP, ESP)

        def native_loop():
            uc = cpu.uc
            sp = uc.reg_read(reg.UC_X86_REG_ESP)
            assert cpu.u32(cpu.cave) == 1
            assert cpu.u32(sp + 4) == MATRIX
            assert uc.reg_read(reg.UC_X86_REG_ECX) == CONTEXT
            invocations.append(site)
            uc.reg_write(reg.UC_X86_REG_ESP, sp + 8)  # native ret 4
            uc.reg_write(reg.UC_X86_REG_EIP, cpu.u32(sp))

        cpu.loop_callback = native_loop
        cpu.run(site, {site + 5})
        assert cpu.u32(cpu.cave) == 0, 'HatEffect scope leaked'
        assert cpu.uc.reg_read(reg.UC_X86_REG_ESP) == ESP + 4
    assert invocations == list(CALLS)
    return dict(render_call_cases=len(invocations))


def verify_layout(source, image, isolated):
    cpu = Machine(image)
    assert image.read(cpu.cave, 4) == bytes(4)
    assert image.read(cpu.cave + 4, 4) == struct.pack('<f', BIAS)
    md = Cs(CS_ARCH_X86, CS_MODE_32)
    code = list(md.disasm(image.read(cpu.bridge, 151), cpu.bridge))
    assert sum(i.size for i in code) == 151
    assert code[-1].mnemonic == 'jmp' and int(code[-1].op_str, 16) == CONVERTED
    assert [int(i.op_str, 16) for i in code if i.mnemonic == 'call'] == [CONVERT]
    if isolated:
        allowed = set(range(cpu.cave, cpu.cave + 0x120))
        for site in (*CALLS, HOOK):
            allowed.update(range(site, site + 5))
        for section in source.pe.sections:
            if not section.Characteristics & 0x20000000:
                continue
            before = section.get_data()[:section.Misc_VirtualSize]
            after = image.read(BASE + section.VirtualAddress, len(before))
            stray = [BASE + section.VirtualAddress + i for i, (a, b) in enumerate(zip(before, after))
                     if a != b and BASE + section.VirtualAddress + i not in allowed]
            assert not stray, f'Unscoped native writes: {stray[:10]}'
    return dict(bridge_bytes=151, cave=hex(cpu.cave), bridge=hex(cpu.bridge))


def export(fixture, folder, source, patches, expect_error=None):
    folder.mkdir()
    target = folder / 'client.exe'
    profile = folder / 'profile.yml'
    profile.write_text('from: ' + json.dumps(str(source.resolve())) + '\nto: ' +
                       json.dumps(str(target.resolve())) + '\ninputs: {}\npatches:\n' +
                       ''.join('    - ' + p + '\n' for p in patches), encoding='utf-8')
    run = subprocess.run([str(fixture / 'win32/WARP_console.exe'), '-using', str(profile)],
                         cwd=fixture, capture_output=True, timeout=180,
                         creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    log = (run.stdout + run.stderr).decode(errors='replace')
    if expect_error:
        assert expect_error in log, log[-6000:]
    else:
        assert run.returncode == 0 and '-E-' not in log and target.exists(), log[-6000:]
    return target


def verify(source, warp, baseline=None, only=None, baseline_ref=None):
    verify_source()
    assert digest(source) == SOURCE_HASH, 'Unrecognized original 2025-07-16 client'
    original = Image(source)
    rows = []
    outputs = ROOT / 'Outputs'
    outputs.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='hat-depth-77-', dir=outputs) as temporary:
        work = Path(temporary)
        fixture = work / 'fixture'
        fixture.mkdir()
        for name in ['Scripts', 'Patches']:
            shutil.copytree(ROOT / name, fixture / name, ignore=shutil.ignore_patterns('__pycache__', '*.exe'))
        # These directories are read-only for this patch. Linking avoids copying
        # thousands of irrelevant images and native Qt DLLs for every test group.
        for name in ['Tables', 'Inputs', 'Languages', 'Styles', 'Images', 'win32']:
            target = warp.parent if name == 'win32' else ROOT / name
            os.symlink(target.resolve(), fixture / name, target_is_directory=True)
        shutil.copy2(ROOT / 'Patches.yml', fixture / 'Patches.yml')
        (fixture / 'Assets').mkdir()
        if not (fixture / 'Patches/Premium.yml').exists():
            (fixture / 'Patches/Premium.yml').write_text('{}\n', encoding='utf-8')
        print('Prepared isolated WARP fixture', flush=True)
        if baseline_ref:
            baseline = work / 'baseline.qjs'
            baseline.write_bytes(subprocess.check_output(
                ['git', 'show', f'{baseline_ref}:Scripts/Patches/{PATCH}.qjs'], cwd=ROOT))
        if baseline:
            patch = fixture / f'Scripts/Patches/{PATCH}.qjs'
            saved = patch.read_bytes()
            try:
                patch.write_bytes(baseline.read_bytes())
                old = export(fixture, work / 'baseline', source, [PATCH])
                old_image = Image(old)
                # Historical source also clobbers EAX/ECX and upper XMM lanes.
                # Reproduce its Z separately from those independent ABI defects.
                cpu = Machine(old_image)
                old_z = cpu.depth(120., -96., check_abi=False)
                sprite_z = normalized(cpu.native_sprite_rhw(120., -96.))
                assert old_z > sprite_z, 'Historical self-occlusion was not reproduced'
                rows.append(dict(case='historical-regression', effect_z=old_z,
                                 wearer_plane_z=sprite_z, reproduced=True))
                print('PASS historical self-occlusion reproduced at close zoom', flush=True)
            finally:
                patch.write_bytes(saved)
        combinations = [('isolated', [PATCH])]
        # These optional companions are local to some forks, not prerequisites.
        companions = ['UniformSpriteRHW', 'FloorSafeSpriteDepth']
        if all((fixture / f'Scripts/Patches/{p}.qjs').exists() for p in companions):
            combinations += [('sprite-first', companions + [PATCH]), ('hat-first', [PATCH] + companions)]
        for name, patches in combinations:
            if only and name not in only:
                continue
            target = export(fixture, work / name, source, patches)
            image = Image(target)
            row = dict(case=name, sha256=digest(target), patches=patches)
            row.update(verify_layout(original, image, name == 'isolated'))
            row.update(verify_depth(image))
            row.update(verify_wrapper(image))
            rows.append(row)
            print('PASS ' + name, flush=True)
        if not only or 'reapply' in only:
            first = work / 'isolated/client.exe'
            if not first.exists():
                first = export(fixture, work / 'isolated', source, [PATCH])
            again = export(fixture, work / 'reapply', first, [PATCH])
            verify_layout(original, Image(again), True)
            verify_depth(Image(again))
            rows.append(dict(case='reapply', sha256=digest(again), passed=True))
            print('PASS safe reapply through WARP', flush=True)
        # Corrupt every profiled native guard, then execute the selected patch
        # directly in the real QuickJS engine so validate() cannot hide errors.
        patch = fixture / f'Scripts/Patches/{PATCH}.qjs'
        saved = patch.read_bytes()
        try:
            patch.write_bytes(saved + b'\r\nAllHatEffectsWorldDepthOracle.validate = () => true;\r\n')
            for i, va in enumerate([*CALLS, 0xAD8D91, 0xAD93C5, 0xAD9308, HOOK, 0xAD8B7D, 0xC4102B]):
                if only and f'guards-{i // 2 + 1}' not in only:
                    continue
                raw = bytearray(source.read_bytes())
                raw[original.pe.get_offset_from_rva(va - BASE)] ^= 1
                bad = work / f'bad-{i}.exe'
                bad.write_bytes(raw)
                target = export(fixture, work / f'reject-{i}', bad, [PATCH], 'mismatch, got')
                if target.exists():
                    bad_image, result = Image(bad), Image(target)
                    for site in (*CALLS, HOOK):
                        assert result.read(site, 5) == bad_image.read(site, 5), 'Partial hook after rejection'
                rows.append(dict(case='reject-native-guard', address=hex(va), passed=True))
            if any(r['case'] == 'reject-native-guard' for r in rows):
                print('PASS selected native mismatch guards reject before hook writes', flush=True)
        finally:
            patch.write_bytes(saved)
    assert digest(source) == SOURCE_HASH, 'Original client changed'
    return dict(issue='https://github.com/CrazyBebop/WARP0716/issues/77',
                source_sha256=SOURCE_HASH, patch_sha256=digest(ROOT / f'Scripts/Patches/{PATCH}.qjs'),
                verifier_sha256=digest(Path(__file__)), warp_sha256=digest(warp),
                cases=rows, temporary_artifacts_removed=True, live_visual_accepted=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=ORIGINAL)
    parser.add_argument('--warp', type=Path, default=ROOT / 'win32/WARP_console.exe')
    baseline_group = parser.add_mutually_exclusive_group()
    baseline_group.add_argument('--baseline-qjs', type=Path, help='Optional original QJS to reproduce issue #77')
    baseline_group.add_argument('--baseline-ref', help='Read original QJS bytes from this Git ref into the temporary fixture')
    parser.add_argument('--report', type=Path)
    parser.add_argument('--only', action='append', choices=[
        'isolated', 'sprite-first', 'hat-first', 'reapply',
        'guards-1', 'guards-2', 'guards-3', 'guards-4'],
        help='Run a bounded subset; repeat to combine groups (default: all)')
    args = parser.parse_args()
    report = verify(args.source, args.warp, args.baseline_qjs, args.only, args.baseline_ref)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))