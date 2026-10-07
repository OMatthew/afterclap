#!/usr/bin/env python3
"""Short 03 layout: writes layout.json from shots.json, the traced crops and paint targets
picked on the source PNGs (pixel coordinates in the 1024px drawings).

Usage: python3 stories/03-purple-glass/layout.py   (after shots.py and the trace step)
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
    1: [('glass-panes', 540, 720, 700), ('old-bottle', 700, 862, 157)],   # Short 02's last picture
    2: [('owens-machine', 560, 520, 720), ('carry-in-boy', 330, 1080, 300)],
    3: [('sand-scoop', 540, 760, 820)],
    4: [('glass-pot', 420, 540, 600), ('soap-bar', 680, 1080, 420)],
    5: [('sun-bottle', 540, 740, 760)],
    6: [('half-buried', 540, 760, 860)],
    7: [('ww1-helmet', 540, 780, 680)],
    8: [('owens-machine', 540, 740, 860)],
    9: [('selenium-spoon', 540, 760, 820)],
    10: [('glassblower', 540, 740, 860)],
    11: [('carry-in-boy', 540, 740, 520)],
    12: [('owens-machine', 380, 480, 560), ('boy-door', 690, 1010, 400)],
    13: [('cherry-jar', 540, 760, 640)],
}
POLYS = json.load(open(os.path.join(HERE, 'art', 'polys.json')))
T = json.load(open(os.path.join(HERE, 'art', 'targets.json')))   # paint targets, picked on the source PNGs
# paint: (scene, word) -> art id, target name in targets.json (or PNG point), R, extras
PAINT = {
    (1, 'purple'): ('old-bottle', (512, 630), 34, {}),
    (2, 'machine'): ('owens-machine', 'machine', 40, {}),
    (2, 'kids'): ('carry-in-boy', 'boy', 32, {}),
    (3, 'green'): ('sand-scoop', 'specks', 44, {}),
    (4, 'manganese'): ('glass-pot', 'powder', 30, {}),
    (4, 'soap'): ('soap-bar', 'soap', 40, {}),
    (5, 'lavender'): ('sun-bottle', 'bottle', 40, {}),
    (6, 'purple'): ('half-buried', 'above', 50, {'poly': POLYS['half-buried'], 'dripX': 0}),
    (7, 'scarce'): ('ww1-helmet', 'helmet', 46, {}),
    (8, 'machine'): ('owens-machine', 'machine', 44, {}),
    (8, 'tanks'): ('owens-machine', 'tank', 40, {}),
    (9, 'selenium'): ('selenium-spoon', 'pinch', 24, {}),
    (10, 'blown'): ('glassblower', 'bubble', 40, {}),
    (11, 'hot'): ('carry-in-boy', 'bottles', 34, {}),
    (12, 'jobs'): ('owens-machine', 'machine', 36, {}),
    (12, 'end'): ('boy-door', 'boy', 34, {}),
    (13, 'red'): ('cherry-jar', 'cherries', 44, {}),
}


scenes = []
for sc in shots['scenes']:
    art = [{'id': a, 'x': x, 'y': y, 'w': w} for a, x, y, w in ART[sc['id']]]
    paint = []
    for p in sc['paint']:
        aid, tgt, R, ex = PAINT[(sc['id'], p['word'])]
        if isinstance(tgt, str):
            tgt = T[aid][tgt]
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
    'cover': {'words': ['Made clear.', 'Turned purple.'], 'art': 'sun-bottle', 'at': frac('sun-bottle', *T['sun-bottle']['bottle']),
              'x': 560, 'y': 1150, 'w': 760, 'R': 56},
    'scenes': scenes,
}
with open(os.path.join(HERE, 'layout.json'), 'w') as fh:
    json.dump(layout, fh, indent=1)
print('wrote layout.json:', len(scenes), 'scenes,', sum(len(s['paint']) for s in scenes), 'landings')
