"""Regression checks for the deterministic builder, with automatic teardown."""

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    inputs = ROOT / "Inputs/DualWeaponRuntime"
    before = {name: (inputs / name).read_bytes() for name in ("compositor.dwcp", "legacy-support.dwls")}
    command = [sys.executable, str(ROOT / "tools/build_dual_weapon_runtime.py"), "--check"]
    subprocess.run(command, check=True)
    assert all((inputs / name).read_bytes() == data for name, data in before.items())
    with tempfile.TemporaryDirectory(prefix="dual-build-regression-") as temporary:
        fixture = Path(temporary)
        pins = json.loads((inputs / "build.json").read_text())
        names = [*pins["source_sha256"], "Inputs/DualWeaponRuntime/build.json",
                 "tools/build_dual_weapon_runtime.py", *["Inputs/DualWeaponRuntime/" + name for name in before]]
        for name in names:
            target = fixture / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / name, target)
        candidate = fixture / "Inputs/DualWeaponRuntime/compositor.dwcp"
        raw = bytearray(candidate.read_bytes())
        raw[-1] ^= 1
        candidate.write_bytes(raw)
        result = subprocess.run([sys.executable, str(fixture / "tools/build_dual_weapon_runtime.py"), "--check"],
                                capture_output=True, text=True)
        assert result.returncode and "payload is stale" in result.stderr, result.stderr
        assert candidate.read_bytes() == raw, "--check overwrote a corrupt input"
        source = fixture / "CustomDLL/DualWeapon/compositor.c"
        source.write_bytes(source.read_bytes() + b"\n// changed\n")
        result = subprocess.run([sys.executable, str(fixture / "tools/build_dual_weapon_runtime.py"), "--check"],
                                capture_output=True, text=True)
        assert result.returncode and "Pinned source differs" in result.stderr, result.stderr
    print("PASS exact rebuild, check-only immutability, stale payload rejection, source-pin rejection and temporary teardown")


if __name__ == "__main__":
    main()