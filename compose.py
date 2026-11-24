#!/usr/bin/env python3
"""
compose.py - draws the make.fun news-image-20261123 entry.

One 1024x1024 newspaper-style front page summing up the world news of
Monday 23 November 2026. Everything is drawn with Pillow primitives: no
photographs, no external images, no network. The output is deterministic.
"""

import os
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "assets", "entry.png")

# ---------------------------------------------------------------- palette
PAPER = (243, 238, 226)
PAPER_ALT = (236, 230, 216)
INK = (28, 27, 25)
INK_SOFT = (74, 71, 66)
RULE = (120, 114, 103)
RULE_LIGHT = (190, 183, 169)
OCEAN = (214, 226, 230)

REGION_COLOR = {
    "EUROPE":       (31, 78, 121),
    "MIDDLE EAST":  (166, 58, 42),
    "ASIA":         (31, 122, 92),
    "AMERICAS":     (106, 61, 154),
    "AFRICA":       (168, 116, 18),
    "OCEANIA":      (15, 123, 138),
    "WORLD":        (61, 61, 61),
}

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
_FONTS = {}


def font(name, size):
    key = (name, size)
    if key not in _FONTS:
        path = os.path.join(FONT_DIR, name)
        _FONTS[key] = ImageFont.truetype(path, max(1, int(size)))
    return _FONTS[key]


SERIF_B = "DejaVuSerif-Bold.ttf"
SERIF = "DejaVuSerif.ttf"
SANS = "DejaVuSans.ttf"
SANS_B = "DejaVuSans-Bold.ttf"


# ---------------------------------------------------------------- text fit
def text_w(draw, text, f):
    return draw.textlength(text, font=f)


def fit_line(draw, text, name, size, max_w, min_size=5):
    """Largest font size that fits, else truncate with an ellipsis."""
    s = size
    while s > min_size:
        f = font(name, s)
        if text_w(draw, text, f) <= max_w:
            return text, f
        s -= 1
    f = font(name, min_size)
    if text_w(draw, text, f) <= max_w:
        return text, f
    ell = "\u2026"
    out = text
    while out and text_w(draw, out + ell, f) > max_w:
        out = out[:-1]
    return (out.rstrip() + ell) if out else ell, f


def wrap(draw, text, f, max_w, max_lines):
    """Greedy word wrap, at most max_lines, ellipsis on the last line."""
    words = text.split()
    lines = []
    cur = ""
    for w in words:
        trial = (cur + " " + w).strip()
        if text_w(draw, trial, f) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
            if len(lines) == max_lines:
                break
    if cur and len(lines) < max_lines:
        lines.append(cur)
    if not lines:
        return [""]
    if len(lines) > max_lines:
        lines = lines[:max_lines]
    # If there is overflow left over, mark it.
    joined = " ".join(lines)
    if joined != text:
        last = lines[-1]
        ell = "\u2026"
        while last and text_w(draw, last + ell, f) > max_w:
            last = last[:-1]
        lines[-1] = last.rstrip() + ell
    else:
        # Even when all words fit, trim any single over-wide line.
        fixed = []
        for ln in lines:
            if text_w(draw, ln, f) > max_w:
                ln, _ = fit_line(draw, ln, f.path.split("/")[-1], f.size, max_w)
            fixed.append(ln)
        lines = fixed
    return lines


def wrap_fit(draw, text, name, size, max_w, max_lines, min_size=5):
    """Choose a size that lets text wrap into max_lines, then wrap."""
    s = size
    while s > min_size:
        f = font(name, s)
        # estimate lines needed
        words = text.split()
        line = ""
        n = 1
        for w in words:
            trial = (line + " " + w).strip()
            if text_w(draw, trial, f) <= max_w or not line:
                line = trial
            else:
                n += 1
                line = w
        if n <= max_lines:
            return wrap(draw, text, f, max_w, max_lines)
        s -= 1
    return wrap(draw, text, font(name, min_size), max_w, max_lines)


def draw_lines(draw, lines, f, x, y, max_w, lh, fill=INK):
    for i, ln in enumerate(lines):
        if text_w(draw, ln, f) > max_w:
            ln, f2 = fit_line(draw, ln, f.path.split("/")[-1], f.size, max_w)
        else:
            f2 = f
        draw.text((x, y + i * lh), ln, font=f2, fill=fill)
    return y + len(lines) * lh


# ---------------------------------------------------------------- data
# 13 pictured stories: (number, region, headline, summary)
PICTURED = [
    (1,  "EUROPE",      "COP31 FAILS WITH NO DEAL",
     "First COP since 2009 to end without an agreement; Guterres \u201cdeeply disappointed\u201d as calls grow to reform the summit system."),
    (2,  "EUROPE",      "DYMER TOLL HITS 11 AS BOY PULLED ALIVE",
     "Russian strike wrecked a five-storey block near Kyiv; rescuers saved Davyd and Valentyna from the rubble."),
    (3,  "EUROPE",      "UKRAINE HITS REFINERIES DEEP INSIDE RUSSIA",
     "Novoshakhtinsk plant suspends operations; the Perm refinery was struck 1,700 km from Ukraine."),
    (10, "MIDDLE EAST", "THREE TANKERS HIT MINES IN HORMUZ",
     "IRGC says the vessels caught fire after striking naval mines, with 22 attacks logged in November."),
    (11, "MIDDLE EAST", "ISRAELI STRIKE KILLS UN WORKER IN GAZA",
     "UNRWA worker Adel Al-Helo died in Jabalia; two more were killed in a vehicle strike in Gaza City."),
    (18, "ASIA",        "INDONESIA CONFIRMS 24 DEAD IN FACTORY FIRE",
     "Blaze at the Cikande sweets factory; 24 body bags recovered and about 30 people still missing."),
    (19, "ASIA",        "INDIA GIVES NEPAL $1.63BN REBUILD PACKAGE",
     "Eight deals signed; an Ayodhya\u2013Janakpur train was flagged off and a new IIT campus announced."),
    (24, "AMERICAS",    "NVIDIA REINSTATES JENSEN HUANG AS CEO",
     "Shares jumped about 31% after Trump dialled into a Sunday board meeting backing his return."),
    (25, "AMERICAS",    "REP. JIMMY GOMEZ TO RESIGN AFTER ETHICS REPORT",
     "A House panel found \u201csubstantial evidence\u201d of sexual misconduct; his exit is set for 1 December."),
    (31, "AFRICA",      "UKRAINE SINKS RUSSIAN CORVETTE OFF LIBYA",
     "Seven naval drones sank the Merkury at Benghazi; the cargo ship MV Angara was also hit."),
    (32, "AFRICA",      "NIGERIA BOAT TOLL RISES TO 29",
     "NEMA updated the Bayelsa funeral-boat disaster figures; 50 people were rescued and the boat is still missing."),
    (36, "OCEANIA",     "PACIFIC GOES IT ALONE AFTER COP31 COLLAPSE",
     "Island nations formed their own climate coalitions; Tuvalu called the failure a survival issue."),
    (39, "WORLD",       "BEPICOLOMBO \u2018ON TRACK\u2019 DESPITE GLITCH",
     "The Mercury probe is safe in a stable orbit; a shortened burn delivered 77% of planned thrust."),
]

