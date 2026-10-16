#!/usr/bin/env node
// Afterclap thread video: several Shorts joined into one horizontal 16:9 film on one paper strip.
//
//   node engine/thread.cjs threads/01-08.json                   video (master + review copy) into threads/out/<name>/
//   node engine/thread.cjs threads/01-08.json --stills 2,30.5   just stills (PNG + 720px JPG)
//   node engine/thread.cjs threads/01-08.json --scene-stills    one still per scene (after its last landing)
//   node engine/thread.cjs threads/01-08.json --seam-stills     four stills across each story boundary
//   node engine/thread.cjs threads/01-08.json --plan            print the timeline and layout, render nothing
//   options: --par N, --from s --to s (preview a range), --no-review (master only), --review-height 720,
//            --max-mb N (review copy cap, default 19), --out name.mp4
//
// The thread JSON:
//   { "name": "01-08", "stories": ["01-dime", "02-ridges", ...], "gap": 0.6,
//     "intro": { "lines": ["One question", "leads to the next."], "dur": 4.2 },
//     "outro": { "lines": ["..."], "dur": 3.5 } }            (outro optional)
//
// Chapters (Matthew, 2026-10-15), in place of "stories":
//   "chapters": [{ "title": "Coins", "sub": "the nickel and the dime", "stories": ["01-dime", "02-ridges"] }, ...],
//   "seamGap": 1.0, "breath": 0.4, "chapterCard": { "dur": 4.0 }
// Inside a chapter the stories join seamlessly: each one but the chapter's last loses its tease
// ("And why ...? That's another story."), its audio ending `breath` s after the word before the tease
// (a cut in the silence, nothing re-timed), and the next story's question comes `seamGap` s after
// that word. A chapter's last story (the film's last too) keeps its tease question as the cliffhanger but
// never "That's another story." (cut in the silence after the question), then the chapter's title card
// (the paint lands as its full stop, the subtitle inks on under it). YouTube chapter timestamps go
// to threads/out/<name>/chapters.txt.
//
// Each story keeps its own voice.mp3 (never edited, only placed on the timeline), words.json timings,
// layout.json (drawings and paint landings, re-laid for 16:9) and traced art. Between stories the
// tease line runs straight into the next story's opening after `gap` seconds of breath; the run-out
// and brand sting play only at the very end. When a story's last scene and the next story's first
// scene show the same drawings (the thread's bridge picture), they become one panel and the paint
// hops on it; otherwise the camera pans on along the strip and the paint travels with it.
const fs = require('fs'), path = require('path');
const { loadStory, planFrom, snapPaint, FPS } = require('./plan.cjs');
const { loadLayout } = require('./layout.cjs');
const { reelMap } = require('./reel.cjs');
const { makeRenderer, run, launch, ROOT } = require('./frames.cjs');
const { spawnSync } = require('child_process');

const args = process.argv.slice(2);
const opt = k => { const i = args.indexOf('--' + k); return i < 0 ? null : (args[i + 1] && !args[i + 1].startsWith('--') ? args[i + 1] : true); };
const cfgFile = args.find(a => !a.startsWith('--') && a.endsWith('.json'));
if (!cfgFile || !fs.existsSync(cfgFile)) { console.error('usage: node engine/thread.cjs threads/<name>.json [options]'); process.exit(1); }
const CFG = JSON.parse(fs.readFileSync(cfgFile, 'utf8'));
const NAME = CFG.name || path.basename(cfgFile, '.json');
const OUT = path.join(ROOT, 'threads', 'out', NAME);
fs.mkdirSync(OUT, { recursive: true });

// ---------------------------------------------------------------- 16:9 geometry
const W = 1920, H = 1080, PITCH = 1920;
const ZONE = { x0: 110, x1: 1810, y0: 60, y1: 820 };          // drawings stay above the caption band
const GEOM = { W, H, axis: 'x', pitch: PITCH, cap: { x: 960, y: 978, size: 60, maxW: 1560 }, capChars: 34 };
const GAP = CFG.gap != null ? CFG.gap : 0.6;
const BRAND = Object.assign({ x: 960, y: 520, height: 440 }, CFG.brand || {});
const clamp = (x, a, b) => Math.max(a, Math.min(b, x));
const r3 = x => Math.round(x * 1000) / 1000;

