"""Execute installed cache x86 and real native callers; font/CRT boundaries are doubles.

No in-game acceptance or frame-time claim is made by this suite.
"""

import argparse
import hashlib
import json
import struct
from pathlib import Path

from chat_native_test_support import Machine, native_crt, pack
from chat_native_test_support import Machine as IconMachine
from chat_patch_layout import installed_cache
from unicorn.x86_const import *

ROOT = Path(__file__).resolve().parents[1]
SOURCE = None  # Validated original input supplied by test_chat_performance.py.


class CacheMachine(IconMachine):
    def __init__(self, exe):
        Machine.__init__(self, str(exe))
        self.imports = {
            e.name.decode(): e.address
            for mod in self.pe.DIRECTORY_ENTRY_IMPORT
            for e in mod.imports
            if e.name
        }
        self.c = installed_cache(self.pe)
        assert self.c
        self.layout = [self.r(self.c["layout"] + 4 * i) for i in range(14)]
        self.native_calls = 0
        self.contexts = {}
        self.force_width = None
        self.on_measure = None
        native_crt(self)
        self.stub(0xDBC895, lambda: self.ret(0, self.alloc(self.args(1)[0])))
        self.stub(0xDBC89E, lambda: self.ret(0))
        # Execute the real generic thiscall, including its SEH frame and ret 24.
        self.u.hook_del(self._stub_handles.pop(0xA21C90))
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
        self.stub(step, self.decode)
        self.w(0x159B818, 949)
        self.owner = self.new_owner()
        self.output = self.alloc(4)

    def new_owner(self, vt=0x102D280):
        owner = self.alloc(0x200)
        self.w(owner, vt)
        self.w(owner + 0x24, self.alloc(0x40))
        return owner

    def buffer(self, value):
        ptr = self.alloc(len(value) + 1)
        self.u.mem_write(ptr, value + b"\0")
        return ptr

    def font_begin(self):
        obj = self.u.reg_read(UC_X86_REG_ECX)
        self.contexts[obj] = [0, 12, 0, 0]
        self.ret(4, obj)

    def font_config(self):
        self.contexts[self.u.reg_read(UC_X86_REG_ECX)] = self.args(4)
        self.ret(16)

    def units(self, text):
        pos = 0
        while pos < len(text):
            size = 1 if text[pos] < 128 else (3 if self.r(0x159B818) == 65001 else 2)
            yield text[pos : pos + size]
            pos += size

    def font_measure(self):
        ptr, length, out = self.args(3)
        text = bytes(self.u.mem_read(ptr, length))
        args = self.contexts[self.u.reg_read(UC_X86_REG_ECX)]
        self.native_calls += 1
        width = sum(
            3
            if unit == b" "
            else (
                0
                if unit in [b"\r", b"\n"]
                else (9 if len(unit) > 1 else 4 + unit[0] % 4)
            )
            for unit in self.units(text)
        )
        width += len(text) * (args[0] + args[1] - 12 + args[2] + args[3])
        if self.force_width is not None:
            width = self.force_width
        if self.on_measure:
            callback, self.on_measure = self.on_measure, None
            callback()
        self.w(out, width)
        self.w(out + 4, 12)
        self.ret(12)

    def decode(self):
        ptr, remaining = self.args(2)
        byte = self.u.mem_read(ptr, 1)[0]
        size = 1 if byte < 128 else (3 if self.r(0x159B818) == 65001 else 2)
        self.ret(8, ptr + min(size, remaining))

    def glyph(self, text=b"a", owner=None, length=None, ptr=None):
        ptr = self.buffer(text) if ptr is None else ptr
        self.invoke(
            self.c["glyph"],
            0,
            [
                self.owner if owner is None else owner,
                ptr,
                len(text) if length is None else length,
                self.output,
            ],
        )
        ok = self.u.reg_read(UC_X86_REG_EAX)
        return ok, struct.unpack("<i", self.u.mem_read(self.output, 4))[0]

    def fragment(self, text=b"fragment", owner=None, args=None, ptr=None):
        ptr = self.buffer(text) if ptr is None else ptr
        self.invoke(
            self.c["fragment"],
            self.owner if owner is None else owner,
            [ptr, *(args or [0, 0, 12, 0, 0])],
        )
        return struct.unpack("<i", pack(self.u.reg_read(UC_X86_REG_EAX)))[0]

    def clear_cache(self):
        self.u.mem_write(self.c["state"], bytes(self.layout[0]))