# 28 listed stories grouped by region: (number, headline)
LISTED = {
    "EUROPE": [
        (4,  "EU unveils 22nd Russia sanctions package"),
        (5,  "NATO to send AWACS aircraft to Poland"),
        (6,  "Germany to adopt Ukraine\u2019s Delta battle tool"),
        (7,  "NHS launches huge AI breast screening trial"),
        (8,  "Belgium flights grounded by austerity strike"),
        (9,  "Thousands rally in Istanbul against crackdown"),
    ],
    "MIDDLE EAST": [
        (12, "Iran flogs singer Parastoo Ahmadi"),
        (13, "US sanctions Iranian shadow banking networks"),
        (14, "Iran demands $290bn damages from US"),
        (15, "Iran unveils dual-missile launcher"),
        (16, "Bahrain reports two wounded in Iran strike"),
        (17, "Houthis claim Saudi refinery hit"),
    ],
    "ASIA": [
        (20, "EU and Indonesia sign landmark trade deal"),
        (21, "Taiwan tightens short-selling rules"),
        (22, "Asian tech shares fall as AI sell-off deepens"),
        (23, "Bangladesh garment wage talks stall"),
    ],
    "AMERICAS": [
        (26, "US blacklists Singapore AI firm Megaspeed"),
        (27, "Trump pauses toxic explosive disposal in Iowa"),
        (28, "Drone attack hits Colombia police base"),
        (29, "Bitcoin rebounds to $61K from two-year low"),
        (30, "NYT: US tracked Huang aide\u2019s China contacts"),
    ],
    "AFRICA": [
        (33, "Nigerian army rescues 18 abducted children"),
        (34, "Fighting traps Ebola responders in DRC"),
        (35, "Saudi, Egypt condemn Khartoum drone strikes"),
    ],
    "OCEANIA": [
        (37, "Prespakis wins AFLW best and fairest"),
        (38, "Fonterra seeks to dump 22m litres of milk"),
    ],
    "WORLD": [
        (40, "$72bn in Ethereum faces quantum threat"),
        (41, "Chernobyl fungus could trap nerve agents"),
    ],
}

REGION_ORDER = ["EUROPE", "MIDDLE EAST", "ASIA", "AMERICAS", "AFRICA", "OCEANIA", "WORLD"]
REGION_COUNTS = {r: len([s for s in PICTURED if s[1] == r]) + len(LISTED[r]) for r in REGION_ORDER}

# Approximate locations (lon, lat) for pictured stories with a place.
PINS = {
    2:  (30.5, 50.4),    # Kyiv / Dymer
    3:  (56.0, 48.0),    # Perm region
    10: (56.5, 26.6),    # Strait of Hormuz
    11: (34.4, 31.5),    # Gaza
    18: (106.3, -6.3),   # Cikande, Indonesia
    19: (77.2, 28.6),    # New Delhi
    24: (-121.9, 37.3),  # Santa Clara
    25: (-77.0, 38.9),   # Washington DC
    31: (20.1, 32.1),    # Benghazi
    32: (6.0, 4.8),      # Bayelsa
    36: (179.2, -8.5),   # Tuvalu
}


# ---------------------------------------------------------------- map
CONTINENTS = [
    # North America
    [(-168,65),(-140,70),(-95,72),(-60,60),(-55,48),(-70,42),(-80,25),
     (-97,16),(-105,20),(-115,30),(-125,40),(-130,55),(-150,60)],
    # Central America
    [(-105,20),(-92,16),(-83,8),(-78,8),(-83,14),(-95,18),(-105,20)],
    # South America
    [(-78,8),(-60,10),(-50,0),(-35,-6),(-38,-22),(-48,-28),(-58,-38),
     (-65,-55),(-72,-52),(-72,-30),(-75,-15),(-81,-4)],
    # Europe
    [(-10,36),(0,44),(3,52),(10,58),(25,70),(40,68),(45,55),(40,45),
     (28,41),(22,36),(10,38),(0,37)],
    # Africa
    [(-17,15),(-10,30),(10,37),(32,31),(43,12),(51,12),(41,-2),(40,-15),
     (35,-24),(25,-34),(18,-34),(12,-18),(8,4),(-8,4)],
    # Asia
    [(45,55),(60,70),(90,75),(140,72),(160,70),(170,65),(140,50),(140,35),
     (120,22),(110,10),(100,5),(95,15),(80,8),(70,22),(60,25),(45,30),(40,45)],
    # India
    [(68,24),(72,8),(78,8),(88,22),(80,24)],
    # SE Asia / Indonesia
    [(95,5),(120,0),(140,-8),(130,-8),(110,-8),(100,0)],
    # Australia
    [(114,-22),(122,-18),(130,-12),(142,-11),(145,-18),(153,-27),(150,-37),
     (135,-35),(125,-33),(115,-34)],
    # Greenland
    [(-45,60),(-20,70),(-20,82),(-60,82),(-58,70)],
    # Madagascar
    [(44,-13),(50,-15),(49,-25),(44,-25)],
    # British Isles
    [(-8,50),(-2,50),(0,55),(-5,58),(-10,54)],
    # Japan
    [(130,32),(142,40),(145,44),(141,45),(137,37),(132,34)],
    # New Zealand
    [(166,-46),(174,-41),(178,-37),(176,-40),(170,-44)],
]