// Re-lay one scene of a Short (scene-local 1080x1920 boxes) for a 1920x1080 panel. Drawings that
// overlap in the Short (a bottle standing on a windowsill) keep their arrangement as one group; the
// groups then sit side by side in the order the paint visits them, so the paint reads left to right
// like the camera. One scale per scene (never enlarged), a little of the Short's up/down stagger kept.
function relayout(ls, traced) {
  const boxes = ls.art.map(a => {
    const tr = traced[a.id], h = tr.size[1] * a.w / tr.size[0];
    return { id: a.id, a, x0: a.x - a.w / 2, x1: a.x + a.w / 2, y0: a.y - h / 2, y1: a.y + h / 2, w: a.w, h };
  });
  // groups: union of boxes overlapping by more than 12% of the smaller one
  const par = boxes.map((_, i) => i), find = i => par[i] === i ? i : (par[i] = find(par[i]));
  for (let i = 0; i < boxes.length; i++) for (let j = i + 1; j < boxes.length; j++) {
    const A = boxes[i], B = boxes[j];
    const ix = Math.max(0, Math.min(A.x1, B.x1) - Math.max(A.x0, B.x0)), iy = Math.max(0, Math.min(A.y1, B.y1) - Math.max(A.y0, B.y0));
    if (ix * iy > 0.12 * Math.min(A.w * A.h, B.w * B.h)) par[find(i)] = find(j);
  }
  const groups = {};
  boxes.forEach((b, i) => (groups[find(i)] = groups[find(i)] || []).push(b));
  const firstPaint = id => { const p = ls.paint.filter(p => p.art === id).map(p => p.t); return p.length ? Math.min(...p) : 1e9; };
  const units = Object.values(groups).map(bs => {
    const x0 = Math.min(...bs.map(b => b.x0)), x1 = Math.max(...bs.map(b => b.x1)), y0 = Math.min(...bs.map(b => b.y0)), y1 = Math.max(...bs.map(b => b.y1));
    return { bs, x0, x1, y0, y1, w: x1 - x0, h: y1 - y0, cy: (y0 + y1) / 2, order: Math.min(...bs.map(b => firstPaint(b.id))) };
  }).sort((a, b) => a.order - b.order || a.cy - b.cy);
  const n = units.length, ZW = ZONE.x1 - ZONE.x0, ZH = ZONE.y1 - ZONE.y0;
  const sumW = units.reduce((s, u) => s + u.w, 0);
  const s = Math.min(1, (ZW - 90 * (n - 1)) / sumW, ZH / Math.max(...units.map(u => u.h)));
  const gap = n > 1 ? clamp((ZW - sumW * s) / (n + 1), 90, 260) : 0;
  const total = sumW * s + gap * (n - 1);
  const meanCy = units.reduce((a, u) => a + u.cy, 0) / n, midY = (ZONE.y0 + ZONE.y1) / 2;
  let x = W / 2 - total / 2;
  const art = [];
  for (const u of units) {
    const uw = u.w * s, uh = u.h * s;
    let cy = midY + clamp((u.cy - meanCy) * 0.2, -60, 60);
    cy = clamp(cy, ZONE.y0 + uh / 2, ZONE.y1 - uh / 2);
    const cx = x + uw / 2;
    for (const b of u.bs) art.push({ id: b.id, x: r3(cx + ((b.x0 + b.x1) / 2 - (u.x0 + u.x1) / 2) * s), y: r3(cy + ((b.y0 + b.y1) / 2 - u.cy) * s), w: r3(b.w * s) });
    x += uw + gap;
  }
  return { art, s };
}

