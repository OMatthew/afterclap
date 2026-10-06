// Afterclap hand-ink stroke model. Works in the browser (window.Ink) and in node (require).
//
// A traced centerline goes in; a filled outline of a hand-inked stroke comes out:
// slight wobble, gentle pressure and weight changes, ink pooling where the pen
// lands and stops, small overshoots or gaps at the ends. `progress` draws the
// stroke on (0..1) with a wet pen head; `boil` re-jitters it slightly.
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.Ink = factory();
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  function mulberry32(a) {
    return function () {
      a |= 0; a = (a + 0x6D2B79F5) | 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  // smooth value noise in [-1,1]
  function noise1(seed) {
    const r = mulberry32(seed), N = 97, v = [];
    for (let i = 0; i < N; i++) v.push(r() * 2 - 1);
    return function (x) {
      const i = Math.floor(x), f = x - i, u = f * f * (3 - 2 * f);
      const a = v[((i % N) + N) % N], b = v[(((i + 1) % N) + N) % N];
      return a + (b - a) * u;
    };
  }
  const clamp = (x, a, b) => Math.max(a, Math.min(b, x));
  const smooth = (e0, e1, x) => { const t = clamp((x - e0) / (e1 - e0), 0, 1); return t * t * (3 - 2 * t); };
  const f1 = n => (Math.round(n * 10) / 10).toString();

  // Catmull-Rom densify to roughly `step` px spacing
  function densify(P, step) {
    if (P.length < 2) return P.slice();
    const out = [];
    for (let i = 0; i < P.length - 1; i++) {
      const p0 = P[Math.max(0, i - 1)], p1 = P[i], p2 = P[i + 1], p3 = P[Math.min(P.length - 1, i + 2)];
      const L = Math.hypot(p2[0] - p1[0], p2[1] - p1[1]);
      const n = Math.max(1, Math.ceil(L / step));
      for (let k = 0; k < n; k++) {
        const t = k / n, t2 = t * t, t3 = t2 * t;
        const x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3);
        const y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3);
        out.push([x, y]);
      }
    }
    out.push(P[P.length - 1].slice());
    return out;
  }

  // Prepare a stroke once (geometry that doesn't change per frame).
  // pts: [[x,y],...] already in output pixels. opts: {w, seed, closed}
  function prepare(pts, opts) {
    const seed = opts.seed | 0;
    const r = mulberry32(seed * 7919 + 13);
    let P = pts.map(p => [p[0], p[1]]);
    const tan = (a, b) => { const dx = b[0] - a[0], dy = b[1] - a[1], l = Math.hypot(dx, dy) || 1; return [dx / l, dy / l]; };
    const w = opts.w;
    // end behaviour: overshoot (+) or small gap (-), in px
    const endAdj = () => { const u = r(); return u < 0.22 ? -(0.6 + r() * 1.4) * w * 0.35 : (r() * r()) * w * 0.9; };
    if (opts.closed) {
      // hand-closed loop: run a little past the start, or stop just short
      P = P.slice(0, -1);
      const u = r(), over = u < 0.3 ? -(0.5 + r()) * w * 0.4 : (0.4 + r() * 1.2) * w;
      // start the loop at a random point so joins don't all sit at the top
      const k = Math.floor(r() * P.length);
      P = P.slice(k).concat(P.slice(0, k));
      P.push(P[0].slice());
      if (over > 0) { // continue along the start for `over` px
        let acc = 0;
        for (let i = 1; i < P.length && acc < over; i++) {
          const d = Math.hypot(P[i][0] - P[i - 1][0], P[i][1] - P[i - 1][1]);
          if (acc + d > over) { const t = (over - acc) / d; P.push([P[i - 1][0] + (P[i][0] - P[i - 1][0]) * t, P[i - 1][1] + (P[i][1] - P[i - 1][1]) * t]); break; }
          acc += d; P.push(P[i].slice());
        }
      } else { P = trimEnd(P, -over); }
    } else if (P.length >= 2) {
      const a0 = endAdj(), a1 = endAdj();
      if (a0 > 0) { const t = tan(P[1], P[0]); P.unshift([P[0][0] + t[0] * a0, P[0][1] + t[1] * a0]); }
      else if (a0 < 0) P = trimEnd(P.slice().reverse(), -a0).reverse();
      const n = P.length;
      if (a1 > 0) { const t = tan(P[n - 2], P[n - 1]); P.push([P[n - 1][0] + t[0] * a1, P[n - 1][1] + t[1] * a1]); }
      else if (a1 < 0) P = trimEnd(P, -a1);
    }
    const D = densify(P, 2.5);
    const S = [0];
    for (let i = 1; i < D.length; i++) S.push(S[i - 1] + Math.hypot(D[i][0] - D[i - 1][0], D[i][1] - D[i - 1][1]));
    const N = [];
    for (let i = 0; i < D.length; i++) {
      const a = D[Math.max(0, i - 1)], b = D[Math.min(D.length - 1, i + 1)];
      const t = tan(a, b); N.push([-t[1], t[0]]);
    }
    return {
      D, S, N, L: S[S.length - 1], w,
      nWob: noise1(seed * 31 + 1), nFine: noise1(seed * 31 + 2), nPress: noise1(seed * 31 + 3), nBoil: noise1(seed * 31 + 4),
      phase: r() * 50, startPool: 1.08 + r() * 0.16, endPool: 1.2 + r() * 0.3, wobA: 0.9 + r() * 0.9, wk: 0.92 + r() * 0.16,
    };
  }
  function trimEnd(P, amt) {
    let acc = 0;
    for (let i = P.length - 1; i > 0; i--) {
      const d = Math.hypot(P[i][0] - P[i - 1][0], P[i][1] - P[i - 1][1]);
      if (acc + d >= amt) { const t = (amt - acc) / d; const q = [P[i][0] + (P[i - 1][0] - P[i][0]) * t, P[i][1] + (P[i - 1][1] - P[i][1]) * t]; return P.slice(0, i).concat([q]); }
      acc += d;
    }
    return P.slice(0, 2);
  }

  // Outline path for a prepared stroke. progress 0..1 draws it on; boil is an integer.
  function outline(st, progress = 1, boil = 0, boilAmp = 0.5) {
    if (progress <= 0 || st.D.length < 2) return '';
    const Lp = st.L * Math.min(1, progress);
    const wet = progress < 1;
    const L = [], R = [];
    let last = null;
    const bo = boil * 13.7;
    for (let i = 0; i < st.D.length; i++) {
      const s = st.S[i];
      if (s > Lp) break;
      last = i;
    }
    if (last === null) return '';
    const pts = [];
    for (let i = 0; i <= last; i++) pts.push(i);
    // partial final point
    let tail = null;
    if (last < st.D.length - 1 && Lp > st.S[last]) {
      const t = (Lp - st.S[last]) / (st.S[last + 1] - st.S[last]);
      tail = [st.D[last][0] + (st.D[last + 1][0] - st.D[last][0]) * t, st.D[last][1] + (st.D[last + 1][1] - st.D[last][1]) * t];
    }
    const wAt = (s) => {
      let k = st.wk * (1 + 0.17 * st.nPress(s / 55 + st.phase) + 0.05 * st.nPress(s / 13 + 7));
      k *= 1 + (st.startPool - 1) * Math.exp(-(s / 5) * (s / 5));
      const dEnd = Lp - s;
      const pool = wet ? 1.1 : st.endPool;
      k *= 1 + (pool - 1) * Math.exp(-(dEnd / 4.5) * (dEnd / 4.5));
      // pen lands: a hair thinner just after touchdown
      k *= 0.86 + 0.14 * smooth(0, 9, s);
      return st.w * 0.5 * k;
    };
    const off = (s) => st.wobA * (1.1 * st.nWob(s / 85 + st.phase) + 0.35 * st.nFine(s / 19 + st.phase))
      + (boil ? boilAmp * st.nBoil(s / 40 + bo) : 0);
    const push = (p, n, s) => {
      const o = off(s), hw = wAt(s);
      const cx = p[0] + n[0] * o, cy = p[1] + n[1] * o;
      L.push([cx + n[0] * hw, cy + n[1] * hw]); R.push([cx - n[0] * hw, cy - n[1] * hw]);
      return [cx, cy, hw];
    };
    let first = null, end = null, endN = null;
    for (const i of pts) {
      const r = push(st.D[i], st.N[i], st.S[i]);
      if (first === null) first = r;
      end = r; endN = st.N[i];
    }
    if (tail) { end = push(tail, st.N[last], Lp); endN = st.N[last]; }
    // caps: half circles
    const cap = (c, n, dir) => {
      const out = [];
      const a0 = Math.atan2(n[1], n[0]);
      for (let k = 1; k < 8; k++) {
        const a = a0 + dir * Math.PI * k / 8;
        out.push([c[0] + Math.cos(a) * c[2], c[1] + Math.sin(a) * c[2]]);
      }
      return out;
    };
    const n0 = st.N[0];
    const endCap = cap(end, endN, -1);      // from L side round to R side at the end
    const startCap = cap(first, [-n0[0], -n0[1]], -1); // from R side round to L side at the start
    const all = L.concat(endCap, R.reverse(), startCap);
    let d = 'M' + f1(all[0][0]) + ' ' + f1(all[0][1]);
    for (let i = 1; i < all.length; i++) d += 'L' + f1(all[i][0]) + ' ' + f1(all[i][1]);
    return d + 'Z';
  }

  // A small filled blob (eyes, pupils) with a wobbly edge
  function blob(cx, cy, rx, ry, seed, scale = 1) {
    const n = noise1(seed * 17 + 5);
    let d = '';
    for (let i = 0; i < 28; i++) {
      const a = i / 28 * Math.PI * 2, k = 1 + 0.07 * n(i / 4);
      d += (i ? 'L' : 'M') + f1(cx + Math.cos(a) * rx * k * scale) + ' ' + f1(cy + Math.sin(a) * ry * k * scale);
    }
    return d + 'Z';
  }

  // Build the re-inked drawing from a traced JSON. Returns [{d-fn, ...}] items ready to draw.
  // tr: traced json; place: {x, y, scale}; style: {w, inner, minLen}
  function buildDrawing(tr, place, style) {
    const sc = place.scale, W = style.w, inner = style.inner || 0.7;
    const items = [];
    tr.strokes.forEach((s, i) => {
      if (s.len * sc < (style.minLen || 0)) return;
      const pts = s.pts.map(p => [place.x + p[0] * sc, place.y + p[1] * sc]);
      const w = W * (s.outer ? 1 : inner);
      items.push({ kind: 'stroke', st: prepare(pts, { w, seed: (style.seed || 1) * 1000 + i, closed: s.closed }), len: s.len * sc, outer: s.outer });
    });
    (tr.fills || []).forEach((f, i) => {
      items.push({ kind: 'fill', cx: place.x + f.cx * sc, cy: place.y + f.cy * sc, rx: Math.max(W * 0.55, f.rx * sc), ry: Math.max(W * 0.55, f.ry * sc), seed: (style.seed || 1) * 1000 + 500 + i });
    });
    // draw-on schedule: outer strokes first, in traced order; each stroke's share ~ its length
    let acc = 0; const total = items.reduce((a, it) => a + (it.kind === 'stroke' ? it.len + 40 : 30), 0) || 1;
    for (const it of items) { const l = it.kind === 'stroke' ? it.len + 40 : 30; it.t0 = acc / total; it.t1 = (acc + l) / total; acc += l; }
    return items;
  }

  // SVG path data for the whole drawing at reveal r (0..1). Several pens run at once
  // (each stroke starts on schedule but takes a bit longer), so it feels quick and drawn.
  function drawingPaths(items, reveal = 1, boil = 0, boilAmp = 0.5) {
    const out = [];
    for (const it of items) {
      // overlap: each item's window is stretched 3x so several strokes draw at once
      const a = it.t0 * 0.72, b = Math.min(1, a + (it.t1 - it.t0) * 3 + 0.08);
      const p = reveal >= 1 ? 1 : clamp((reveal - a) / (b - a), 0, 1);
      if (p <= 0) continue;
      if (it.kind === 'stroke') out.push(outline(it.st, easeOut(p), boil, boilAmp));
      else out.push(blob(it.cx, it.cy, it.rx, it.ry, it.seed, Math.min(1, p * 1.6)));
    }
    return out;
  }
  const easeOut = u => 1 - Math.pow(1 - u, 2.2);

  return { mulberry32, noise1, prepare, outline, blob, buildDrawing, drawingPaths };
});
