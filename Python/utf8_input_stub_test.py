r"""Emulate the exact bytes emitted by utf8_input_stub_gen.py and check every path.

Runs the assembled paste stub under unicorn against a reference model of
WideCharToMultiByte, covering the stdcall frame discipline, the callee-saved
registers, the two failure paths (which differ on purpose - see below) and the
length cap that keeps the conversion from ever overflowing the scratch buffer.

The failure paths are asymmetric and that asymmetry is the point: a failed
GlobalLock returns NULL, because the caller is then right to skip both the
insert and its GlobalUnlock; a failed conversion returns an empty string,
because the handle IS locked by then and returning NULL would leak the lock
count. An earlier revision returned NULL from both and leaked.

    pip install unicorn
    python Python/utf8_input_stub_test.py
"""
import sys, os, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from unicorn import *
from unicorn.x86_const import *
import utf8_input_stub_gen as gen

CODE  = 0x00100000
IATPG = 0x00200000          # fake IAT page
BUFPG = 0x00300000          # the UTF-8 scratch buffer
WIDEPG = 0x00500000         # the "locked" clipboard block
STACK = 0x00400000
GL_FN = 0x00600000          # fake GlobalLock
WC_FN = 0x00700000          # fake WideCharToMultiByte

SLOT_LOCK = IATPG + 0x00
SLOT_W2MB = IATPG + 0x04
RETMARK   = 0xBEEF0000

BUFSIZE = gen.BUFSIZE
CAP     = gen.CAP
CP_UTF8 = 0xFDE9

# The same sentinel table the generator prints for the .qjs, resolved here to
# this harness's addresses exactly as AllowUTF8Enconding.qjs resolves them.
WANT = [
    ('GlobalLock',           gen.SENT_LOCK, 'imp'),
    ('WideCharToMultiByte',  gen.SENT_W2MB, 'imp'),
    ('buf',                  gen.SENT_BUF,  'buf'),
]
RESOLVE = {gen.SENT_LOCK: SLOT_LOCK, gen.SENT_W2MB: SLOT_W2MB, gen.SENT_BUF: BUFPG}
BY_NAME = {name: value for name, value, _ in WANT}


def assemble():
    """Assemble the stub and apply the fixups, so the test can never drift
    from the bytes the generator actually emits into the patch."""
    code = bytearray(gen.assemble(gen.PASTE))
    for off, kind, name in gen.find_sentinels(bytes(code), WANT):
        code[off:off + 4] = struct.pack('<I', RESOLVE[BY_NAME[name]])
    return bytes(code)


def run(text, handle=0x1234, lock_fails=False, wc_fails=False):
    """Call the stub as __stdcall(HGLOBAL) and report what it produced."""
    mu = Uc(UC_ARCH_X86, UC_MODE_32)
    for base, size in ((CODE, 0x1000), (IATPG, 0x1000), (BUFPG, BUFSIZE),
                       (STACK, 0x10000), (WIDEPG, 0x20000),
                       (GL_FN, 0x1000), (WC_FN, 0x1000)):
        mu.mem_map(base, size)
    mu.mem_write(CODE, assemble())
    mu.mem_write(SLOT_LOCK, struct.pack('<I', GL_FN))
    mu.mem_write(SLOT_W2MB, struct.pack('<I', WC_FN))
    mu.mem_write(WIDEPG, text.encode('utf-16-le') + b'\x00\x00')
    mu.mem_write(BUFPG, b'\xCC' * BUFSIZE)      # poison, so real writes show up

    seen = {}

    def hook(u, addr, size, _):
        sp = u.reg_read(UC_X86_REG_ESP)
        ret = struct.unpack('<I', u.mem_read(sp, 4))[0]
        if addr == GL_FN:                        # LPVOID __stdcall GlobalLock(HGLOBAL)
            seen['handle'] = struct.unpack('<I', u.mem_read(sp + 4, 4))[0]
            u.reg_write(UC_X86_REG_EAX, 0 if lock_fails else WIDEPG)
            u.reg_write(UC_X86_REG_ESP, sp + 8)
        elif addr == WC_FN:                      # int __stdcall WideCharToMultiByte(8)
            a = struct.unpack('<8I', u.mem_read(sp + 4, 32))
            seen['args'] = a
            cp, flags, src, srclen, dst, dstlen, defchr, useddef = a
            # Under CP_UTF8 these two MUST be NULL or the real API fails outright.
            assert (defchr, useddef) == (0, 0), 'lpDefaultChar must be NULL for CP_UTF8'
            assert flags == 0, 'dwFlags must be 0 for CP_UTF8'
            if wc_fails:
                u.reg_write(UC_X86_REG_EAX, 0)
            else:
                # errors='replace' models the real API: with flags 0 an unpaired
                # surrogate becomes U+FFFD rather than failing the call.
                s = bytes(u.mem_read(src, srclen * 2)).decode('utf-16-le', 'replace')
                enc = s.encode('utf-8')
                assert len(enc) <= dstlen, 'stub asked for too small a buffer'
                u.mem_write(dst, enc)
                u.reg_write(UC_X86_REG_EAX, len(enc))
            u.reg_write(UC_X86_REG_ESP, sp + 36)
        else:
            return
        u.reg_write(UC_X86_REG_EIP, ret)

    mu.hook_add(UC_HOOK_CODE, hook, begin=GL_FN, end=WC_FN + 0x1000)

    sp = STACK + 0x8000
    mu.mem_write(sp, struct.pack('<I', RETMARK))
    mu.mem_write(sp + 4, struct.pack('<I', handle))
    mu.reg_write(UC_X86_REG_ESP, sp)
    for reg, val in ((UC_X86_REG_EBX, 0xB0B0B0B0), (UC_X86_REG_ESI, 0x51515151),
                     (UC_X86_REG_EDI, 0xD1D1D1D1)):
        mu.reg_write(reg, val)
    try:
        mu.emu_start(CODE, RETMARK, count=2000000)
    except UcError:
        pass

    eax = mu.reg_read(UC_X86_REG_EAX)
    out = None
    if eax:
        raw = bytes(mu.mem_read(eax, BUFSIZE))
        assert b'\x00' in raw, 'result is not NUL-terminated inside the buffer'
        out = raw[:raw.index(b'\x00')].decode('utf-8', 'replace')
    return dict(eax=eax, out=out, esp=mu.reg_read(UC_X86_REG_ESP) - sp,
                ebx=mu.reg_read(UC_X86_REG_EBX), esi=mu.reg_read(UC_X86_REG_ESI),
                edi=mu.reg_read(UC_X86_REG_EDI), **seen)


