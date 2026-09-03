#!/usr/bin/env python
"""
Generates the emoji-sprite machine code for Scripts/Patches/AllowUTF8Enconding.qjs

The patch needs ~600 bytes of x86-32 that GDI-draws text runs and
AlphaBlends colour emoji sprites between them. Hand-assembling that as hex
is not realistic, so this builds it with keystone, resolves labels itself
(keystone has no label support) and verifies the result with capstone.

Absolute references (our data block, IAT slots) cannot be known until WARP
allocates, so they are emitted as sentinels and reported as a fixup list.
The .qjs writes the real values with Exe.SetUint32 at those byte offsets.

Usage:  python emoji_stub_gen.py          # emit the qjs constants
        python emoji_stub_gen.py --dis    # also disassemble for review
"""

import re
import sys

import capstone
import keystone

# ---------------------------------------------------------------- data layout
# Offsets inside the allocated data block. Kept in one place because both this
# script and the .qjs header comment describe them.
D = {
    "PFNBLEND":  0x000,   # resolved AlphaBlend (0=unresolved, -1=unavailable)
    "WSPACE":    0x008,   # L" " - measured to get the line height
    "SIZEBUF":   0x010,   # SIZE scratch for GetTextExtentPoint32W
    "BLEND":     0x018,   # BLENDFUNCTION {AC_SRC_OVER,0,255,AC_SRC_ALPHA}
    "BMI":       0x01C,   # BITMAPINFOHEADER for the sprite DIB
    "PPV":       0x044,   # ppvBits out-param from CreateDIBSection
    "PATHBUF":   0x050,   # built sprite path
    "FMT":       0x168,   # "data\emoji\%X.bmp"
    "MSIMG":     0x17C,   # "msimg32.dll"
    "ALPHABLEND":0x188,   # "AlphaBlend"
    "GDI32":     0x193,   # "gdi32.dll"
    "GDIALPHA":  0x19D,   # "GdiAlphaBlend"
    "CACHE":     0x1B0,   # 64 x 16 bytes: cp, hdcSrc, w, h
    "QPCTHRESH": 0x5B0,   # one group's worth of QPC ticks (0 = not resolved yet)
    "QPCBUF":    0x5B8,   # LARGE_INTEGER scratch for QPC / QPF
    "DEDUP":     0x5C0,   # 8 x 24 bytes: hdc, cch, hash, anchorX, anchorY, tLast
    "FMGROBJ":   0x680,   # g_fileMgr (0 = GRF loading unavailable, use CreateFileA)
    "FMGRGET":   0x684,   # CFileMgr::Get
    "SIZEOUT":   0x688,   # size out-param for CFileMgr::Get
}
DATA_SIZE = 0x690
CACHE_SLOTS = 64
DEDUP_SLOTS = 8

# IAT slots the stub calls through, resolved by the .qjs at patch time.
IMPORTS = [
    ("TextOutW",             "GDI32.dll"),
    ("GetTextExtentPoint32W","GDI32.dll"),
    ("CreateCompatibleDC",   "GDI32.dll"),
    ("CreateDIBSection",     "GDI32.dll"),
    ("SelectObject",         "GDI32.dll"),
    ("DeleteDC",             "GDI32.dll"),
    ("DeleteObject",         "GDI32.dll"),
    ("CreateFileA",          "KERNEL32.dll"),
    ("GetFileSize",          "KERNEL32.dll"),
    ("ReadFile",             "KERNEL32.dll"),
    ("CloseHandle",          "KERNEL32.dll"),
    # VirtualAlloc rather than the heap: the newer clients (2025 and 2026 here)
    # link the CRT through ucrtbase and no longer import HeapAlloc/HeapFree at
    # all, while VirtualAlloc/VirtualFree are imported by every client we
    # support. It is also what CFileMgr::Get hands back, so one allocator
    # covers both load paths.
    ("VirtualAlloc",         "KERNEL32.dll"),
    ("VirtualFree",          "KERNEL32.dll"),
    ("LoadLibraryA",         "KERNEL32.dll"),
    ("GetProcAddress",       "KERNEL32.dll"),
    ("QueryPerformanceCounter",   "KERNEL32.dll"),
    ("QueryPerformanceFrequency", "KERNEL32.dll"),
    ("wsprintfA",            "USER32.dll"),
]

# Sentinel ranges. Chosen so they cannot collide with real code bytes we care
# about and are trivially recognisable in a hex dump while debugging.
SENT_DATA = 0xE0000000        # + offset into the data block
SENT_IAT  = 0xE1000000        # + 4 * index into IMPORTS

STRINGS = {
    "FMT":        b"data\\emoji\\%X.bmp\x00",
    "MSIMG":      b"msimg32.dll\x00",
    "ALPHABLEND": b"AlphaBlend\x00",
    "GDI32":      b"gdi32.dll\x00",
    "GDIALPHA":   b"GdiAlphaBlend\x00",
}


def d(name, extra=0):
    """Absolute sentinel for a data-block field."""
    return SENT_DATA + D[name] + extra


def imp(name):
    """Absolute sentinel for an IAT slot."""
    idx = [n for n, _ in IMPORTS].index(name)
    return SENT_IAT + 4 * idx


# ------------------------------------------------------------------ assembler
# keystone assembles one instruction at a time with no notion of labels, so we
# resolve them ourselves: assemble repeatedly, feeding back the offsets we
# learned, until nothing moves. Short-vs-near jump selection makes sizes shrink
# between rounds, hence the fixed-point loop rather than two passes.
_ks = keystone.Ks(keystone.KS_ARCH_X86, keystone.KS_MODE_32)
_ks.syntax = keystone.KS_OPT_SYNTAX_INTEL

LABEL_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*):$")


