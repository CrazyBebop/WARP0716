"""Bounded x86/CRT/font test boundaries; native classifiers and splitters execute.

No renderer, image assets, private UI patch or OS thread runs in Unicorn.
The separate Win32 host tests production cache code on the real x86 ABI.
"""

import struct

import pefile
from unicorn import UC_ARCH_X86, UC_HOOK_CODE, UC_MODE_32, Uc
from unicorn.x86_const import *


def pack(value):
    return struct.pack("<I", value & 0xFFFFFFFF)


class Machine:
    def __init__(self, exe):
        self.pe = pefile.PE(str(exe))
        self.base = self.pe.OPTIONAL_HEADER.ImageBase
        self.u = Uc(UC_ARCH_X86, UC_MODE_32)
        self.u.mem_map(0, 0x1000)
        self.u.mem_map(self.base, (self.pe.OPTIONAL_HEADER.SizeOfImage + 4095) & ~4095)
        self.u.mem_write(self.base, self.pe.get_memory_mapped_image())
        self.u.mem_map(0x20000000, 0x08000000)
        self.u.mem_map(0x30000000, 0x10000)
        self.heap, self.stop = 0x20000000, 0x30000000
        self.stub(0xA21C90, lambda: self.ret(24, 0))
        self.stub(0xDBBBD4, lambda: self.ret(0))

    def stub(self, address, fn):
        if not hasattr(self, "_stub_handles"):
            self._stub_handles = {}
        if address in self._stub_handles:
            self.u.hook_del(self._stub_handles[address])
        self._stub_handles[address] = self.u.hook_add(
            UC_HOOK_CODE, lambda u, a, s, d: fn(), begin=address, end=address
        )

    def cstr(self, address):
        result = bytearray()
        for offset in range(4096):
            value = self.u.mem_read(address + offset, 1)[0]
            if value == 0:
                return result.decode("latin1")
            result.append(value)
        raise AssertionError("unterminated test string")

    def string(self, value, where=None):
        value = value.encode("latin1") if isinstance(value, str) else value
        obj = where if where is not None else self.alloc(24)
        self.u.mem_write(obj, bytes(24))
        if len(value) < 16:
            data, capacity = obj, 15
        else:
            data, capacity = self.alloc(len(value) + 1), len(value)
            self.w(obj, data)
        self.u.mem_write(data, value + b"\0")
        self.w(obj + 16, len(value))
        self.w(obj + 20, capacity)
        return obj

    def str_value(self, obj):
        data = obj if self.r(obj + 20) < 16 else self.r(obj)
        return bytes(self.u.mem_read(data, self.r(obj + 16))).decode("latin1")

    def iat(self, address, fn):
        stub = self.alloc(16)
        self.stub(stub, fn)
        self.w(address, stub)

    def alloc(self, size):
        address = self.heap
        self.heap += (size + 15) & ~15
        assert self.heap < 0x28000000
        return address

    def r(self, address):
        return struct.unpack("<I", self.u.mem_read(address, 4))[0]

    def w(self, address, value):
        self.u.mem_write(address, pack(value))

    def args(self, count):
        sp = self.u.reg_read(UC_X86_REG_ESP)
        return [self.r(sp + 4 + i * 4) for i in range(count)]

    def ret(self, cleanup, value=0):
        sp = self.u.reg_read(UC_X86_REG_ESP)
        target = self.r(sp)
        self.u.reg_write(UC_X86_REG_ESP, sp + 4 + cleanup)
        self.u.reg_write(UC_X86_REG_EAX, value)
        self.u.reg_write(UC_X86_REG_ECX, 0xCCCCCCCC)
        self.u.reg_write(UC_X86_REG_EDX, 0xDDDDDDDD)
        self.u.reg_write(UC_X86_REG_EIP, target)

    def invoke(self, address, obj, args=()):
        sp = 0x3000F000
        self.u.mem_write(sp, pack(self.stop) + b"".join(pack(a) for a in args))
        for reg, value in [
            (UC_X86_REG_EBX, 0xBBBBBBBB),
            (UC_X86_REG_ESI, 0xEEEEEEEE),
            (UC_X86_REG_EDI, 0xFFFFFFFF),
            (UC_X86_REG_EBP, 0xABABABAB),
        ]:
            self.u.reg_write(reg, value)
        self.u.reg_write(UC_X86_REG_ECX, obj)
        self.u.reg_write(UC_X86_REG_ESP, sp)
        self.u.emu_start(
            address, self.stop, count=getattr(self, "instruction_limit", 12000000)
        )
        assert self.u.reg_read(UC_X86_REG_EIP) == self.stop, "did not return"
        assert self.u.reg_read(UC_X86_REG_ESP) == sp + 4 + len(args) * 4, (
            "stack imbalance"
        )
        for reg, value in [
            (UC_X86_REG_EBX, 0xBBBBBBBB),
            (UC_X86_REG_ESI, 0xEEEEEEEE),
            (UC_X86_REG_EDI, 0xFFFFFFFF),
            (UC_X86_REG_EBP, 0xABABABAB),
        ]:
            assert self.u.reg_read(reg) == value, "callee-save register corrupted"

    def window(self, w=594, h=240, vt=0x1037F80, parent=0):
        obj = self.alloc(0x200)
        self.w(obj, vt)
        self.w(obj + 0x10, parent)
        self.w(obj + 0x30, 1)
        self.setsize(obj, w, h)
        return obj

    def setsize(self, obj, w, h):
        assert 0 < w <= 2048 and 0 < h <= 2048, (w, h)
        self.w(obj + 0x14, w)
        self.w(obj + 0x18, h)
        surf = self.alloc(0x40)
        pix = self.alloc(w * h * 4)
        self.w(surf + 4, w)
        self.w(surf + 8, h)
        self.w(surf + 0x18, pix)
        self.w(obj + 0x24, surf)


def native_crt(m):
    m.stub(0xDBBC4F, lambda: m.ret(0, m.alloc(m.args(1)[0])))
    m.stub(0xDBBEAE, lambda: m.ret(0, m.alloc(m.args(1)[0])))
    m.stub(0xDBBC7F, lambda: m.ret(0))

    def copy():
        dest, src, count = m.args(3)
        m.u.mem_write(dest, bytes(m.u.mem_read(src, count)))
        m.ret(0, dest)

    def clear():
        dest, value, count = m.args(3)
        m.u.mem_write(dest, bytes([value & 255]) * count)
        m.ret(0, dest)

    def find():
        hay, needle = m.args(2)
        where = m.cstr(hay).find(m.cstr(needle))
        m.ret(0, hay + where if where >= 0 else 0)

    m.iat(0xFC1740, copy)
    m.iat(0xFC1760, copy)
    m.iat(0xFC1744, clear)
    m.iat(0xFC1964, find)
    m.iat(0xFC1764, find)
    m.iat(0xFC1B30, lambda: m.ret(0, min(len(m.cstr(m.args(2)[0])), m.args(2)[1])))

    # Pure byte-search intrinsic used by MSVC std::string::find.
    def memchr():
        source, byte, count = m.args(3)
        at = bytes(m.u.mem_read(source, count)).find(bytes([byte & 255]))
        m.ret(0, source + at if at >= 0 else 0)

    if "memchr" in m.imports:
        m.iat(m.imports["memchr"], memchr)
    if "memcmp" in m.imports:

        def compare():
            left, right, count = m.args(3)
            l = bytes(m.u.mem_read(left, count))
            r = bytes(m.u.mem_read(right, count))
            m.ret(0, (l > r) - (l < r))

        m.iat(m.imports["memcmp"], compare)
