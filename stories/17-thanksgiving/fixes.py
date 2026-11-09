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

# store-doors: two small fills inside the wreath read as eyes (Codex cut review 1); drop them
p = os.path.join(HERE, 'art', 'traced', 'store-doors.json')
d = json.load(open(p)); x0, y0 = d['crop'][:2]
n = len(d.get('fills', []))
d['fills'] = [f for f in d.get('fills', []) if not (530 <= f['cx'] + x0 <= 590 and 320 <= f['cy'] + y0 <= 380)]
json.dump(d, open(p, 'w'))
print(f'store-doors: fills {n} -> {len(d["fills"])}')

# store-doors: the traced wreath still reads as a smiling face; redraw it as a leafy ring with a bow
import math
p = os.path.join(HERE, 'art', 'traced', 'store-doors.json')
d = json.load(open(p)); x0, y0 = d['crop'][:2]
def inside(s, b):
    return all(b[0] <= x + x0 <= b[2] and b[1] <= y + y0 <= b[3] for x, y in s['pts'])
d['strokes'] = [s for s in d['strokes'] if not s.get('hand') and not inside(s, (440, 282, 592, 470))]
d['fills'] = [f for f in d.get('fills', []) if not (440 <= f['cx'] + x0 <= 592 and 282 <= f['cy'] + y0 <= 470)]
cx, cy = 515, 392
def add(pts, closed=False):
    pts = [[round(x - x0, 1), round(y - y0, 1)] for x, y in pts]
    q = pts + pts[:1] if closed else pts
    L = sum(((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) ** 0.5 for a, b in zip(q, q[1:]))
    d['strokes'].append({'pts': pts, 'closed': closed, 'len': round(L, 1), 'fix': True, 'hand': True})
add([(cx + (64 + (5 if k % 2 else -1)) * math.cos(2 * math.pi * k / 36), cy + (64 + (5 if k % 2 else -1)) * math.sin(2 * math.pi * k / 36)) for k in range(36)], closed=True)   # leafy outer edge
add([(cx + (38 + (3 if k % 2 else 0)) * math.cos(2 * math.pi * k / 24), cy + (38 + (3 if k % 2 else 0)) * math.sin(2 * math.pi * k / 24)) for k in range(24)], closed=True)   # inner edge
by = cy - 66
add([(cx, by), (cx - 14, by - 12), (cx - 22, by - 4), (cx - 14, by + 6), (cx, by)], closed=False)   # bow loops
add([(cx, by), (cx + 14, by - 12), (cx + 22, by - 4), (cx + 14, by + 6), (cx, by)], closed=False)
add([(cx - 2, by + 2), (cx - 10, by + 22)]); add([(cx + 2, by + 2), (cx + 10, by + 22)])            # tails
json.dump(d, open(p, 'w'))
print('store-doors: wreath redrawn')
