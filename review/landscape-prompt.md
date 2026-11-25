# Task: a landscape (16:9) mode for the Afterclap engine

You are working in a git worktree of the Afterclap repo (branch engine/landscape). Read CLAUDE.md, CHANNEL_RULES.md and the headers of engine/layout.cjs, engine/plan.cjs, engine/page.html and engine/render.cjs first.

Rules: no pushes, no deploys, no uploads or publishing, no edits outside this worktree. Never edit any story's voice.mp3 or words.json. Commit your work on this branch when done (local commits only).

## Why
Afterclap makes vertical Shorts (1080x1920): one long vertical paper strip that scrolls down from scene to scene, hand-inked drawings, one red-lead paint accent, burned-in captions. We want to try 8-12 minute long-form videos on YouTube in the same look.

## What to build
1. `layout.style.frame: 'landscape'` (default stays `'portrait'`). In landscape the frame is 1920x1080 and the paper strip runs horizontally: scenes sit left to right and the camera eases sideways between them, with the same feel and easing as today's vertical scroll. Scene-local coordinates are 1920x1080 in landscape (art x/y/w, paint, letters, nudge etc. all work the same, just in the wider frame). Paper texture, ink, boil, paint, stains, drips (gravity still points down), cover, intro title, letters and motion beats must all work in landscape.
2. Captions in landscape: an option `style.captions` (default true). When on, captions sit low and centred, sized for 16:9 (smaller than Shorts, one line, about 42 chars). Long-form will probably run with captions off, so also write `out/<name>.srt` from words.json and the same caption grouping, in both modes.
3. Chapters: if a scene in layout.py/shots has `chapter: "Title"`, write `out/<name>-chapters.txt` in YouTube's format (`0:00 Title`, first chapter at 0:00).
4. Long renders: a 10-minute video is ~18,000 frames. Make render.cjs able to split the frame range across N parallel Chromium workers (`--workers N`, default 1) and join the chunks losslessly before the final encode, so the output is identical to a single-worker render. Keep it deterministic. Cap at what a 10-core Mac shared with its owner can take (default suggestion 3; run under `nice`).
5. Cover in landscape is a 1280x720 thumbnail-style frame (same cover options).
6. A small demo: `stories/lf-demo/`, a copy of `stories/18-macys-balloons` laid out in landscape (first ~25 s only is fine: trim shots to the voice's first scenes; don't edit the audio file itself, use a start/end option in render if needed, or add one). Render it and save stills at 3 or 4 points to `stories/lf-demo/review/*.jpg` (1280 px wide).

## Must not change
Portrait output must stay byte-identical: render stills from stories/17-thanksgiving at 3.0, 14.0 and 30.0 s before and after your change and compare (use `--stills`). Put the result of that check in your final report.

## Environment
macOS, node at ~/.local/bin/node, Playwright Chromium in ~/Library/Caches/ms-playwright, ffmpeg available. Run `npm install --silent` if node_modules is missing (then `git checkout package-lock.json` if it changed). Run renders under `nice -n 10`, one at a time apart from the --workers test.

## Report
Write review/landscape-report.md: what you built, the new options with an example, the byte-identical check, render time for the demo with 1 vs 3 workers, and open issues. Keep it short and plain.
