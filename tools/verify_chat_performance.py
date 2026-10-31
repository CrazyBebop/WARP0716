"""Verify production chat hooks and the import-free cache; no diagnostic ABI."""

import argparse
import hashlib
import json
import struct
import zlib
from pathlib import Path

import pefile
from chat_patch_layout import ROOT, installed_cache, installed_histories, installed_stutter

SOURCE_SHA256 = "ead7c0a316bc6c27705a5a6876daf5093abec31677f3c1af7525c1709b201bff"


def verify(exe, source_path, stutter=True, cache=True, history_sites=None):
    assert hashlib.sha256(source_path.read_bytes()).hexdigest() == SOURCE_SHA256
    pe = pefile.PE(str(exe))
    source = pefile.PE(str(source_path))
    base = pe.OPTIONAL_HEADER.ImageBase
    assert pe.FILE_HEADER.Machine == 0x14C and base == 0x400000
    assert not pe.OPTIONAL_HEADER.DllCharacteristics & 0x40
    s, c = installed_stutter(pe), installed_cache(pe)
    assert bool(s) == stutter and bool(c) == cache
    histories = installed_histories(pe)
    if history_sites is not None:
        assert len(histories) == history_sites
    if not stutter:
        assert not histories
    assert pe.get_data(0x866340 - base, 0x360) == source.get_data(
        0x866340 - base, 0x360
    ), "Native rich-text parser/fallback changed"
    # Neither production patch writes the append entry, route or cleanup hooks.
    for va, size in [
        (0x83D3F0, 0x62),
        (0x83D49B, 0x14),
        (0x83D4AF, 11),
        (0x83D606, 7),
        (0x575780, 0xE1),
        (0x7FAF70, 0x132),
    ]:
        assert pe.get_data(va - base, size) == source.get_data(va - base, size), hex(va)
    if c:
        raw = (ROOT / "Inputs/ChatMeasurementCache/runtime.bin").read_bytes()
        meta = json.loads(
            (ROOT / "Inputs/ChatMeasurementCache/runtime.json").read_text()
        )
        magic, version, size, count, api, state_size, client, crc = struct.unpack_from(
            "<8I", raw
        )
        assert (magic, version, size, state_size, client) == (
            0x43434D43,
            1,
            meta["size"],
            meta["layout"][0],
            20250716,
        )
        assert (
            zlib.crc32(raw[32:]) == crc
            and hashlib.sha256(raw).hexdigest() == meta["payload_sha256"]
        )
        assert (
            hashlib.sha256(
                (ROOT / "Scripts/Runtime/ChatMeasurementCache/runtime.cpp")
                .read_bytes()
                .replace(b"\r\n", b"\n")
            ).hexdigest()
            == meta["source_sha256"]
        )
        assert set(meta["exports"]) == {
            "@ChatFragmentWidth@32",
            "_ChatGlyphWidth@16",
            "ChatCacheApi",
            "ChatCacheLayout",
        }
        assert meta["imports"] == [] and api == meta["exports"]["ChatCacheApi"]
        code = bytearray(raw[32 + count * 4 :])
        assert len(code) == size
        for off in struct.unpack_from("<" + "I" * count, raw, 32):
            value = struct.unpack_from("<I", code, off)[0]
            assert off + 4 <= size and value < size
            struct.pack_into("<I", code, off, value + c["code"])
        struct.pack_into("<I", code, api, c["state"])
        assert pe.get_data(c["code"] - base, size) == code
        assert c["state"] % 4096 == 0 and pe.get_data(
            c["state"] - base, state_size
        ) == bytes(state_size)
        for word in [
            b"ChatDiagnostics",
            b"ChatPerformance",
            b"CreateThread",
            b"CreateFile",
            b"QueryPerformanceCounter",
            b".log",
        ]:
            assert word not in code, word
    return dict(stutter=s, cache=c, history_sites=len(histories), no_runtime_diagnostics=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("exe", type=Path)
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--history-sites", type=int, choices=[0, 2])
    a = p.parse_args()
    print(json.dumps(verify(a.exe, a.source, history_sites=a.history_sites), indent=2))


if __name__ == "__main__":
    main()
