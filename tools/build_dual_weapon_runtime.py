"""Rebuild the public dual-weapon DWCP/DWLS inputs with pinned MSVC x86.

--check builds in temporary storage and compares both files without modifying
the checkout. Generated authoring headers are frozen inputs, not regenerated art.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import tempfile
import zlib

import pefile

ROOT = Path(__file__).resolve().parents[1]
TOOLSET = "14.51.36231"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def tool_directory(value):
    if value:
        result = value.resolve()
    else:
        installer = Path(os.environ["ProgramFiles(x86)"]) / "Microsoft Visual Studio/Installer/vswhere.exe"
        location = subprocess.check_output(
            [str(installer), "-latest", "-products", "*", "-requires",
             "Microsoft.VisualStudio.Component.VC.Tools.x86.x64", "-property", "installationPath"],
            text=True,
        ).strip()
        result = Path(location) / "VC/Tools/MSVC" / TOOLSET / "bin/Hostx64/x86"
    if result.parents[2].name != TOOLSET:
        raise ValueError(f"Use MSVC toolset {TOOLSET} Hostx64/x86, not {result}")
    for name in ("cl.exe", "link.exe"):
        if not (result / name).is_file():
            raise FileNotFoundError(result / name)
    return result


def compile_image(tools, source, work, name, metadata=None):
    obj, dll = work / (name + ".obj"), work / (name + ".dll")
    commands = [
        [str(tools / "cl.exe"), "/nologo", "/c", "/TP", "/GR-", "/O2", "/Oi",
         "/GS-", "/Zl", "/arch:SSE2", "/fp:precise", "/W4", "/WX",
         "/Fo" + str(obj), str(source)],
        [str(tools / "link.exe"), "/nologo", "/DLL", "/NOENTRY", "/NODEFAULTLIB",
         "/MACHINE:X86", "/DYNAMICBASE:NO", "/NXCOMPAT", "/OPT:REF", "/OPT:ICF",
         "/BREPRO", "/OUT:" + str(dll), str(obj)],
    ]
    for command in commands:
        result = subprocess.run(command, cwd=work, capture_output=True)
        if result.returncode:
            output = (result.stdout + result.stderr).decode(errors="replace")
            raise RuntimeError(f"{Path(command[0]).name} failed ({result.returncode}):\n{output}")
    with pefile.PE(str(dll)) as pe:
        if (pe.FILE_HEADER.Machine != 0x14C or pe.OPTIONAL_HEADER.AddressOfEntryPoint
                or getattr(pe, "DIRECTORY_ENTRY_IMPORT", None)
                or getattr(pe, "DIRECTORY_ENTRY_TLS", None)):
            raise ValueError("Runtime container must be import-free x86 without entry point/TLS")
        sections = [s for s in pe.sections if s.Name.rstrip(b"\0") != b".reloc"]
        first = min(s.VirtualAddress for s in sections)
        end = max(s.VirtualAddress + s.Misc_VirtualSize for s in sections)
        code = bytearray(end - first)
        for section in sections:
            data = section.get_data()[:section.Misc_VirtualSize]
            offset = section.VirtualAddress - first
            code[offset:offset + len(data)] = data
        if metadata is not None:
            # /BREPRO includes build-container identity, which varies with the
            # temporary output path. These non-executable PE metadata bytes were
            # historically included in DWCP. Pin only the identified fields;
            # never normalize machine code, profiles, exports, or relocations.
            offset = pe.get_rva_from_offset(
                pe.DIRECTORY_ENTRY_EXPORT.struct.get_field_absolute_offset("TimeDateStamp")) - first
            struct.pack_into("<I", code, offset, metadata["export_timestamp"])
            for debug in pe.DIRECTORY_ENTRY_DEBUG:
                kind = str(debug.struct.Type)
                offset = pe.get_rva_from_offset(
                    debug.struct.get_field_absolute_offset("TimeDateStamp")) - first
                struct.pack_into("<I", code, offset, metadata["debug_timestamps"][kind])
                if debug.struct.Type == 16:
                    offset = debug.struct.AddressOfRawData - first
                    expected = bytes.fromhex(metadata["repro_data"])
                    if debug.struct.SizeOfData != len(expected):
                        raise ValueError("Unexpected reproducible-build metadata size")
                    code[offset:offset + len(expected)] = expected
        relocations = []
        for block in getattr(pe, "DIRECTORY_ENTRY_BASERELOC", []):
            for relocation in block.entries:
                if not relocation.type:
                    continue
                if relocation.type != 3:
                    raise ValueError("Only IMAGE_REL_BASED_HIGHLOW is supported")
                offset = relocation.rva - first
                target = struct.unpack_from("<I", code, offset)[0] - pe.OPTIONAL_HEADER.ImageBase - first
                if offset < 0 or offset + 4 > len(code) or not 0 <= target < len(code):
                    raise ValueError("Relocation escapes extracted image")
                struct.pack_into("<I", code, offset, target)
                relocations.append((offset, target))
        exports = {s.name.decode(): s.address - first for s in pe.DIRECTORY_ENTRY_EXPORT.symbols}
    return code, relocations, exports


def build(tools, work, root=ROOT):
    source = root / "CustomDLL/DualWeapon"
    pins = json.loads((root / "Inputs/DualWeaponRuntime/build.json").read_text())
    code, relocations, exports = compile_image(
        tools, source / "compositor.c", work, "compositor", pins["container_metadata"])
    authored = root / "Inputs/DualWeaponAuthored"
    rig = (authored / "rigs/female-assassin-canonical.dwr3").read_bytes()
    grip = (authored / "grips/female-assassin-canonical.dwc2").read_bytes()
    body = b"".join(struct.pack("<I", off) for off, _ in relocations) + code + rig + grip
    compositor = struct.pack("<8I", 0x50435744, 1, len(code), exports["_DualWeaponCompose@36"],
                             len(relocations), len(rig), len(grip), zlib.crc32(body)) + body

    image, relocs, exports = compile_image(tools, source / "depth_helper.cpp", work, "depth")
    begin = exports["_DualWeaponDepth@16"]
    # The reviewed function owns 1,380 bytes including its aligned constants.
    helper = bytearray(image[begin:begin + 1380])
    pairs = []
    for offset, target in relocs:
        if not begin <= offset < begin + len(helper):
            continue
        offset, target = offset - begin, target - begin
        if not 0 <= target < len(helper):
            raise ValueError("Depth helper relocation escapes its own function")
        struct.pack_into("<I", helper, offset, 0)
        pairs.append((offset, target))
    if len(helper) != 1380 or len(pairs) != 3:
        raise ValueError("Depth helper ABI/relocation count changed")
    # DWLS v2 carries only the injected helper. Retired capture core/rig are not shipped.
    body = helper + b"".join(struct.pack("<2I", *pair) for pair in pairs)
    support = struct.pack("<12I", 0x534C5744, 2, 0, 0, 0, len(helper), 0, len(pairs),
                          0, zlib.crc32(body), 0, 0) + body
    return {"compositor.dwcp": bytes(compositor), "legacy-support.dwls": support}, bytes(helper), pairs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tool-dir", type=Path)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="Compare exact bytes; never rewrite shipped files")
    mode.add_argument("--write", action="store_true", help="Regenerate both checked-in patch inputs")
    args = parser.parse_args()
    tools = tool_directory(args.tool_dir)
    manifest = ROOT / "Inputs/DualWeaponRuntime/build.json"
    pins = json.loads(manifest.read_text())
    for name, expected in pins["tool_sha256"].items():
        if sha((tools / name).read_bytes()) != expected:
            raise ValueError(f"Pinned compiler tool differs: {name}")
    for relative, expected in pins["source_sha256"].items():
        if sha((ROOT / relative).read_bytes().replace(b"\r\n", b"\n")) != expected:
            raise ValueError(f"Pinned source differs: {relative}")
    with tempfile.TemporaryDirectory(prefix="warp-dual-runtime-") as temporary:
        payloads, helper, pairs = build(tools, Path(temporary))
    for name, data in payloads.items():
        target = ROOT / "Inputs/DualWeaponRuntime" / name
        if sha(data) != pins["payload_sha256"][name]:
            raise ValueError(f"Rebuilt payload differs from the accepted pin: {name}")
        if args.check and target.read_bytes() != data:
            raise ValueError(f"Checked-in payload is stale: {target}")
    if sha(helper) != pins["helper_sha256"] or [list(pair) for pair in pairs] != pins["helper_relocations"]:
        raise ValueError("Frozen depth-helper bytes/relocations changed")
    for name, data in payloads.items():
        if args.write:
            (ROOT / "Inputs/DualWeaponRuntime" / name).write_bytes(data)
        print(f"PASS {name}: {len(data)} bytes SHA-256 {sha(data)}")
    print(f"PASS pinned MSVC {TOOLSET}; helper {len(helper)} bytes/{len(pairs)} relocations; temporary outputs removed")


if __name__ == "__main__":
    main()