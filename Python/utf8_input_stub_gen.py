#!/usr/bin/env python
r"""Generate the clipboard-paste machine code embedded in
Scripts/Patches/AllowUTF8Enconding.qjs.

The client's paste routine asks the clipboard for CF_TEXT, which makes the OS
flatten the text to the ANSI codepage before the client sees a byte - every
character outside that codepage becomes '?'. The patch switches the
request to CF_UNICODETEXT and redirects the GlobalLock call that follows here.

This stub has GlobalLock's exact signature (stdcall, one argument, `ret 4`),
so the InsertString call after it needs no adjustment. It locks the handle,
converts the UTF-16 to UTF-8, and returns a pointer to the converted buffer
instead of the raw lock.

The wide length is capped so the conversion can never fail for want of room:
UTF-8 needs at most 3 bytes per UTF-16 code unit (a surrogate pair is 2 units
-> 4 bytes, i.e. 2 bytes per unit), so (BUFSIZE-1)//3 units always fit.
Truncating mid-surrogate is harmless - with flags 0, WideCharToMultiByte
emits U+FFFD for the unpaired half rather than failing.

    pip install keystone-engine capstone
    python utf8_input_stub_gen.py          # print the constants for the .qjs
    python utf8_input_stub_gen.py --dis    # same, plus an annotated disassembly

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
SENT_LOCK = 0xE1000000          # &KERNEL32.GlobalLock
SENT_W2MB = 0xE1000004          # &KERNEL32.WideCharToMultiByte
SENT_BUF = 0xE0000000           # the allocated UTF-8 scratch buffer

BUFSIZE = 0x1000                # scratch buffer, must match .qjs BufSize
CAP = (BUFSIZE - 1) // 3        # UTF-16 units that always fit once encoded

PASTE = [
    '; LPSTR __stdcall Utf8ClipLock(HGLOBAL hMem)',
    ';   Drop-in for GlobalLock on the paste path. Returns a UTF-8 string, or',
    ';   NULL if the lock itself failed - which is exactly when the caller is',
    ';   right to skip both the insert and its GlobalUnlock.',
    '    push    ebp',
    '    mov     ebp, esp',
    '    push    esi',
    '',
    '    push    dword ptr [ebp + 0x8]',
    f'    call    dword ptr [{SENT_LOCK:#x}]',
    '    test    eax, eax',
    '    je      fail',                        # nothing locked -> nothing to unlock
    '    mov     esi, eax',                    # esi = LPCWSTR
    '',
    '; wlen = min(wcslen(esi), CAP)',
    '    xor     ecx, ecx',
    'len_loop:',
    f'    cmp     ecx, {CAP:#x}',
    '    jae     len_done',
    '    cmp     word ptr [esi + ecx * 0x2], 0x0',
    '    je      len_done',
    '    inc     ecx',
    '    jmp     len_loop',
    'len_done:',
    '    test    ecx, ecx',
    '    je      empty',                       # empty clipboard -> ""
    '',
    '; WideCharToMultiByte(CP_UTF8, 0, esi, wlen, buf, BUFSIZE-1, NULL, NULL)',
    ';   lpDefaultChar and lpUsedDefaultChar MUST be NULL under CP_UTF8 -',
    ';   the call fails outright otherwise. Flags must be 0 for the same reason.',
    '    push    0x0',
    '    push    0x0',
    f'    push    {BUFSIZE - 1:#x}',
    f'    push    {SENT_BUF:#x}',
    '    push    ecx',
    '    push    esi',
    '    push    0x0',
    '    push    0xFDE9',
    f'    call    dword ptr [{SENT_W2MB:#x}]',
    '    test    eax, eax',
    ';   -> empty, NOT fail. The lock succeeded, so the handle must stay',
    ';   unlockable: the caller only reaches its GlobalUnlock when we return',
    ';   non-NULL, and returning NULL here would leak the lock count. An empty',
    ';   string inserts nothing and lets the unlock run. (With the cap above',
    ';   the call has no remaining way to fail, so this is belt and braces.)',
    '    je      empty',
    '',
    '; NUL-terminate at the returned byte count and hand back the buffer',
    f'    mov     ecx, {SENT_BUF:#x}',
    '    mov     byte ptr [ecx + eax], 0x0',
    '    mov     eax, ecx',
    '    jmp     done',
    '',
    'empty:',
    f'    mov     eax, {SENT_BUF:#x}',
    '    mov     byte ptr [eax], 0x0',
    '    jmp     done',
    '',
    'fail:',
    '    xor     eax, eax',
    '',
    'done:',
    '    pop     esi',
    '    pop     ebp',
    '    ret     0x4',
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
    """Locate each sentinel dword; SENT_BUF legitimately appears more than once."""
    out = []
    for name, value, kind in want:
        needle = struct.pack('<I', value)
        hits = [i for i in range(len(blob) - 3) if blob[i:i + 4] == needle]
        if not hits:
            sys.exit(f'{name}: sentinel not found')
        for h in hits:
            out.append((h, kind, name))
    return sorted(out)


def qjs_hex(blob, per_line=16):
    rows = []
    for i in range(0, len(blob), per_line):
        rows.append('"' + ' '.join(f'{b:02X}' for b in blob[i:i + per_line]) + ' "')
    return '\t  ' + '\n\t+ '.join(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dis', action='store_true', help='also print a disassembly')
    args = ap.parse_args()

    blob = assemble(PASTE)
    sent = find_sentinels(blob, [
        ('GlobalLock', SENT_LOCK, 'imp'),
        ('WideCharToMultiByte', SENT_W2MB, 'imp'),
        ('buf', SENT_BUF, 'buf'),
    ])

    print(f'; {len(blob)} bytes, cap {CAP:#x} UTF-16 units, buffer {BUFSIZE:#x}')
    print()
    print(f'AllowUTF8Enconding.InputBufSize = 0x{BUFSIZE:X};')
    print()
    print('AllowUTF8Enconding.InputFixups = [')
    for off, kind, name in sent:
        print(f"\t[0x{off:03X}, '{kind}', '{name}'],")
    print('];')
    print()
    print('AllowUTF8Enconding.InputCode =')
    print(qjs_hex(blob))
    print('\t;')

    if args.dis:
        import capstone
        md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
        print()
        print('; ---- disassembly ----')
        for i in md.disasm(blob, 0):
            print(f'{i.address:#05x}  {i.bytes.hex(" "):<26} '
                  f'{i.mnemonic:<7} {i.op_str}')

    return 0


if __name__ == '__main__':
    sys.exit(main())
