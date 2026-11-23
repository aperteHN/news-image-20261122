#!/usr/bin/env python3
"""Sum up 22 November 2026 world news in one image.

Writes /output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png): a one-page
newspaper front page for Sunday 22 November 2026, drawn pixel by pixel
with the Python standard library only. Deterministic: same bytes on
every run. Stories as reported that day: COP31 collapse in Antalya,
Ukraine strikes and drone-hit ships, Hormuz/Bahrain, Khartoum, UK-EU
deals, Mexico cartel capture, Brazil/Nigeria/Indonesia disasters,
France protests, West Bank arson, Nvidia chip probe.
"""
import os
import struct
import zlib

W = H = 1024
PAPER = (247, 243, 234)
WHITE = (255, 255, 255)
INK = (18, 18, 20)
MUTED = (92, 88, 80)
CREAM = (255, 240, 200)
GOLD = (255, 196, 64)
RED = (178, 34, 40)
BLUE = (28, 74, 135)
TEAL = (16, 110, 105)
ORANGE = (199, 102, 18)
PURPLE = (94, 58, 140)
GREEN = (46, 110, 52)
BROWN = (130, 82, 30)
LINE = (190, 185, 172)

# 5x7 bitmap font, each glyph is 7 rows of 5 pixels ('#' = on).
FONT = {
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "B": ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    "C": [".####", "#....", "#....", "#....", "#....", "#....", ".####"],
    "D": ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "F": ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
    "G": [".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."],
    "H": ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "I": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"],
    "J": ["..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."],
    "K": ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
    "L": ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    "M": ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
    "N": ["#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"],
    "O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "P": ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    "Q": [".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"],
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    "S": [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "U": ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "V": ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    "W": ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"],
    "X": ["#...#", ".#.#.", "..#..", "..#..", "..#..", ".#.#.", "#...#"],
    "Y": ["#...#", ".#.#.", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "Z": ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"],
    "0": [".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."],
    "1": ["..#..", ".##..", "#.#..", "..#..", "..#..", "..#..", "#####"],
    "2": [".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"],
    "3": ["####.", "....#", "....#", ".###.", "....#", "....#", "####."],
    "4": ["...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."],
    "5": ["#####", "#....", "####.", "....#", "....#", "#...#", ".###."],
    "6": [".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."],
    "7": ["#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."],
    "8": [".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."],
    "9": [".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."],
    " ": [".....", ".....", ".....", ".....", ".....", ".....", "....."],
    ".": [".....", ".....", ".....", ".....", ".....", ".##..", ".##.."],
    ",": [".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."],
    ":": [".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."],
    ";": [".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."],
    "'": ["..#..", "..#..", ".#...", ".....", ".....", ".....", "....."],
    '"': [".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."],
    "!": ["..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."],
    "?": [".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."],
    "-": [".....", ".....", ".....", "#####", ".....", ".....", "....."],
    "&": [".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"],
    "/": ["....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."],
    "(": ["...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"],
    ")": ["##...", "..#..", "...#.", "...#.", "...#.", "..#..", "##..."],
    "+": [".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."],
    "*": [".....", "#.#.#", ".###.", "#####", ".###.", "#.#.#", "....."],
    "%": ["##..#", "##.#.", "....#", "...#.", "..#..", ".#...", "#..##"],
    "$": ["..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."],
}

px = bytearray(bytes(PAPER) * (W * H))


def rect(x, y, w, h, color):
    r, g, b = color
    for yy in range(max(0, y), min(H, y + h)):
        base = (yy * W + max(0, x)) * 3
        for xx in range(max(0, x), min(W, x + w)):
            i = (yy * W + xx) * 3
            px[i], px[i + 1], px[i + 2] = r, g, b


def outline(x, y, w, h, color, t=2):
    rect(x, y, w, t, color)
    rect(x, y + h - t, w, t, color)
    rect(x, y, t, h, color)
    rect(x + w - t, y, t, h, color)


def text_w(s, scale):
    return len(s) * 6 * scale - scale


def draw_text(x, y, s, scale, color):
    cx = x
    for ch in s.upper():
        glyph = FONT.get(ch, FONT[" "])
        for row_i, row in enumerate(glyph):
            for col_i, cell in enumerate(row):
                if cell == "#":
                    rect(cx + col_i * scale, y + row_i * scale, scale, scale, color)
        cx += 6 * scale
    return cx


def wrap(s, scale, maxw):
    words, lines, cur = s.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if text_w(t, scale) <= maxw:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def block(x, y, s, scale, color, maxw, leading):
    for line in wrap(s, scale, maxw):
        draw_text(x, y, line, scale, color)
        y += leading
    return y


# Masthead
rect(0, 0, W, 148, INK)
draw_text(36, 16, "THE WORLD IN ONE DAY", 6, WHITE)
draw_text(36, 86, "SUNDAY * 22 NOVEMBER 2026", 4, GOLD)
draw_text(W - 36 - text_w("GLOBAL NEWS", 3), 94, "GLOBAL NEWS", 3, (210, 208, 200))
rect(36, 158, W - 72, 3, INK)

# Lead story
y = 172
rect(36, y, W - 72, 190, WHITE)
outline(36, y, W - 72, 190, INK, 2)
rect(36, y, W - 72, 40, RED)
draw_text(52, y + 8, "LEAD * CLIMATE * ANTALYA, TURKEY", 3, WHITE)
block(52, y + 54, "COP31 CLIMATE TALKS COLLAPSE WITHOUT A DEAL", 5, INK, W - 140, 44)
block(52, y + 148, "UN SUMMIT ENDS IN RECORD OVERTIME; DRAFT DEAL OMITS FOSSIL FUELS. EU AND ISLAND NATIONS REJECT IT AS UNCONSCIONABLE.", 2, MUTED, W - 120, 20)

panels = [
    ("UKRAINE WAR", BLUE, "STRIKES KILL NEAR KYIV; SHIPS ABLAZE",
     "RUSSIAN ATTACK NEAR KYIV KILLS 3, BURIES OTHERS; MISSILES KILL 2 IN ZELENSKYY'S HOMETOWN. DRONE-HIT SHIPS BURN IN BALTIC AND OFF LIBYA."),
    ("MIDDLE EAST * HORMUZ", ORANGE, "IRAN HITS TANKERS; BAHRAIN PLANT STRUCK",
     "TANKERS STRUCK NEAR STRAIT OF HORMUZ. BAHRAIN: IRANIAN ATTACK SETS SITRA PLANT ABLAZE, WOUNDS 2. TEHRAN SHOWS MISSILE CITY."),
    ("SUDAN", PURPLE, "DRONES STRIKE HOMES AND UN IN KHARTOUM",
     "DRONE STRIKES HIT HOMES AND A UN BUILDING IN SUDAN'S CAPITAL, WITNESSES AND THE UN SAID SUNDAY."),
    ("UK - EU RESET", TEAL, "BRITAIN AND EU STRIKE TRADE, TRAVEL DEALS",
     "LONDON AND BRUSSELS AGREE TRADE AND TRAVEL DEALS, PLEDGING TO REBUILD TIES A DECADE AFTER BREXIT."),
    ("MEXICO", GREEN, "CARTEL BOSS CAPTURED; 11 DEAD",
     "'EL CHAPO ISIDRO' CAPTURED IN SINALOA AFTER A BLOODY FIREFIGHT THAT LEFT AT LEAST 11 DEAD."),
    ("DISASTERS", BROWN, "STORM, BOAT AND FACTORY FIRE TOLLS RISE",
     "BRAZIL STORM KILLS 4, INJURES 162. NIGERIA FUNERAL BOAT: 24 DEAD. INDONESIA: SEARCH AFTER FACTORY FIRE."),
]
px0, py0, pw, ph, gap = 36, 376, 470, 174, 12
for i, (kicker, color, head, body) in enumerate(panels):
    x = px0 + (i % 2) * (pw + gap)
    yy = py0 + (i // 2) * (ph + gap)
    rect(x, yy, pw, ph, WHITE)
    outline(x, yy, pw, ph, LINE, 2)
    rect(x, yy, pw, 34, color)
    draw_text(x + 14, yy + 7, kicker, 3, WHITE)
    block(x + 14, yy + 46, head, 3, INK, pw - 28, 27)
    block(x + 14, yy + 106, body, 2, MUTED, pw - 28, 19)

ty = py0 + 3 * (ph + gap) + 4
rect(36, ty, W - 72, 78, INK)
block(52, ty + 10, "ALSO: FRANCE MARCHES, 6TH WEEKEND, OVER LIVING COSTS * WEST BANK SETTLERS TORCH HOMES * US DEMANDS NVIDIA ANSWERS ON AI CHIPS TO CHINA", 2, CREAM, W - 104, 20)


def chunk(tag, data):
    c = struct.pack(">I", len(data)) + tag + data
    return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)


raw = b"".join(b"\x00" + bytes(px[y * W * 3:(y + 1) * W * 3]) for y in range(H))
png = (b"\x89PNG\r\n\x1a\n"
       + chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
       + chunk(b"IDAT", zlib.compress(raw, 9))
       + chunk(b"IEND", b""))

out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
os.makedirs(out_dir, exist_ok=True)
out = os.path.join(out_dir, "entry.png")
with open(out, "wb") as fh:
    fh.write(png)
os.chmod(out, 0o644)
