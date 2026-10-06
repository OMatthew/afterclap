// Film-reel spin-up and wind-down: a projector starting and stopping.
//
// Remaps PICTURE time only (never the narration, never the captions, which stay on the
// voice). Each output frame gets:
//   tau    picture time to render
//   capT   caption time (always real time)
//   weave  vertical gate weave in whole px (held frames only)
//   expo   exposure flicker, -1..1 (small; + brighter, - darker)
//
// Start: the picture advances in held steps that shorten (default 5,4,3,2,1 frames = 0.5 s),
// sampling real time at each step so nothing drifts and the first paint landing stays on its word.
// End: from `endAt` the steps lengthen and the picture slows (each step advances one frame), then
// it stops on a held final frame. Config lives in layout.json → style.reel.
const DEFAULT = { on: true, start: [6, 4, 3, 2, 1, 1], end: [1, 2, 2, 3, 4, 5, 6], endAt: null, weave: 3, flicker: 0.1, pullIn: 360, creep: 600 };

function mulberry32(a) { return function () { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }

function reelMap(plan) {
  const fps = plan.fps, N = plan.frames;
  const cfg = Object.assign({}, DEFAULT, (plan.style && plan.style.reel) || {});
  const map = Array.from({ length: N }, (_, f) => ({ tau: f / fps, capT: f / fps, weave: 0, expo: 0 }));
  const cues = [], notes = [];
  if (cfg.on === false) return { map, cues, cfg, notes };
  const r = mulberry32(1866);
  const jitter = amp => Math.round((r() * 2 - 1) * amp);
  // gate weave: each new frame lands a few px off and settles over its hold, with a little jitter
  let land = 0;
  const weaveAt = (i, s) => { if (i === 0) land = (r() < 0.5 ? -1 : 1) * cfg.weave * s * (0.6 + 0.4 * r()); return Math.round(land * Math.exp(-i * 0.7) + (r() * 2 - 1) * s); };
  // exposure: each new frame arrives with a small shutter pulse that fades within its hold,
  // so the flicker beats at the same rate as the steps (and the clatter); it shrinks as speed rises
  // (mostly a dimming: the lamp is brightest as a new frame arrives, then the picture sags darker
  // until the next pull-down, so the flicker beats at the step rate and the clatter's rate)
  const pulse = (i, s) => -cfg.flicker * s * (0.3 + 0.7 * (1 - Math.exp(-i * 1.0)) + (r() * 2 - 1) * 0.1);

  // ---- spin-up: must finish before the first paint landing
  let holds = cfg.start.slice();
  const firstLand = plan.landings.length ? plan.landings[0].t : 9;
  const limit = Math.floor((firstLand - 0.1) * fps);
  while (holds.reduce((a, b) => a + b, 0) > limit && holds.length) {
    const i = holds.indexOf(Math.max(...holds)); if (holds[i] > 1) holds[i]--; else holds.pop();
  }
  let f = 0;
  holds.forEach((h, k) => {
    const tau = f / fps, s = h / holds[0];             // s: how slow this step is, 1 = slowest
    cues.push({ t: +tau.toFixed(3), type: 'clatter', rate: +(fps / h).toFixed(2), gain: +(0.35 + 0.35 * s).toFixed(2), phase: 'start' });
    for (let i = 0; i < h && f < N; i++, f++) {
      map[f].tau = tau; map[f].held = true;
      map[f].weave = weaveAt(i, s);
      map[f].expo = pulse(i, s);
    }
  });
  notes.push(`spin-up ${holds.join(',')} frames (${(f / fps).toFixed(2)} s), first landing at ${firstLand.toFixed(2)} s`);

  // ---- wind-down: under the last caption line, ends on a held frame
  const lastCap = plan.captions[plan.captions.length - 1];
  let endAt = cfg.endAt != null ? cfg.endAt : lastCap ? lastCap.t0 : plan.duration - 1.2;
  const eh = cfg.end.slice();
  const need = eh.reduce((a, b) => a + b, 0) + 8; // steps + at least 8 held frames
  endAt = Math.min(endAt, (N - need) / fps);
  let fe = Math.round(endAt * fps);
  const tau0 = fe / fps, hmax = Math.max(...eh);
  eh.forEach((h, k) => {
    const tau = tau0 + k / fps, s = h / hmax;          // the film slows: one frame per step
    cues.push({ t: +(fe / fps).toFixed(3), type: 'clatter', rate: +(fps / h).toFixed(2), gain: +(0.35 + 0.35 * s).toFixed(2), phase: 'end' });
    for (let i = 0; i < h && fe < N; i++, fe++) {
      map[fe].tau = tau; map[fe].held = true;
      map[fe].weave = weaveAt(i, s);
      map[fe].expo = pulse(i, s);
    }
  });
  const tauEnd = tau0 + (eh.length - 1) / fps;
  cues.push({ t: +(fe / fps).toFixed(3), type: 'reel-stop' });
  // final held frame: the gate settles, the lamp steadies
  for (let i = 0; fe < N; i++, fe++) {
    map[fe].tau = tauEnd; map[fe].held = true;
    map[fe].weave = i < 3 ? jitter(cfg.weave * (1 - i / 3) * 0.6) : 0;
    map[fe].expo = i < 4 ? cfg.flicker * (1 - i / 4) * (r() * 2 - 1) * 0.5 : 0;
  }
  notes.push(`wind-down from ${tau0.toFixed(2)} s, steps ${eh.join(',')}, held final frame at picture time ${tauEnd.toFixed(2)} s`);
  // the paper strip is the film: at the start it is pulled up into the gate (settled before the first
  // landing); at the end it creeps on, so the slowing steps are visible on the strip itself
  const drift = {
    start: { t0: 0, t1: f / fps, d: cfg.pullIn },
    end: { t0: tau0 - 0.3, v: cfg.creep },
  };
  return { map, cues, cfg, notes, drift };
}

module.exports = { reelMap, DEFAULT };
