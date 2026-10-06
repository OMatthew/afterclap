// Default layout for a story, merged with whatever is already in <story>/layout.json.
// A layout says where each drawing sits in its scene (scene-local px, 1080x1920 per scene)
// and where on each drawing the paint lands. Hand edits to layout.json always win; this
// only fills gaps, so a new story gets a usable starting point from its shots.json alone.
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

function defaultLayout(shots, traced) {
  const scenes = shots.scenes.map(sc => {
    const pat = PATTERNS[Math.min(4, sc.art.length)] || PATTERNS[4];
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
    style: { ink: 6.4, inner: 0.68, minLen: 16, boil: 0.35, boilFps: 4,
      reel: { on: true, start: [5, 4, 3, 2, 1], end: [1, 2, 2, 3, 3, 4, 5], endAt: null, weave: 2, flicker: 0.04, pullIn: 90, creep: 240 } },
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
  const lay = merge(defaultLayout(shots, traced), cur);
  if (write && JSON.stringify(lay) !== JSON.stringify(cur)) fs.writeFileSync(file, JSON.stringify(lay, null, 1) + '\n');
  return lay;
}

module.exports = { loadLayout, defaultLayout, ZONE, PATTERNS };
