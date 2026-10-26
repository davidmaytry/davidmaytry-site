# Draws the studio mark (same geometry as assets/mark.svg, a "d" made of a
# ring and a stem, no font) into favicon.ico and assets/apple-touch-icon.png.
# Run from the repo root: python tools/make_icons.py
from PIL import Image, ImageDraw

ACCENT = (255, 122, 69, 255)
INK = (22, 19, 15, 255)


def mark(px, rounded=True):
    s = 16  # supersample
    k = px * s / 64.0
    im = Image.new("RGBA", (px * s, px * s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if rounded:
        d.rounded_rectangle([0, 0, px * s - 1, px * s - 1], radius=14 * k, fill=ACCENT)
    else:
        d.rectangle([0, 0, px * s, px * s], fill=ACCENT)
    # ring: centre (32, 38), r 10, stroke 7 -> outer 13.5, inner 6.5
    cx, cy = 32 * k, 38 * k
    ro, ri = 13.5 * k, 6.5 * k
    d.ellipse([cx - ro, cy - ro, cx + ro, cy + ro], fill=INK)
    d.ellipse([cx - ri, cy - ri, cx + ri, cy + ri], fill=ACCENT)
    # stem: x 38.5..45.5, y 13..51.5
    d.rounded_rectangle([38.5 * k, 13 * k, 45.5 * k, 51.5 * k], radius=1 * k, fill=INK)
    return im.resize((px, px), Image.LANCZOS)


mark(180, rounded=False).convert("RGB").save("assets/apple-touch-icon.png", optimize=True)
big = mark(256)
big.save("favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
mark(512).save("tools/mark-512.png")
print("ok")
