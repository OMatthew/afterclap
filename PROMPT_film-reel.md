# Film-reel spin-up and wind-down (Matthew's idea, 2026-10-06)

Add this to the template as an option, on by default, and use it for 01-dime. Do it after the current re-render is done.

**The idea:** a projector starting and stopping. At the start, the picture advances in visible steps that speed up: the same frame is held for several beats, then fewer, then the motion is smooth. Once it reaches the full 30 fps, the animation is properly under way. The end is the reverse: the picture winds down into held frames and stops.

**Rules**
- **Start:** keep it short, about 0.5 s. It must finish before the first paint landing (0.68 s in 01-dime). The hook question must not be delayed. Remap the picture's timing only; never touch the narration.
- **End:** the wind-down runs under "That's another story" and lands on a held final frame.
- **Make it read as a projector, not lag:**
  - Add gate weave: a pixel or two of vertical jitter on held frames.
  - Add a gentle exposure flicker that settles as the speed rises.
  - Add a projector-clatter cue to cues.json, with its rate matched to the frame steps.
  - If it could still read as the video buffering on a phone, tone it down.
- **Avoid the stock "old film" filter:** no fake scratches, dust, burns, sepia or vignette.
- **Loop:** Shorts loop, so check that the end flowing back into the start feels intentional.

**Deliver** on the template branch:
- dime-rough.mp4 re-rendered with the effect
- a 4 s clip of each end, so the lead can judge them
