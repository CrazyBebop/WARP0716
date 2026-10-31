"""Execute installed stutter x86 and compare real native append/wrapping paths.

CRT allocation/memchr and font measurement are explicit test boundaries.
The native classifier, byte-search helper, splitter and append cleanup execute.
"""

import argparse
import hashlib
import json
import random
from pathlib import Path

import pefile
from chat_cache_cases import CacheMachine
from chat_native_test_support import Machine, native_crt
from chat_native_test_support import Machine as IconMachine
from chat_patch_layout import installed_stutter
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import *

SOURCE = None  # Supplied by the public test runner after validating the original input.
TAGS = [0x1202C28, 0x1202C40, 0x1202B50, 0x1202B68]
NORMAL = [b"<NAVIL>", b"</NAVIL>", b"<ITEML>", b"</ITEML>"]


class StutterMachine(IconMachine):
    font_begin = CacheMachine.font_begin
    font_config = CacheMachine.font_config
    font_measure = CacheMachine.font_measure
    units = CacheMachine.units
    decode = CacheMachine.decode

    def __init__(self, exe, uncached=False):
        Machine.__init__(self, str(exe))
        self.imports = {
            e.name.decode(): e.address
            for d in self.pe.DIRECTORY_ENTRY_IMPORT
            for e in d.imports
            if e.name
        }
        self.record = self.descriptor()
        native_crt(self)
        self.allocations = 0
        self.allocated_bytes = 0
        for address in [0xDBBC4F, 0xDBBEAE, 0xDBC895]:
            self.stub(address, self.allocate_boundary)
        self.stub(0xDBC89E, lambda: self.ret(0))
        self.u.hook_del(self._stub_handles.pop(0xA21C90))
        self.native_calls = 0
        self.contexts = {}
        self.force_width = None
        self.on_measure = None
        self.stub(0x5443C0, self.font_begin)
        self.stub(0x546F60, self.font_config)
        self.stub(0x546C80, self.font_measure)
        self.stub(0x5446F0, lambda: self.ret(0))
        decoder = self.alloc(0x100)
        vt = self.alloc(0x20)
        step = self.alloc(16)
        self.w(decoder, vt)
        self.w(vt + 0x14, step)
        self.w(0x159B80C, decoder)
        self.w(0x159B818, 949)
        self.stub(step, self.decode)
        self.set_tags(NORMAL)
        self.routes = []
        self.rows = []
        self.temp_constructs = 0
        self.temp_destroys = 0
        self.observe(
            0x83D480, lambda: setattr(self, "temp_constructs", self.temp_constructs + 1)
        )
        self.observe(
            0x7FB087, lambda: setattr(self, "temp_destroys", self.temp_destroys + 1)
        )
        self.observe(0x83D49B, lambda: self.route("direct"))
        self.observe(0x83D4AF, lambda: self.route("wrap"))
        self.dispatch = self.alloc(16)
        self.stub(self.dispatch, self.append)
        for table in [0x102D280, 0x102D370, 0x102D460]:
            self.w(table + 0xE4, self.dispatch)
        self.parent = self.window(vt=0x1037F80)
        self.pane = self.window(vt=0x102D280, parent=self.parent)
        if uncached:
            native = pefile.PE(str(SOURCE))
            self.u.mem_write(0x83D452, native.get_data(0x83D452 - 0x400000, 5))
            self.u.ctl_remove_cache(0x83D452, 0x83D457)

    def descriptor(self):
        return installed_stutter(self.pe)

    def observe(self, address, callback):
        self.u.hook_add(
            UC_HOOK_CODE, lambda u, a, s, d: callback(), begin=address, end=address
        )

    def set_tags(self, tags):
        for address, text in zip(TAGS, tags):
            self.string(text, address)

    def allocate_boundary(self):
        size = self.args(1)[0]
        self.allocations += 1
        self.allocated_bytes += size
        self.ret(0, self.alloc(size))

    def route(self, name):
        frame = self.u.reg_read(UC_X86_REG_EBP)
        assert self.r(frame - 4) == 0, "Native vector EH state was not retained"
        self.routes.append(name)

    def append(self):
        text, color, original = self.args(3)
        self.rows.append((self.cstr(text), color, self.cstr(original)))
        self.ret(12)

    def message(self, text, width=120, vt=0x102D280, parent=0x1037F80):
        self.w(self.parent, parent)
        self.w(self.pane, vt)
        self.w(self.pane + 0x14, width)
        self.routes.clear()
        self.rows.clear()
        source = self.alloc(len(text) + 1)
        self.u.mem_write(source, text + b"\0")
        fs_before = self.r(0)
        self.invoke(0x83D3F0, self.pane, [source, 0x345678, source])
        assert self.r(0) == fs_before, "Native SEH chain leaked"
        assert bytes(self.u.mem_read(source, len(text) + 1)) == text + b"\0", (
            "Input bytes changed"
        )
        return list(self.routes), list(self.rows)

    def classify(self, text, native=False):
        if native:
            # Use native construction so >=4096-byte strings carry MSVC's
            # aligned-allocation header expected by the real destructor.
            obj = self.string(b"")
            ptr = self.alloc(len(text) + 1)
            self.u.mem_write(ptr, text + b"\0")
            self.invoke(0x4F1940, obj, [ptr, len(text)])
            args = [self.r(obj + 4 * i) for i in range(6)]
            self.invoke(0x7FAF70, 0, args)
        else:
            ptr = self.alloc(len(text) + 1)
            self.u.mem_write(ptr, text + b"\0")
            self.invoke(self.record["matcher"], 0, [ptr])
        return self.u.reg_read(UC_X86_REG_EAX) & 255


