#!/usr/bin/env python3
"""Hand-placed fixes for traced drawings, from stories/<story>/art/fixes.json.

The tracer drops fine repeated lines as hatching. That's right for texture, but wrong when the
repetition is the subject: the ridges on a coin's edge, the bricks in a blocked-up window. These
fixes redraw those parts as clean, slightly irregular strokes, so the re-inking treats them like
any other line. trace.py applies them after each trace. All coordinates are source PNG pixels.

fixes.json:
{
  "<art id>": [
    {"ridges": {"near": [x, y],      // a point inside the coin's face
                "gap": 11,           // px between ridges along the edge (or "n": count)
                "skip_near": [[x, y, r]],  // no ridges within r of these points (a notch)
                "split": [f0, f1],   // leave this fraction of each ridge clear (a band across the edge)
                "max_angle": 72,     // degrees: how far round the edge the ridges go
                "arc": true}},       // also draw the face's edge where the band meets it
    {"bricks": {"rect": [x0, y0, x1, y1], "rows": 7, "cols": 3}}  // inside a window frame
  ]
}
Usage: python3 tools/artfix.py stories/02-ridges [ids]   (re-applies to existing traced JSON)
"""
import json, math, os, sys
import numpy as np


def _rng(seed):
    return np.random.default_rng(seed)


def _plen(p):
    p = np.asarray(p, float)
    return float(np.sum(np.hypot(*np.diff(p, axis=0).T))) if len(p) > 1 else 0.0


def _line(a, b, k=4):
    return [[round(float(a[0] + (b[0] - a[0]) * t), 1), round(float(a[1] + (b[1] - a[1]) * t), 1)] for t in np.linspace(0, 1, k)]


def _stroke(pts, closed=False):
    return {'pts': pts, 'closed': closed, 'len': round(_plen(pts), 1), 'outer': False, 'fix': True}


def _fit_ellipse(xy):
    """Direct least-squares ellipse fit (Fitzgibbon, Pilu & Fisher 1999), stable form (Halir & Flusser)."""
    p = np.asarray(xy, float)
    mu = p.mean(0); sc = p.std() or 1.0
    x, y = ((p - mu) / sc).T
    D1 = np.c_[x * x, x * y, y * y]
    D2 = np.c_[x, y, np.ones_like(x)]
    S1, S2, S3 = D1.T @ D1, D1.T @ D2, D2.T @ D2
    T = -np.linalg.solve(S3, S2.T)
    M = S1 + S2 @ T
    M = np.array([M[2] / 2, -M[1], M[0] / 2])
    w, v = np.linalg.eig(M)
    v = np.real(v)
    cond = 4 * v[0] * v[2] - v[1] ** 2
    a1 = v[:, np.argmax(cond > 0)]
    A, B, C, D, E, F = np.r_[a1, T @ a1]
    den = B * B - 4 * A * C
    xc = (2 * C * D - B * E) / den
    yc = (2 * A * E - B * D) / den
    num = 2 * (A * E * E + C * D * D - B * D * E + den * F)
    r = math.sqrt((A - C) ** 2 + B * B)
    a = math.sqrt(num * (A + C + r)) / -den
    b = math.sqrt(num * (A + C - r)) / -den
    th = 0.5 * math.atan2(-B, C - A)
    # back to pixel units; make `a` the x-ish semi-axis for th in (-45, 45] degrees
    xc, yc, a, b = xc * sc + mu[0], yc * sc + mu[1], abs(a) * sc, abs(b) * sc
    return xc, yc, a, b, th


def _ell(xc, yc, a, b, th, t):
    c, s = math.cos(th), math.sin(th)
    x, y = a * np.cos(t), b * np.sin(t)
    return np.c_[xc + c * x - s * y, yc + s * x + c * y]


def _inside(xc, yc, a, b, th, p, k=1.0):
    c, s = math.cos(th), math.sin(th)
    dx, dy = p[..., 0] - xc, p[..., 1] - yc
    u, v = c * dx + s * dy, -s * dx + c * dy
    return (u / (a * k)) ** 2 + (v / (b * k)) ** 2 <= 1.0