def assemble(source, base=0):
    """Assemble `source` (label: / instruction lines). Returns (bytes, labels).

    `{name}` in an operand expands to that label's absolute address.
    """
    lines = []
    label_names = set()
    for raw in source.splitlines():
        line = raw.split(";")[0].strip()
        if not line:
            continue
        m = LABEL_RE.match(line)
        if m:
            label_names.add(m.group(1))
            lines.append(("label", m.group(1)))
        else:
            lines.append(("insn", line))

    # keystone has no symbol table, so branch targets have to be numbers by the
    # time it sees them. Substitute each known label name with its current
    # address; unknown-so-far labels resolve to 0 and settle on later rounds.
    label_re = re.compile(r"\b(" + "|".join(sorted(label_names, key=len, reverse=True)) + r")\b") if label_names else None

    labels = {}
    encoded = {}

    for _ in range(60):
        offset = 0
        new_labels = {}
        new_encoded = {}
        for idx, (kind, text) in enumerate(lines):
            if kind == "label":
                new_labels[text] = base + offset
                continue
            # keystone's Intel parser reads bare integers as HEX, so a literal
            # like `40` silently becomes 0x40. Refuse anything ambiguous and
            # force every constant to be written with an explicit 0x prefix.
            for lit in re.findall(r"(?<![\w0-9xX])(\d+)(?![\w])", text):
                # Only literals that read differently in the two bases are a
                # hazard; 0-9 mean the same thing either way.
                if int(lit, 10) != int(lit, 16):
                    raise SyntaxError(
                        f"ambiguous decimal literal {lit!r} in {text!r} - "
                        f"write it as 0x{int(lit):X}"
                    )
            expanded = text
            if label_re:
                expanded = label_re.sub(
                    lambda m: hex(labels.get(m.group(1), 0)), expanded
                )
            try:
                enc, _cnt = _ks.asm(expanded.encode(), base + offset)
            except keystone.KsError as err:
                raise SyntaxError(
                    f"cannot assemble {expanded!r} (from {text!r}): {err}"
                ) from None
            if enc is None:
                raise SyntaxError(f"cannot assemble: {expanded}")
            new_encoded[idx] = bytes(enc)
            offset += len(enc)

        if new_labels == labels and new_encoded == encoded:
            break
        labels, encoded = new_labels, new_encoded
    else:
        raise RuntimeError("label resolution did not converge")


    blob = b"".join(encoded[i] for i in sorted(encoded))
    return blob, labels


def find_fixups(blob):
    """Locate every embedded sentinel dword and describe it for the .qjs."""
    fixups = []
    for off in range(0, len(blob) - 3):
        val = int.from_bytes(blob[off:off + 4], "little")
        if SENT_DATA <= val < SENT_DATA + 0x10000:
            fixups.append((off, "data", val - SENT_DATA))
        elif SENT_IAT <= val < SENT_IAT + 0x1000:
            idx = (val - SENT_IAT) // 4
            fixups.append((off, "imp", IMPORTS[idx][0]))
    return fixups


