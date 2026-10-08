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
  // pass 3 (lead, 2026-10-06): the start is plain by default; the first half-second belongs to the hook
  start: { on: false, holds: [5, 4, 3, 2, 1], roll: [0.40, 0.22, 0.10, 0.04, 0], flicker: 0.12, weave: 2 },
  end: { at: null, holds: [1, 2, 2, 3, 4, 5, 6, 7], roll: [0, 0, -0.02, -0.04, -0.07, -0.10, -0.14, -0.19],
    // run-out: the last frame and `copies` near-copies roll up through the gate, slowing, then blank paper.
    // copies: 0 gives the single slide-out (runout.dur ~0.35 s)
    runout: { copies: 2, dur: 1.0 }, flicker: 0.12, weave: 2, maxAfterVoice: 1.5 },
  // brand sting on the empty gate: the avatar's "a" brushes on, a drop of red lead falls into its bowl
  // and settles, so the last frame is the channel avatar (Matthew, 2026-10-06)
  brand: { on: true, mark: 'brand/a-mark.json', x: 540, y: 820, height: 520, reveal: 0.42, fall: 0.34, settle: 0.85 },
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
  // the slip waits for the last word to finish (Fable, Short 04: slipping during "That's another story"
  // undercut the sign-off); Shorts 01-03 slipped from the last caption's start
  const e0 = E.at != null ? E.at : E.from === 'lastCap' && lastCap ? lastCap.t0 : lastWordEnd + 0.05;
  const fe0 = Math.round(e0 * fps);
  const holdFrames = E.holds.reduce((a, b) => a + b, 0);
  const runStart = Math.max(fe0 + holdFrames, Math.round((lastWordEnd + 0.08) * fps));
  const RO = typeof E.runout === 'number' ? { copies: 0, dur: E.runout } : E.runout;
  const runFrames = Math.round(RO.dur * fps);
  // the whole run-out and blank beat end within maxAfterVoice of the last word
  let N = Math.max(baseN, Math.round((lastWordEnd + E.maxAfterVoice) * fps), runStart + runFrames + 6);
  const B = cfg.brand, brandOn = !!(B && B.on !== false);
  if (brandOn) N = Math.max(N, runStart + runFrames + Math.round((B.reveal + B.fall + B.settle) * fps) + 2);
  const map = Array.from({ length: N }, (_, f) => frame(f));

  // ---------------- start: roll into register
  const S = cfg.start;
  const holds = S.holds.slice(), rolls = S.roll.slice();
  const firstLand = plan.landings.length ? plan.landings[0].t : 9;
  const limit = Math.floor(Math.min(0.6, firstLand - 0.1) * fps);
  while (holds.reduce((a, b) => a + b, 0) > limit) { const i = holds.indexOf(Math.max(...holds)); if (holds[i] > 1) holds[i]--; else break; }
  let f = 0;
  const startSteps = [];
  if (S.on !== false) holds.forEach((h, k) => {
    const tau = f / fps, s = h / holds[0];
    startSteps.push({ frame: f, hold: h, roll: rolls[k] });
    cues.push({ t: +tau.toFixed(3), type: 'clatter', rate: +(fps / h).toFixed(2), gain: +(0.35 + 0.35 * s).toFixed(2), phase: 'start' });
    for (let i = 0; i < h; i++, f++) {
      Object.assign(map[f], { tau, held: true, roll: Math.round(rolls[k] * H), weave: rolls[k] > 0 ? jit(S.weave * s) : 0, expo: pulse(i, s, S.flicker) });
    }
  });
  notes.push(S.on === false ? 'start: plain (reel start off)' : `start: holds ${holds.join(',')} (${(f / fps).toFixed(2)} s), roll ${rolls.map(x => Math.round(x * 100) + '%').join(' → ')}; first landing ${firstLand.toFixed(2)} s`);

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
  // run-out: the last frame (and its near-copies, if any) roll up through the gate and out,
  // picking up speed off the hold and then slowing as the film runs out; after the last copy
  // there is only the lit, empty gate
  cues.push({ t: +(fe / fps).toFixed(3), type: 'reel-runout', copies: RO.copies });
  let brandF = null;
  const L = cfg.frameLine, P = H + L, out = -(RO.copies * P + H + L + 30);
  const prof = []; let acc = 0;
  for (let i = 0; i < runFrames; i++) { const u = (i + 0.5) / runFrames; const v = Math.min(1, u / 0.14) * (Math.pow(1 - u, 1.25) + 0.12); prof.push(acc += v); }
  let prevY = lastRoll;
  for (let i = 0; i < runFrames && fe < N; i++, fe++) {
    const y = Math.round(lastRoll + (out - lastRoll) * prof[i] / acc);
    Object.assign(map[fe], { tau: lastTau, held: true, runout: true, copies: RO.copies, roll: y, vel: y - prevY, weave: 0,
      expo: -E.flicker * (0.35 + 0.35 * r()) });
    // the brand mark starts as soon as the film's tail has cleared the space it sits in
    if (brandOn && brandF == null && y + RO.copies * P + H < B.y - B.height / 2 - 30) brandF = fe;
    prevY = y;
  }
  const runEndF = fe;
  let brand = null;
  if (brandOn) {
    if (brandF == null) brandF = runEndF;
    const dropF = brandF + Math.round(B.reveal * 0.7 * fps), impactF = dropF + Math.round(B.fall * fps);
    const endF = impactF + Math.round(B.settle * fps);
    N = endF;
    map.length = Math.min(map.length, N);
    while (map.length < N) map.push(frame(map.length));
    brand = { x: B.x, y: B.y, height: B.height, start: brandF / fps, revealEnd: (brandF + B.reveal * fps) / fps, dropStart: dropF / fps, impact: impactF / fps, mark: B.mark };
    for (let f2 = brandF; f2 < N; f2++) Object.assign(map[f2], { brand: true, bt: f2 / fps });
    cues.push({ t: +(impactF / fps).toFixed(3), type: 'brand-splat' });
  } else map.length = N;
  // the empty gate: bright blank paper, the lamp steadying
  for (let i = 0; fe < N; i++, fe++) Object.assign(map[fe], { tau: lastTau, blank: true, roll: 0, expo: i < 6 ? E.flicker * 0.4 * (1 - i / 6) * (r() * 2 - 1) : 0 });
  if (brand) notes.push(`brand: "a" from ${brand.start.toFixed(2)} s, paint lands ${brand.impact.toFixed(2)} s, holds to ${(N / fps).toFixed(2)} s`);
  notes.push(`end: slips from ${(fe0 / fps).toFixed(2)} s (holds ${eh.join(',')}), runs out at ${(runStart / fps).toFixed(2)} s through ${RO.copies + 1} frame(s) in ${RO.dur} s, blank paper to ${(N / fps).toFixed(2)} s (${(N / fps - lastWordEnd).toFixed(2)} s after the last word)`);

  // the end clatter's own wind-down starts as the film begins to slow
  return { cfg, frames: N, map, cues, notes, startSteps, startOn: S.on !== false, runStart, runEnd: runEndF, brand, tailAt: runStart + Math.round(runFrames * 0.4), e0: fe0 / fps };
}

module.exports = { reelMap, DEFAULT };