def test_hits_and_bounds(m):
    for text in [b"a", b"\x81\x82", b"\x81\x82" * 127 + b"x"]:
        m.clear_cache()
        before = m.native_calls
        first = m.glyph(text)
        assert first[0] == 1 and first[1] > 0
        assert m.glyph(text) == first and m.native_calls == before + 1
    for text in [b"", b"x" * 256]:
        before = m.native_calls
        assert m.glyph(text)[0] == 0 and m.native_calls == before
    assert m.glyph(owner=0)[0] == 0
    assert m.glyph(ptr=0, length=1)[0] == 0
    assert m.glyph(owner=m.new_owner(0x1037F80))[0] == 0
    for text in [b"x", b"x" * 511]:
        m.clear_cache()
        before = m.native_calls
        first = m.fragment(text)
        assert m.fragment(text) == first and m.native_calls == before + 1
    for text in [b"x" * 512, b"x" * 513]:
        m.clear_cache()
        before = m.native_calls
        m.fragment(text)
        m.fragment(text)
        assert m.native_calls == before + 2
    assert m.fragment(b"") == 0 and m.fragment(ptr=0) == 0
    for args in [
        [1, 0, 12, 0, 0],
        [0, 1, 12, 0, 0],
        [0, 0, 13, 0, 0],
        [0, 0, 12, 1, 0],
        [0, 0, 12, 0, 1],
    ]:
        m.clear_cache()
        before = m.native_calls
        a = m.fragment(args=args)
        assert m.fragment(args=args) == a and m.native_calls == before + 2
    alien = m.new_owner(0x1037F80)
    m.clear_cache()
    before = m.native_calls
    m.fragment(owner=alien)
    m.fragment(owner=alien)
    assert m.native_calls == before + 2
    print(
        "PASS native-width hit/miss, eligibility, explicit lengths, null/empty and 255/256/511/512 boundaries"
    )


def test_invalidation_and_storage(m):
    keys = [m.owner + 0x24, 0x159B80C, 0x159B8A4, 0x159B810, 0x159B818]
    keys += [0x11DCF30 + 4 * i for i in range(20)]
    encoding = m.r(0x159B80C)
    keys += [encoding + 0xB4]
    alternative = m.alloc(0x100)
    m.w(alternative, m.r(encoding))
    for addr in keys:
        m.clear_cache()
        m.glyph()
        m.fragment()
        before = m.native_calls
        old = m.r(addr)
        m.w(addr, alternative if addr == 0x159B80C else old + 1)
        m.glyph()
        m.fragment()
        assert m.native_calls == before + 2, hex(addr)
        m.w(addr, old)
    for fn in [m.glyph, m.fragment]:
        m.clear_cache()
        before = m.native_calls
        m.on_measure = lambda: m.w(0x159B818, m.r(0x159B818) + 1)
        fn()
        fn()
        assert m.native_calls == before + 2, "Changed key during miss was stored"
        m.w(0x159B818, 949)
        for bad in [0, -1]:
            m.clear_cache()
            m.force_width = bad
            before = m.native_calls
            fn()
            fn()
            assert m.native_calls == before + 2
            m.force_width = None
            fn()
            fn()
            assert m.native_calls == before + 3
    # Cache owns bytes, independent of source addresses and source buffer reuse.
    m.clear_cache()
    ptr = m.buffer(b"ab")
    a = m.glyph(b"ab", ptr=ptr)
    m.u.mem_write(ptr, b"cd")
    b = m.glyph(b"cd", ptr=ptr)
    before = m.native_calls
    assert m.glyph(b"ab") == a and m.glyph(b"cd") == b and m.native_calls == before
    m.clear_cache()
    ptr = m.buffer(b"first")
    a = m.fragment(ptr=ptr)
    m.u.mem_write(ptr, b"other")
    m.fragment(ptr=ptr)
    assert m.fragment(b"first") == a
    # Force a matching hash+length but different bytes in the exact slot.
    state = m.c["state"]
    base = state + m.layout[9]
    for i in range(32):
        entry = base + i * m.layout[5]
        if m.r(entry + 8) > 0 and bytes(m.u.mem_read(entry + 12, 5)) == b"first":
            m.u.mem_write(entry + 12, b"XXXXX")
            break
    before = m.native_calls
    m.fragment(b"first")
    assert m.native_calls == before + 1
    # Distinct full hashes sharing the same low-five-bit direct-map slot.
    m.clear_cache()
    before = m.native_calls
    m.fragment(b"a")
    m.fragment(b"A")
    m.fragment(b"a")
    assert m.native_calls == before + 3
    # Owner identity invalidates even when the complete painter/font key agrees.
    m.clear_cache()
    alias = m.new_owner()
    m.w(alias + 0x24, m.r(m.owner + 0x24))
    before = m.native_calls
    m.fragment(owner=m.owner)
    m.fragment(owner=alias)
    m.fragment(owner=m.owner)
    assert m.native_calls == before + 3
    # Each of the four owner contexts, fifth-owner replacement and generation wrap.
    m.clear_cache()
    owners = [m.new_owner() for _ in range(5)]
    for owner in owners[:4]:
        m.glyph(owner=owner)
    before = m.native_calls
    for owner in owners[:4]:
        m.glyph(owner=owner)
    assert m.native_calls == before
    m.glyph(owner=owners[4])
    m.glyph(owner=owners[0])
    assert m.native_calls == before + 2
    m.clear_cache()
    m.glyph()
    ctx = state + m.layout[6]
    m.w(ctx + m.layout[10], 0xFFFFFFFF)
    m.w(0x159B810, m.r(0x159B810) + 1)
    m.glyph()
    assert m.r(ctx + m.layout[10]) == 1
    m.w(0x159B810, m.r(0x159B810) - 1)
    m.clear_cache()
    for i in range(17):
        m.glyph(bytes([0x81, i + 1]))
    before = m.native_calls
    m.glyph(b"\x81\x01")
    assert m.native_calls == before + 1
    # Contention and abandoned measurements keep the native fallback.
    m.w(state, 1)
    assert m.glyph()[0] == 0
    before = m.native_calls
    m.fragment()
    m.fragment()
    assert m.native_calls == before + 2
    m.w(state, 0)
    print(
        "PASS all 26 key dependencies, post-miss changes, failed widths, owned bytes, collisions, eviction, generation wrap and busy fallback"
    )


