#!/usr/bin/env python3
"""Afterclap trace step: PNG line drawing -> simplified centerline strokes.

The image-model drawings are composition guides, not final line art. This tool
pulls out the centerlines, throws away specks, hatching and fussy detail, and
writes the strokes that carry the shape. The renderer (engine/ink.js) re-inks
them with a hand-drawn stroke model, so every drawing ends up in one hand.

Usage:
  python3 tools/trace.py stories/01-dime            # every art/*.png
  python3 tools/trace.py stories/01-dime goblin     # just one
Writes, per drawing:
  art/traced/<id>.json   strokes (crop-pixel coords), used by the renderer
Then run `node engine/inksvg.cjs <story>` to write art/traced/<id>.svg
(the re-inked, single-colour, transparent SVG).
"""
import json, math, os, sys
from collections import defaultdict

import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage.morphology import skeletonize

# ---------------------------------------------------------------- settings
INK_THRESHOLD = 150      # grey level; the off-white haze around lines sits above this
MIN_SPECK_AREA = 40      # px; smaller ink islands are specks
SPUR_LEN = 14            # px; skeleton whiskers shorter than this are pruned
JOIN_MAX_TURN = 50       # deg; edges meeting at a junction join into one stroke if they turn less
SMOOTH_SIGMA = 2.2       # px; centerline smoothing before simplification
RDP_EPS = 0.9            # px
MIN_STROKE = 26          # px; open strokes shorter than this are dropped (hatching, texture)
MIN_LOOP = 22            # px; closed loops (eyes, rivets) can be a little shorter
CROWD_R = 16             # px; neighbourhood for the crowding test
CROWD_MAX_LEN = 70       # px; only short strokes are crowd-tested
CROWD_LIMIT = 2.4        # other ink per unit of own length inside CROWD_R => texture, drop
ZIGZAG_RATIO = 1.07      # path length / heavily-smoothed length above which a long stroke is ironed flat
ZIGZAG_SIGMA = 7.0
END_JOIN_K = 3.4         # x line width; open ends this close that carry on in the same direction are joined
DUP_K = 3.4              # x line width; a stroke running this close beside a longer one...
DUP_COVER = 0.72         # ...for this share of its length is a double line, and goes


def load_mask(path):
    g = np.asarray(Image.open(path).convert('L'), dtype=np.float32)
    g = ndi.gaussian_filter(g, 0.7)
    m = g < INK_THRESHOLD
    lab, n = ndi.label(m, structure=np.ones((3, 3)))
    if n:
        areas = ndi.sum(m, lab, index=np.arange(1, n + 1))
        keep = np.zeros(n + 1, bool)
        keep[1:] = areas >= MIN_SPECK_AREA
        m = keep[lab]
    m = m | ndi.binary_closing(m, iterations=1)
    return m


# ---------------------------------------------------------------- skeleton -> graph
N8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]


def skeleton_graph(sk):
    H, W = sk.shape
    pts = set(zip(*np.nonzero(sk)))

    def nb(p):
        y, x = p
        return [(y + dy, x + dx) for dy, dx in N8 if (y + dy, x + dx) in pts]

    deg = {p: len(nb(p)) for p in pts}
    nodepix = {p for p in pts if deg[p] != 2}
    # cluster adjacent node pixels into one node
    cid = {}
    nodes = []
    for p in nodepix:
        if p in cid:
            continue
        stack = [p]
        cid[p] = len(nodes)
        members = []
        while stack:
            q = stack.pop()
            members.append(q)
            for r in nb(q):
                if r in nodepix and r not in cid:
                    cid[r] = len(nodes)
                    stack.append(r)
        ys = [m[0] for m in members]
        xs = [m[1] for m in members]
        nodes.append({'y': float(np.mean(ys)), 'x': float(np.mean(xs)),
                      'end': len(members) == 1 and deg[members[0]] <= 1})
    edges = []
    used = set()
    for p in nodepix:
        for q in nb(p):
            if q in nodepix:
                continue
            if (p, q) in used:
                continue
            path = [p, q]
            used.add((p, q))
            prev, cur = p, q
            while cur not in nodepix:
                nxt = [r for r in nb(cur) if r != prev]
                if not nxt:
                    break
                # prefer a node pixel if adjacent (stop cleanly at junctions)
                nn = [r for r in nxt if r in nodepix]
                r = nn[0] if nn else nxt[0]
                path.append(r)
                prev, cur = cur, r
            used.add((path[-1], path[-2]))
            a, b = cid[path[0]], cid.get(path[-1])
            if b is None:
                continue
            edges.append({'a': a, 'b': b, 'pix': path})
    # pure loops (no node pixels)
    seen = set()
    for e in edges:
        seen.update(e['pix'])
    rest = [p for p in pts if p not in seen and p not in nodepix]
    restset = set(rest)
    for p in rest:
        if p not in restset:
            continue
        loop = [p]
        restset.discard(p)
        prev, cur = None, p
        while True:
            nxt = [r for r in nb(cur) if r in restset]
            if not nxt:
                break
            cur = nxt[0]
            restset.discard(cur)
            loop.append(cur)
        if len(loop) > 6:
            edges.append({'a': None, 'b': None, 'pix': loop, 'loop': True})
    return nodes, edges


