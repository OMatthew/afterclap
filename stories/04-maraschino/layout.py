#!/usr/bin/env python3
"""Short 04 layout: writes layout.json from shots.json, the traced crops and paint targets
picked on the source PNGs (pixel coordinates in the 1024px drawings).

Usage: python3 stories/04-maraschino/layout.py   (after shots.py and the trace step)
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
    1: [('cherry-jar', 540, 760, 640)],                      # Short 03's last picture
    2: [('brine-barrel', 540, 760, 760)],
    3: [('straw-bottle', 320, 720, 400), ('marasca-sprig', 760, 520, 440), ('padlock-chain', 760, 1000, 300)],
    4: [('chemist-bench', 540, 600, 880), ('magnifier-bug', 290, 1100, 390), ('sealed-crate', 790, 1110, 380)],
    5: [('label-pen', 540, 760, 760)],
    6: [('shopper-hand', 540, 760, 940)],
    7: [('dye-bottles', 540, 760, 640)],
    8: [('cherry-jar', 330, 740, 500), ('green-orange', 820, 1010, 340)],   # room around the orange (Fable)
}
POLYS = json.load(open(os.path.join(HERE, 'art', 'polys.json')))
T = json.load(open(os.path.join(HERE, 'art', 'targets.json')))   # paint targets, picked on the source PNGs
# paint: (scene, word) -> art id, target name in targets.json (or PNG point), R, extras
# extras: poly/dripX (fill a shape), tint (the paint takes a colour the narration names: CHANNEL_RULES.md, "The paint")
PAINT = {   # (scene, word[, nth landing on that word in the scene])
    (1, 'red'): ('cherry-jar', (430, 676), 26, {'poly': POLYS['cherry'], 'dripX': 0}),
    (1, 'dye'): ('cherry-jar', (430, 676), 26, {'poly': POLYS['cherry'], 'dripX': 0}),
    (2, 'cherries'): ('brine-barrel', 'top', 54, {'tint': [('pale', ('pale', 1)), ('red', ('red', 1))]}),
    (3, 'marasca'): ('marasca-sprig', 'cherry', 30, {'tint': [('wine', None)]}),
    (3, 'Prohibition'): ('padlock-chain', 'lock', 40, {}),
    (4, 'opening'): ('chemist-bench', 'jar', 32, {}),
    (4, 'liqueur'): ('chemist-bench', 'tube', 20, {}),
    (4, 'insect'): ('magnifier-bug', 'bug', 24, {'ellipse': (446, 430, 129, 89, -18), 'dripX': 0}),   # the bug's body fills red
    (4, 'seized'): ('sealed-crate', 'seal', 28, {}),
    (5, 'imitation'): ('label-pen', 'label', 50, {}),
    (6, 'red'): ('shopper-hand', 'held', 26, {'swell': ('dyed', 1, 1.75)}),   # one jar: lands on "red", swells on "dyed" (Fable)
    (7, '40'): ('dye-bottles', 'tall', 40, {}),
    (7, 'erythrosine'): ('dye-bottles', 'small', 34, {'poly': POLYS['small-bottle'], 'dripX': 0}),
    (8, 'green'): ('green-orange', 'orange', 40, {'poly': POLYS['orange'], 'dripX': 0, 'tint': [('green', None)]}),
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
    'cover': {'words': ['Bleached.', 'Then dyed.'], 'art': 'cherry-jar', 'at': frac('cherry-jar', 430, 676),
              'x': 540, 'y': 1150, 'w': 640, 'R': 56},
    'scenes': scenes,
}
with open(os.path.join(HERE, 'layout.json'), 'w') as fh:
    json.dump(layout, fh, indent=1)
print('wrote layout.json:', len(scenes), 'scenes,', sum(len(s['paint']) for s in scenes), 'landings')
