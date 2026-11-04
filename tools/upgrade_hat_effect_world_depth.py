"""Upgrade a hash-pinned current client using real WARP-emitted world isolation.

Adds one RXW payload section after the existing sections; adjusts raw header
offsets only if the original header has no free section slot. All previous
section contents, overlay, imports and unrelated hooks remain identical.
Install and signing are transactional. A sparse gzip rollback stores replaced
bytes/header offsets rather than another full client.
"""
from pathlib import Path
import argparse
import gzip
import json
import os
import struct
import subprocess
import sys
import tempfile
import time

import pefile
from capstone import Cs, CS_ARCH_X86, CS_MODE_32, CS_GRP_CALL, CS_GRP_JUMP
from capstone.x86 import X86_OP_IMM, X86_OP_MEM

import verify_hat_effect_world_depth as verify
from hat_effect_release_support import ROOT, SERVER, ASSETS, SIGNATURE, sha, save, signature, closed, atomic_bytes, fixture_at
from js_data_format import load_assignment

SECTION = b'.hdepth'


def align(value, boundary):
    return (value + boundary - 1) & ~(boundary - 1)


def exports(source):
    return load_assignment(source, 'AllHatEffectsWorldDepthOracleStatic.Payload')


def build(before, reference):
    old = pefile.PE(data=before, fast_load=True)
    assert old.OPTIONAL_HEADER.ImageBase == verify.BASE and not old.OPTIONAL_HEADER.DllCharacteristics & 0x40
    assert old.FILE_HEADER.Machine == 0x14C
    assert not any(s.Name.rstrip(b'\0') == SECTION for s in old.sections), 'Already upgraded; inspect existing runtime'
    qjs = verify.QJS.read_text(encoding='utf-8')
    payload = exports(qjs)
    checks = load_assignment(qjs, 'AllHatEffectsWorldDepthOracleStatic.WorldChecks')
    for check in checks:
        actual = old.get_data(check['va'] - verify.BASE, len(bytes.fromhex(check['bytes'])))
        wanted = bytes.fromhex(check['bytes'])
        if check['name'] == 'native world ground2' and actual != wanted:
            # The current signed client already owns GrayMap's lightmap option
            # override. Replay its existing native pass with that hook intact.
            at = 0x55D8DF - check['va']
            assert actual[:at] == wanted[:at] and actual[at + 5:] == wanted[at + 5:]
            assert actual[at] == 0xE8
            target = 0x55D8E4 + struct.unpack_from('<i', actual, at + 1)[0]
            bridge_bytes = old.get_data(target - verify.BASE, 32)
            assert bridge_bytes[:3] == b'\x9c\x83\x3d' and bridge_bytes[7:14] == bytes.fromhex('000f8407000000')
            assert bridge_bytes[14:22] == bytes.fromhex('9db800000000c39d')
            assert bridge_bytes[22] == 0xE9 and target + 27 + struct.unpack_from('<i', bridge_bytes, 23)[0] == 0x68EA70
        else:
            assert actual == wanted, check['name']
    bridge = verify.Machine(verify.Image(reference))
    ref = bridge.image
    scope = bridge.cave
    start = old.OPTIONAL_HEADER.ImageBase + align(old.OPTIONAL_HEADER.SizeOfImage, old.OPTIONAL_HEADER.SectionAlignment)
    ref_payload = int.from_bytes(ref.read(0xFD6D9C, 4), 'little') - payload['exports']['@HatDepthDraw32@12']
    length = ref_payload + len(payload['hex']) // 2 + 0x300 - scope
    code = bytearray(ref.read(scope, length))
    delta = start - scope
    md = Cs(CS_ARCH_X86, CS_MODE_32)
    md.detail = True
    relative_ranges = [(scope + 8, 32), (scope + 0x30, 241)]
    for site, resume in [(0xAD9413, 0xAD9418), (0x55E685, 0x55E68B), (0x542B26, 0x542B2C), (0x55C189, 0x55C18F)]:
        at = ref.target(site, 0xE9)
        size = 0
        for insn in md.disasm(ref.read(at, 220), at):
            size += insn.size
            if insn.mnemonic == 'jmp' and insn.op_str == hex(resume): break
        else: raise AssertionError('Unterminated emitted trampoline')
        relative_ranges.append((at, size))
    for at, count in relative_ranges:
        for insn in md.disasm(ref.read(at, count), at):
            offset = insn.address - scope
            for operand in insn.operands:
                if operand.type == X86_OP_MEM and not operand.mem.base and not operand.mem.index:
                    address = operand.mem.disp
                    if scope <= address < scope + length:
                        assert insn.disp_size == 4
                        struct.pack_into('<I', code, offset + insn.disp_offset, address + delta)
                elif operand.type == X86_OP_IMM and (insn.group(CS_GRP_CALL) or insn.group(CS_GRP_JUMP)):
                    address = operand.imm
                    if not scope <= address < scope + length:
                        assert insn.imm_size == 4
                        struct.pack_into('<i', code, offset + insn.imm_offset, address - (insn.address + delta + insn.size))
    for offset in payload['relocations']:
        at = ref_payload - scope + offset
        struct.pack_into('<I', code, at, struct.unpack_from('<I', code, at)[0] + delta)
    config = ref_payload - scope + payload['exports']['HatDepthConfig']
    struct.pack_into('<I', code, config, start)
    writes = []
    for site, opcode in [(verify.CALLS[0], 0xE8), (verify.CALLS[1], 0xE8),
                          (verify.HOOK, 0xE9), (0xAD9413, 0xE9), (0x55E685, 0xE9),
                          (0x542B26, 0xE9), (0x55C189, 0xE9), (0x55CA9C, 0xE8)]:
        size = 6 if site in [0x55E685, 0x542B26, 0x55C189] else 5
        data = bytes([opcode]) + struct.pack('<i', ref.target(site, opcode) + delta - site - 5) + b'\x90' * (size - 5)
        offset = old.get_offset_from_rva(site - verify.BASE)
        writes.append(dict(offset=offset, before=before[offset:offset + size].hex(), after=data.hex(), va=hex(site)))
    for site in [0xFD6D98, 0xFD6D9C]:
        offset = old.get_offset_from_rva(site - verify.BASE)
        value = int.from_bytes(ref.read(site, 4), 'little') + delta
        writes.append(dict(offset=offset, before=before[offset:offset + 4].hex(), after=struct.pack('<I', value).hex(), va=hex(site)))
    data = bytearray(before)
    for row in writes:
        offset = row['offset']; raw = bytes.fromhex(row['after'])
        data[offset:offset + len(raw)] = raw
    first = min(s.PointerToRawData for s in old.sections if s.SizeOfRawData)
    header = old.sections[-1].get_file_offset() + 40
    shift = max(0, align(header + 40, old.OPTIONAL_HEADER.FileAlignment) - first)
    assert not old.FILE_HEADER.PointerToSymbolTable and not old.OPTIONAL_HEADER.DATA_DIRECTORY[4].VirtualAddress
    old.parse_data_directories(directories=[6])
    assert not getattr(old, 'DIRECTORY_ENTRY_DEBUG', []), 'Handle native debug offsets explicitly'
    header_before = before[:first]
    if shift:
        data[first:first] = bytes(shift)
        for section in old.sections:
            if section.SizeOfRawData:
                struct.pack_into('<I', data, section.get_field_absolute_offset('PointerToRawData'), section.PointerToRawData + shift)
        struct.pack_into('<I', data, old.OPTIONAL_HEADER.get_field_absolute_offset('SizeOfHeaders'), first + shift)
    raw_at = align(len(data), old.OPTIONAL_HEADER.FileAlignment)
    raw_size = align(len(code), old.OPTIONAL_HEADER.FileAlignment)
    data.extend(bytes(raw_at - len(data)) + code + bytes(raw_size - len(code)))
    overlay = old.get_overlay() or b''
    data.extend(overlay)
    data[header:header + 40] = struct.pack('<8sIIIIIIHHI', SECTION, len(code), start - verify.BASE,
                                        raw_size, raw_at, 0, 0, 0, 0, 0xE0000060)
    struct.pack_into('<H', data, old.FILE_HEADER.get_field_absolute_offset('NumberOfSections'), len(old.sections) + 1)
    struct.pack_into('<I', data, old.OPTIONAL_HEADER.get_field_absolute_offset('SizeOfImage'),
                     align(start - verify.BASE + len(code), old.OPTIONAL_HEADER.SectionAlignment))
    struct.pack_into('<I', data, old.OPTIONAL_HEADER.get_field_absolute_offset('SizeOfCode'), old.OPTIONAL_HEADER.SizeOfCode + raw_size)
    updated = pefile.PE(data=bytes(data), fast_load=True)
    allowed = {row['offset'] + n for row in writes for n in range(len(bytes.fromhex(row['after'])))}
    changed = 0
    for section in old.sections:
        a = section.get_data()
        b = updated.get_data(section.VirtualAddress, section.SizeOfRawData)
        assert len(a) == len(b)
        for i, (x, y) in enumerate(zip(a, b)):
            if x != y:
                assert section.PointerToRawData + i in allowed, hex(section.VirtualAddress + i)
                changed += 1
    assert updated.get_overlay() == overlay
    rollback = dict(before_sha256=sha(before), after_sha256=sha(data), original_length=len(before),
                    header_before_hex=header_before.hex(), first_raw=first, header_shift=shift,
                    writes=writes, original_section_hashes={s.Name.rstrip(b'\0').decode():sha(s.get_data()) for s in old.sections})
    assert restore_bytes(bytes(data), rollback) == before
    return bytes(data), rollback, dict(payload=hex(start), added_section=SECTION.decode(), bytes=len(code),
                                     previous_section_contents_preserved_except_owned_hooks=True,
                                     changed_existing_bytes=changed, previous_overlay_preserved=True,
                                     header_shift_bytes=shift)