def plen(xy):
    if len(xy) < 2:
        return 0.0
    d = np.diff(xy, axis=0)
    return float(np.hypot(d[:, 0], d[:, 1]).sum())


def edge_xy(e, nodes):
    xy = np.array([[p[1], p[0]] for p in e['pix']], dtype=float)
    if e.get('a') is not None:
        xy[0] = [nodes[e['a']]['x'], nodes[e['a']]['y']]
    if e.get('b') is not None:
        xy[-1] = [nodes[e['b']]['x'], nodes[e['b']]['y']]
    return xy


def prune_and_assemble(nodes, edges):
    for e in edges:
        e['xy'] = edge_xy(e, nodes)
        e['len'] = plen(e['xy'])
    loops = [e for e in edges if e.get('loop')]
    E = [e for e in edges if not e.get('loop')]
    # prune spurs: free end + short + other end at a junction
    for _ in range(3):
        inc = defaultdict(list)
        for i, e in enumerate(E):
            inc[e['a']].append(i)
            inc[e['b']].append(i)
        drop = set()
        for i, e in enumerate(E):
            da, db = len(inc[e['a']]), len(inc[e['b']])
            if e['len'] < SPUR_LEN and ((da == 1 and db >= 3) or (db == 1 and da >= 3)):
                drop.add(i)
        if not drop:
            break
        E = [e for i, e in enumerate(E) if i not in drop]
    # self-loops at a node become loops
    for e in [e for e in E if e['a'] == e['b'] and e['len'] > 8]:
        loops.append(e)
    E = [e for e in E if e['a'] != e['b']]

    # junction pairing: join edges that continue straight through a node
    inc = defaultdict(list)
    for i, e in enumerate(E):
        inc[e['a']].append((i, 0))
        inc[e['b']].append((i, 1))

    def tangent(e, end):
        xy = e['xy']
        if end == 0:
            p0 = xy[0]
            seg = xy[1:]
        else:
            p0 = xy[-1]
            seg = xy[-2::-1]
        acc = 0.0
        q = seg[-1] if len(seg) else p0
        last = p0
        for s in seg:
            acc += math.hypot(*(s - last))
            last = s
            if acc >= 9:
                q = s
                break
        v = q - p0
        n = math.hypot(*v) or 1.0
        return v / n  # pointing away from the node

    link = {}  # (edge, end) -> (edge, end)
    for node, ends in inc.items():
        if len(ends) < 2:
            continue
        tans = {k: tangent(E[k[0]], k[1]) for k in ends}
        free = list(ends)
        while len(free) >= 2:
            best, bp = None, None
            for i in range(len(free)):
                for j in range(i + 1, len(free)):
                    if free[i][0] == free[j][0]:
                        continue
                    c = float(np.dot(tans[free[i]], tans[free[j]]))
                    turn = 180 - math.degrees(math.acos(max(-1, min(1, c))))
                    if best is None or turn < best:
                        best, bp = turn, (free[i], free[j])
            if bp is None or best > JOIN_MAX_TURN:
                break
            link[bp[0]] = bp[1]
            link[bp[1]] = bp[0]
            free.remove(bp[0])
            free.remove(bp[1])

    # walk chains
    strokes = []
    done = set()

    def chain_from(i, end_in):
        xy = []
        cur, cend = i, end_in
        visited = []
        while True:
            e = E[cur]
            seg = e['xy'] if cend == 0 else e['xy'][::-1]
            xy.extend(seg if not xy else seg[1:])
            done.add(cur)
            visited.append(cur)
            out_end = 1 - cend
            nxt = link.get((cur, out_end))
            if nxt is None or nxt[0] in done:
                closed = nxt is not None and nxt[0] == i
                return np.array(xy), closed
            cur, cend = nxt

    # start at chain ends first (edge ends without a link)
    for i in range(len(E)):
        if i in done:
            continue
        for end in (0, 1):
            if (i, end) not in link:
                if i not in done:
                    xy, closed = chain_from(i, end)
                    strokes.append({'xy': xy, 'closed': False})
                break
    for i in range(len(E)):  # remaining: closed chains
        if i not in done:
            xy, closed = chain_from(i, 0)
            strokes.append({'xy': xy, 'closed': True})
    for e in loops:
        xy = e['xy']
        strokes.append({'xy': np.vstack([xy, xy[:1]]), 'closed': True})
    return strokes