def ridges(res, cfg, seed):
    x0, y0 = res['crop'][0], res['crop'][1]
    near = np.array(cfg['near'], float) - [x0, y0]
    strokes = res['strokes']
    # the face's rim: the closed inner stroke around `near` (smallest that contains it)
    best = None
    for s in strokes:
        p = np.array(s['pts'])
        if not s['closed'] or len(p) < 8:
            continue
        lo, hi = p.min(0), p.max(0)
        if (lo <= near).all() and (near <= hi).all():
            area = float(np.prod(hi - lo))
            if best is None or area < best[0]:
                best = (area, s)
    if best is None:
        raise SystemExit(f"ridges: no closed stroke around {cfg['near']} in {res['id']}")
    rim = np.array(best[1]['pts'])
    xc, yc, a, b, th = _fit_ellipse(rim)
    flo, fhi = rim.min(0), rim.max(0)
    # the coin's silhouette: outer-stroke points around the rim
    # (only outer strokes that mostly sit around this coin, so a neighbouring coin doesn't count)
    pad = 0.35 * (fhi - flo)
    parts = []
    for s in strokes:
        p = np.array(s['pts'])
        if s['outer'] and ((p >= flo - pad) & (p <= fhi + pad)).all(1).mean() > 0.8:
            parts.append(p)
    if not parts:
        raise SystemExit(f"ridges: no silhouette around {cfg['near']} in {res['id']}")
    sil = np.concatenate(parts)
    slo, shi = sil.min(0), sil.max(0)
    m_lo, m_hi = flo - slo, shi - fhi            # margins: rim width on one side, rim + band on the other
    rim_w = np.minimum(m_lo, m_hi)
    k = float(np.mean((0.5 * (fhi - flo) + rim_w) / (0.5 * (fhi - flo))))
    A, B = a * k, b * k                          # the face's outer edge
    shift = np.where(m_lo > m_hi, -(m_lo - rim_w), m_hi - rim_w)
    sd = shift / (np.linalg.norm(shift) + 1e-9)
    # where the band shows: the face edge's outward normal points along the shift
    T = np.linspace(0, 2 * math.pi, 1441)[:-1]
    P = _ell(xc, yc, A, B, th, T)
    dP = np.gradient(P, axis=0)
    nrm = np.c_[dP[:, 1], -dP[:, 0]]
    nrm /= np.linalg.norm(nrm, axis=1, keepdims=True) + 1e-9
    if np.mean(np.einsum('ij,ij->i', nrm, P - [xc, yc])) < 0:
        nrm = -nrm
    vis = np.einsum('ij,j->i', nrm, sd) > math.cos(math.radians(cfg.get('max_angle', 72)))
    # the visible run as one contiguous arc (rotate the ring so it doesn't wrap)
    start = int(np.argmin(vis)) if not vis.all() else 0
    order = np.roll(np.arange(len(T)), -start)
    run = order[vis[order]]
    arcP = P[run]
    L = _plen(arcP)
    n = int(cfg.get('n') or max(3, round(L / cfg.get('gap', 11))))
    cum = np.r_[0, np.cumsum(np.hypot(*np.diff(arcP, axis=0).T))]
    r = _rng(seed)
    # drop the tracer's leftover ridge fragments inside the band
    def in_band(p):
        if _inside(xc, yc, A, B, th, p, 1.02):
            return False
        return any(_inside(xc, yc, A, B, th, p - lam * shift, 1.03) for lam in np.linspace(0, 1, 12))
    kept = []
    for s in strokes:
        p = np.array(s['pts'])
        if not s['outer'] and s['len'] < 140 and np.mean([in_band(q) for q in p]) > 0.6:
            continue
        kept.append(s)
    res['strokes'] = kept
    skips = [(np.array(q[:2], float) - [x0, y0], q[2]) for q in cfg.get('skip_near', [])]
    added = 0
    for i in range(n):
        d = (i + 0.5) / n * L + r.uniform(-0.12, 0.12) * L / n
        j = int(np.clip(np.searchsorted(cum, d), 0, len(arcP) - 1))
        p = arcP[j]
        q = p + shift * r.uniform(0.9, 1.0)
        mid = (p + q) / 2
        if any(np.hypot(*(mid - c)) < rr for c, rr in skips):
            continue
        p = p + r.normal(0, 0.5, 2)
        if cfg.get('split'):                     # leave a band clear (the copper core on a clad dime)
            f0, f1 = cfg['split']
            res['strokes'].append(_stroke(_line(p, p + (q - p) * f0, 3)))
            res['strokes'].append(_stroke(_line(p + (q - p) * f1, q, 3)))
        else:
            res['strokes'].append(_stroke(_line(p, q)))
        added += 1
    if cfg.get('arc', True):
        res['strokes'].append(_stroke([[round(float(x), 1), round(float(y), 1)] for x, y in arcP[::6]]))
    return f'ridges: {added} on a {L:.0f}px edge, band {np.linalg.norm(shift):.0f}px'


