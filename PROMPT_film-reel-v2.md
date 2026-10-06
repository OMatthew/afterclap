# Film reel, pass 2: make it visible (lead review, 2026-10-06)

Matthew couldn't see the reel effect. The lead checked the clips. The start holds frames on a nearly still, half-drawn picture for 0.5 s, so the holds just look like the drawing paused. The effect needs a visible film cue. Keep the narration and caption timing exactly as they are.

**What Matthew pictures:** a projector starting up. You see individual film frames, nearly identical, go by slowly. They speed up until the film locks in and the animation runs at normal speed. At the end, the reverse.

**Start (≤ 0.6 s, finished before the first paint landing at 0.68 s)**
- **Roll into register.** On the first stepped frames, offset the whole picture vertically, as if the film isn't yet seated in the gate. A thin dark frame line and the top or bottom of the neighboring (identical) frame should show. Shrink the offset step by step (for example 40% → 22% → 10% → 4% → 0 of the frame height) while the holds shorten (for example 5, 4, 3, 2, 1 frames).
- **Flicker.** Add a brightness flicker on each step that fades out as it locks.
- **Captions** stay steady, outside the film.

**End (may run past the narration; extend the video by up to 1.5 s)**
- **Wind down.** Under "That's another story" the cadence slows, the flicker comes back, and the picture starts slipping out of register: the frame line creeps in.
- **Film runs out.** After the last word, the last frame slides up out of the gate, leaving a beat of bright, blank paper.
- **Loop.** Shorts loop, so the blank paper should hand off to the start's roll-in cleanly.

**Sound (new: `sfx/` on main, generated with ElevenLabs sound effects)**
- `projector-start-a.mp3` / `projector-start-b.mp3` (2.0 s) and `projector-end-a.mp3` / `projector-end-b.mp3` (3.5 s). Matthew is picking one of each; until he does, use the `-a` files.
- Trim them to fit, and align the clacks with the visual steps where you can.
- Mix the start under the first words at about −24 dB relative to the voice, ducked so the question stays clear. The end can sit a little louder once the voice has finished.
- Mix the narration exactly as now.

**Deliver** on template-v1:
- the 4 s start, end and loop-seam clips again, with sound
- the full dime-rough.mp4
- 6 stills of the start roll-in, one per step, so the lead can check that the frame line reads
