"""Check the WARP banner, metadata alignment and QJS source encoding.

Generated templates obey the same contract as their exported patch files.
This complements, rather than replaces, real WARP and native execution tests.
"""

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULTS = [
    "Scripts/Patches/ChatPerformanceNative.qjs",
    "Scripts/Patches/ChatMeasurementCache.qjs",
    "Scripts/Patches/ChatStutterFix.qjs",
]

WIDTH = 76


def verify(path):
    raw = path.read_bytes()
    assert raw.startswith(b"/*"), f"{path}: missing banner or UTF-8 BOM"
    assert b"\n" not in raw.replace(b"\r\n", b""), f"{path}: bare LF"
    text = raw.decode("utf-8")
    lines = text.splitlines()
    assert lines[0] == "/" + "*" * (WIDTH - 2) + "\\", f"{path}: opening border"
    closing = "\\" + "*" * (WIDTH - 2) + "/"
    end = lines.index(closing)
    header = lines[: end + 1]
    for number, line in enumerate(header, 1):
        assert len(line) == WIDTH, (
            f"{path}:{number}: header width {len(line)} != {WIDTH}"
        )
        if number not in [1, end + 1]:
            assert line[0] == line[-1] and line[0] in "*|", (
                f"{path}:{number}: border alignment"
            )
        if re.match(
            r"\*   (?:Author\(s\)|Created Date|Last Modified|Description|Evidence|Verifier|Generator)\s*:",
            line,
        ):
            assert line[18] == ":", f"{path}:{number}: metadata colon alignment"
    for label in ["Author(s)", "Last Modified", "Description", "Evidence", "Verifier"]:
        assert any(label in line for line in header), f"{path}: missing {label}"
    for number, line in enumerate(lines[end + 1 :], end + 2):
        assert not line.startswith(" "), f"{path}:{number}: use tabs for indentation"
        assert line == line.rstrip(), f"{path}:{number}: trailing whitespace"
    assert not re.search(r"\bnew\s+Date\s*\(", text), f"{path}: unsupported Date API"
    assert "console.error(" not in text, f"{path}: unconfirmed console.error API"
    return dict(path=str(path), banner_width=WIDTH, header_lines=len(header))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path)
    args = parser.parse_args()
    paths = args.paths or [ROOT / name for name in DEFAULTS]
    for path in paths:
        result = verify(path)
        print(
            f"PASS {result['path']}: aligned {WIDTH}-column banner, tabs, CRLF, UTF-8 without BOM"
        )
