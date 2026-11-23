#!/usr/bin/env python3
"""Short 23 hand fixes to the traced art. Run after trace.py, before inksvg.cjs (idempotent: re-trace first to re-run).
- ferry-tiger: the tracer garbles the crewmen's faces and the tiger; simple dot-eye faces, and the tiger redrawn as a
  soggy, half-deflated striped balloon hanging from the boat hook (it read as a live cat).
- radio-room, phone-caller, liner-lookout: the solid eye dots are lost in tracing; put them back (fills). Telegraph key knob.
All coordinates are source PNG pixels (1024).
"""
import json, math, os
HERE = os.path.dirname(os.path.abspath(__file__))
P = lambda a: os.path.join(HERE, 'art', 'traced', a + '.json')

def load(a):
    d = json.load(open(P(a))); return d, d['crop'][0], d['crop'][1]

def inside(s, b, x0, y0):
    return all(b[0] <= x + x0 <= b[2] and b[1] <= y + y0 <= b[3] for x, y in s['pts'])

def add(d, x0, y0, pts, closed=False):
    dense = []   # densify: the stroke model needs several points to give a short line its full width
    for a, b in zip(pts, pts[1:]):
        n = max(1, int(math.hypot(b[0] - a[0], b[1] - a[1]) / 8))
        dense += [(a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n) for k in range(n)]
    pts = dense + [pts[-1]]
    pts = [[round(x - x0, 1), round(y - y0, 1)] for x, y in pts]
    q = pts + pts[:1] if closed else pts
    L = sum(((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) ** 0.5 for a, b in zip(q, q[1:]))
    d['strokes'].append({'pts': pts, 'closed': closed, 'len': round(L, 1), 'fix': True, 'hand': True})

def dot(d, x0, y0, x, y, r=6):
    d.setdefault('fills', []).append({'cx': round(x - x0, 1), 'cy': round(y - y0, 1), 'rx': r, 'ry': r + 0.5, 'fix': True})

def clean(d):
    d['strokes'] = [s for s in d['strokes'] if not s.get('hand')]
    d['fills'] = [f for f in d.get('fills', []) if not f.get('fix')]

# ---- ferry-tiger
d, x0, y0 = load('ferry-tiger'); clean(d)
for box in [(388, 262, 462, 345), (662, 312, 738, 378), (298, 688, 800, 948)]:
    d['strokes'] = [s for s in d['strokes'] if not inside(s, box, x0, y0)]
d['fills'] = [f for f in d['fills'] if not (298 <= f['cx'] + x0 <= 800 and 688 <= f['cy'] + y0 <= 948)]
dot(d, x0, y0, 416, 279, 5); dot(d, x0, y0, 444, 287, 5)
add(d, x0, y0, [(412, 322), (426, 326), (440, 321)])
dot(d, x0, y0, 688, 327, 5); dot(d, x0, y0, 716, 337, 5)
add(d, x0, y0, [(683, 362), (696, 365), (709, 360)])
# soggy balloon: a saggy bag from the knot under the hook down into the water, with stripes and a small simple face
bag = [(486, 664), (470, 690), (430, 712), (382, 742), (352, 784), (346, 830), (366, 868), (414, 888), (480, 894),
       (552, 898), (626, 892), (690, 886), (742, 892), (770, 880), (752, 858), (700, 832), (642, 792), (590, 744),
       (540, 704), (506, 678), (486, 664)]
add(d, x0, y0, bag)
def wedge(p0, p1, w):   # a bold stripe: a closed, tapered band from p0 to p1
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]; L = math.hypot(dx, dy); nx, ny = -dy / L * w / 2, dx / L * w / 2
    m = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2)
    add(d, x0, y0, [p0, (m[0] + nx, m[1] + ny), p1, (m[0] - nx * 0.6, m[1] - ny * 0.6), p0])
for p0, p1 in [((530, 704), (512, 772)), ((578, 742), (552, 822)), ((628, 782), (600, 862)), ((680, 822), (660, 884)),
               ((728, 856), (720, 890)), ((352, 828), (390, 838)), ((362, 862), (396, 866))]:
    wedge(p0, p1, 20)
# two upright ears with an inner line each
add(d, x0, y0, [(372, 754), (364, 716), (382, 706), (406, 730)]); add(d, x0, y0, [(376, 742), (376, 722), (392, 730)])
add(d, x0, y0, [(424, 716), (428, 680), (446, 676), (460, 702)]); add(d, x0, y0, [(432, 706), (436, 688), (448, 696)])
# cat nose, mouth and whiskers
add(d, x0, y0, [(433, 816), (447, 816), (440, 825), (433, 816)])
add(d, x0, y0, [(430, 832), (440, 838), (450, 832)])
for p0, p1 in [((414, 828), (382, 822)), ((414, 836), (384, 842)), ((466, 828), (498, 822)), ((466, 836), (496, 842))]:
    add(d, x0, y0, [p0, p1])
# a striped tail trailing in the water
C = [(768, 882), (806, 874), (846, 882), (878, 870), (900, 846)]
def off(pts, k):
    o = []
    for i, (x, y) in enumerate(pts):
        a_, b_ = pts[max(0, i - 1)], pts[min(len(pts) - 1, i + 1)]
        dx, dy = b_[0] - a_[0], b_[1] - a_[1]; L = math.hypot(dx, dy)
        o.append((x - dy / L * k, y + dx / L * k))
    return o
up, lo = off(C, -12), off(C, 12)
add(d, x0, y0, up + [(906, 842)] + lo[::-1])
for i in (1, 2, 3):
    add(d, x0, y0, [up[i], lo[i]])
for x in (330, 600):   # two drips falling off the wet balloon
    add(d, x0, y0, [(x, 900), (x - 6, 914), (x, 922), (x + 6, 914), (x, 900)])
json.dump(d, open(P('ferry-tiger'), 'w')); print('ferry-tiger fixed')

# ---- eye dots
for a, pts in [('radio-room', [(490, 395), (570, 403)]), ('phone-caller', [(417, 218)]), ('liner-lookout', [(408, 267), (453, 254)])]:
    d, x0, y0 = load(a); clean(d)
    for x, y in pts: dot(d, x0, y0, x, y, 6)
    if a == 'radio-room':
        add(d, x0, y0, [(422, 822) ] + [(445 + 24 * math.cos(u), 825 + 10 * math.sin(u)) for u in [2 * math.pi * k / 20 for k in range(21)]][1:], closed=False)
        add(d, x0, y0, [(445, 836), (445, 872)])
    json.dump(d, open(P(a), 'w')); print(a, 'eyes')