def point_in_poly(x, y, poly):
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi + 1e-12) + xi):
            inside = not inside
        j = i
    return inside


def draw_dotted_map(draw, x0, y0, mw, mh):
    lon0, lon1 = -180.0, 180.0
    lat0, lat1 = 84.0, -60.0

    def project(lon, lat):
        px = x0 + (lon - lon0) / (lon1 - lon0) * mw
        py = y0 + (lat0 - lat) / (lat0 - lat1) * mh
        return px, py

    draw.rectangle([x0, y0, x0 + mw, y0 + mh], fill=OCEAN, outline=RULE_LIGHT)
    # faint graticule
    for lon in range(-150, 180, 30):
        px, _ = project(lon, 0)
        draw.line([(px, y0 + 2), (px, y0 + mh - 2)], fill=(198, 212, 216))
    for lat in (-30, 0, 30, 60):
        _, py = project(0, lat)
        draw.line([(x0 + 2, py), (x0 + mw - 2, py)], fill=(198, 212, 216))

    step = 5.5
    r = 1.4
    lat = lat0 - 2
    while lat >= lat1 + 1:
        lon = lon0 + 2
        while lon <= lon1 - 1:
            inside = any(point_in_poly(lon, lat, poly) for poly in CONTINENTS)
            if inside:
                px, py = project(lon, lat)
                draw.ellipse([px - r, py - r, px + r, py + r], fill=(90, 108, 112))
            lon += step
        lat -= step
    return project


# ---------------------------------------------------------------- illustrations
def icon_area(draw, box, region):
    """Soft tinted panel to hold a drawn pictogram."""
    x0, y0, x1, y1 = box
    col = REGION_COLOR[region]
    tint = tuple(min(255, int(c + (255 - c) * 0.78)) for c in col)
    draw.rectangle([x0, y0, x1, y1], fill=tint, outline=col, width=1)


def ic_cop31(draw, box, col):
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2 + 1
    r = min(x1 - x0, y1 - y0) // 4
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=col, width=2, fill=(230, 240, 245))
    draw.arc([cx - r, cy - r, cx + r, cy + r], 200, 340, fill=col, width=1)
    draw.line([cx, cy - r, cx, cy + r], fill=col, width=1)
    draw.line([cx - r, cy, cx + r, cy], fill=col, width=1)
    # crack
    draw.line([cx + 2, cy - r + 3, cx - 3, cy - 2, cx + 4, cy + 3, cx - 1, cy + r - 3], fill=(166, 58, 42), width=2)
    # little X
    draw.line([x1 - 14, y0 + 6, x1 - 6, y0 + 14], fill=(166, 58, 42), width=2)
    draw.line([x1 - 6, y0 + 6, x1 - 14, y0 + 14], fill=(166, 58, 42), width=2)


def ic_rubble(draw, box, col):
    x0, y0, x1, y1 = box
    w = x1 - x0
    h = y1 - y0
    base = y1 - 6
    # five-storey block with a broken top corner
    bx0 = x0 + 6
    bx1 = x1 - 18
    by0 = y0 + 10
    draw.rectangle([bx0, by0, bx1, base], fill=(150, 140, 125), outline=col)
    for r in range(3):
        for c in range(3):
            wx = bx0 + 4 + c * 9
            wy = by0 + 5 + r * 9
            if wx + 5 < bx1:
                draw.rectangle([wx, wy, wx + 5, wy + 5], fill=(70, 66, 60))
    # collapsed wedge
    draw.polygon([(bx1, base), (bx1 + 12, base), (bx1, by0 + 18)], fill=(110, 102, 92))
    # rubble
    draw.ellipse([bx1 - 2, base - 4, bx1 + 8, base + 3], fill=(110, 102, 92))
    draw.ellipse([bx0 + 1, base - 5, bx0 + 9, base + 2], fill=(120, 111, 99))
    # red cross
    ccx, ccy = x0 + 11, y0 + 9
    draw.rectangle([ccx - 2, ccy - 6, ccx + 2, ccy + 6], fill=(190, 40, 35))
    draw.rectangle([ccx - 6, ccy - 2, ccx + 6, ccy + 2], fill=(190, 40, 35))


def ic_refinery(draw, box, col):
    x0, y0, x1, y1 = box
    base = y1 - 7
    # towers
    for i, (tx, tw, th) in enumerate([(8, 6, 22), (19, 5, 30), (30, 7, 18)]):
        draw.rectangle([x0 + tx, base - th, x0 + tx + tw, base], fill=(120, 116, 108), outline=col)
        draw.ellipse([x0 + tx - 1, base - th - 4, x0 + tx + tw + 1, base - th + 2], fill=(120, 116, 108), outline=col)
    # pipe
    draw.line([x0 + 6, base - 8, x1 - 20, base - 8], fill=col, width=2)
    # flame
    fx = x1 - 16
    draw.polygon([(fx, base - 6), (fx - 6, base - 18), (fx - 1, base - 13),
                  (fx + 2, base - 26), (fx + 7, base - 15), (fx + 10, base - 20),
                  (fx + 10, base - 6)], fill=(226, 108, 30))
    draw.polygon([(fx + 1, base - 7), (fx + 2, base - 16), (fx + 6, base - 9)], fill=(247, 200, 60))
    # drone
    dx, dy = x1 - 9, y0 + 7
    draw.line([dx - 5, dy, dx + 5, dy], fill=INK, width=1)
    draw.ellipse([dx - 2, dy - 2, dx + 2, dy + 2], fill=INK)


