"""Execute both guarded history blocks and native tag classification/fallback in x86."""

import argparse
import hashlib
import json
from pathlib import Path

import pefile
import chat_stutter_cases
from chat_patch_layout import HISTORY_SITES, installed_histories
from chat_stutter_cases import StutterMachine
from unicorn import UC_HOOK_CODE
from verify_chat_performance import SOURCE_SHA256
from unicorn.x86_const import (
    UC_X86_REG_EBP,
    UC_X86_REG_EBX,
    UC_X86_REG_ECX,
    UC_X86_REG_EDI,
    UC_X86_REG_EIP,
    UC_X86_REG_ESI,
    UC_X86_REG_ESP,
)

SITES = [
    dict(
        name="site" + str(i + 1), address=address, size=size, tagged=tagged, plain=plain
    )
    for i, (address, size, tagged, plain) in enumerate(HISTORY_SITES)
]
NORMAL = [b"<NAVIL>", b"</NAVIL>", b"<ITEML>", b"</ITEML>"]


class BlockMachine(StutterMachine):
    def __init__(self, exe, source, patched):
        super().__init__(exe)
        self.trace = []
        self.constructs = 0
        self.stub(0x83DD90, self.plain)
        self.u.hook_add(
            UC_HOOK_CODE, lambda u, a, s, d: self.tagged(), begin=0x8663DA, end=0x8663DA
        )
        self.u.hook_add(
            UC_HOOK_CODE,
            lambda u, a, s, d: setattr(self, "constructs", self.constructs + 1),
            begin=0x4F1940,
            end=0x4F1940,
        )
        if not patched:
            original = pefile.PE(str(source))
            for site in SITES:
                self.u.mem_write(
                    site["address"],
                    original.get_data(site["address"] - 0x400000, site["size"]),
                )
                self.u.ctl_remove_cache(site["address"], site["address"] + site["size"])

    def plain(self):
        self.trace.append(("plain", self.cstr(self.args(1)[0])))
        self.ret(4)

    def tagged(self):
        frame = self.u.reg_read(UC_X86_REG_EBP)
        self.trace.append(("tag-parser", self.cstr(self.r(frame + 8))))
        self.u.emu_stop()

    def block(self, site, text, tags=NORMAL):
        self.set_tags(tags)
        self.trace.clear()
        text_ptr = self.alloc(len(text) + 1)
        self.u.mem_write(text_ptr, text + b"\0")
        frame = self.alloc(0x500) + 0x200
        stack = 0x3000D000
        self.w(frame + 8, text_ptr)
        self.w(frame + 12, 0x123456)
        self.w(frame + 16, 4)
        self.w(frame - 4, 0xFFFFFFFF)
        self.w(frame - 0x14, 4)
        self.w(0x131ED60, self.alloc(0x100))
        for reg, value in [
            (UC_X86_REG_EBP, frame),
            (UC_X86_REG_ESP, stack),
            (UC_X86_REG_ESI, text_ptr),
            (UC_X86_REG_EBX, text_ptr),
            (UC_X86_REG_EDI, self.pane),
            (UC_X86_REG_ECX, self.pane),
        ]:
            self.u.reg_write(reg, value)
        self.w(0, 0)
        before = self.constructs
        end = 0x83D7B4 if site["name"] == "site1" else 0x83DAF7
        self.u.emu_start(site["address"], end, count=2000000)
        tagged = self.u.reg_read(UC_X86_REG_EIP) == 0x8663DA
        if not tagged:
            assert self.u.reg_read(UC_X86_REG_EIP) == end
            assert self.u.reg_read(UC_X86_REG_ESP) == stack
            assert self.u.reg_read(UC_X86_REG_EBP) == frame
            assert self.u.reg_read(UC_X86_REG_EDI) == self.pane
            register = UC_X86_REG_EBX if site["name"] == "site1" else UC_X86_REG_ESI
            assert self.u.reg_read(register) == self.r(0x131ED60), (
                "Original receiver load was not replayed"
            )
            assert self.r(frame - 4) == 0xFFFFFFFF and self.r(0) == 0
        return dict(
            trace=list(self.trace),
            temporary_strings=self.constructs - before,
            native_tag_path=tagged,
        )


def run(exe, source, out):
    assert hashlib.sha256(source.read_bytes()).hexdigest() == SOURCE_SHA256
    chat_stutter_cases.SOURCE = source
    out.mkdir(parents=True, exist_ok=True)
    assert len(installed_histories(pefile.PE(str(exe)))) == 2
    original, changed = BlockMachine(exe, source, False), BlockMachine(exe, source, True)
    corpus = [
        b"",
        b"plain",
        b"a" * 15,
        b"a" * 16,
        b"a" * 63,
        b"a" * 64,
        b"a" * 65,
        b"a" * 1500,
        b"<3",
        b"<<",
        b"a < b",
        b"x\r\ny",
        b"\x81\x82text",
        b"^FF0000colored",
        b"<ITEML>test</ITEML>",
        b"<NAVIL>prontera,1,2</NAVIL>",
        b"x" * 200 + b"<NAVIL>late",
        b"^i[501]Potion",
    ]
    rows = []
    for site in SITES:
        for text in corpus:
            a, b = original.block(site, text), changed.block(site, text)
            assert a["trace"] == b["trace"], (site["name"], text, a, b)
            rows.append(
                dict(site=site["name"], input_hex=text.hex(), original=a, proposed=b)
            )
    # Explicitly exercise the boundary of the literal-'<' fast-filter assumption.
    exceptions = []
    for tags, text in [
        ([b"Q", b"Z", b"Y", b"X"], b"Q"),
        ([b"", b"</NAVIL>", b"<ITEML>", b"</ITEML>"], b"ordinary"),
        (
            [b"long_custom_marker_12345", b"end", b"x", b"y"],
            b"long_custom_marker_12345",
        ),
    ]:
        for site in SITES:
            a, b = original.block(site, text, tags), changed.block(site, text, tags)
            assert a["trace"] == b["trace"], (site["name"], tags, a, b)
            exceptions.append(dict(site=site["name"], equal=True))
    result = dict(
        standard_grammar_vectors=len(rows),
        guarded_runtime_tag_vectors=len(exceptions),
        standard_output_and_recognition_equal=True,
        actual_native_classifier_and_false_positive_fallback_executed=True,
        native_tag_renderer_boundary="Stopped at the unchanged recognized-tag parser; full rendering is a separate test",
        nonstandard_runtime_tag_vectors=exceptions,
        cases=rows,
        installed_client_modified=False,
    )
    (out / "history-tests.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("exe", type=Path)
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    result = run(args.exe.resolve(), args.source.resolve(), args.output.resolve())
    print(json.dumps({k: v for k, v in result.items() if k != "cases"}, indent=2))


if __name__ == "__main__":
    main()
