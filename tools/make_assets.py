"""Copies the studio's brand art into this site as small web files.

Sources are only READ (never changed, moved or deleted):
  - the owner's originals:  D:/Important/Games/DavidMayTry/
  - the shorts brand kit:   C:/Projects/media/postkit/brand/ and postkit/stickers/

Run from the repo root:  python tools/make_assets.py
Needs Pillow, fontTools and brotli (pip install pillow fonttools brotli).
"""
import io
import os
import shutil

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OWNER = "D:/Important/Games/DavidMayTry"
KIT = "C:/Projects/media/postkit"
ICON = f"{OWNER}/david_may_try_icon_1024.png"

OUT = os.path.join(ROOT, "assets")
BRAND = os.path.join(OUT, "brand")
FONTS = os.path.join(OUT, "fonts")


def webp(src, dst, width):
    im = Image.open(src).convert("RGBA")
    if im.width > width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    im.save(os.path.join(BRAND, dst), "WEBP", quality=88, method=6)


def stickers():
    os.makedirs(BRAND, exist_ok=True)
    # the logo: head (dark theme keeps the white sticker border, light theme has none) + wordmark per theme
    webp(f"{KIT}/brand/logo/head_color.png", "head-dark.webp", 720)
    webp(f"{KIT}/stickers/cut_light/head_color.png", "head-light.webp", 720)
    webp(f"{KIT}/brand/logo/wordmark_white.png", "wordmark-white.webp", 1000)
    webp(f"{KIT}/brand/logo/wordmark_black.png", "wordmark-black.webp", 1000)
    # the boy next to the games: the author's own faces and hands
    for name, w in [("face_tongue", 420), ("face_suspicious", 420), ("face_smile", 420),
                    ("hand_point", 260), ("icon_hourglass", 240)]:
        webp(f"{KIT}/stickers/cut/{name}.png", f"{name.replace('_', '-')}-dark.webp", w)
        webp(f"{KIT}/stickers/cut_light/{name}.png", f"{name.replace('_', '-')}-light.webp", w)


