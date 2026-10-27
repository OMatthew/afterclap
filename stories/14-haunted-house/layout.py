#!/usr/bin/env python3
"""Short 14 layout: writes layout.json from shots.json, the traced crops and paint targets
picked on the source PNGs (pixel coordinates in the 1024px drawings).

Usage: python3 stories/14-haunted-house/layout.py   (after shots.py and the trace step)
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
    1: [fit('old-house', 860)],
    2: [fit('wagon-roof', 960)],
    3: [fit('old-house', 860)],
    4: [fit('church-manse', 980)],
    5: [fit('stair-ghost', 900)],
    6: [fit('dark-hand', 980)],
    7: [fit('grape-saucer', 900)],
    8: [fit('tipped-outhouse', 900)],
    9: [fit('soaped-window', 900)],
    10: [fit('costume-party', 980)],
    11: [fit('ticket-coins', 900)],
    12: [fit('ticket-line', 900)],
    13: [fit('coin-jar', 760)],
    14: [fit('small-haunts', 980)],
    15: [fit('ghost-top', 900)],
}
POLYS = {}
T = json.load(open(os.path.join(HERE, 'art', 'targets.json')))
CALM = {'splat': {'nSpk': 0, 'nSat': 0, 'drip': 0}}
PAINT = {
    (1, 'haunted'): ('old-house', 'window', 22, CALM),
    (2, 'pranks'): ('wagon-roof', 'wagon', 26, {}),
    (3, 'older'): ('old-house', 'window', 22, CALM),
    (4, "minister's"): ('church-manse', 'door', 22, CALM),
    (5, 'pounced'): ('stair-ghost', 'sheet', 20, CALM),
    (6, 'sponge'): ('dark-hand', 'sponge', 24, CALM),
    (7, 'grapes'): ('grape-saucer', 'saucer', 20, CALM),
    (8, 'outhouses'): ('tipped-outhouse', 'door', 24, {}),
    (9, 'soap'): ('soaped-window', 'squiggle', 20, CALM),
    (10, 'parties'): ('costume-party', 'streamer', 22, CALM),
    (11, 'money'): ('ticket-coins', 'ticket', 28, {}),
    (12, 'tickets'): ('ticket-line', 'door', 26, CALM),
    (13, 'thousands'): ('coin-jar', 'coins', 30, {}),
    (14, 'clubs'): ('small-haunts', 'door', 20, CALM),
    (15, 'ghost'): ('ghost-top', 'sheet', 22, CALM),
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
    'cover': {'words': ['The stairway', 'that leads to death.'], 'art': 'ghost-top', 'at': frac('ghost-top', 351, 150), 'x': 540, 'y': 1230, 'w': 860, 'R': 24, 'splat': {'nSpk': 0, 'nSat': 0, 'drip': 0}},
    'scenes': scenes,
}
with open(os.path.join(HERE, 'layout.json'), 'w') as fh:
    json.dump(layout, fh, indent=1)
print('wrote layout.json:', len(scenes), 'scenes,', sum(len(s['paint']) for s in scenes), 'landings')
