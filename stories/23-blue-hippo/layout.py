#!/usr/bin/env python3
"""Short 23 layout: writes layout.json from shots.json, the traced crops and paint targets
picked on the source PNGs (pixel coordinates in the 1024px drawings).

Usage: python3 stories/23-blue-hippo/layout.py   (after shots.py and the trace step)
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
    1: [fit('liner-lookout', 1000, top=620)],    # below the on-screen question (style.introTitle)
    2: [fit('letting-go', 960)],
    3: [fit('prize-man', 900)],
    4: [fit('ferry-tiger', 980)],
    5: [fit('cat-wire', 980)],
    6: [fit('empire-hippo', 1000)],
    7: [fit('radio-room', 960)],
    8: [fit('phone-caller', 940)],
    9: [fit('handlers-hippo', 1000)],
}
POLY = json.load(open(os.path.join(HERE, 'art', 'hippo-polys.json')))   # body outlines (head left out), from the source PNGs
T = {'letting-go': {'dragon': [585, 315]}, 'prize-man': {'bag': [702, 351]}}   # Short 18's targets
CALM = {'nSpk': 0, 'nSat': 0, 'drip': 0}
def ex(swell=None, calm=True, exit=None, enter=None):
    e = {}
    if exit: e['exit'] = exit      # paint leaves this landing off the side / straight up (engine, 2026-11-23)
    if enter: e['enter'] = enter   # paint arrives here from the side / straight down
    if swell: e['swell'] = swell
    if calm: e['splat'] = CALM
    return e
PAINT = {   # red lead, except on the hippo, which we call blue: the paint turns blue there and back to red before it jumps
    (1, 'sea'): ('liner-lookout', [742, 860], 40, ex(exit='right')),                    # the lifebuoy's right side: the opening drop falls right of the binoculars, clear of his face
    (2, 'letting'): ('letting-go', 'dragon', 44, ex(enter='right', exit='right')),         # the dragon balloon, above the handlers' heads
    (3, 'back'): ('prize-man', 'bag', 50, ex(enter='right', exit='right')),                # the balloon bag on his shoulder (away from his face)
    (4, 'tiger'): ('ferry-tiger', [862, 640], 32, ex(enter='right', exit='right')),             # the ferry's side, right of the porthole: off the hook point and away from the balloon's face (Fable cut review)
    (5, 'line'): ('cat-wire', [66, 600], 32, ex(enter='left', exit='left')),              # the left pole, nowhere near the smoke (no fire read)
    (6, 'hippo'): ('empire-hippo', [330, 400], 60, dict(ex(enter='left', exit='left'), poly=POLY['empire-hippo'],
                    drain=(('kept', 1, 0.0), ('going', 1, 0.5)), tint=[('blue', -0.93, 0.3)], tint_back=('going', 1, 1.05))),
                    # fills the hippo's body (not its head) in blue; the drop is already blue before it touches the hippo (25.45-25.75),
                    # stays blue through the drain and the drip, and turns red only once it is in empty paper below the feet (Fable cut review)
    (7, 'radioed'): ('radio-room', [118, 560], 32, ex(enter='left', exit='left')),         # the radio set, left of his face
    (8, 'saying'): ('phone-caller', [600, 925], 34, ex(enter='right', exit='right')),     # the phone's base, far below his mouth
    (9, 'blue'): ('handlers-hippo', [370, 360], 60, dict(ex(enter='left'), poly=POLY['handlers-hippo'],
                    drain=(('time', 1, 0.0), ('it', 1, 0.4)), tint=[('blue', -0.98, 0.3)])),     # the hippo's body, blue before it touches; drains and fades blue
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
        if 'drain' in ex and 'drain' not in p:
            p = dict(p, drain=[round(word_n(w, n, sc['start']) + o, 2) for w, n, o in ex['drain']])
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
                if isinstance(when, (int, float)): return round(p['t'] + when, 2)   # seconds from the landing (negative: in flight, before it touches)
                if isinstance(when, tuple): return word_n(when[0], when[1], p['t'])
                return p[when]
            e['tint'] = [dict({'at': when_t(tw[1]), 'color': tw[0]}, **({'dur': tw[2]} if len(tw) > 2 else {})) for tw in ex['tint']]
        if 'swell' in ex:   # (word, occurrence after the landing, size factor)
            e['swell'] = {'at': word_n(ex['swell'][0], ex['swell'][1], p['t']), 'k': ex['swell'][2]}
        if 'soak_word' in ex:
            e['soak'] = word_t(ex['soak_word'], p['t'])
        if 'tint_back' in ex:   # (word, occurrence after the landing, offset s): when the paint turns back to red (engine tintBack)
            w_, n_, o_ = ex['tint_back']
            e['tintBack'] = round(word_n(w_, n_, p['t']) + o_, 2)
        for k in ('exit', 'enter'):
            if k in ex: e[k] = ex[k]
        if 'splat' in ex:   # calmer splat on danger beats: no specks, no drip (2026-10-19)
            e['splat'] = ex['splat']
        paint.append(e)
    scenes.append({'id': sc['id'], 'art': art, 'paint': paint})

layout = {
    'style': {'ink': 6.4, 'inner': 0.68, 'minLen': 5, 'boil': 0.35, 'boilFps': 4, 'reel': {'on': False}, 'loop': True, 'loopFade': [0.75, 0.1], 'introTitle': {'words': ["Why did Macy's", 'ask ships to look', 'for a blue hippo?'], 'until': 2.6, 'fade': 0.4, 'size': 112, 'top': 190}, 'cap': {'size': 80, 'stroke': 1.1, 'maxW': 900}, 'capChars': 24, 'hangIntro': True},
    'cover': {'words': ['Last seen:', 'flying'], 'color': 'blue', 'art': 'empire-hippo', 'at': frac('empire-hippo', 300, 380), 'x': 540, 'y': 1300, 'w': 920, 'R': 92, 'splat': {'nSpk': 0, 'nSat': 0, 'drip': 0}},
    'scenes': scenes,
}
with open(os.path.join(HERE, 'layout.json'), 'w') as fh:
    json.dump(layout, fh, indent=1)
print('wrote layout.json:', len(scenes), 'scenes,', sum(len(s['paint']) for s in scenes), 'landings')