// shift every time in a paint entry by dt (and the drawing it lands on to its thread id)
function shiftPaint(p, dt, ns, s, seedKey, story) {
  const q = JSON.parse(JSON.stringify(p));
  q.t = r3(q.t + dt); if (q.key_t != null) q.key_t = r3(q.key_t + dt);
  if (q.art) q.art = ns(q.art);
  if (q.R) q.R = Math.max(12, Math.round(q.R * s));
  if (q.swell) q.swell.at = r3(q.swell.at + dt);
  if (q.slide) q.slide.at = r3(q.slide.at + dt);
  if (q.soak != null) q.soak = r3(q.soak + dt);
  if (q.fill && q.fill.drain) q.fill.drain = q.fill.drain.map(v => r3(v + dt));
  if (q.tint) q.tint = q.tint.map(k => Object.assign({}, k, { at: r3(k.at + dt) }));
  q.seedKey = seedKey; q.story = story;
  return q;
}

// title card lines, measured in the page's own font so the paint can land as the full stop
async function measure(lines, size) {
  const browser = await launch();
  const page = await browser.newPage();
  await page.goto('file://' + path.join(__dirname, 'page.html'));
  const w = await page.evaluate(async ([lines, size]) => {
    await document.fonts.load("100px 'IM Fell English'"); await document.fonts.ready;
    const NS = 'http://www.w3.org/2000/svg', t = document.createElementNS(NS, 'text');
    t.setAttribute('font-family', "'IM Fell English', Georgia, serif");
    document.getElementById('svg').appendChild(t);
    return lines.map((L, i) => { t.setAttribute('font-size', [].concat(size)[i] || size); t.textContent = L; return t.getComputedTextLength(); });
  }, [lines, size]);
  await browser.close();
  return w;
}

// a title card: lines centred on its panel; a final "." becomes the landing spot for the paint.
// C.sub: an optional smaller line under the title that inks on once the paint has landed.
async function card(C, panelX, t0) {
  const size = C.size || 104, lh = size * 1.22, subSize = C.subSize || 50;
  const lines = C.lines.slice();
  const stop = /\.$/.test(lines[lines.length - 1]) && C.paint !== false;
  if (stop) lines[lines.length - 1] = lines[lines.length - 1].replace(/\.$/, '');
  const widths = await measure(C.sub ? lines.concat(C.sub) : lines, lines.map(() => size).concat(subSize));
  const y0 = (C.y || 470) - (lines.length - 1) * lh / 2 + size * 0.32 - (C.sub ? subSize * 0.95 : 0);
  const titles = lines.map((text, i) => {
    const cx = W / 2 + (stop && i === lines.length - 1 ? -size * 0.08 : 0);
    const a = t0 + (C.at || 0.3) + i * 0.7;
    return { text, size, x: panelX + cx, y: y0 + i * lh, x0: panelX + cx - widths[i] / 2, x1: panelX + cx + widths[i] / 2, t0: a, t1: a + 0.5 + 0.35 * widths[i] / 900 };
  });
  const last = titles[titles.length - 1];
  const land = stop ? { pos: [last.x1 - panelX + size * 0.27, last.y - size * 0.1], R: Math.round(size * 0.12), t: r3(last.t1 + (C.paintDelay || 0.45)) } : null;
  if (C.sub) {
    const sw = widths[lines.length], a = (land ? land.t : last.t1) + 0.2;
    titles.push({ text: C.sub, size: subSize, x: panelX + W / 2, y: last.y + subSize * 1.9, x0: panelX + W / 2 - sw / 2, x1: panelX + W / 2 + sw / 2, t0: r3(a), t1: r3(a + 0.45 + 0.35 * sw / 900) });
  }
  return { titles, land };
}

// the tease ("And why ...? That's another story."): where it starts, and where the audio may end before it
const norm = s => s.toLowerCase().replace(/[^a-z0-9]/g, '');
function teaseCut(S, breath) {
  const w = S.words;
  let i = -1;
  for (let k = w.length - 2; k > 0; k--) if (norm(w[k].w) === 'and' && norm(w[k + 1].w) === 'why') { i = k; break; }
  if (i < 0) throw new Error(`${S.id}: no "And why ..." tease in words.json`);
  const before = w[i - 1], room = w[i].s - before.e;
  return { i, teaseStart: w[i].s, lastEnd: before.e, audioEnd: r3(before.e + Math.max(0.05, Math.min(breath, room - 0.1))) };
}

