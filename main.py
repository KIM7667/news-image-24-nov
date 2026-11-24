#!/usr/bin/env python3
"""The World Today - 24 November 2026.

Pure-stdlib Python that paints a newspaper front page summing up the
world news of Tuesday, 24 November 2026 as a single 1024x1024 PNG.

Writes $MAKEFUN_OUTPUT_DIR/entry.png (default /output/entry.png).
No network, no third-party modules, deterministic: repeated runs
write identical bytes.

Lead + six verified stories of 24 November 2026:
  Lead: Russian military jets enter South Korea's air defence zone
    near Ulleung Island; jets scrambled, a 07:52 air-raid alert
    tells islanders to take shelter, lifted minutes later. Seoul
    says no airspace violation and will summon Russia's attache.
  1. Antalya: after COP31 collapses with no deal, Erdogan says the
    summit laid a foundation for the next round; 46 decisions kept.
  2. Washington: the US blacklists Singapore-based Megaspeed, the
    firm at the centre of an alleged Nvidia spy scandal.
  3. Kyiv: Zelensky calls for four-party talks with Russia, the US
    and Europe as soon as possible, ready to meet on Tuesday.
  4. Indonesia: the search goes on after a factory fire leaves 3
    dead and dozens of workers missing.
  5. Himalayas: a flash flood kills at least 4 and leaves around
    100 unaccounted for; the Indian Army searches the valley.
  6. Ottawa: the Pentagon rebukes Canada over defence spending and
    its review of the F-35 fighter jets.
Footer: UN chief wants an AI-regulation deal within a year; China
sentences an official to death for spying; two killed in a US
university shooting; India holds third in the Asia Power Index;
Trump announces a Japan trade deal; South Africa votes.
"""

import math
import os
import struct
import zlib
from pathlib import Path

W, H = 1024, 1024

PAPER = (248, 244, 233)
INK = (18, 18, 18)
RED = (172, 30, 30)
BLUE = (28, 60, 118)
OCEAN = (58, 110, 165)
PALE = (198, 216, 232)
LAND = (146, 182, 118)
GOLD = (198, 158, 40)
GREY = (105, 105, 105)
CREAM = (236, 229, 212)
FIRE = (226, 112, 50)
EMBER = (242, 172, 62)
TEAL = (24, 118, 110)
NIGHT = (24, 38, 68)

