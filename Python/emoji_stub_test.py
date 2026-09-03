"""Emulate CLAIMGROUP under Unicorn and check that a chatbox emoji blits exactly
once per frame, for any number of outline passes the client happens to make.

The old build counted passes and freed the slot on the fifth match, which only
lined up with a 5-pass outline renderer; every other pass count left the entry
live at frame end, so the next frame's first pass matched it and was suppressed
- that is the blinking the user reported. This drives the same matrix against
the timestamp build.
"""
import sys, os, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from unicorn import *
from unicorn.x86_const import *
import emoji_stub_gen as G

CODE = 0x00400000
DATA = 0x00500000
IAT  = 0x00600000
STACK = 0x00700000
FAKE = 0x00800000          # trampoline bodies for emulated imports
SCRATCH = 0x00900000       # caller-side buffers

QPF_HZ = 10_000_000        # 10 MHz, the usual Windows value
NAMES = [n for n, _ in G.IMPORTS]


def patch(blob, fixups):
    b = bytearray(blob)
    for off, kind, ref in fixups:
        val = (DATA + ref) if kind == "data" else (IAT + 4 * NAMES.index(ref))
        struct.pack_into("<I", b, off, val)
    return bytes(b)


_BUILD = None


class Harness:
    def __init__(self):
        global _BUILD
        if _BUILD is None:                # assembling is slow; do it once
            blob, labels, fixups = G.build()
            _BUILD = (patch(blob, fixups), labels)
        self.code, self.labels = _BUILD
        self.clock = 0            # virtual QPC ticks, advanced by the test
        self.fail_mode = None     # exercise the "no usable timer" bypass

        uc = Uc(UC_ARCH_X86, UC_MODE_32)
        self.uc = uc
        uc.mem_map(CODE, 0x10000)
        uc.mem_map(DATA, 0x10000)
        uc.mem_map(IAT, 0x1000)
        uc.mem_map(STACK, 0x10000)
        uc.mem_map(FAKE, 0x1000)
        uc.mem_map(SCRATCH, 0x1000)
        uc.mem_write(CODE, self.code)
        uc.mem_write(DATA, b"\x00" * G.DATA_SIZE)

        # every import points at its own 'ret'-style stub so we can dispatch by pc
        self.stub_of = {}
        for i, n in enumerate(NAMES):
            addr = FAKE + 0x10 * i
            self.stub_of[addr] = n
            uc.mem_write(IAT + 4 * i, struct.pack("<I", addr))
            uc.mem_write(addr, b"\xC3")      # placeholder; hook intercepts first

        uc.hook_add(UC_HOOK_CODE, self._on_code, begin=FAKE, end=FAKE + 0x1000)

    def _on_code(self, uc, addr, size, user):
        name = self.stub_of.get(addr)
        if name is None:
            return
        esp = uc.reg_read(UC_X86_REG_ESP)
        ret = struct.unpack("<I", uc.mem_read(esp, 4))[0]
        args = [struct.unpack("<I", uc.mem_read(esp + 4 + 4 * k, 4))[0]
                for k in range(4)]
        if name == "QueryPerformanceFrequency":
            if self.fail_mode == "qpf_fails":
                eax, pops = 0, 1
            else:
                freq = {"freq_too_high": 1 << 33, "freq_zero": 0}.get(
                    self.fail_mode, QPF_HZ)
                uc.mem_write(args[0], struct.pack("<Q", freq))
                eax, pops = 1, 1
        elif name == "QueryPerformanceCounter":
            uc.mem_write(args[0], struct.pack("<Q", self.clock))
            eax, pops = 1, 1
        else:
            raise AssertionError(f"CLAIMGROUP called unexpected import {name}")
        uc.reg_write(UC_X86_REG_EAX, eax)
        uc.reg_write(UC_X86_REG_ESP, esp + 4 + 4 * pops)   # stdcall callee-pop
        uc.reg_write(UC_X86_REG_EIP, ret)

    def claim(self, hdc, text, x, y):
        """Call CLAIMGROUP with a synthetic TextOutW frame. Returns eax (1=blit)."""
        uc = self.uc
        wtext = text.encode("utf-16-le")
        uc.mem_write(SCRATCH, wtext)
        cch = len(wtext) // 2            # UTF-16 units, so a pair counts as 2

        # CLAIMGROUP reads its inputs off the hook's frame: [ebp+0]=saved ebp,
        # [ebp+4]=return address, then [ebp+8]=hdc, [ebp+0C]=x, [ebp+10]=y,
        # [ebp+14]=lpString, [ebp+18]=cch
        ebp = STACK + 0x8000
        frame = struct.pack("<IIIIIII", 0xDEAD, 0xC0DE, hdc, x & 0xFFFFFFFF,
                            y & 0xFFFFFFFF, SCRATCH, cch)
        uc.mem_write(ebp, frame)

        esp = ebp - 0x400
        STOP = CODE + 0xF000
        uc.mem_write(esp, struct.pack("<I", STOP))   # return address
        uc.reg_write(UC_X86_REG_ESP, esp)
        uc.reg_write(UC_X86_REG_EBP, ebp)
        uc.reg_write(UC_X86_REG_ECX, 0x1234)        # must survive
        uc.emu_start(CODE + self.labels["CLAIMGROUP"], STOP, count=200000)
        assert uc.reg_read(UC_X86_REG_ECX) == 0x1234, "CLAIMGROUP clobbered ecx"
        assert uc.reg_read(UC_X86_REG_ESP) == esp + 4, "CLAIMGROUP unbalanced esp"
        return uc.reg_read(UC_X86_REG_EAX)

    def thresh(self):
        return struct.unpack("<i", self.uc.mem_read(DATA + G.D["QPCTHRESH"], 4))[0]


