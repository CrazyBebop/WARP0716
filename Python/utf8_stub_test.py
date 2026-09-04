r"""Emulate the exact bytes emitted by utf8_stub_gen.py and check every path.

Runs the assembled stubs under unicorn against a reference model, including
the stack discipline of the stdcall frame (which is what makes the tail-jump
fallback safe) and guard-page checks that the stubs never read outside the
buffer they were handed.

    pip install unicorn keystone-engine
    python Python/utf8_stub_test.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from unicorn import *
from unicorn.x86_const import *
import utf8_stub_gen as gen

CODE  = 0x00100000
IATPG = 0x00200000          # fake IAT page
BUFPG = 0x00300000          # text buffer page (guarded on BOTH sides)
STACK = 0x00400000
LEGACY_NEXT = 0xDEAD0000    # tail-jump lands here -> "fell through to the API"
LEGACY_PREV = 0xDEAD0004
RETMARK     = 0xBEEF0000    # the caller we return to

SLOT_NEXT = IATPG + 0x00
SLOT_PREV = IATPG + 0x04

nxt  = gen.assemble(gen.NEXT)
prv  = gen.assemble(gen.PREV)
BLOB = bytearray(nxt + prv)
ENTRY_NEXT = 0
ENTRY_PREV = len(nxt)

# apply the fixups the .qjs would apply
import struct
for name, sent, slot in (('CharNextExA', gen.SENT_NEXT, SLOT_NEXT),
                         ('CharPrevExA', gen.SENT_PREV, SLOT_PREV)):
    off = BLOB.find(struct.pack('<I', sent))
    assert off >= 0 and BLOB.find(struct.pack('<I', sent), off + 1) < 0, name
    struct.pack_into('<I', BLOB, off, slot)


def run(entry, args, buf_bytes, buf_at_page_start):
    """Invoke one stub. Returns (legacy?, eax, esp_delta)."""
    uc = Uc(UC_ARCH_X86, UC_MODE_32)
    uc.mem_map(CODE, 0x1000)
    uc.mem_map(IATPG, 0x1000)
    uc.mem_map(BUFPG, 0x1000)          # neighbours deliberately UNMAPPED
    uc.mem_map(STACK, 0x4000)
    uc.mem_map(LEGACY_NEXT & ~0xFFF, 0x1000)   # fetch must succeed for the
    uc.mem_map(RETMARK & ~0xFFF, 0x1000)       # code hook to see the address
    uc.mem_write(LEGACY_NEXT & ~0xFFF, b'\xF4' * 0x10)
    uc.mem_write(RETMARK & ~0xFFF, b'\xF4' * 0x10)
    uc.mem_write(CODE, bytes(BLOB))
    uc.mem_write(SLOT_NEXT, struct.pack('<I', LEGACY_NEXT))
    uc.mem_write(SLOT_PREV, struct.pack('<I', LEGACY_PREV))

    if buf_at_page_start:
        base = BUFPG                              # guard page below
    else:
        base = BUFPG + 0x1000 - len(buf_bytes)    # guard page above
    uc.mem_write(base, buf_bytes)

    esp0 = STACK + 0x2000
    esp = esp0 - 4 * len(args)
    for i, a in enumerate(args):
        uc.mem_write(esp + 4 * i, struct.pack('<I', base + a if isinstance(a, Rel) else a))
    esp -= 4
    uc.mem_write(esp, struct.pack('<I', RETMARK))
    uc.reg_write(UC_X86_REG_ESP, esp)

    state = {}

    def hook(u, addr, size, _):
        if addr in (LEGACY_NEXT, LEGACY_PREV):
            state['legacy'] = True
            state['esp'] = u.reg_read(UC_X86_REG_ESP)
            u.emu_stop()
        elif addr == RETMARK:
            state['legacy'] = False
            state['eax'] = u.reg_read(UC_X86_REG_EAX)
            state['esp'] = u.reg_read(UC_X86_REG_ESP)
            u.emu_stop()

    uc.hook_add(UC_HOOK_CODE, hook)
    uc.emu_start(CODE + entry, 0, count=10000)
    if 'legacy' not in state:
        raise RuntimeError('never reached a terminator')
    return base, state


class Rel(int):
    """An argument expressed as an offset into the buffer."""


FAIL = []


def check(name, cond, detail=''):
    if cond:
        print(f'  ok   {name}')
    else:
        print(f'  FAIL {name}  {detail}')
        FAIL.append(name)


def t_next(name, cp, data, off, expect, at_start=True):
    """expect: an int step count, or 'legacy'."""
    args = [cp, Rel(off), 0]
    esp_in = 4 * len(args)
    try:
        base, st = run(ENTRY_NEXT, args, data, at_start)
    except UcError as e:
        check(name, False, f'memory fault: {e}')
        return
    if expect == 'legacy':
        ok = st['legacy'] and st['esp'] == STACK + 0x2000 - esp_in - 4
        check(name, ok, f'legacy={st["legacy"]} esp_off={st["esp"]-(STACK+0x2000)}')
    else:
        ok = (not st['legacy'] and st['eax'] == base + off + expect
              and st['esp'] == STACK + 0x2000)
        check(name, ok, f'legacy={st.get("legacy")} eax={st.get("eax",0)-base-off} '
                        f'want={expect} esp_off={st["esp"]-(STACK+0x2000)}')


def t_prev(name, cp, data, start, cur, expect, at_start=True):
    args = [cp, Rel(start), Rel(cur), 0]
    esp_in = 4 * len(args)
    try:
        base, st = run(ENTRY_PREV, args, data, at_start)
    except UcError as e:
        check(name, False, f'memory fault: {e}')
        return
    if expect == 'legacy':
        ok = st['legacy'] and st['esp'] == STACK + 0x2000 - esp_in - 4
        check(name, ok, f'legacy={st["legacy"]} esp_off={st["esp"]-(STACK+0x2000)}')
    else:
        ok = (not st['legacy'] and st['eax'] == base + expect
              and st['esp'] == STACK + 0x2000)
        check(name, ok, f'legacy={st.get("legacy")} eax={st.get("eax",0)-base} '
                        f'want={expect} esp_off={st["esp"]-(STACK+0x2000)}')


U = lambda s: s.encode('utf-8')

print('CharNextExA replacement')
t_next('ascii -> legacy',        0, b'A\0',                 0, 'legacy')
t_next('NUL -> legacy',          0, b'\0\0',                0, 'legacy')
t_next('2-byte U+00E9',          0, U('é') + b'\0',    0, 2)
t_next('3-byte U+20AC',          0, U('€') + b'\0',    0, 3)
t_next('4-byte U+1F600',         0, U('\U0001F600') + b'\0', 0, 4)
# --- grapheme clusters -------------------------------------------------------
# Line 2051 of msgstringtable.txt is U+1F6E1 followed by U+FE0F. Stepping only
# the shield left the selector standing as a "character" of its own, and the
# vertical tab strip put it on a line by itself where it has no glyph - the
# stray box. Absorbing extenders into the base is what removes it.
t_next('emoji + VS16 is one char',    0, U('\U0001F6E1️') + b'\0',            0, 7)
t_next('emoji + VS16 mid-cluster',    0, U('\U0001F6E1️') + b'\0',            4, 3)
t_next('emoji + skin tone',           0, U('\U0001F44D\U0001F3FD') + b'\0',        0, 8)
t_next('base + keycap',               0, U('⚽⃣') + b'\0',                0, 6)
t_next('ZWJ joins two emoji',         0, U('\U0001F468‍\U0001F469') + b'\0',  0, 11)
t_next('ZWJ chain of three',          0, U('\U0001F468‍\U0001F469‍\U0001F467') + b'\0', 0, 18)
t_next('VS16 then ZWJ then base',     0, U('❤️‍\U0001FA79') + b'\0', 0, 13)
# a joiner with nothing to join is handed back on its own, as before
t_next('dangling ZWJ not absorbed',   0, U('\U0001F600‍') + b'\0',            0, 4)
t_next('dangling ZWJ steps alone',    0, U('\U0001F600‍') + b'\0',            4, 3)
t_next('ZWJ + bad lead not absorbed', 0, U('\U0001F600‍') + b'\xF5\0',        0, 4)
t_next('ZWJ + bad trail not absorbed',0, U('\U0001F600‍') + b'\xC3\x41\0',    0, 4)
# same lead byte as an extender, but not one - must not be swallowed
t_next('EF that is not VS16',         0, U('\U0001F600�') + b'\0',            0, 4)
t_next('F0 that is not skin tone',    0, U('\U0001F600\U0001F600') + b'\0',        0, 4)
t_next('E2 that is not keycap/ZWJ',   0, U('\U0001F600⭐') + b'\0',            0, 4)
t_next('truncated VS16 at NUL',       0, U('\U0001F600') + b'\xEF\0',              0, 4)
t_next('truncated skin tone at NUL',  0, U('\U0001F600') + b'\xF0\x9F\0',          0, 4)
t_next('bad trail C3 41',        0, b'\xC3\x41\0',          0, 'legacy')
t_next('trail is NUL C3 00',     0, b'\xC3\x00\0',          0, 'legacy')
t_next('stray trail 0x80',       0, b'\x80\0',              0, 'legacy')
t_next('overlong lead 0xC1',     0, b'\xC1\x80\0',          0, 'legacy')
t_next('invalid lead 0xF5',      0, b'\xF5\x80\x80\x80\0',  0, 'legacy')
t_next('invalid lead 0xFF',      0, b'\xFF\0',              0, 'legacy')
t_next('cp 932 keeps legacy',  0x3A4, U('é') + b'\0',  0, 'legacy')
t_next('cp 936 keeps legacy',  0x3A8, U('é') + b'\0',  0, 'legacy')
t_next('cp 949 keeps legacy',  0x3B5, U('é') + b'\0',  0, 'legacy')
t_next('cp 950 keeps legacy',  0x3B6, U('é') + b'\0',  0, 'legacy')
t_next('cp 1361 keeps legacy', 0x551, U('é') + b'\0',  0, 'legacy')
t_next('cp 1252 decodes',      0x4E4, U('é') + b'\0',  0, 2)
t_next('cp 874 decodes',       0x36A, U('é') + b'\0',  0, 2)
# guard page ABOVE: truncated lead at the very last two bytes of the page
t_next('no read past NUL at page end', 0, b'\xC3\x00', 0, 'legacy', at_start=False)
# The absorb loop reads one byte past the character it stepped. On a
# NUL-terminated string that byte is the terminator, so nothing beyond it is
# ever touched and the guard page stays intact.
t_next('char then NUL at page end',    0, U('\U0001F600') + b'\0',          0, 4, at_start=False)
t_next('cluster then NUL at page end', 0, U('\U0001F6E1️') + b'\0',    0, 7, at_start=False)
t_next('truncated VS16 at page end',   0, U('\U0001F600') + b'\xEF\0',      0, 4, at_start=False)

print()
print('CharPrevExA replacement')
t_prev('ascii back one',         0, b'AB',                    0, 2, 1)
t_prev('2-byte back',            0, U('é'),              0, 2, 0)
t_prev('3-byte back',            0, U('€'),              0, 3, 0)
t_prev('4-byte back',            0, U('\U0001F600'),          0, 4, 0)
# --- grapheme clusters: land on the base, never inside the cluster -----------
t_prev('back over VS16 to base',    0, U('\U0001F6E1️'),                  0, 7,  0)
t_prev('back over skin tone',       0, U('\U0001F44D\U0001F3FD'),              0, 8,  0)
t_prev('back over keycap',          0, U('⚽⃣'),                      0, 6,  0)
t_prev('back over ZWJ pair',        0, U('\U0001F468‍\U0001F469'),        0, 11, 0)
t_prev('back over ZWJ chain',       0, U('\U0001F468‍\U0001F469‍\U0001F467'), 0, 18, 0)
t_prev('back over VS16 + ZWJ',      0, U('❤️‍\U0001FA79'),      0, 13, 0)
t_prev('cluster keeps prior char',  0, U('A\U0001F6E1️'),                 0, 8,  1)
t_prev('two emoji stay separate',   0, U('\U0001F600\U0001F600'),              0, 8,  4)
t_prev('EF that is not VS16',       0, U('\U0001F600�'),                  0, 7,  4)
t_prev('E2 that is not keycap',     0, U('\U0001F600⭐'),                  0, 7,  4)
t_prev('dangling ZWJ stands alone', 0, U('\U0001F600‍'),                  0, 7,  4)
t_prev('extender at start',         0, U('️'),                            0, 3,  0)
t_prev('malformed before extender', 0, b'\xFF' + U('️'),                  0, 4,  1)
t_prev('cur == start -> legacy', 0, b'AB',                    0, 0, 'legacy')
t_prev('cur < start -> legacy',  0, b'AB',                    1, 0, 'legacy')
t_prev('short seq -> legacy',    0, b'\xC3\xA9',              0, 1, 'legacy')
t_prev('5 trails -> legacy',     0, b'\x80' * 5,              0, 5, 'legacy')
t_prev('cp 932 keeps legacy', 0x3A4, U('é'),             0, 2, 'legacy')
t_prev('cp 950 keeps legacy', 0x3B6, U('é'),             0, 2, 'legacy')
# guard page BELOW: buffer starts on the page boundary, nothing mapped under it
t_prev('no read below start (trails)', 0, b'\x80\x80',        0, 2, 'legacy')
t_prev('no read below start (lead)',   0, b'\xC3\xA9',        0, 2, 0)

print()
if FAIL:
    print(f'{len(FAIL)} FAILURE(S): ' + ', '.join(FAIL))
    sys.exit(1)
print('all paths verified')