FAILED = []


def check(name, cond, detail=''):
    print(f"  {'ok  ' if cond else 'FAIL'} {name}" + (f'   {detail}' if detail else ''))
    if not cond:
        FAILED.append(name)


print('round trip through the stub')
for txt in ('hello', 'Grüße', '한국어 테스톸',
            '\U0001F600', 'hi \U0001F600\U0001F389 there',
            'héllo 日本 \U0001F600' * 3):
    r = run(txt)
    check(f'{txt[:18]!r} survives', r['out'] == txt, f'-> {r["out"]!r}')
    check('  codepage is CP_UTF8', r['args'][0] == CP_UTF8)
    check('  stack balanced (ret 4)', r['esp'] == 8)

print('\ncallee-saved registers')
r = run('\U0001F600')
check('esi restored', r['esi'] == 0x51515151, f'0x{r["esi"]:08X}')
check('edi untouched', r['edi'] == 0xD1D1D1D1, f'0x{r["edi"]:08X}')
check('ebx untouched', r['ebx'] == 0xB0B0B0B0, f'0x{r["ebx"]:08X}')

print('\nargument passthrough')
r = run('x', handle=0xCAFE)
check('original handle reaches GlobalLock', r['handle'] == 0xCAFE, f'0x{r["handle"]:X}')

print('\nempty clipboard')
r = run('')
check('returns an empty buffer, not NULL', r['eax'] != 0 and r['out'] == '')
check('stack balanced', r['esp'] == 8)

print('\nfailure paths (asymmetric on purpose)')
r = run('\U0001F600', lock_fails=True)
check('failed lock -> NULL, caller skips insert and unlock', r['eax'] == 0)
check('stack balanced', r['esp'] == 8)
r = run('\U0001F600', wc_fails=True)
check('failed conversion -> "" so the unlock stays reachable', r['eax'] != 0 and r['out'] == '')
check('stack balanced', r['esp'] == 8)

print('\nlength cap')
r = run('\U0001F600' * 4000)
check('wide length capped', r['args'][3] == CAP, f'{r["args"][3]} units, cap {CAP}')
check('dest size is BUFSIZE-1', r['args'][5] == BUFSIZE - 1,
      f'0x{r["args"][5]:X}, last byte kept for the NUL')
check('output fits the buffer', len(r['out'].encode()) < BUFSIZE)
r = run('a' * 4000)
check('ascii cap truncates cleanly', r['out'] == 'a' * r['args'][3], f'{r["args"][3]} chars')

print()
if FAILED:
    print(f'{len(FAILED)} check(s) failed: ' + ', '.join(FAILED))
    sys.exit(1)
print('all paths verified')