US = QPF_HZ // 1_000_000       # ticks per microsecond
MS = QPF_HZ // 1_000           # ticks per millisecond

# the offsets the client's outline renderer uses, in call order
PASS_OFFSETS = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]


def frame(h, hdc, text, x, y, npass, us_between=20):
    """One frame: npass draws of the same string, microseconds apart."""
    blits = 0
    for k in range(npass):
        dx, dy = PASS_OFFSETS[k % len(PASS_OFFSETS)]
        blits += h.claim(hdc, text, x + dx, y + dy)
        h.clock += us_between * US
    return blits


print("=== blink matrix: 10 frames, 16ms apart (60fps), per pass count ===")
ok = True
for npass in range(1, 9):
    h = Harness()
    seq = []
    for f in range(10):
        seq.append(frame(h, 0x1111, "\U0001F600", 100, 200, npass))
        h.clock += 16 * MS
    good = all(b == 1 for b in seq)
    ok &= good
    print(f"  {npass}-pass: {seq}  {'OK' if good else '*** BLINKS/DUPES ***'}")

print("\n=== slow frames (100ms apart) ===")
for npass in (1, 5):
    h = Harness()
    seq = []
    for f in range(6):
        seq.append(frame(h, 0x1111, "\U0001F600", 100, 200, npass))
        h.clock += 100 * MS
    good = all(b == 1 for b in seq)
    ok &= good
    print(f"  {npass}-pass: {seq}  {'OK' if good else '*** BAD ***'}")

print("\n=== distinct emoji must NOT be suppressed by each other ===")
h = Harness()
cases = [
    ("same string, 3px apart", 0x1111, "\U0001F600", 103, 200),
    ("same string, 41px apart", 0x1111, "\U0001F600", 141, 200),
    ("same string, other line", 0x1111, "\U0001F600", 100, 216),
    ("different DC", 0x2222, "\U0001F600", 100, 200),
    ("different string", 0x1111, "\U0001F601", 100, 200),
]
base = frame(h, 0x1111, "\U0001F600", 100, 200, 5)
print(f"  baseline group: {base} blit(s)  {'OK' if base == 1 else '*** BAD ***'}")
ok &= base == 1
for label, hdc, txt, x, y in cases:
    n = frame(h, hdc, txt, x, y, 5)
    good = n == 1
    ok &= good
    print(f"  {label:26s}: {n} blit(s)  {'OK' if good else '*** SUPPRESSED ***'}")

