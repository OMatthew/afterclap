# Afterclap

Short, true stories about the unlikely chains of events behind everyday things.

- `CHANNEL_RULES.md`: what the channel is, plus the look, voice, accuracy and packaging rules
- `reference/motion-test/`: the approved paint-and-paper motion prototype
- `stories/<nn-name>/`: one folder per Short:
  - `voice.mp3`, `words.json`, `narration.txt`: the narration and its word timings
  - `shots.json`: the shot list
  - `script.md`: beats and the fact table
  - `art/`: line drawings
  - `out/`: renders

To render a Short: `node engine/render.cjs stories/<nn-name>` (see `NOTES.md`). Needs Python 3 with numpy, scipy, scikit-image and Pillow, Node 18+, ffmpeg, and Playwright Chromium (preinstalled on the build boxes); `npm install` adds the caption font.