# --------------------------------------------------------------- the stub code
# Emoji ranges. Deliberately narrow: these blocks are pictographs nobody types
# as prose, so treating them as sprites cannot swallow ordinary text. Arrows
# (U+2190..21FF) are excluded on purpose - RO UI strings use them as glyphs.
SOURCE = r"""
; ============================================================ EmojiTextOut
; Replaces `call [TextOutW]`. stdcall, 5 args, returns BOOL.
;   [ebp+08] hdc   [ebp+0C] x   [ebp+10] y   [ebp+14] wstr   [ebp+18] cch
; locals
;   [ebp-04] penX      [ebp-08] runStart  [ebp-0C] i      [ebp-10] lineH
;   [ebp-14] cpLen     [ebp-18] cp        [ebp-1C] retVal
;   [ebp-20] runCount  [ebp-24] runPtr    [ebp-28] ownSprites
EmojiTextOut:
    push ebp
    mov ebp, esp
    sub esp, 0x30
    push ebx
    push esi
    push edi
    mov dword ptr [ebp-0x1C], 1

    mov esi, [ebp+0x14]
    test esi, esi
    jz ETO_PLAIN
    mov ecx, [ebp+0x18]
    cmp ecx, 0
    jle ETO_PLAIN

    xor edi, edi
ETO_SCAN:
    mov ecx, [ebp+0x18]
    call DECODE
    push edx
    mov ecx, eax
    call ISEMOJI
    pop edx
    test eax, eax
    jnz ETO_HAVE
    add edi, edx
    cmp edi, [ebp+0x18]
    jl ETO_SCAN

ETO_PLAIN:
    push dword ptr [ebp+0x18]
    push dword ptr [ebp+0x14]
    push dword ptr [ebp+0x10]
    push dword ptr [ebp+0x0C]
    push dword ptr [ebp+8]
    call dword ptr [{IAT_TEXTOUTW}]
    mov [ebp-0x1C], eax
    jmp ETO_DONE

ETO_HAVE:
    ; Outlined text is the same string drawn five times - (x-1,y) (x+1,y)
    ; (x,y-1) (x,y+1) in the outline colour, then (x,y) in the fill colour.
    ; GDI hides the four outline copies behind the fill, but AlphaBlend does
    ; not honour SetTextColor, so an unguarded sprite blits at full colour on
    ; every pass and the emoji appears five times. Claim the group on its
    ; first pass and blit only for that one; the other four still draw their
    ; text runs, which is what keeps the outline.
    call CLAIMGROUP
    mov [ebp-0x28], eax

    ; line height = cy of a single space in the current font
    push {DAT_SIZEBUF}
    push 1
    push {DAT_WSPACE}
    push dword ptr [ebp+8]
    call dword ptr [{IAT_GTEP}]
    mov eax, [{DAT_SIZEBUF_CY}]
    cmp eax, 0
    jg ETO_LH_OK
    mov eax, 0xC
ETO_LH_OK:
    mov [ebp-0x10], eax

    mov eax, [ebp+0x0C]
    mov [ebp-4], eax
    xor eax, eax
    mov [ebp-8], eax
    mov [ebp-0x0C], eax

ETO_LOOP:
    mov edi, [ebp-0x0C]
    cmp edi, [ebp+0x18]
    jge ETO_TAIL
    mov esi, [ebp+0x14]
    mov ecx, [ebp+0x18]
    call DECODE
    mov [ebp-0x18], eax
    mov [ebp-0x14], edx
    mov ecx, eax
    call ISEMOJI
    test eax, eax
    jnz ETO_EMOJI
    mov eax, [ebp-0x14]
    add [ebp-0x0C], eax
    jmp ETO_LOOP

ETO_EMOJI:
    call FLUSHRUN
    ; Skip the blit on a non-owning pass, but fall through to the pen
    ; advance below - every pass must advance identically or the text
    ; following an emoji would land at a different x on each pass.
    cmp dword ptr [ebp-0x28], 0
    je ETO_NOSPR
    mov ecx, [ebp-0x18]
    call GETSPRITE
    test eax, eax
    jz ETO_NOSPR
    mov ebx, eax
    ; AlphaBlend(hdc, penX, y, lineH, lineH, src, 0, 0, w, h, blend)
    push dword ptr [{DAT_BLEND}]
    push dword ptr [ebx+0x0C]
    push dword ptr [ebx+8]
    push 0
    push 0
    push dword ptr [ebx+4]
    push dword ptr [ebp-0x10]
    push dword ptr [ebp-0x10]
    push dword ptr [ebp+0x10]
    push dword ptr [ebp-4]
    push dword ptr [ebp+8]
    call dword ptr [{DAT_PFNBLEND}]
ETO_NOSPR:
    mov eax, [ebp-0x10]
    add [ebp-4], eax
    mov eax, [ebp-0x14]
    add [ebp-0x0C], eax
    ; swallow a trailing VARIATION SELECTOR-16 so it never draws as a box
    mov edi, [ebp-0x0C]
    cmp edi, [ebp+0x18]
    jge ETO_NOVS
    mov esi, [ebp+0x14]
    movzx eax, word ptr [esi+edi*2]
    cmp eax, 0xFE0F
    jne ETO_NOVS
    inc dword ptr [ebp-0x0C]
ETO_NOVS:
    mov eax, [ebp-0x0C]
    mov [ebp-8], eax
    jmp ETO_LOOP

ETO_TAIL:
    call FLUSHRUN
ETO_DONE:
    mov eax, [ebp-0x1C]
    pop edi
    pop esi
    pop ebx
    mov esp, ebp
    pop ebp
    ret 0x14

; --------------------------------------------------------------- CLAIMGROUP
; Decides whether this call owns the sprite blit. eax=1 to blit, 0 to skip.
;
; A group is one logical string drawn several times over. The passes differ
; only in position (by one pixel) and colour, so identity is: same hdc, same
; length, same characters. Position cannot be part of the key - it is the one
; thing that changes - so an anchor is stored on the first pass and later
; passes match if they are within +/-2 of it.
;
; The first pass to arrive wins, and that is the (x-1,y) outline pass, so the
; sprite lands one pixel left of the true position. At UI line heights that is
; not perceptible, and it is the only choice available without knowing on pass
; one how many passes are coming.
;
; WHAT SEPARATES A GROUP FROM THE NEXT FRAME IS TIME, NOT A COUNT
; --------------------------------------------------------------
; Counting passes and freeing the slot on the fifth is wrong, and the failure
; is ugly: any caller that draws a different number of times leaves the entry
; live at the end of the frame, so the NEXT frame's first pass matches it and
; gets suppressed - the emoji vanishes for a frame, reappears when the count
; finally rolls over, and the whole chatbox flickers. Pass counts do vary:
; unoutlined text draws once, drop-shadowed text twice.
;
; The passes of one group are consecutive calls microseconds apart, while the
; next frame is milliseconds away - so an entry is simply given a lifetime.
; A match must be both key-equal AND recent; anything older is a new frame and
; is reclaimed. That is correct for ANY number of passes, with nothing to
; desync, and a slot cannot leak because age alone makes it reusable.
;
; The lifetime is 2ms of QPC ticks, resolved once on first use. Groups finish
; in tens of microseconds; frames are 16ms at 60fps and 4ms even at 250fps, so
; the window sits an order of magnitude clear of both ends. If QPC is somehow
; unavailable the table is bypassed entirely and every pass blits - visibly
; wrong, but never invisible, which is the better way to fail.
;
; ecx is preserved for the caller; only eax is returned.
CLAIMGROUP:
    push ebx
    push esi
    push edi
    push ecx
    push edx

    ; --- resolve the group lifetime once, then honour the bypass marker ---
    mov eax, [{DAT_QPCTHRESH}]
    test eax, eax
    jnz CG_HAVE_THRESH
    call INITTHRESH
    mov eax, [{DAT_QPCTHRESH}]
CG_HAVE_THRESH:
    cmp eax, -1
    jne CG_TIMED
    mov eax, 1
    jmp CG_RET
CG_TIMED:

    ; --- hash the string: h = h*33 + ch over all cch units ---
    mov esi, [ebp+0x14]
    mov ecx, [ebp+0x18]
    xor eax, eax
    xor edi, edi
CG_HASH:
    cmp edi, ecx
    jge CG_HASHED
    mov edx, eax
    shl edx, 5
    add eax, edx
    movzx edx, word ptr [esi+edi*2]
    add eax, edx
    inc edi
    jmp CG_HASH
CG_HASHED:
    mov ebx, eax

    ; --- read 'now' once; edx carries it for the rest of the routine ---
    call READNOW
    mov edx, eax

    ; --- look for a FRESH entry with the same hdc, length and hash ---
    ; tLast == 0 means the slot was never used. Any slot older than the group
    ; lifetime belongs to an earlier frame and is treated as empty, which is
    ; what makes this work for any number of passes.
    mov esi, {DAT_DEDUP}
    xor edi, edi
CG_FIND:
    mov eax, [esi+0x14]
    test eax, eax
    jz CG_NEXT
    mov eax, edx
    sub eax, [esi+0x14]
    cmp eax, [{DAT_QPCTHRESH}]
    jae CG_NEXT
    mov eax, [esi]
    cmp eax, [ebp+8]
    jne CG_NEXT
    mov eax, [esi+4]
    cmp eax, [ebp+0x18]
    jne CG_NEXT
    cmp [esi+8], ebx
    jne CG_NEXT

    ; Same string on the same DC - now require it to be near the anchor,
    ; otherwise this is a genuine second occurrence somewhere else on screen.
    ;
    ; The window is +/-2, not +/-1. The anchor is whatever the FIRST pass was,
    ; and that pass is (x-1, y); the group then spans x-1 .. x+1, so relative
    ; to the anchor the offsets run 0 .. +2 on x and -1 .. +1 on y. A +/-1
    ; window would miss the (x+1, y) pass, which would then claim a second
    ; slot and blit again - two sprites instead of one.
    ;
    ; Unsigned trick: add the window, then one compare catches both signs.
    mov eax, [ebp+0x0C]
    sub eax, [esi+0x0C]
    add eax, 2
    cmp eax, 4
    ja CG_NEXT
    mov eax, [ebp+0x10]
    sub eax, [esi+0x10]
    add eax, 2
    cmp eax, 4
    ja CG_NEXT

    ; A later pass of the group that is still running. Refresh the stamp so a
    ; long group cannot age out from under itself mid-draw, and skip the blit.
    ; Nothing is counted and nothing is freed - the entry simply goes stale on
    ; its own once this frame stops touching it.
    mov [esi+0x14], edx
    xor eax, eax
    jmp CG_RET

CG_NEXT:
    add esi, 0x18
    inc edi
    cmp edi, {DEDUP_SLOTS_IMM}
    jl CG_FIND

    ; --- no match: take the first slot that is empty or stale, and blit ---
    ; A stale slot is always reclaimable, so the table cannot wedge and there
    ; is no victim to guess at. Should every slot somehow be fresh (more than
    ; DEDUP_SLOTS distinct strings drawn inside one lifetime), fall through
    ; with the last slot - one extra blit, never a suppressed one.
    mov esi, {DAT_DEDUP}
    xor edi, edi
CG_FREE:
    mov eax, [esi+0x14]
    test eax, eax
    jz CG_TAKE
    mov eax, edx
    sub eax, [esi+0x14]
    cmp eax, [{DAT_QPCTHRESH}]
    jae CG_TAKE
    add esi, 0x18
    inc edi
    cmp edi, {DEDUP_SLOTS_IMM}
    jl CG_FREE
    sub esi, 0x18
CG_TAKE:
    mov eax, [ebp+8]
    mov [esi], eax
    mov eax, [ebp+0x18]
    mov [esi+4], eax
    mov [esi+8], ebx
    mov eax, [ebp+0x0C]
    mov [esi+0x0C], eax
    mov eax, [ebp+0x10]
    mov [esi+0x10], eax
    ; stamp with 'now'. READNOW never returns 0, so a stamped slot is always
    ; distinguishable from a never-used one.
    mov [esi+0x14], edx
    mov eax, 1
CG_RET:
    pop edx
    pop ecx
    pop edi
    pop esi
    pop ebx
    ret

; ---------------------------------------------------------------- INITTHRESH
; Works out how many QPC ticks one group may span and stores it in QPCTHRESH.
; Called once - afterwards QPCTHRESH is non-zero, either the tick count or -1
; to mean "no usable timer, never suppress".
INITTHRESH:
    push ecx
    push edx
    push {DAT_QPCBUF}
    call dword ptr [{IAT_QPF}]
    test eax, eax
    jz IT_FAIL
    ; frequency is a 64-bit count/second; anything needing the high dword is
    ; far beyond what a 32-bit divide handles, so treat it as unusable
    mov eax, [{DAT_QPCBUF_HI}]
    test eax, eax
    jnz IT_FAIL
    mov eax, [{DAT_QPCBUF}]
    test eax, eax
    jz IT_FAIL
    ; threshold = freq / 500  ->  2 milliseconds
    xor edx, edx
    mov ecx, 0x1F4
    div ecx
    test eax, eax
    jz IT_FAIL
    mov [{DAT_QPCTHRESH}], eax
    pop edx
    pop ecx
    ret
IT_FAIL:
    mov dword ptr [{DAT_QPCTHRESH}], -1
    pop edx
    pop ecx
    ret

; ------------------------------------------------------------------ READNOW
; Low dword of QueryPerformanceCounter, never 0 so it cannot be mistaken for
; an unused slot.
;
; Only the low dword is kept, so the elapsed subtraction in CLAIMGROUP is
; modulo 2^32 - correct for any gap shorter than one wrap, which at typical
; frequencies is several minutes. Two things can happen across a wrap, both
; harmless and both self-correcting on the next call:
;
;   - a group whose passes straddle the wrap reads as a new group: one extra
;     blit on one frame.
;   - an entry left untouched for very nearly a whole wrap reads as fresh
;     again: its next first pass is suppressed, so one dark frame. This needs
;     the elapsed time to land inside a 2ms window once every few minutes,
;     on a slot nothing else reclaimed in the meantime, with every key field
;     still matching - and a match restamps the slot, so the frame after it
;     is correct again.
READNOW:
    push ecx
    push edx
    push {DAT_QPCBUF}
    call dword ptr [{IAT_QPC}]
    mov eax, [{DAT_QPCBUF}]
    test eax, eax
    jnz RN_RET
    inc eax
RN_RET:
    pop edx
    pop ecx
    ret

; ---------------------------------------------------------------- FLUSHRUN
; Draws wstr[runStart..i) at penX and advances penX. Runs on the caller's
; frame, so it is only valid from EmojiTextOut.
FLUSHRUN:
    mov eax, [ebp-0x0C]
    sub eax, [ebp-8]
    jle FR_RET
    mov [ebp-0x20], eax
    mov ecx, [ebp-8]
    mov esi, [ebp+0x14]
    lea edx, [esi+ecx*2]
    mov [ebp-0x24], edx
    push {DAT_SIZEBUF}
    push dword ptr [ebp-0x20]
    push dword ptr [ebp-0x24]
    push dword ptr [ebp+8]
    call dword ptr [{IAT_GTEP}]
    push dword ptr [ebp-0x20]
    push dword ptr [ebp-0x24]
    push dword ptr [ebp+0x10]
    push dword ptr [ebp-4]
    push dword ptr [ebp+8]
    call dword ptr [{IAT_TEXTOUTW}]
    test eax, eax
    jnz FR_OK
    mov dword ptr [ebp-0x1C], 0
FR_OK:
    mov eax, [{DAT_SIZEBUF}]
    add [ebp-4], eax
FR_RET:
    ret
"""

