#!/usr/bin/env python3
"""Short 12 layout: writes layout.json from shots.json, the traced crops and paint targets
picked on the source PNGs (pixel coordinates in the 1024px drawings).

Usage: python3 stories/12-jack-o-lantern/layout.py   (after shots.py and the trace step)
"""
import json, math, os

HERE = os.path.dirname(os.path.abspath(__file__))
shots = json.load(open(os.path.join(HERE, 'shots.json')))
words = json.load(open(os.path.join(HERE, 'words.json')))
crop = {}
def C(aid):
    if aid not in crop:
        crop[aid] = json.load(open(os.path.join(HERE, 'art', 'traced', aid + '.json')))['crop']
    return crop[aid]
def frac(aid, x, y):
    x0, y0, w, h = C(aid)
    return [round((x - x0) / w, 4), round((y - y0) / h, 4)]
def word_n(w, n, after):
    hits = [x['s'] for x in words if x['w'].lower().strip(".,?:'\"") == w.lower() and x['s'] >= after - 1e-6]
    return hits[n - 1]

def word_t(w, after):
    return next(x['s'] for x in words if x['w'].lower().strip(".,?") == w and x['s'] >= after)

# where each drawing sits in its scene: scene id -> [(art id, x, y, w)], scene-local 1080x1920 px
def fit(aid, wmax=960, x=540, top=200, bottom=1330):
    """Largest placement of a drawing inside the box above the caption band (captions at y ~1434)."""
    _, _, cw, ch = C(aid)
    w = min(wmax, (bottom - top) * cw / ch)
    return (aid, x, round((top + bottom) / 2), round(w))

ART = {
    1: [fit('pumpkin-lit', 900)],
    2: [fit('jack-devil')],
    3: [fit('jack-turnip')],
    4: [fit('prank-boys', 1000)],
    5: [fit('skull-turnip', 820)],
    6: [fit('hedge-scare', 1000)],
    7: [fit('farm-boy', 600, x=420, top=180, bottom=1020), fit('pumpkin-lit', 400, x=770, top=1010, bottom=1330)],
    8: [fit('old-book', 980)],
    9: [fit('scoop-hands')],
    10: [fit('pumpkin-lit', 900)],
    11: [fit('night-carry')],
    12: [fit('old-book', 980)],
    13: [fit('prank-boys', 1000)],
    14: [fit('party')],
    15: [fit('harvest-porch')],
    16: [fit('penny-journal')],
    17: [fit('lantern-man', 700, top=160, bottom=900), fit('no-list', 940, top=930, bottom=1330)],
    18: [fit('marsh-light', 1000)],
    19: [fit('pumpkin-lit', 900)],
}
POLYS = {}
T = json.load(open(os.path.join(HERE, 'art', 'targets.json')))
CALM = {'splat': {'nSpk': 0, 'nSat': 0, 'drip': 0}}
PAINT = {
    (1, 'pumpkins'): ('pumpkin-lit', 'candle', 22, CALM),
    (2, 'Irish'): ('jack-devil', 'trunk', 22, CALM),
    (3, 'wander'): ('jack-turnip', 'road', 22, CALM),
    (4, 'oldest'): ('prank-boys', 'wall', 24, CALM),
    (5, 'candle'): ('skull-turnip', 'flame', 12, CALM),
    (6, 'boys'): ('hedge-scare', 'hedge', 24, CALM),
    (7, "jack-o'-lanterns"): ('pumpkin-lit', 'candle', 16, CALM),
    (8, 'book'): ('old-book', 'cover', 26, {}),
    (10, 'candle'): ('pumpkin-lit', 'candle', 22, CALM),
    (11, 'carry'): ('night-carry', 'stalk', 20, CALM),
    (12, 'Halloween'): ('old-book', 'picture', 26, {}),
    (13, 'prank'): ('prank-boys', 'wall', 24, CALM),
    (14, 'Partly'): ('party', 'lantern', 26, {}),
    (15, 'pumpkins'): ('harvest-porch', 'pumpkin', 34, {}),
    (16, 'printed'): ('penny-journal', 'lantern', 18, CALM),
    (17, 'lantern'): ('lantern-man', 'lantern', 20, CALM),
    (18, 'light'): ('marsh-light', 'glow', 26, dict(CALM, swell=('light', 2, 1.6))),
    (19, 'carved'): ('pumpkin-lit', 'candle', 22, CALM),
}

