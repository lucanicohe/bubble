#!/usr/bin/env python3
"""
Generates the pixel-art sprite sheets for the Puzzle Bobble clone.

  assets/blob_bubbles.png    8 colours x 32 frames of the little blob character (32x32 per frame)
  assets/hero_character.png  the original wheel-turning blob, palette-swapped to its own unique colour

Run:  python3 tools/make_sprites.py          (from the project folder)
Everything is drawn with hard pixels only: no anti-aliasing, no scaling, 1px black outline,
4-tone ramps (light / base / shade / deep) exactly like the reference screenshot.
"""
import colorsys, math, os, sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, '..', 'source', 'assets')
CELL = 32

# ------------------------------------------------------------------ palettes
# the original blob ramp (base, shade, light, mouth, deep)
RED = dict(base=(217, 87, 99), shade=(187, 57, 69), light=(234, 117, 128), deep=(158, 29, 29))

def hsl_shift(rgb, hue, sm, dl):
    """same recolour maths the game used before, so every colour keeps its familiar identity"""
    r, g, b = [v / 255 for v in rgb]
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    s = min(1, s * sm); l = max(0, min(1, l + dl))
    r, g, b = colorsys.hls_to_rgb((hue % 360) / 360, l, s)
    return tuple(int(round(v * 255)) for v in (r, g, b))

# hue, saturation multiplier, lightness add  (blue red green yellow orange cyan gray purple)
TINT = [(225, 1, -.02), (0, 1, 0), (125, .9, 0), (52, 1.2, .1), (26, 1.2, .02), (195, 1, .05), (220, .12, -.02), (272, 1, 0)]
COLOURS = ['blue', 'red', 'green', 'yellow', 'orange', 'cyan', 'gray', 'purple']

def ramp(i):
    if i == 1:
        return dict(RED)
    hu, sm, dl = TINT[i]
    return {k: hsl_shift(v, hu, sm, dl) for k, v in RED.items()}

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
SWEAT = (120, 224, 255)
GOLD = (255, 236, 150)

# ------------------------------------------------------------------ tiny canvas
class Img:
    def __init__(self): self.p = {}
    def put(self, x, y, c):
        x, y = int(x), int(y)
        if 0 <= x < CELL and 0 <= y < CELL: self.p[(x, y)] = c
    def get(self, x, y): return self.p.get((x, y))
    def to_image(self):
        im = Image.new('RGBA', (CELL, CELL), (0, 0, 0, 0))
        for (x, y), c in self.p.items(): im.putpixel((x, y), c + (255,))
        return im

# ------------------------------------------------------------------ body silhouette
# analytic blob: a squat super-ellipse with two feet, anchored to the bottom row so squash/stretch stays grounded
BOT = 29  # last body row (outline sits on row 30)

def body_mask(sx=1.0, sy=1.0, ball=False):
    """returns set of interior pixels (outline is added later)"""
    m = set()
    cx = 15.5
    if ball:
        r = 12.0 * min(sx, sy) + .2
        cyy = BOT - 1 - 12 * sy
        for y in range(CELL):
            for x in range(CELL):
                if (x + .5 - cx) ** 2 + (y + .5 - cyy) ** 2 <= r * r: m.add((x, y))
        return m
    a = 12.0 * sx; b = 12.2 * sy; n = 2.55
    cy = BOT - 2 - b + 1.0
    for y in range(CELL):
        for x in range(CELL):
            u = abs((x + .5 - cx) / a); v = abs((y + .5 - cy) / b)
            if u ** n + v ** n <= 1: m.add((x, y))
    # little feet
    for fx in (-1, 1):
        fcx = cx + fx * 7.2 * sx
        for y in range(CELL):
            for x in range(CELL):
                if ((x + .5 - fcx) / (4.3 * sx)) ** 2 + ((y + .5 - (BOT - 1.2)) / 2.7) ** 2 <= 1 and y <= BOT: m.add((x, y))
    # bottom notch between the feet
    for y in range(BOT - 2, BOT + 1):
        m.discard((15, y)); m.discard((16, y))
    return m

def hands_mask(sx=1.0, sy=1.0, lift=(0, 0)):
    """two mitten bumps on the sides; lift = how many px each is raised"""
    out = []
    for side, lf in zip((-1, 1), lift):
        hx = 15.5 + side * 10.8 * sx
        hy = BOT - 11.5 * sy - lf
        m = set()
        for y in range(CELL):
            for x in range(CELL):
                if ((x + .5 - hx) / 3.1) ** 2 + ((y + .5 - hy) / 4.3) ** 2 <= 1: m.add((x, y))
        out.append(m)
    return out