def test_reentrancy_and_real_fragment(m):
    # Reenter the installed x86 from inside the font boundary. The emulated
    # CPU executes both nested calls; Python does not recursively invoke Unicorn.
    for fragment in [False, True]:
        m.clear_cache()
        text = m.buffer(b"R")
        result = m.alloc(4)
        thunk = m.alloc(128)
        leaf = m.alloc(16)
        args = [text, 0, 0, 12, 0, 0] if fragment else [m.owner, text, 1, m.output]
        target = m.c["fragment" if fragment else "glyph"]
        code = b"\x9c\x60" + b"".join(b"\x68" + pack(v) for v in reversed(args))
        code += b"\xb9" + pack(m.owner)
        code += b"\xe8" + pack(target - (thunk + len(code) + 5))
        code += b"\xa3" + pack(result) + b"\x61\x9d"
        code += b"\xe9" + pack(leaf - (thunk + len(code) + 5))
        m.u.mem_write(thunk, code)
        m.stub(leaf, m.font_measure)
        entered = [False]

        def reenter():
            if entered[0]:
                m.font_measure()
            else:
                entered[0] = True
                assert m.r(m.c["state"]) == 1
                m.u.reg_write(UC_X86_REG_EIP, thunk)

        m.stub(0x546C80, reenter)
        before = m.native_calls
        if fragment:
            m.fragment(b"R")
        else:
            m.glyph(b"R")
        assert entered[0] and m.r(m.c["state"]) == 0
        assert m.r(result) == (6 if fragment else 0)
        assert m.native_calls == before + (2 if fragment else 1)
    m.stub(0x546C80, m.font_measure)
    # Execute the actual fragment caller, native history insertion and max-width
    # update. Only its final UI invalidation virtual method is doubled.
    m.clear_cache()
    owner = m.new_owner()
    m.stub(0x85E120, lambda: m.ret(0))
    before = m.native_calls
    for _ in range(2):
        m.invoke(0x83DD90, owner, [m.buffer(b"fragment exact caller")])
    begin, end = m.r(owner + 0x88), m.r(owner + 0x8C)
    assert (
        end - begin == 48
        and m.str_value(begin) == m.str_value(begin + 24) == "fragment exact caller"
    )
    assert m.r(owner + 0xA0) > 0 and m.native_calls == before + 1
    # Unavailable state forwards safely; static reservation has no runtime
    # allocator failure mode. A busy/abandoned miss disables reuse.
    api = (
        m.c["code"]
        + json.loads((ROOT / "Inputs/ChatMeasurementCache/runtime.json").read_text())[
            "exports"
        ]["ChatCacheApi"]
    )
    state = m.r(api)
    assert state == m.c["state"]
    m.w(api, 0)
    assert m.glyph()[0] == 0
    before = m.native_calls
    m.fragment()
    m.fragment()
    assert m.native_calls == before + 2
    m.w(api, state)
    print(
        "PASS actual x86 recursion, unavailable-state fallback and native fragment insertion/max-width/ret-24 contracts"
    )