SOURCE += r"""
; ========================================================== EmojiMeasure
; Replaces `call [GetTextExtentPoint32W]`. Measures the same way EmojiTextOut
; draws, so wrapping and centring stay in agreement with what appears.
;   [ebp+08] hdc  [ebp+0C] wstr  [ebp+10] cch  [ebp+14] lpSize
; locals: [ebp-04] total [ebp-08] runStart [ebp-0C] i [ebp-10] lineH
;         [ebp-14] cpLen [ebp-18] cp       [ebp-1C] ret
EmojiMeasure:
    push ebp
    mov ebp, esp
    sub esp, 0x28
    push ebx
    push esi
    push edi

    push dword ptr [ebp+0x14]
    push dword ptr [ebp+0x10]
    push dword ptr [ebp+0x0C]
    push dword ptr [ebp+8]
    call dword ptr [{IAT_GTEP}]
    mov [ebp-0x1C], eax
    test eax, eax
    jz EM_DONE

    mov esi, [ebp+0x0C]
    test esi, esi
    jz EM_DONE
    mov ecx, [ebp+0x10]
    cmp ecx, 0
    jle EM_DONE

    xor edi, edi
EM_SCAN:
    mov ecx, [ebp+0x10]
    call DECODE
    push edx
    mov ecx, eax
    call ISEMOJI
    pop edx
    test eax, eax
    jnz EM_HAVE
    add edi, edx
    cmp edi, [ebp+0x10]
    jl EM_SCAN
    jmp EM_DONE

EM_HAVE:
    mov eax, [ebp+0x14]
    mov eax, [eax+4]
    cmp eax, 0
    jg EM_LH_OK
    mov eax, 0xC
EM_LH_OK:
    mov [ebp-0x10], eax
    xor eax, eax
    mov [ebp-4], eax
    mov [ebp-8], eax
    mov [ebp-0x0C], eax

EM_LOOP:
    mov edi, [ebp-0x0C]
    cmp edi, [ebp+0x10]
    jge EM_TAIL
    mov esi, [ebp+0x0C]
    mov ecx, [ebp+0x10]
    call DECODE
    mov [ebp-0x18], eax
    mov [ebp-0x14], edx
    mov ecx, eax
    call ISEMOJI
    test eax, eax
    jnz EM_EMOJI
    mov eax, [ebp-0x14]
    add [ebp-0x0C], eax
    jmp EM_LOOP

EM_EMOJI:
    call MEASURERUN
    mov eax, [ebp-0x10]
    add [ebp-4], eax
    mov eax, [ebp-0x14]
    add [ebp-0x0C], eax
    mov edi, [ebp-0x0C]
    cmp edi, [ebp+0x10]
    jge EM_NOVS
    mov esi, [ebp+0x0C]
    movzx eax, word ptr [esi+edi*2]
    cmp eax, 0xFE0F
    jne EM_NOVS
    inc dword ptr [ebp-0x0C]
EM_NOVS:
    mov eax, [ebp-0x0C]
    mov [ebp-8], eax
    jmp EM_LOOP

EM_TAIL:
    call MEASURERUN
    mov ecx, [ebp+0x14]
    mov eax, [ebp-4]
    mov [ecx], eax
    mov eax, [ebp-0x10]
    mov [ecx+4], eax
EM_DONE:
    mov eax, [ebp-0x1C]
    pop edi
    pop esi
    pop ebx
    mov esp, ebp
    pop ebp
    ret 0x10

; -------------------------------------------------------------- MEASURERUN
MEASURERUN:
    mov eax, [ebp-0x0C]
    sub eax, [ebp-8]
    jle MR_RET
    mov ecx, [ebp-8]
    mov esi, [ebp+0x0C]
    lea edx, [esi+ecx*2]
    push {DAT_SIZEBUF}
    push eax
    push edx
    push dword ptr [ebp+8]
    call dword ptr [{IAT_GTEP}]
    mov eax, [{DAT_SIZEBUF}]
    add [ebp-4], eax
MR_RET:
    ret

; ------------------------------------------------------------------ DECODE
; esi=wstr edi=index ecx=cch -> eax=codepoint edx=unitCount
DECODE:
    push ebx
    movzx eax, word ptr [esi+edi*2]
    mov edx, 1
    mov ebx, eax
    and ebx, 0xFC00
    cmp ebx, 0xD800
    jne DEC_RET
    lea ebx, [edi+1]
    cmp ebx, ecx
    jge DEC_RET
    movzx ebx, word ptr [esi+edi*2+2]
    push ebx
    and ebx, 0xFC00
    cmp ebx, 0xDC00
    pop ebx
    jne DEC_RET
    sub eax, 0xD800
    shl eax, 0xA
    add eax, ebx
    sub eax, 0xDC00
    add eax, 0x10000
    mov edx, 2
DEC_RET:
    pop ebx
    ret

; ----------------------------------------------------------------- ISEMOJI
; ecx=codepoint -> eax=1 when we own the glyph
ISEMOJI:
    xor eax, eax
    cmp ecx, 0x1F000
    jl IE_BMP
    cmp ecx, 0x1FAFF
    jg IE_NO
    inc eax
    ret
IE_BMP:
    cmp ecx, 0x2600
    jl IE_NO
    cmp ecx, 0x27BF
    jg IE_2B
    inc eax
    ret
IE_2B:
    cmp ecx, 0x2B00
    jl IE_NO
    cmp ecx, 0x2BFF
    jg IE_NO
    inc eax
IE_NO:
    ret
"""

