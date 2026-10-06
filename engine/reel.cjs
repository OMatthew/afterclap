// Film reel, pass 2: a projector starting up and running out.
//
// Remaps PICTURE time and the picture's place in the projector gate; never the narration and
// never the captions (they stay on the voice's clock, steady, outside the film).
//
// Per output frame:
//   tau     picture time to render
//   capT    caption time (real time)
//   roll    px the film sits out of register: > 0 = picture low, the neighbouring (identical)
//           frame shows above with a dark frame line between; < 0 = picture high, neighbour below
//   runout  true while the last frame slides out: nothing follows it but blank, lit gate
//   blank   true when the gate is empty (bright blank paper)
//   weave   gate weave in px; expo exposure flicker (-1..1); held = a film frame held on screen
//
// Start (<= 0.6 s, done before the first paint landing): holds 5,4,3,2,1 frames while the roll
// shrinks 40% -> 22% -> 10% -> 4% -> 0 of the frame height, flickering, then it locks.
// End: under the last line the cadence slows and the film slips out of register (the frame
// line creeps in from below); after the last word the last frame slides up out of the gate and
// leaves a beat of bright blank paper, which hands off to the start when Shorts loops.
const DEFAULT = {
  on: true,
  frameLine: 18,
  start: { holds: [5, 4, 3, 2, 1], roll: [0.40, 0.22, 0.10, 0.04, 0], flicker: 0.12, weave: 2 },
  end: { at: null, holds: [1, 2, 2, 3, 4, 5, 6, 7], roll: [0, 0, -0.02, -0.04, -0.07, -0.10, -0.14, -0.19],
    runout: 0.35, blank: 0.55, flicker: 0.12, weave: 2, maxExtend: 1.5 },
  sound: { start: 'sfx/projector-start-a.mp3', startDb: -24, startTrim: [0.055, 1.0], startFadeOut: 0.45,
    end: 'sfx/projector-end-a.mp3', endDb: -6, endDuckDb: 8, endTail: 2.82, endFadeIn: 0.15 },
};

