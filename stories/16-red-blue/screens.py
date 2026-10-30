#!/usr/bin/env python3
"""Short 16: clean map outlines on the TV screens.

The tracer turns the tiny state maps on the TV screens into scribbles. This swaps them for one
clean outline of the US (taken from art/us-map.png), fitted to each map's box. Also a few hand fixes
(FIX) for lines the tracer drops: the talkers' profiles, the animals' eyes, the calendar squares.
Run after trace.py (on a fresh trace: it is not idempotent), before inksvg.cjs. All boxes are source-PNG pixels: (x0, y0, x1, y1).
Usage: python3 stories/16-red-blue/screens.py
"""
import json, math, os
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage import measure

HERE = os.path.dirname(os.path.abspath(__file__))
# art id -> list of (erase box, map box)
SCREENS = {
    'two-tvs': [((203, 443, 405, 600), (211, 451, 397, 592)),
                ((573, 430, 792, 600), (580, 438, 783, 592))],
    'three-tvs': [((98, 448, 310, 566), (105, 455, 302, 560)),
                  ((402, 448, 606, 566), (410, 455, 598, 560)),
                  ((694, 448, 906, 568), (700, 455, 900, 562))],
}


def outline():
    a = np.array(Image.open(os.path.join(HERE, 'art', 'us-map.png')).convert('L')) < 150
    a = ndi.binary_closing(a, iterations=6)
    a = ndi.binary_fill_holes(a)
    lab, n = ndi.label(a)
    big = lab == (1 + int(np.argmax(ndi.sum(a, lab, range(1, n + 1)))))
    c = max(measure.find_contours(big.astype(float), 0.5), key=len)       # (row, col)
    c = measure.approximate_polygon(c, 1.6)
    xy = c[:, ::-1]
    return xy, xy.min(0), xy.max(0)


# hand fixes, source-PNG pixels: drop small scribbles in a box, add lines (open), eyes (filled ellipses)
FIX = {
    'two-talking': {
        'add': [
            [(380, 247), (390, 265), (392, 285), (391, 299), (396, 309), (402, 322), (389, 327), (387, 337), (373, 342),
             (385, 350), (380, 359), (377, 366), (370, 370), (350, 370), (342, 372), (334, 392)],     # left man's profile
            [(663, 258), (658, 270), (654, 282), (653, 295), (656, 303), (650, 312), (639, 330), (650, 334), (650, 348),
             (668, 351), (655, 360), (658, 367), (660, 378), (665, 384), (680, 385)],                    # right man's profile
            [(415, 340), (435, 334)], [(411, 355), (425, 364)],                                           # speech ticks
            [(608, 341), (625, 347)], [(607, 362), (622, 359)], [(617, 381), (627, 373)],
        ]},
    'donkey-elephant': {'eyes': [(415, 453, 4.5, 7.5), (568, 457, 4.5, 8)]},
    'calendar': {
        'erase_small': ((300, 380, 512, 690), 62),
        'squares': {'side': 38, 'rot': -14, 'at': [(432, 412), (442, 467), (393, 486), (337, 504), (412, 534), (359, 555),
                                                   (487, 564), (438, 584), (386, 608), (465, 629), (414, 654)]}},
}


def hand(d, f):
    x0, y0 = d['crop'][0], d['crop'][1]
    rng = np.random.default_rng(16)
    def add(pts, closed=False):
        pts = [[round(float(x - x0), 1), round(float(y - y0), 1)] for x, y in pts]
        L = float(np.sum(np.hypot(*np.diff(np.array(pts + pts[:1] if closed else pts), axis=0).T)))
        d['strokes'].append({'pts': pts, 'closed': closed, 'len': round(L, 1), 'fix': True})
    if 'erase_small' in f:
        (bx0, by0, bx1, by1), m = f['erase_small']
        def small(s):
            p = np.array(s['pts']) + [x0, y0]
            w, h = p.max(0) - p.min(0)
            return max(w, h) <= m and all(bx0 <= x <= bx1 and by0 <= y <= by1 for x, y in p)
        d['strokes'] = [s for s in d['strokes'] if not small(s)]
    for line in f.get('add', []):
        add(line)
    if 'squares' in f:
        q = f['squares']; a = math.radians(q['rot'])
        for cx, cy in q['at']:
            h = q['side'] / 2 * (1 + rng.uniform(-0.06, 0.06))
            cs = [(ux * h + rng.uniform(-1.5, 1.5), uy * h + rng.uniform(-1.5, 1.5)) for ux, uy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
            pts = []
            for k in range(4):   # four points per side, so the closed spline keeps its corners
                (ax, ay), (bx, by) = cs[k], cs[(k + 1) % 4]
                for t in (0, 0.33, 0.67):
                    x, y = ax + (bx - ax) * t, ay + (by - ay) * t
                    pts.append((cx + x * math.cos(a) - y * math.sin(a), cy + x * math.sin(a) + y * math.cos(a)))
            add(pts, closed=True)
    for cx, cy, rx, ry in f.get('eyes', []):   # a small closed loop, as the ghost's eyes in Short 14
        add([(cx + rx * math.cos(2 * math.pi * k / 12), cy + ry * math.sin(2 * math.pi * k / 12)) for k in range(12)], closed=True)


def main():
    for aid, f in FIX.items():
        p = os.path.join(HERE, 'art', 'traced', aid + '.json')
        d = json.load(open(p)); n = len(d['strokes'])
        hand(d, f)
        json.dump(d, open(p, 'w'))
        print(f'{aid}: {n} strokes -> {len(d["strokes"])} (hand fixes)')
    xy, lo, hi = outline()
    for aid, boxes in SCREENS.items():
        f = os.path.join(HERE, 'art', 'traced', aid + '.json')
        d = json.load(open(f))
        x0, y0 = d['crop'][0], d['crop'][1]
        inside = lambda p, b: b[0] <= p[0] + x0 <= b[2] and b[1] <= p[1] + y0 <= b[3]
        before = len(d['strokes'])
        d['strokes'] = [s for s in d['strokes'] if not any(all(inside(p, e) for p in s['pts']) for e, _ in boxes)]
        d['fills'] = [q for q in d.get('fills', []) if not any(inside((q['cx'], q['cy']), e) for e, _ in boxes)]
        for _, m in boxes:
            k = min((m[2] - m[0]) / (hi[0] - lo[0]), (m[3] - m[1]) / (hi[1] - lo[1]))
            ox = (m[0] + m[2]) / 2 - k * (lo[0] + hi[0]) / 2 - x0
            oy = (m[1] + m[3]) / 2 - k * (lo[1] + hi[1]) / 2 - y0
            pts = [[round(float(k * x + ox), 1), round(float(k * y + oy), 1)] for x, y in xy]
            L = float(np.sum(np.hypot(*np.diff(np.array(pts), axis=0).T)))
            d['strokes'].append({'pts': pts, 'closed': True, 'len': round(L, 1), 'fix': True})
        json.dump(d, open(f, 'w'))
        print(f'{aid}: {before} strokes -> {len(d["strokes"])} ({len(boxes)} screen outlines, {len(xy)} pts each)')


if __name__ == '__main__':
    main()