SOURCE += r"""
; ---------------------------------------------------------------- RESOLVEFN
; AlphaBlend lives in msimg32.dll, which just forwards to gdi32's
; GdiAlphaBlend. Try the documented name first, fall back to the real one.
RESOLVEFN:
    push {DAT_MSIMG}
    call dword ptr [{IAT_LOADLIB}]
    test eax, eax
    jz RF_GDI
    push {DAT_ALPHABLEND}
    push eax
    call dword ptr [{IAT_GETPROC}]
    test eax, eax
    jz RF_GDI
    mov [{DAT_PFNBLEND}], eax
    ret
RF_GDI:
    push {DAT_GDI32}
    call dword ptr [{IAT_LOADLIB}]
    test eax, eax
    jz RF_FAIL
    push {DAT_GDIALPHA}
    push eax
    call dword ptr [{IAT_GETPROC}]
    test eax, eax
    jz RF_FAIL
    mov [{DAT_PFNBLEND}], eax
    ret
RF_FAIL:
    mov dword ptr [{DAT_PFNBLEND}], -1
    ret

; ---------------------------------------------------------------- GETSPRITE
; ecx=codepoint -> eax=cache entry (cp,hdc,w,h) or 0.
; A miss is remembered with hdc=0 so a missing file costs one CreateFileA ever.
GETSPRITE:
    push ebx
    push esi
    push edi
    mov ebx, ecx
    mov eax, [{DAT_PFNBLEND}]
    test eax, eax
    jnz GS_FN
    call RESOLVEFN
GS_FN:
    mov eax, [{DAT_PFNBLEND}]
    cmp eax, -1
    je GS_FAIL
    mov esi, {DAT_CACHE}
    xor edi, edi
GS_LOOP:
    mov eax, [esi]
    cmp eax, ebx
    je GS_FOUND
    test eax, eax
    jz GS_LOAD
    add esi, 0x10
    inc edi
    cmp edi, {CACHE_SLOTS_IMM}
    jl GS_LOOP
    jmp GS_FAIL
GS_FOUND:
    cmp dword ptr [esi+4], 0
    je GS_FAIL
    mov eax, esi
    jmp GS_RET
GS_LOAD:
    mov [esi], ebx
    mov dword ptr [esi+4], 0
    mov ecx, ebx
    push esi
    call LOADSPRITE
    pop esi
    test eax, eax
    jz GS_FAIL
    mov eax, esi
    jmp GS_RET
GS_FAIL:
    xor eax, eax
GS_RET:
    pop edi
    pop esi
    pop ebx
    ret

; --------------------------------------------------------------- LOADSPRITE
; ecx=codepoint, esi=cache slot. Fills slot with a DIB-backed memory DC whose
; pixels are premultiplied (AC_SRC_ALPHA requires it). eax=1 on success.
; locals
;  [ebp-04] cp      [ebp-08] slot   [ebp-0C] hFile  [ebp-10] buf
;  [ebp-14] hdcSrc  [ebp-18] hbm    [ebp-1C] size   [ebp-20] bytesRead
;  [ebp-24] w       [ebp-28] h      [ebp-2C] topDown [ebp-30] pixOff
;  [ebp-34] stride  [ebp-38] y      [ebp-3C] x
LOADSPRITE:
    push ebp
    mov ebp, esp
    sub esp, 0x48
    push ebx
    push esi
    push edi
    mov [ebp-4], ecx
    mov [ebp-8], esi
    mov dword ptr [ebp-0x0C], 0
    mov dword ptr [ebp-0x10], 0
    mov dword ptr [ebp-0x14], 0
    mov dword ptr [ebp-0x18], 0

    push dword ptr [ebp-4]
    push {DAT_FMT}
    push {DAT_PATHBUF}
    call dword ptr [{IAT_WSPRINTF}]
    add esp, 0x0C

    ; The client's own file manager searches the data folder AND every mounted
    ; GRF, honouring the data-first setting, so one call covers both places and
    ; a failure here means the file is in neither. It hands back a
    ; VirtualAlloc'd buffer, which is why the disk path below allocates the
    ; same way - one free path then covers both.
    mov eax, [{DAT_FMGROBJ}]
    test eax, eax
    jz LS_DISK
    mov dword ptr [{DAT_SIZEOUT}], 0
    push 0
    push {DAT_SIZEOUT}
    push {DAT_PATHBUF}
    mov ecx, eax
    call dword ptr [{DAT_FMGRGET}]
    test eax, eax
    jz LS_FAIL
    mov [ebp-0x10], eax
    mov eax, [{DAT_SIZEOUT}]
    cmp eax, 0x40
    jb LS_FAIL
    cmp eax, 0x1000000
    ja LS_FAIL
    mov [ebp-0x1C], eax
    jmp LS_PARSE

LS_DISK:
    push 0
    push 0x80
    push 3
    push 0
    push 1
    push 0x80000000
    push {DAT_PATHBUF}
    call dword ptr [{IAT_CREATEFILE}]
    cmp eax, -1
    je LS_FAIL
    mov [ebp-0x0C], eax

    push 0
    push eax
    call dword ptr [{IAT_GETFILESIZE}]
    cmp eax, 0x40
    jb LS_FAIL
    cmp eax, 0x1000000
    ja LS_FAIL
    mov [ebp-0x1C], eax

    push 0x4
    push 0x1000
    push dword ptr [ebp-0x1C]
    push 0
    call dword ptr [{IAT_VIRTUALALLOC}]
    test eax, eax
    jz LS_FAIL
    mov [ebp-0x10], eax

    push 0
    lea eax, [ebp-0x20]
    push eax
    push dword ptr [ebp-0x1C]
    push dword ptr [ebp-0x10]
    push dword ptr [ebp-0x0C]
    call dword ptr [{IAT_READFILE}]
    test eax, eax
    jz LS_FAIL

    push dword ptr [ebp-0x0C]
    call dword ptr [{IAT_CLOSEHANDLE}]
    mov dword ptr [ebp-0x0C], 0

LS_PARSE:
    ; --- BITMAPFILEHEADER(14) + BITMAPINFOHEADER ---
    mov ebx, [ebp-0x10]
    cmp word ptr [ebx], 0x4D42
    jne LS_FAIL
    movzx eax, word ptr [ebx+0x1C]
    cmp eax, 0x20
    jne LS_FAIL
    mov eax, [ebx+0x12]
    cmp eax, 1
    jl LS_FAIL
    cmp eax, 0x200
    jg LS_FAIL
    mov [ebp-0x24], eax
    mov eax, [ebx+0x16]
    mov edx, 0
    cmp eax, 0
    jg LS_POS
    neg eax
    mov edx, 1
LS_POS:
    cmp eax, 1
    jl LS_FAIL
    cmp eax, 0x200
    jg LS_FAIL
    mov [ebp-0x28], eax
    mov [ebp-0x2C], edx
    mov eax, [ebx+0x0A]
    cmp eax, 0x36
    jb LS_FAIL
    mov [ebp-0x30], eax
    ; stride = w*4 ; require pixOff + h*stride <= size
    mov eax, [ebp-0x24]
    shl eax, 2
    mov [ebp-0x34], eax
    imul eax, [ebp-0x28]
    add eax, [ebp-0x30]
    cmp eax, [ebp-0x1C]
    ja LS_FAIL
"""

