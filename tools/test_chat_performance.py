"""Execute native 2025-07-16 chat matrices and four independently built states.

Requires pefile, capstone and unicorn. Font/CRT/OS boundaries are explicit
in chat_native_test_support; no private UI patch or image pack is required.
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

import chat_cache_cases
import chat_stutter_cases
from test_chat_history_stutter import run as history_cases
from verify_chat_performance import verify


def states(matrix):
    from chat_stutter_cases import StutterMachine

    corpus = [
        b"",
        b"a",
        b"combat event 12345",
        b"W" * 65,
        b"Alice: " + b"wide words " * 30,
        b"<ITEML>one</ITEML> and <ITEML>two</ITEML>",
        b"Alice: ^i[501]Red Potion",
        b"one\r\ntwo",
    ]
    baseline = None
    results = []
    for name in ["baseline", "stutter", "cache", "both"]:
        m = StutterMachine(matrix[name])
        values = [m.message(text, width) for width in [24, 80, 240] for text in corpus]
        if baseline is None:
            baseline = values
        else:
            assert values == baseline, (name, "Native rows/routes differ")
        native, copies = m.native_calls, m.temp_constructs
        for _ in range(100):
            m.message(b"repeat combat message", 240)
        native = m.native_calls - native
        copies = m.temp_constructs - copies
        assert copies == (0 if name in ["stutter", "both"] else 100)
        results.append(
            dict(
                state=name,
                wrapping_vectors=len(values),
                native_measurements=native,
                temporary_strings=copies,
            )
        )
    assert results[2]["native_measurements"] < results[0]["native_measurements"]
    assert results[3]["native_measurements"] < results[1]["native_measurements"]
    return results


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("exe", type=Path)
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--matrix", type=Path, required=True)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=True)
    assert (
        hashlib.sha256(a.source.read_bytes()).hexdigest()
        == "ead7c0a316bc6c27705a5a6876daf5093abec31677f3c1af7525c1709b201bff"
    )
    verify(a.exe, a.source, history_sites=2)
    chat_cache_cases.SOURCE = chat_stutter_cases.SOURCE = a.source
    for module, name in [(chat_stutter_cases, "stutter"), (chat_cache_cases, "cache")]:
        sys.argv = [name, str(a.exe), "--report", str(a.output / (name + ".json"))]
        module.main()
    history = history_cases(a.exe, a.source, a.output / "history")
    result = dict(
        passed=True,
        history_cases=history["standard_grammar_vectors"] + history["guarded_runtime_tag_vectors"],
        states=states(
            {
                name: a.matrix.parent / case["exe"]
                for name, case in json.loads(a.matrix.read_text()).items()
            }
        ),
        source_sha256=hashlib.sha256(a.source.read_bytes()).hexdigest(),
        exe_sha256=hashlib.sha256(a.exe.read_bytes()).hexdigest(),
    )
    (a.output / "build-states.json").write_text(json.dumps(result, indent=2) + "\n")
    print(
        "PASS all four independently built states, 96 wrapping vectors and unchanged native rows"
    )


if __name__ == "__main__":
    main()
