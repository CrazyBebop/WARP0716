"""Behavioural test of the CustomRuneSystem caves in a patched 2025-07-16 Ragexe.

Native engine functions (the Refresh lookup, Resize, the pane draw/hover, the
tag-list click, DrawBitmap/TextOut, child Move, Invalidate) are mocked; the
native leaf getters (set ID, category) and the unequip packet code run
unpatched. This checks the emitted code: the set cache, scrolling, the
preview/button/unequip getters, the 0x0bd6 fields, stacked rows and the mouse
row mapping. It does not replace an in-game test.

Usage: python tools/test_custom_rune_system.py [patched.exe]
Requires pefile and unicorn (.venv-target-hud).
"""
from __future__ import annotations
import struct
import sys
from collections import namedtuple

import pefile
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32, UC_HOOK_CODE
from unicorn.x86_const import (UC_X86_REG_EAX, UC_X86_REG_EBX, UC_X86_REG_ECX,
    UC_X86_REG_EDX, UC_X86_REG_ESI, UC_X86_REG_EDI, UC_X86_REG_EBP,
    UC_X86_REG_ESP, UC_X86_REG_EFLAGS)

MGR_PTR = 0x01318A10
ROW = 0x52
PANE_W = 0x11B
CAPACITY = 255
UNEQUIP_SET_FLAG = 0x8000
STATE = dict(count=0x00, first=0x04, interact=0x08, yoff=0x0C, pane=0x10, surface=0x14,
             depth=0x18, pane_self=0x1C, pane_w=0x20, pane_h=0x24, captured=0x28, hover_yoff=0x5C,
             slots=0x60)
# UIRuneSystemWnd +0xC8 tier bar, +0xCC set list, +0xD0/+0xD4 other tab pages
CHILD_Y = [0xA4, 0xC4, 0x76, 0x76]
LIST_H, LIST_PAGE, LIST_TOTAL = 0x159, 5, 8
INFO_VTABLE = 0x010239AC
STRIP = dict(up=0x01023FAC, down=0x01023FE0, top=0x01024014, mid=0x01024040, bottom=0x0102406C)

RuneSet = namedtuple('RuneSet', 'tag id ptr')


