# 20-first-sleep: log

## 2026-11-25 (scheduled lead run)
- **Research (gate 2): PASS** (research/20-first-sleep.md, verified 2026-11-20). Date: BBC 2022 says 13 April 1699, CNN 2022 says 1697, so the script says "the 1690s" and the description gives both (research note corrected).
- **Script (gate 3): PASS on v6** (= v4 with "the 1690s").
  - v3 (123 words): Fable fact check FIX (pronoun "He found it", "how common it was" heard as the phrase, unhedged "closed the gap"); panel: 4 of 5 exits on "Researchers still argue about how common it was." (END 50/62/62/77/78). Fail.
  - v4 (133 words): fixes taken; added "In that hour, people prayed, talked, or visited the neighbours." (asked for by 4 of 5); debate line moved after the experiment. Panel exits split 2/2/1 (debate, lamps, "in that hour"), END 48/74/78/46/65, median 65: PASS. Fable v4: FIX on the year only.
  - v5 tried folding the debate line in with "But did the habit vanish too?": panel 3 of 5 exits on the debate line, Fable FIX (the question overpromises). Rejected; went back to v4 + "the 1690s" (year verified in Fable v5).
  - Rejected: "And doctors say waking in the night can be normal." (length; Fable called it optional).
- **Voice (gate 4): PASS.** Take a, tempo 1.0: 52.0 s; words.py 0.970 (digit forms only); blips 0. Mac folder short-20-first-sleep.
- **Art (gate 5): PASS.** 9 ChatGPT guides (Sonnet helper, no redos); ending reuses jane-court. fixes.py restores eye dots (blob detector inside face boxes) and drops three bad traces. Helper deleted its own temp script (.save.sh) instead of moving it; minor, noted.
- **Cut (gate 6): SHIP on round 3** (review/fable-cut.md, -v2.md, -v3.md).
  - Round 1 FIX: lamp landing fired before the lamp was drawn (moved to "brighter"); zero-length word stamps for "volunteers"/"Researchers" (caption data corrected, audio untouched). Also taken: capChars 26, mother's faceless head loop removed (read as a pillow and contradicted "they had just woken"), stray chin line and door blob removed, cover "First sleep. / Then what?".
  - Round 2 FIX: lantern exit rode past the neighbour's face (landing moved to the door's lower panel, exit right); scene 9 entry crossed a hand because `enter='up'` is a silent no-op in the engine (`'top'` is the straight-down value).
  - Round 3 SHIP. Left: two-frame crossings of fingers (historian, researcher), noted not fixed.
  - Paint: candle flame in scene 1 (a killing is named; never on a person or the table) and again at the end, dropping straight down between the faces.
- **Publish (gate 7): scheduled** Sat Nov 28, 2026, 11:00 AM CT: https://youtube.com/shorts/7tonTaAymP4 (Sonnet helper; checks no issues; playlist set; related video 23; re-read 11:00 AM GMT-6). After it is public: set 23's related video to 20.
