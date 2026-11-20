# Engine review: `origin/engine/landscape` (59ed976)

Reviewer: Fable, 2026-11-20. Scope: `engine/`, `tools/`, `package.json` only, against merge base fd89c03.
Changed files: `engine/frames.cjs`, `layout.cjs`, `page.html`, `plan.cjs`, `render.cjs`, new `sidecars.cjs`. No `tools/` or `package.json` changes.

The branch's commit message says "untested in a browser". Everything below marked "ran" was run here in Chromium (2 vCPU container, ffmpeg 6.1.1), in throwaway detached worktrees that have since been removed. Nothing was committed, pushed or merged.

## Summary

The landscape mode works and the parallel path is deterministic. Portrait stills and covers are byte-identical to main. Two things need fixing before merge: the lossless intermediates need about 78 GB of scratch disk for lf01 (and about 11 GB for every ordinary Short), and a `--from/--to` preview overwrites the story's full-length SRT and chapters files.

## What was checked

### Merge into main
- `git merge-tree --write-tree origin/main origin/engine/landscape` is clean (tree 933a37a). Main has not touched `engine/`, `tools/` or `package.json` since the merge base.
- The branch does not contain `stories/lf01-minefields` (it is only on main) and adds `stories/lf-demo`; no overlap.

### Portrait unchanged (ran)
- Stories 18 and 10, stills at 0.5, 1.5, 5, 20, 40, 66 s (18) and 0.6, 12, 60 s (10), plus both covers: every PNG has the same SHA-256 on main and on the branch. `cues.json` and `landings.json` are unchanged (git shows no diff).
- Portrait video is not byte-identical, by design: parts are now PNG to FFV1 with one final x264 encode, where main piped JPEG q95 into x264 per part. Story 18, 5-6 s, main vs branch: PSNR 43.6 dB average (Y 42.0, U 51.9, V 52.9), so same picture, no colour shift.
- New side effect for Shorts: every run (including `--stills`) now writes `out/<name>.srt`, an untracked file in each story's `out/`.

### Parallel path deterministic (ran)
- Story 18 (portrait), 0-8 s, `--workers 1`, `2`, `3`: all 240 lossless frame hashes equal, and `parts/video.mp4` has the same SHA-256 in all three runs.
- lf-demo (landscape), 3-9 s across a camera move, `--workers 1` vs `3`: all 180 frame hashes equal, same `video.mp4` SHA-256.
- By reading: each worker has its own browser and its own part file, indexed by worker number; the concat list is built in worker order; frames are written with an awaited write callback, so there is no reordering or shared file. A failed worker sets a flag that stops the others, and the ffmpeg child and browser are closed in `finally`.

### Landscape render (ran, on `stories/lf-demo`; lf01 has no shots.json or layout yet)
- Stills are 1920x1080 PNG with 1280x720 JPG; cover is 1280x720. Looked at stills at 0.5, 5, 9, 15, 21, 23.3 s and the cover: paper fills the frame, ink, paint, intro title and captions all draw correctly.
- Full render with `nice -n 10 ... --workers 3`: 705 frames, master 23.5 s H.264 yuv420p 1920x1080 with AAC, cover, SRT and chapters all written. 293 ms/frame on 2 vCPU.

## Required fixes

1. **Intermediate disk use (`engine/frames.cjs`, `video()`).** FFV1 parts measured 2.5-2.6 MB per frame at both 1080x1920 and 1920x1080, and `joined.mkv` is a second full copy. lf01's narration ends at 503.2 s, about 15,100 frames: roughly 39 GB of parts plus 39 GB joined, about 78 GB peak. This container has about 19 GB free, so the lf01 render would die with a full disk here; on the Mac it depends on free space. It also hits Shorts: a 75 s Short now needs about 11.6 GB of scratch where main needed tens of MB. Fix both halves:
   - Drop `joined.mkv`: feed the concat list straight into the final x264 encode.
   - Use a lossless inter-frame codec for parts: `-c:v libx264rgb -qp 0 -preset ultrafast`. Measured on the lf-demo range: 0.26 MB per frame against 2.53 MB for FFV1, and the decoded frames are bit-identical to the FFV1 ones (same MD5). That brings lf01 to about 4 GB.