# ---------------------------------------------------------------- geometry
def resample(xy, step):
    L = plen(xy)
    if L < step:
        return xy
    d = np.r_[0, np.cumsum(np.hypot(*np.diff(xy, axis=0).T))]
    s = np.linspace(0, d[-1], max(2, int(round(d[-1] / step)) + 1))
    return np.c_[np.interp(s, d, xy[:, 0]), np.interp(s, d, xy[:, 1])]


def smooth(xy, sigma, closed):
    if len(xy) < 5:
        return xy
    if closed:
        core = xy[:-1]
        out = np.c_[ndi.gaussian_filter1d(core[:, 0], sigma, mode='wrap'),
                    ndi.gaussian_filter1d(core[:, 1], sigma, mode='wrap')]
        return np.vstack([out, out[:1]])
    out = np.c_[ndi.gaussian_filter1d(xy[:, 0], sigma, mode='nearest'),
                ndi.gaussian_filter1d(xy[:, 1], sigma, mode='nearest')]
    out[0], out[-1] = xy[0], xy[-1]
    return out


def rdp(xy, eps):
    if len(xy) < 3:
        return xy
    a, b = xy[0], xy[-1]
    ab = b - a
    n = math.hypot(*ab)
    if n < 1e-9:
        d = np.hypot(*(xy - a).T)
    else:
        d = np.abs(ab[0] * (xy[:, 1] - a[1]) - ab[1] * (xy[:, 0] - a[0])) / n
    i = int(np.argmax(d))
    if d[i] > eps:
        return np.vstack([rdp(xy[:i + 1], eps)[:-1], rdp(xy[i:], eps)])
    return np.vstack([a, b])


def drop_loop_patterns(strokes):
    """Rows of small closed loops (chain links, rivets, rows of windows) are pattern, not shape.
    Eyes and toes (two or three together) stay; runs of four or more go."""
    small = [i for i, s in enumerate(strokes) if s['closed'] and plen(s['xy']) < 110]
    if len(small) < 3:
        return strokes
    cen = {i: strokes[i]['xy'].mean(axis=0) for i in small}
    dia = {i: plen(strokes[i]['xy']) / math.pi for i in small}
    parent = {i: i for i in small}
    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    for a in small:
        for b in small:
            if a < b and math.hypot(*(cen[a] - cen[b])) < 0.9 * (dia[a] + dia[b]) + 8:
                parent[find(a)] = find(b)
    groups = defaultdict(list)
    for i in small:
        groups[find(i)].append(i)
    drop = set(i for g in groups.values() if len(g) >= 4 for i in g)
    return [s for i, s in enumerate(strokes) if i not in drop]