def shade_body(img, mask, pal, hands=None, glossy=True):
    """outline + 4-tone shading from simple distance-to-edge rules (light from the top left)"""
    def inside(x, y): return (x, y) in mask
    def run(x, y, dx, dy):
        n = 0
        while inside(x + dx * (n + 1), y + dy * (n + 1)): n += 1
        return n
    for (x, y) in mask:
        dt, db, dl, dr = run(x, y, 0, -1), run(x, y, 0, 1), run(x, y, -1, 0), run(x, y, 1, 0)
        c = pal['base']
        if db < 3 or dr < 3 or (db < 4 and dr < 5): c = pal['shade']
        if dt < 2 or (dl < 2 and dt < 9 and db > 6): c = pal['light']
        if dt == 0 and dl > 3 and dr > 3 and db > 5: c = pal['light']
        img.put(x, y, c)
    if glossy:  # tiny specular glints keep the "bubble" read
        tops = {}
        for (x, y) in mask:
            if x not in tops or y < tops[x]: tops[x] = y
        gx = 8
        if gx in tops:
            gy = tops[gx] + 2
            for (ox, oy) in ((0, 0), (1, 0), (0, 1)): img.put(gx + ox, gy + oy, WHITE)
    # hands
    if hands:
        for hm, side in zip(hands, (-1, 1)):
            for (x, y) in hm:
                dt, db = 0, 0
                while (x, y - dt - 1) in hm: dt += 1
                while (x, y + db + 1) in hm: db += 1
                c = pal['light'] if dt < 2 else pal['base']
                if db < 2: c = pal['shade']
                img.put(x, y, c)
        # hand outline where it sits on the body, and the silhouette outline around everything
        allm = set(mask)
        for hm in hands: allm |= hm
        for hm in hands:
            for (x, y) in hm:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    q = (x + dx, y + dy)
                    if q not in hm and q in mask: img.put(x, y, BLACK)
        mask = allm
    for (x, y) in list(mask):
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + dx, y + dy)
            if q not in mask: img.put(q[0], q[1], BLACK)
    return mask

# ------------------------------------------------------------------ face parts (ASCII patches)
# O black, w white, k pupil(black), d deep mouth colour, t tongue (light), s sweat, . skip, y gold
EYE_OPEN = ["..OOOO..",
            ".OwwwwO.",
            "OwwwwwwO",
            "OwwwwwwO",
            "OwwwwwwO",
            "OwwwwwwO",
            ".OwwwwO.",
            "..OOOO.."]
EYE_BLINK = ["........",
             "........",
             "........",
             "........",
             "OOOOOOOO",
             ".OOOOOO.",
             "........",
             "........"]
EYE_HAPPY = ["........",
             "........",
             "..OOOO..",
             ".OO..OO.",
             "OO....OO",
             "........",
             "........",
             "........"]
EYE_WIDE = ["..OOOO..",
            ".OwwwwO.",
            "OwwwwwwO",
            "OwwwwwwO",
            "OwwwwwwO",
            "OwwwwwwO",
            "OwwwwwwO",
            ".OwwwwO.",
            "..OOOO.."]
EYE_SQUINT_L = ["OOO.....",
                "OwwOOO..",
                "OwwwwOOO",
                "OwwwwwwO",
                "OwwwwwwO",
                ".OwwwwO.",
                "..OOOO.."]
EYE_SQUINT_R = [row[::-1] for row in EYE_SQUINT_L]
EYE_WORRY_L = ["....OOOO",
               "..OOwwwO",
               ".OwwwwwO",
               "OwwwwwwO",
               "OwwwwwwO",
               ".OwwwwO.",
               "..OOOO.."]
EYE_WORRY_R = [row[::-1] for row in EYE_WORRY_L]

MOUTH = {
    'smile': ["O......O",
              ".OOOOOO."],
    'flat': ["OOOOOO"],
    'o': [".OO.",
          "OddO",
          "OddO",
          ".OO."],
    'scream': [".OOOOOO.",
               "OddddddO",
               "OdddddddO"[:8],
               "OdttttdO",
               ".OOOOOO."],
    'wavy': [".O..O..O..O.",
             "O.OO.OO.OO.O"],
    'grin': ["OOOOOOOOOO",
             "OwwwwwwwwO",
             ".OddddddO.",
             "..OOOOOO.."],
    'cat': ["O...O...O",
            ".OOO.OOO."],
    'gritted': ["OOOOOOOO",
                "OwOwOwOO",
                "OOOOOOOO"],
    'wobble': [".OOOOOO.",
               "OddddddO",
               ".OOOOOO."],
}

