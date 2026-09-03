#!/usr/bin/env python
r"""Generate the character-stepping machine code embedded in
Scripts/Patches/AllowUTF8Enconding.qjs.

The client steps through text one "character" at a time with USER32's
CharNextExA / CharPrevExA - ANSI/DBCS APIs that know nothing about UTF-8.
Under a single-byte codepage they advance exactly one byte, so every layout
routine (word wrap, line splitting, vertical tab labels, caret movement)
chops a multi-byte UTF-8 sequence into individual bytes.

This emits two drop-in replacements with the identical stdcall signatures.
They handle well-formed UTF-8 themselves and tail-jump to the genuine import
for everything else, so any input that is not valid UTF-8 keeps its original
behaviour byte for byte.

A "character" here is the whole grapheme cluster, not one codepoint. A base
codepoint followed by a zero-width extender - VARIATION SELECTOR
(U+FE00..FE0F), an emoji skin-tone modifier (U+1F3FB..1F3FF), COMBINING
ENCLOSING KEYCAP (U+20E3), or a ZERO WIDTH JOINER (U+200D) plus whatever it
joins to - steps as a single unit. Stepping only the base would strand the
extender as a "character" of its own, and every layout routine that splits per
character then hands it to the renderer alone: the vertical tab strip in the
inventory puts it on its own line, where it has no glyph and draws as a box.

Absorbing costs ONE byte of lookahead past the character being stepped. That
byte is either more text or the NUL terminator - exactly what the caller's own
next iteration reads - so the window still stops at the terminator.

    pip install keystone-engine capstone
    python utf8_stub_gen.py          # assemble + print the constants for the .qjs
    python utf8_stub_gen.py --dis    # same, plus a full annotated disassembly

NOTE: keystone parses bare integer literals as HEX, so `cmp eax, 10` means 16.
Every constant below is written as 0x.. and check_literals() refuses to
assemble anything ambiguous.
"""
import argparse
import re
import struct
import sys

from keystone import Ks, KS_ARCH_X86, KS_MODE_32

# Sentinel dwords patched to real addresses by the .qjs Fixups pass.
SENT_NEXT = 0xE1000000          # &USER32.CharNextExA
SENT_PREV = 0xE1000004          # &USER32.CharPrevExA

# Codepages whose two-byte sequences overlap the UTF-8 lead-byte ranges.
# Text in these is genuinely DBCS, so the legacy stepping must be kept.
DBCS = [
    (0x3A4, '932  Shift-JIS'),
    (0x3A8, '936  GBK'),
    (0x3B5, '949  Unified Hangul'),
    (0x3B6, '950  Big5'),
    (0x551, '1361 Johab'),
]


def dbcs_guard(label):
    """cp is in eax; bail to `label` for every DBCS codepage."""
    out = []
    for cp, name in DBCS:
        out.append(f'    cmp     eax, {cp:#x}          ; {name}')
        out.append(f'    je      {label}')
    return out