// the sign-off ("That's another story."), which a chaptered film never plays (Matthew, 2026-10-16):
// the audio ends `breath` s after the question's last word, snapped into a real silence before "That's"
function silences(file) {
  const r = spawnSync('ffmpeg', ['-hide_banner', '-nostats', '-i', file, '-af', 'silencedetect=n=-38dB:d=0.05', '-f', 'null', '-'], { encoding: 'utf8' });
  const a = [...r.stderr.matchAll(/silence_start: ([\d.]+)/g)].map(m => +m[1]), b = [...r.stderr.matchAll(/silence_end: ([\d.]+)/g)].map(m => +m[1]);
  return a.map((x, i) => [x, b[i] != null ? b[i] : 1e9]);
}
function signoffCut(S, breath) {
  const w = S.words;
  const i = w.findIndex((x, k) => k > w.length - 6 && norm(x.w) === 'thats' && w[k + 1] && norm(w[k + 1].w) === 'another');
  if (i < 0) throw new Error(`${S.id}: no "That's another story." in words.json`);
  const q = w[i - 1], want = q.e + breath, lo = q.e + 0.12, hi = w[i].e - 0.2;   // "That's" may be timed early (09)
  let at = null, bd = 1e9;
  for (const [a, b] of silences(S.audio)) {
    const A = Math.max(a + 0.05, lo), B = Math.min(b - 0.01, hi); if (A > B) continue;
    const c = Math.min(Math.max(want, A), B); if (Math.abs(c - want) < bd) { bd = Math.abs(c - want); at = c; }
  }
  if (at == null) { at = Math.min(want, w[i].s - 0.05); console.warn(`  ! ${S.id}: no silence found before "That's"; cutting at ${at.toFixed(2)}`); }
  return { i, teaseStart: w[i].s, lastEnd: q.e, audioEnd: r3(at), signoff: true };
}

// YouTube's chapter format: m:ss, or h:mm:ss past an hour
const stamp = t => { t = Math.floor(t); const h = Math.floor(t / 3600), m = Math.floor(t / 60) % 60, s = String(t % 60).padStart(2, '0'); return h ? `${h}:${String(m).padStart(2, '0')}:${s}` : `${m}:${s}`; };

