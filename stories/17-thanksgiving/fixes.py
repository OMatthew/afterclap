#!/usr/bin/env python3
"""Short 17 hand fixes to the traced art. Run after trace.py, before inksvg.cjs (idempotent).
- capitol: the two cupola window fills read as a pair of eyes; drop them.
Lincoln and the shopkeeper are traced with TRACE_MIN_SPECK=8 TRACE_MIN_LOOP=8 TRACE_KEEP_LOOPS=lincoln-quill
so Lincoln keeps his beard:
  TRACE_MIN_SPECK=8 TRACE_MIN_LOOP=8 TRACE_KEEP_LOOPS=lincoln-quill python3 tools/trace.py stories/17-thanksgiving lincoln-quill shop-window
"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, 'art', 'traced', 'capitol.json')
d = json.load(open(p)); x0, y0 = d['crop'][:2]
n = len(d.get('fills', []))
d['fills'] = [f for f in d.get('fills', []) if not (440 <= f['cx'] + x0 <= 580 and 250 <= f['cy'] + y0 <= 340)]
json.dump(d, open(p, 'w'))
print(f'capitol: fills {n} -> {len(d["fills"])}')

# lincoln-quill: the tracer drops his beard (fine hatching); add its outline and a few strokes of texture
BEARD = [
    [(458, 360), (450, 388), (440, 410), (433, 430), (433, 450), (441, 466), (456, 480), (471, 491), (486, 500), (501, 503), (515, 499), (522, 489), (520, 476), (514, 470)],
    [(464, 372), (470, 400), (474, 428), (478, 450), (492, 466), (510, 470)],
    [(440, 400), (446, 412)], [(452, 395), (458, 408)], [(437, 425), (445, 437)], [(457, 420), (463, 433)],
    [(438, 442), (448, 453)], [(462, 440), (469, 452)], [(446, 458), (456, 470)], [(458, 470), (466, 482)],
    [(474, 480), (482, 494)], [(486, 488), (490, 500)], [(497, 486), (500, 498)], [(511, 480), (514, 492)],
]
p = os.path.join(HERE, 'art', 'traced', 'lincoln-quill.json')
d = json.load(open(p)); x0, y0 = d['crop'][:2]
d['strokes'] = [s for s in d['strokes'] if not s.get('hand')]
for line in BEARD:
    pts = [[round(x - x0, 1), round(y - y0, 1)] for x, y in line]
    L = sum(((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) ** 0.5 for a, b in zip(pts, pts[1:]))
    d['strokes'].append({'pts': pts, 'closed': False, 'len': round(L, 1), 'fix': True, 'hand': True})
json.dump(d, open(p, 'w'))
print('lincoln-quill: beard added')
