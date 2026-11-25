# Gate 6, round 2: full-cut review, Short 20 "What was 'first sleep'?"

Reviewer: Fable (fresh, cold). 2026-11-25. Repo at 3e1befa.
Cut: `out/first-sleep-rough.mp4` (52.5 s, 1080x1920, 30 fps, 1575 frames, H.264, AAC). Cover: `out/first-sleep-cover.jpg`.

How I checked: stills every 0.25 s across the whole cut (210 frames, all looked at); every frame in which the paint moves (230 frames, zoomed on the paint), with full-resolution crops of the risky ones; a per-frame scan for red pixels and for an empty caption band; the SRT against `narration.txt`; the cut's audio subtracted from `voice.mp3`; ebur128; the description, cover, title and the round-1 fixes one by one. I did not re-open the web sources.

## Blocking

1. **30.80-30.87 s: the paint crosses the neighbour's face (new, caused by moving the lamp landing).** Leaving the lantern, the drop rides straight up the neighbour's body (frame 924, over his arm and chest) and sits on his face and forehead in frame 925 (30.83), then clears the roof at 30.87. Round 1 had no red on any face; this route is new because the 6 to 7 move is now a `ride` (no time to leave the screen), and the ride goes up through him. Fix in `layout.py` (6): bow the ride away from him (`exit='right'`, so it bulges through the door panel, not `'left'`), or start the lift one or two frames later so the scroll has carried his head out from under the path. Check frames 922-930 after.

2. **42.83-42.93 s: the scene 9 entry is not from above; it still comes in from the right and now runs over the woman researcher's resting hand for three frames** (frames 1285-1287: on her wrist, the back of her hand, her fingers). Round-1 item 9 is not fixed in the render. Cause: `enter='up'` is not an engine value. `engine/page.html` line 305 only knows `enter === 'top'` (straight down); anything else falls to `edge()`, which returns the right edge for every value except `'left'`. The same no-op is on scene 2 (`enter='up'`), where the drop also comes in from the right (harmless there: it is level with the window top, well above the girl). Fix: `enter='top'` on (9). A straight drop at the current x (548) passes about 20 px left of her raised fingers, which is too tight; move the landing about 45 px left on the same sheet of paper (screen x about 500), which leaves about 70 px to his beard and to her fingers, and check frames 1280-1297.

## Should fix

3. **Scene 3: the drop passes over the historian's right thumb and fingers** on the way in (11.60-11.67, frames 348-350) and again on the way out (15.10-15.17, frames 453-455). Same class as item 2, two or three frames each, and the beat has no danger in it. `enter='top'` cannot be used here (his face is above the page). Cheapest: land about 60 px lower on the page so the low side entry comes in under his fist, or leave it; I would not hold the Short for this alone.

4. **Ending (45.86-52.5 s), left without paint on purpose.** It reads as clean and calm, not dead: the picture returns to Jane and the clerk, the candle is out with a curl of smoke where the red flame was in scene 1, the line boil keeps it alive, and four captions change over the 6.6 s. It is the flattest stretch of the film, though, and the paint leaves by scrolling off on the researchers' papers (last red 45.80) rather than fading. The reason given for skipping the candle (every route crossed the clerk's face) is probably the same `enter='up'` no-op as item 2: with `enter='top'` the drop falls straight down the gap between Jane and the clerk, exactly as it does in scene 1 (2.7-3.1 s), and in scene 10 the gap is wider (about 170 px to her face, about 190 px to his). If the lead wants the "paint fading out" ending from CHANNEL_RULES, that is the route: land calm on the wick at "meant" (48.08), fade over the last second. If not, delete the dead `(10, 'meant')` idea from the notes and ship the quiet ending; it passes.

5. **"and the phrase" is on screen 34.06-34.60 (fully visible about 0.4 s).** Readable, just. Merging it with "was forgotten." is 29 characters, over `capChars`; "the two sleeps became one," / "and the phrase was forgotten." would need capChars 29. Optional.

