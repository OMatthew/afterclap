#!/usr/bin/env python3
"""Short 16 layout: writes layout.json from shots.json, the traced crops and paint targets
picked on the source PNGs (pixel coordinates in the 1024px drawings).

Usage: python3 stories/16-red-blue/layout.py   (after shots.py and the trace step)
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
    1: [fit('two-tvs', 980)],
    2: [fit('remote-tv', 900)],
    3: [fit('nbc-map', 1000)],
    4: [fit('big-ben', 900)],
    5: [fit('three-tvs', 1010)],
    6: [fit('remote-tv', 900)],
    7: [fit('donkey-elephant', 960)],
    8: [fit('us-map', 1000)],
    9: [fit('calendar', 880)],
    10: [fit('courthouse', 920)],
    11: [fit('night-tv', 900)],
    12: [fit('newspaper-map', 960)],
    13: [fit('two-talking', 960)],
    14: [fit('donkey-elephant', 960)],
    15: [fit('two-tvs', 980)],
}
T = json.load(open(os.path.join(HERE, 'art', 'targets.json')))
CALM = {'nSpk': 0, 'nSat': 0, 'drip': 0}
def ex(color=None, swell=None, flip=None, calm=True):
    """color: the paint takes it on landing; flip: (word, occurrence, colour) it turns later; swell: (word, n, k)"""
    e = {}
    if color: e['tint'] = [(color, None)] + ([(flip[2], (flip[0], flip[1]), 0.18)] if flip else [])   # the flip is quick: a channel change
    if swell: e['swell'] = swell
    if calm: e['splat'] = CALM
    return e
PAINT = {
    (1, 'red'): ('two-tvs', 'left', 26, ex('red')),
    (1, 'blue'): ('two-tvs', 'right', 26, ex('blue')),
    (2, 'channel'): ('remote-tv', [585, 563], 20, ex()),   # the remote's button: red lead, no party
    (3, 'lit-up'): ('nbc-map', 'bulb', 18, ex('yellow')),
    (3, 'blue'): ('nbc-map', 'blue', 24, ex('blue')),
    (3, 'red'): ('nbc-map', 'red', 26, ex('red')),
    (4, 'conservatives'): ('big-ben', 'clock', 22, ex('blue')),
    (5, 'picked'): ('three-tvs', 'tv1', 22, ex('blue')),
    (5, 'colors'): ('three-tvs', 'tv3', 22, ex('red')),
    (6, 'state'): ('remote-tv', 'screen', 28, ex('red', flip=('change', 1, 'blue'))),
    (7, 'red'): ('donkey-elephant', [690, 330], 28, ex('red')),   # on the backs, like a saddle cloth: never on the belly (wound)
    (7, 'blue'): ('donkey-elephant', [250, 478], 22, ex('blue')),
    (8, 'Bush'): ('us-map', 'texas', 26, ex('red')),
    (8, 'Gore'): ('us-map', 'california', 24, ex('blue')),
    (9, 'five'): ('calendar', 'page', 24, ex()),
    (11, 'red-and-blue'): ('night-tv', 'west', 22, ex('red')),
    (11, 'map'): ('night-tv', 'east', 22, ex('blue')),
    (12, 'map'): ('newspaper-map', [476, 420], 22, ex('red')),   # mid-map (Kansas), not a coast
    (12, 'red'): ('newspaper-map', 'pencil', 18, ex('red')),
    (12, 'R'): ('newspaper-map', [300, 496], 22, ex('red')),   # the hand-lettered R (screens.py)
    (13, 'red'): ('two-talking', 'leftplant', 20, ex('red')),
    (13, 'blue'): ('two-talking', 'rightplant', 20, ex('blue')),
    (14, 'party'): ('donkey-elephant', [690, 330], 28, ex('red')),
    (14, 'colors'): ('donkey-elephant', [250, 478], 22, ex('blue')),
    (15, 'maps'): ('two-tvs', 'left', 26, ex('red')),
    (15, 'coverage'): ('two-tvs', 'right', 26, ex('blue')),
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
            e['tint'] = [dict({'at': when_t(tw[1]), 'color': tw[0]}, **({'dur': tw[2]} if len(tw) > 2 else {})) for tw in ex['tint']]
        if 'swell' in ex:   # (word, occurrence after the landing, size factor)
            e['swell'] = {'at': word_n(ex['swell'][0], ex['swell'][1], p['t']), 'k': ex['swell'][2]}
        if 'soak_word' in ex:
            e['soak'] = word_t(ex['soak_word'], p['t'])
        if 'splat' in ex:   # calmer splat on danger beats: no specks, no drip (2026-10-19)
            e['splat'] = ex['splat']
        paint.append(e)
    scenes.append({'id': sc['id'], 'art': art, 'paint': paint})

layout = {
    'style': {'ink': 6.4, 'inner': 0.68, 'minLen': 16, 'boil': 0.35, 'boilFps': 4, 'reel': {'on': False}, 'loop': True, 'hangIntro': True},
    'cover': {'words': ['Why red', 'for Republicans?'], 'art': 'two-tvs', 'at': frac('two-tvs', 300, 520), 'x': 540, 'y': 1230, 'w': 960, 'R': 30, 'color': 'red', 'splat': {'nSpk': 0, 'nSat': 0, 'drip': 0}},
    'scenes': scenes,
}
with open(os.path.join(HERE, 'layout.json'), 'w') as fh:
    json.dump(layout, fh, indent=1)
print('wrote layout.json:', len(scenes), 'scenes,', sum(len(s['paint']) for s in scenes), 'landings')
