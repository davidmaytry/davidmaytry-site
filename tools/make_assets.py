"""Copies the studio's brand art into this site as small web files.

Sources are only READ (never changed, moved or deleted):
  - the owner's originals:  D:/Important/Games/DavidMayTry/
  - the shorts brand kit:   C:/Projects/media/postkit/brand/ and postkit/stickers/

Run from the repo root:  python tools/make_assets.py
Needs Pillow, fontTools and brotli (pip install pillow fonttools brotli).
"""
import io
import math
import os
import random
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


# ---------- social icons: drawn here, in the stickers' look ----------
# Each network's own silhouette (Clyde, valve, play button, Snoo, X, camera, note), but in thick black marker with flat
# fills from the site's palette, the way the shorts' stickers are drawn. The paper plate behind each icon is
# the page's own hand-drawn outline (main.js), so these PNGs are the glyph only, with "paper" parts left
# transparent: the plate shows through, cream or white, in either theme.

SOCIAL = os.path.join(OUT, "social")
S4 = 768                      # drawn 4x, saved at 192 px
INK = (17, 17, 17, 255)
CLEAR = (0, 0, 0, 0)          # "paper": cut out, the plate shows through
PINK, CYAN, LILAC = (255, 92, 154, 255), (11, 178, 221, 255), (162, 116, 240, 255)
MARKER = 34                   # marker width at 4x (~8.5 px at 192)


def _wobble(pts, amp, seed):
    """Bends a closed outline a little, like a line drawn by hand: a few slow waves along its length."""
    rnd = random.Random(seed)
    waves = [(rnd.choice([2, 3, 4, 5]), rnd.uniform(0, 6.283), rnd.uniform(.5, 1)) for _ in range(3)]
    n = len(pts)
    out = []
    for i, (x, y) in enumerate(pts):
        t = i / n * 6.283
        dx = sum(a * math.sin(f * t + p) for f, p, a in waves) * amp / 2
        dy = sum(a * math.cos(f * t + p * 1.7) for f, p, a in waves) * amp / 2
        out.append((x + dx, y + dy))
    return out


def _ellipse(cx, cy, rx, ry=None, n=120):
    ry = rx if ry is None else ry
    return [(cx + rx * math.cos(i / n * 6.283), cy + ry * math.sin(i / n * 6.283)) for i in range(n)]


def _rrect(x0, y0, x1, y1, r, n=16):
    pts = []
    for cx, cy, a0 in [(x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)]:
        for k in range(n + 1):
            a = math.radians(a0 + 90 * k / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return _dense(pts)


def _dense(pts, step=12):
    """Adds points along straight sides so the wobble can bend them too."""
    out = []
    for i, a in enumerate(pts):
        b = pts[(i + 1) % len(pts)]
        k = max(1, int(math.hypot(b[0] - a[0], b[1] - a[1]) / step))
        out += [(a[0] + (b[0] - a[0]) * j / k, a[1] + (b[1] - a[1]) * j / k) for j in range(k)]
    return out


def _bez(p0, p1, p2, n=24):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
             (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]) for t in (i / n for i in range(n + 1))]


def _part(d, pts, fill, seed, amp=7, line=MARKER):
    """One flat piece: fill, then the marker line over its edge."""
    pts = _wobble(pts, amp, seed)
    d.polygon(pts, fill=fill)
    if line:
        _brush(d, pts + pts[:1], line)


def _brush(d, pts, width):
    """A round felt tip dragged along the points: a dab every few pixels, so joins and ends are round."""
    r = width / 2
    for i in range(len(pts) - 1):
        (ax, ay), (bx, by) = pts[i], pts[i + 1]
        k = max(1, int(math.hypot(bx - ax, by - ay) / 4))
        for j in range(k + 1):
            x, y = ax + (bx - ax) * j / k, ay + (by - ay) * j / k
            d.ellipse((x - r, y - r, x + r, y + r), fill=INK)


def _stroke(d, pts, width=MARKER):
    _brush(d, pts, width)