NEXT = [
    '; LPSTR __stdcall CharNextExA(WORD cp, LPCSTR p, DWORD flags)',
    '; [esp+4] cp   [esp+8] p   [esp+0xC] flags',
    'utf8_next:',
    '    mov     eax, [esp + 0x4]',
] + dbcs_guard('next_legacy') + [
    '    mov     ecx, [esp + 0x8]',
    '    movzx   eax, byte ptr [ecx]',
    '    cmp     eax, 0xC2',
    '    jb      next_legacy',       # 00-C1 NUL / ASCII / stray trail / overlong
    '    cmp     eax, 0xF5',
    '    jae     next_legacy',       # F5-FF never a valid lead
    '    mov     edx, 0x2',
    '    cmp     eax, 0xE0',
    '    jb      next_have',
    '    inc     edx',               # 3
    '    cmp     eax, 0xF0',
    '    jb      next_have',
    '    inc     edx',               # 4
    'next_have:',
    '    mov     eax, 0x1',
    'next_check:',
    '    cmp     eax, edx',
    '    jae     next_done',
    '    cmp     byte ptr [ecx + eax], 0x80',
    '    jb      next_legacy',
    '    cmp     byte ptr [ecx + eax], 0xBF',
    '    ja      next_legacy',
    '    inc     eax',
    '    jmp     next_check',

    # The base sequence is well formed, so from here on the answer can only
    # move further forward. The absorb loop below therefore bails to next_ret,
    # never to next_legacy - handing a half-stepped pointer to the genuine API
    # would make it step again from the wrong place.
    'next_done:',
    '    add     ecx, edx',

    # Absorb every zero-width extender that follows so a cluster steps as one
    # character. Each read is gated by the previous byte being non-NUL, which
    # is what keeps the window inside the string.
    'next_abs:',
    '    movzx   eax, byte ptr [ecx]',
    '    cmp     eax, 0xEF',         # U+FE00..FE0F   EF B8 80..8F
    '    je      next_vs',
    '    cmp     eax, 0xF0',         # U+1F3FB..1F3FF F0 9F 8F BB..BF
    '    je      next_skin',
    '    cmp     eax, 0xE2',         # U+20E3 E2 83 A3 / U+200D E2 80 8D
    '    je      next_e2',
    'next_ret:',
    '    mov     eax, ecx',
    '    ret     0xC',

    'next_vs:',
    '    cmp     byte ptr [ecx + 0x1], 0xB8',
    '    jne     next_ret',
    '    movzx   eax, byte ptr [ecx + 0x2]',
    '    cmp     eax, 0x80',
    '    jb      next_ret',
    '    cmp     eax, 0x8F',
    '    ja      next_ret',
    '    add     ecx, 0x3',
    '    jmp     next_abs',

    'next_skin:',
    '    cmp     byte ptr [ecx + 0x1], 0x9F',
    '    jne     next_ret',
    '    cmp     byte ptr [ecx + 0x2], 0x8F',
    '    jne     next_ret',
    '    movzx   eax, byte ptr [ecx + 0x3]',
    '    cmp     eax, 0xBB',
    '    jb      next_ret',
    '    cmp     eax, 0xBF',
    '    ja      next_ret',
    '    add     ecx, 0x4',
    '    jmp     next_abs',

    'next_e2:',
    '    movzx   eax, byte ptr [ecx + 0x1]',
    '    cmp     eax, 0x83',         # COMBINING ENCLOSING KEYCAP
    '    je      next_kc',
    '    cmp     eax, 0x80',         # ZERO WIDTH JOINER
    '    jne     next_ret',
    '    cmp     byte ptr [ecx + 0x2], 0x8D',
    '    jne     next_ret',
    # A joiner belongs to the cluster only when a real sequence follows it.
    # Step over it provisionally and validate what comes next; next_undo hands
    # a dangling joiner back as a character of its own, which is what the
    # unpatched API did with it.
    '    add     ecx, 0x3',
    '    movzx   eax, byte ptr [ecx]',
    '    cmp     eax, 0xC2',
    '    jb      next_undo',
    '    cmp     eax, 0xF5',
    '    jae     next_undo',
    '    mov     edx, 0x2',
    '    cmp     eax, 0xE0',
    '    jb      next_jhave',
    '    inc     edx',
    '    cmp     eax, 0xF0',
    '    jb      next_jhave',
    '    inc     edx',
    'next_jhave:',
    '    mov     eax, 0x1',
    'next_jcheck:',
    '    cmp     eax, edx',
    '    jae     next_jok',
    '    cmp     byte ptr [ecx + eax], 0x80',
    '    jb      next_undo',
    '    cmp     byte ptr [ecx + eax], 0xBF',
    '    ja      next_undo',
    '    inc     eax',
    '    jmp     next_jcheck',
    'next_jok:',
    '    add     ecx, edx',
    '    jmp     next_abs',
    'next_undo:',
    '    sub     ecx, 0x3',
    '    jmp     next_ret',

    'next_kc:',
    '    cmp     byte ptr [ecx + 0x2], 0xA3',
    '    jne     next_ret',
    '    add     ecx, 0x3',
    '    jmp     next_abs',

    'next_legacy:',
    f'    jmp     dword ptr [{SENT_NEXT:#x}]',
]

