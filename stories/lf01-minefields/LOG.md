# lf01-minefields: log

## Before 2026-11-27
Script draft 4 after panel-v1, panel-v2 and the Fable review (review-script-fable.md); voiced 8:23 (voice.json); storyboard draft 1 (STORYBOARD.md).

## 2026-11-27 (scheduled lead run)
- **Art (gate 5): 28 of 31 usable, 3 to redo.** Prompt: PROMPT_art.md (31 wide 3:2 drawings). ChatGPT made items 1-6 and 8, then went silent on image requests (no error) in two chats; Gemini made 7 and 9-31 (25 in a row) before its daily cap. Originals: ~/Movies/Afterclap/work/lf01-art/; 1024-wide copies in art-src/.
  - The Gemini drawings are thin grey lines on a soft gradient, and the tracer (threshold 150) dropped most of them at 1024 px. prep.py flattens the paper, stretches the ink to black and thickens lines; run it before trace.py for those ids (now applied to ridge-blast, ridge-long, walk-lane, defence-belt, four-things, farm-over-charge, ukraine-map). Bold drawings (drones v2) are traced as they are.
  - drones redrawn bold in ChatGPT (the hanging mine had to be worded as "a disc-shaped payload").
  - Still weak after prep: four-things (tripod with no gun; small objects collapse), defence-belt (the mines and blocks vanish), walk-lane (the walker breaks up). ChatGPT refused all three redraws (weapons/minefield guardrails); the helper did not work around the refusals. Redo in Gemini with "bold thick line, draw it big", or rethink the shots (e.g. beat 7 from separate items; beat 25 on the treaty page and the deminer lane).
  - Faces: only small figures (crater farmer, seismograph man, deminer, ten-figures); no red near any of them.