def ic_tanker(draw, box, col):
    x0, y0, x1, y1 = box
    wy = y1 - 15
    draw.rectangle([x0, wy + 5, x1, y1], fill=(150, 190, 205))
    hull = [(x0 + 5, wy), (x1 - 12, wy), (x1 - 4, wy + 9), (x0 + 9, wy + 9)]
    draw.polygon(hull, fill=(70, 70, 76), outline=col)
    draw.rectangle([x0 + 16, wy - 12, x0 + 30, wy], fill=(180, 80, 60), outline=col)
    draw.rectangle([x1 - 26, wy - 8, x1 - 16, wy], fill=(200, 200, 200), outline=col)
    # smoke
    draw.ellipse([x0 + 19, wy - 20, x0 + 27, wy - 13], fill=(150, 150, 150))
    draw.ellipse([x0 + 22, wy - 27, x0 + 31, wy - 19], fill=(170, 170, 170))
    # mines
    for mx in (x0 + 6, x1 - 6):
        draw.ellipse([mx - 4, wy + 8, mx + 4, wy + 16], fill=(40, 40, 40))
        for a in range(0, 360, 45):
            import math
            ex = mx + 6 * math.cos(math.radians(a))
            ey = wy + 12 + 6 * math.sin(math.radians(a))
            draw.line([mx, wy + 12, ex, ey], fill=(40, 40, 40))


def ic_un(draw, box, col):
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    r = min(x1 - x0, y1 - y0) // 4
    draw.ellipse([cx - r, cy - r - 4, cx + r, cy + r - 4], fill=(70, 120, 180), outline=col)
    draw.arc([cx - r + 2, cy - r - 2, cx + r - 2, cy + r - 6], 200, 340, fill=(255, 255, 255), width=2)
    # aid box
    by = cy + r + 1
    draw.rectangle([cx - 12, by, cx + 12, by + 10], fill=(220, 210, 180), outline=col)
    draw.rectangle([cx - 2, by + 2, cx + 2, by + 8], fill=(190, 40, 35))
    draw.rectangle([cx - 6, by + 4, cx + 6, by + 6], fill=(190, 40, 35))
    # black ribbon
    draw.line([x1 - 9, y0 + 5, x1 - 9, y0 + 17], fill=INK, width=2)


def ic_factory_fire(draw, box, col):
    x0, y0, x1, y1 = box
    base = y1 - 7
    draw.rectangle([x0 + 5, base - 20, x1 - 6, base], fill=(125, 120, 112), outline=col)
    # sawtooth roof
    draw.polygon([(x0 + 5, base - 20), (x0 + 13, base - 28), (x0 + 21, base - 20),
                  (x0 + 29, base - 28), (x0 + 37, base - 20)], outline=col)
    for wx in range(x0 + 9, x1 - 8, 9):
        draw.rectangle([wx, base - 14, wx + 5, base - 8], fill=(60, 56, 52))
    # flames and smoke
    fx = (x0 + x1) // 2
    draw.polygon([(fx - 10, base - 6), (fx - 4, base - 22), (fx + 1, base - 14),
                  (fx + 5, base - 30), (fx + 10, base - 16), (fx + 14, base - 6)], fill=(226, 100, 30))
    draw.polygon([(fx - 3, base - 7), (fx + 1, base - 18), (fx + 6, base - 9)], fill=(247, 200, 60))
    draw.ellipse([fx - 16, y0 + 4, fx - 2, y0 + 16], fill=(120, 120, 120))
    draw.ellipse([fx - 6, y0 + 1, fx + 10, y0 + 14], fill=(150, 150, 150))


def ic_handshake(draw, box, col):
    x0, y0, x1, y1 = box
    cy = (y0 + y1) // 2
    # two flag blocks
    draw.rectangle([x0 + 6, cy - 16, x0 + 16, cy - 2], fill=(255, 153, 51))
    draw.rectangle([x0 + 6, cy - 2, x0 + 16, cy + 12], fill=(19, 136, 8))
    draw.ellipse([x0 + 9, cy - 7, x0 + 13, cy - 3], fill=(0, 0, 128))
    draw.rectangle([x1 - 16, cy - 16, x1 - 6, cy - 2], fill=(220, 20, 60))
    draw.rectangle([x1 - 16, cy - 2, x1 - 6, cy + 12], fill=(0, 56, 147))
    draw.ellipse([x1 - 13, cy - 7, x1 - 9, cy - 3], fill=(255, 255, 255))
    # clasped hands
    draw.rounded_rectangle([x0 + 17, cy - 5, x1 - 17, cy + 5], radius=4, fill=(224, 190, 150), outline=col)
    draw.line([(x0 + 22, cy), (x1 - 22, cy)], fill=(170, 130, 95), width=1)
    # rupee
    draw.text((x0 + 2, y1 - 15), "\u20b9", font=font(SANS_B, 11), fill=col)


