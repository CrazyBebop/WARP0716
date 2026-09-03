#!/usr/bin/env python
r"""Generate 32bpp BMP emoji sprites for the AllowUTF8Enconding WARP patch.

Sprites are written as <out>\data\emoji\<CODEPOINT-HEX>.bmp - exactly where
the patched client looks for them. Copy that data folder into your RO install
(or point --out straight at the install).

    python make_emoji_sprites.py                      # every glyph, 64x64
    python make_emoji_sprites.py --size 32
    python make_emoji_sprites.py --out "C:\\RO" --add 1F92D,1F9E1

This walks every emoji and symbol block the patch recognises and writes a
sprite for each codepoint the font actually has art for - a few thousand
files. At 64x64 that is roughly 16 KB apiece; drop --size if you want a
smaller set on disk.

Colors come out of the font's COLR/CPAL tables via Pillow's embedded_color,
which is the exact thing GDI refuses to do - hence the patch.

Transparency is 1-bit on purpose. The client's text surface is keyed on
#FF00FF, so a half-transparent edge pixel blends to *nearly* magenta and the
key then fails to remove it - which reads on screen as pink fringing and
stray magenta in areas that should be empty. Every pixel here is therefore
either fully opaque or fully clear, and clear pixels carry the key color.
Pass --threshold 0 to get graduated alpha back on a client that composites
per-pixel alpha properly.
"""
import argparse
import os
import struct
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

FONT = r"C:\Windows\Fonts\seguiemj.ttf"

# The client's transparency key, same as every other RO sprite.
KEY = (255, 0, 255)

# Where a glyph's own art lands exactly on the key, nudge it one step off so
# the client does not punch a hole through the middle of the emoji.
KEY_ALT = (254, 0, 254)

# Every block the stub's ISEMOJI accepts, and nothing else. A sprite outside
# these is dead weight - the patch never looks it up and the client draws the
# codepoint through GDI as usual. Keep in sync with emoji_stub_gen.py.
RANGES = [
    (0x2600, 0x27BF),      # Misc Symbols, Dingbats
    (0x2B00, 0x2BFF),      # Misc Symbols and Arrows
    (0x1F000, 0x1FAFF),    # Mahjong through Symbols and Pictographs Extended-A
]

# Codepoints inside RANGES that the font draws but that are meaningless alone:
# skin-tone modifiers only ever follow another emoji, so a standalone swatch
# sprite would replace text the client had drawn correctly.
SKIP = set(range(0x1F3FB, 0x1F400))


def font_codepoints(path):
    """Codepoints the font's cmap actually maps, from the file itself.

    Rendering a range blind is not an option: an unmapped codepoint comes out
    of the font as .notdef, which is a box with ink in it, so the alpha test in
    render() cannot tell it from a real glyph and every gap in a block would
    ship as a tofu sprite. Only formats 4 and 12 are handled - between them
    they cover the BMP and the astral planes in every emoji font in practice.
    """
    with open(path, "rb") as fh:
        raw = fh.read()

    if raw[:4] == b"ttcf":
        raw = raw[struct.unpack_from(">I", raw, 12)[0]:]

    tables = struct.unpack_from(">H", raw, 4)[0]
    cmap = None
    for i in range(tables):
        tag, _, off, _ = struct.unpack_from(">4sIII", raw, 12 + i * 16)
        if tag == b"cmap":
            cmap = off
            break
    if cmap is None:
        return None

    found = set()
    for i in range(struct.unpack_from(">H", raw, cmap + 2)[0]):
        sub = cmap + struct.unpack_from(">I", raw, cmap + 8 + i * 8)[0]
        fmt = struct.unpack_from(">H", raw, sub)[0]

        if fmt == 4:
            segs = struct.unpack_from(">H", raw, sub + 6)[0] // 2
            ends = sub + 14
            starts = ends + segs * 2 + 2
            for s in range(segs):
                lo = struct.unpack_from(">H", raw, starts + s * 2)[0]
                hi = struct.unpack_from(">H", raw, ends + s * 2)[0]
                if lo <= hi and hi != 0xFFFF:
                    found.update(range(lo, hi + 1))

        elif fmt == 12:
            for g in range(struct.unpack_from(">I", raw, sub + 12)[0]):
                lo, hi, _ = struct.unpack_from(">III", raw, sub + 16 + g * 12)
                found.update(range(lo, hi + 1))

    return found


