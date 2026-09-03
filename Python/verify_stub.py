"""Static checks over the generated emoji stub: stack discipline (CFG walk),
sentinel/fixup bijection, and data-offset range. Run from the repo root."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import capstone
from capstone import x86
import emoji_stub_gen as G

blob, labels, fixups = G.build()
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
md.detail = True
insns = list(md.disasm(bytes(blob), 0))
by_addr = {i.address: i for i in insns}
addr_of = sorted(by_addr)

print(f"code {len(blob)} bytes, {len(fixups)} fixups, {len(insns)} insns")

# stdcall callee-pop arg counts for the imports these routines call
STDCALL_ARGS = {
    "QueryPerformanceCounter": 1,
    "QueryPerformanceFrequency": 1,
}
IMP_BY_IDX = {i * 4: n for i, (n, _) in enumerate(G.IMPORTS)}

TERMINAL = {"ret", "retn", "retf"}
UNCOND = {"jmp"}


def succ(i, end):
    """Successors of instruction i, restricted to [.., end)."""
    m = i.mnemonic
    if m in TERMINAL:
        return []
    nxt = i.address + i.size
    out = []
    if m in UNCOND or m.startswith("j"):
        op = i.operands[0]
        if op.type == x86.X86_OP_IMM:
            t = op.imm
            if 0 <= t < end:
                out.append(t)
        if m not in UNCOND:
            out.append(nxt)
        return out
    return [nxt] if nxt < end else []


def delta(i):
    """Net esp change in dwords, or None if unmodelled."""
    m = i.mnemonic
    if m == "push":
        return +1
    if m == "pop":
        return -1
    if m in ("pushfd", "pushf"):
        return +1
    if m in ("popfd", "popf"):
        return -1
    if m in ("add", "sub") and i.operands[0].type == x86.X86_OP_REG and \
            i.reg_name(i.operands[0].reg) == "esp":
        if i.operands[1].type != x86.X86_OP_IMM:
            return None
        n = i.operands[1].imm // 4
        return -n if m == "add" else +n
    if m == "call":
        op = i.operands[0]
        if op.type == x86.X86_OP_IMM:
            return 0                      # internal helper, balanced
        if op.type == x86.X86_OP_MEM and op.mem.base == 0 and op.mem.index == 0:
            disp = op.mem.disp & 0xFFFFFFFF
            if (disp & 0xFF000000) == G.SENT_IAT:
                name = IMP_BY_IDX.get(disp & 0xFFFFFF)
                if name in STDCALL_ARGS:
                    return -STDCALL_ARGS[name]
                return None
        return None
    if m == "mov" and i.operands[0].type == x86.X86_OP_REG and \
            i.reg_name(i.operands[0].reg) == "esp":
        return None
    return 0


def cfg_stack_check(start, end):
    seen = {}
    todo = [(start, 0)]
    rets, bad, unknown = [], [], []
    while todo:
        a, d = todo.pop()
        if a in seen:
            if seen[a] != d:
                bad.append((hex(a), f"path depths {seen[a]} vs {d}"))
            continue
        seen[a] = d
        i = by_addr.get(a)
        if i is None:
            bad.append((hex(a), "not an instruction boundary"))
            continue
        if i.mnemonic in TERMINAL:
            rets.append((hex(a), d))
            if d != 0:
                bad.append((hex(a), f"ret at depth {d}"))
            continue
        dv = delta(i)
        if dv is None:
            unknown.append(f"{hex(a)} {i.mnemonic} {i.op_str}")
            dv = 0
        for s in succ(i, end):
            todo.append((s, d + dv))
    return rets, bad, unknown


ROUTINES = ["CLAIMGROUP", "INITTHRESH", "READNOW"]
LOCAL_PREFIX = ("CG_", "IT_", "RN_")
tops = sorted(a for n, a in labels.items() if not n.startswith(LOCAL_PREFIX))

print("\n-- stack discipline (CFG walk) --")
for r in ROUTINES:
    if r not in labels:
        print(f"  {r}: MISSING LABEL")
        continue
    start = labels[r]
    later = [a for a in tops if a > start]
    end = min(later) if later else len(blob)
    rets, bad, unknown = cfg_stack_check(start, end)
    print(f"  {r}: 0x{start:x}..0x{end:x} ({end - start} B) rets={rets}")
    print(f"      {'OK' if not bad else 'BAD ' + str(bad)}"
          f"{'' if not unknown else '  unmodelled: ' + str(unknown)}")

print("\n-- sentinel <-> fixup bijection --")
found = []
for i in insns:
    for op in i.operands:
        if op.type == x86.X86_OP_IMM:
            v = op.imm & 0xFFFFFFFF
            if (v & 0xFF000000) in (G.SENT_DATA, G.SENT_IAT):
                found.append((i.address, v))
        elif op.type == x86.X86_OP_MEM:
            disp = op.mem.disp & 0xFFFFFFFF
            if op.mem.base == 0 and op.mem.index == 0 and \
                    (disp & 0xFF000000) in (G.SENT_DATA, G.SENT_IAT):
                found.append((i.address, disp))

print(f"  operand-level sentinels: {len(found)}   fixups: {len(fixups)}")
sent_locs = {a for a, _ in found}
unmatched = []
for fa in sorted(f[0] for f in fixups):
    owner = next((i.address for i in insns
                  if i.address <= fa < i.address + i.size), None)
    if owner not in sent_locs:
        unmatched.append(hex(fa))
print(f"  fixups not inside a sentinel insn: {unmatched or 'none'}")

print("\n-- operand ranges --")
oor = []
for a, v in found:
    if (v & 0xFF000000) == G.SENT_DATA:
        off = v & 0xFFFFFF
        if not (0 <= off < G.DATA_SIZE):
            oor.append((hex(a), hex(off)))
    else:
        idx = (v & 0xFFFFFF) // 4
        if not (0 <= idx < len(G.IMPORTS)) or (v & 3):
            oor.append((hex(a), f"imp#{idx}"))
print(f"  out of range: {oor or 'none'} "
      f"(DATA_SIZE=0x{G.DATA_SIZE:x}, imports={len(G.IMPORTS)})")