def _cubic(p0, p1, p2, p3, n=32):
    return [tuple((1 - t) ** 3 * a + 3 * (1 - t) ** 2 * t * b + 3 * (1 - t) * t * t * c + t ** 3 * e
                  for a, b, c, e in zip(p0, p1, p2, p3)) for t in (i / n for i in range(n + 1))]


def _discord(d):
    """Clyde, the gamepad-face, after the official outline (127 x 96 units) scaled into the icon."""
    k, ox, oy = 5.2, 54, 134
    u = lambda x, y: (ox + x * k, oy + y * k)
    shape = (_bez(u(19.4, 8.1), u(32, 2.5), u(45.6, 0)) + [u(49, 6.8), u(63.5, 5.7), u(78.1, 6.8)]   # horns, brow
             + _bez(u(81.5, 0), u(95, 2.5), u(107.7, 8.1))
             + _cubic(u(107.7, 8.1), u(122.1, 29.1), u(129.2, 52.8), u(126.6, 80.2))              # right cheek
             + _bez(u(126.6, 80.2), u(112, 91), u(94.4, 96.4))
             + _bez(u(87.5, 84.5), u(63.6, 90), u(39.6, 84.5))                                     # feet, chin
             + _bez(u(32.7, 96.4), u(15, 91), u(0.5, 80.2))
             + _cubic(u(0.5, 80.2), u(-1.7, 56.6), u(2.8, 32.7), u(19.4, 8.1)))                    # left cheek
    _part(d, _dense(shape), LILAC, 61)
    _part(d, _ellipse(*u(42.4, 53), 11.6 * k, 12.9 * k), CLEAR, 62, amp=3, line=26)                # eyes
    _part(d, _ellipse(*u(84.7, 53), 11.6 * k, 12.9 * k), CLEAR, 63, amp=3, line=26)


def _steam(d):
    """The valve: a disk with a crank, the rod running out through the disk's edge to the paper."""
    cx, cy, R = 384, 384, 340
    _part(d, _ellipse(cx, cy, R), CYAN, 71)
    sx, sy = 292, 508                               # small joint (crank pin)
    gx, gy = 502, 290                               # the big wheel
    # rod: from the pin out to the lower-left edge; its fill erases the disk's line there, so it opens to paper
    ux, uy = -0.92, 0.39
    nx, ny = -uy, ux
    def hit(px, py):                                # where a ray along the rod leaves the disk
        b = (px - cx) * ux + (py - cy) * uy
        c = (px - cx) ** 2 + (py - cy) ** 2 - R * R
        t = -b + math.sqrt(b * b - c)
        return px + ux * t, py + uy * t
    w0, w1 = 58, 74                                 # a little wider where it leaves the disk
    a0, b0 = (sx + nx * w0, sy + ny * w0), (sx - nx * w0, sy - ny * w0)
    a1 = hit(sx + nx * w1, sy + ny * w1)
    b1 = hit(sx - nx * w1, sy - ny * w1)
    far = lambda p: (p[0] + ux * 60, p[1] + uy * 60)
    d.polygon([a0, a1, far(a1), far(b1), b1, b0], fill=CLEAR)
    _stroke(d, _dense([a0, a1])[:-1] + [a1])
    _stroke(d, _dense([b0, b1])[:-1] + [b1])
    # arm from the pin to the wheel, wider at the wheel
    vx, vy = gx - sx, gy - sy
    L = math.hypot(vx, vy)
    vx, vy = vx / L, vy / L
    px, py = -vy, vx
    _part(d, _dense([(sx + px * 50, sy + py * 50), (gx + px * 92, gy + py * 92),
                     (gx - px * 92, gy - py * 92), (sx - px * 50, sy - py * 50)]), CLEAR, 72, amp=4)
    _part(d, _ellipse(sx, sy, 88), CLEAR, 73, amp=3)
    _part(d, _ellipse(sx, sy, 38), CYAN, 74, amp=2, line=22)
    _part(d, _ellipse(gx, gy, 132), CLEAR, 75, amp=4)
    _part(d, _ellipse(gx, gy, 68), CYAN, 76, amp=3, line=24)


