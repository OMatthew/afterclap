# Gate 6, round 3: full-cut review, Short 20 "What was 'first sleep'?"

Reviewer: Fable (fresh, cold). 2026-11-25. Repo at 5ddb41d.
Cut: `out/first-sleep-rough.mp4` (52.5 s, 1080x1920, 30 fps, 1575 frames, H.264, AAC). Cover: `out/first-sleep-cover.jpg`.

How I checked: the caption band every 0.25 s across the whole cut (210 strips, all read against the SRT and `narration.txt`); full stills every 0.5 s (105, all looked at); a per-frame red-pixel scan of all 1575 frames to find every frame in which the paint moves, then every one of those frames for scenes 1, 3, 6, 9 and 10 (the ones with people near the path) and every second or third frame for scenes 2, 4, 5, 7 and 8, with full-resolution crops of the close calls; the cut's audio subtracted from `voice.mp3`; cover, title, description. I did not re-open the web sources.

## Blocking

None.

## Should fix

1. **45.40-45.43 s (frames 1362-1363): leaving the papers, the drop passes over the woman researcher's resting fingers** (her left hand on the table), then over the books and out to the right. Two frames, during the scroll blur, in a beat with no danger in it, about 300 px below her face; I could only find it by stepping. Same class as item 2; not worth holding the Short. If touched: `exit='left'` is worse (his pointing hand), so lift later (after the scroll has carried her hand up) or exit lower.
2. **Scene 3, unchanged from round 2: the drop crosses the historian's right fingers** on the way in (11.63-11.67, frames 349-350) and out (15.13-15.17, frames 454-455). Two frames each. Round 2 said not to hold the Short for it; I agree.
3. **Scene 6 landing (29.93-30.77) sits at the very edge of the frame**: centre x 1033 of 1080, y 974, at the foot of the open door. It reads (a red dot on the neighbour's door) but it is small, in the corner, and on a phone it is under the Shorts button column. The route is clean, which was the point of the move; a landing 60-80 px further left on the same door panel would keep the route and be seen.
4. **Housekeeping (not on screen):** `shots.json` still says scene 1 paint "on the paper" (it is the candle flame), scene 2 art "beside a sleeping woman" (she is gone), scene 6 paint "on the lantern" (it is the door). `layout.py` (6) carries two comments, the second stale ("the neighbour's lantern, held low").

## Fine

- **Round-2 blockers, both fixed.**
  - Scene 6 exit (30.77-31.03, frames 923-931): the drop leaves the door corner and rides up the right edge of the frame, half off-screen, about 150 px right of the neighbour's face at its closest, then arcs over the roof to the lamp. No red on him in any frame. Entry (29.60-29.93) slides down the outside edge of the door; also clear.
  - Scene 9 entry (42.93-43.23, frames 1288-1297): now a straight drop from the top, between the two researchers; about 85 px right of his beard and about 70 px left of her raised fingers at the closest frames (1294-1295). Nothing touched.
- **Scene 10 (new):** the drop falls straight down the gap between Jane and the clerk (47.80-48.07, frames 1434-1442), never nearer than about 150 px to either face, and lands as a small calm flame on the wick at "meant". It holds to 52.0 and fades in place by 52.27; the last six frames match the unlit candle of the opening. This is the ending round 1 and 2 asked for, and the final 6.6 s no longer feels flat.
- **Scene 1:** drop and lift both run straight up the gap (2.73-3.13, 4.97-5.30); no red on Jane, the clerk, the table or the page while "her mother was killed." is on screen. The blob is a flame on a candle. Not blood.
- **Blood generally:** nothing red reads as blood anywhere. The only spattered landings are the doctor's book (20.07, short run down the page) and the gas lamp (31.60); neither beat is about the killing.
- **Scenes 2, 4, 5, 7, 8:** window (straight down now, 7.30-7.53; out right 8.60-8.87), open book, second window, lamp head, clock. All paths clear of faces and hands.
- **Captions vs narration:** the 37 SRT cards equal `narration.txt` word for word; all 210 strips show the right card for the words being spoken. No empty band longer than one or two frames (cross-fades; 49.00 is one frame). All cards on one line. Shortest cards: "talked," 0.68 s, "and the phrase" 0.54 s (readable, as round 2 said).
- **Audio:** `voice.mp3` at zero lag, gain 0.997, correlation 0.99985, residual at least 30 dB under the voice in every second; digital silence 51.97-52.5. Nothing added or cut.
- **Drawings:** hand-inked, wobbly, readable; faces read in every scene with people. Scene 2 (girl alone, empty pillow) works. Scene 6 is still small. No text on screen but captions and the opening question (0-2.6 s).
- **Cover and title:** "First sleep. / Then what?" over the girl awake and a red window; title "What was 'first sleep'?". Neither answers the question. Brand dot red, top left. No AI mention, nothing about the killing.
- **Description:** footer "Made with the help of AI tools." present once, before the hashtags; ten sources; text unchanged from the version passed in rounds 1 and 2.
- **Length:** 52.5 s.

## Timing table

| Time (s) | Frames | What |
|---|---|---|
| 11.63-11.67 | 349-350 | drop over the historian's right fingers, in (item 2) |
| 15.13-15.17 | 454-455 | same, out (item 2) |
| 29.93-30.77 | 898-923 | landing at the frame edge, x 1033 (item 3) |
| 45.40-45.43 | 1362-1363 | drop over the woman's resting fingers, out (item 1) |
| 52.00-52.27 | 1560-1568 | paint fades on the candle |

VERDICT: SHIP