def ic_chip_arrow(draw, box, col):
    x0, y0, x1, y1 = box
    cx, cy = x0 + 20, y0 + 22
    draw.rectangle([cx - 11, cy - 11, cx + 11, cy + 11], fill=(60, 150, 110), outline=col)
    draw.rectangle([cx - 5, cy - 5, cx + 5, cy + 5], fill=(220, 240, 230))
    for i in range(3):
        off = -7 + i * 7
        draw.line([cx + off, cy - 15, cx + off, cy - 11], fill=col, width=1)
        draw.line([cx + off, cy + 11, cx + off, cy + 15], fill=col, width=1)
        draw.line([cx - 15, cy + off, cx - 11, cy + off], fill=col, width=1)
        draw.line([cx + 11, cy + off, cx + 15, cy + off], fill=col, width=1)
    # rising arrow
    ax0, ay0 = x1 - 26, y1 - 8
    draw.line([x0 + 24, y1 - 10, x1 - 24, y0 + 10], fill=(30, 130, 80), width=2)
    draw.polygon([(x1 - 24, y0 + 10), (x1 - 32, y0 + 12), (x1 - 26, y0 + 18)], fill=(30, 130, 80))
    draw.text((x1 - 24, y1 - 12), "31%", font=font(SANS_B, 8), fill=(30, 110, 70))


def ic_capitol(draw, box, col):
    x0, y0, x1, y1 = box
    base = y1 - 8
    cx = (x0 + x1) // 2
    draw.rectangle([x0 + 7, base - 12, x1 - 7, base], fill=(200, 195, 182), outline=col)
    for i in range(5):
        px = x0 + 10 + i * 7
        if px < x1 - 8:
            draw.line([(px, base - 12), (px, base)], fill=col, width=1)
    draw.rectangle([x0 + 9, base - 17, x1 - 9, base - 12], fill=(215, 210, 198), outline=col)
    draw.pieslice([cx - 11, base - 29, cx + 11, base - 13], 180, 360, fill=(215, 210, 198), outline=col)
    draw.ellipse([cx - 2, base - 33, cx + 2, base - 29], fill=col)
    # resignation X on paper
    draw.rectangle([x1 - 12, y0 + 5, x1 - 2, y0 + 15], fill=(255, 255, 255), outline=col)
    draw.line([x1 - 10, y0 + 7, x1 - 4, y0 + 13], fill=(180, 40, 35), width=1)
    draw.line([x1 - 4, y0 + 7, x1 - 10, y0 + 13], fill=(180, 40, 35), width=1)


def ic_corvette(draw, box, col):
    x0, y0, x1, y1 = box
    wy = y1 - 14
    draw.rectangle([x0, wy + 5, x1, y1], fill=(150, 190, 205))
    hull = [(x0 + 4, wy), (x1 - 14, wy), (x1 - 6, wy + 8), (x0 + 8, wy + 8)]
    draw.polygon(hull, fill=(95, 105, 115), outline=col)
    draw.rectangle([x0 + 22, wy - 12, x0 + 34, wy], fill=(95, 105, 115), outline=col)
    draw.line([x0 + 28, wy - 12, x0 + 30, wy - 20], fill=col, width=1)
    # explosion
    ex, ey = x1 - 14, wy - 3
    draw.polygon([(ex, ey), (ex - 8, ey - 8), (ex - 3, ey - 4), (ex - 6, ey - 14),
                  (ex + 2, ey - 7), (ex + 6, ey - 12), (ex + 8, ey - 2)],
                 fill=(226, 100, 30))
    draw.ellipse([ex - 3, ey - 6, ex + 3, ey], fill=(247, 200, 60))
    # drones
    for dx, dy in ((x0 + 10, y0 + 10), (x0 + 22, y0 + 6)):
        draw.line([dx - 4, dy, dx + 4, dy], fill=INK, width=1)
        draw.ellipse([dx - 1, dy - 1, dx + 1, dy + 1], fill=INK)


def ic_boat(draw, box, col):
    x0, y0, x1, y1 = box
    wy = y1 - 12
    draw.rectangle([x0, wy + 4, x1, y1], fill=(150, 190, 205))
    hull = [(x0 + 6, wy), (x1 - 6, wy), (x1 - 13, wy + 8), (x0 + 13, wy + 8)]
    draw.polygon(hull, fill=(120, 85, 55), outline=col)
    draw.line([x0 + 24, wy, x0 + 24, wy - 18], fill=(80, 60, 45), width=2)
    draw.polygon([(x0 + 25, wy - 17), (x0 + 38, wy - 12), (x0 + 25, wy - 7)], fill=(235, 230, 215), outline=col)
    # waves
    draw.arc([x0, wy + 5, x0 + 20, wy + 15], 200, 340, fill=(90, 130, 150), width=1)
    draw.arc([x1 - 22, wy + 5, x1 - 2, wy + 15], 200, 340, fill=(90, 130, 150), width=1)
    draw.text((x1 - 14, y0 + 5), "29", font=font(SANS_B, 11), fill=(166, 58, 42))


def ic_island(draw, box, col):
    x0, y0, x1, y1 = box
    wy = y1 - 18
    draw.rectangle([x0, wy + 6, x1, y1], fill=(120, 175, 195))
    draw.arc([x0 + 2, wy, x1 - 2, wy + 12], 200, 340, fill=(70, 120, 145), width=1)
    # island
    draw.ellipse([x0 + 18, wy - 5, x1 - 18, wy + 7], fill=(190, 170, 120), outline=col)
    # palm
    px = (x0 + x1) // 2
    draw.line([px, wy, px + 3, wy - 22], fill=(95, 70, 45), width=2)
    for ang in (-55, -30, 0, 30, 55):
        import math
        ex = px + 3 + 10 * math.sin(math.radians(ang))
        ey = wy - 22 - 5 * math.cos(math.radians(ang))
        draw.line([px + 3, wy - 22, ex, ey], fill=(40, 120, 70), width=2)
    # rising sea
    draw.line([x0 + 4, wy + 2, x1 - 4, wy + 2], fill=(210, 80, 60), width=1)
    draw.polygon([(x1 - 12, wy + 5), (x1 - 6, wy - 3), (x1, wy + 5)], fill=(210, 80, 60))


