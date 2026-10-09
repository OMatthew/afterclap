#!/usr/bin/env python3
"""Short 05 layout: writes layout.json from shots.json, the traced crops and paint targets
picked on the source PNGs (pixel coordinates in the 1024px drawings).

Usage: python3 stories/05-oranges/layout.py   (after shots.py and the trace step)
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
    1: [('cherry-jar', 330, 740, 500), ('green-orange', 820, 1010, 340)],   # Short 04's last picture, same place
    2: [('dye-tin', 540, 520, 520), ('court-front', 540, 1030, 620)],
    3: [('orange-branch', 540, 800, 820)],
    4: [('kerosene-stove', 540, 820, 860)],
    5: [('dye-tank', 540, 800, 940)],
    6: [('test-flasks', 540, 500, 640), ('magnifier-peel', 540, 1040, 560)],
    7: [('court-front', 540, 800, 820)],
    8: [('capitol', 540, 560, 800), ('law-book', 540, 1060, 600)],
    9: [('dusty-bottle', 540, 800, 560)],
    10: [('green-orange', 300, 860, 340), ('margarine-block', 700, 1080, 620)],
}
POLYS = json.load(open(os.path.join(HERE, 'art', 'polys.json')))
T = json.load(open(os.path.join(HERE, 'art', 'targets.json')))   # paint targets, picked on the source PNGs
PAINT = {   # (scene, word[, nth landing on that word in the scene])
    (1, 'oranges'): ('green-orange', 'orange', 40, {'poly': POLYS['orange'], 'dripX': 0, 'tint': [('green', None), ('orange', ('orange', 1))]}),
    (2, 'dye'): ('dye-tin', 'powder', 40, {}),
    (2, 'Court'): ('court-front', 'pediment', 36, {}),
    (3, 'green'): ('orange-branch', 'orange', 44, {'ellipse': (503, 697, 140, 140), 'dripX': 0, 'tint': [('green', None)]}),   # holds green (Fable: the flip to orange read as random)
    (4, 'stoves'): ('kerosene-stove', 'stove', 36, {}),   # lands on the stove instead of hanging in the air (Fable)
    (4, 'green'): ('kerosene-stove', 'crate', 46, {'tint': [('green', None)]}),
    (4, 'fumes'): ('kerosene-stove', 'fumes', 30, {}),
    (4, 'pale'): ('kerosene-stove', 'crate', 46, {'tint': [('paleyellow', None)]}),
    (5, '1930s'): ('dye-tank', 'oranges', 56, {'tint': [('paleyellow', None), ('orange', ('orange', 1))]}),
    (6, 'tests'): ('test-flasks', 'liquid', 30, {'ellipse': (752, 742, 132, 70), 'dripX': 0}),
    (6, 'trace'): ('magnifier-peel', 'dots', 22, {}),
    (7, 'Court'): ('court-front', 'pediment', 40, {'poly': POLYS['pediment'], 'dripX': 0}),
    (8, 'Congress'): ('capitol', 'dome', 36, {}),
    (8, 'law'): ('law-book', 'page', 40, {'tint': [('orange', ('oranges', 1))]}),
    (9, 'dye'): ('dusty-bottle', 'body', 34, {'ellipse': (472, 640, 108, 168), 'dripX': 0}),
    (10, 'pink'): ('margarine-block', 'block', 46, {'tint': [('pink', None)]}),
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
    'cover': {'words': ['Ripe.', 'Still green.'], 'art': 'orange-branch', 'at': frac('orange-branch', 503, 697),
              'x': 540, 'y': 1150, 'w': 700, 'R': 100, 'color': 'green'},
    'scenes': scenes,
}
with open(os.path.join(HERE, 'layout.json'), 'w') as fh:
    json.dump(layout, fh, indent=1)
print('wrote layout.json:', len(scenes), 'scenes,', sum(len(s['paint']) for s in scenes), 'landings')