def _youtube(d):
    _part(d, _rrect(60, 168, 708, 600, 150), PINK, 11)
    _part(d, _dense([(306, 252), (306, 516), (536, 384)]), CLEAR, 12, amp=4)


def _reddit(d):
    _part(d, _ellipse(384, 384, 340), CYAN, 21)
    _stroke(d, [(392, 300), (424, 178), (500, 196)])               # antenna
    _part(d, _ellipse(536, 196, 46), CLEAR, 22, amp=3)
    _part(d, _ellipse(196, 368, 62), CLEAR, 23, amp=3)              # ears, behind the head
    _part(d, _ellipse(572, 368, 62), CLEAR, 24, amp=3)
    _part(d, _ellipse(384, 452, 222, 152), CLEAR, 25, amp=5)        # head
    _part(d, _ellipse(302, 430, 40), PINK, 26, amp=2, line=22)      # eyes
    _part(d, _ellipse(466, 430, 40), PINK, 27, amp=2, line=22)
    _stroke(d, _bez((298, 512), (384, 566), (470, 512)), width=26)  # smile


def _x(d):
    _stroke(d, [(160, 640), (606, 128)], width=58)                  # the thin "/"
    _part(d, _dense([(120, 118), (300, 118), (648, 650), (468, 650)]), CLEAR, 31, amp=5)  # the hollow "\"


def _instagram(d):
    _part(d, _rrect(84, 84, 684, 684, 190), LILAC, 41)
    _part(d, _ellipse(384, 396, 150), CLEAR, 42, amp=4)             # lens
    _part(d, _ellipse(554, 212, 40), PINK, 43, amp=2, line=24)      # flash dot


def _tiktok(d, img):
    """The note in black over a cyan copy (up-left) and a pink one (down-right), as in the logo."""
    def note(off):
        m = Image.new("L", (S4, S4), 0)
        md = ImageDraw.Draw(m)
        ox, oy = off
        sh = lambda pts: [(x + ox, y + oy) for x, y in pts]
        md.polygon(sh(_wobble(_ellipse(318, 520, 158), 5, 51)), fill=255)          # bowl
        md.polygon(sh(_wobble(_ellipse(318, 520, 72), 4, 52)), fill=0)             # its hole
        md.polygon(sh(_wobble(_dense([(400, 110), (476, 110), (476, 540), (400, 540)]), 4, 53)), fill=255)  # stem
        flag = _bez((476, 110), (500, 236), (640, 250)) + _bez((640, 340), (536, 330), (476, 274))
        md.polygon(sh(_wobble(flag, 3, 54)), fill=255)
        return m
    k = 46
    for color, off in [(CYAN, (-k, -k * .8)), (PINK, (k, k * .8)), (INK, (0, 0))]:
        img.paste(Image.new("RGBA", (S4, S4), color), (0, 0), note(off))


def social_icons():
    os.makedirs(SOCIAL, exist_ok=True)
    for name, fn in [("discord", _discord), ("steam", _steam), ("youtube", _youtube), ("reddit", _reddit), ("x", _x),
                     ("instagram", _instagram), ("tiktok", _tiktok)]:
        img = Image.new("RGBA", (S4, S4), CLEAR)
        d = ImageDraw.Draw(img)
        if name == "tiktok":
            fn(d, img)
        else:
            fn(d)
        img = img.resize((192, 192), Image.LANCZOS)
        img.save(os.path.join(SOCIAL, f"{name}.png"), optimize=True)   # no text chunks: no paths, no names


if __name__ == "__main__":
    import sys
    if sys.argv[1:] == ["social"]:          # only the social icons; the brand art stays as it is
        social_icons()
        sys.exit()
    stickers()
    icons()
    og()
    fonts()
    social_icons()
    for base, _, files in os.walk(OUT):
        for f in sorted(files):
            p = os.path.join(base, f)
            print(f"{os.path.getsize(p) / 1024:8.1f} KB  {os.path.relpath(p, ROOT)}")