def stamp(img, patch, x0, y0, pal, flip=False):
    for j, row in enumerate(patch):
        r = row[::-1] if flip else row
        for i, ch in enumerate(r):
            x, y = x0 + i, y0 + j
            if ch == '.': continue
            c = {'O': BLACK, 'k': BLACK, 'w': WHITE, 'd': pal['deep'], 't': pal['light'], 's': SWEAT, 'y': GOLD}.get(ch)
            if c: img.put(x, y, c)

def pupil(img, ex, ey, dx, dy, size=(2, 3)):
    """pupil inside an EYE_OPEN stamped at ex,ey; dx,dy shift within the white"""
    px, py = ex + 3 + dx, ey + 2 + dy
    for j in range(size[1]):
        for i in range(size[0]):
            img.put(px + i, py + j, BLACK)

# ------------------------------------------------------------------ frame builders
EX_L, EX_R = 7, 17   # left/right x of eye patches (8 wide)

def face(img, pal, top, eyes='open', look=(0, 0), mouth='smile', sweat=False, wide=False, tilt=0, mdy=11):
    """top = y of the eyes' top; mouth sits below"""
    ey = top
    if eyes == 'open':
        stamp(img, EYE_OPEN, EX_L, ey, pal); stamp(img, EYE_OPEN, EX_R, ey, pal)
        pupil(img, EX_L, ey, look[0] - 1, look[1] + 1)
        pupil(img, EX_R, ey, look[0] - 1, look[1] + 1)
    elif eyes == 'blink':
        stamp(img, EYE_BLINK, EX_L, ey, pal); stamp(img, EYE_BLINK, EX_R, ey, pal)
    elif eyes == 'happy':
        stamp(img, EYE_HAPPY, EX_L, ey, pal); stamp(img, EYE_HAPPY, EX_R, ey, pal)
    elif eyes == 'wide':
        stamp(img, EYE_WIDE, EX_L, ey - 1, pal); stamp(img, EYE_WIDE, EX_R, ey - 1, pal)
        for ex in (EX_L, EX_R):
            img.put(ex + 3, ey + 3, BLACK); img.put(ex + 4, ey + 3, BLACK)
            img.put(ex + 3, ey + 4, BLACK); img.put(ex + 4, ey + 4, BLACK)
    elif eyes == 'squint':
        stamp(img, EYE_SQUINT_L, EX_L, ey + 1, pal); stamp(img, EYE_SQUINT_R, EX_R, ey + 1, pal)
        for ex, dx in ((EX_L, 3), (EX_R, 3)):
            img.put(ex + dx + look[0], ey + 4, BLACK); img.put(ex + dx + 1 + look[0], ey + 4, BLACK)
            img.put(ex + dx + look[0], ey + 5, BLACK); img.put(ex + dx + 1 + look[0], ey + 5, BLACK)
    elif eyes == 'worry':
        stamp(img, EYE_WORRY_L, EX_L, ey + 1, pal); stamp(img, EYE_WORRY_R, EX_R, ey + 1, pal)
        for ex in (EX_L, EX_R):
            img.put(ex + 3, ey + 4, BLACK); img.put(ex + 4, ey + 4, BLACK)
            img.put(ex + 3, ey + 5, BLACK); img.put(ex + 4, ey + 5, BLACK)
    m = MOUTH[mouth]
    mw = max(len(r) for r in m)
    stamp(img, m, 16 - mw // 2, ey + mdy, pal)
    if sweat:
        stamp(img, [".s.", "sss", "sss", ".s."], 25, ey - 1, pal)
        img.put(26, ey, WHITE)

def make_body(pal, sx=1.0, sy=1.0, hands_lift=(0, 0), ball=False, dy=0, hands=True):
    img = Img()
    mask = body_mask(sx, sy, ball=ball)
    if dy:  # raise the whole thing (jump) by shifting the mask
        mask = {(x, y - dy) for (x, y) in mask}
    hm = hands_mask(sx, sy, hands_lift) if hands and not ball else None
    if hm and dy: hm = [{(x, y - dy) for (x, y) in h} for h in hm]
    shade_body(img, mask, pal, hm, glossy=True)
    return img

def top_of(sy, dy=0):
    # y of the eyes' top for a given vertical scale
    return int(round(BOT - 20.5 * sy - dy))

def idle_frames(pal):
    fr = []
    #            sx    sy   (neutral, squash, neutral, stretch)
    for sx, sy in ((1.0, 1.0), (1.05, .94), (1.0, 1.0), (.96, 1.05)):
        img = make_body(pal, sx, sy)
        face(img, pal, top_of(sy), 'open', (0, 0), 'smile')
        fr.append(img)
    return fr

def blink(pal):
    img = make_body(pal); face(img, pal, top_of(1), 'blink', mouth='smile'); return img

def look_frames(pal):
    out = []
    for lx, ly in ((-2, 0), (0, -1), (2, 0)):
        img = make_body(pal); face(img, pal, top_of(1), 'open', (lx, ly), 'smile'); out.append(img)
    return out

def scared_frames(pal):
    out = []
    for k in range(2):
        img = make_body(pal, 1.0 + .02 * k, 1.0 - .02 * k)
        # shiver: shift everything 1px sideways on alternating frames
        face(img, pal, top_of(1), 'wide', mouth='wavy', sweat=(k == 0))
        out.append(shift(img, 1 if k else -1, 0))
    return out

def grin(pal):
    img = make_body(pal, 1.04, .96); face(img, pal, top_of(.96), 'squint', mouth='grin'); return img

def shift(img, dx, dy):
    o = Img()
    for (x, y), c in img.p.items(): o.put(x + dx, y + dy, c)
    return o

def rot90(img, k, cx=15.5, cy=15.5, only=None):
    o = Img()
    for (x, y), c in img.p.items():
        if only is not None and (x, y) not in only: o.put(x, y, c); continue
        u, v = x + .5 - cx, y + .5 - cy
        for _ in range(k % 4): u, v = -v, u
        o.put(int(math.floor(u + cx)), int(math.floor(v + cy)), c)
    return o

def roll_frames(pal):
    """the launched character curls into a ball and tumbles: the face rotates in clean 90 degree steps"""
    out = []
    for k in range(4):
        body = Img(); mask = body_mask(1, 1, ball=True)
        shade_body(body, mask, pal, None, glossy=True)
        f = Img()
        face(f, pal, 10, 'squint', mouth='gritted')
        # a little arm nub so the rotation reads
        for yy in (14, 15, 16): f.put(3, yy, pal['light']); f.put(2, yy, BLACK)
        f = rot90(f, k)
        # compose: face over body, clipped to the ball
        for (x, y), c in f.p.items():
            if (x, y) in mask: body.put(x, y, c)
        out.append(body)
    return out

def land_frames(pal):
    out = []
    for sx, sy, mouth, eyes, mdy in ((1.14, .82, 'flat', 'blink', 7), (.92, 1.1, 'smile', 'open', 11), (1.04, .96, 'smile', 'open', 10)):
        img = make_body(pal, sx, sy); face(img, pal, top_of(sy), eyes, mouth=mouth, mdy=mdy); out.append(img)
    return out

def fall_frames(pal):
    out = []
    for k in range(2):
        img = make_body(pal, .98, 1.02, hands_lift=(7 + 2 * k, 9 - 2 * k), dy=1 + k)
        face(img, pal, top_of(1.02, 1 + k), 'wide', mouth='scream')
        out.append(img)
    return out

def wave_frames(pal):
    out = []
    for k in range(2):
        sx, sy = (1.0, 1.0) if k == 0 else (1.04, .95)
        img = make_body(pal, sx, sy, hands_lift=(0, 11 if k == 0 else 8))
        face(img, pal, top_of(sy), 'happy' if k else 'open', (1, 0), 'smile' if k == 0 else 'cat')
        out.append(img)
    return out

def whiten(img, t):
    o = Img()
    for (x, y), c in img.p.items():
        if c == BLACK: o.put(x, y, c if t < .8 else WHITE); continue
        o.put(x, y, tuple(int(c[i] + (255 - c[i]) * t) for i in range(3)))
    return o

def pop_frames(pal):
    out = []
    # 0: surprised, stretched, half flashed
    img = make_body(pal, .92, 1.12); face(img, pal, top_of(1.12), 'wide', mouth='o'); out.append(whiten(img, .45))
    # 1: pure white flash silhouette, slightly bigger
    img = make_body(pal, 1.08, 1.06, hands=True)
    sil = Img()
    for (x, y), c in img.p.items(): sil.put(x, y, WHITE if c != BLACK else pal['light'])
    out.append(sil)
    # 2..5: shards flying out + a star
    cols = [pal['light'], pal['base'], pal['shade'], pal['base'], pal['light'], pal['base'], pal['shade'], pal['light']]
    for k, (rad, sz) in enumerate(((7, 3), (11, 3), (13, 2), (14, 1))):
        o = Img()
        cx, cy = 15.5, 16
        for i in range(8):
            a = i * math.pi / 4 + (.2 if k % 2 else 0)
            x = cx + math.cos(a) * rad * (1.0 if i % 2 == 0 else .8)
            y = cy + math.sin(a) * rad * (1.0 if i % 2 == 0 else .8)
            xi, yi = int(round(x - sz / 2)), int(round(y - sz / 2))
            for jj in range(sz):
                for ii in range(sz):
                    edge = (ii in (0, sz - 1)) and (jj in (0, sz - 1)) and sz > 2
                    if not edge: o.put(xi + ii, yi + jj, cols[i])
            if sz >= 3: o.put(xi + 1, yi + 1, WHITE)
        # star in the middle shrinking away
        if k < 3:
            r = (4, 3, 1)[k]
            for d in range(-r, r + 1):
                o.put(15 + d, 15, WHITE); o.put(15, 15 + d, WHITE)
            if r >= 3:
                for d in (-1, 1): o.put(15 + d, 15 + d, GOLD); o.put(15 + d, 15 - d, GOLD)
        out.append(o)
    return out

# ------------------------------------------------------------------ sheet layout
FRAMES = [
    ('idle', 4), ('blink', 1), ('look', 3), ('scared', 2), ('grin', 1),
    ('roll', 4), ('land', 3), ('fall', 2), ('wave', 2), ('pop', 6),
]
ORDER = []
off = 0
INDEX = {}
for name, n in FRAMES:
    INDEX[name] = (off, n); off += n
TOTAL = off

def build_row(pal):
    row = []
    row += idle_frames(pal)
    row.append(blink(pal))
    row += look_frames(pal)
    row += scared_frames(pal)
    row.append(grin(pal))
    row += roll_frames(pal)
    row += land_frames(pal)
    row += fall_frames(pal)
    row += wave_frames(pal)
    row += pop_frames(pal)
    assert len(row) == TOTAL, (len(row), TOTAL)
    return row

def build_sheet():
    sheet = Image.new('RGBA', (CELL * TOTAL, CELL * 8), (0, 0, 0, 0))
    for r in range(8):
        for c, f in enumerate(build_row(ramp(r))):
            sheet.alpha_composite(f.to_image(), (c * CELL, r * CELL))
    return sheet

# ------------------------------------------------------------------ the unique wheel character
# hero ramp: exact palette swap of the original red blob (10 colours in total -> clean pixel art)
HERO = {
    (217, 87, 99): (238, 241, 250),    # base   : cool snow white, no bubble colour is anywhere near it
    (187, 57, 69): (178, 190, 218),    # shade
    (234, 117, 128): (255, 255, 255),  # light
}                                      # mouth, outline, eyes, tears and the stick stay exactly as drawn

# the flattened "game over" pancake is painted with the mouth red (172,50,50), so it gets its own swap inside its frame only
PANCAKE_RECT = (163, 245, 52, 22)
PANCAKE = {(172, 50, 50): (160, 174, 208)}

def bake_hero(src_path, dst_path, mapping=HERO):
    im = Image.open(src_path).convert('RGBA')
    px = im.load()
    x0, y0, w0, h0 = PANCAKE_RECT
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if not a: continue
            if x0 <= x < x0 + w0 and y0 <= y < y0 + h0 and (r, g, b) in PANCAKE:
                px[x, y] = PANCAKE[(r, g, b)] + (255,)
            elif (r, g, b) in mapping:
                px[x, y] = mapping[(r, g, b)] + (255,)
    im.save(dst_path)

if __name__ == '__main__':
    os.makedirs(ASSETS, exist_ok=True)
    sheet = build_sheet()
    sheet.save(os.path.join(ASSETS, 'blob_bubbles.png'))
    bake_hero(os.path.join(ASSETS, 'triple_bubble_sprites_-_character.png'), os.path.join(ASSETS, 'hero_character.png'))
    print('frames per row:', TOTAL, INDEX)
