#!/usr/bin/env python3
"""Short 07 layout: writes layout.json from shots.json, the traced crops and paint targets
picked on the source PNGs (pixel coordinates in the 1024px drawings).

Usage: python3 stories/07-swiss-cheese/layout.py   (after shots.py and the trace step)
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
    1: [('margarine-block', 300, 860, 380), ('swiss-hay', 720, 1060, 560)],   # Short 06's last picture, same place
    2: [('court-front', 540, 800, 820)],
    3: [('cheese-wheel', 540, 820, 900)],
    4: [('hay-stem2', 540, 820, 940)],
    5: [('cow-hay', 540, 800, 880)],
    6: [('milking-machine', 540, 540, 620), ('blind-wedge', 620, 1080, 560)],   # the wedge echoes scene 1's
    7: [('law-book', 540, 800, 760)],
    8: [('hay-pinch', 470, 500, 580), ('rubber-stamp', 620, 1050, 600)],
    9: [('court-front', 540, 500, 600), ('cheese-wheel', 540, 1060, 680)],
    10: [('deli-slicer2', 540, 800, 900)],
    11: [('coin-pea2', 540, 820, 820)],
    12: [('two-slices2', 540, 820, 940)],
    13: [('cheese-pan', 540, 820, 820)],
}
POLYS = {}
T = json.load(open(os.path.join(HERE, 'art', 'targets.json')))   # paint targets, picked on the source PNGs
PAINT = {   # (scene, word[, nth landing on that word in the scene])
    (1, 'holes'): ('swiss-hay', 'cheese', 34, {}),
    (2, 'court'): ('court-front', 'pediment', 36, {}),
    (3, 'gas'): ('cheese-wheel', 'hole', 34, {'swell': ('start', 1, 1.5)}),
    (4, 'Specks'): ('hay-stem2', 'speck', 22, {}),
    (4, 'tubes'): ('hay-stem2', 'tube', 16, {'swell': ('gathers', 1, 3.0)}),
    (5, 'buckets'): ('cow-hay', 'pail', 30, {}),
    (6, 'closed'): ('milking-machine', 'can', 36, {}),
    (7, 'holes'): ('law-book', 'page', 36, {}),
    (8, 'pinch'): ('hay-pinch', 'pinch', 20, {}),
    (8, 'no'): ('rubber-stamp', 'stamp', 34, {}),
    (9, 'court'): ('court-front', 'pediment', 32, {}),
    (9, 'holes'): ('cheese-wheel', 'hole', 30, {'swell': ('back', 1, 1.6)}),
    (10, 'torn'): ('deli-slicer2', 'torn', 32, {}),
    (11, 'dime'): ('coin-pea2', 'coin', 40, {}),
    (11, 'pea'): ('coin-pea2', 'pea', 26, {}),
    (12, 'smallest'): ('two-slices2', 'left', 28, {}),
    (12, 'biggest'): ('two-slices2', 'right', 28, {}),
    (13, 'melt'): ('cheese-pan', 'slice', 34, {}),
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
        paint.append(e)
    scenes.append({'id': sc['id'], 'art': art, 'paint': paint})

layout = {
    'style': {'ink': 6.4, 'inner': 0.68, 'minLen': 16, 'boil': 0.35, 'boilFps': 4, 'reel': {'on': True}, 'hangIntro': True},
    'cover': {'words': ['Cheesemakers', 'went to court.'], 'art': 'cheese-wheel', 'at': frac('cheese-wheel', 628, 642),
              'x': 540, 'y': 1060, 'w': 1000, 'R': 90},
    'scenes': scenes,
}
with open(os.path.join(HERE, 'layout.json'), 'w') as fh:
    json.dump(layout, fh, indent=1)
print('wrote layout.json:', len(scenes), 'scenes,', sum(len(s['paint']) for s in scenes), 'landings')