def cut_out(icon):
    """The icon without its white paper: flood the white from the corners, keep the white inside the drawing
    (eyes, teeth, glasses), then trim to the head and pad to a square."""
    rgb = icon.convert("RGB")
    w, h = rgb.size
    mask = Image.new("L", (w, h), 0)
    seen = rgb.copy()
    for x, y in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]:
        ImageDraw.floodfill(seen, (x, y), (255, 0, 255), thresh=60)
    px, mp = seen.load(), mask.load()
    for y in range(h):
        for x in range(w):
            if px[x, y] != (255, 0, 255):
                mp[x, y] = 255
    out = icon.convert("RGBA")
    out.putalpha(mask)
    out = out.crop(out.getbbox())
    side = max(out.size) + max(out.size) // 24
    sq = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    sq.paste(out, ((side - out.width) // 2, (side - out.height) // 2), out)
    return sq


def icons():
    icon = Image.open(ICON).convert("RGBA")
    clear = cut_out(icon)
    # iOS paints a transparent home-screen icon black, so the touch icon keeps the white paper
    icon.resize((180, 180), Image.LANCZOS).convert("RGB").save(os.path.join(OUT, "apple-touch-icon.png"), optimize=True)
    clear.resize((192, 192), Image.LANCZOS).save(os.path.join(OUT, "icon-192.png"), optimize=True)
    clear.resize((512, 512), Image.LANCZOS).save(os.path.join(OUT, "icon-512.png"), optimize=True)
    clear.save(os.path.join(ROOT, "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48)])


def og():
    """1200x630 link preview: the icon as a tilted paper sticker + the wordmark on cream paper."""
    W, H = 1200, 630
    cream, ink = (246, 238, 223, 255), (17, 17, 17, 255)
    img = Image.new("RGBA", (W, H), cream)

    s = 440
    card = Image.new("RGBA", (s + 40, s + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    d.rounded_rectangle((8, 8, s + 31, s + 31), radius=34, fill=(255, 255, 255, 255), outline=ink, width=9)
    face = Image.open(ICON).convert("RGBA").resize((s - 20, s - 20), Image.LANCZOS)
    card.alpha_composite(face, (30, 30))
    card = card.rotate(4, resample=Image.BICUBIC, expand=True)
    img.alpha_composite(card, (70, (H - card.height) // 2))

    wm = Image.open(f"{KIT}/brand/logo/wordmark_black.png").convert("RGBA")
    wm = wm.resize((600, round(wm.height * 600 / wm.width)), Image.LANCZOS)
    img.alpha_composite(wm, (560, 150))

    font = ImageFont.truetype(f"{KIT}/brand/fonts/GochiHand.ttf", 58)
    line = Image.new("RGBA", (660, 100), (0, 0, 0, 0))
    ImageDraw.Draw(line).text((0, 10), "cozy multiplayer games", font=font, fill=ink)
    line = line.rotate(3, resample=Image.BICUBIC, expand=True)
    img.alpha_composite(line, (585, 400))
    img.convert("RGB").save(os.path.join(OUT, "og-image.png"), optimize=True)


def fonts():
    """The two faces the shorts use (Shantell Sans for text, Gochi Hand for notes) as woff2.

    Shantell Sans has no Reserved Font Name, so it is cut down to Latin. Gochi Hand has one ("Gochi",
    "Gochi Hand"), so it is only repacked as woff2 with every glyph kept, not subset.
    """
    from fontTools import subset
    from fontTools.ttLib import TTFont

    os.makedirs(FONTS, exist_ok=True)
    latin = "U+0020-007E,U+00A0-00FF,U+0131,U+0152-0153,U+02C6,U+02DA,U+02DC,U+2013-2014,U+2018-201E,U+2022,U+2026,U+20AC,U+2122"
    font = TTFont(f"{KIT}/brand/fonts/ShantellSans.ttf")
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = ["*"]
    opts.unicodes = subset.parse_unicodes(latin)
    sub = subset.Subsetter(opts)
    sub.populate(unicodes=opts.unicodes)
    sub.subset(font)
    font.flavor = "woff2"
    font.save(os.path.join(FONTS, "ShantellSans-latin.woff2"))

    font = TTFont(f"{KIT}/brand/fonts/GochiHand.ttf")
    font.flavor = "woff2"
    font.save(os.path.join(FONTS, "GochiHand.woff2"))

    write_licenses()


def write_licenses():
    """Brand LICENSES.txt holds the Shantell Sans OFL; Gochi Hand's notice comes from its own OFL.txt."""
    bar = "=" * 60
    parts = [
        "Fonts on this site",
        "==================",
        "",
        "ShantellSans-latin.woff2  Shantell Sans, cut down to Latin characters",
        "GochiHand.woff2           Gochi Hand, repacked as woff2, glyphs unchanged",
        "",
        "Both are licensed under the SIL Open Font License, Version 1.1 (full text below).",
        "",
        bar, "Shantell Sans", bar, "",
        open(f"{KIT}/brand/fonts/LICENSES.txt", encoding="utf-8").read().strip(),
        "",
        bar, "Gochi Hand", bar, "",
        open(f"{KIT}/brand/fonts/candidates/gochihand/OFL.txt", encoding="utf-8").read().strip(),
        "",
    ]
    with open(os.path.join(FONTS, "LICENSES.txt"), "w", encoding="utf-8", newline="\n") as out:
        out.write("\n".join(parts))


if __name__ == "__main__":
    stickers()
    icons()
    og()
    fonts()
    for base, _, files in os.walk(OUT):
        for f in sorted(files):
            p = os.path.join(base, f)
            print(f"{os.path.getsize(p) / 1024:8.1f} KB  {os.path.relpath(p, ROOT)}")
