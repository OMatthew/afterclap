// Default layout for a story, merged with whatever is already in <story>/layout.json.
// A layout says where each drawing sits in its scene (scene-local px, 1080x1920 per scene)
// (landscape: 1920x1080, style.frame = 'landscape')
// and where on each drawing the paint lands. Hand edits to layout.json always win; this
// only fills gaps, so a new story gets a usable starting point from its shots.json alone.
//
// style.frame: 'portrait' (default) or 'landscape'; style.captions: true (default) or false.
// scene.chapter: a title for the chapter sidecar (also accepted on shots.json scenes).
// Optional keys (times are seconds, taken from words.json in the story's layout.py; nothing changes when they're absent):
//   scene.letters: [{text, at, x, y, size?, dur?, id?, weight?}]  a number or a few words written by hand at a word time (x, y = centre in scene px; size = digit height, ~120-180; glyphs: 0-9 $ % . , ' - + / : ! ? a-z, engine/letters.cjs); a paint landing can sit on it with "art": "letters:<text>" (or its id)
//   art.late: [{at, box: [u0, v0, u1, v1], dur?}]  the strokes wholly inside the box (fractions of the drawing, like paint "at") wait and draw on at a word time
//   art.drawAt: t  a second drawing in the scene waits and draws on at a word time
//   art.nudge: [{at, dx?, dy?, rot?, dur?, stay?}]  the drawing shifts (px) or tips (degrees, about art.pivot, default its centre) on a word and eases back (stay: it keeps the new pose); ink only, so keep it small or off drawings with paint on them
const fs = require('fs'), path = require('path');

// Safe art zone in a 1080x1920 frame: clear of the Shorts top bar, the caption band and the
// bottom/right UI. Captions sit at y ~1400, centred at x ~490.
const ZONE = { x0: 70, x1: 1010, y0: 200, y1: 1300 };

// Patterns by number of drawings in the scene: [cx, cy, boxW, boxH]
const PATTERNS = {
  1: [[540, 760, 840, 900]],
  2: [[390, 500, 600, 560], [680, 1010, 600, 520]],
  3: [[330, 420, 500, 420], [730, 770, 500, 420], [350, 1120, 520, 360]],
  4: [[300, 420, 440, 400], [770, 520, 440, 400], [310, 950, 440, 380], [760, 1080, 440, 360]],
};

const LANDSCAPE_PATTERNS = {
  1: [[960, 465, 1440, 720]],
  2: [[510, 460, 780, 700], [1410, 460, 780, 700]],
  3: [[350, 450, 520, 660], [960, 450, 520, 660], [1570, 450, 520, 660]],
  4: [[510, 265, 740, 340], [1410, 265, 740, 340], [510, 665, 740, 340], [1410, 665, 740, 340]],
};

function defaultLayout(shots, traced, frame = 'portrait') {
  const patterns = frame === 'landscape' ? LANDSCAPE_PATTERNS : PATTERNS;
  const scenes = shots.scenes.map(sc => {
    const pat = patterns[Math.min(4, sc.art.length)] || patterns[4];
    const art = sc.art.map((a, i) => {
      const [cx, cy, bw, bh] = pat[i % pat.length];
      const tr = traced[a.id];
      const asp = tr ? tr.size[0] / tr.size[1] : 1;
      const w = Math.round(Math.min(bw, bh * asp));
      return { id: a.id, x: cx, y: cy, w };
    });
    const paint = sc.paint.map((p, i) => ({
      word: p.word, t: p.t,
      art: sc.art[Math.min(i, sc.art.length - 1)].id,
      at: [0.5, 0.5],
    }));
    return { id: sc.id, art, paint };
  });
  return {
    style: { ink: 6.4, inner: 0.68, minLen: 16, boil: 0.35, boilFps: 4, reel: { on: true } },
    cover: { words: ['Why?'], art: shots.scenes[0].art[0].id, at: [0.5, 0.5] },
    scenes,
  };
}

// merge: keep everything already in `cur`, add missing scenes / art / paint entries
function merge(def, cur) {
  if (!cur) return def;
  const out = JSON.parse(JSON.stringify(cur));
  out.style = Object.assign({}, def.style, cur.style || {});
  out.cover = cur.cover || def.cover;
  out.scenes = def.scenes.map(ds => {
    const cs = (cur.scenes || []).find(s => s.id === ds.id);
    if (!cs) return ds;
    const art = ds.art.map(da => (cs.art || []).find(a => a.id === da.id) || da);
    const paint = ds.paint.map((dp, i) => {
      const cp = (cs.paint || []).find(p => p.word === dp.word && Math.abs(p.t - dp.t) < 0.4);
      return cp ? Object.assign({}, dp, cp, { t: dp.t, word: dp.word }) : dp;
    });
    return Object.assign({}, cs, { id: ds.id, art, paint });
  });
  return out;
}

function loadLayout(story, shots, traced, { write = true } = {}) {
  const file = path.join(story, 'layout.json');
  const cur = fs.existsSync(file) ? JSON.parse(fs.readFileSync(file, 'utf8')) : null;
  const lay = merge(defaultLayout(shots, traced, cur?.style?.frame), cur);
  if (write && JSON.stringify(lay) !== JSON.stringify(cur)) fs.writeFileSync(file, JSON.stringify(lay, null, 1) + '\n');
  return lay;
}

module.exports = { loadLayout, defaultLayout, ZONE, PATTERNS };
