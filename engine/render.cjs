#!/usr/bin/env node
// Afterclap renderer: one story folder in, one finished Short out.
//
//   node engine/render.cjs stories/01-dime                 trace (if needed) + video + cover
//   node engine/render.cjs stories/01-dime --stills 0.9,5.9 just stills (PNG + 1280px JPG)
//   node engine/render.cjs stories/01-dime --scene-stills   one still per scene (mid-hold)
//   node engine/render.cjs stories/01-dime --cover          just the cover frame
//   options: --par N (parallel parts, default = CPU count), --out name.mp4, --from s --to s (preview a range),
//            --retrace (force the trace step), --no-cover, --remux (rebuild the mp4s from the last frames),
//            --max-mb N (size cap for the committed review copy, default 19)
const fs = require('fs'), path = require('path'), os = require('os');
const { spawn, spawnSync } = require('child_process');
const { chromium } = require('./pw.cjs');
const { buildPlan } = require('./plan.cjs');

const ROOT = path.resolve(__dirname, '..');
const args = process.argv.slice(2);
const story = path.resolve(args.find(a => !a.startsWith('--')) || '');
const opt = k => { const i = args.indexOf('--' + k); return i < 0 ? null : (args[i + 1] && !args[i + 1].startsWith('--') ? args[i + 1] : true); };
if (!fs.existsSync(path.join(story, 'shots.json'))) { console.error('usage: node engine/render.cjs <story-folder> [options]'); process.exit(1); }
const OUT = path.join(story, 'out');
fs.mkdirSync(OUT, { recursive: true });
const sname = path.basename(story).replace(/^\d+-/, '');

function run(cmd, a, o = {}) { const r = spawnSync(cmd, a, Object.assign({ stdio: 'inherit' }, o)); if (r.status !== 0) throw new Error(`${cmd} failed (${r.status})`); }

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

// ---------------------------------------------------------------- browser
async function openPage(browser, plan) {
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  page.on('pageerror', e => console.error('page error:', e.message));
  await page.goto('file://' + path.join(__dirname, 'page.html'));
  await page.evaluate(p => window.__boot(p), plan);
  await page.waitForFunction(() => window.ready === true);
  return page;
}
const launch = () => chromium.launch({ args: ['--disable-gpu', '--force-color-profile=srgb', '--allow-file-access-from-files', '--font-render-hinting=none'] });

function toJpg(png, jpg, h = 1280) {
  run('ffmpeg', ['-v', 'error', '-y', '-i', png, '-vf', `scale=-2:${h}:flags=lanczos`, '-q:v', '3', jpg]);
}

async function stills(plan, times, tag = 'still') {
  const browser = await launch();
  const page = await openPage(browser, plan);
  const dir = path.join(OUT, 'stills'); fs.mkdirSync(dir, { recursive: true });
  const outs = [];
  for (const t of times) {
    const tf = Math.round(t * plan.fps) / plan.fps; // snap to a real frame
    await page.evaluate(t => renderAt(t), tf);
    const name = `${tag}_${tf.toFixed(2)}`;
    const png = path.join(dir, name + '.png');
    await page.screenshot({ path: png, type: 'png' });
    toJpg(png, path.join(dir, name + '.jpg'));
    outs.push(png);
  }
  await browser.close();
  console.log(`stills: ${outs.length} in ${path.relative(ROOT, dir)}`);
  return outs;
}

async function cover(plan) {
  const browser = await launch();
  const page = await openPage(browser, plan);
  await page.evaluate(() => renderCover());
  const png = path.join(OUT, `${sname}-cover.png`);
  await page.screenshot({ path: png, type: 'png' });
  await browser.close();
  console.log('cover:', path.relative(ROOT, png));
}

// ---------------------------------------------------------------- video
async function video(plan) {
  const fps = plan.fps;
  const f0 = opt('from') ? Math.round(+opt('from') * fps) : 0;
  const f1 = opt('to') ? Math.round(+opt('to') * fps) : plan.frames;
  const P = Math.max(1, +(opt('par') || os.cpus().length));
  const parts = path.join(OUT, 'parts'); fs.rmSync(parts, { recursive: true, force: true }); fs.mkdirSync(parts, { recursive: true });
  const n = f1 - f0, per = Math.ceil(n / P);
  const t0 = Date.now(); let done = 0;
  const browser = await launch();
  const files = [];
  await Promise.all(Array.from({ length: P }, async (_, w) => {
    const a = f0 + w * per, b = Math.min(f1, a + per);
    if (a >= b) return;
    const file = path.join(parts, `part_${String(w).padStart(2, '0')}.mp4`); files[w] = file;
    const page = await openPage(browser, plan);
    const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-',
      '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', '-r', String(fps), '-g', String(fps * 2), file], { stdio: ['pipe', 'inherit', 'inherit'] });
    const closed = new Promise((res, rej) => ff.on('close', c => c === 0 ? res() : rej(new Error('ffmpeg part failed ' + c))));
    for (let f = a; f < b; f++) {
      await page.evaluate(t => renderAt(t), f / fps);
      const buf = await page.screenshot({ type: 'jpeg', quality: 95 });
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      if (++done % 60 === 0) {
        const el = (Date.now() - t0) / 1000;
        console.log(`  ${done}/${n} frames  ${el.toFixed(0)}s  (~${(el / done * (n - done)).toFixed(0)}s left)`);
      }
    }
    ff.stdin.end(); await closed; await page.close();
  }));
  await browser.close();
  const renderSec = (Date.now() - t0) / 1000;
  const list = path.join(parts, 'list.txt');
  fs.writeFileSync(list, files.filter(Boolean).map(f => `file '${f}'`).join('\n'));
  const silent = path.join(parts, 'video.mp4');
  run('ffmpeg', ['-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', list, '-c', 'copy', silent]);
  finish(plan, silent, f0, n, renderSec, P);
  return { out, renderSec, frames: n };
}