print("\n=== many distinct strings in one frame (table pressure) ===")
h = Harness()
n = 0
for k in range(12):
    n += frame(h, 0x1111, chr(0x1F600 + k), 100 + 40 * k, 200, 5)
print(f"  12 emoji in one frame -> {n} blits "
      f"{'OK' if n == 12 else '*** LOST ' + str(12 - n) + ' ***'}")
ok &= n == 12
# and the next frame must still draw all 12
n2 = 0
h.clock += 16 * MS
for k in range(12):
    n2 += frame(h, 0x1111, chr(0x1F600 + k), 100 + 40 * k, 200, 5)
print(f"  same 12 next frame  -> {n2} blits "
      f"{'OK' if n2 == 12 else '*** LOST ' + str(12 - n2) + ' ***'}")
ok &= n2 == 12

print("\n=== long group must not age out mid-draw (30 passes, 100us apart) ===")
h = Harness()
b = 0
for k in range(30):
    dx, dy = PASS_OFFSETS[k % 5]
    b += h.claim(0x1111, "\U0001F600", 100 + dx, 200 + dy)
    h.clock += 100 * US
print(f"  30 passes spanning 3ms -> {b} blit(s) {'OK' if b == 1 else '*** BAD ***'}")
ok &= b == 1

print("\n=== 32-bit QPC wrap: at worst one bad frame, self-correcting ===")
# Only the low dword is kept, so elapsed is modulo 2^32. Walk the wrap in fine
# steps and confirm no run of consecutive dark frames - a single one is the
# documented worst case, a run would be visible blinking.
worst_dark, worst_dupe = 0, 0
for step in range(60):
    h = Harness()
    h.claim(0x1111, "\U0001F600", 100, 200)          # resolve QPCTHRESH first
    h.clock = (1 << 32) - 20 * MS + step * (700 * US)
    seq = []
    for _ in range(8):                                # 8 frames at 60fps
        seq.append(frame(h, 0x1111, "\U0001F600", 100, 200, 5))
        h.clock += 16 * MS
    run = best = 0
    for b in seq:
        run = run + 1 if b == 0 else 0
        best = max(best, run)
    worst_dark = max(worst_dark, best)
    worst_dupe = max(worst_dupe, max(seq))
good = worst_dark <= 1 and worst_dupe <= 2
ok &= good
print(f"  60 offsets across the wrap: longest dark run {worst_dark} frame(s), "
      f"most blits in a frame {worst_dupe}  {'OK' if good else '*** BAD ***'}")

print("\n=== threshold ===")
h = Harness()
h.claim(0x1111, "\U0001F600", 100, 200)
t = h.thresh()
print(f"  QPCTHRESH = {t} ticks = {t / US:.0f} us "
      f"{'OK' if t == QPF_HZ // 500 else '*** BAD ***'}")
ok &= t == QPF_HZ // 500

print("\n=== no usable timer: bypass, never invisible ===")
for mode in ("qpf_fails", "freq_too_high", "freq_zero"):
    h = Harness()
    h.fail_mode = mode
    seq = [frame(h, 0x1111, "\U0001F600", 100, 200, 5) for _ in range(3)]
    t = h.thresh()
    # bypass means every pass blits: 5 passes -> 5 blits, and never 0
    good = t == -1 and all(b == 5 for b in seq)
    ok &= good
    print(f"  {mode:14s}: thresh={t} blits={seq} {'OK' if good else '*** BAD ***'}")

print("\n" + ("ALL CHECKS PASSED" if ok else "*** FAILURES ABOVE ***"))
sys.exit(0 if ok else 1)
