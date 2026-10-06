// Build a render plan from a story folder: layout, camera moves, ink draw-on times,
// paint landings and travels, captions and foley cues. Everything time-based comes
// from shots.json and words.json; positions come from layout.json.
const fs = require('fs'), path = require('path');
const { loadLayout } = require('./layout.cjs');

const FPS = 30, W = 1080, H = 1920, PITCH = 1920;
const readJSON = f => JSON.parse(fs.readFileSync(f, 'utf8'));
const clamp = (x, a, b) => Math.max(a, Math.min(b, x));
const hash = s => { let h = 2166136261; for (const c of s) { h ^= c.charCodeAt(0); h = Math.imul(h, 16777619); } return h >>> 0; };

// a sketchy picture-frame placeholder, used when a drawing is missing
function placeholderTrace(id) {
  const w = 600, h = 450, m = 20;
  const rect = [[m, m], [w - m, m], [w - m, h - m], [m, h - m], [m, m]];
  return {
    id, placeholder: true, size: [w, h], lw_src: 4, fills: [],
    strokes: [
      { pts: rect, closed: true, len: 2 * (w + h - 4 * m), outer: true },
      { pts: [[m + 30, h - m - 30], [w * 0.38, h * 0.45], [w * 0.55, h * 0.66], [w * 0.7, h * 0.38], [w - m - 30, h - m - 30]], closed: false, len: 700, outer: false },
      { pts: [[w * 0.74, h * 0.2], [w * 0.8, h * 0.17], [w * 0.84, h * 0.22], [w * 0.8, h * 0.27], [w * 0.74, h * 0.25], [w * 0.74, h * 0.2]], closed: true, len: 110, outer: false },
    ],
  };
}

function loadTraced(story, ids) {
  const out = {};
  for (const id of ids) {
    const f = path.join(story, 'art', 'traced', id + '.json');
    out[id] = fs.existsSync(f) ? readJSON(f) : placeholderTrace(id);
    if (!fs.existsSync(f)) console.warn(`  ! no traced art for "${id}", using a placeholder`);
  }
  return out;
}

// ---------------------------------------------------------------- captions
function normalize(s) { return s.toLowerCase().replace(/[^a-z0-9]/g, ''); }

function buildCaptions(words, narration, maxChars = 30) {
  // map each timed word onto narration tokens so captions keep the script's casing and punctuation
  const toks = narration.replace(/\[\[[^\]]*\]\]/g, ' ').split(/\s+/).filter(Boolean);
  let stream = '', owner = [];
  toks.forEach((tk, i) => { const n = normalize(tk); stream += n; for (let k = 0; k < n.length; k++) owner.push(i); });
  let pos = 0;
  const W = words.map(w => {
    const n = normalize(w.w);
    let at = stream.indexOf(n, pos);
    if (at < 0 || at - pos > 40 || !n) return Object.assign({}, w, { a: null, b: null });
    pos = at + n.length;
    return Object.assign({}, w, { a: owner[at], b: owner[at + n.length - 1] });
  });
  const textOf = (ws) => {
    const a = ws.find(w => w.a != null), b = [...ws].reverse().find(w => w.b != null);
    if (!a || !b) return ws.map(w => w.w).join(' ');
    return toks.slice(a.a, b.b + 1).join(' ');
  };
  // phrases: split at punctuation and real pauses; long phrases split into balanced lines
  const WEAK = new Set(['a', 'an', 'the', 'and', 'of', 'to', 'in', 'on', 'that', 'but', 'with', 'his', 'its', 'he', 'up', 'who', 'why', 'does']);
  const tokOf = w => (w.b != null ? toks[w.b] : w.w);
  const phrases = []; let cur = [];
  for (let i = 0; i < W.length; i++) {
    const w = W[i]; cur.push(w);
    const next = W[i + 1];
    const gap = next ? next.s - w.e : 9;
    if (/[.?!,;:]$/.test(tokOf(w)) || gap > 0.45) { phrases.push(cur); cur = []; }
  }
  if (cur.length) phrases.push(cur);
  const lines = [];
  for (const ph of phrases) {
    const len = textOf(ph).length;
    if (len <= maxChars || ph.length < 2) { lines.push(ph); continue; }
    const n = Math.ceil(len / maxChars);
    // dynamic programme over break points: balanced lengths, no weak word left dangling
    const best = (ws, parts) => {
      if (parts === 1) { const L = textOf(ws).length; return L <= maxChars + 2 ? { cost: 0, cut: [ws] } : { cost: 1e9, cut: [ws] }; }
      let out = { cost: 1e9, cut: [ws] };
      const target = textOf(ws).length / parts;
      for (let k = 1; k < ws.length; k++) {
        const head = ws.slice(0, k), tail = ws.slice(k);
        const hl = textOf(head).length; if (hl > maxChars + 2) break;
        const sub = best(tail, parts - 1); if (sub.cost >= 1e9) continue;
        const pen = Math.abs(hl - target) + (WEAK.has(normalize(tokOf(head[head.length - 1]))) ? 12 : 0);
        if (pen + sub.cost < out.cost) out = { cost: pen + sub.cost, cut: [head].concat(sub.cut) };
      }
      return out;
    };
    let r = best(ph, n); if (r.cost >= 1e9) r = best(ph, n + 1);
    lines.push(...r.cut);
  }
  const caps = lines.map(ws => ({ ws }));
  const out = caps.filter(c => c.ws.length).map(c => ({ t0: c.ws[0].s - 0.08, t1: c.ws[c.ws.length - 1].e + 0.75, text: textOf(c.ws) }));
  for (let i = 0; i < out.length - 1; i++) if (out[i].t1 > out[i + 1].t0) out[i].t1 = out[i + 1].t0;
  out.forEach(c => { c.text = c.text.replace(/\s+-/g, '-'); c.t0 = Math.max(0, c.t0); });
  return out;
}

