# Afterclap template v1: notes

One command turns a story folder into a finished Short:

```
node engine/render.cjs stories/01-dime
```

That traces any new or changed drawings, lays out the strip, renders 1080x1920 at 30 fps in parallel parts, muxes the narration, and writes:

- `out/dime-rough.mp4` (H.264 yuv420p, AAC)
- `out/dime-cover.png` (1080x1920 cover frame)
- `out/cues.json` (foley cue sheet) and `out/landings.json` (paint landings in frame terms)

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
     - `"slide": {"at", "dur", "to": [u, v]}` slides the paint to another spot on the same drawing.
     - `"soak": t` lets the final splat soak into the paper as a stain.
   - `cover.words` (2–4 big words), `cover.art`, `cover.at`. The brand mark is a red-lead dot at a fixed spot (`cover.mark`, default x 104, y 176, r 24).
4. Check stills at any time: `--stills 5.86,12.54` (PNG plus a 1280 px JPG, snapped to real frames).
5. Full render: `node engine/render.cjs stories/02-something`, then `python3 tools/check_paint.py stories/02-something` to confirm each landing hits its word.

Other options: `--par N` parallel parts (default: CPU count), `--from 20 --to 30 --out test-x.mp4` to preview a range, `--cover` only the cover, `--retrace` force the trace step.

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

### Captions

IM Fell English (from @fontsource), ink colour, one short line at a time, 64 px, centred in a column that clears the right-hand buttons, at y ~1400 above the bottom UI. Lines break at punctuation and pauses, long phrases are split into balanced lines that never end on a weak word ("the", "and"), and text comes from `narration.txt` so "Civil War" and "five-cent" keep their form. Fades are 0.12 s; there is a soft paper-coloured halo so ink scrolling behind stays readable. No karaoke, no boxes.

### Foley hook

`out/cues.json` lists every paint and paper event (`drop`, `splat` with size, `gather`, `lift`, `drain`, `slide`, `soak`, `scroll` with duration, `pen` with duration). Drop WAVs named after the cue types into `stories/<story>/sfx/` or `./sfx/` and the mux step places each one at its cue. No folder, no foley (this pass has none).

## Honest assessment

RENDER_ASSESSMENT

## Render time

RENDER_TIME

## Next steps

NEXT_STEPS