PREV = [
    '; LPSTR __stdcall CharPrevExA(WORD cp, LPCSTR start, LPCSTR cur, DWORD flags)',
    '; [esp+4] cp   [esp+8] start   [esp+0xC] cur   [esp+0x10] flags',
    'utf8_prev:',
    '    mov     eax, [esp + 0x4]',
] + dbcs_guard('prev_legacy') + [
    '    mov     ecx, [esp + 0x8]',          # start
    '    mov     eax, [esp + 0xC]',          # cur
    '    cmp     eax, ecx',
    '    jbe     prev_legacy',               # already at/behind the start
    '    call    prev_seq',
    '    jc      prev_legacy',

    # eax stands on a well-formed sequence. Keep walking back while that
    # sequence is a zero-width extender, or while a joiner sits in front of it,
    # so the caret lands on the base of the whole cluster instead of inside it.
    # Everything read here is within [start, cur) and eax only ever decreases,
    # so the loop terminates at the start in the worst case.
    'prev_abs:',
    '    movzx   edx, byte ptr [eax]',
    '    cmp     edx, 0xEF',
    '    je      prev_vs',
    '    cmp     edx, 0xF0',
    '    je      prev_skin',
    '    cmp     edx, 0xE2',
    '    je      prev_kc',

    # Not an extender itself - but a joiner immediately in front of it makes it
    # the tail of a joined cluster. 0xE2 is a lead byte, so finding one exactly
    # three bytes back is unambiguous: UTF-8 is self-synchronising, and a lead
    # byte can never appear inside another sequence.
    'prev_join:',
    '    mov     edx, eax',
    '    sub     edx, ecx',                  # how much room is left behind us
    '    cmp     edx, 0x3',
    '    jb      prev_done',                 # (subtracting from eax could wrap)
    '    mov     edx, eax',
    '    sub     edx, 0x3',
    '    cmp     byte ptr [edx], 0xE2',
    '    jne     prev_done',
    '    cmp     byte ptr [edx + 0x1], 0x80',
    '    jne     prev_done',
    '    cmp     byte ptr [edx + 0x2], 0x8D',
    '    jne     prev_done',
    '    mov     eax, edx',                  # stand on the joiner ...

    'prev_step:',                            # ... and take one more step back
    '    cmp     eax, ecx',
    '    jbe     prev_done',
    '    push    eax',
    '    call    prev_seq',
    '    jnc     prev_more',
    '    pop     eax',                       # malformed further back - stop
    '    jmp     prev_done',
    'prev_more:',
    '    add     esp, 0x4',
    '    jmp     prev_abs',

    'prev_done:',
    '    ret     0x10',

    'prev_vs:',
    '    cmp     byte ptr [eax + 0x1], 0xB8',
    '    jne     prev_join',
    '    movzx   edx, byte ptr [eax + 0x2]',
    '    cmp     edx, 0x80',
    '    jb      prev_join',
    '    cmp     edx, 0x8F',
    '    ja      prev_join',
    '    jmp     prev_step',

    'prev_skin:',
    '    cmp     byte ptr [eax + 0x1], 0x9F',
    '    jne     prev_join',
    '    cmp     byte ptr [eax + 0x2], 0x8F',
    '    jne     prev_join',
    '    movzx   edx, byte ptr [eax + 0x3]',
    '    cmp     edx, 0xBB',
    '    jb      prev_join',
    '    cmp     edx, 0xBF',
    '    ja      prev_join',
    '    jmp     prev_step',

    'prev_kc:',
    '    cmp     byte ptr [eax + 0x1], 0x83',
    '    jne     prev_join',
    '    cmp     byte ptr [eax + 0x2], 0xA3',
    '    jne     prev_join',
    '    jmp     prev_step',

    'prev_legacy:',
    f'    jmp     dword ptr [{SENT_PREV:#x}]',

    # ------------------------------------------------------------------
    # prev_seq - ecx = start, eax = some position > start.
    #   success: eax = start of the sequence immediately before it, CF = 0
    #   failure: CF = 1, eax clobbered (the caller keeps its own copy)
    #
    # POP does not touch the flags, so the CF set just before RET survives.
    # prev_seq never reaches prev_legacy, which is what keeps the tail jump
    # running on the caller's own frame with nothing of ours pushed.
    # ------------------------------------------------------------------
    'prev_seq:',
    '    push    ebx',
    '    mov     ebx, eax',                  # remember where we came from
    '    mov     edx, eax',
    '    sub     edx, 0x4',                  # lowest slot a lead may occupy
    '    cmp     edx, ecx',
    '    jae     ps_floor',
    '    mov     edx, ecx',                  # ..but never below the start
    'ps_floor:',
    '    dec     eax',
    'ps_back:',
    '    cmp     byte ptr [eax], 0x80',
    '    jb      ps_ascii',
    '    cmp     byte ptr [eax], 0xC0',
    '    jae     ps_lead',
    '    cmp     eax, edx',                  # a trail byte - keep walking back
    '    jbe     ps_fail',                   # 4 trails in a row, or hit start
    '    dec     eax',
    '    jmp     ps_back',
    'ps_ascii:',
    '    mov     edx, ebx',
    '    sub     edx, eax',
    '    cmp     edx, 0x1',                  # ASCII is only ever 1 byte back
    '    jne     ps_fail',
    '    jmp     ps_ok',
    'ps_lead:',
    '    mov     edx, ebx',
    '    sub     edx, eax',                  # distance walked
    '    movzx   ebx, byte ptr [eax]',       # ebx is spent - reuse as scratch
    '    cmp     ebx, 0xC2',
    '    jb      ps_fail',
    '    cmp     ebx, 0xF5',
    '    jae     ps_fail',
    '    cmp     ebx, 0xE0',
    '    jb      ps_w2',
    '    cmp     ebx, 0xF0',
    '    jb      ps_w3',
    '    cmp     edx, 0x4',                  # the lead must declare exactly
    '    jne     ps_fail',                   # the distance we walked
    '    jmp     ps_ok',
    'ps_w3:',
    '    cmp     edx, 0x3',
    '    jne     ps_fail',
    '    jmp     ps_ok',
    'ps_w2:',
    '    cmp     edx, 0x2',
    '    jne     ps_fail',
    'ps_ok:',
    '    pop     ebx',
    '    clc',
    '    ret',
    'ps_fail:',
    '    pop     ebx',
    '    stc',
    '    ret',
]