def join_ends(strokes, gap):
    """Join open strokes whose ends nearly touch and carry on in the same direction
    (broken skeleton runs, chain links), so the re-ink draws them as one stroke."""
    def end_dir(xy, end):
        if end == 0:
            p, q = xy[0], xy[min(len(xy) - 1, 5)]
        else:
            p, q = xy[-1], xy[max(0, len(xy) - 6)]
        v = p - q
        n = math.hypot(*v) or 1.0
        return p, v / n   # end point, outward direction
    changed = True
    while changed:
        changed = False
        opens = [i for i, s in enumerate(strokes) if not s['closed'] and len(s['xy']) >= 3]
        best = None
        for ii, i in enumerate(opens):
            for j in opens[ii + 1:]:
                for ei in (0, 1):
                    pi, di = end_dir(strokes[i]['xy'], ei)
                    for ej in (0, 1):
                        pj, dj = end_dir(strokes[j]['xy'], ej)
                        d = math.hypot(*(pj - pi))
                        if d > gap:
                            continue
                        # outward directions should point at each other
                        if float(np.dot(di, -dj)) < math.cos(math.radians(40)):
                            continue
                        if best is None or d < best[0]:
                            best = (d, i, ei, j, ej)
        if best:
            _, i, ei, j, ej = best
            a = strokes[i]['xy'] if ei == 1 else strokes[i]['xy'][::-1]
            b = strokes[j]['xy'] if ej == 0 else strokes[j]['xy'][::-1]
            strokes[i] = {'xy': np.vstack([a, b]), 'closed': False}
            del strokes[j]
            changed = True
    return strokes