def ic_spacecraft(draw, box, col):
    x0, y0, x1, y1 = box
    cx, cy = x0 + 18, y0 + 22
    draw.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill=(150, 150, 155), outline=col)
    draw.arc([cx - 10, cy - 10, cx + 6, cy + 8], 120, 320, fill=(100, 100, 105), width=1)
    draw.ellipse([cx - 3, cy - 3, cx + 4, cy + 4], fill=(120, 120, 125))
    # orbit
    draw.arc([cx - 24, cy - 20, cx + 26, cy + 22], 210, 40, fill=(80, 110, 140), width=1)
    # spacecraft
    sx, sy = x1 - 18, y1 - 16
    draw.rectangle([sx - 6, sy - 4, sx + 4, sy + 4], fill=(200, 200, 205), outline=col)
    draw.rectangle([sx - 14, sy - 6, sx - 6, sy + 6], fill=(60, 90, 150), outline=col)
    draw.polygon([(sx + 4, sy - 4), (sx + 10, sy), (sx + 4, sy + 4)], fill=(200, 200, 205), outline=col)


ICON_FUNCS = {
    1: ic_cop31, 2: ic_rubble, 3: ic_refinery, 10: ic_tanker, 11: ic_un,
    18: ic_factory_fire, 19: ic_handshake, 24: ic_chip_arrow, 25: ic_capitol,
    31: ic_corvette, 32: ic_boat, 36: ic_island, 39: ic_spacecraft,
}


# ---------------------------------------------------------------- cards
def draw_number_badge(draw, cx, cy, n, bg, fg=(255, 255, 255), rad=9, size=10):
    draw.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], fill=bg, outline=(255, 255, 255), width=1)
    s = str(n)
    f = font(SANS_B, size)
    tw = text_w(draw, s, f)
    draw.text((cx - tw / 2, cy - size * 0.72), s, font=f, fill=fg)


def draw_lead_card(draw, x, y, w, h, story):
    n, region, headline, summary = story
    x, y, w, h = int(x), int(y), int(w), int(h)
    col = REGION_COLOR[region]
    draw.rectangle([x, y, x + w, y + h], fill=PAPER_ALT, outline=col, width=2)
    # colour header bar
    draw.rectangle([x, y, x + w, y + 3], fill=col)
    # icon panel
    ix0, iy0 = x + 7, y + 9
    iw = 96
    icon_area(draw, (ix0, iy0, ix0 + iw, y + h - 7), region)
    ICON_FUNCS[n](draw, (ix0, iy0, ix0 + iw, y + h - 7), col)
    draw_number_badge(draw, ix0 + 10, iy0 + 10, n, col, rad=10, size=11)
    # text
    tx = ix0 + iw + 8
    tw = x + w - 7 - tx
    ty = y + 8
    rf = font(SANS_B, 7)
    draw.text((tx, ty), region, font=rf, fill=col)
    draw.text((tx + text_w(draw, region, rf) + 6, ty), "\u00b7  PICTURED", font=font(SANS, 6), fill=INK_SOFT)
    ty += 10
    hf = font(SERIF_B, 14)
    hlines = wrap_fit(draw, headline, SERIF_B, 14, tw, 2, 10)
    hf = font(SERIF_B, max(10, 14 - max(0, len(hlines) - 1)))
    # recompute font for exact wrap (wrap_fit already used a size); use returned size
    hf, hlines = _wrap_with_size(draw, headline, SERIF_B, 15, tw, 2, 11)
    ty = draw_lines(draw, hlines, hf, tx, ty, tw, hf.size + 1, INK)
    ty += 3
    sf, slines = _wrap_with_size(draw, summary, SANS, 9, tw, 3, 6)
    draw_lines(draw, slines, sf, tx, ty, tw, sf.size + 2, INK_SOFT)


def _wrap_with_size(draw, text, name, size, max_w, max_lines, min_size):
    s = size
    while s > min_size:
        f = font(name, s)
        words = text.split()
        line = ""
        n = 1
        for wd in words:
            trial = (line + " " + wd).strip()
            if text_w(draw, trial, f) <= max_w or not line:
                line = trial
            else:
                n += 1
                line = wd
        if n <= max_lines:
            return f, wrap(draw, text, f, max_w, max_lines)
        s -= 1
    f = font(name, min_size)
    return f, wrap(draw, text, f, max_w, max_lines)


def draw_small_card(draw, x, y, w, h, story):
    n, region, headline, summary = story
    x, y, w, h = int(x), int(y), int(w), int(h)
    col = REGION_COLOR[region]
    draw.rectangle([x, y, x + w, y + h], fill=PAPER_ALT, outline=col, width=1)
    draw.rectangle([x, y, x + w, y + 2], fill=col)
    # icon panel left
    ix0, iy0 = x + 4, y + 5
    iw = 50
    ih = h - 9
    icon_area(draw, (ix0, iy0, ix0 + iw, iy0 + ih), region)
    ICON_FUNCS[n](draw, (ix0, iy0, ix0 + iw, iy0 + ih), col)
    draw_number_badge(draw, ix0 + 8, iy0 + 8, n, col, rad=7, size=8)
    # text
    tx = ix0 + iw + 5
    tw = x + w - 4 - tx
    ty = y + 3
    draw.text((tx, ty), region, font=font(SANS_B, 6), fill=col)
    ty += 8
    hf, hlines = _wrap_with_size(draw, headline, SANS_B, 9, tw, 2, 7)
    ty = draw_lines(draw, hlines, hf, tx, ty, tw, hf.size + 1, INK)
    ty += 2
    sf, slines = _wrap_with_size(draw, summary, SANS, 7, tw, 3, 5)
    draw_lines(draw, slines, sf, tx, ty, tw, sf.size + 1, INK_SOFT)