SOURCE += r"""
    ; --- memory DC + 32bpp top-down DIB to hold the sprite ---
    push 0
    call dword ptr [{IAT_CREATEDC}]
    test eax, eax
    jz LS_FAIL
    mov [ebp-0x14], eax

    mov dword ptr [{DAT_BMI}], 0x28
    mov eax, [ebp-0x24]
    mov [{DAT_BMI_W}], eax
    mov eax, [ebp-0x28]
    neg eax
    mov [{DAT_BMI_H}], eax
    mov dword ptr [{DAT_BMI_PLANES}], 0x00200001
    mov dword ptr [{DAT_BMI_COMP}], 0
    mov dword ptr [{DAT_BMI_SZIMG}], 0
    mov dword ptr [{DAT_BMI_XPPM}], 0
    mov dword ptr [{DAT_BMI_YPPM}], 0
    mov dword ptr [{DAT_BMI_CLRU}], 0
    mov dword ptr [{DAT_BMI_CLRI}], 0

    push 0
    push 0
    push {DAT_PPV}
    push 0
    push {DAT_BMI}
    push dword ptr [ebp-0x14]
    call dword ptr [{IAT_CREATEDIB}]
    test eax, eax
    jz LS_FAIL
    mov [ebp-0x18], eax
    push eax
    push dword ptr [ebp-0x14]
    call dword ptr [{IAT_SELECTOBJ}]

    ; --- copy rows, flipping if the BMP is bottom-up, premultiplying as we go
    mov dword ptr [ebp-0x38], 0
LS_ROW:
    mov eax, [ebp-0x38]
    cmp eax, [ebp-0x28]
    jge LS_ROWEND
    mov eax, [ebp-0x2C]
    test eax, eax
    jnz LS_TD
    mov eax, [ebp-0x28]
    dec eax
    sub eax, [ebp-0x38]
    jmp LS_SY
LS_TD:
    mov eax, [ebp-0x38]
LS_SY:
    imul eax, [ebp-0x34]
    add eax, [ebp-0x30]
    add eax, [ebp-0x10]
    mov esi, eax
    mov eax, [ebp-0x38]
    imul eax, [ebp-0x34]
    add eax, [{DAT_PPV}]
    mov ebx, eax
    mov dword ptr [ebp-0x3C], 0
LS_COL:
    mov eax, [ebp-0x3C]
    cmp eax, [ebp-0x24]
    jge LS_COLEND
    movzx edx, byte ptr [esi+3]
    movzx eax, byte ptr [esi]
    imul eax, edx
    add eax, 0x80
    mov ecx, eax
    shr ecx, 8
    add eax, ecx
    shr eax, 8
    mov [ebx], al
    movzx eax, byte ptr [esi+1]
    imul eax, edx
    add eax, 0x80
    mov ecx, eax
    shr ecx, 8
    add eax, ecx
    shr eax, 8
    mov [ebx+1], al
    movzx eax, byte ptr [esi+2]
    imul eax, edx
    add eax, 0x80
    mov ecx, eax
    shr ecx, 8
    add eax, ecx
    shr eax, 8
    mov [ebx+2], al
    mov [ebx+3], dl
    add esi, 4
    add ebx, 4
    inc dword ptr [ebp-0x3C]
    jmp LS_COL
LS_COLEND:
    inc dword ptr [ebp-0x38]
    jmp LS_ROW
LS_ROWEND:

    ; --- publish into the cache slot ---
    mov esi, [ebp-8]
    mov eax, [ebp-0x14]
    mov [esi+4], eax
    mov eax, [ebp-0x24]
    mov [esi+8], eax
    mov eax, [ebp-0x28]
    mov [esi+0x0C], eax
    mov dword ptr [ebp-0x14], 0
    mov eax, 1
    jmp LS_CLEAN

LS_FAIL:
    xor eax, eax
LS_CLEAN:
    push eax
    mov eax, [ebp-0x0C]
    test eax, eax
    jz LS_NOFILE
    push eax
    call dword ptr [{IAT_CLOSEHANDLE}]
LS_NOFILE:
    mov eax, [ebp-0x10]
    test eax, eax
    jz LS_NOBUF
    push 0x8000
    push 0
    push eax
    call dword ptr [{IAT_VIRTUALFREE}]
LS_NOBUF:
    ; hdcSrc is only non-zero here when we failed after creating it
    mov eax, [ebp-0x14]
    test eax, eax
    jz LS_NODC
    push eax
    call dword ptr [{IAT_DELETEDC}]
LS_NODC:
    pop eax
    pop edi
    pop esi
    pop ebx
    mov esp, ebp
    pop ebp
    ret
"""

