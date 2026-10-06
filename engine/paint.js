// Afterclap red-lead paint: splats, gathers, drops in flight, fills and drains, slides, soaks.
// Generalised from the motion test's splat-and-drop model. Browser or node (pure geometry,
// returns SVG element strings). All randomness is seeded, so frames are deterministic.
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.Paint = factory();
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';
  function mulberry32(a) { return function () { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
  const clamp = (x, a, b) => Math.max(a, Math.min(b, x));
  const lerp = (a, b, u) => a + (b - a) * u;
  const prog = (t, a, b) => b <= a ? (t >= b ? 1 : 0) : clamp((t - a) / (b - a), 0, 1);
  const eio = u => u < .5 ? 4 * u * u * u : 1 - Math.pow(-2 * u + 2, 3) / 2;
  const eis = u => -(Math.cos(Math.PI * u) - 1) / 2;
  const eo = u => 1 - Math.pow(1 - u, 3);
  const eoq = u => 1 - (1 - u) * (1 - u);
  const f1 = n => n.toFixed(1);
  function spring(tau, w = 24, z = 0.36) {
    if (tau <= 0) return 0; const s = Math.sqrt(1 - z * z), wd = w * s;
    return 1 - Math.exp(-z * w * tau) * (Math.cos(wd * tau) + z / s * Math.sin(wd * tau));
  }
  function angDiff(a, b) { let d = a - b; while (d > Math.PI) d -= 2 * Math.PI; while (d < -Math.PI) d += 2 * Math.PI; return d; }

  // ---------------------------------------------------------------- splat
  // o: {R, Rdrop, r0, nSat, satD, satR, tendrilP, nSpk, spkD, drip, dripX, sy, rot}
  function makeSplat(seed, o) {
    const r = mulberry32(seed);
    const harm = []; for (let k = 2; k <= 9; k++) harm.push({ k, a: (0.085 / Math.sqrt(k)) * (0.4 + 0.6 * r()), p: r() * 6.283 });
    const sats = []; for (let i = 0; i < o.nSat; i++) {
      const ang = (i / o.nSat) * 6.283 + (r() - .5) * 0.8 + (o.rot || 0);
      const tendril = r() < o.tendrilP;
      sats.push({ ang, dist: lerp(o.satD[0], o.satD[1], r()) * (tendril ? 0.8 : 1), rad: lerp(o.satR[0], o.satR[1], r()), tf: lerp(0.09, 0.2, r()), det: tendril ? 99 : lerp(0.06, 0.14, r()), tw: lerp(0.12, 0.15, r()) * o.R, g: r() });
    }
    const specks = []; for (let i = 0; i < o.nSpk; i++) {
      const dist = lerp(o.spkD[0], o.spkD[1], Math.sqrt(r()));
      specks.push({ ang: r() * 6.283, dist, rad: lerp(1.8, 5.5, Math.pow(r(), 1.7)), tf: lerp(0.1, 0.3, r()), g: r(), keep: dist > o.R * 1.9 && r() < 0.55 });
    }
    const bumps = []; for (let i = 0; i < 8; i++) bumps.push({ ang: r() * 6.283, a: lerp(0.08, 0.24, r()), w: lerp(0.10, 0.22, r()) });
    return Object.assign({}, o, { harm, sats, specks, bumps });
  }
  // a splat sized from its radius R (px). small: fewer, tighter satellites
  function splatFor(seed, R, extra) {
    const k = R / 92;
    const r = mulberry32(seed + 77);
    return makeSplat(seed, Object.assign({
      R, Rdrop: Math.max(22, R * 0.5), r0: R * 0.45, nSat: R > 50 ? 10 : 8,
      satD: [R * 1.35, R * 2.25], satR: [Math.max(5, 10 * k), Math.max(8, 18 * k)], tendrilP: 0.42,
      nSpk: Math.round(10 + 12 * k), spkD: [R * 1.2, R * 3.4], drip: r() < 0.55 ? R * lerp(0.6, 1.0, r()) : 0, dripX: R * lerp(-0.2, 0.2, r()),
      rot: r() * 6.28,
    }, extra || {}));
  }
  function polarD(cx, cy, fr, sy = 1, N = 110) {
    let d = ''; for (let i = 0; i < N; i++) { const th = i / N * 2 * Math.PI, rr = fr(th); d += (i ? 'L' : 'M') + f1(cx + rr * Math.cos(th)) + ' ' + f1(cy + rr * Math.sin(th) * sy); } return d + 'Z';
  }
  function taperD(x0, y0, x1, y1, w0, w1) {
    const dx = x1 - x0, dy = y1 - y0, L = Math.hypot(dx, dy) || 1, nx = -dy / L, ny = dx / L;
    return `M${f1(x0 + nx * w0 / 2)} ${f1(y0 + ny * w0 / 2)} L${f1(x1 + nx * w1 / 2)} ${f1(y1 + ny * w1 / 2)} L${f1(x1 - nx * w1 / 2)} ${f1(y1 - ny * w1 / 2)} L${f1(x0 - nx * w0 / 2)} ${f1(y0 - ny * w0 / 2)}Z`;
  }
  function ell(x, y, rx, ry, deg) { return `<ellipse cx="${f1(x)}" cy="${f1(y)}" rx="${f1(Math.max(0, rx))}" ry="${f1(Math.max(0, ry))}" transform="rotate(${f1(deg)} ${f1(x)} ${f1(y)})"/>`; }

  // tau: time since impact; U: gather 0..1; soak 0..1; antic: anticipation squash 0..1; grow: extra size factor
  function splatEls(sp, cx, cy, tau, U, soak, antic, goo, spk, grow2 = 1) {
    const sy = sp.sy || 1, gU = eio(U);
    const grow = lerp(sp.r0 / sp.R, 1, spring(tau, 26, 0.34));
    const R = lerp(sp.R * grow * grow2, sp.Rdrop, gU) * (1 - soak);
    const nA = (1 - gU) * clamp(tau / 0.07, 0, 1);
    if (R > 1) {
      if (gU >= 0.999) { const a = antic; goo.push(ell(cx, cy + 0.2 * R * a, R * (1 + 0.3 * a), R * (1 - 0.26 * a), 0)); }
      else {
        const fr = th => { let v = 1; for (const h of sp.harm) v += h.a * nA * Math.sin(h.k * th + h.p); for (const b of sp.bumps) { const d = angDiff(th, b.ang); v += b.a * nA * Math.exp(-(d * d) / (b.w * b.w)); } return R * v; };
        goo.push(`<path d="${polarD(cx, cy, fr, sy)}"/>`);
      }
    }
    for (const s of sp.sats) {
      const p = eo(prog(tau, 0, s.tf)); const gu = eio(prog(U, s.g * 0.3, s.g * 0.3 + 0.7));
      const d = s.dist * p * (1 - gu); const ca = Math.cos(s.ang), sa = Math.sin(s.ang);
      const pull = gu * (1 - gu) * 4;
      const st = 1 + 1.5 * (1 - p) * (tau < s.tf ? 1 : 0) + 0.7 * pull;
      const rad = s.rad * (1 - soak) * lerp(0.75, 1, p) * (1 - 0.35 * gu);
      const x = cx + ca * d, y = cy + sa * d * sy, deg = Math.atan2(sa * sy, ca) * 180 / Math.PI;
      if (rad > 1) goo.push(ell(x, y, rad * st, rad / Math.sqrt(st), deg));
      let L;
      if (s.det > 50) L = d; else if (tau < s.det) L = d; else L = lerp(s.dist * eo(prog(s.det, 0, s.tf)), R * 0.6, eo(prog(tau, s.det, s.det + 0.13))) * (1 - gu);
      if (s.det > 50 || tau < s.det + 0.13) {
        if (L > R * 0.75 && R > 2) { const tw = s.tw * (1 - soak); goo.push(`<path d="${taperD(cx + ca * R * 0.5, cy + sa * R * 0.5 * sy, cx + ca * L, cy + sa * L * sy, tw * 2.1, tw * 0.88)}"/>`); }
      }
    }
    for (const k of sp.specks) {
      if (k.keep) continue; // residue specks are drawn by residueEls
      const p = eo(prog(tau, 0, k.tf)); if (p <= 0) continue; const gu = eio(prog(U, k.g * 0.25, k.g * 0.25 + 0.55));
      const d = k.dist * p * (1 - gu); if (d < R * 0.92) continue;
      const st = 1 + 2.2 * (1 - p); const rad = k.rad * (1 - soak) * (1 - 0.5 * gu); if (rad < 0.6) continue;
      const ca = Math.cos(k.ang), sa = Math.sin(k.ang);
      spk.push(ell(cx + ca * d, cy + sa * d * sy, rad * st, rad / Math.sqrt(st), Math.atan2(sa * sy, ca) * 180 / Math.PI));
    }
    if (sp.drip) {
      const Ld = sp.drip * eo(prog(tau, 0.5, 2.0)) * (1 - eio(prog(U, 0, 0.45))) * (1 - soak);
      if (Ld > 3) {
        const x = cx + sp.dripX, y0 = cy + R * 0.55, y1 = cy + R * 0.78 + Ld, k = sp.R / 92;
        goo.push(`<path d="${taperD(x, y0, x, y1, 19 * k + 4, 13 * k + 3)}"/>`);
        goo.push(ell(x, y1 + 2, (12.5 * k + 3) * lerp(0.7, 1, Ld / sp.drip), (13.5 * k + 3) * lerp(0.7, 1, Ld / sp.drip), 0));
      }
    }
  }
  // the far specks stay on the paper after the paint lifts off
  function residueEls(sp, cx, cy, tau, out) {
    const sy = sp.sy || 1;
    for (const k of sp.specks) {
      if (!k.keep) continue;
      const p = eo(prog(tau, 0, k.tf)); if (p <= 0) continue;
      const d = k.dist * p, st = 1 + 2.2 * (1 - p), ca = Math.cos(k.ang), sa = Math.sin(k.ang);
      out.push(ell(cx + ca * d, cy + sa * d * sy, k.rad * st, k.rad / Math.sqrt(st), Math.atan2(sa * sy, ca) * 180 / Math.PI));
    }
  }

  // flying drop with velocity stretch + teardrop tail (velocities in px/s, screen space)
  function dropEls(goo, x, y, r, vx, vy, { wob = 0, maxPerp = null } = {}) {
    const sp = Math.hypot(vx, vy); const s = 1 + Math.min(0.62, sp / 2600);
    const deg = sp > 1 ? Math.atan2(vy, vx) * 180 / Math.PI : 90;
    let rPar = r * s * (1 + wob), rPerp = r / s * (1 - wob);
    if (maxPerp != null && rPerp > maxPerp) { const k = maxPerp / rPerp; rPerp *= k; rPar /= k; }
    goo.push(ell(x, y, rPar, rPerp, deg));
    if (sp > 500) {
      const k = Math.min(1, (sp - 500) / 1800), ux = vx / sp, uy = vy / sp;
      const r1 = rPerp * 0.74 * k, d1 = rPar * 0.62;
      if (r1 > r * 0.18) goo.push(ell(x - ux * d1, y - uy * d1, rPar * 0.7, r1, deg));
      const r2 = rPerp * 0.42 * k, d2 = d1 + rPar * 0.62 * k;
      if (r2 > r * 0.2) goo.push(ell(x - ux * d2, y - uy * d2, rPar * 0.5, r2, deg));
    }
  }

  return { mulberry32, clamp, lerp, prog, eio, eis, eo, eoq, spring, makeSplat, splatFor, polarD, taperD, ell, splatEls, residueEls, dropEls };
});