def restore_bytes(raw, record):
    data = bytearray(raw[:record['original_length'] + record['header_shift']])
    first, shift = record['first_raw'], record['header_shift']
    if shift: del data[first:first + shift]
    data[:first] = bytes.fromhex(record['header_before_hex'])
    for row in record['writes']:
        at = row['offset']; old = bytes.fromhex(row['before'])
        data[at:at + len(old)] = old
    assert sha(data) == record['before_sha256'], 'Sparse rollback does not reconstruct source'
    return bytes(data)


def install(target, expected, evidence, apply=False):
    target = target.resolve(); game = target.parent
    closed(game)
    before = target.read_bytes()
    assert sha(before) == expected.lower(), 'Target changed; inspect the current client'
    assets, sig = (game / ASSETS).read_bytes(), (game / SIGNATURE).read_bytes()
    previous = signature(target, game / ASSETS, game / SIGNATURE, game)
    protected = {str(p):sha(p.read_bytes()) for p in [game / 'riftlock.dll', game / 'libsodium.dll', game / 'DATA.INI', ROOT / 'Settings.yml', ROOT / 'profiles/2025-07-16 PROFILE MAIN.yml']}
    grfs = {str(p):(p.stat().st_size,p.stat().st_mtime_ns) for p in game.glob('*.grf')}
    with tempfile.TemporaryDirectory(prefix='hat-world-upgrade-',dir=ROOT / 'Outputs') as directory:
        work = Path(directory); fixture = fixture_at(work)
        reference = verify.export(fixture, work / 'reference', verify.ORIGINAL, [verify.PATCH])
        after, rollback, preservation = build(before, reference)
        stage = work / 'stage'; stage.mkdir(); candidate = stage / target.name; candidate.write_bytes(after)
        image = verify.Image(candidate)
        native = dict(layout=verify.verify_layout(verify.Image(verify.ORIGINAL),image,False),
                      depth=verify.verify_depth(image),wrappers=verify.verify_wrapper(image))
        scan = subprocess.run([sys.executable,str(SERVER / 'tools/riftlock_assets.py'),'--game-root',str(game),
                               '--client-exe',str(candidate),'--output',str(work / 'assets.txt')],capture_output=True,timeout=600)
        assert scan.returncode==0,(scan.stdout+scan.stderr).decode(errors='replace')
        assert (work / 'assets.txt').read_bytes()==assets,'Current assets changed; do not widen this renderer update'
        for name in ['riftlock.dll','libsodium.dll']:os.symlink((game / name).resolve(),stage / name)
        (stage / ASSETS).write_bytes(assets)
        key = SERVER / 'conf/riftlock-server.key'
        secret=bytes.fromhex(key.read_text(encoding='ascii').strip());assert len(secret)==64 and secret[32:].hex()==previous['public_key'];del secret
        run=subprocess.run([sys.executable,str(SERVER / 'tools/riftlock_release.py'),'--game-root',str(stage),
                            '--client-exe',target.name,'--keep-assets','--build-id',str(previous['build']),
                            '--release',str(max(int(time.time()),previous['release']+1)),'--secret',str(key),
                            '--library',str(SERVER / 'libsodium.dll')],capture_output=True,timeout=120)
        assert run.returncode==0,(run.stdout+run.stderr).decode(errors='replace')
        signed=signature(candidate,stage / ASSETS,stage / SIGNATURE,game)
        signed_bytes = (stage / SIGNATURE).read_bytes()
        rollback.update(target=str(candidate),before_signature_hex=sig.hex(),
                        after_signature_hex=signed_bytes.hex(),asset_manifest_sha256=sha(assets))
        sandbox_recovery = work / 'sandbox-rollback.json.gz'
        with gzip.open(sandbox_recovery,'wt',encoding='utf-8') as stream:
            json.dump(rollback,stream,separators=(',',':'))
        rollback_result = globals()['rollback'](sandbox_recovery)
        assert rollback_result['sha256'] == sha(before) and candidate.read_bytes() == before
        candidate.write_bytes(after)
        (stage / SIGNATURE).write_bytes(signed_bytes)
        signature(candidate,stage / ASSETS,stage / SIGNATURE,game)
        result=dict(target=str(target),before_sha256=sha(before),after_sha256=sha(after),native=native,
                    preservation=preservation,before_signature=previous,after_signature=signed,
                    installed=False,live_visual_accepted=False,fresh_asset_scan_matches=True,
                    actual_rollback_sandbox_tested=True,protected_hashes=protected)
        print('PASS current-client preservation, emitted runtime, 216 depth cases and staged signature',flush=True)
        if apply:
            recovery=evidence.with_name(evidence.stem+'-rollback.json.gz')
            assert not evidence.exists() and not recovery.exists()
            rollback.update(target=str(target),before_signature_hex=sig.hex(),after_signature_hex=(stage / SIGNATURE).read_bytes().hex(),asset_manifest_sha256=sha(assets))
            recovery.parent.mkdir(parents=True,exist_ok=True)
            with gzip.open(recovery,'wt',encoding='utf-8') as stream:json.dump(rollback,stream,separators=(',',':'))
            closed(game)
            assert target.read_bytes()==before and (game / SIGNATURE).read_bytes()==sig
            assert (game / ASSETS).read_bytes()==assets
            try:
                atomic_bytes(target,after);atomic_bytes(game / SIGNATURE,(stage / SIGNATURE).read_bytes())
                signature(target,game / ASSETS,game / SIGNATURE,game)
                assert all(sha(Path(p).read_bytes())==h for p,h in protected.items())
                assert all((Path(p).stat().st_size,Path(p).stat().st_mtime_ns)==stamp for p,stamp in grfs.items())
                verify.verify_isolation(verify.Image(target));verify.verify_depth(verify.Image(target))
            except Exception:
                atomic_bytes(target,before);atomic_bytes(game / SIGNATURE,sig);raise
            result.update(installed=True,status='installed_for_live_testing',rollback=str(recovery),
                          rollback_sha256=sha(recovery.read_bytes()),all_grfs_dlls_ini_settings_preserved=True)
    result['temporary_artifacts_removed']=True
    save(evidence,result)
    return result