LITERAL = re.compile(r'(?<![\w.$])(\d+)(?![\w.])')


def check_literals(lines):
    """keystone reads bare integers as hex - refuse anything ambiguous."""
    bad = []
    for line in lines:
        body = line.split(';')[0]
        for m in LITERAL.finditer(body):
            if m.group(1) not in ('0', '1'):
                bad.append(line.strip())
                break
    if bad:
        sys.exit('ambiguous decimal literals (write them as 0x..):\n  '
                 + '\n  '.join(bad))


def assemble(lines):
    check_literals(lines)
    src = '\n'.join(line.split(';')[0].rstrip() for line in lines)
    ks = Ks(KS_ARCH_X86, KS_MODE_32)
    encoding, _ = ks.asm(src, 0)
    return bytes(encoding)


def find_sentinels(blob, want):
    """Locate each sentinel dword, requiring exactly one occurrence."""
    out = {}
    for name, value in want.items():
        needle = struct.pack('<I', value)
        hits = [i for i in range(len(blob) - 3) if blob[i:i + 4] == needle]
        if len(hits) != 1:
            sys.exit(f'{name}: expected 1 sentinel, found {len(hits)}')
        out[name] = hits[0]
    return out


def qjs_hex(blob, per_line=16):
    rows = []
    for i in range(0, len(blob), per_line):
        rows.append('"' + ' '.join(f'{b:02X}' for b in blob[i:i + per_line]) + ' "')
    return '\t  ' + '\n\t+ '.join(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dis', action='store_true', help='also print a disassembly')
    args = ap.parse_args()

    nxt = assemble(NEXT)
    prv = assemble(PREV)
    blob = nxt + prv
    entry_prev = len(nxt)

    sent = find_sentinels(blob, {'CharNextExA': SENT_NEXT, 'CharPrevExA': SENT_PREV})

    print(f'; {len(blob)} bytes total  (next {len(nxt)}, prev {len(prv)})')
    print()
    print(f'AllowUTF8Enconding.LayoutEntryNext = 0x{0:03X};')
    print(f'AllowUTF8Enconding.LayoutEntryPrev = 0x{entry_prev:03X};')
    print()
    print('AllowUTF8Enconding.LayoutFixups = [')
    for name, off in sorted(sent.items(), key=lambda kv: kv[1]):
        print(f"\t[0x{off:03X}, '{name}'],")
    print('];')
    print()
    print('AllowUTF8Enconding.LayoutCode =')
    print(qjs_hex(blob))
    print('\t;')

    if args.dis:
        import capstone
        md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
        print()
        print('; ---- disassembly ----')
        for i in md.disasm(blob, 0):
            mark = ''
            if i.address == 0:
                mark = '   <- EntryNext'
            elif i.address == entry_prev:
                mark = '   <- EntryPrev'
            print(f'{i.address:#05x}  {i.bytes.hex(" "):<26} '
                  f'{i.mnemonic:<7} {i.op_str}{mark}')

    return 0


if __name__ == '__main__':
    sys.exit(main())