(async () => {
  // ---------------------------------------------------------------- stories on one timeline
  // without "chapters" the film is one untitled chapter whose stories all keep their teases (as before)
  const CHAPTERS = CFG.chapters || [{ title: null, stories: CFG.stories, keepTeases: true }];
  const SEAM = CFG.seamGap != null ? CFG.seamGap : 1.0, BREATH = CFG.breath != null ? CFG.breath : 0.4;
  const CARD = Object.assign({ dur: 4.0, at: 0.75, paintDelay: 0.3 }, CFG.chapterCard || {});
  const stories = CHAPTERS.flatMap((ch, ci) => ch.stories.map((id, j) => {
    const dir = path.join(ROOT, 'stories', id);
    const S = loadStory(dir, { writeLayout: false });
    const warn = snapPaint(S.shots, S.words);
    for (const w of warn) console.warn(`  ! ${id}: ${w}`);
    S.lay = loadLayout(dir, S.shots, S.traced, { write: false });
    S.id = id; S.chapter = ci; S.opensChapter = j === 0;
    S.scenes = S.shots.scenes;
    // seamless inside a chapter: drop the tease line, its words and its scene
    if (j < ch.stories.length - 1 && !ch.keepTeases) {
      const c = teaseCut(S, BREATH);
      S.words = S.words.slice(0, c.i);
      S.narration = S.narration.slice(0, S.narration.lastIndexOf('And why'));
      S.scenes = S.scenes.filter(sc => sc.start < c.lastEnd && !(sc.paint.length && sc.paint.every(p => p.t >= c.teaseStart - 0.01)));
      for (const sc of S.scenes) for (const p of sc.paint) if (p.t >= c.teaseStart - 0.01) console.warn(`  ! ${id}: landing "${p.word}" @${p.t} is in the dropped tease`);
      S.cut = c;
    } else if (!ch.keepTeases) {   // a chapter's last story keeps its question, never the sign-off
      const c = signoffCut(S, BREATH);
      S.words = S.words.slice(0, c.i);
      S.narration = S.narration.slice(0, S.narration.lastIndexOf("That's another story"));
      for (const sc of S.scenes) for (const p of sc.paint) if (p.t >= c.lastEnd + 0.01) console.warn(`  ! ${id}: landing "${p.word}" @${p.t} is after the question`);
      S.cut = c;
    }
    S.first = S.words[0].s; S.last = S.words[S.words.length - 1].e;
    return S;
  }));
  // where a story's last panel ends: just after its last word, or a beat after a cliffhanger question
  // (its sign-off cut), so the paint holds on the question before the camera leaves for the card
  const tail = S => r3(S.cut && S.cut.signoff ? S.off + S.cut.audioEnd + 0.5 : S.off + S.last + 0.05);
  const introDur = CFG.intro ? (CFG.intro.dur || 4.2) : 0;
  // each titled chapter opens on its card: after the intro, or after the last chapter's tease
  const cards = [];
  stories.forEach((S, i) => {
    const prev = stories[i - 1], ch = CHAPTERS[S.chapter];
    if (S.opensChapter && ch.title) {
      const start = prev ? tail(prev) : introDur, dur = ch.dur || CARD.dur;
      S.card = { chapter: S.chapter, title: ch.title, start, end: r3(start + dur) };
      cards.push(S.card);
      S.off = S.card.end + GAP - S.first;
    } else S.off = !prev ? introDur - S.first : prev.off + prev.last + (prev.cut ? SEAM : GAP) - S.first;
  });

  const shots = { story: NAME, scenes: [], duration: 0 };
  const layout = { style: null, cover: false, scenes: [] };
  const words = [], narr = [], traced = {}, titles = [];
  let panel = 0;
  const style = JSON.parse(JSON.stringify(stories[0].lay.style));
  style.hangIntro = true;
  style.reel = Object.assign({}, style.reel || {}, { on: true, start: { on: false }, brand: Object.assign({}, BRAND) });
  layout.style = style;

  if (CFG.intro) {
    const c = await card(CFG.intro, 0, 0);
    titles.push(...c.titles);
    const sc = { id: 'intro', panel: 0, start: 0, end: introDur, art: [], paint: [] };
    const ls = { id: 'intro', art: [], paint: [] };
    if (c.land) { sc.paint.push({ t: c.land.t }); ls.paint.push({ t: c.land.t, pos: c.land.pos, R: c.land.R, seedKey: 'intro-stop' }); }
    shots.scenes.push(sc); layout.scenes.push(ls);
    panel = 1;
  }

  const sameArt = (a, b) => a.length === b.length && a.every((x, i) => x.id === b[i].id);
  for (const [si, S] of stories.entries()) {
    const ns = id => `${si + 1}:${id}`;
    for (const id of S.ids) traced[ns(id)] = S.traced[id];
    for (const w of S.words) words.push({ w: w.w, s: r3(w.s + S.off), e: r3(w.e + S.off) });
    narr.push(S.narration.trim());
    const prev = stories[si - 1];
    if (S.card) {      // the chapter's title card, on its own panel
      const C = CHAPTERS[S.chapter], c = await card({ lines: [C.title.replace(/\.?$/, '.')], sub: C.sub, at: CARD.at, paintDelay: CARD.paintDelay, size: CARD.size, subSize: CARD.subSize }, panel * PITCH, S.card.start);
      titles.push(...c.titles);
      const id = `chapter-${S.chapter + 1}`;
      const sc = { id, panel: panel++, start: S.card.start, end: S.card.end, art: [], paint: [] }, ls = { id, art: [], paint: [] };
      if (c.land) { S.card.stop = c.land.t; sc.paint.push({ t: c.land.t }); ls.paint.push({ t: c.land.t, pos: c.land.pos, R: c.land.R, seedKey: id + '-stop' }); }
      shots.scenes.push(sc); layout.scenes.push(ls);
    }
    for (const [k, sc] of S.scenes.entries()) {
      const ls = S.lay.scenes.find(x => x.id === sc.id);
      const { art, s } = relayout(ls, S.traced);
      const paint = ls.paint.map(p => shiftPaint(p, S.off, ns, s, `${S.id}:${p.word}${p.t}`, S.id));
      let start = r3(sc.start + S.off), end = r3(sc.end + S.off);
      if (k === 0 && S.card) start = S.card.end;
      else if (k === 0 && prev) start = tail(prev);
      if (k === S.scenes.length - 1 && si < stories.length - 1) end = tail(S);
      if (k === S.scenes.length - 1 && si === stories.length - 1 && S.cut) end = r3(S.off + S.cut.audioEnd + 0.1);
      const lastSc = shots.scenes[shots.scenes.length - 1], lastLs = layout.scenes[layout.scenes.length - 1];
      // the bridge picture: the next story opens on the drawings the last one closed on -> one panel
      if (k === 0 && prev && !S.card && lastLs && sameArt(lastLs.origArt || [], ls.art)) {
        const map = {}; for (const a of lastLs.art) map[ns(a.seedKey)] = a.id;   // by the drawing's own id (relayout reorders)
        const scale = lastLs.scale / s;
        for (const p of paint) { p.art = map[p.art] || p.art; if (p.R) p.R = Math.max(12, Math.round(p.R * scale)); }
        lastLs.paint.push(...paint);
        lastSc.paint.push(...paint.map(p => ({ word: p.word, t: p.t })));
        lastSc.end = end; lastSc.merged = (lastSc.merged || [lastSc.id]).concat(`${si + 1}-${sc.id}`);
        continue;
      }
      const id = `${si + 1}-${sc.id}`;
      shots.scenes.push({ id, panel: panel++, start, end, story: S.id, art: art.map(a => ({ id: ns(a.id) })), paint: paint.map(p => ({ word: p.word, t: p.t })) });
      layout.scenes.push({ id, art: art.map(a => Object.assign({}, a, { id: ns(a.id), seedKey: a.id })), paint, origArt: ls.art, scale: s });
    }
  }
  const lastS = stories[stories.length - 1];
  shots.duration = r3(lastS.off + (lastS.cut ? lastS.cut.audioEnd + 0.1 : lastS.shots.duration));
  // after a cut sign-off the reel's slip waits a beat past the question, so the paint is seen on its landing
  let endWords = lastS.cut ? words.concat([{ w: '', s: r3(lastS.off + lastS.cut.audioEnd + 0.15), e: r3(lastS.off + lastS.cut.audioEnd + 0.2) }]) : words;

  if (CFG.outro) {
    const od = CFG.outro.dur || 3.5, o0 = r3(lastS.off + lastS.last + 0.05);
    const c = await card(Object.assign({ at: 1.0 }, CFG.outro), panel * PITCH, o0);
    titles.push(...c.titles);
    const sc = { id: 'outro', panel: panel++, start: o0, end: r3(o0 + od), art: [], paint: [] };
    const ls = { id: 'outro', art: [], paint: [] };
    if (c.land) { sc.paint.push({ t: c.land.t }); ls.paint.push({ t: c.land.t, pos: c.land.pos, R: c.land.R, seedKey: 'outro-stop' }); }
    shots.scenes[shots.scenes.length - 1].end = o0;
    shots.scenes.push(sc); layout.scenes.push(ls);
    shots.duration = r3(o0 + od);
    endWords = words.concat([{ w: '', s: r3(o0 + od - 0.3), e: r3(o0 + od - 0.25) }]);   // the reel waits for the card
  }

  // ---------------------------------------------------------------- seams: a Short's last landing may hold to the end
  // (a fill that never drains, a soak after the last word). In a thread the next landing comes ~2 s later,
  // so the paint must be free to leave before it.
  const allPaint = layout.scenes.flatMap(s => s.paint).sort((a, b) => a.t - b.t);
  const fixes = [];
  allPaint.forEach((p, i) => {
    const nx = allPaint[i + 1]; if (!nx || nx.story === p.story) return;   // only at a seam between stories
    if (p.fill && p.fill.drain && p.fill.drain[1] > nx.t - 0.55) {
      const d1 = r3(nx.t - 0.55), dur = Math.min(0.6, p.fill.drain[1] - p.fill.drain[0]), d0 = r3(Math.max(p.t + 0.9, d1 - dur));
      fixes.push(`fill "${p.word}" @${p.t}: drain ${p.fill.drain.join('-')} -> ${d0}-${d1}`); p.fill.drain = [d0, Math.max(d0 + 0.2, d1)];
    }
    if (p.soak != null && p.soak > nx.t - 1.0) { const v = r3(Math.max(p.t + 0.3, nx.t - 1.0)); fixes.push(`soak "${p.word}" @${p.t}: ${p.soak} -> ${v}`); p.soak = v; }
    if (p.slide && p.slide.at + (p.slide.dur || 0.5) > nx.t - 0.6) { const v = r3(Math.max(p.t + 0.2, nx.t - 0.6 - (p.slide.dur || 0.5))); fixes.push(`slide "${p.word}" @${p.t}: ${p.slide.at} -> ${v}`); p.slide.at = v; }
  });
  for (const f of fixes) console.log('seam: ' + f);

  // ---------------------------------------------------------------- plan
  const plan = planFrom({ shots, words, narration: narr.join('\n'), traced, ids: Object.keys(traced), layout, audio: path.join(OUT, 'voice.wav') }, GEOM);
  for (const w of plan.warnings) console.warn('  ! ' + w);
  plan.titles = titles;
  plan.reel = reelMap(plan, endWords);
  plan.frames = plan.reel.frames; plan.duration = plan.frames / plan.fps;
  if (plan.reel.brand) {
    const mf = path.join(ROOT, plan.reel.brand.mark);
    if (fs.existsSync(mf)) plan.reel.brand.data = JSON.parse(fs.readFileSync(mf, 'utf8'));
  }
  for (const n of plan.reel.notes) console.log('reel: ' + n);
  plan.cues = plan.cues.concat(plan.reel.cues).sort((a, b) => a.t - b.t);

  // timeline summary
  const bounds = stories.map((S, i) => Object.assign({ story: S.id, voiceAt: r3(S.off), firstWord: r3(S.off + S.first), lastWord: r3(S.off + S.last) }, S.cut ? { [S.cut.signoff ? 'signoffDropped' : 'teaseDropped']: r3(S.off + S.cut.teaseStart), audioEnd: r3(S.off + S.cut.audioEnd) } : {}));
  // YouTube chapters: the first at 0:00, each one from the moment its title card comes in
  const chapters = cards.map((c, i) => ({ t: i === 0 ? 0 : c.start, title: c.title }));
  if (chapters.length) {
    fs.writeFileSync(path.join(OUT, 'chapters.txt'), chapters.map(c => `${stamp(c.t)} ${c.title}`).join('\n') + '\n');
    if (chapters.length < 3) console.warn(`  ! YouTube shows chapters only when there are at least 3 (this film has ${chapters.length})`);
    chapters.forEach((c, i) => { const nx = chapters[i + 1] ? chapters[i + 1].t : plan.duration; if (nx - c.t < 10) console.warn(`  ! chapter "${c.title}" is under 10 s; YouTube needs 10 s each`); });
    console.log('chapters:\n' + chapters.map(c => `  ${stamp(c.t)} ${c.title}`).join('\n'));
  }
  fs.writeFileSync(path.join(OUT, 'timeline.json'), JSON.stringify({ name: NAME, frames: plan.frames, duration: r3(plan.duration), intro: introDur, gap: GAP, seamGap: SEAM, chapters: cards, stories: bounds,
    panels: plan.scenes.map(s => ({ id: s.id, panel: s.panel, start: r3(s.start), end: r3(s.end), art: s.art.map(a => [a.id, Math.round(a.left - s.x0), Math.round(a.top), Math.round(a.w), Math.round(a.h)]) })),
    seams: fixes }, null, 1));
  fs.writeFileSync(path.join(OUT, 'cues.json'), JSON.stringify(plan.cues, null, 1));
  console.log(`thread ${NAME}: ${stories.length} stories, ${plan.scenes.length} panels, ${plan.landings.length} landings, ${(plan.duration / 60).toFixed(2)} min (${plan.frames} frames)`);
  if (opt('plan')) { console.log(JSON.stringify(bounds, null, 1)); return; }

  // ---------------------------------------------------------------- the narration: each voice.mp3 placed at its offset, untouched
  const voice = path.join(OUT, 'voice.wav');
  {
    const a = ['-v', 'error', '-y'], f = [];
    stories.forEach((S, i) => {
      a.push('-i', S.audio);
      const ms = Math.round(S.off * 1000);
      // a seamless join ends the voice in the silence before its tease (a 40 ms fade there only avoids a click)
      const cut = S.cut ? `atrim=end=${S.cut.audioEnd},afade=t=out:st=${r3(S.cut.audioEnd - 0.04)}:d=0.04,` : '';
      f.push(`[${i}:a]${cut}aresample=48000,aformat=sample_fmts=fltp:channel_layouts=mono,adelay=${ms}:all=1[v${i}]`);
    });
    f.push(`${stories.map((_, i) => `[v${i}]`).join('')}amix=inputs=${stories.length}:normalize=0:duration=longest[out]`);
    run('ffmpeg', [...a, '-filter_complex', f.join(';'), '-map', '[out]', '-c:a', 'pcm_s16le', voice]);
  }

  const R = makeRenderer({ OUT, name: NAME, opt, sfxDirs: [path.join(ROOT, 'sfx')], jpgHeight: 720 });
  const st = opt('stills');
  if (st) { await R.stills(plan, String(st).split(',').map(Number)); return; }
  if (opt('scene-stills')) {
    const ts = plan.scenes.map(sc => { const L = plan.landings.filter(L => L.scene === sc.idx).pop(); return L ? Math.min(sc.end - 0.05, L.t + 0.55) : (sc.start + sc.end) / 2; });
    await R.stills(plan, ts, 'scene'); return;
  }
  if (opt('seam-stills')) {   // across each story boundary: the last line, mid-breath, the pan, (the card,) the first landing
    const ts = [];
    stories.forEach((S, i) => {
      const firstL = plan.landings.find(L => L.word_t >= S.off + S.first - 0.01);
      if (S.card) {
        const a = S.card.start, stop = S.card.stop != null ? S.card.stop : (S.card.start + S.card.end) / 2;
        if (i > 0) ts.push(a - 1.0, a + 0.5);
        ts.push(stop - 0.25, Math.min(S.card.end - 0.1, stop + 1.3), S.card.end + 0.3);
      } else if (i > 0) { const a = stories[i - 1].off + stories[i - 1].last; ts.push(a - 1.0, a + 0.35, a + 0.9); }
      else return;
      ts.push(firstL ? firstL.t + 0.5 : S.off + S.first + 2);
    });
    await R.stills(plan, ts, 'seam'); return;
  }
  const t0 = Date.now();
  const r = await R.video(plan);
  fs.writeFileSync(path.join(OUT, 'render-log.json'), JSON.stringify({ when: new Date().toISOString(), frames: r.frames, renderSec: +r.renderSec.toFixed(1), totalSec: +((Date.now() - t0) / 1000).toFixed(1), out: path.relative(ROOT, r.out) }, null, 1));
})().catch(e => { console.error(e); process.exit(1); });
