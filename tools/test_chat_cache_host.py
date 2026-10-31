"""Compile and execute the production cache in a real Windows x86 host."""

import hashlib
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    out = ROOT / "Outputs/chat-performance/native-cache-host"
    out.mkdir(parents=True, exist_ok=True)
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
    command = out / "build.cmd"
    command.write_text(
        f'@echo off\ncall "{vs / "Common7/Tools/VsDevCmd.bat"}" -arch=x86 -host_arch=x64 >nul\nif errorlevel 1 exit /b 1\ncd /d "{out}"\ncl /nologo /EHsc /O2 /MT /W4 /WX /std:c++17 "{ROOT / "tools/native/chat_cache_host.cpp"}" /Fe:test.exe /link /DYNAMICBASE /FIXED:NO\nexit /b %errorlevel%\n'
    )
    r = subprocess.run(
        ["cmd.exe", "/d", "/c", str(command)], capture_output=True, timeout=120
    )
    (out / "build.log").write_bytes(r.stdout + r.stderr)
    assert not r.returncode, "See " + str(out / "build.log")
    r = subprocess.run(
        [str(out / "test.exe")], cwd=out, capture_output=True, timeout=20
    )
    assert not r.returncode, r.stdout + r.stderr
    assert r.stdout.startswith(b"PASS native Win32 cache:")
    report = dict(
        passed=True,
        real_win32_x86=True,
        native_font_boundary="controlled double",
        binary_sha256=hashlib.sha256((out / "test.exe").read_bytes()).hexdigest(),
        output=r.stdout.decode().strip(),
        live_gameplay_accepted=False,
    )
    (out / "result.json").write_text(json.dumps(report, indent=2) + "\n")
    print(report["output"])


if __name__ == "__main__":
    main()