class VM:
    def __init__(self, path):
        pe = pefile.PE(path, fast_load=True)
        self.base = pe.OPTIONAL_HEADER.ImageBase
        image = pe.get_memory_mapped_image()
        self.u = Uc(UC_ARCH_X86, UC_MODE_32)
        self.u.mem_map(self.base, (len(image) + 0xFFF) & ~0xFFF)
        self.u.mem_write(self.base, image)
        self.u.mem_map(0x60000000, 0x200000)
        self.stop, self.stack, self.heap = 0x60000000, 0x60008000, 0x60010000
        self.stubs, self.lookup, self.log = {}, {}, {}
        self.locate()

        self.mgr = self.alloc(0x40)
        self.write32(MGR_PTR, self.mgr)
        self.stub(0x00730B40, 16, self.native_refresh)
        self.stub(0x00A1CB70, 8, self.resize)
        self.stub(0x007E1610, 0, self.pane_draw)
        self.stub(0x007E4CC0, 8, self.mouse('hover'))
        self.stub(0x007E4B70, 8, self.mouse('tag_click'))
        self.stub(0x00A1D260, 16, self.record('image'))
        self.stub(0x00A25A70, 16, self.record('text'))
        self.stub(0x00A1D460, 20, self.record('fill'))
        self.stub(0x00A90350, 0, lambda ecx, args: 0x6000F000)
        self.stub(0x00A9F030, 0, lambda ecx, args: args[0], nargs=1)  # cdecl: name -> path
        self.stub(0x00A8D4A0, 4, lambda ecx, args: args[0])  # path -> bitmap marker
        self.stub(0x007E4A50, 8, self.record('pane_click'))
        self.stub(0x007E4910, 8, self.record('pane_dblclick'))

        move, invalidate, overlay = self.alloc(16), self.alloc(16), self.alloc(16)
        self.stub(move, 8, self.child_move)
        self.stub(invalidate, 0, self.record('invalidate'))
        self.stub(overlay, 8, self.record('overlay'))
        child_vt, pane_vt, surface_vt = self.alloc(0xA0), self.alloc(0xA0), self.alloc(0x50)
        self.write32(child_vt + 0x10, move)
        self.write32(child_vt + 0x98, invalidate)
        self.write32(pane_vt + 0x98, invalidate)
        self.write32(surface_vt + 0x40, overlay)

        self.window = self.alloc(0x100)
        self.surface = self.alloc(0x10)
        self.write32(self.surface, surface_vt)
        self.pane = self.alloc(0x40)
        self.write32(self.pane, pane_vt)
        self.write32(self.pane + 0x10, self.window)
        self.write32(self.pane + 0x14, PANE_W)
        self.write32(self.pane + 0x18, ROW)
        self.write32(self.pane + 0x24, self.surface)
        self.write32(self.window + 0xC4, self.pane)
        self.children = []
        for i, y in enumerate(CHILD_Y):
            child = self.alloc(0xC0)
            self.write32(child, child_vt)
            self.write32(child + 0x14, PANE_W)
            self.write32(child + 0x1C, 0x10 + i)
            self.write32(child + 0x20, y)
            self.write32(self.window + 0xC8 + i * 4, child)
            self.children.append(child)
        self.list = self.children[1]
        self.write32(self.list + 0x18, LIST_H)
        self.write32(self.list + 0x80, LIST_TOTAL - LIST_PAGE)
        self.write32(self.list + 0x98, LIST_TOTAL)
        self.write32(self.list + 0x9C, LIST_PAGE)
        self.u.hook_add(UC_HOOK_CODE, self.step)

    # --- memory -----------------------------------------------------------
    def alloc(self, size):
        address = self.heap
        self.heap += (size + 15) & ~15
        return address

    def write32(self, address, value):
        self.u.mem_write(address, struct.pack('<I', value & 0xffffffff))

    def read32(self, address):
        return struct.unpack('<I', self.u.mem_read(address, 4))[0]

    def call_target(self, va):
        assert self.u.mem_read(va, 1)[0] == 0xE8, hex(va)
        return (va + 5 + struct.unpack('<i', self.u.mem_read(va + 1, 4))[0]) & 0xffffffff

    def locate(self):
        c = self.call_target
        self.cave = dict(
            refresh=c(0x00CF953F), preview=c(0x007E69D6), selected=c(0x007E5C12),
            unequip=c(0x007E67EA), unequip_id=c(0x007E685F), image=c(0x007E1673),
            text=c(0x007E17D5), overlay=c(0x007E1758), tooltip=c(0x007E4D17),
            draw=self.read32(0x0102317C), hover=self.read32(0x0102319C),
            wheel=self.read32(0x010231B8), tag_click=self.read32(0x01023268),
            click=self.read32(0x01023190), dblclick=self.read32(0x01023194))
        assert c(0x00CF9591) == self.cave['refresh']
        assert c(0x007E5E47) == c(0x007E5E56) == self.cave['selected']
        assert c(0x007E4E00) == self.cave['tooltip']
        assert self.u.mem_read(0x007E1757, 1) == b'\x56'
        assert self.u.mem_read(0x007E6864, 5) == b'\x90' * 5
        assert self.u.mem_read(0x007E6869, 7) == bytes.fromhex('66 89 85 7A FF FF FF')
        wheel = bytes(self.u.mem_read(self.cave['wheel'], 34))
        assert wheel[0:2] == b'\x8b\x15' and wheel[24] == 0xA1 and wheel[29] == 0x2D, wheel.hex()
        self.state = struct.unpack_from('<I', wheel, 2)[0] - STATE['first']
        assert struct.unpack_from('<I', wheel, 25)[0] == self.state + STATE['count']
        self.rows = struct.unpack_from('<I', wheel, 30)[0]
        assert 1 <= self.rows <= 5, self.rows

    def st(self, field, value=None):
        address = self.state + STATE[field]
        if value is None:
            return self.read32(address)
        self.write32(address, value)

    def cache(self):
        return [struct.unpack('<3I', self.u.mem_read(self.state + STATE['slots'] + i * 12, 12))
                for i in range(self.st('count'))]

    def ptrs(self):
        return [ptr for _, _, ptr in self.cache()]

    def equipped(self):
        return self.read32(self.mgr + 0x14)

    # --- mocks ------------------------------------------------------------
    def stub(self, address, pop, handler, nargs=None):
        self.stubs[address] = (pop, handler, pop // 4 if nargs is None else nargs)
        self.u.mem_write(address, b'\xc2' + struct.pack('<H', pop) if pop else b'\xc3')

    def step(self, uc, address, size, context):
        if address not in self.stubs:
            return
        pop, handler, nargs = self.stubs[address]
        esp, ecx = uc.reg_read(UC_X86_REG_ESP), uc.reg_read(UC_X86_REG_ECX)
        args = [self.read32(esp + 4 + i * 4) for i in range(nargs)]
        result = handler(ecx, args)
        uc.reg_write(UC_X86_REG_EAX, (result or 0) & 0xffffffff)
        # Native calls may destroy every volatile register.
        uc.reg_write(UC_X86_REG_ECX, 0xCAFE0001)
        uc.reg_write(UC_X86_REG_EDX, 0xCAFE0002)

    def record(self, name):
        def handler(ecx, args):
            self.log.setdefault(name, []).append((ecx, args))
            return 1
        return handler

    def native_refresh(self, ecx, args):
        tag, set_id = args[0], args[1]
        self.write32(ecx + 0x14, self.lookup.get((tag, set_id), 0) if set_id else 0)
        return 0x1234

    def resize(self, ecx, args):
        self.write32(ecx + 0x14, args[0])
        self.write32(ecx + 0x18, args[1])

    def pane_draw(self, ecx, args):
        self.log.setdefault('draw', []).append(
            (ecx, self.equipped(), self.st('yoff'), self.st('pane'), self.st('surface')))

    def mouse(self, name):
        def handler(ecx, args):
            self.log.setdefault(name, []).append((ecx, args[0], args[1], self.equipped(), self.st('hover_yoff')))
        return handler

    def child_move(self, ecx, args):
        self.write32(ecx + 0x1C, args[0])
        self.write32(ecx + 0x20, args[1])

    def take(self, name):
        return self.log.pop(name, [])

    # --- execution --------------------------------------------------------
    def run(self, entry, args=(), ecx=0, regs=None, pop=None):
        esp = self.stack
        self.u.mem_write(esp, struct.pack('<I', self.stop) +
                         b''.join(struct.pack('<I', a & 0xffffffff) for a in args))
        saved = {UC_X86_REG_EBX: 0xBEEFBEEF, UC_X86_REG_ESI: 0xABABABAB,
                 UC_X86_REG_EDI: 0xCDCDCDCD, UC_X86_REG_EBP: 0xEFEFEFEF}
        saved.update(regs or {})
        for reg, value in saved.items():
            self.u.reg_write(reg, value)
        self.u.reg_write(UC_X86_REG_ESP, esp)
        self.u.reg_write(UC_X86_REG_ECX, ecx)
        self.u.reg_write(UC_X86_REG_EFLAGS, 0x202)
        self.u.emu_start(entry, self.stop, count=2_000_000)
        assert self.u.reg_read(UC_X86_REG_ESP) == esp + 4 + (len(args) * 4 if pop is None else pop), hex(entry)
        for reg, value in saved.items():
            assert self.u.reg_read(reg) == value, f'{entry:#x}: nonvolatile register clobber'
        return self.u.reg_read(UC_X86_REG_EAX)

    def run_native(self, start, until, regs):
        self.u.reg_write(UC_X86_REG_ESP, self.stack)
        for reg, value in regs.items():
            self.u.reg_write(reg, value)
        self.u.emu_start(start, until, count=100_000)

    def make_set(self, tag, set_id):
        ptr = self.alloc(0x60)
        self.write32(ptr + 0x10, set_id)
        self.write32(ptr + 0x14, 0)
        self.write32(ptr + 0x48, tag)
        self.lookup[(tag, set_id)] = ptr
        return RuneSet(tag, set_id, ptr)

    def refresh(self, tag, set_id):
        return self.run(self.cave['refresh'], [tag, set_id, 0xFFFFFFFF, 0xFFFFFFFF], ecx=self.mgr)

    def sync(self, sets):
        """The map-server's multi-set full sync (doc/rune_tablet.txt 6.)."""
        for tag in range(1, 5):
            self.refresh(tag, 0)
        for s in sets:
            self.refresh(s.tag, s.id)

    def wheel(self, delta):
        return self.run(self.cave['wheel'], [delta], ecx=self.pane)


def test_cache(vm, sets):
    a, b, c, d = sets[0], sets[1], sets[2], sets[4]   # tags 1, 1, 2, 3
    assert vm.refresh(1, 0) == 0x1234, 'Refresh result must pass through'
    vm.sync([a, b, c, d])
    assert vm.ptrs() == [a.ptr, b.ptr, c.ptr, d.ptr]
    assert vm.cache()[1] == (b.tag, b.id, b.ptr)
    vm.refresh(b.tag, b.id)
    assert vm.ptrs() == [a.ptr, b.ptr, c.ptr, d.ptr], 'a cached set is updated, not appended'
    vm.refresh(4, 999)
    assert vm.ptrs() == [a.ptr, b.ptr, c.ptr, d.ptr], 'a set unknown to the client is ignored'
    vm.st('interact', b.ptr)
    vm.refresh(a.tag, 0)
    assert vm.ptrs() == [c.ptr, d.ptr], 'set 0 drops every set of the tag and compacts'
    assert vm.st('interact') == 0, 'a dropped hovered set is forgotten'
    vm.st('interact', d.ptr)
    vm.refresh(c.tag, 0)
    assert vm.ptrs() == [d.ptr] and vm.st('interact') == d.ptr
    vm.sync([])
    assert vm.ptrs() == [] and vm.st('interact') == 0


def test_capacity(vm, sets):
    many = [vm.make_set(1 + i % 4, 1300000 + i) for i in range(CAPACITY + 1)]
    for s in many:
        vm.refresh(s.tag, s.id)
    assert vm.st('count') == CAPACITY
    assert vm.ptrs() == [s.ptr for s in many[:CAPACITY]], 'a full cache drops new sets'
    vm.st('first', CAPACITY)
    vm.refresh(2, 0)
    assert vm.ptrs() == [s.ptr for s in many[:CAPACITY] if s.tag != 2], 'compaction keeps the order'
    assert vm.st('first') == max(0, vm.st('count') - vm.rows), 'removal clamps the scroll position'
    vm.sync([])
    assert vm.st('count') == 0 and vm.st('first') == 0


def test_wheel(vm, sets):
    shown = sets[:vm.rows + 1]
    vm.sync(shown)
    vm.st('first', 0)
    vm.st('interact', shown[0].ptr)
    vm.take('invalidate')
    vm.wheel(-120)
    assert vm.st('first') == 1 and vm.st('interact') == 0
    assert vm.take('invalidate') == [(vm.pane, [])]
    vm.wheel(-120)
    assert vm.st('first') == 1 and not vm.take('invalidate'), 'scrolling stops at the last row'
    vm.wheel(120)
    assert vm.st('first') == 0 and len(vm.take('invalidate')) == 1
    vm.wheel(120)
    assert vm.st('first') == 0 and not vm.take('invalidate'), 'scrolling stops at the first row'
    vm.sync(sets[:vm.rows])
    vm.wheel(-120)
    assert vm.st('first') == 0, 'no scrolling while every set is visible'
    vm.sync(shown)
    vm.wheel(-120)
    assert vm.st('first') == 1
    vm.refresh(shown[-1].tag, 0)
    assert vm.st('first') == max(0, vm.st('count') - vm.rows)


def expected_layout(extra):
    """Tier bar and set list move down by extra; the list shrinks and its page scales."""
    height = max(LIST_H - extra, 0x44)
    page = max(1, LIST_PAGE * height // LIST_H)
    ys = [CHILD_Y[0] + extra, CHILD_Y[1] + extra, CHILD_Y[2], CHILD_Y[3]]
    return ys, (height, page, max(LIST_TOTAL - page, 0))


def layout(vm):
    ys = [vm.read32(ch + 0x20) for ch in vm.children]
    return ys, (vm.read32(vm.list + 0x18), vm.read32(vm.list + 0x9C), vm.read32(vm.list + 0x80))


def test_draw(vm, sets):
    shown = sets[:vm.rows + 1]
    vm.sync(shown)
    vm.st('first', 1)
    stock = vm.equipped()
    vm.take('draw')
    vm.run(vm.cave['draw'], ecx=vm.pane)
    draws = vm.take('draw')
    assert [d[1] for d in draws] == [s.ptr for s in shown[1:1 + vm.rows]]
    assert [d[2] for d in draws] == [i * ROW for i in range(vm.rows)]
    assert all(d[0] == vm.pane and d[3] == vm.pane and d[4] == vm.surface for d in draws)
    assert vm.equipped() == stock, 'the stock equipped set is restored'
    assert (vm.read32(vm.pane + 0x14), vm.read32(vm.pane + 0x18)) == (PANE_W, vm.rows * ROW)
    assert layout(vm) == expected_layout((vm.rows - 1) * ROW), layout(vm)
    assert [vm.read32(ch + 0x1C) for ch in vm.children] == [0x10 + i for i in range(4)]
    assert vm.read32(vm.list + 0x14) == PANE_W
    assert (vm.st('yoff'), vm.st('pane'), vm.st('surface'), vm.st('depth')) == (0, 0, 0, 0)
    assert (vm.st('pane_self'), vm.st('pane_w'), vm.st('pane_h')) == (vm.pane, PANE_W, ROW)

    vm.sync(shown[:2])
    vm.run(vm.cave['draw'], ecx=vm.pane)
    rows = min(2, vm.rows)
    assert [d[1] for d in vm.take('draw')] == [s.ptr for s in shown[:rows]]
    assert vm.read32(vm.pane + 0x18) == rows * ROW
    assert layout(vm) == expected_layout((rows - 1) * ROW), layout(vm)

    vm.st('depth', 1)
    vm.run(vm.cave['draw'], ecx=vm.pane)
    assert [d[2] for d in vm.take('draw')] == [0], 're-entered draw is the stock draw'
    vm.st('depth', 0)

    vm.sync([])
    vm.run(vm.cave['draw'], ecx=vm.pane)
    assert len(vm.take('draw')) == 1
    assert (vm.read32(vm.pane + 0x14), vm.read32(vm.pane + 0x18)) == (PANE_W, ROW)
    assert layout(vm) == expected_layout(0), 'empty: stock layout, height and page'


def test_mouse(vm, sets):
    shown = sets[:vm.rows + 1]
    vm.sync(shown)
    vm.st('first', 1)
    stock = vm.equipped()
    for row in range(vm.rows):
        vm.st('interact', 0)
        vm.run(vm.cave['hover'], [10, row * ROW + 7], ecx=vm.pane)
        assert vm.take('hover') == [(vm.pane, 10, 7, shown[1 + row].ptr, row * ROW)], row
        assert vm.st('interact') == shown[1 + row].ptr and vm.equipped() == stock
        assert vm.st('hover_yoff') == 0, 'the tooltip offset only lives during the stock hover'
    vm.run(vm.cave['hover'], [10, vm.rows * ROW + 30], ecx=vm.pane)
    assert vm.take('hover') == [(vm.pane, 10, ROW + 30, shown[vm.rows].ptr, (vm.rows - 1) * ROW)], 'below: last row'

    other = vm.alloc(0x40)
    vm.st('interact', shown[0].ptr)
    vm.run(vm.cave['tag_click'], [3, 200], ecx=other)
    assert vm.take('tag_click') == [(other, 3, 200, shown[0].ptr, 0)]
    vm.st('interact', sets[-1].ptr)
    vm.run(vm.cave['tag_click'], [3, 200], ecx=other)
    assert vm.take('tag_click') == [(other, 3, 200, stock, 0)], 'an uncached set is never exposed'
    assert vm.equipped() == stock


def test_getters(vm, sets):
    shown = sets[:4]
    vm.sync(shown)
    stock = vm.equipped()
    stale = sets[-1].ptr
    vm.st('interact', shown[2].ptr)
    assert vm.run(vm.cave['preview'], ecx=vm.mgr) == shown[2].ptr
    vm.st('interact', stale)
    assert vm.run(vm.cave['preview'], ecx=vm.mgr) == stock
    vm.st('interact', 0)
    assert vm.run(vm.cave['preview'], ecx=vm.mgr) == stock

    info = vm.alloc(0x100)
    vm.write32(info, INFO_VTABLE)
    selected = lambda ptr: (vm.write32(info + 0x7C, ptr),
                            vm.run(vm.cave['selected'], ecx=vm.mgr, regs={UC_X86_REG_ESI: info}))[1]
    assert selected(shown[1].ptr) == shown[1].ptr, 'equipped shown set: Unequip'
    assert selected(stale) == 0, 'unequipped shown set: Equip'
    assert vm.run(vm.cave['selected'], ecx=vm.mgr, regs={UC_X86_REG_ESI: 0}) == 0

    frame = vm.alloc(0x200) + 0x100
    foreign = vm.alloc(0x100)
    vm.write32(foreign, 0x01020304)
    vm.write32(foreign + 0x7C, shown[1].ptr)

    def unequip(sender):
        vm.write32(frame + 8, sender)
        return vm.run(vm.cave['unequip'], ecx=vm.mgr,
                      regs={UC_X86_REG_EBP: frame, UC_X86_REG_EDI: vm.window})

    assert vm.st('pane_self') == vm.pane
    vm.st('interact', shown[2].ptr)
    vm.write32(info + 0x7C, shown[1].ptr)
    vm.write32(vm.window + 0x7C, 0)
    assert unequip(vm.pane) == shown[2].ptr, 'pane: the hovered row'
    assert unequip(info) == shown[1].ptr, 'Unequip button: the detail panel set'
    assert unequip(foreign) == 0, 'only UIRuneSet_Info senders are trusted'
    vm.write32(info + 0x7C, stale)
    assert unequip(info) == 0
    vm.st('interact', 0)
    assert unequip(vm.pane) == 0
    assert unequip(0) == 0
    vm.sync(shown[:1])
    assert unequip(vm.pane) == shown[0].ptr, 'one cached set: that set'
    assert unequip(info) == shown[0].ptr
    assert unequip(foreign) == shown[0].ptr
    vm.sync([])
    assert unequip(vm.pane) == 0


def test_unequip_packet(vm, sets):
    s = sets[2]
    frame = vm.alloc(0x200) + 0x100
    vm.run_native(0x007E684C, 0x007E6870, {UC_X86_REG_ESI: s.ptr, UC_X86_REG_EBP: frame})
    opcode, category, set_id = struct.unpack('<HHI', vm.u.mem_read(frame - 0x88, 8))
    assert (opcode, category, set_id) == (0x0BD6, s.tag | UNEQUIP_SET_FLAG, s.id), \
        (hex(opcode), hex(category), set_id)
    assert vm.u.reg_read(UC_X86_REG_ESI) == s.ptr


def test_row_shift(vm, sets):
    for name in ('image', 'text', 'overlay'):
        vm.take(name)
    vm.st('pane', vm.pane)
    vm.st('surface', vm.surface)
    vm.st('yoff', 2 * ROW)
    other = vm.alloc(0x40)
    for name in ('image', 'text'):
        vm.run(vm.cave[name], [5, 7, 0x1111, 0], ecx=vm.pane)
        vm.run(vm.cave[name], [5, 7, 0x1111, 0], ecx=other)
        assert vm.take(name) == [(vm.pane, [5, 7 + 2 * ROW, 0x1111, 0]), (other, [5, 7, 0x1111, 0])], name
    vm.run(vm.cave['overlay'], [0x2222, 9], ecx=vm.surface)
    assert vm.take('overlay') == [(vm.surface, [0x2222, 9 + 2 * ROW])]
    for field in ('pane', 'surface', 'yoff'):
        vm.st(field, 0)
    vm.run(vm.cave['overlay'], [0x2222, 9], ecx=vm.surface)
    assert vm.take('overlay') == [(vm.surface, [0x2222, 9])]


def test_tooltip(vm, sets):
    """Tooltip positions: the native LocalToScreen plus the hovered row offset."""
    vm.write32(vm.pane + 0x1C, 0x11B)
    vm.write32(vm.pane + 0x20, 0x52)
    vm.write32(vm.window + 0x1C, 100)
    vm.write32(vm.window + 0x20, 50)
    point = vm.alloc(8)
    other = vm.alloc(0x40)

    def place(ecx, x, y):
        vm.write32(point, x)
        vm.write32(point + 4, y)
        vm.run(vm.cave['tooltip'], [point, point + 4], ecx=ecx)
        return [struct.unpack('<i', vm.u.mem_read(point + i, 4))[0] for i in (0, 4)]

    assert vm.st('pane_self') == vm.pane
    vm.st('hover_yoff', 2 * ROW)
    assert place(vm.pane, 6, -15) == [6 + 0x11B + 100, -15 + 0x52 + 50 + 2 * ROW], 'hovered row'
    assert place(other, 6, -15) == [6, -15], 'other windows are untouched'
    vm.st('hover_yoff', 0)
    assert place(vm.pane, 6, -15) == [6 + 0x11B + 100, -15 + 0x52 + 50], 'first row'


def test_indicator(vm, sets):
    """Scroll column: only with hidden sets, geometry of the stock list scrollbar."""
    x = PANE_W - 7
    vm.sync(sets[:vm.rows])
    vm.st('first', 0)
    for name in ('fill', 'image', 'draw'):
        vm.take(name)
    vm.run(vm.cave['draw'], ecx=vm.pane)
    assert not vm.take('fill') and not vm.take('image'), 'every set fits: no column'

    count = vm.rows + 2
    vm.sync(sets[:count])
    h = vm.rows * ROW
    track = h - 14
    length = max(9, track * vm.rows // count)
    tops = []
    for first in range(count - vm.rows + 1):
        vm.st('first', first)
        vm.take('draw')
        vm.run(vm.cave['draw'], ecx=vm.pane)
        assert vm.take('fill') == [(vm.pane, [x, 0, 7, h, 0xDCC4B1]), (vm.pane, [x + 1, 1, 5, h - 2, 0xFFFFFF])]
        top = 7 + max(track - length, 0) * first // (count - vm.rows)
        bottom = top + length - 3
        expected = ([(x, 1, STRIP['up'], 1), (x, h - 7, STRIP['down'], 1), (x, top, STRIP['top'], 1)]
                    + [(x, y, STRIP['mid'], 1) for y in range(top + 3, bottom, 3)]
                    + [(x, bottom, STRIP['bottom'], 1)])
        images = [tuple(args) for ecx, args in vm.take('image') if ecx == vm.pane]
        assert images == expected, (first, images)
        assert 7 <= top and bottom + 3 <= h - 7, 'the thumb stays between the arrows'
        tops.append(top)
    assert tops == sorted(tops) and tops[0] == 7 and tops[-1] > tops[0], tops


def test_strip_click(vm, sets):
    """Clicks on the column scroll; elsewhere they preview/unequip as stock."""
    count = vm.rows + 2
    vm.sync(sets[:count])
    vm.run(vm.cave['draw'], ecx=vm.pane)
    h, x = vm.rows * ROW, PANE_W - 7
    for cave, stock in (('click', 'pane_click'), ('dblclick', 'pane_dblclick')):
        vm.st('first', 1)
        vm.take(stock)
        vm.run(vm.cave[cave], [x + 2, 3], ecx=vm.pane)
        assert vm.st('first') == 0, cave + ': upper half scrolls up'
        vm.run(vm.cave[cave], [x + 2, h - 3], ecx=vm.pane)
        assert vm.st('first') == 1, cave + ': lower half scrolls down'
        vm.run(vm.cave[cave], [x - 1, 3], ecx=vm.pane)
        assert vm.st('first') == 1 and vm.take(stock) == [(vm.pane, [x - 1, 3])], cave + ': rows stay stock'
    vm.sync(sets[:vm.rows])
    vm.run(vm.cave['draw'], ecx=vm.pane)
    vm.run(vm.cave['click'], [x + 2, 3], ecx=vm.pane)
    assert vm.take('pane_click') == [(vm.pane, [x + 2, 3])], 'no column when every set fits'


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else 'Outputs/custom_rune_system_test.exe'
    vm = VM(path)
    sets = [vm.make_set(1 + i // 2, 1260068 + i) for i in range(8)]
    sets.append(vm.make_set(4, 1260099))         # never synced: a stale pointer
    tests = [test_cache, test_capacity, test_wheel, test_draw, test_mouse,
             test_getters, test_unequip_packet, test_row_shift, test_tooltip,
             test_indicator, test_strip_click]
    for test in tests:
        test(vm, sets)
        print('ok', test.__name__)
    print(f'CustomRuneSystem: {len(tests)} tests passed (visible rows {vm.rows}, state {vm.state:#x})')


if __name__ == '__main__':
    main()
