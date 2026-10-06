# Afterclap template v1: notes

One command turns a story folder into a finished Short:

```
node engine/render.cjs stories/01-dime
```

That traces any new or changed drawings, lays out the strip, renders 1080x1920 at 30 fps in parallel parts, muxes the narration, and writes:

- `out/dime-rough.mp4` (H.264 yuv420p, AAC)
- `out/dime-cover.png` (1080x1920 cover frame)
- `out/dime-master.mp4` (full quality, not committed) and `out/dime-rough.mp4` (the same picture squeezed under 19 MB for the repo)
- `out/cues.json` (foley cue sheet) and `out/landings.json` (paint landings in frame terms)

Run-out and brand stills are in `stories/01-dime/out/runout-stills/` and `stories/01-dime/out/brand-stills/`. Stills for review are in `stories/01-dime/out/v1-stills/` (two paint landings, a third landing with the footprint trail, the drain, a scene change mid-scroll, the paint on the goblin's name). The re-inked SVGs for all 18 drawings are in `stories/01-dime/art/traced/`, and `reference/look-check/reink-side-by-side.jpg` compares originals with the re-ink.

## Making a new Short

1. Make the folder:

```
stories/02-something/
  voice.mp3        narration (never re-timed here)
  words.json       [{ "w": "Why", "s": 0.0, "e": 0.22 }, ...]
  narration.txt    the script; captions take their casing and punctuation from it
  shots.json       scenes: time range, art ids, paint landings keyed to a word (see 01-dime)
  art/<id>.png     one line drawing per art id (image-model output is fine)
```

2. Rough pass: `node engine/render.cjs stories/02-something --scene-stills`
   - Traces every PNG into `art/traced/<id>.json` (strokes) and `art/traced/<id>.svg` (the re-inked drawing).
   - Writes `layout.json` with default positions (1, 2, 3 or 4 drawings per scene each have a pattern) and puts every paint landing at the middle of its drawing.
   - Renders one still per scene into `out/stills/`.
3. Edit `layout.json` while looking at the stills (the art grid trick: crop the PNG and read off fractions):
   - `art[].x, y, w`: centre and width in scene px (each scene is a 1080x1920 stop on the strip). Keep art inside x 70–1010, y 200–1300; captions sit at y ~1400 and the Shorts UI covers the bottom and right edge.
   - `paint[].at`: where on the drawing the paint lands, as fractions of the drawing's box. `R`: splat radius in px.
   - Special paint moves, all optional:
     - `"fill": {"cx", "cy", "r", "drain": [t0, t1], "dripX"}` floods a circle and drains out through a drip (dime scene).
     - `"fill": {"poly": [[u, v], ...], "drain": [t0, t1], "dripX"}` floods any outline instead (the inside of a chest, an ellipse given as points; 02-ridges).
     - `"slide": {"at", "dur", "to": [u, v], "hold"}` slides the paint to another spot on the same drawing; `hold` (default 0.95 s) is how long it rests before it can leave.
     - `"soak": t` lets the final splat soak into the paper as a stain.
   - `cover.words` (2–4 big words), `cover.art`, `cover.at`. The brand mark is a red-lead dot at a fixed spot (`cover.mark`, default x 104, y 176, r 24).
4. Check stills at any time: `--stills 5.86,12.54` (PNG plus a 1280 px JPG, snapped to real frames).
5. Full render: `node engine/render.cjs stories/02-something`, then `python3 tools/check_paint.py stories/02-something` to confirm each landing hits its word.

Other options: `--par N` parallel parts (default: CPU count), `--from 20 --to 30 --out test-x.mp4` to preview a range, `--cover` only the cover, `--retrace` force the trace step.

**The 02-ridges way (recommended):** word timings come from `python3 tools/words.py <story>` (faster-whisper small.en, lined up with narration.txt; it reports anything it misheard or skipped). The story's own `shots.py` and `layout.py` write shots.json and layout.json, with every time looked up from words.json by word (never typed by hand) and every paint target picked in source-PNG pixels. When the tracer drops fine repeated lines that matter (coin ridges, window bricks), list them in `art/fixes.json` and `tools/artfix.py` redraws them on every trace. A drawing that stands in front of another (the tax man before the house) gets `{"knockout": {}}` there: paper fills its outline so the lines behind it don't show through.

Re-run the trace by hand with `python3 tools/trace.py <story> [ids]` and `node engine/inksvg.cjs <story> [ids]`. `node tools/lookcheck.cjs <story> <out.png> id1 id2 id3` makes an original-vs-re-inked comparison.

## What's in it

| File | What it does |
|---|---|
| `tools/trace.py` | PNG → centreline strokes. Thresholds out the image-model haze, removes specks, skeletonises, builds a stroke graph, prunes whiskers, joins strokes that carry straight through junctions and across small breaks, drops hatching/texture (short strokes in crowded ink), double lines (rims, nested frames), rows of small loops (chain links, window rows), irons zigzags (chains) flat, keeps small round solid dots (eyes) as fills, and marks silhouette vs interior strokes. |
| `engine/ink.js` | The hand-ink stroke model, shared by the renderer and the SVG export. Every stroke is redrawn as a filled outline with low-frequency wobble, gentle pressure and weight changes, ink pooling where the pen lands and stops, small overshoots or gaps at the ends, loops that close a little past or short of their start. Silhouette lines are full weight (6.4 px), interior lines 0.68 of that, so every drawing reads as one hand whatever the source line weight. Draw-on runs several pens at once with a wet head; a very small line boil (0.35 px, 4 times a second) keeps held frames alive. |
| `engine/paper.js` | The motion test's paper (warm off-white #F2ECDF, grain, mottling, fibres) and a lighter dry-ink texture filter. |
| `engine/paint.js` | The motion test's splat-and-drop model, generalised: splats sized by `R`, gather and anticipation, drops with velocity stretch and a teardrop tail, residue specks. |
| `engine/plan.cjs` | Turns shots + words + layout into a timeline: one scroll per scene change, draw-on times, paint landings and the travel between them, captions, foley cues, cover. |
| `engine/page.html` | The renderer page (SVG + filters). `renderAt(t)` is a pure function of time, so any frame can be rendered alone and the output is deterministic. |
| `engine/render.cjs` | CLI: trace step, Playwright Chromium frame by frame in parallel parts piped to ffmpeg, concat, mux, cover. |
| `engine/layout.cjs` | Default layouts and merging with hand edits (hand edits always win). |
| `tools/check_paint.py` | Measures the actual impact frame of every landing in the rendered mp4. |

### How the paint carries the chain

- The first drop falls in from the top and lands on the first keyed word.
- Inside a scene it **hops**: gathers back into a bead, squashes, lifts and arcs to the next thing.
- Between scenes the strip scrolls down (eased, with vertical motion blur, as in the motion test). If the next landing comes soon after the scroll, the drop **rides** the scroll: it lifts as the strip starts moving, peaks and falls into the new scene. If the next landing is seconds later, it is **tossed**: it lifts out of the top of the frame as the scroll begins and falls back in from the top on the keyed word, so the scene can play first.
- What the paint leaves behind: a faint soaked footprint on every object it touched (revealed as the paint lifts) and a few far specks. Scrolling back up the strip would show the whole trail.
- Landings hit the first frame at or after the keyed word's start in `words.json`. If a shots.json time doesn't sit on its word, the word wins and the render prints a warning.

### Film reel: projector run-out at the end (on by default)

Pass 3, the lead's call (`PROMPT_film-reel-v3.md`): **the start is plain** (the first half-second belongs to the hook); **the end keeps the effect.** Code: `engine/reel.cjs` (the timeline) and `placeFilm()` in `engine/page.html` (the gate). Picture time and the picture's place in the gate are remapped; the narration and caption timing are untouched.

- **Captions are part of the picture.** They're SVG inside the film, so whenever the film steps, slips or slides they move, flicker and get copied with it. Nothing stays pinned over a moving frame. They look the same as the old overlay captions.
- **End:** under "That's another story" (75.6 s) the cadence slows (holds of 1, 2, 2, 3, 4, 5, 6, 7 frames, one picture frame per step), the flicker comes back and the film slips upward out of register, so the frame line creeps in from below.
- **Run-out:** after the last word (76.6 s) the last frame and two near-copies roll up through the gate. Each copy has a hair of side weave, and the frame lines and motion blur show the speed. The film picks up speed off the hold, then slows as it runs out; its tail edge creeps up and leaves the lit, empty gate (bright blank paper) until 78.03 s, 1.5 s after the last word. `end.runout.copies: 0` (with `dur` ~0.35) gives the single slide-out instead.
- **Sound:** `sfx/projector-end-a.mp3` comes in with the slip, ducked well under the voice, and rises once the voice stops. Its own wind-down starts as the film begins to slow (40% into the run-out), so the clatter dies away with the film, and the blank beat is quiet. Levels come from measured loudness (EBU R128). Switching takes is one line: `style.reel.sound.end` in layout.json. The start sound is used only if `start.on` is true.
- **Brand sting:** once the film's tail has cleared the middle of the gate, the channel avatar's "a" brushes itself on in writing order (bowl, hook, stem, tail; 0.42 s). Then a drop of red lead falls into its bowl and settles under the ink, so the last frame is the avatar. The mark comes from `brand/avatar-yt-800.jpg` via `python3 tools/brand_mark.py --order 0,3,1,2r` → `brand/a-mark.json` (outline, brush spine, paint spot). Settings: `style.reel.brand` (`on`, `x`, `y`, `height`, `reveal`, `fall`, `settle`). It adds about 0.8 s, so the video ends 2.3 s after the last word. There's a `brand-splat` cue but no splat sound yet.
- **Loop:** the avatar frame cuts to the plain start (coins inking, paint landing on "dime"), which reads as the next reel.
- **Settings:** `layout.json → style.reel` (defaults in `engine/reel.cjs`): `start.on` (pass-2 roll-in, off), `end.holds` / `end.roll`, `end.at` (null = the last caption), `end.runout.copies` / `.dur`, `end.maxAfterVoice`, `frameLine`, flicker, weave and sound. `"on": false` turns the whole effect off.
- **Review:** `--brand-stills` writes five moments of the brand beat; `--runout-stills` writes four stills across the run-out (`out/stills/runout_*.jpg`). Each full render writes `out/reel-clips/` (first 4 s, last 4 s and the loop seam, all with sound); `--clips` rebuilds them from the master.
- **No old-film filter:** no scratches, dust, burns, sepia or extra vignette.

### Captions

IM Fell English (from @fontsource), ink colour, one short line at a time, 64 px, centred in a column that clears the right-hand buttons, at y ~1400 above the bottom UI. Lines break at punctuation and pauses, long phrases are split into balanced lines that never end on a weak word ("the", "and"), and text comes from `narration.txt` so "Civil War" and "five-cent" keep their form. Fades are 0.12 s; there is a soft paper-coloured halo so ink scrolling behind stays readable. No karaoke, no boxes.

### Foley hook

`out/cues.json` lists every paint and paper event (`drop`, `splat` with size, `gather`, `lift`, `drain`, `slide`, `soak`, `scroll` with duration, `pen` with duration). Drop WAVs named after the cue types into `stories/<story>/sfx/` or `./sfx/` and the mux step places each one at its cue. No folder, no foley (this pass has none).

## Honest assessment

What works:
- **The paint.** It reads as real wet paint (gloss, rim, mottle, contact shadow from the motion test) and it carries the story on its own. Every landing hits its keyed word: contact is on the frame nearest the word's start (≤ 0.5 frame), and `tools/check_paint.py` measures the spread splash one frame later on all 21 landings (≤ 1.4 frames).
- **The goblin ending** (narration v5) pays off in pictures: the paint gives the goblin a red cap on "Copper goblin", then lands on "name" and runs down onto the nickel he sits on.
- **The dime beat** (scene 7) is the other best moment: the paint floods the dime, drains out on "The size stayed", and the last drip hangs from the coin as the strip carries it away, then falls into the money bags.
- **The trail.** Faint soaked footprints stay on everything the paint touched. In the three-vignette scenes you can see the chain without anyone saying "chain".
- **The re-ink.** Simple subjects (coins, goblin, bags, scales, press, jar, hand and stamp) look hand-inked and of one hand, close to the motion test. Captions are quiet and readable.

What's weak:
- **Busy drawings simplify unevenly.** The miners (lantern lost, figures a bit mushy), the school gate (windows become loose arches), the Capitol (scaffolding gone, some scrappy strokes) and the mine entrance are the weakest. The trace can only simplify what the image model drew; prompting for fewer, bolder lines would help more than further trace tuning.
- **Small trace oddities:** the nickel's shield stripes don't close at the bottom, the dime's torch handle is thin, the goblin's toes merged into plain feet.
- **Scene 6 is slack.** Fourteen seconds in one frame with three small vignettes; the paint hops keep it alive, but it's the place a viewer might swipe.
- **The "toss" between scenes** (paint leaves the top of the frame, falls back in seconds later on the keyed word) is clear in the frames, but it's the least physical move. Worth Matthew's eye at full speed.
- **Scene changes show a moment of bare paper**, because the next drawing only starts inking as it arrives. It's calm, but a slightly earlier draw-on would make the scroll feel more like moving between drawings.
- **The committed mp4 is a review copy** (two-pass ~2.2 Mbps to stay under 19 MB), so paper grain is softer than the real thing. The full-quality master (`out/dime-master.mp4`, ~60 MB) is not committed; rebuild it with the render command.
- **Data fixes (v5 shots.json):** three paint times sit one word early: "School" 52.44 (snapped to 52.66), "name" 69.94, which is "goblin's" (snapped to 70.40), and "ridges" 73.18, which is "have" (snapped to 73.46). The keyed word wins and the render prints a warning for each. If the earlier words were meant, change the words in shots.json.
- **The film reel (pass 3)** is end-only. The run-out through near-copies is busy for about a third of a second at full speed, then slows and settles on blank paper; it reads as film running out, not as a glitch. If it ever feels like too much, `end.runout.copies: 0` brings back the single slide-out.
- No foley yet, and the cover words ("Smaller. Worth more.") are a placeholder that hasn't had a groove check.

## Render time

On this box (2 vCPU, 2 parallel parts), narration v5 (76.8 s): **frames 577 s** for 2,304 frames (251 ms a frame, film-reel on), plus about **3.5 min** to concat, mux and make the review copy. About **13 min** end to end. Parts scale with cores (`--par`), so an 8-core box should be near 3 minutes for frames. Tracing all 18 drawings takes ~40 s; a still takes ~1 s after a ~3 s browser start.

## Next steps

1. Matthew's taste gate on the rough (and on the "toss" move and the footprint trail in particular).
2. Foley: wet splat, lift, a soft paper scroll, a dry pen scratch for draw-ons. The cue sheet and mixer hook are ready; it just needs the WAVs.
3. Art prompts: ask for simpler line drawings with fewer interior details and no textures (and say "no chains, no lettering"). Add a per-drawing `simplify` knob in layout.json for the stubborn ones.
4. Long scenes: allow a scene to take two stops on the strip so the camera glides between its vignettes (scene 6).
5. Start each scene's draw-on a little earlier in the scroll so the incoming drawing is half-inked as it arrives.
6. Cover: two or three word options through the groove check; the drain moment would also make a strong cover.
7. A 0.5–0.8 s held tail after the last line, so the end doesn't feel clipped when the Short loops.