def matcher_parity(m):
    randomizer = random.Random(20250716)
    vectors = 0
    tag_sets = [
        NORMAL,
        [b"Q" * 21, b"ZZ", b"\x81\x82", b""],
        [b"<x>", b"a\0b", b"custom_long_needle_0123456789", b"\x01\x02"],
    ]
    for tags in tag_sets:
        m.set_tags(tags)
        cases = [
            b"",
            b"x" * 63,
            b"x" * 64,
            b"x" * 65,
            b"x" * 4096,
            b"<iteml>",
            b"xx: yy\r\nzz",
        ]
        for tag in tags:
            if b"\0" not in tag:
                cases += [tag, b"x" * 63 + tag, b"x" * 1024 + tag + b"tail", tag * 3]
        cases += [
            bytes(
                randomizer.choice(b"ab<>/ITEML: \r\n\x81\x82")
                for _ in range(randomizer.randrange(1, 250))
            )
            for _ in range(80)
        ]
        for text in cases:
            assert m.classify(text) == m.classify(text, native=True), (tags, text)
            vectors += 1
    m.set_tags(NORMAL)
    print(
        "PASS native classifier parity",
        vectors,
        "vectors, live inline/heap/empty/binary tag strings",
    )
    return vectors


def append_parity(exe):
    optimized = StutterMachine(exe)
    control = StutterMachine(exe, uncached=True)
    corpus = [
        b"",
        b"a",
        b"x" * 15,
        b"x" * 16,
        b"x" * 63,
        b"x" * 64,
        b"x" * 65,
        b"x" * 1500,
        b"Alice: text " * 15,
        b"one\r\ntwo\nthree",
        b"wide WWWWWWWWWWWWWWWWWWW",
        b"\x81\x82 " * 35,
        b"plain ^FF0000colored ^000000message",
        b"<ITEM>501</ITEM>",
        b"x" * 70 + b"<ITEML>00000085'00)00)00)00)00</ITEML>",
        b"x" * 1100 + b"<ITEML>late</ITEML>",
        b"<ITEML>one</ITEML> and <ITEML>two</ITEML>",
        b"Alice: ^i[501]Red Potion and ^i[1201,0]Dagger",
        b"<NAVIL>prontera,1,2</NAVIL>",
        b"near\r" + b"x" * 62 + b": tail",
        b"x" * 63 + b": tail",
    ]
    vectors = 0
    for parent in [0x1037F80, 0x1037EA8]:
        for width in [24, 80, 240, 600]:
            for text in corpus:
                a = control.message(text, width, parent=parent)
                b = optimized.message(text, width, parent=parent)
                assert a == b, (parent, width, text, a, b)
                assert optimized.temp_constructs == 0 and optimized.temp_destroys == 0
                vectors += 1
    # Same history classes and two encoding backends, with exactly matched rows.
    for table in [0x102D370, 0x102D460]:
        for cp, text in [(949, b"\x81\x82A " * 20), (65001, b"\xe3\x81\x82A " * 20)]:
            control.w(0x159B818, cp)
            optimized.w(0x159B818, cp)
            assert control.message(text, 80, vt=table) == optimized.message(
                text, 80, vt=table
            )
            vectors += 1
    # Matched repeated message workload: font and row operations stay native.
    before = [
        control.temp_constructs,
        optimized.temp_constructs,
        control.allocations,
        optimized.allocations,
    ]
    for _ in range(100):
        text = b"ordinary combat log message with repeated text"
        assert control.message(text, 240) == optimized.message(text, 240)
    counts = dict(
        uncached_temporary_strings=control.temp_constructs - before[0],
        optimized_temporary_strings=optimized.temp_constructs - before[1],
        uncached_heap_calls=control.allocations - before[2],
        optimized_heap_calls=optimized.allocations - before[3],
    )
    assert (
        counts["uncached_temporary_strings"] == 100
        and counts["optimized_temporary_strings"] == 0
    )
    assert counts["optimized_heap_calls"] < counts["uncached_heap_calls"], counts
    print("PASS native append/wrapping", vectors, "vectors;", json.dumps(counts))
    return dict(vectors=vectors, rows_and_routes_equal=True, **counts)


def null_fallback(m):
    frame = m.alloc(256) + 128
    sp = 0x3000D000
    m.u.reg_write(UC_X86_REG_EBP, frame)
    m.u.reg_write(UC_X86_REG_ESP, sp)
    m.u.reg_write(UC_X86_REG_ESI, 0)
    m.u.reg_write(UC_X86_REG_EDX, 0)
    m.u.emu_start(0x83D452, 0x83D457, count=10000)
    assert m.u.reg_read(UC_X86_REG_EIP) == 0x83D457
    assert m.u.reg_read(UC_X86_REG_ESP) == sp - 24
    assert m.u.reg_read(UC_X86_REG_ECX) == sp - 24
    print("PASS null request replays displaced native preprocessing")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("exe", type=Path)
    ap.add_argument("--report", type=Path)
    args = ap.parse_args()
    m = StutterMachine(args.exe)
    matcher_vectors = matcher_parity(m)
    null_fallback(m)
    result = append_parity(args.exe)
    result.update(
        matcher_vectors=matcher_vectors,
        exe=str(args.exe.resolve()),
        sha256=hashlib.sha256(args.exe.read_bytes()).hexdigest(),
        native_search_and_splitter_executed=True,
        font_and_crt_boundaries="controlled doubles",
        deployed=False,
        live_accepted=False,
    )
    if args.report:
        args.report.write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