6. **Housekeeping (stale text, not on screen):** `shots.json` scene 2 still describes "a girl sitting up awake ... beside a sleeping woman", and the `layout.py` comment on (2) says "far from the girl and the sleeping woman". The woman is gone. `layout.py` (2) and (9) carry `enter='up'`, which does nothing (item 2).

## Fine

- **Round-1 fixes that did land:** lamp landing on "brighter" (31.60) after the scroll settles; the drop waits above the street from 31.1 and lands on a drawn, still lamp; nothing red touches the caption. "volunteers kept in darkness" comes up at 37.04-37.13 with the word (37.12); "Researchers still debate" at 42.34-42.43 with the word (42.42). "or visited the neighbours." and "Then what was the second?" are one card each (1.5 s). The stray chin line in scene 5 and the black blob on the door in scene 6 are gone. Cover wording is "First sleep. / Then what?". The research note now gives both dates.
- **Scene 2 without the mother:** it works, and better than before. One girl sitting up awake in a wide bed with an empty pillow beside her, looking at a night window with a moon. "They had just woken" over a picture of one person is a small mismatch, but the empty place in the bed reads as the mother's, which suits the line before it. No leftover strokes where the head loop was; the pillow and bedclothes are whole.
- **Captions vs narration:** the 37 SRT cards equal `narration.txt` word for word (curly quotes, "1690s", "doctors' books", "neighbours"). In the 210 stills every card on screen matches its SRT card and its spoken words. The caption band is never empty for more than 5 frames (cross-fades only). All cards fit one line, including the 27-28 character ones.
- **Audio:** identical to `voice.mp3`: zero lag, gain 0.997, correlation 0.99985, residual 30-45 dB under the voice in every second (AAC coding noise). -16.1 LUFS, LRA 2.2 LU, true peak -1.5 dBFS. Digital silence after the voice ends (51.97-52.5). Nothing added, nothing cut.
- **Paint elsewhere:** scene 1's drop falls and lifts straight up the gap between Jane and the clerk (2.7-3.1, 5.0-5.3), never on either face, and sits on the wick as a small calm flame while "killed" is on screen. Window (7.1-7.5, 8.6-8.9), open book (19.6-20.1, 21.0-21.4), second window (25.4-25.8, 26.7-26.9), lantern entry at door-handle height (29.5-29.9), lamp (31.0-31.6, 35.2-35.6), clock (37.7-38.2, 41.6-41.9): all clear of faces and hands.
- **Blood:** nothing red reads as blood. Scene 1 is a flame. The two spattered landings are the doctor's book (with a short run down the page) and the gas lamp; neither beat is about the body. As in round 1, a calm splat on the book would be the strict reading of the rule; not required.
- **Drawings:** hand-inked, wobbly, readable; faces read in scenes 1, 2, 3, 5, 7, 8, 9, 10. Scene 6 is still small, and the lantern is still a plain loop until the paint lands; acceptable. No text on screen except captions and the opening question (0-2.6 s).
- **Cover and title:** neither answers the question; the cover adds the second one. Girl awake, window filled red, brand dot red at top left, no AI mention, nothing about the killing.
- **Description:** unchanged from round 1 (2,993 characters), ten sources, "Made with the help of AI tools." once at the end before the hashtags.
- **Length:** 52.5 s.

## Timing table (for the fixer)

| Time (s) | Frames | What |
|---|---|---|
| 11.60-11.67 | 348-350 | drop over the historian's right hand, in (item 3) |
| 15.10-15.17 | 453-455 | same, out (item 3) |
| 30.80-30.87 | 924-926 | lift from the lantern crosses the neighbour's body and face (item 1) |
| 34.06-34.60 | | "and the phrase" short card (item 5) |
| 42.77-42.93 | 1283-1288 | scene 9 entry from the right, over the woman's hand (item 2) |
| 45.80 | 1374 | last red pixel; none after (item 4) |

VERDICT: FIX