// master (full quality, not committed) + review copy squeezed under ~19 MB for the repo
function finish(plan, silent, f0, n, renderSec, P) {
  const fps = plan.fps, parts = path.join(OUT, 'parts');
  const master = path.join(OUT, `${sname}-master.mp4`);
  mux(plan, silent, master, f0 / fps, n / fps);
  const out = path.join(OUT, opt('out') || `${sname}-rough.mp4`);
  const maxMB = +(opt('max-mb') || 19);
  const vk = Math.floor((maxMB * 8e6 * 0.96 / (n / fps) - 160e3) / 1000);
  const pass = path.join(parts, 'x264pass');
  run('ffmpeg', ['-v', 'error', '-y', '-i', master, '-c:v', 'libx264', '-preset', 'slow', '-b:v', vk + 'k', '-pass', '1', '-passlogfile', pass, '-pix_fmt', 'yuv420p', '-an', '-f', 'mp4', '/dev/null']);
  run('ffmpeg', ['-v', 'error', '-y', '-i', master, '-c:v', 'libx264', '-preset', 'slow', '-b:v', vk + 'k', '-pass', '2', '-passlogfile', pass, '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', out]);
  console.log(`video: ${path.relative(ROOT, out)} (${(fs.statSync(out).size / 1e6).toFixed(1)} MB review copy), master ${path.relative(ROOT, master)}  (${n} frames, render ${renderSec.toFixed(0)}s, ${(renderSec / n * 1000).toFixed(0)} ms/frame, ${P} parts)`);
  return out;
}

// Narration + optional foley. Foley hook: drop WAVs named after cue types (splat.wav, lift.wav,
// drop.wav, gather.wav, scroll.wav, pen.wav, drain.wav, slide.wav, soak.wav) into <story>/sfx/
// or ./sfx/, and each cue in out/cues.json plays its sound. No folder, no foley.
function mux(plan, silent, out, start, dur) {
  const sfxDir = [path.join(story, 'sfx'), path.join(ROOT, 'sfx')].find(d => fs.existsSync(d));
  const a = ['-v', 'error', '-y', '-i', silent, '-ss', start.toFixed(3), '-t', dur.toFixed(3), '-i', plan.audio];
  const filt = [];
  let mixIns = ['[1:a]'];  // narration
  if (sfxDir) {
    const byType = {};
    for (const c of plan.cues) { const f = path.join(sfxDir, c.type + '.wav'); if (fs.existsSync(f) && c.t >= start && c.t < start + dur) (byType[c.type] = byType[c.type] || { f, cues: [] }).cues.push(c); }
    let k = 2;
    for (const [type, { f, cues }] of Object.entries(byType)) {
      a.push('-i', f);
      filt.push(`[${k}:a]asplit=${cues.length}${cues.map((_, i) => `[${type}${i}]`).join('')}`);
      cues.forEach((c, i) => { const ms = Math.max(0, Math.round((c.t - start) * 1000)); filt.push(`[${type}${i}]adelay=${ms}|${ms},volume=${c.gain || 0.5}[${type}d${i}]`); mixIns.push(`[${type}d${i}]`); });
      k++;
    }
  }
  if (mixIns.length > 1) filt.push(`${mixIns.join('')}amix=inputs=${mixIns.length}:normalize=0:duration=first,apad[aout]`);
  else filt.push('[1:a]apad[aout]');
  a.push('-filter_complex', filt.join(';'), '-map', '0:v', '-map', '[aout]');
  a.push('-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-t', dur.toFixed(3), '-movflags', '+faststart', out);
  run('ffmpeg', a);
}

(async () => {
  ensureTraced();
  const plan = buildPlan(story);
  for (const w of plan.warnings) console.warn('  ! ' + w);
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
  if (opt('remux')) { // re-mux existing frames (e.g. after adding foley) without re-rendering
    finish(plan, path.join(OUT, 'parts', 'video.mp4'), 0, plan.frames, 0, 0); return;
  }
  const r = await video(plan);
  if (!opt('no-cover') && !opt('from')) await cover(plan);
  fs.writeFileSync(path.join(OUT, 'render-log.json'), JSON.stringify({ when: new Date().toISOString(), frames: r.frames, renderSec: +r.renderSec.toFixed(1), parts: +(opt('par') || os.cpus().length), cpus: os.cpus().length }, null, 1));
})().catch(e => { console.error(e); process.exit(1); });