# ------------------------------------------------------------------- driver
def build():
    subs = {
        "IAT_TEXTOUTW":    imp("TextOutW"),
        "IAT_GTEP":        imp("GetTextExtentPoint32W"),
        "IAT_CREATEDC":    imp("CreateCompatibleDC"),
        "IAT_CREATEDIB":   imp("CreateDIBSection"),
        "IAT_SELECTOBJ":   imp("SelectObject"),
        "IAT_DELETEDC":    imp("DeleteDC"),
        "IAT_CREATEFILE":  imp("CreateFileA"),
        "IAT_GETFILESIZE": imp("GetFileSize"),
        "IAT_READFILE":    imp("ReadFile"),
        "IAT_CLOSEHANDLE": imp("CloseHandle"),
        "IAT_VIRTUALALLOC": imp("VirtualAlloc"),
        "IAT_VIRTUALFREE": imp("VirtualFree"),
        "IAT_LOADLIB":     imp("LoadLibraryA"),
        "IAT_GETPROC":     imp("GetProcAddress"),
        "IAT_WSPRINTF":    imp("wsprintfA"),
        "IAT_QPC":         imp("QueryPerformanceCounter"),
        "IAT_QPF":         imp("QueryPerformanceFrequency"),
        "DAT_PFNBLEND":    d("PFNBLEND"),
        "DAT_WSPACE":      d("WSPACE"),
        "DAT_SIZEBUF":     d("SIZEBUF"),
        "DAT_SIZEBUF_CY":  d("SIZEBUF", 4),
        "DAT_BLEND":       d("BLEND"),
        "DAT_PPV":         d("PPV"),
        "DAT_PATHBUF":     d("PATHBUF"),
        "DAT_FMT":         d("FMT"),
        "DAT_MSIMG":       d("MSIMG"),
        "DAT_ALPHABLEND":  d("ALPHABLEND"),
        "DAT_GDI32":       d("GDI32"),
        "DAT_GDIALPHA":    d("GDIALPHA"),
        "DAT_CACHE":       d("CACHE"),
        "DAT_DEDUP":       d("DEDUP"),
        "DAT_QPCTHRESH":   d("QPCTHRESH"),
        "DAT_QPCBUF":      d("QPCBUF"),
        "DAT_QPCBUF_HI":   d("QPCBUF", 4),
        "DAT_FMGROBJ":     d("FMGROBJ"),
        "DAT_FMGRGET":     d("FMGRGET"),
        "DAT_SIZEOUT":     d("SIZEOUT"),
        "CACHE_SLOTS_IMM": CACHE_SLOTS,
        "DEDUP_SLOTS_IMM": DEDUP_SLOTS,
    }
    for i, field in enumerate(
        ["", "W", "H", "PLANES", "COMP", "SZIMG", "XPPM", "YPPM", "CLRU", "CLRI"]
    ):
        subs["DAT_BMI" + ("_" + field if field else "")] = d("BMI", 4 * i)

    src = SOURCE
    for key, val in subs.items():
        src = src.replace("{" + key + "}", hex(val))

    blob, labels = assemble(src, base=0)
    return blob, labels, find_fixups(blob)


