#!/usr/bin/env python3
"""Short 06 layout: writes layout.json from shots.json, the traced crops and paint targets
picked on the source PNGs (pixel coordinates in the 1024px drawings).

Usage: python3 stories/06-margarine/layout.py   (after shots.py and the trace step)
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
    1: [('green-orange', 300, 860, 340), ('margarine-block', 700, 1080, 620)],   # Short 05's last picture, same place
    2: [('butter-dye', 540, 820, 900)],
    3: [('margarine-block', 540, 560, 540), ('patent-bottle', 540, 1080, 700)],
    4: [('cow-hay', 540, 540, 780), ('butter-churn', 560, 1080, 460)],
    5: [('law-book', 540, 560, 620), ('margarine-block', 540, 1060, 560)],
    6: [('shop-counter', 540, 800, 860)],
    7: [('court-front', 540, 800, 820)],
    8: [('margarine-package', 540, 800, 880)],
    9: [('kneading-bag', 540, 800, 860)],
    10: [('diner-plate', 540, 800, 900)],
    11: [('dairy-trio', 540, 800, 980)],
    12: [('margarine-block', 300, 860, 380), ('swiss-hay', 720, 1060, 560)],
}
POLYS = json.load(open(os.path.join(HERE, 'art', 'polys.json')))
T = json.load(open(os.path.join(HERE, 'art', 'targets.json')))   # paint targets, picked on the source PNGs
PAINT = {   # (scene, word[, nth landing on that word in the scene])
    (1, 'pink'): ('margarine-block', 'block', 46, {'tint': [('pink', None)]}),
    (2, 'yellow'): ('butter-dye', 'butter', 46, {'tint': [('yellow', None)]}),
    (2, 'dye'): ('butter-dye', 'bottle', 30, {'tint': [('yellow', None)]}),
    (3, 'patent'): ('patent-bottle', 'seal', 30, {}),
    (3, 'yellow'): ('patent-bottle', 'bottle', 32, {'tint': [('yellow', None)]}),
    (4, 'hay'): ('cow-hay', 'hay', 30, {}),
    (4, 'paler'): ('butter-churn', 'pat', 44, {'tint': [('pale', None), ('yellow', ('dairies', 1))]}),
    (5, 'fake'): ('margarine-block', 'block', 40, {'tint': [('yellow', None)]}),
    (5, 'law'): ('law-book', 'page', 36, {}),
    (5, 'pink'): ('margarine-block', 'block', 44, {'tint': [('pink', None)]}),
    (6, 'pink'): ('shop-counter', 'pushed', 36, {'tint': [('pink', None)]}),
    (7, 'Court'): ('court-front', 'pediment', 36, {}),
    (7, 'forcing'): ('court-front', 'pediment', 40, {'poly': POLYS['pediment'], 'dripX': 0}),
    (8, 'yellow'): ('margarine-package', 'block', 46, {'tint': [('yellow', None)], 'swell': ('forty', 1, 1.45)}),
    (9, 'capsule'): ('kneading-bag', 'bead', 24, {'tint': [('yellow', ('yellow', 1)), ('yellow', ('mixed', 1))], 'swell': ('mixed', 1, 3.4)}),
    (10, 'rule'): ('diner-plate', 'card', 30, {}),
    (10, 'label'): ('diner-plate', 'card2', 26, {}),
    (10, 'triangle'): ('diner-plate', 'pat', 34, {'poly': POLYS['pat'], 'dripX': 0, 'tint': [('yellow', None)]}),
    (11, 'dyed'): ('dairy-trio', 'butter', 34, {'tint': [('yellow', None)]}),
    (11, 'cheese'): ('dairy-trio', 'cheese', 30, {}),
    (12, 'holes'): ('swiss-hay', 'cheese', 34, {}),
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
    'cover': {'words': ['Butter was', 'dyed yellow.'], 'art': 'butter-dye', 'at': frac('butter-dye', 435, 600),
              'x': 540, 'y': 1060, 'w': 1000, 'R': 116, 'color': 'yellow'},
    'scenes': scenes,
}
with open(os.path.join(HERE, 'layout.json'), 'w') as fh:
    json.dump(layout, fh, indent=1)
print('wrote layout.json:', len(scenes), 'scenes,', sum(len(s['paint']) for s in scenes), 'landings')
