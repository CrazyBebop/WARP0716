"""Use real WARP to reject incompatible bytes at every owned stutter site."""

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

import pefile
import yaml
from verify_chat_performance import SOURCE_SHA256

ROOT = Path(__file__).resolve().parents[1]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--source", type=Path, required=True)
    a = p.parse_args()
    out = a.output.resolve()
    original = a.source.resolve()
    source = original.read_bytes()
    assert hashlib.sha256(source).hexdigest() == SOURCE_SHA256
    pe = pefile.PE(data=source)
    saved = {
        p: p.read_bytes() if p.exists() else None
        for p in [ROOT / "Settings.yml", ROOT / "SkippedPatches.log"]
    }
    rows = []
    try:
        for label, address in [
            ("prewrap", 0x83D452),
            ("history1", 0x83D73A),
            ("history2", 0x83DA71),
            ("native-fallback", 0x8663C4),
        ]:
            arm = out / "guard-rejections" / label
            arm.mkdir(parents=True, exist_ok=False)
            data = bytearray(source)
            offset = pe.get_offset_from_rva(address - 0x400000)
            data[offset] ^= 1
            changed = arm / "incompatible.exe"
            changed.write_bytes(data)
            mutated = pefile.PE(data=bytes(data))
            target = arm / "rejected.exe"
            profile = arm / "profile.yml"
            profile.write_text(
                yaml.safe_dump(
                    {
                        "from": changed.as_posix(),
                        "to": target.as_posix(),
                        "inputs": {},
                        "patches": ["ChatStutterFix"],
                    },
                    sort_keys=False,
                )
            )
            r = subprocess.run(
                [str(ROOT / "win32/WARP_console.exe"), "-using", str(profile)],
                cwd=ROOT,
                capture_output=True,
                timeout=90,
            )
            log = r.stdout + r.stderr
            (arm / "build.log").write_bytes(log)
            assert b"mismatch" in log or b"failed" in log.lower(), log.decode(
                errors="replace"
            )[-1000:]
            if target.exists():
                rejected = pefile.PE(str(target))
                for site, size in [(0x83D452, 5), (0x83D73A, 82), (0x83DA71, 80)]:
                    raw = rejected.get_data(site - 0x400000, size)
                    assert raw == mutated.get_data(
                        site - 0x400000, size
                    )
            rows.append(dict(site=label, rejected=True, no_hook_changes=True))
            print("PASS incompatible", label, flush=True)
    finally:
        for path, content in saved.items():
            if content is None:
                if path.exists():
                    path.unlink()
            else:
                path.write_bytes(content)
    (out / "guard-rejections.json").write_text(
        json.dumps(dict(passed=True, cases=rows), indent=2) + "\n"
    )


if __name__ == "__main__":
    main()
