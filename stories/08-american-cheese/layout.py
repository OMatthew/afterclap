#!/usr/bin/env python3
"""Short 08 layout: writes layout.json from shots.json, the traced crops and paint targets
picked on the source PNGs (pixel coordinates in the 1024px drawings).

Usage: python3 stories/08-american-cheese/layout.py   (after shots.py and the trace step)
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
ART = {
    1: [('cheese-pan', 540, 820, 820)],   # Short 08's last picture, same place
    2: [('cheese-wheel', 540, 820, 900)],
    3: [('ship', 540, 800, 980)],
    4: [('hay-pinch', 540, 800, 860)],
    5: [('cheese-tin', 540, 800, 900)],
    6: [('greasy-pan', 540, 800, 900)],
    7: [('dye-tin', 470, 520, 560), ('cheese-pan', 600, 1060, 640)],
    8: [('wrapped-slices', 540, 800, 860)],
    9: [('patent-bottle', 540, 800, 880)],
    10: [('wrapped-slices', 540, 800, 860)],
}
POLYS = {}
T = json.load(open(os.path.join(HERE, 'art', 'targets.json')))
PAINT = {
    (1, 'melt'): ('cheese-pan', 'slice', 34, {}),
    (2, 'Switzerland'): ('cheese-wheel', 'hole', 34, {'splat': {'nSpk': 0, 'nSat': 0, 'drip': 0}}),
    (3, 'overseas'): ('ship', 'wheels', 28, {}),
    (3, 'spoil'): ('ship', 'wheels', 26, {'swell': ('trip', 1, 1.4)}),
    (4, 'pinch'): ('hay-pinch', 'pinch', 20, {}),
    (5, 'tins'): ('cheese-tin', 'tin', 34, {}),
    (6, 'grease'): ('greasy-pan', 'grease', 40, {}),
    (7, 'salt'): ('dye-tin', 'powder', 30, {}),
    (7, 'smooth'): ('cheese-pan', 'slice', 32, {}),
    (8, 'slice'): ('wrapped-slices', 'top', 38, {'splat': {'nSpk': 0, 'nSat': 0, 'drip': 0}}),
    (9, 'patent'): ('patent-bottle', 'seal', 30, {}),
    (9, 'laxative'): ('patent-bottle', 'bottle', 30, {'splat': {'nSpk': 0, 'nSat': 0, 'drip': 0}}),   # calm: read as blood (2026-10-19)
    (10, 'wrapper'): ('wrapped-slices', 'flap', 30, {}),
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
        if 'splat' in ex:
            e['splat'] = ex['splat']
        paint.append(e)
    scenes.append({'id': sc['id'], 'art': art, 'paint': paint})

layout = {
    'style': {'ink': 6.4, 'inner': 0.68, 'minLen': 16, 'boil': 0.35, 'boilFps': 4, 'reel': {'on': True}, 'hangIntro': True},
    'cover': {'words': ['Patented as', 'a laxative.'], 'art': 'patent-bottle', 'at': frac('patent-bottle', 750, 480),
              'x': 540, 'y': 1060, 'w': 1000, 'R': 80},
    'scenes': scenes,
}
with open(os.path.join(HERE, 'layout.json'), 'w') as fh:
    json.dump(layout, fh, indent=1)
print('wrote layout.json:', len(scenes), 'scenes,', sum(len(s['paint']) for s in scenes), 'landings')
