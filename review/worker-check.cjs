// Exercises the real FFV1/concat/final-encode pipeline with fixed PNGs instead of Chromium.
const fs = require('node:fs'), path = require('node:path'), assert = require('node:assert/strict');
const { execFileSync } = require('node:child_process');
const dir = path.join(__dirname, 'worker-test');
fs.mkdirSync(path.join(dir, 'source'), { recursive: true });
execFileSync('ffmpeg', ['-v','error','-y','-f','lavfi','-i','testsrc=size=192x108:rate=30','-frames:v','35',path.join(dir,'source/%03d.png')]);
const fakeChromium = { launch: async () => ({ newPage: async () => {
  let frame = 0;
  return { on() {}, goto: async () => {}, waitForFunction: async () => {},
    evaluate: async (fn, m) => { if (m && m.tau != null) frame = Math.round(m.tau * 30); },
    screenshot: async () => fs.readFileSync(path.join(dir, 'source', String(frame + 1).padStart(3, '0') + '.png')) };
}, close: async () => {} }) };
require.cache[require.resolve('../engine/pw.cjs')] = { exports: { chromium: fakeChromium } };
const { makeRenderer, workerCount } = require('../engine/frames.cjs');
for (const x of [0, -1, 4, 1.5, 'no', true]) assert.throws(() => workerCount(x));
assert.equal(workerCount(3), 3);
const plan = { fps: 30, frames: 35, W: 192, H: 108,
  audio: path.join(__dirname, '../stories/lf-demo/voice.mp3'), cues: [],
  reel: { cfg: { on: false }, map: Array.from({ length: 35 }, (_, f) => ({ tau: f / 30 })) } };
(async () => {
  for (const workers of [1, 3]) {
    const OUT = path.join(dir, 'w' + workers); fs.mkdirSync(OUT, { recursive: true });
    const opts = { workers, 'no-review': true };
    await makeRenderer({ OUT, name: 'test', opt: k => opts[k], sfxDirs: [] }).video(plan);
  }
  const f = w => path.join(dir, 'w' + w, 'parts/video.mp4');
  assert(fs.readFileSync(f(1)).equals(fs.readFileSync(f(3))));
  for (const w of [1,3]) {
    const decoded = execFileSync('ffmpeg', ['-v','error','-i',path.join(dir,'w'+w,'parts/joined.mkv'),'-pix_fmt','rgb24','-f','rawvideo','-'], { maxBuffer: 10e6 });
    const source = execFileSync('ffmpeg', ['-v','error','-framerate','30','-i',path.join(dir,'source/%03d.png'),'-pix_fmt','rgb24','-f','rawvideo','-'], { maxBuffer: 10e6 });
    assert(decoded.equals(source), 'lossless join must retain all 35 source frames');
  }
  console.log('PASS: 35 source frames retained losslessly, final silent MP4 byte-identical with 1 and 3 workers');
  fs.rmSync(dir, { recursive: true, force: true });
})().catch(e => { console.error(e); process.exitCode = 1; });