// ---------------------------------------------------------------- plan
function buildPlan(storyDir) {
  const story = path.resolve(storyDir);
  const shots = readJSON(path.join(story, 'shots.json'));
  const words = readJSON(path.join(story, shots.words || 'words.json'));
  const narrFile = ['narration.txt', 'script.txt'].map(f => path.join(story, f)).find(f => fs.existsSync(f));
  const narration = narrFile ? fs.readFileSync(narrFile, 'utf8') : words.map(w => w.w).join(' ');
  const ids = [...new Set(shots.scenes.flatMap(s => s.art.map(a => a.id)))];
  const traced = loadTraced(story, ids);
  // the keyed word is the truth: if a paint time doesn't sit on its word, snap it to the word
  const warnings = [];
  for (const sc of shots.scenes) for (const p of sc.paint) {
    const key = normalize(p.word);
    const cands = words.filter(w => normalize(w.w) === key && Math.abs(w.s - p.t) < 1.5).sort((a, b) => Math.abs(a.s - p.t) - Math.abs(b.s - p.t));
    if (!cands.length) { warnings.push(`paint "${p.word}" @${p.t}: word not found near that time; using the time as given`); continue; }
    if (Math.abs(cands[0].s - p.t) > 0.04) {
      warnings.push(`paint "${p.word}" @${p.t}: that time is "${(words.find(w => Math.abs(w.s - p.t) < 0.04) || {}).w || '?'}"; snapped to "${cands[0].w}" @${cands[0].s}`);
      p.key_t = p.t; p.t = cands[0].s;
    }
  }

  const layout = loadLayout(story, shots, traced);
  const st = layout.style;
  const duration = shots.duration;

  // check keyed words against words.json
  // ---- place drawings
  const scenes = shots.scenes.map((sc, k) => {
    const ls = layout.scenes.find(s => s.id === sc.id);
    const art = ls.art.map(a => {
      const tr = traced[a.id];
      const w = a.w, scale = w / tr.size[0], h = tr.size[1] * scale;
      const inkLen = tr.strokes.reduce((s, x) => s + x.len, 0) * scale;
      return { id: a.id, left: a.x - w / 2, top: k * PITCH + a.y - h / 2, w, h, scale, trace: tr, inkLen, seed: (hash(a.id) % 9973) + 1, weight: a.weight || 1 };
    });
    return { idx: k, id: sc.id, start: sc.start, end: sc.end, y0: k * PITCH, art, ls };
  });

  // ---- landings
  const landings = [];
  scenes.forEach((sc, k) => {
    for (const p of sc.ls.paint) {
      const a = sc.art.find(a => a.id === p.art) || sc.art[0];
      const x = a.left + p.at[0] * a.w, y = a.top + p.at[1] * a.h;
      const R = p.R || clamp(0.085 * a.w, 30, 78);
      // impact on the frame nearest the word's start (never more than half a frame off)
      const L = { t: Math.round(p.t * FPS) / FPS, word_t: p.t, word: p.word, x, y, R, scene: k, art: a.id, seed: (hash(p.word + p.t) % 99991) + 3 };
      if (p.fill) {
        const r = p.fill.r * a.w;
        L.fill = { cx: a.left + p.fill.cx * a.w, cy: a.top + p.fill.cy * a.h, r, drain: p.fill.drain, dripX: (p.fill.dripX || 0) * a.w };
      }
      if (p.slide) L.slide = { at: p.slide.at, dur: p.slide.dur || 0.5, x: a.left + p.slide.to[0] * a.w, y: a.top + p.slide.to[1] * a.h };
      if (p.soak) L.soak = { at: p.soak };
      landings.push(L);
    }
  });
  landings.sort((a, b) => a.t - b.t);
  // when the paint is free to leave a landing
  const release = L => L.fill ? L.fill.drain[1] + 0.15 : L.slide ? L.slide.at + L.slide.dur + 0.95 : L.t + 0.8;
  const leavePoint = L => L.fill ? [L.fill.cx + L.fill.dripX, L.fill.cy + L.fill.r + 30] : L.slide ? [L.slide.x, L.slide.y] : [L.x, L.y];

  // ---- camera: one scroll per scene change
  const camera = [];
  for (let k = 1; k < scenes.length; k++) {
    const S = scenes[k].start;
    const first = landings.find(L => L.scene === k);
    const prev = [...landings].reverse().find(L => L.scene < k);
    const firstT = first ? first.t : S + 1.2;
    const lb = prev ? release(prev) : S - 1.5;
    let end = Math.min(S + 0.45, firstT - 0.4), start = end - 1.15;
    if (start < lb) { start = lb; if (end - start < 0.8) end = start + 0.8; }
    camera.push({ s0: +start.toFixed(3), s1: +end.toFixed(3), y0: (k - 1) * PITCH, y1: k * PITCH, scene: k });
  }
  const scrollOf = k => camera.find(c => c.scene === k);

  // ---- ink draw-on
  for (const sc of scenes) {
    const scr = scrollOf(sc.idx);
    // first scene: with the film-reel on, the strip's pull-in is the arrival, so the drawing is
    // nearly whole on the first frame (and makes a better first impression)
    const reelOn = !st.reel || st.reel.on !== false;
    const arrive = scr ? scr.s0 + 0.5 * (scr.s1 - scr.s0) : (reelOn ? -0.7 : -0.25);
    sc.art.forEach((a, j) => {
      const D = clamp(0.45 + a.inkLen / 9000, 0.55, 1.0);
      const firstL = landings.find(L => L.scene === sc.idx && L.art === a.id);
      let t0 = j === 0 ? arrive : arrive + 0.2 * j;
      if (j > 0 && firstL) t0 = Math.max(t0, firstL.t - D - 0.35);
      let t1 = t0 + D;
      if (firstL && t1 > firstL.t - 0.12) t1 = Math.max(t0 + 0.35, firstL.t - 0.12);
      a.draw = [+t0.toFixed(3), +t1.toFixed(3)];
    });
  }

  // ---- travels between landings
  const travels = landings.map(() => null);
  for (let i = 0; i < landings.length - 1; i++) {
    const A = landings[i], B = landings[i + 1];
    const from = leavePoint(A), to = [B.x, B.y];
    const rel = A.fill ? A.fill.drain[1] + 0.15 : A.slide ? A.slide.at + A.slide.dur + 0.3 : A.t + (A.scene === B.scene ? 0.5 : 0.85); // earliest sensible lift
    const r1size = clamp(B.R * 0.5, 16, 46), r0 = clamp(A.R * 0.5, 16, 46);
    let tr;
    if (A.scene === B.scene) {
      const dist = Math.hypot(to[0] - from[0], to[1] - from[1]);
      const base = A.slide ? A.slide.at + A.slide.dur : A.t;
      const avail = B.t - base;
      let F = clamp(0.34 + dist / 2400, 0.4, 0.72), G = 0.32;
      if (avail < F + G + 0.3) { F = Math.max(0.3, avail * 0.5); G = Math.max(0.14, avail * 0.28); }
      const tl = B.t - F;
      tr = { mode: 'hop', tl, t2: B.t, g0: tl - G, g1: tl - 0.1, apex: clamp(80 + dist * 0.35, 90, 260) };
    } else {
      const scr = scrollOf(B.scene);
      const tl = Math.max(rel, scr.s0 - 0.05);
      const settle = A.fill ? A.fill.drain[1] : A.slide ? A.slide.at + A.slide.dur : A.t;
      const G = Math.max(0.15, Math.min(0.35, tl - settle - 0.15));
      if (A.fill) tr = { mode: 'drip', tl, t2: B.t };
      else if (B.t - scr.s1 <= 0.75) tr = { mode: 'ride', tl, t2: B.t };
      else tr = { mode: 'toss', tl, t2: B.t, r1: tl + 0.42, f0: B.t - 0.55 };
      tr.g0 = tl - G; tr.g1 = tl - 0.1;
    }
    Object.assign(tr, { from, to, r0, r1size });
    travels[i] = tr;
  }
  const first = landings[0];
  const incoming = first ? { t0: first.t - 0.42, x0: first.x + 46, r: clamp(first.R * 0.5, 16, 46) } : null;

  // ---- captions
  const captions = buildCaptions(words, narration);

  // ---- cues for foley (paint + paper sounds); the mixer reads these
  const cues = [];
  if (incoming) cues.push({ t: +incoming.t0.toFixed(3), type: 'drop', x: incoming.x0, gain: 0.6 });
  landings.forEach((L, i) => {
    cues.push({ t: L.t, type: 'splat', size: +L.R.toFixed(0), word: L.word });
    if (L.fill) cues.push({ t: L.fill.drain[0], type: 'drain', dur: +(L.fill.drain[1] - L.fill.drain[0]).toFixed(2) });
    if (L.slide) cues.push({ t: L.slide.at, type: 'slide', dur: L.slide.dur });
    if (L.soak) cues.push({ t: L.soak.at, type: 'soak' });
    const tr = travels[i];
    if (tr) { cues.push({ t: +tr.g0.toFixed(3), type: 'gather' }); cues.push({ t: +tr.tl.toFixed(3), type: 'lift', mode: tr.mode }); }
  });
  camera.forEach(c => cues.push({ t: c.s0, type: 'scroll', dur: +(c.s1 - c.s0).toFixed(3) }));
  scenes.forEach(sc => sc.art.forEach(a => cues.push({ t: a.draw[0], type: 'pen', dur: +(a.draw[1] - a.draw[0]).toFixed(3), art: a.id })));
  cues.sort((a, b) => a.t - b.t);

  // ---- cover
  const cv = layout.cover || {};
  const ctr = traced[cv.art] || traced[ids[0]];
  const cw = cv.w || 900, csc = cw / ctr.size[0], ch = ctr.size[1] * csc;
  const ccx = cv.x || 540, ccy = cv.y || 1120;
  const coverPlan = {
    words: cv.words || ['Why?'], trace: ctr, left: ccx - cw / 2, top: ccy - ch / 2, scale: csc,
    x: ccx - cw / 2 + (cv.at || [0.5, 0.5])[0] * cw, y: ccy - ch / 2 + (cv.at || [0.5, 0.5])[1] * ch,
    R: cv.R || 80, seed: 4242, mark: cv.mark || [104, 176, 24],
  };

  return {
    story: shots.story, fps: FPS, W, H, duration, frames: Math.round(duration * FPS),
    style: st, scenes: scenes.map(s => ({ idx: s.idx, id: s.id, start: s.start, end: s.end, art: s.art })),
    camera, landings, travels, incoming, captions, cues, coverPlan, warnings,
    audio: path.join(story, shots.audio || 'voice.mp3'),
  };
}

module.exports = { buildPlan, buildCaptions, FPS, W, H };

if (require.main === module) {
  const p = buildPlan(process.argv[2]);
  const brief = Object.assign({}, p, { scenes: p.scenes.map(s => ({ id: s.id, art: s.art.map(a => ({ id: a.id, draw: a.draw, box: [a.left, a.top, a.w, a.h].map(Math.round) })) })), coverPlan: undefined });
  console.log(JSON.stringify(brief, (k, v) => typeof v === 'number' ? Math.round(v * 1000) / 1000 : v, 1));
}
