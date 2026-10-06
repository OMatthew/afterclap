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
const { spawn, spawnSync } = require('child_process');
const { chromium } = require('./pw.cjs');
const { buildPlan } = require('./plan.cjs');
const { reelMap } = require('./reel.cjs');

const ROOT = path.resolve(__dirname, '..');
const args = process.argv.slice(2);
const story = path.resolve(args.find(a => !a.startsWith('--')) || '');
const opt = k => { const i = args.indexOf('--' + k); return i < 0 ? null : (args[i + 1] && !args[i + 1].startsWith('--') ? args[i + 1] : true); };
if (!fs.existsSync(path.join(story, 'shots.json'))) { console.error('usage: node engine/render.cjs <story-folder> [options]'); process.exit(1); }
const OUT = path.join(story, 'out');
fs.mkdirSync(OUT, { recursive: true });
const sname = path.basename(story).replace(/^\d+-/, '');

function run(cmd, a, o = {}) { const r = spawnSync(cmd, a, Object.assign({ stdio: 'inherit', maxBuffer: 1 << 26 }, o)); if (r.status !== 0) { console.error(cmd + ' ' + a.map(x => JSON.stringify(x)).join(' ')); throw new Error(`${cmd} failed (${r.status} ${r.signal || ''} ${r.error || ''})`); } }

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
    const fi = Math.max(0, Math.min(plan.frames - 1, Math.round(t * plan.fps))); // snap to a real frame
    const tf = fi / plan.fps, m = plan.reel.map[fi];
    await page.evaluate(m => renderAt(m.tau, m), m);
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
      await page.evaluate(m => renderAt(m.tau, m), plan.reel.map[f]);
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
  const out = finish(plan, silent, f0, n, renderSec, P);
  return { out, renderSec, frames: n };
}

