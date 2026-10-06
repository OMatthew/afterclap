#!/usr/bin/env node
// Write the re-inked drawing for each traced file as a single-colour SVG with a transparent
// background: art/traced/<id>.svg. Uses the same stroke model as the renderer.
//   node engine/inksvg.cjs stories/01-dime [id ...]
const fs = require('fs'), path = require('path');
const Ink = require('./ink.js');
const story = process.argv[2], only = new Set(process.argv.slice(3));
const dir = path.join(story, 'art', 'traced');
const SIZE = 900, W = 6.4, INNER = 0.68, INK = '#1C1815';
const hash = s => { let h = 2166136261; for (const c of s) { h ^= c.charCodeAt(0); h = Math.imul(h, 16777619); } return h >>> 0; };
for (const f of fs.readdirSync(dir).filter(f => f.endsWith('.json'))) {
  const id = f.replace(/\.json$/, '');
  if (only.size && !only.has(id)) continue;
  const tr = JSON.parse(fs.readFileSync(path.join(dir, f), 'utf8'));
  const sc = SIZE / Math.max(...tr.size), pad = 12;
  const w = Math.ceil(tr.size[0] * sc + 2 * pad), h = Math.ceil(tr.size[1] * sc + 2 * pad);
  const items = Ink.buildDrawing(tr, { x: pad, y: pad, scale: sc }, { w: W, inner: INNER, minLen: 16, seed: (hash(id) % 9973) + 1 });
  const paths = Ink.drawingPaths(items, 1).filter(Boolean).map(d => `<path d="${d}"/>`).join('\n');
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}">\n<!-- Afterclap re-ink of ${tr.src}: traced centrelines, hand stroke model, one colour, transparent background -->\n<g fill="${INK}">\n${paths}\n</g>\n</svg>\n`;
  fs.writeFileSync(path.join(dir, id + '.svg'), svg);
  console.log(`svg ${id}  ${items.length} strokes`);
}