function mulberry32(a) { return function () { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
const merge = (a, b) => { const o = Object.assign({}, a); for (const k in (b || {})) o[k] = (b[k] && typeof b[k] === 'object' && !Array.isArray(b[k]) && a[k]) ? merge(a[k], b[k]) : b[k]; return o; };

function reelMap(plan, words) {
  const fps = plan.fps, H = plan.H || 1920;
  const cfg = merge(DEFAULT, (plan.style && plan.style.reel) || {});
  const baseN = plan.frames;
  const frame = f => ({ tau: f / fps, capT: f / fps, roll: 0, weave: 0, expo: 0 });
  if (cfg.on === false) return { cfg, frames: baseN, map: Array.from({ length: baseN }, (_, f) => frame(f)), cues: [], notes: [] };
  const r = mulberry32(1866);
  const cues = [], notes = [];
  // a new film frame lands bright and the picture sags darker until the next pull-down,
  // so the flicker beats with the steps; s scales it (1 = slowest step)
  const pulse = (i, s, amp) => -amp * s * (0.25 + 0.75 * (1 - Math.exp(-i * 1.0)) + (r() * 2 - 1) * 0.1);
  const jit = amp => Math.round((r() * 2 - 1) * amp);

  // ---------------- end timing first: it decides how long the video is
  const lastCap = plan.captions[plan.captions.length - 1];
  const lastWordEnd = words && words.length ? words[words.length - 1].e : plan.duration - 0.3;
  const E = cfg.end;
  const e0 = E.at != null ? E.at : (lastCap ? lastCap.t0 : plan.duration - 1.2);
  const fe0 = Math.round(e0 * fps);
  const holdFrames = E.holds.reduce((a, b) => a + b, 0);
  const runStart = Math.max(fe0 + holdFrames, Math.round((lastWordEnd + 0.08) * fps));
  const runFrames = Math.round(E.runout * fps), blankFrames = Math.round(E.blank * fps);
  let N = Math.max(baseN, runStart + runFrames + blankFrames);
  N = Math.min(N, baseN + Math.round(E.maxExtend * fps));
  const map = Array.from({ length: N }, (_, f) => frame(f));

  // ---------------- start: roll into register
  const S = cfg.start;
  const holds = S.holds.slice(), rolls = S.roll.slice();
  const firstLand = plan.landings.length ? plan.landings[0].t : 9;
  const limit = Math.floor(Math.min(0.6, firstLand - 0.1) * fps);
  while (holds.reduce((a, b) => a + b, 0) > limit) { const i = holds.indexOf(Math.max(...holds)); if (holds[i] > 1) holds[i]--; else break; }
  let f = 0;
  const startSteps = [];
  holds.forEach((h, k) => {
    const tau = f / fps, s = h / holds[0];
    startSteps.push({ frame: f, hold: h, roll: rolls[k] });
    cues.push({ t: +tau.toFixed(3), type: 'clatter', rate: +(fps / h).toFixed(2), gain: +(0.35 + 0.35 * s).toFixed(2), phase: 'start' });
    for (let i = 0; i < h; i++, f++) {
      Object.assign(map[f], { tau, held: true, roll: Math.round(rolls[k] * H), weave: rolls[k] > 0 ? jit(S.weave * s) : 0, expo: pulse(i, s, S.flicker) });
    }
  });
  notes.push(`start: holds ${holds.join(',')} (${(f / fps).toFixed(2)} s), roll ${rolls.map(x => Math.round(x * 100) + '%').join(' → ')}; first landing ${firstLand.toFixed(2)} s`);

  // ---------------- end: wind down and slip, run out, blank gate
  let fe = fe0;
  const eh = E.holds, hmax = Math.max(...eh);
  eh.forEach((h, k) => {
    const tau = fe0 / fps + k / fps, s = h / hmax;   // the film slows: one frame per step
    cues.push({ t: +(fe / fps).toFixed(3), type: 'clatter', rate: +(fps / h).toFixed(2), gain: +(0.35 + 0.35 * s).toFixed(2), phase: 'end' });
    for (let i = 0; i < h && fe < N; i++, fe++) {
      Object.assign(map[fe], { tau, held: true, roll: Math.round(E.roll[k] * H), weave: jit(E.weave * s), expo: pulse(i, s, E.flicker) });
    }
  });
  // keep holding the last slipped frame until the run-out begins (if the last word runs long)
  const lastTau = fe0 / fps + (eh.length - 1) / fps, lastRoll = Math.round(E.roll[E.roll.length - 1] * H);
  for (; fe < runStart && fe < N; fe++) Object.assign(map[fe], { tau: lastTau, held: true, roll: lastRoll, weave: jit(E.weave), expo: pulse(6, 1, E.flicker) });
  // run-out: the last frame slides up and out of the gate, accelerating
  cues.push({ t: +(fe / fps).toFixed(3), type: 'reel-runout' });
  const out = -(H + cfg.frameLine + 40);
  for (let i = 0; i < runFrames && fe < N; i++, fe++) {
    const u = (i + 1) / runFrames;
    Object.assign(map[fe], { tau: lastTau, held: true, runout: true, roll: Math.round(lastRoll + (out - lastRoll) * u * u), weave: 0, expo: E.flicker * 0.5 * u });
  }
  // the empty gate: bright blank paper, the lamp steadying
  for (let i = 0; fe < N; i++, fe++) Object.assign(map[fe], { tau: lastTau, blank: true, roll: 0, expo: i < 6 ? E.flicker * 0.4 * (1 - i / 6) * (r() * 2 - 1) : 0 });
  notes.push(`end: slips from ${(fe0 / fps).toFixed(2)} s (holds ${eh.join(',')}), runs out at ${(runStart / fps).toFixed(2)} s, blank paper to ${(N / fps).toFixed(2)} s (+${((N - baseN) / fps).toFixed(2)} s)`);

  return { cfg, frames: N, map, cues, notes, startSteps, runStart, runEnd: runStart + runFrames, e0: fe0 / fps };
}

module.exports = { reelMap, DEFAULT };