# ------------------------------------------------------------------ font
# 5x7 pixel letters; '#' marks a filled cell.
GLYPHS = {
    'A': (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'B': ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    'C': (".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."),
    'D': ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    'E': ("#####", "#....", "####.", "#....", "#....", "#....", "#####"),
    'F': ("#####", "#....", "####.", "#....", "#....", "#....", "#...."),
    'G': (".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".###."),
    'H': ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'I': (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    'J': ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    'K': ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    'L': ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    'M': ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    'N': ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    'O': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'P': ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    'Q': (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    'R': ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    'S': (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    'T': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    'U': ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'V': ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'W': ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    'X': ("#...#", ".#.#.", "..#..", "..#..", "..#..", ".#.#.", "#...#"),
    'Y': ("#...#", ".#.#.", "..#..", "..#..", "..#..", "..#..", "..#.."),
    'Z': ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    '0': (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    '1': ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    '2': (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    '3': ("#####", "...#.", "..#..", "...#.", "....#", "#...#", ".###."),
    '4': ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    '5': ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    '6': (".##..", ".#...", "#....", "####.", "#...#", "#...#", ".###."),
    '7': ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    '8': (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    '9': (".###.", "#...#", "#...#", ".####", "....#", "...#.", ".##.."),
    ' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    '.': (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ',': (".....", ".....", ".....", ".....", ".##..", "..#..", ".#..."),
    ':': (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ';': (".....", ".##..", ".##..", ".....", ".##..", "..#..", ".#..."),
    '-': (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '!': ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    '?': (".###.", "#...#", "....#", "..##.", "..#..", ".....", "..#.."),
    '/': ("....#", "....#", "...#.", "..#..", ".#...", ".#...", "#...."),
    '(': ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ')': (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    '$': ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    '%': ("##..#", "##.#.", "....#", "...#.", "..#..", ".#.##", "#..##"),
    '&': (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".#.#."),
    '+': (".....", "..#..", "..#..", ".###.", "..#..", "..#..", "....."),
    '=': (".....", ".....", ".####", ".....", ".####", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    '*': (".....", "..#..", "#.#.#", ".###.", "#.#.#", "..#..", "....."),
}

BLANK = (".....",) * 7


def text_width(s, k):
    """Pixel width of s rendered at scale k (6 px advance per glyph)."""
    return len(s) * 6 * k - k


def wrap_text(s, n):
    """Wrap a string into lines of at most n characters."""
    lines, cur = [], ""
    for word in s.split():
        trial = word if not cur else cur + " " + word
        if len(trial) <= n:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


class Canvas:
    """An RGB pixel buffer with tiny vector drawing helpers."""

    def __init__(self):
        self.px = bytearray(PAPER * (W * H))

    def put(self, x, y, rgb):
        if 0 <= x < W and 0 <= y < H:
            i = (y * W + x) * 3
            self.px[i:i + 3] = bytes(rgb)

    def rect(self, x, y, w, h, rgb):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.put(xx, yy, rgb)

    def hline(self, x, y, w, rgb, t=1):
        self.rect(x, y, w, t, rgb)

    def vline(self, x, y, h, rgb, t=1):
        self.rect(x, y, t, h, rgb)

    def frame(self, x, y, w, h, rgb, t=3):
        self.hline(x, y, w, rgb, t)
        self.hline(x, y + h - t, w, rgb, t)
        self.vline(x, y, h, rgb, t)
        self.vline(x + w - t, y, h, rgb, t)

    def segment(self, x0, y0, x1, y1, rgb, t=2):
        """A straight line drawn as a chain of t x t blocks."""
        steps = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(steps + 1):
            x = x0 + (x1 - x0) * i // steps
            y = y0 + (y1 - y0) * i // steps
            self.rect(x, y, t, t, rgb)

    def disc(self, cx, cy, r, rgb):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.put(xx, yy, rgb)

    def ring(self, cx, cy, r, rgb, t=3):
        lo = (r - t) ** 2
        for yy in range(cy - r - t, cy + r + t + 1):
            for xx in range(cx - r - t, cx + r + t + 1):
                d = (xx - cx) ** 2 + (yy - cy) ** 2
                if lo < d <= r * r:
                    self.put(xx, yy, rgb)

    def triangle(self, pts, rgb):
        """Fill a triangle by horizontal scanlines."""
        (ax, ay), (bx, by), (cx, cy) = pts
        top, bot = min(ay, by, cy), max(ay, by, cy)
        edges = (((ax, ay), (bx, by)), ((bx, by), (cx, cy)),
                 ((cx, cy), (ax, ay)))
        for y in range(top, bot + 1):
            xs = []
            for (x0, y0), (x1, y1) in edges:
                if y0 == y1 or not (min(y0, y1) <= y <= max(y0, y1)):
                    continue
                f = (y - y0) / (y1 - y0)
                xs.append(x0 + (x1 - x0) * f)
            if len(xs) >= 2:
                for x in range(int(min(xs)), int(max(xs)) + 1):
                    self.put(x, y, rgb)

    def glyph(self, x, y, ch, k, rgb):
        rows = GLYPHS.get(ch, BLANK)
        for r, row in enumerate(rows):
            for c, cell in enumerate(row):
                if cell == '#':
                    self.rect(x + c * k, y + r * k, k, k, rgb)

    def text(self, x, y, s, k, rgb):
        cx = x
        for ch in s.upper():
            self.glyph(cx, y, ch, k, rgb)
            cx += 6 * k
        return cx

    def text_center(self, y, s, k, rgb, cx=W // 2):
        return self.text(cx - text_width(s, k) // 2, y, s, k, rgb)

    def text_right(self, x_end, y, s, k, rgb):
        return self.text(x_end - text_width(s, k), y, s, k, rgb)


# ------------------------------------------------------------------- art
def jet(c, x, y, s, rgb):
    """Swept-wing jet silhouette, nose pointing up-right."""
    nose = (x + 20 * s, y - 24 * s)
    tail_l, tail_r = (x - 6 * s, y + 14 * s), (x + 8 * s, y + 12 * s)
    c.triangle([nose, (x - 8 * s, y - 4 * s), tail_l], rgb)
    c.triangle([nose, tail_r, (x + 10 * s, y - 2 * s)], rgb)
    c.triangle([(x - 8 * s, y - 4 * s), (x - 28 * s, y + 6 * s),
                (x - 10 * s, y + 10 * s)], rgb)
    c.triangle([(x + 10 * s, y - 2 * s), (x + 28 * s, y + 8 * s),
                (x + 10 * s, y + 12 * s)], rgb)
    c.triangle([(x - 4 * s, y + 10 * s), (x + 6 * s, y + 10 * s),
                (x + 2 * s, y + 24 * s)], rgb)


def radar(c, cx, cy, r):
    """Radar screen: concentric rings, cross-hairs, a dotted sweep arc,
    three blips and two jets closing in on the island."""
    c.disc(cx, cy, r, NIGHT)
    for rr in (r - 6, int(r * 0.66), int(r * 0.38)):
        c.ring(cx, cy, rr, TEAL, 2)
    c.segment(cx - r, cy, cx + r, cy, TEAL, 2)
    c.segment(cx, cy - r, cx, cy + r, TEAL, 2)
    c.ring(cx, cy, r, INK, 4)
    # dotted sweep arc, upper-right quadrant
    for deg in range(0, 91, 6):
        a = math.radians(deg)
        for rr in (r - 18, r - 30, r - 42):
            c.disc(cx + int(rr * math.cos(a)), cy - int(rr * math.sin(a)),
                   3, EMBER)
    c.disc(cx + 52, cy - 58, 6, RED)
    c.disc(cx - 44, cy + 30, 5, RED)
    c.disc(cx + 18, cy + 62, 5, EMBER)
    jet(c, cx - 58, cy - 62, 1, CREAM)
    jet(c, cx + 66, cy + 44, 1, EMBER)


# ------------------------------------------------------------------ story
LEAD_BODY = (
    "Russian military aircraft enter South Korea's air defence "
    "zone and close on Ulleung Island. Jets scramble, a 07:52 "
    "air-raid alert tells islanders to take shelter, and the "
    "alert lifts minutes later. Seoul says its airspace was "
    "not violated and will summon Russia's attache.")

TILES = [
    ("ANTALYA", "COP31 AFTERMATH: DEAL DEAD, TALKS LIVE ON",
     "Erdogan: the failed summit laid a foundation for next "
     "talks.", TEAL),
    ("WASHINGTON", "US BLACKLISTS MEGASPEED IN NVIDIA SPY CASE",
     "The Singapore firm in the Nvidia spy case joins the "
     "Entity List.", BLUE),
    ("KYIV", "ZELENSKY SEEKS FOUR-PARTY TALKS NOW",
     "Kyiv is ready to meet as early as Tuesday.", GOLD),
    ("INDONESIA", "FACTORY FIRE: SEARCH GOES ON FOR MISSING",
     "Three dead, dozens missing as rescue teams keep "
     "digging.", FIRE),
    ("HIMALAYAS", "FLOOD: SCORES MISSING IN THE MOUNTAINS",
     "At least four dead, about 100 missing after the "
     "valley flood.", OCEAN),
    ("OTTAWA", "PENTAGON REBUKES CANADA OVER F-35 REVIEW",
     "Washington says Ottawa falls short as a partner in "
     "defence.", RED),
]

FOOTER = [
    "ALSO: UN CHIEF WANTS AN AI-REGULATION DEAL WITHIN A YEAR - CHINA",
    "SENTENCES AN OFFICIAL TO DEATH FOR SPYING - TWO KILLED IN A US",
    "UNIVERSITY SHOOTING - INDIA HOLDS THIRD IN ASIA POWER INDEX",
]


def draw_masthead(c):
    c.text_center(26, "THE WORLD TODAY", 11, INK)
    c.hline(28, 118, W - 56, INK, 5)
    c.text(28, 132, "TUESDAY 24 NOVEMBER 2026", 3, INK)
    c.text_right(W - 28, 132, "ONE IMAGE, THE DAY'S NEWS", 3, RED)
    c.hline(28, 158, W - 56, INK, 3)


def draw_lead(c):
    c.frame(28, 168, W - 56, 356, INK, 4)
    c.rect(28, 168, W - 56, 52, RED)
    c.text(48, 182, "KOREA ON ALERT", 4, CREAM)
    c.text_right(W - 48, 182, "ULLEUNG ISLAND", 4, CREAM)
    c.text(48, 238, "RUSSIAN JETS", 7, INK)
    c.text(48, 296, "NEAR THE ISLAND", 7, INK)
    y = 360
    for ln in wrap_text(LEAD_BODY, 52):
        c.text(48, y, ln, 2, INK)
        y += 21
    radar(c, 806, 372, 104)


def draw_tile(c, x, y, w, h, kicker, head, body, accent):
    c.frame(x, y, w, h, INK, 3)
    c.rect(x, y, w, 34, accent)
    c.text(x + 12, y + 8, kicker, 3, CREAM)
    yy = y + 46
    for ln in wrap_text(head, 23):
        c.text(x + 12, yy, ln, 2, INK)
        yy += 20
    yy += 4
    for ln in wrap_text(body, 23):
        c.text(x + 12, yy, ln, 2, GREY)
        yy += 17


def draw_grid(c):
    tw, th = 312, 168
    xs = (28, 356, 684)
    rows = (544, 728)
    i = 0
    for ry in rows:
        for rx in xs:
            kicker, head, body, accent = TILES[i]
            draw_tile(c, rx, ry, tw, th, kicker, head, body, accent)
            i += 1


def draw_footer(c):
    c.hline(28, 912, W - 56, INK, 4)
    y = 928
    for ln in FOOTER:
        c.text_center(y, ln, 2, INK)
        y += 24
    c.hline(28, 1004, W - 56, INK, 3)


def build():
    c = Canvas()
    draw_masthead(c)
    draw_lead(c)
    draw_grid(c)
    draw_footer(c)
    return c


# -------------------------------------------------------------------- png
def png_bytes(c):
    raw = bytearray()
    rowlen = W * 3
    for y in range(H):
        raw.append(0)  # filter: none
        raw += c.px[y * rowlen:(y + 1) * rowlen]

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        return out + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))


def main():
    out = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out.mkdir(parents=True, exist_ok=True)
    (out / "entry.png").write_bytes(png_bytes(build()))


if __name__ == "__main__":
    main()
