"""Compile/extract the import-free chat measurement cache; the DLL is build-only."""

import hashlib
import json
import os
import struct
import subprocess
import zlib
from pathlib import Path

import pefile

ROOT = Path(__file__).resolve().parents[1]


def main():
    work = ROOT / "Outputs/chat-performance/build-cache"
    work.mkdir(parents=True, exist_ok=True)
    vswhere = (
        Path(os.environ["ProgramFiles(x86)"])
        / "Microsoft Visual Studio/Installer/vswhere.exe"
    )
    vs = Path(
        subprocess.check_output(
            [
                str(vswhere),
                "-latest",
                "-products",
                "*",
                "-requires",
                "Microsoft.VisualStudio.Component.VC.Tools.x86.x64",
                "-property",
                "installationPath",
            ],
            text=True,
        ).strip()
    )
    version = (
        (vs / "VC/Auxiliary/Build/Microsoft.VCToolsVersion.default.txt")
        .read_text()
        .strip()
    )
    tools = vs / "VC/Tools/MSVC" / version / "bin/Hostx64/x86"
    source = ROOT / "Scripts/Runtime/ChatMeasurementCache/runtime.cpp"
    obj, dll = work / "runtime.obj", work / "carrier.dll"
    subprocess.run(
        [
            str(tools / "cl.exe"),
            "/nologo",
            "/c",
            "/TP",
            "/GR-",
            "/O2",
            "/Oi",
            "/GS-",
            "/Zl",
            "/W4",
            "/WX",
            "/Fo" + str(obj),
            str(source),
        ],
        cwd=work,
        check=True,
    )
    subprocess.run(
        [
            str(tools / "link.exe"),
            "/nologo",
            "/DLL",
            "/NOENTRY",
            "/NODEFAULTLIB",
            "/MACHINE:X86",
            "/DYNAMICBASE:NO",
            "/NXCOMPAT",
            "/OPT:REF",
            "/OPT:ICF",
            "/BREPRO",
            "/OUT:" + str(dll),
            "/IMPLIB:" + str(work / ("carrier-" + str(os.getpid()) + ".lib")),
            str(obj),
        ],
        cwd=work,
        check=True,
    )
    pe = pefile.PE(str(dll))
    assert not getattr(pe, "DIRECTORY_ENTRY_IMPORT", None), (
        "Unexpected runtime dependency"
    )
    assert not pe.OPTIONAL_HEADER.AddressOfEntryPoint
    assert not getattr(pe, "DIRECTORY_ENTRY_TLS", None)
    sections = [s for s in pe.sections if s.Name.rstrip(b"\0") != b".reloc"]
    first = min(s.VirtualAddress for s in sections)
    end = max(s.VirtualAddress + s.Misc_VirtualSize for s in sections)
    code = bytearray(end - first)
    for s in sections:
        data = s.get_data()[: s.Misc_VirtualSize]
        code[s.VirtualAddress - first : s.VirtualAddress - first + len(data)] = data
    relocations = []
    for block in pe.DIRECTORY_ENTRY_BASERELOC:
        for r in block.entries:
            if not r.type:
                continue
            assert r.type == 3
            offset = r.rva - first
            target = (
                struct.unpack_from("<I", code, offset)[0]
                - pe.OPTIONAL_HEADER.ImageBase
                - first
            )
            assert 0 <= target < len(code)
            struct.pack_into("<I", code, offset, target)
            relocations.append(offset)
    exports = {
        s.name.decode(): s.address - first for s in pe.DIRECTORY_ENTRY_EXPORT.symbols
    }
    layout = struct.unpack("<14I", pe.get_data(first + exports["ChatCacheLayout"], 56))
    body = struct.pack("<" + "I" * len(relocations), *relocations) + code
    out = ROOT / "Inputs/ChatMeasurementCache/runtime.bin"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(
        struct.pack(
            "<8I",
            0x43434D43,
            1,
            len(code),
            len(relocations),
            exports["ChatCacheApi"],
            layout[0],
            20250716,
            zlib.crc32(body),
        )
        + body
    )
    meta = dict(
        version=1,
        client=20250716,
        size=len(code),
        exports=exports,
        layout=list(layout),
        source_sha256=hashlib.sha256(
            source.read_bytes().replace(b"\r\n", b"\n")
        ).hexdigest(),
        payload_sha256=hashlib.sha256(out.read_bytes()).hexdigest(),
        imports=[],
        compiler="MSVC x86",
        compiler_version=version,
        exception_policy="Native exception dispatch unchanged; an unwound miss disables caching until restart",
    )
    out.with_suffix(".json").write_text(json.dumps(meta, indent=2) + "\n")
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()