def bricks(res, cfg, seed):
    x0, y0 = res['crop'][0], res['crop'][1]
    X0, Y0, X1, Y1 = cfg['rect']
    X0, X1, Y0, Y1 = X0 - x0, X1 - x0, Y0 - y0, Y1 - y0
    m = 3
    kept = []
    for s in res['strokes']:
        p = np.array(s['pts'])
        inside = ((p[:, 0] > X0 + m) & (p[:, 0] < X1 - m) & (p[:, 1] > Y0 + m) & (p[:, 1] < Y1 - m)).mean()
        if not s['outer'] and inside > 0.7:
            continue
        kept.append(s)
    res['strokes'] = kept
    rows, cols = cfg.get('rows', 7), cfg.get('cols', 3)
    r = _rng(seed)
    h = (Y1 - Y0) / rows
    w = (X1 - X0) / cols
    for i in range(1, rows):
        y = Y0 + i * h + r.normal(0, 0.6)
        res['strokes'].append(_stroke(_line((X0 + 1, y), (X1 - 1, y + r.normal(0, 0.8)))))
    for i in range(rows):
        off = 0.5 * w if i % 2 else 0.0
        xs = [X0 + off + j * w for j in range(cols + 1)]
        for x in xs:
            if X0 + 0.25 * w < x < X1 - 0.25 * w:
                x += r.normal(0, 0.8)
                res['strokes'].append(_stroke(_line((x, Y0 + i * h + 1.5), (x, Y0 + (i + 1) * h - 1.5), 3)))
    return f'bricks: {rows} courses in {X1 - X0:.0f}x{Y1 - Y0:.0f}px'


def apply(story, aid, res):
    path = os.path.join(story, 'art', 'fixes.json')
    if not os.path.exists(path):
        return res, []
    fixes = json.load(open(path)).get(aid, [])
    notes = []
    for k, fx in enumerate(fixes):
        seed = (sum(map(ord, aid)) * 31 + k) & 0xffff
        if 'ridges' in fx:
            notes.append(ridges(res, fx['ridges'], seed))
        if 'bricks' in fx:
            notes.append(bricks(res, fx['bricks'], seed))
    return res, notes


def main():
    story = sys.argv[1]
    only = set(sys.argv[2:])
    import trace as T  # noqa
    fixes = json.load(open(os.path.join(story, 'art', 'fixes.json')))
    for aid in fixes:
        if only and aid not in only:
            continue
        res = T.trace(os.path.join(story, 'art', aid + '.png'))
        res, notes = apply(story, aid, res)
        with open(os.path.join(story, 'art', 'traced', aid + '.json'), 'w') as fh:
            json.dump(res, fh, separators=(',', ':'))
        print(f'{aid:18s} ' + '; '.join(notes))


if __name__ == '__main__':
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main()