// master (full quality, not committed) + review copy squeezed under ~19 MB for the repo
function finish(plan, silent, f0, n, renderSec, P) {
  const fps = plan.fps, parts = path.join(OUT, 'parts');
  // a --from/--to preview never overwrites the real master
  const master = opt('from') || opt('to') ? path.join(parts, 'range-master.mp4') : path.join(OUT, `${sname}-master.mp4`);
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

// Short review clips of the film-reel ends: the first 4 s, the last 4 s, and the loop seam
// (last 2 s straight into the first 2 s, as Shorts plays it)
function clips(plan) {
  const master = path.join(OUT, `${sname}-master.mp4`);
  if (!fs.existsSync(master)) { console.warn('clips: no master yet'); return; }
  const dir = path.join(OUT, 'reel-clips'); fs.mkdirSync(dir, { recursive: true });
  const D = plan.frames / plan.fps;
  const enc = ['-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart'];
  run('ffmpeg', ['-v', 'error', '-y', '-i', master, '-t', '4', ...enc, path.join(dir, `${sname}-start-4s.mp4`)]);
  run('ffmpeg', ['-v', 'error', '-y', '-ss', (D - 4).toFixed(3), '-i', master, '-t', '4', ...enc, path.join(dir, `${sname}-end-4s.mp4`)]);
  run('ffmpeg', ['-v', 'error', '-y', '-ss', (D - 2).toFixed(3), '-i', master, '-t', '2', '-i', master,
    '-filter_complex', '[0:v]setpts=PTS-STARTPTS[v0];[0:a]asetpts=PTS-STARTPTS[a0];[1:v]trim=0:2,setpts=PTS-STARTPTS[v1];[1:a]atrim=0:2,asetpts=PTS-STARTPTS[a1];[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]',
    '-map', '[v]', '-map', '[a]', ...enc, path.join(dir, `${sname}-loop-seam-4s.mp4`)]);
  console.log('clips:', path.relative(ROOT, dir));
}

function lufs(file, ss = 0, t = null) {
  const a = ['-hide_banner', '-nostats', '-ss', String(ss)].concat(t ? ['-t', String(t)] : []).concat(['-i', file, '-af', 'ebur128', '-f', 'null', '-']);
  const r = spawnSync('ffmpeg', a, { encoding: 'utf8' });
  const m = [...(r.stderr || '').matchAll(/I:\s+(-?[\d.]+) LUFS/g)];
  return m.length ? +m[m.length - 1][1] : -23;
}

// Narration + film-reel projector sounds + optional foley. The narration is mixed exactly as it is.
// Foley hook: WAVs named after cue types (splat.wav, lift.wav, drop.wav, gather.wav, scroll.wav,
// pen.wav, drain.wav, slide.wav, soak.wav, clatter.wav) in <story>/sfx/ or ./sfx/ play at each cue.
function mux(plan, silent, out, start, dur) {
  const sfxDir = [path.join(story, 'sfx'), path.join(ROOT, 'sfx')].find(d => fs.existsSync(d));
  const a = ['-v', 'error', '-y', '-i', silent, '-ss', start.toFixed(3), '-t', dur.toFixed(3), '-i', plan.audio];
  const filt = [];
  const reel = plan.reel && plan.reel.cfg && plan.reel.cfg.on !== false ? plan.reel : null;
  const snd = reel ? reel.cfg.sound : null;
  const startF = snd && snd.start && fs.existsSync(path.join(ROOT, snd.start)) ? path.join(ROOT, snd.start) : null;
  const endF = snd && snd.end && fs.existsSync(path.join(ROOT, snd.end)) ? path.join(ROOT, snd.end) : null;
  filt.push(`[1:a]apad=whole_dur=${dur.toFixed(3)},asplit=3[vo][sc1][sc2]`);
  const mixIns = ['[vo]'];
  let k = 2;
  if (startF || endF) {
    const Iv = lufs(plan.audio);
    if (startF && start < 1.2) {            // under the first words, ~24 dB below the voice, ducked by it
      const [t0, t1] = snd.startTrim, len = t1 - t0;
      const g = (Iv + snd.startDb) - lufs(startF, t0, len);
      a.push('-i', startF);
      filt.push(`[${k}:a]atrim=start=${t0}:end=${t1},asetpts=PTS-STARTPTS,afade=t=out:st=${(len - snd.startFadeOut).toFixed(3)}:d=${snd.startFadeOut},volume=${g.toFixed(1)}dB,aformat=channel_layouts=stereo[s0];[s0][sc1]sidechaincompress=threshold=0.02:ratio=4:attack=5:release=180[rs]`);
      mixIns.push('[rs]'); k++;
    }
    if (endF) {                             // the run-out: the clatter's own wind-down tail lands on it
      // the clatter runs on through the run-out (louder once the voice is done); its own wind-down
      // tail starts as the last frame leaves and plays over the blank paper
      const tRun = reel.runEnd / plan.fps, tIn = reel.e0 - 0.1;
      let off = snd.endTail - (tRun - tIn), at = tIn;
      if (off < 0) { at -= off; off = 0; }
      const g = (Iv + snd.endDb) - lufs(endF, off);
      const ms = Math.max(0, Math.round((at - start) * 1000));
      if (at + 3.5 > start && at < start + dur) {
        a.push('-ss', off.toFixed(3), '-i', endF);
        filt.push(`[${k}:a]asetpts=PTS-STARTPTS,afade=t=in:d=${snd.endFadeIn},volume=${g.toFixed(1)}dB,aformat=channel_layouts=stereo,adelay=${ms}|${ms}[e0];[e0][sc2]sidechaincompress=threshold=0.012:ratio=10:attack=5:release=220[re]`);
        mixIns.push('[re]'); k++;
      }
    }
  }
  if (!mixIns.includes('[rs]')) filt.push('[sc1]anullsink');
  if (!mixIns.includes('[re]')) filt.push('[sc2]anullsink');
  if (sfxDir) {
    const byType = {};
    for (const c of plan.cues) { const f = path.join(sfxDir, c.type + '.wav'); if (fs.existsSync(f) && c.t >= start && c.t < start + dur) (byType[c.type] = byType[c.type] || { f, cues: [] }).cues.push(c); }
    for (const [type, { f, cues }] of Object.entries(byType)) {
      a.push('-i', f);
      filt.push(`[${k}:a]asplit=${cues.length}${cues.map((_, i) => `[${type}${i}]`).join('')}`);
      cues.forEach((c, i) => { const ms = Math.max(0, Math.round((c.t - start) * 1000)); filt.push(`[${type}${i}]adelay=${ms}|${ms},volume=${c.gain || 0.5}[${type}d${i}]`); mixIns.push(`[${type}d${i}]`); });
      k++;
    }
  }
  filt.push(`${mixIns.join('')}amix=inputs=${mixIns.length}:normalize=0:duration=first[aout]`);
  a.push('-filter_complex', filt.join(';'), '-map', '0:v', '-map', '[aout]');
  a.push('-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-t', dur.toFixed(3), '-movflags', '+faststart', out);
  run('ffmpeg', a);
}

(async () => {
  ensureTraced();
  const plan = buildPlan(story);
  for (const w of plan.warnings) console.warn('  ! ' + w);
  const words = JSON.parse(fs.readFileSync(path.join(story, 'words.json'), 'utf8'));
  plan.reel = reelMap(plan, words);
  plan.frames = plan.reel.frames; plan.duration = plan.frames / plan.fps;   // the run-out may extend the video
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