# ---------------------------------------------------------------- sections
def draw_header(draw):
    # top rule + kicker
    draw.rectangle([0, 0, W, 5], fill=INK)
    draw.text((12, 9), "NEWS SUMMARY  \u00b7  MONDAY 23 NOVEMBER 2026  \u00b7  WORLD EDITION",
              font=font(SANS_B, 9), fill=(150, 40, 35))
    draw.text((W - 12, 9), "41 STORIES  \u00b7  7 REGIONS  \u00b7  ONE DAY",
              font=font(SANS, 9), fill=INK_SOFT, anchor="ra")
    # masthead
    title = "THE WORLD IN ONE DAY"
    f = font(SERIF_B, 62)
    tw = text_w(draw, title, f)
    while tw > W - 30 and f.size > 30:
        f = font(SERIF_B, f.size - 1)
        tw = text_w(draw, title, f)
    draw.text(((W - tw) / 2, 22), title, font=f, fill=INK)
    sub = "Monday, 23 November 2026"
    sf = font(SERIF, 25)
    sw = text_w(draw, sub, sf)
    draw.text(((W - sw) / 2, 86), sub, font=sf, fill=(150, 40, 35))
    # rules around masthead
    draw.line([(12, 83), (12, 110)], fill=INK, width=1)
    draw.line([(W - 12, 83), (W - 12, 110)], fill=INK, width=1)
    draw.line([(12, 113), (W - 12, 113)], fill=INK, width=3)
    draw.line([(12, 117), (W - 12, 117)], fill=INK, width=1)


def draw_ticker(draw, y):
    text = ("LEAD  \u00b7  COP31 collapse  \u00b7  Merkury sunk off Libya  \u00b7  Nvidia reinstates Huang  "
            "\u00b7  Dymer toll 11  \u00b7  Hormuz tanker mines  \u00b7  Indonesia factory fire  "
            "\u00b7  India\u2013Nepal $1.63bn package")
    f = font(SANS_B, 9)
    t, f = fit_line(draw, text, SANS_B, 9, W - 28)
    draw.rectangle([10, y, W - 10, y + 19], fill=(233, 228, 215), outline=RULE_LIGHT)
    draw.text((15, y + 5), t, font=f, fill=INK)


def draw_stats(draw, y):
    cells = [
        ("41", "STORIES", "all dated 23 Nov"),
        ("7", "REGIONS", "Europe to Oceania"),
        ("13", "PICTURED", "illustrated cards"),
        ("28", "LISTED", "regional one-liners"),
        ("23 NOV 2026", "DATE", "Monday, worldwide"),
    ]
    x = 10
    gap = 0
    widths = [196, 150, 190, 190, W - 20 - (196 + 150 + 190 + 190)]
    for (big, label, note), w in zip(cells, widths):
        draw.rectangle([x, y, x + w, y + 39], fill=PAPER_ALT, outline=RULE)
        bf = font(SERIF_B, 23 if len(big) < 6 else 17)
        draw.text((x + 8, y + 5), big, font=bf, fill=INK)
        draw.text((x + 8, y + 27), label, font=font(SANS_B, 7), fill=(150, 40, 35))
        draw.text((x + 8 + text_w(draw, label, font(SANS_B, 7)) + 8, y + 28),
                  note, font=font(SANS, 6), fill=INK_SOFT)
        x += w
    draw.rectangle([10, y, W - 10, y + 39], outline=INK, width=1)


def draw_listed(draw, x, y, w, h):
    # two columns
    draw.rectangle([x, y, x + w, y + h], fill=PAPER_ALT, outline=INK, width=1)
    draw.rectangle([x, y, x + w, y + 16], fill=INK)
    draw.text((x + 6, y + 4), "ALSO IN THE NEWS  \u00b7  28 LISTED STORIES, 7 REGIONS",
              font=font(SANS_B, 8.5), fill=(245, 240, 228))
    body_y = y + 22
    gap = 10
    colw = (w - 12 - gap) / 2
    col1 = x + 6
    col2 = x + 6 + colw + gap
    groups_a = ["EUROPE", "MIDDLE EAST", "ASIA"]
    groups_b = ["AMERICAS", "AFRICA", "OCEANIA", "WORLD"]

    def draw_group(gx, gy, region):
        col = REGION_COLOR[region]
        total = len(LISTED[region]) + len([s for s in PICTURED if s[1] == region])
        bar = 14
        draw.rectangle([gx, gy, gx + colw, gy + bar], fill=col)
        draw.text((gx + 4, gy + 3), region, font=font(SANS_B, 8.5), fill=(255, 255, 255))
        tag = "%d stories" % total
        draw.text((gx + colw - 4, gy + 3), tag, font=font(SANS, 7), fill=(255, 255, 255), anchor="ra")
        gy += bar + 4
        for num, head in LISTED[region]:
            line = "%d. %s" % (num, head)
            txt, f = fit_line(draw, line, SANS, 9, colw - 4, 6)
            draw.text((gx + 2, gy), txt, font=f, fill=INK)
            gy += 14
        return gy + 6

    gy = body_y
    for r in groups_a:
        gy = draw_group(col1, gy, r)
    gy = body_y
    for r in groups_b:
        gy = draw_group(col2, gy, r)
    # tally strip pinned to the panel foot
    draw.line([(x + 6, y + h - 14), (x + w - 6, y + h - 14)], fill=RULE_LIGHT)
    draw.text((x + 6, y + h - 11),
              "13 PICTURED CARDS ABOVE  +  28 LISTED HERE  =  41 STORIES ACROSS 7 REGIONS",
              font=font(SANS_B, 7), fill=INK_SOFT)


