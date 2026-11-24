#!/usr/bin/env python3
"""The World Today - 24 November 2026.

Pure-stdlib Python that paints a newspaper front page summing up the
world news of Tuesday, 24 November 2026 as a single 1024x1024 PNG.

Writes $MAKEFUN_OUTPUT_DIR/entry.png (default /output/entry.png).
No network, no third-party modules, deterministic: repeated runs write
identical bytes.

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

import os
import struct
import zlib
from pathlib import Path

W = 1024
H = 1024

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

# ---------------------------------------------------------------- font
# 5x7 pixel letters; '#' marks a filled cell.
FONT = {
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


def text_w(s, k):
    return len(s) * 6 * k - k


def wrap(s, n):
    """Wrap a string into lines of at most n characters."""
    out, cur = [], ""
    for word in s.split():
        trial = word if not cur else cur + " " + word
        if len(trial) <= n:
            cur = trial
        else:
            out.append(cur)
            cur = word
    if cur:
        out.append(cur)
    return out


class Page:
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

    def frame(self, x, y, w, h, rgb, t=3):
        self.rect(x, y, w, t, rgb)
        self.rect(x, y + h - t, w, t, rgb)
        self.rect(x, y, t, h, rgb)
        self.rect(x + w - t, y, t, h, rgb)

    def line(self, x0, y0, x1, y1, rgb, t=2):
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
        for yy in range(cy - r - t, cy + r + t + 1):
            for xx in range(cx - r - t, cx + r + t + 1):
                d = (xx - cx) ** 2 + (yy - cy) ** 2
                if (r - t) ** 2 < d <= r * r:
                    self.put(xx, yy, rgb)

    def tri(self, pts, rgb):
        """Fill a triangle by scanlines."""
        ys = sorted(p[1] for p in pts)
        for y in range(ys[0], ys[2] + 1):
            xs = []
            for a, b in ((pts[0], pts[1]), (pts[1], pts[2]), (pts[2], pts[0])):
                if a[1] == b[1]:
                    continue
                if min(a[1], b[1]) <= y <= max(a[1], b[1]):
                    t = (y - a[1]) / (b[1] - a[1])
                    xs.append(a[0] + (b[0] - a[0]) * t)
            if len(xs) >= 2:
                for x in range(int(min(xs)), int(max(xs)) + 1):
                    self.put(x, y, rgb)

    def text(self, x, y, s, k, rgb):
        s = s.upper()
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT[' '])
            for r, row in enumerate(glyph):
                for c, cell in enumerate(row):
                    if cell == '#':
                        self.rect(cx + c * k, y + r * k, k, k, rgb)
            cx += 6 * k
        return cx

    def text_c(self, y, s, k, rgb, cx=W // 2):
        return self.text(cx - text_w(s, k) // 2, y, s, k, rgb)

    def text_r(self, x_end, y, s, k, rgb):
        return self.text(x_end - text_w(s, k), y, s, k, rgb)


# ---------------------------------------------------------------- lead
def draw_jet(p, x, y, s, rgb):
    """A small swept-wing jet silhouette pointing up-right."""
    body = [(x, y - 26 * s), (x + 8 * s, y - 6 * s), (x + 6 * s, y + 14 * s),
            (x + 2 * s, y + 10 * s), (x - 2 * s, y + 10 * s),
            (x - 6 * s, y + 14 * s), (x - 8 * s, y - 6 * s)]
    p.tri(body[:3], rgb)
    p.tri([(x, y - 26 * s), (x - 8 * s, y - 6 * s), (x - 6 * s, y + 14 * s)], rgb)
    p.tri([(x - 8 * s, y - 6 * s), (x - 26 * s, y + 4 * s), (x - 10 * s, y + 10 * s)], rgb)
    p.tri([(x + 8 * s, y - 6 * s), (x + 26 * s, y + 4 * s), (x + 10 * s, y + 10 * s)], rgb)
    p.tri([(x - 4 * s, y + 10 * s), (x + 4 * s, y + 10 * s), (x, y + 22 * s)], rgb)


def draw_radar(p, cx, cy, r):
    """Radar screen: rings, sweep, blips, and two jets closing in."""
    p.disc(cx, cy, r, NIGHT)
    for rr in (r - 6, int(r * 0.66), int(r * 0.38)):
        p.ring(cx, cy, rr, TEAL, 2)
    p.line(cx - r, cy, cx + r, cy, TEAL, 2)
    p.line(cx, cy - r, cx, cy + r, TEAL, 2)
    p.ring(cx, cy, r, INK, 4)
    # sweep wedge
    for i in range(0, r, 3):
        p.line(cx, cy, cx + int(i * 0.72), cy - int(i * 0.72), EMBER, 3)
    # blips
    p.disc(cx + 52, cy - 58, 6, RED)
    p.disc(cx - 44, cy + 30, 5, RED)
    p.disc(cx + 18, cy + 62, 5, EMBER)
    draw_jet(p, cx - 58, cy - 62, 1, CREAM)
    draw_jet(p, cx + 66, cy + 44, 1, EMBER)


def draw_lead(p):
    p.frame(28, 168, W - 56, 356, INK, 4)
    p.rect(28, 168, W - 56, 52, RED)
    p.text(48, 182, "KOREA ON ALERT", 4, CREAM)
    p.text_r(W - 48, 182, "ULLEUNG ISLAND", 4, CREAM)
    p.text(48, 238, "RUSSIAN JETS", 7, INK)
    p.text(48, 296, "NEAR THE ISLAND", 7, INK)
    body = ("Russian military aircraft enter South Korea's air defence "
            "zone and close on Ulleung Island. Jets scramble, a 07:52 "
            "air-raid alert tells islanders to take shelter, and the "
            "alert lifts minutes later. Seoul says its airspace was "
            "not violated and will summon Russia's attache.")
    y = 360
    for ln in wrap(body, 52):
        p.text(48, y, ln, 2, INK)
        y += 21
    draw_radar(p, 806, 372, 104)


# ---------------------------------------------------------------- tiles
def tile(p, x, y, w, h, kicker, head, body, accent):
    p.frame(x, y, w, h, INK, 3)
    p.rect(x, y, w, 34, accent)
    p.text(x + 12, y + 8, kicker, 3, CREAM)
    yy = y + 46
    for ln in wrap(head, 23):
        p.text(x + 12, yy, ln, 2, INK)
        yy += 20
    yy += 4
    for ln in wrap(body, 23):
        p.text(x + 12, yy, ln, 2, GREY)
        yy += 17


def draw_tiles(p):
    tw, th = 312, 168
    xs = (28, 356, 684)
    rows = (544, 728)
    data = [
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
    i = 0
    for ry in rows:
        for rx in xs:
            kicker, head, body, accent = data[i]
            tile(p, rx, ry, tw, th, kicker, head, body, accent)
            i += 1


# ---------------------------------------------------------------- page
def build():
    p = Page()
    # masthead
    p.text_c(26, "THE WORLD TODAY", 11, INK)
    p.rect(28, 118, W - 56, 5, INK)
    p.text(28, 132, "TUESDAY 24 NOVEMBER 2026", 3, INK)
    p.text_r(W - 28, 132, "ONE IMAGE, THE DAY'S NEWS", 3, RED)
    p.rect(28, 158, W - 56, 3, INK)
    draw_lead(p)
    draw_tiles(p)
    # footer strip
    p.rect(28, 912, W - 56, 4, INK)
    foot = [
        "ALSO: UN CHIEF WANTS AN AI-REGULATION DEAL WITHIN A YEAR - CHINA",
        "SENTENCES AN OFFICIAL TO DEATH FOR SPYING - TWO KILLED IN A US",
        "UNIVERSITY SHOOTING - INDIA HOLDS THIRD IN ASIA POWER INDEX",
    ]
    y = 928
    for ln in foot:
        p.text_c(y, ln, 2, INK)
        y += 24
    p.rect(28, 1004, W - 56, 3, INK)
    return p


def png_bytes(p):
    raw = bytearray()
    rowlen = W * 3
    for y in range(H):
        raw.append(0)
        raw += p.px[y * rowlen:(y + 1) * rowlen]

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

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
