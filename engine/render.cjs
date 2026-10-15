#!/usr/bin/env node
// Afterclap renderer: one story folder in, one finished Short out.
//
//   node engine/render.cjs stories/01-dime                 trace (if needed) + video + cover
//   node engine/render.cjs stories/01-dime --stills 0.9,5.9 just stills (PNG + 1280px JPG)
//   node engine/render.cjs stories/01-dime --scene-stills   one still per scene (mid-hold)
//   node engine/render.cjs stories/01-dime --cover          just the cover frame
//   options: --par N (parallel parts, default = CPU count), --out name.mp4, --from s --to s (preview a range),
//            --retrace (force the trace step), --no-cover, --remux (rebuild the mp4s from the last frames),
//            --max-mb N (size cap for the committed review copy, default 19), --clips (film-reel review clips), --reel-stills (one still per start step)
const fs = require('fs'), path = require('path'), os = require('os');
const { buildPlan } = require('./plan.cjs');
const { makeRenderer, run } = require('./frames.cjs');
const { reelMap } = require('./reel.cjs');

const ROOT = path.resolve(__dirname, '..');
const args = process.argv.slice(2);
const story = path.resolve(args.find(a => !a.startsWith('--')) || '');
const opt = k => { const i = args.indexOf('--' + k); return i < 0 ? null : (args[i + 1] && !args[i + 1].startsWith('--') ? args[i + 1] : true); };
if (!fs.existsSync(path.join(story, 'shots.json'))) { console.error('usage: node engine/render.cjs <story-folder> [options]'); process.exit(1); }
const OUT = path.join(story, 'out');
fs.mkdirSync(OUT, { recursive: true });
const sname = path.basename(story).replace(/^\d+-/, '');

// ---------------------------------------------------------------- trace step
function ensureTraced() {
  const art = path.join(story, 'art'), tdir = path.join(art, 'traced');
  if (!fs.existsSync(art)) return;
  const pngs = fs.readdirSync(art).filter(f => /\.png$/i.test(f));
  const stale = pngs.filter(f => {
    const j = path.join(tdir, f.replace(/\.png$/i, '.json'));
    return opt('retrace') || !fs.existsSync(j) || fs.statSync(j).mtimeMs < fs.statSync(path.join(art, f)).mtimeMs;
  }).map(f => f.replace(/\.png$/i, ''));
  if (stale.length) {
    console.log(`trace: ${stale.length} drawing(s)`);
    run('python3', [path.join(ROOT, 'tools', 'trace.py'), story, ...stale]);
    run(process.execPath, [path.join(__dirname, 'inksvg.cjs'), story, ...stale]);
  }
}

// ---------------------------------------------------------------- frames, video, sound (shared with thread.cjs)
const R = makeRenderer({ OUT, name: sname, opt, sfxDirs: [path.join(story, 'sfx'), path.join(ROOT, 'sfx')] });
const { stills, cover, video, finish, clips } = R;

(async () => {
  ensureTraced();
  const plan = buildPlan(story);
  for (const w of plan.warnings) console.warn('  ! ' + w);
  const words = JSON.parse(fs.readFileSync(path.join(story, 'words.json'), 'utf8'));
  plan.reel = reelMap(plan, words);
  plan.frames = plan.reel.frames; plan.duration = plan.frames / plan.fps;   // the run-out may extend the video
  if (plan.reel.brand) {               // the brand mark: brand/a-mark.json (made by tools/brand_mark.py)
    const mf = path.join(ROOT, plan.reel.brand.mark);
    if (fs.existsSync(mf)) plan.reel.brand.data = JSON.parse(fs.readFileSync(mf, 'utf8'));
    else console.warn('  ! brand mark not found: ' + plan.reel.brand.mark + ' (run python3 tools/brand_mark.py)');
  }
  for (const n of plan.reel.notes) console.log('reel: ' + n);
  plan.cues = plan.cues.concat(plan.reel.cues).sort((a, b) => a.t - b.t);
  fs.writeFileSync(path.join(OUT, 'cues.json'), JSON.stringify(plan.cues, null, 1));
  // paint landings in frame terms, for tools/check_paint.py
  const camY = t => plan.camera.reduce((y, k) => { const u = Math.max(0, Math.min(1, (t - k.s0) / (k.s1 - k.s0))); const e = u < .5 ? 4 * u * u * u : 1 - Math.pow(-2 * u + 2, 3) / 2; return y + (k.y1 - k.y0) * e; }, 0);
  fs.writeFileSync(path.join(OUT, 'landings.json'), JSON.stringify(plan.landings.map(L => ({
    word: L.word, t: L.word_t, frame: Math.round(L.t * plan.fps), x: Math.round(L.x), y: Math.round(L.y - camY(L.t)), R: L.R })), null, 1));
  const st = opt('stills');
  if (st) { await stills(plan, String(st).split(',').map(Number)); return; }
  if (opt('scene-stills')) {
    const ts = plan.scenes.map(sc => { const L = plan.landings.filter(L => L.scene === sc.idx).pop(); return L ? L.t + 0.55 : (sc.start + sc.end) / 2; });
    await stills(plan, ts, 'scene'); return;
  }
  if (opt('cover')) { await cover(plan); return; }
  if (opt('brand-stills')) { // the brand beat, five moments to the last frame
    const B = plan.reel.brand, T = [B.start + 0.12, B.revealEnd, B.impact - 0.1, B.impact + 0.15, (plan.frames - 1) / plan.fps];
    await stills(plan, T, 'brand'); return;
  }
  if (opt('runout-stills')) { // four stills across the run-out
    const a = plan.reel.runStart, b = plan.reel.runEnd, fr = [0, 1, 2, 3].map(k => Math.round(a + (b - a) * (0.08 + 0.28 * k)));
    await stills(plan, fr.map(f => f / plan.fps), 'runout'); return;
  }
  if (opt('reel-stills')) { // one still per start step, plus the first locked frame
    const fr = plan.reel.startSteps.map(x => x.frame); fr.push(fr[fr.length - 1] + plan.reel.startSteps[plan.reel.startSteps.length - 1].hold);
    await stills(plan, fr.map(f => f / plan.fps), 'reel'); return;
  }
  if (opt('remux')) { // re-mux existing frames (e.g. after adding foley) without re-rendering
    finish(plan, path.join(OUT, 'parts', 'video.mp4'), 0, plan.frames, 0, 0); return;
  }
  if (opt('clips')) { clips(plan); return; }
  const r = await video(plan);
  if (!opt('no-cover') && !opt('from')) await cover(plan);
  if (!opt('from')) clips(plan);
  fs.writeFileSync(path.join(OUT, 'render-log.json'), JSON.stringify({ when: new Date().toISOString(), frames: r.frames, renderSec: +r.renderSec.toFixed(1), parts: +(opt('par') || os.cpus().length), cpus: os.cpus().length }, null, 1));
})().catch(e => { console.error(e); process.exit(1); });