scenes = []
for sc in shots['scenes']:
    art = [{'id': a, 'x': x, 'y': y, 'w': w} for a, x, y, w in ART[sc['id']]]
    paint, seen = [], {}
    for p in sc['paint']:
        seen[p['word']] = seen.get(p['word'], 0) + 1
        key = (sc['id'], p['word'], seen[p['word']])
        aid, tgt, R, ex = PAINT[key] if key in PAINT else PAINT[key[:2]]
        if isinstance(tgt, str):
            tgt = T[aid][tgt]
        e = {'word': p['word'], 't': p['t'], 'art': aid, 'at': frac(aid, *tgt), 'R': R}
        x0, y0, cw, ch = C(aid)
        if 'poly' in ex:
            e['fill'] = {'poly': [frac(aid, *q) for q in ex['poly']], 'drain': p['drain'], 'dripX': round(ex.get('dripX', 0) / cw, 4)}
        if 'ellipse' in ex:   # (cx, cy, a, b[, rotation in degrees])
            cx, cy, a, b, *rot = ex['ellipse']
            r = math.radians(rot[0] if rot else 0)
            pts = [(cx + a * math.cos(u) * math.cos(r) - b * math.sin(u) * math.sin(r),
                    cy + a * math.cos(u) * math.sin(r) + b * math.sin(u) * math.cos(r))
                   for u in (2 * math.pi * k / 48 for k in range(48))]
            e['fill'] = {'poly': [frac(aid, *q) for q in pts], 'drain': p['drain'], 'dripX': round(ex.get('dripX', 0) / cw, 4)}
        if 'slide_to' in ex:
            e['slide'] = {'at': p['slide_at'], 'dur': 0.55, 'hold': 0.3, 'to': frac(aid, *ex['slide_to'])}
        if 'soak' in p:
            e['soak'] = p['soak']
        if 'tint' in ex:   # the paint takes this colour where it stands for it: (colour, None = on landing | 'soak')
            def when_t(when):
                if when is None: return p['t']
                if isinstance(when, tuple): return word_n(when[0], when[1], p['t'])
                return p[when]
            e['tint'] = [{'at': when_t(when), 'color': c} for c, when in ex['tint']]
        if 'swell' in ex:   # (word, occurrence after the landing, size factor)
            e['swell'] = {'at': word_n(ex['swell'][0], ex['swell'][1], p['t']), 'k': ex['swell'][2]}
        if 'soak_word' in ex:
            e['soak'] = word_t(ex['soak_word'], p['t'])
        if 'splat' in ex:   # calmer splat on danger beats: no specks, no drip (2026-10-19)
            e['splat'] = ex['splat']
        paint.append(e)
    scenes.append({'id': sc['id'], 'art': art, 'paint': paint})

layout = {
    'style': {'ink': 6.4, 'inner': 0.68, 'minLen': 16, 'boil': 0.35, 'boilFps': 4, 'reel': {'on': True}, 'hangIntro': True},
    'cover': {'words': ['Why carve', 'a face?'], 'art': 'pumpkin-lit', 'at': frac('pumpkin-lit', 512, 672),
              'x': 540, 'y': 1230, 'w': 860, 'R': 24, 'splat': {'nSpk': 0, 'nSat': 0, 'drip': 0}},
    'scenes': scenes,
}
with open(os.path.join(HERE, 'layout.json'), 'w') as fh:
    json.dump(layout, fh, indent=1)
print('wrote layout.json:', len(scenes), 'scenes,', sum(len(s['paint']) for s in scenes), 'landings')