2. **A `--from/--to` preview overwrites the full sidecars (`engine/render.cjs` + `engine/sidecars.cjs`).** `writeSidecars` runs on every invocation and writes `out/<name>.srt` and `out/<name>-chapters.txt` rebased to the preview range. After the lf-demo `--from 3 --to 9` run, the SRT started at "straight into a giant balloon cat" at 00:00:00 and chapters had one line. The real master is protected from range renders ("a --from/--to preview never overwrites the real master"); the upload SRT and chapters need the same protection. Either skip the sidecars when `--from` or `--to` is set, or write range ones under `parts/`.

## Recommended, not blocking

3. **Default worker count dropped from CPU count to 1, and `--par` above 3 now throws.** LEAD.md's Short procedure is plain `node engine/render.cjs stories/<id>`, so Shorts render on one worker with PNG capture: 403 ms/frame here against 208 ms/frame for main on the same range. `engine/thread.cjs` shares `makeRenderer`, so thread renders also default to one worker and `--par 8` fails. Update LEAD.md to pass `--workers` for Shorts too, and fix the stale `--par` text in NOTES.md (lines 47, 119) and the `thread.cjs` header.
4. **Review copy for a long video.** The 19 MB cap gives lf01 about 130 kbps at 1080p. Render lf01 with `--no-review`, or `--review-height 720 --max-mb N`.
5. **`clips()` runs on landscape renders** and writes the Shorts loop-seam and reel-end clips under `out/reel-clips/`. Harmless but meaningless for long-form; skip when `style.frame` is landscape or the reel is off.
6. **Default layout picks portrait patterns for a new landscape story.** `loadLayout` reads the frame from the existing `layout.json` (`cur?.style?.frame`). If lf01's first render happens before `layout.json` carries `style.frame: "landscape"`, the gaps are filled with 1080x1920 positions and those then persist as hand values. lf01's `layout.py` must write `style.frame` before the first render.
7. **Intro title box in landscape.** `setupFrame` pins the cover words to `left: 120px; right: 1020px` (a 780 px column) for every non-portrait frame, and the intro title shares that element. Long lf01 title lines will wrap inside 780 px. Fine for the demo; check with a still.
8. **`render-log.json` key renamed** from `parts` to `workers`. Nothing in `engine/` or `tools/` reads it.
9. **Colour tags.** The master has no colour matrix tag and is converted with BT.601, as on main. Players assume BT.709 for 1080p. This is unchanged from how Shorts already ship, so the long-form will match them; tag it only if the look is revisited.
10. **Landscape cover is 1280x720** (page scaled by 2/3 before the screenshot). Acceptable for a YouTube thumbnail; 1920x1080 would need no scaling step.
11. **Chapters file.** The first chapter is forced to 0:00, as YouTube requires. YouTube also needs at least three chapters of 10 s or more each; the engine does not check this.

## Checks with no findings
- `plan.cjs`: `snapPaint` still runs before the layout is read; portrait geometry is still `GEOM_SHORT`; an unknown `style.frame` throws. `thread.cjs` passes its own geometry and is unaffected by the new default.
- `render.cjs`: `shots.words` override matches `loadStory`; the `landings.json` camera maths gives identical output for portrait.
- `page.html`: the `setupFrame` additions sit after the portrait early return; `thread.cjs` sets `cover: false` and no intro title, so its frames are unaffected.
- Range validation happens before `parts/` is wiped.

VERDICT: FIX

Required fixes:
1. Cut intermediate disk use in `video()`: remove the `joined.mkv` copy and encode parts with lossless `libx264rgb -qp 0 -preset ultrafast` instead of FFV1 (about 78 GB peak for lf01 today, about 4 GB after).
2. Do not overwrite `out/<name>.srt` and `out/<name>-chapters.txt` on `--from/--to` preview renders.