# ---------------------------------------------------------------- main per drawing
def trace(png):
    m = load_mask(png)
    ys, xs = np.nonzero(m)
    if not len(ys):
        raise SystemExit(f'no ink in {png}')
    pad = 6
    y0, y1 = max(0, ys.min() - pad), min(m.shape[0], ys.max() + pad + 1)
    x0, x1 = max(0, xs.min() - pad), min(m.shape[1], xs.max() + pad + 1)
    m = m[y0:y1, x0:x1]
    dist = ndi.distance_transform_edt(m)
    sk = skeletonize(m)
    lw = float(np.median(2 * dist[sk])) if sk.any() else 4.0

    # solid fills (eyes, pupils): regions much thicker than a line
    thick = dist > max(3.2, 1.25 * lw)
    thick = ndi.binary_dilation(thick, iterations=int(round(lw)))
    thick &= m
    fills = []
    cands = []
    lab, n = ndi.label(thick)
    for k in range(1, n + 1):
        comp = lab == k
        A = comp.sum()
        if A < 60:
            continue
        cy, cx = ndi.center_of_mass(comp)
        yy, xx = np.nonzero(comp)
        rx = (xx.max() - xx.min() + 1) / 2
        ry = (yy.max() - yy.min() + 1) / 2
        ratio = A / (math.pi * rx * ry)
        # only small, round, solid dots (eyes, pupils, rivets); dense hatching also reads as
        # "thick", so anything ragged or large is left to the skeleton
        if max(rx, ry) > 16 or min(rx, ry) < 3 or ratio < 0.72:
            continue
        cands.append((comp, {'cx': round(float(cx), 1), 'cy': round(float(cy), 1),
                             'rx': round(float(rx), 1), 'ry': round(float(ry), 1)}))
    if len(cands) <= 5:      # many dots = a pattern (dome windows); leave them out
        for comp, f in cands:
            fills.append(f)
            sk[comp] = False

    nodes, edges = skeleton_graph(sk)
    raw = prune_and_assemble(nodes, edges)

    # exterior distance map: which strokes are the silhouette
    solid = ndi.binary_fill_holes(ndi.binary_closing(ndi.binary_dilation(m, iterations=3), iterations=4))
    ext_d = ndi.distance_transform_edt(solid)

    pre = []
    for s in raw:
        xy = s['xy']
        if len(xy) < 2:
            continue
        xy = smooth(resample(xy, 2.0), SMOOTH_SIGMA, s['closed'])
        pre.append({'xy': xy, 'closed': s['closed']})
    pre = drop_loop_patterns(pre)
    pre = join_ends(pre, END_JOIN_K * lw)

    strokes = []
    for s in pre:
        xy = s['xy']
        L = plen(xy)
        # wiggly long strokes (chains, ropes, scalloped edges) read as noise when re-inked:
        # iron them into one calm line
        if not s['closed'] and L > 90 and len(xy) > 12:
            heavy = smooth(xy, ZIGZAG_SIGMA, False)
            if L / max(1.0, plen(heavy)) > ZIGZAG_RATIO:
                xy = heavy
                L = plen(xy)
        if s['closed'] and L < MIN_LOOP:
            continue
        if not s['closed'] and L < MIN_STROKE:
            continue
        xy = rdp(xy, RDP_EPS)
        yi = np.clip(xy[:, 1].astype(int), 0, m.shape[0] - 1)
        xi = np.clip(xy[:, 0].astype(int), 0, m.shape[1] - 1)
        outer = float(np.median(ext_d[yi, xi])) < 3.2 + lw
        strokes.append({'xy': xy, 'closed': s['closed'], 'len': L, 'outer': outer})

    # crowding: short strokes sitting in dense ink are hatching / texture
    skel_xy = np.c_[np.nonzero(sk)[1], np.nonzero(sk)[0]].astype(float)
    tree = None
    try:
        from scipy.spatial import cKDTree
        tree = cKDTree(skel_xy)
    except Exception:
        pass
    kept = []
    for s in strokes:
        if tree is not None and not s['outer'] and s['len'] < CROWD_MAX_LEN:
            samp = resample(s['xy'], 4.0)
            own = cKDTree(samp)
            near = tree.query_ball_point(samp, CROWD_R)
            pts = set(i for lst in near for i in lst)
            # ink nearby that is not this stroke
            other = sum(1 for i in pts if own.query(skel_xy[i])[0] > 3.0)
            s['crowd'] = other / max(1.0, s['len'])
            if s['crowd'] > CROWD_LIMIT:
                continue
        kept.append(s)
    strokes = kept

    # parallel doubles (coin rims, nested frames): keep the longer line only
    if strokes:
        dup_d = DUP_K * lw
        order = sorted(range(len(strokes)), key=lambda i: -strokes[i]['len'])
        kept_pts = []
        keep_idx = []
        for i in order:
            samp = resample(strokes[i]['xy'], 3.0)
            if kept_pts:
                tr = cKDTree(np.vstack(kept_pts))
                dd, _ = tr.query(samp)
                if (dd < dup_d).mean() >= DUP_COVER:
                    continue
            keep_idx.append(i)
            kept_pts.append(samp)
        strokes = [strokes[i] for i in sorted(keep_idx)]

    # orientation (start at the top/left end) and draw order
    for s in strokes:
        xy = s['xy']
        if not s['closed'] and (xy[0][1] - xy[-1][1]) + 0.3 * (xy[0][0] - xy[-1][0]) > 0:
            s['xy'] = xy[::-1]
    strokes.sort(key=lambda s: (0 if s['outer'] else 1, float(s['xy'][:, 1].min()) + 0.25 * float(s['xy'][:, 0].min())))

    h, w = m.shape
    return {
        'id': os.path.splitext(os.path.basename(png))[0],
        'src': os.path.basename(png),
        'crop': [int(x0), int(y0), int(x1 - x0), int(y1 - y0)],
        'size': [int(w), int(h)],
        'lw_src': round(lw, 2),
        'strokes': [{'pts': [[round(float(p[0]), 1), round(float(p[1]), 1)] for p in s['xy']],
                     'closed': bool(s['closed']), 'len': round(s['len'], 1), 'outer': bool(s['outer'])}
                    for s in strokes],
        'fills': fills,
    }


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import artfix  # noqa: E402


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    story = sys.argv[1]
    only = set(sys.argv[2:])
    art = os.path.join(story, 'art')
    out = os.path.join(art, 'traced')
    os.makedirs(out, exist_ok=True)
    for f in sorted(os.listdir(art)):
        if not f.lower().endswith('.png'):
            continue
        aid = os.path.splitext(f)[0]
        if only and aid not in only:
            continue
        res = trace(os.path.join(art, f))
        res, notes = artfix.apply(story, aid, res)   # hand-placed fixes (ridges, bricks), if any
        with open(os.path.join(out, aid + '.json'), 'w') as fh:
            json.dump(res, fh, separators=(',', ':'))
        tot = sum(s['len'] for s in res['strokes'])
        print(f"{aid:18s} strokes {len(res['strokes']):4d}  fills {len(res['fills'])}  ink {tot:7.0f}px  lw_src {res['lw_src']}" + ('  | ' + '; '.join(notes) if notes else ''))


if __name__ == '__main__':
    main()