def resize_glyph(img, target):
    """LANCZOS resize done in premultiplied space.

    A straight-alpha resize averages in the RGB of fully clear pixels, which
    for these fonts is black - that is where the dark rim around a shrunken
    emoji comes from. Premultiplying first weights each pixel by its own
    coverage, so only real color contributes.
    """
    src = np.asarray(img, dtype=np.uint32)
    alpha = src[..., 3:4]
    premul = (src[..., :3] * alpha + 127) // 255

    scaled = Image.fromarray(
        np.dstack([premul, alpha]).astype(np.uint8), "RGBA"
    ).resize(target, Image.LANCZOS)

    out = np.asarray(scaled, dtype=np.int32)
    alpha = out[..., 3:4]
    rgb = np.where(
        alpha > 0,
        np.clip(out[..., :3] * 255 // np.maximum(alpha, 1), 0, 255),
        0,
    )
    return Image.fromarray(np.dstack([rgb, alpha]).astype(np.uint8), "RGBA")


def key_out(img, threshold):
    """Force 1-bit transparency and paint the clear pixels with the key.

    Anything between clear and opaque is what breaks on a keyed surface: the
    client blends it against #FF00FF, the result is near-magenta rather than
    exactly the key, and the key test then leaves it on screen. Snapping alpha
    to 0 or 255 removes that middle ground entirely.
    """
    px = np.asarray(img).copy()
    if threshold > 0:
        opaque = px[..., 3] >= threshold
        px[..., 3] = np.where(opaque, 255, 0)
    else:
        opaque = px[..., 3] > 0

    clash = opaque & np.all(px[..., :3] == KEY, axis=-1)
    px[clash, :3] = KEY_ALT
    px[~opaque, :3] = KEY
    return Image.fromarray(px, "RGBA")


def render(cp, size, font, threshold=128):
    """Render one codepoint centered on a keyed size*size canvas.

    Returns None when the font has nothing to draw for it.
    """
    pad = size * 2
    scratch = Image.new("RGBA", (pad, pad), (0, 0, 0, 0))
    ImageDraw.Draw(scratch).text(
        (pad // 4, pad // 4), chr(cp), font=font, embedded_color=True
    )

    box = scratch.getchannel("A").getbbox()
    if box is None:
        return None

    glyph = scratch.crop(box)
    scale = min((size - 2) / glyph.width, (size - 2) / glyph.height)
    glyph = resize_glyph(
        glyph,
        (max(1, round(glyph.width * scale)), max(1, round(glyph.height * scale))),
    )

    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(glyph, ((size - glyph.width) // 2, (size - glyph.height) // 2))
    return key_out(out, threshold)


def verify(path, threshold):
    """Re-read a written BMP the way the patch's loader does.

    The loader takes byte 3 of every pixel as alpha straight out of the file,
    so this checks the bytes on disk rather than trusting what Pillow was
    handed - a partial-alpha pixel here is a magenta fringe in game.
    """
    with open(path, "rb") as fh:
        raw = fh.read()
    size = len(raw)

    if raw[:2] != b"BM":
        return "not a BMP"

    offbits = struct.unpack_from("<I", raw, 0x0A)[0]
    width = struct.unpack_from("<i", raw, 0x12)[0]
    height = struct.unpack_from("<i", raw, 0x16)[0]
    bits = struct.unpack_from("<H", raw, 0x1C)[0]
    compression = struct.unpack_from("<I", raw, 0x1E)[0]

    if bits != 32:
        return f"{bits}bpp, patch needs 32"
    if offbits < 0x36:
        return f"bfOffBits {offbits:#x} below 0x36"
    if offbits + width * abs(height) * 4 > size:
        return "pixel data runs past end of file"

    if threshold > 0:
        pixels = np.frombuffer(
            raw, dtype=np.uint8, count=width * abs(height) * 4, offset=offbits
        ).reshape(-1, 4)
        partial = np.count_nonzero((pixels[:, 3] != 0) & (pixels[:, 3] != 255))
        if partial:
            return f"{partial} pixels with partial alpha - will fringe magenta"
        clear = pixels[pixels[:, 3] == 0]
        if len(clear) and not np.all(clear[:, :3] == KEY[::-1]):
            return "clear pixels are not the #FF00FF key"

    return None, width, height, compression, offbits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="Applications", help="folder to create data\\emoji under")
    ap.add_argument("--size", type=int, default=64, help="sprite edge in pixels")
    ap.add_argument("--font", default=FONT)
    ap.add_argument("--add", default="", help="extra codepoints, comma separated hex")
    ap.add_argument(
        "--threshold", type=int, default=128,
        help="alpha cutoff for 1-bit transparency (0 keeps graduated alpha)",
    )
    args = ap.parse_args()

    if not os.path.exists(args.font):
        sys.exit(f"font not found: {args.font}")
    if not 8 <= args.size <= 512:
        sys.exit("--size must be between 8 and 512 (the patch rejects above 512)")
    if not 0 <= args.threshold <= 255:
        sys.exit("--threshold must be between 0 and 255")

    mapped = font_codepoints(args.font)
    if mapped is None:
        sys.exit(f"no usable cmap in {args.font}")

    wanted = [
        cp
        for lo, hi in RANGES
        for cp in range(lo, hi + 1)
        if cp in mapped and cp not in SKIP
    ]
    if not wanted:
        sys.exit(f"{args.font} maps no codepoints in the patch's emoji ranges")

    for tok in filter(None, (t.strip() for t in args.add.split(","))):
        wanted.append(int(tok, 16))

    outdir = os.path.join(args.out, "data", "emoji")
    os.makedirs(outdir, exist_ok=True)
    font = ImageFont.truetype(args.font, args.size)

    written, missing, bad, shapes = [], [], [], set()
    for cp in dict.fromkeys(wanted):
        img = render(cp, args.size, font, args.threshold)
        if img is None:
            missing.append(cp)
            continue

        path = os.path.join(outdir, f"{cp:X}.bmp")
        img.save(path)

        result = verify(path, args.threshold)
        if isinstance(result, str):
            bad.append((cp, result))
        else:
            shapes.add(result[1:])
            written.append(cp)

    print(f"wrote {len(written)} sprites to {outdir}")
    if shapes:
        for w, h, comp, off in sorted(shapes):
            kind = {0: "BI_RGB", 3: "BI_BITFIELDS"}.get(comp, f"compression {comp}")
            print(f"  header: {w}x{h} 32bpp {kind}, pixels at {off:#x}")
    if missing:
        print(f"no glyph in font ({len(missing)}): "
              + " ".join(f"{c:X}" for c in missing))
    if bad:
        print(f"REJECTED BY LOADER ({len(bad)}):")
        for cp, why in bad:
            print(f"  {cp:X}.bmp - {why}")

    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
