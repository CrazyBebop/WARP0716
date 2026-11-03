Character-creation hair thumbnails for kRO styles 24 to 45
==========================================================

WHAT THIS IS

kRO's data.grf ships hair SPRITES for styles 1 to 45, for both genders, but character-creation
thumbnails for only 1 to 23. Styles 24 to 45 therefore exist in the client and draw as blank cells
in the picker. These 44 files fill that gap: 22 male, 22 female.

They were generated from kRO's own hair sprites, so each thumbnail depicts the hair it is named
after by construction. Do not source thumbnail art from anywhere else. A pack found in the wild on
2026-08-14 numbered its files 24 to 46 but they were byte-identical copies of kRO's 23 down to 1 in
reverse, so page 2 of the picker showed page 1's art over completely different hair. A directory
listing showed 46 files and looked fine; hashing showed 23 distinct images.


HOW TO INSTALL

Copy the "data" folder in here into your RO client folder, merging with the "data" folder already
there. That is all. The destination is

    data\texture\<Korean UI folder>\make_character_ver2\

and the folder is already named correctly on disk here, so a plain copy puts the files in the right
place without you having to type a Korean path on a non-Korean Windows.

Alternatively repack them into your GRF at that same path.


WHAT ELSE HAS TO BE SET

Thumbnails alone are not enough. Three separate limits decide what the picker offers:

  1. WARP patch "IncrNewCharHairs", prompt "Hair Style Limit"
       How many styles character creation offers. Set it to 45 for this set.
       The ceiling is 128: the client compares the style index against a SIGN-EXTENDED byte, so 127
       is the largest value that works and the patch refuses anything higher.

  2. WARP patch "Allow65kHairs", prompt "Hair Style Limit"
       Highest style you ship sprites for. Styles above it fall back to style 1 rather than leaving
       the character headless. Must be at least as high as the picker limit.

  3. Server, conf/import/battle_conf.txt
       max_hair_style must be at least as high as the picker limit.


HOW THE PAGES WORK

The grid is 24 buttons, 4 columns by 6 rows. The first 23 are hairstyles and the 24th is the page
button, which advances and wraps round to the first page.

    page 1 -> styles   1 to  23
    page 2 -> styles  24 to  46
    page 3 -> styles  47 to  69
    page 4 -> styles  70 to  92
    page 5 -> styles  93 to 115
    page 6 -> styles 116 to 128

Cell N on page P is style P*23 + N, counting P from zero. Filenames follow the STYLE number, not
the page: there is no per-page naming.

    img_hairstyle<NN>.bmp         male
    img_hairstyle_girl<NN>.bmp    female

A page is always 23 cells wide, so unless your limit is an exact multiple of 23 the last page ends
with cells that have no style behind them. Those cells are inert.


ADDING MORE STYLES OF YOUR OWN

Every style you offer needs all three of these, or you get the failure next to it:

    sprite      missing -> the loader pops "file not found" and the character is left headless
    thumbnail   missing -> the cell is blank, though it still selects and still works
    palettes    missing -> no hair colour for that style

Generate thumbnails for your own sprites with the tool that made these:

    python make_hair_thumbnails.py --range 46-95 --sex both \
        --loose <your sprite dir> --palettes <your palette dir> --out <dir>

It cuts the face out of the head sprite by diffing that style's colour palettes against each other,
because the palette slots that change between hair colours are the hair and everything else is skin.
With no palettes it cannot do that, and it says so rather than quietly writing thumbnails with faces
on them.


FILE FORMAT

36 x 37, 24-bit BMP, magenta FF00FF as the transparent colour. kRO's own numbered thumbnails carry
two stray trailing bytes and a biSizeImage two larger than the pixel data; the clean 4050-byte form
these use is what kRO's own img_hairstyle_none.bmp does, and the client reads both.
