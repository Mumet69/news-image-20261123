#!/usr/bin/env python3
"""Render the news-image-20261123 entry: one image summing up the world news
of Monday 23 November 2026.

Layout (1024 x 1024, broadsheet front page):
  - masthead with the date (the judge must see which day this is)
  - hero illustration: tankers burning in the Strait of Hormuz
  - "also today" strip: Mercury, MotoGP, Taiwan markets
  - 2x2 story grid: COP31 collapse, Russian missiles in Poland,
    Kyiv apartment strike, Trump-Xi-Putin trilateral

Run: python3 render.py  -> writes entry.png next to this file.
Deterministic: no network, no randomness, no timestamps.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W = H = 1024

NAVY = (12, 27, 46)
NAVY2 = (18, 38, 62)
GOLD = (201, 162, 39)
CREAM = (247, 243, 234)
PAPER = (251, 248, 241)
INK = (16, 24, 38)
GREY = (74, 84, 96)
WHITE = (255, 255, 255)

SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def vgrad(draw, box, top, bottom):
    """Vertical gradient inside box (x0, y0, x1, y1)."""
    x0, y0, x1, y1 = box
    span = max(1, y1 - y0)
    for y in range(y0, y1):
        t = (y - y0) / span
        c = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        draw.line([(x0, y), (x1, y)], fill=c)


def wrap(draw, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def tracked(draw, cx, y, text, fnt, fill, tracking=2):
    """Draw centred text with letter tracking."""
    widths = [draw.textlength(ch, font=fnt) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = cx - total / 2
    for ch, w in zip(text, widths):
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += w + tracking


def flame_layer(size, flames):
    """flames: list of (cx, base_y, w, h, colour). Returns blurred RGBA layer.
    Each flame is a union of stacked ellipses plus a pointed tip."""
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for cx, base_y, w, h, col in flames:
        d.ellipse([cx - w * 0.45, base_y - h * 0.55,
                   cx + w * 0.45, base_y + h * 0.05], fill=col)
        d.ellipse([cx - w * 0.32, base_y - h * 0.83,
                   cx + w * 0.32, base_y - h * 0.27], fill=col)
        d.ellipse([cx - w * 0.16, base_y - h * 1.02,
                   cx + w * 0.16, base_y - h * 0.58], fill=col)
        d.polygon([(cx - w * 0.12, base_y - h * 0.85),
                   (cx + w * 0.12, base_y - h * 0.85),
                   (cx + w * 0.05, base_y - h * 1.05)], fill=col)
    return layer.filter(ImageFilter.GaussianBlur(2))


def smoke_layer(size, puffs):
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for cx, cy, rx, ry, col in puffs:
        d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=col)
    return layer.filter(ImageFilter.GaussianBlur(10))


def draw_masthead(img):
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 108], fill=NAVY)
    d.line([(0, 106), (W, 106)], fill=GOLD, width=3)
    f_small = font(SANS_B, 23)
    tracked(d, W // 2, 16, "THE WORLD IN ONE PICTURE", f_small, GOLD, tracking=6)
    f_date = font(SERIF_B, 54)
    d.text((W // 2, 44), "MONDAY 23 NOVEMBER 2026", font=f_date,
           fill=WHITE, anchor="ma")


def draw_hero(img):
    """Dusk strait scene with a burning tanker, y 108..448."""
    d = ImageDraw.Draw(img)
    top, horizon = 108, 360
    vgrad(d, (0, top, W, horizon), (26, 28, 58), (122, 48, 32))
    vgrad(d, (0, horizon, W, 448), (232, 122, 38), (250, 178, 92))
    # sun low on the horizon
    d.ellipse([742, 318, 806, 382], fill=(245, 214, 122))
    d.ellipse([748, 324, 800, 376], fill=(252, 232, 160))
    # sea
    vgrad(d, (0, horizon, W, 448), (16, 52, 62), (10, 30, 40))
    for yy, alpha in ((378, 90), (398, 70), (420, 55), (438, 40)):
        d.line([(60, yy), (964, yy)], fill=(214, 164, 96), width=2)
    # fire reflection streaks under the flames
    refl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rd = ImageDraw.Draw(refl)
    for x, w in ((330, 90), (400, 130), (470, 80)):
        rd.rectangle([x, horizon + 4, x + w, 446], fill=(240, 130, 40, 110))
    img.paste(Image.alpha_composite(img.convert("RGBA"),
              refl.filter(ImageFilter.GaussianBlur(6))).convert("RGB"), (0, 0))
    d = ImageDraw.Draw(img)

    # tanker silhouette: hull, deck, superstructure, funnel
    d.polygon([(120, 402), (900, 402), (872, 440), (150, 440)], fill=(8, 9, 12))
    d.rectangle([120, 398, 900, 404], fill=(8, 9, 12))
    for x in range(170, 620, 62):
        d.rectangle([x, 372, x + 46, 398], fill=(14, 15, 20))
    d.rectangle([640, 330, 762, 398], fill=(10, 11, 15))
    for yy in (344, 362, 380):
        for xx in (652, 682, 712, 742):
            d.rectangle([xx, yy, xx + 16, yy + 10], fill=(240, 190, 90))
    d.rectangle([790, 348, 822, 398], fill=(10, 11, 15))
    d.rectangle([790, 348, 822, 356], fill=(150, 40, 30))

    # flames rising from midship
    flames = [
        (330, 402, 70, 130, (240, 90, 20, 235)),
        (395, 402, 110, 175, (248, 140, 30, 235)),
        (455, 402, 90, 150, (245, 110, 25, 235)),
        (520, 402, 55, 105, (240, 95, 20, 235)),
        (395, 402, 55, 110, (252, 205, 80, 240)),
        (450, 402, 45, 90, (255, 225, 120, 240)),
    ]
    img.paste(Image.alpha_composite(img.convert("RGBA"),
              flame_layer((W, H), flames)).convert("RGB"), (0, 0))
    # smoke drifting right
    puffs = [
        (380, 250, 70, 34, (140, 138, 145, 130)),
        (470, 210, 95, 42, (130, 128, 135, 120)),
        (590, 175, 110, 46, (120, 118, 125, 110)),
        (720, 150, 120, 48, (112, 110, 118, 100)),
        (850, 132, 120, 46, (105, 103, 110, 90)),
    ]
    img.paste(Image.alpha_composite(img.convert("RGBA"),
              smoke_layer((W, H), puffs)).convert("RGB"), (0, 0))
    d = ImageDraw.Draw(img)

    # naval mine in the foreground water
    mx, my, r = 888, 424, 16
    d.ellipse([mx - r, my - r, mx + r, my + r], fill=(5, 6, 8))
    for k in range(8):
        a = math.pi * 2 * k / 8
        x1 = mx + int((r - 2) * math.cos(a))
        y1 = my + int((r - 2) * math.sin(a))
        x2 = mx + int((r + 12) * math.cos(a))
        y2 = my + int((r + 12) * math.sin(a))
        d.line([(x1, y1), (x2, y2)], fill=(5, 6, 8), width=4)
    d.ellipse([mx - 5, my - 5, mx + 5, my + 5], fill=(120, 60, 40))

    # headline band
    d.rectangle([0, 448, W, 548], fill=NAVY2)
    d.line([(0, 448), (W, 448)], fill=GOLD, width=3)
    f_head = font(SERIF_B, 40)
    d.text((W // 2, 456), "TANKERS BURN IN THE STRAIT OF HORMUZ",
           font=f_head, fill=WHITE, anchor="ma")
    f_sub = font(SANS, 21)
    d.text((W // 2, 506), "Three tankers struck, two more hit mines — the war widens",
           font=f_sub, fill=(214, 222, 232), anchor="ma")
    d.text((W // 2, 526), "to Saudi Arabia and Bahrain",
           font=f_sub, fill=(214, 222, 232), anchor="ma")


def draw_also(img):
    d = ImageDraw.Draw(img)
    d.rectangle([0, 548, W, 592], fill=CREAM)
    d.line([(0, 548), (W, 548)], fill=NAVY, width=1)
    d.line([(0, 591), (W, 591)], fill=NAVY, width=1)
    text = ("ALSO TODAY — BepiColombo reaches Mercury · Marquez takes 8th MotoGP "
            "crown · Taiwan stocks plunge 17.5% in a week")
    size = 18
    while size > 12:
        f = font(SANS_B, size)
        if d.textlength(text, font=f) <= W - 24:
            break
        size -= 1
    d.text((W // 2, 561), text, font=f, fill=NAVY, anchor="ma")


def icon_globe(d, x, y, s):
    d.ellipse([x, y, x + s, y + s], outline=WHITE, width=5)
    d.ellipse([x + s * 0.28, y + 4, x + s * 0.72, y + s - 4], outline=WHITE, width=4)
    d.line([(x + 4, y + s * 0.5), (x + s - 4, y + s * 0.5)], fill=WHITE, width=4)
    d.line([(x + s * 0.5, y + 4), (x + s * 0.5, y + s - 4)], fill=WHITE, width=4)
    # crack
    d.line([(x + s * 0.55, y + s * 0.1), (x + s * 0.45, y + s * 0.4),
            (x + s * 0.6, y + s * 0.55), (x + s * 0.42, y + s * 0.9)],
           fill=GOLD, width=5)


def icon_missile(d, x, y, s):
    # diagonal missile on its own layer, rotated
    lay = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    ld.polygon([(s * 0.5, s * 0.08), (s * 0.62, s * 0.30), (s * 0.62, s * 0.78),
                (s * 0.5, s * 0.92), (s * 0.38, s * 0.78), (s * 0.38, s * 0.30)],
               fill=WHITE)
    ld.polygon([(s * 0.38, s * 0.62), (s * 0.16, s * 0.86), (s * 0.38, s * 0.80)],
               fill=WHITE)
    ld.polygon([(s * 0.62, s * 0.62), (s * 0.84, s * 0.86), (s * 0.62, s * 0.80)],
               fill=WHITE)
    ld.polygon([(s * 0.5, s * 0.92), (s * 0.58, s * 1.0), (s * 0.42, s * 1.0)],
               fill=(255, 190, 60))
    lay = lay.rotate(45, resample=Image.BICUBIC, center=(s / 2, s / 2))
    return lay


def icon_building(d, x, y, s):
    d.rectangle([x + s * 0.12, y + s * 0.30, x + s * 0.88, y + s * 0.92],
                outline=WHITE, width=5)
    for r in range(3):
        for c in range(4):
            wx = x + s * (0.22 + c * 0.18)
            wy = y + s * (0.40 + r * 0.17)
            d.rectangle([wx, wy, wx + s * 0.09, wy + s * 0.09], fill=WHITE)
    d.line([(x + s * 0.12, y + s * 0.30), (x + s * 0.40, y + s * 0.12),
            (x + s * 0.62, y + s * 0.24), (x + s * 0.88, y + s * 0.10)],
           fill=WHITE, width=5)
    d.line([(x + s * 0.55, y + s * 0.30), (x + s * 0.45, y + s * 0.55),
            (x + s * 0.60, y + s * 0.72)], fill=GOLD, width=4)


def icon_flags(d, x, y, s):
    # three small flags on poles: USA, China, Russia
    poles = [x + s * 0.20, x + s * 0.50, x + s * 0.80]
    specs = [
        ([(200, 40, 40), (255, 255, 255), (30, 60, 130)], "us"),
        ([(220, 30, 30)], "cn"),
        ([(255, 255, 255), (30, 90, 200), (210, 30, 30)], "ru"),
    ]
    for px, (stripes, _k) in zip(poles, specs):
        d.line([(px, y + s * 0.12), (px, y + s * 0.92)], fill=WHITE, width=4)
        fw, fh = s * 0.26, s * 0.20
        fy = y + s * 0.14
        if _k == "us":
            for i, c in enumerate([(200, 40, 40), (255, 255, 255), (200, 40, 40),
                                   (255, 255, 255), (200, 40, 40)]):
                d.rectangle([px, fy + i * fh / 5, px + fw, fy + (i + 1) * fh / 5], fill=c)
            d.rectangle([px, fy, px + fw * 0.45, fy + fh * 0.5], fill=(30, 60, 130))
        elif _k == "cn":
            d.rectangle([px, fy, px + fw, fy + fh], fill=(220, 30, 30))
            d.ellipse([px + 4, fy + 4, px + 12, fy + 12], fill=(255, 220, 60))
        else:
            for i, c in enumerate(stripes):
                d.rectangle([px, fy + i * fh / 3, px + fw, fy + (i + 1) * fh / 3], fill=c)


STORIES = [
    ("COP31 COLLAPSES",
     "Climate talks fail after record overtime on fossil fuels",
     (15, 91, 77), "globe"),
    ("RUSSIAN MISSILES CONFIRMED IN POLAND",
     "Three cruise missiles fell on Friday; NATO to meet",
     (122, 31, 31), "missile"),
    ("DRONE HITS KYIV APARTMENT BLOCK",
     "2 killed, 11 missing — two of them children",
     (39, 65, 86), "building"),
    ("TRUMP, XI AND PUTIN MEET",
     "First-ever trilateral ends with a 4-point declaration",
     (74, 42, 90), "flags"),
]


def draw_grid(img):
    d = ImageDraw.Draw(img)
    top = 592
    cell_w, cell_h = W // 2, (H - top) // 2
    f_sub = font(SANS, 19)
    for i, (head, sub, bg, kind) in enumerate(STORIES):
        cx = (i % 2) * cell_w
        cy = top + (i // 2) * cell_h
        d.rectangle([cx, cy, cx + cell_w, cy + cell_h], fill=PAPER)
        # icon panel
        iw = 150
        d.rectangle([cx, cy, cx + iw, cy + cell_h], fill=bg)
        pad = 26
        if kind == "globe":
            icon_globe(d, cx + pad, cy + (cell_h - 98) // 2, 98)
        elif kind == "building":
            icon_building(d, cx + pad, cy + (cell_h - 98) // 2, 98)
        elif kind == "flags":
            icon_flags(d, cx + pad - 8, cy + (cell_h - 98) // 2, 116)
        elif kind == "missile":
            lay = icon_missile(d, 0, 0, 110)
            img.paste(lay, (cx + 20, cy + (cell_h - 110) // 2), lay)
            d = ImageDraw.Draw(img)
        # text: shrink headline until it wraps to at most 2 lines
        tx = cx + iw + 18
        tw = cell_w - iw - 36
        for size in (27, 25, 23, 21):
            f_head = font(SERIF_B, size)
            lines = wrap(d, head, f_head, tw)
            if len(lines) <= 2:
                break
        y = cy + 26
        for ln in lines[:2]:
            d.text((tx, y), ln, font=f_head, fill=INK)
            y += size + 6
        sub_lines = wrap(d, sub, f_sub, tw)
        y += 8
        for ln in sub_lines[:2]:
            d.text((tx, y), ln, font=f_sub, fill=GREY)
            y += 24
    # dividers + frame
    d.line([(W // 2, top), (W // 2, H)], fill=NAVY, width=2)
    d.line([(0, top + cell_h), (W, top + cell_h)], fill=NAVY, width=2)
    d.rectangle([0, 0, W - 1, H - 1], outline=NAVY, width=4)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    draw_masthead(img)
    draw_hero(img)
    draw_also(img)
    draw_grid(img)
    out = os.path.join(HERE, "entry.png")
    img.save(out, "PNG", optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