def rollback(path):
    with gzip.open(path,'rt',encoding='utf-8') as stream:record=json.load(stream)
    target=Path(record['target']);closed(target.parent);raw=target.read_bytes()
    assert sha(raw)==record['after_sha256'],'Current EXE no longer matches this release'
    assert (target.parent / SIGNATURE).read_bytes()==bytes.fromhex(record['after_signature_hex'])
    assert sha((target.parent / ASSETS).read_bytes())==record['asset_manifest_sha256']
    old=restore_bytes(raw,record);atomic_bytes(target,old);atomic_bytes(target.parent / SIGNATURE,bytes.fromhex(record['before_signature_hex']))
    signature(target,target.parent / ASSETS,target.parent / SIGNATURE,target.parent)
    return dict(rolled_back=True,sha256=sha(old))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target',type=Path);parser.add_argument('--expected-source')
    parser.add_argument('--evidence',type=Path);parser.add_argument('--apply',action='store_true')
    parser.add_argument('--rollback',type=Path);args=parser.parse_args()
    if args.rollback:result=rollback(args.rollback)
    else:
        if not all([args.target,args.expected_source,args.evidence]):parser.error('--target/--expected-source/--evidence required')
        result=install(args.target,args.expected_source,args.evidence,args.apply)
    print(json.dumps(result,indent=2))