def draw_map_panel(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=PAPER_ALT, outline=INK, width=1)
    draw.rectangle([x, y, x + w, y + 16], fill=INK)
    draw.text((x + 6, y + 4), "WHERE IT HAPPENED  \u00b7  DOTS = LAND, PINS = PICTURED STORIES",
              font=font(SANS_B, 7.5), fill=(245, 240, 228))
    mx0, my0 = x + 8, y + 22
    mw = w - 16
    mh = h - 50
    project = draw_dotted_map(draw, mx0, my0, mw, mh)
    # pins
    for n, (lon, lat) in PINS.items():
        px, py = project(lon, lat)
        col = REGION_COLOR[[s for s in PICTURED if s[0] == n][0][1]]
        draw.ellipse([px - 6, py - 6, px + 6, py + 6], fill=col, outline=(255, 255, 255), width=1)
        s = str(n)
        f = font(SANS_B, 6)
        tw = text_w(draw, s, f)
        draw.text((px - tw / 2, py - 3.6), s, font=f, fill=(255, 255, 255))
    # caption
    cy = y + h - 24
    draw.text((x + 6, cy), "Pins 2,3,10,11,18,19,24,25,31,32,36 match the numbered cards.",
              font=font(SANS, 6), fill=INK_SOFT)
    draw.text((x + 6, cy + 9), "COP31 (1) and BepiColombo (39) are global / in space, so unmapped.",
              font=font(SANS, 6), fill=INK_SOFT)


def draw_date_check(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(247, 243, 232), outline=(150, 40, 35), width=2)
    draw.rectangle([x, y, x + w, y + 16], fill=(150, 40, 35))
    draw.text((x + 6, y + 4), "DATE CHECK  \u00b7  ALL 41 STORIES DATED MONDAY 23 NOVEMBER 2026",
              font=font(SANS_B, 8), fill=(255, 250, 240))
    body = ("Every story here happened, or was first reported, on 23 November 2026 in some time zone. "
            "Where an event began earlier, this edition carries only its 23 November development: "
            "the COP31 backlash, the Dymer toll and rescues, Indonesia\u2019s fire confirmation, "
            "Nigeria\u2019s boat update and ESA\u2019s BepiColombo statement. "
            "Excluded: items dated 19\u201322 November with no new 23 November update, and reports we could not date.")
    f = font(SANS, 7.5)
    lines = wrap(draw, body, f, w - 12, 3)
    yy = y + 21
    for ln in lines:
        draw.text((x + 6, yy), ln, font=f, fill=INK_SOFT)
        yy += 10
    draw.text((x + 6, y + h - 11), "Sources: Reuters, AP, CNN, Al Jazeera, BBC, AAP, ESA, NIHR and others.",
              font=font(SANS, 6), fill=INK_SOFT)


def draw_top_stories(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=PAPER_ALT, outline=INK, width=1)
    draw.rectangle([x, y, x + w, y + 16], fill=(150, 40, 35))
    draw.text((x + 6, y + 4), "TOP STORIES TODAY", font=font(SANS_B, 8.5), fill=(255, 250, 240))
    items = [
        ("COP31 collapse", "no deal; reform calls grow"),
        ("Merkury sunk", "Ukrainian drones hit Benghazi"),
        ("Nvidia", "Huang reinstated as CEO"),
        ("Dymer", "toll reaches 11 after strike"),
        ("Strait of Hormuz", "three tankers hit mines"),
        ("Indonesia", "24 dead in factory fire"),
        ("India\u2013Nepal", "$1.63bn rebuild package"),
    ]
    yy = y + 21
    for name, note in items:
        f = font(SANS_B, 8.5)
        draw.ellipse([x + 7, yy + 3, x + 11, yy + 7], fill=(150, 40, 35))
        draw.text((x + 15, yy), name, font=f, fill=INK)
        nx = x + 15 + text_w(draw, name, f) + 5
        nf = font(SANS, 7.5)
        if nx + text_w(draw, note, nf) <= x + w - 6:
            draw.text((nx, yy + 1), note, font=nf, fill=INK_SOFT)
        yy += 15


def draw_footer(draw, y):
    draw.line([(12, y), (W - 12, y)], fill=INK, width=2)
    left = ("News summary image  \u00b7  Monday 23 November 2026  \u00b7  compiled from open reports. "
            "All illustrations are original drawings, not photographs.")
    t, f = fit_line(draw, left, SANS, 7, W - 24, 6)
    draw.text((14, y + 5), t, font=f, fill=INK_SOFT)
    right = "This is a news summary image, not a live news service."
    draw.text((W - 14, y + 16), right, font=font(SANS_B, 7), fill=(150, 40, 35), anchor="ra")


# ---------------------------------------------------------------- compose
def main():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)

    draw_header(draw)

    y = 121
    draw_ticker(draw, y)
    y += 24
    draw_stats(draw, y)
    y += 45

    # lead row: 3 cards
    lead = [PICTURED[0], PICTURED[9], PICTURED[7]]  # COP31, Merkury, Nvidia
    lx = 10
    lgap = 6
    lw = (W - 20 - 2 * lgap) / 3
    lh = 116
    for s in lead:
        draw_lead_card(draw, lx, y, lw, lh, s)
        lx += lw + lgap
    y += lh + 6

    # remaining 10 pictured in 5 columns x 2 rows
    rest = [s for s in PICTURED if s not in lead]
    sw = (W - 20 - 4 * 5) / 5
    sh = 88
    sgap = 5
    for i, s in enumerate(rest):
        r = i // 5
        c = i % 5
        sx = 10 + c * (sw + 5)
        sy = y + r * (sh + sgap)
        draw_small_card(draw, sx, sy, sw, sh, s)
    y += 2 * sh + sgap + 7

    # bottom band: map + top stories on the left, the 28 briefs on the right
    map_w = 338
    map_h = 220
    draw_map_panel(draw, 10, y, map_w, map_h)
    draw_top_stories(draw, 10, y + map_h + 6, map_w, 138)
    panel_h = map_h + 6 + 138
    draw_listed(draw, 10 + map_w + 6, y, W - 20 - map_w - 6, panel_h)
    y += panel_h + 6

    draw_date_check(draw, 10, y, W - 20, 86)
    y += 86 + 8
    draw_footer(draw, y)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img.save(OUT, "PNG", optimize=True)
    return OUT


if __name__ == "__main__":
    path = main()
    print("wrote", path, os.path.getsize(path), "bytes")