def emit_qjs(blob, labels, fixups):
    rows = []
    for i in range(0, len(blob), 16):
        rows.append(" ".join(f"{b:02X}" for b in blob[i:i + 16]))

    print("// ---- paste into AllowUTF8Enconding.qjs ----")
    print(f"// code size = {len(blob)} (0x{len(blob):X}) bytes")
    print(f"AllowUTF8Enconding.EmojiDataSize = 0x{DATA_SIZE:X};")
    print(f"AllowUTF8Enconding.EmojiEntryTextOut = 0x{labels['EmojiTextOut']:X};")
    print(f"AllowUTF8Enconding.EmojiEntryMeasure = 0x{labels['EmojiMeasure']:X};")
    print("AllowUTF8Enconding.EmojiCode =")
    for idx, row in enumerate(rows):
        lead = "\t  " if idx == 0 else "\t+ "
        print(f'{lead}"{row} "')
    print("\t;")

    print("AllowUTF8Enconding.EmojiFixups = [")
    for off, kind, ref in fixups:
        if kind == "data":
            print(f"\t[0x{off:03X}, 'data', 0x{ref:X}],")
        else:
            print(f"\t[0x{off:03X}, 'imp', '{ref}'],")
    print("];")

    print("AllowUTF8Enconding.EmojiImports = [")
    for name, dll in IMPORTS:
        print(f"\t['{name}', '{dll}'],")
    print("];")

    print("AllowUTF8Enconding.EmojiStrings = [")
    for key, raw in STRINGS.items():
        hexs = " ".join(f"{b:02X}" for b in raw)
        print(f"\t[0x{D[key]:X}, \"{hexs}\"],  // {raw[:-1].decode()}")
    print("];")


def main():
    blob, labels, fixups = build()

    if "--dis" in sys.argv:
        md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
        name_at = {v: k for k, v in labels.items()}
        for ins in md.disasm(blob, 0):
            if ins.address in name_at:
                print(f"\n{name_at[ins.address]}:")
            print(f"  {ins.address:04X}  {ins.mnemonic:8s} {ins.op_str}")
        print(f"\ntotal {len(blob)} bytes, {len(fixups)} fixups")
        return

    emit_qjs(blob, labels, fixups)


if __name__ == "__main__":
    main()