def test_adapter(m):
    frame = m.alloc(0x500) + 0x300
    text = m.buffer(b"W")
    for owner in [m.owner, m.new_owner(0x1037F80)]:
        for repeat in range(2):
            m.w(frame - 0x44, owner)
            m.w(frame - 0x3C, text)
            m.w(frame - 4, 0xFFFFFFFF)
            regs = {
                UC_X86_REG_EBP: frame,
                UC_X86_REG_ESP: 0x3000E000,
                UC_X86_REG_ESI: 1,
                UC_X86_REG_EDI: 1,
                UC_X86_REG_EBX: 0x12345678,
                UC_X86_REG_EFLAGS: 0x246,
            }
            for reg, value in regs.items():
                m.u.reg_write(reg, value)
            m.u.emu_start(0xA23BA9, 0xA23C00, count=1000000)
            for reg in [UC_X86_REG_EBP, UC_X86_REG_ESP, UC_X86_REG_EDI, UC_X86_REG_EBX]:
                assert m.u.reg_read(reg) == regs[reg], (
                    hex(reg),
                    hex(m.u.reg_read(reg)),
                )
            assert (
                m.u.reg_read(UC_X86_REG_ESI) == 7
                and m.u.reg_read(UC_X86_REG_EAX) == text
            )
            assert m.r(frame - 4) == 0xFFFFFFFF
    print(
        "PASS real glyph hook: miss/hit and displaced native fallback, register/stack/SEH contracts"
    )


def split_rows(m, text, width):
    vector = m.alloc(12)
    source = m.buffer(text)
    m.invoke(0xA23A20, m.owner, [source, vector, width])
    begin, end = m.r(vector), m.r(vector + 4)
    assert begin <= end and (end - begin) % 24 == 0
    return [m.str_value(p).encode("latin1") for p in range(begin, end, 24)]


def test_native_splitter(exe):
    cached = CacheMachine(exe)
    control = CacheMachine(exe)
    source = SOURCE.read_bytes()
    for address, size in [(0xA23BA9, 12), (0x83DEB7, 5)]:
        off = control.pe.get_offset_from_rva(address - control.base)
        control.u.mem_write(address, source[off : off + size])
        control.u.ctl_remove_cache(address, address + size)
    cases = [
        b"ordinary repeated chat words " * 6,
        b"x" * 180,
        b"one\r\ntwo\nthree",
        b"\x81\x82A " * 30,
        b"color ^FF0000red ^000000normal " * 5,
        b"Alice: hello there " * 10,
    ]
    vectors = 0
    for vt in [0x102D280, 0x102D370, 0x102D460, 0x1037F80]:
        cached.w(cached.owner, vt)
        control.w(control.owner, vt)
        for cp in [949, 65001]:
            cached.w(0x159B818, cp)
            control.w(0x159B818, cp)
            for width in [24, 80, 240, 600]:
                for text in cases:
                    if cp == 65001:
                        text = text.replace(b"\x81\x82", b"\xe3\x81\x82")
                    a = split_rows(control, text, width)
                    b = split_rows(cached, text, width)
                    assert a == b, (hex(vt), cp, width, text, a, b)
                    vectors += 1
    # Matched repeat/reflow measurements under the same backend and cache key.
    cached.w(cached.owner, 0x102D280)
    control.w(control.owner, 0x102D280)
    cached.clear_cache()
    cached.native_calls = control.native_calls = 0
    for _ in range(8):
        assert split_rows(control, b"repeated chat history " * 24, 120) == split_rows(
            cached, b"repeated chat history " * 24, 120
        )
    assert cached.native_calls < control.native_calls
    result = dict(
        vectors=vectors,
        uncached_measurements=control.native_calls,
        cached_measurements=cached.native_calls,
        rows_equal=True,
    )
    print("PASS native splitter A/B", json.dumps(result))
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("exe", type=Path)
    ap.add_argument("--report", type=Path)
    args = ap.parse_args()
    m = CacheMachine(args.exe)
    original_code = bytes(m.u.mem_read(m.c["code"], m.c["code_size"]))
    tail = m.c["state"] + m.layout[0]
    m.u.mem_write(tail, b"Z" * 32)
    for test in [
        test_hits_and_bounds,
        test_invalidation_and_storage,
        test_reentrancy_and_real_fragment,
        test_adapter,
    ]:
        m.clear_cache()
        test(m)
    assert bytes(m.u.mem_read(m.c["code"], m.c["code_size"])) == original_code, (
        "Emitted code changed"
    )
    assert bytes(m.u.mem_read(tail, 32)) == b"Z" * 32, "State extent exceeded"
    result = test_native_splitter(args.exe)
    result.update(
        exe=str(args.exe.resolve()),
        sha256=hashlib.sha256(args.exe.read_bytes()).hexdigest(),
        native_font_and_crt_boundaries="controlled test doubles",
        live_accepted=False,
    )
    if args.report:
        args.report.write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
