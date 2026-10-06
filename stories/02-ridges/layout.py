#!/usr/bin/env python3
"""Short 02 layout: writes layout.json from shots.json, the traced crops and paint targets
picked on the source PNGs (pixel coordinates in the 1024px drawings).

Usage: python3 stories/02-ridges/layout.py   (after shots.py and the trace step)
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
def word_t(w, after):
    return next(x['s'] for x in words if x['w'].lower().strip(".,?") == w and x['s'] >= after)

# where each drawing sits in its scene: scene id -> [(art id, x, y, w)], scene-local 1080x1920 px
ART = {
    1: [('coins-edge', 540, 760, 860)],
    2: [('house-bricked', 540, 740, 880)],
    3: [('hammer-coin', 360, 470, 500), ('lumpy-coin', 690, 1030, 520)],
    4: [('shears-clip', 560, 500, 820), ('ladle', 560, 1050, 600)],
    5: [('rope', 540, 760, 600)],
    6: [('balance', 540, 760, 820)],
    7: [('screw-press', 340, 470, 500), ('milled-coin', 680, 1010, 420)],
    8: [('chest', 540, 760, 820)],
    9: [('house-open', 430, 640, 760), ('tax-man', 735, 1090, 330)],
    10: [('house-bricked', 540, 740, 880)],
    11: [('coins-edge', 540, 760, 860)],
    12: [('dime-large', 540, 760, 920)],
    13: [('old-bottle', 540, 740, 380)],
}
# paint: (scene, word) -> art id, target (PNG px), R, extras
DIME_RIDGES = (200, 554)
CHEST_POLY = [(232, 512), (698, 440), (838, 560), (322, 650)]
FACE = (512, 459, 418, 243)          # dime-large: the face inside its rim (cx, cy, a, b)
PAINT = {
    (1, 'ridges'): ('coins-edge', DIME_RIDGES, 42, {}),
    (2, 'bricked-up'): ('house-bricked', (257, 472), 40, {}),
    (3, 'silver'): ('hammer-coin', (470, 497), 34, {}),
    (3, 'uneven'): ('lumpy-coin', (915, 500), 36, {}),
    (4, 'off'): ('shears-clip', (300, 300), 28, {}),
    (4, 'clippings'): ('ladle', (330, 500), 40, {}),
    (5, 'hang'): ('rope', (470, 240), 40, {}),
    (6, 'half'): ('balance', None, 34, {}),
    (7, 'ridged'): ('milled-coin', (350, 640), 34, {}),
    (7, 'tell'): ('milled-coin', (365, 305), 26, {}),
    (8, 'full'): ('chest', (520, 560), 50, {'poly': CHEST_POLY, 'dripX': 50}),
    (9, 'windows'): ('house-open', (256, 471), 36, {}),
    (9, 'count'): ('house-open', (508, 471), 36, {}),
    (10, 'bricked'): ('house-bricked', (257, 472), 40, {}),
    (11, 'dimes'): ('coins-edge', DIME_RIDGES, 42, {}),
    (11, 'copper'): ('coins-edge', (703, 504), 50, {'slide_to': (703, 860)}),
    (12, 'silver'): ('dime-large', (512, 459), 62, {'ellipse': FACE}),
    (12, 'ridges'): ('dime-large', (560, 752), 38, {'soak_word': 'stayed'}),
    (13, 'purple'): ('old-bottle', (512, 630), 54, {'soak_word': 'another'}),
}
TARGETS = json.load(open(os.path.join(HERE, 'art', 'targets.json'))) if os.path.exists(os.path.join(HERE, 'art', 'targets.json')) else {}

scenes = []
for sc in shots['scenes']:
    art = [{'id': a, 'x': x, 'y': y, 'w': w} for a, x, y, w in ART[sc['id']]]
    paint = []
    for p in sc['paint']:
        aid, tgt, R, ex = PAINT[(sc['id'], p['word'])]
        if tgt is None:
            tgt = TARGETS[aid]
        e = {'word': p['word'], 't': p['t'], 'art': aid, 'at': frac(aid, *tgt), 'R': R}
        x0, y0, cw, ch = C(aid)
        if 'poly' in ex:
            e['fill'] = {'poly': [frac(aid, *q) for q in ex['poly']], 'drain': p['drain'], 'dripX': round(ex.get('dripX', 0) / cw, 4)}
        if 'ellipse' in ex:
            cx, cy, a, b = ex['ellipse']
            pts = [(cx + a * math.cos(2 * math.pi * k / 48), cy + b * math.sin(2 * math.pi * k / 48)) for k in range(48)]
            e['fill'] = {'poly': [frac(aid, *q) for q in pts], 'drain': p['drain'], 'dripX': round(ex.get('dripX', 0) / cw, 4)}
        if 'slide_to' in ex:
            e['slide'] = {'at': p['slide_at'], 'dur': 0.55, 'hold': 0.3, 'to': frac(aid, *ex['slide_to'])}
        if 'soak' in p:
            e['soak'] = p['soak']
        if 'soak_word' in ex:
            e['soak'] = word_t(ex['soak_word'], p['t'])
        paint.append(e)
    scenes.append({'id': sc['id'], 'art': art, 'paint': paint})

layout = {
    'style': {'ink': 6.4, 'inner': 0.68, 'minLen': 16, 'boil': 0.35, 'boilFps': 4, 'reel': {'on': True}},
    'cover': {'words': ['Ridges.', 'Bricked windows.'], 'art': 'coins-edge', 'at': frac('coins-edge', *DIME_RIDGES),
              'x': 575, 'y': 1150, 'w': 800, 'R': 64},
    'scenes': scenes,
}
with open(os.path.join(HERE, 'layout.json'), 'w') as fh:
    json.dump(layout, fh, indent=1)
print('wrote layout.json:', len(scenes), 'scenes,', sum(len(s['paint']) for s in scenes), 'landings')
