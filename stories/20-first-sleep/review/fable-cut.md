# Gate 6: full-cut review, Short 20 "What was 'first sleep'?"

Reviewer: Fable (fresh, cold). 2026-11-25.
Cut: `out/first-sleep-rough.mp4` (52.5 s, 1080x1920, 30 fps, 1575 frames, H.264 yuv420p, AAC mono 48 kHz). Cover: `out/first-sleep-cover.jpg`.

How I checked: stills every 0.25 s across the whole cut (210 frames, all looked at), every second frame at 30 fps across each of the 17 paint moves, full-resolution crops of the risky ones, a per-frame scan for red pixels and for an empty caption band, the cut's audio subtracted from `voice.mp3`, ebur128 on both, and the description against `research/20-first-sleep.md` and the v4/v5 script reviews. I did not re-open the web sources (facts passed at v4/v5).

## Blocking

1. **31.07-31.17 s: the paint splats on blank paper, on top of the caption.** The landing for "lamps" (31.10) fires while scene 7 is still scrolling in and before its drawing exists (`pen` starts 31.13, the scroll runs 30.73-31.53). The drop flies down through the caption band and bursts, with spatter, on the "B" of "But as lamps" at about x 300, y 1340 (frames 933-934), then jumps up the frame with the lamp, which stays blurred until about 31.4. It reads as a glitch: red on the caption, a splat on nothing, and the lamp arriving after its word. Fix: land after the scroll settles (on "brighter", 31.60, or give the landing an offset of about +0.45 s), or start the scroll about 0.5 s earlier so the lamp is drawn and still at 31.10.

2. **Two captions run about 0.4 s late, and one flashes for 0.2 s, because of two zero-length words in `words.json`.**
   - `volunteers` is stamped 37.60-37.60, the same start as `kept`. In the audio the word begins at about 37.12 (the silence after "experiment," ends there). So "In one experiment," stays up while "volunteers" is spoken, and "volunteers kept" is fully visible only 37.60-37.80.
   - `Researchers` is stamped 42.80-42.80, the same start as `still`. In the audio it begins at about 42.42. The caption band is empty 42.37-42.80 while the word is spoken, and "Researchers still" arrives as he finishes it.
   Fix: correct the two stamps (volunteers about 37.12-37.60, Researchers about 42.42-42.80), re-run shots.py and layout.py, and check that scene 9's start (now 42.68) moves earlier with it. This is caption data only; the audio is not touched.

## Should fix

3. **Scene 10 (45.86-52.5 s) has no paint, and the paint never fades out.** The last red pixel is at 45.80; the blob on the researchers' papers is not lifted, it just scrolls off the top with scene 9 (45.3-45.8). The final 6.7 s is the longest hold in the film, on a repeated drawing, with nothing moving but the line boil. The 18-22 test asks for an ending "with the paint fading out". `layout.py` still carries `(10, 'meant')` for the candle flame, but `shots.py` gives scene 10 no paint, so the entry is dead. Either land on the candle at "meant" (48.08) and fade it over the last second, or lift the paint off the papers so it leaves on purpose. If the empty ending is deliberate, delete the dead entry and say so in shots.json's notes.

4. **"or visited" is on screen for about 0.3 s** (29.34-29.66, fully visible about 0.17 s), and "Then what was" for about 0.35 s (14.23-14.57). Both are too short to read. Re-break as "talked, or visited" / "the neighbours." and "Then what was the second?" (24 characters, fits `capChars`).

5. **Scene 2 and the cover: the mother does not read as a person.** She is a closed loop on the pillow at the left with no face or hair (5.7-8.9 s; cover, lower left). A viewer sees one girl and a lumpy pillow, one second after "her mother was killed". Also, the line says "they had just woken" while the drawing shows her asleep. Re-ink her with a cap and a profile, awake or stirring, or take the shape out.

6. **Scene 6 (27.0-30.8 s): a solid black blob at the top corner of the door**, next to the neighbour's head (about x 955, y 640). It is the only filled black shape in the film and looks like an ink accident. Remove it in `fixes.py`. In the same drawing the "lantern" is a plain loop that reads as a sack until the paint lands on it at 29.94, and the waving hand in the doorway reads as a heart. A handle and a small frame on the loop would fix the first. The drawing is also small: it fills about a quarter of the frame height, with the faces about 60 px wide.

7. **Scene 5 (21.7-26.6 s): a stray line runs from the man's mouth corner down over his chin to his collar.** It reads as a crack or a dribble. Trim it. The woman's face is one dot and a nose mark; it reads, just.

8. **Cover wording: "Then what was second?"** is not quite English, and the narration says "Then what was the second?". Use "What was the second?" or "First sleep. Then what?". Everything else on the cover passes (see Fine).

9. **42.80-42.87 s: the paint crosses the back of the woman researcher's hand** on its way in from the right (frames 1284-1286). It is two frames, on a hand, in a beat with no danger in it, about 300 px below her face. Use `enter='up'` or a start point below her forearm.

10. **Housekeeping:** `research/20-first-sleep.md` lines 24 and 32 still say "no source for 1697"; v4 found CNN gives 1697, and the description cites it. Correct the note so the fact table and the description agree.

## Fine

- **Captions vs narration:** all 47 caption cards match `narration.txt` word for word, in order, with curly quotes and the "1690s" wording. No missing or extra words. Apart from items 2 and 4, each card comes up within about 0.1 s of its first word. The only empty stretch longer than 5 frames is 42.37-42.80 (item 2); the rest are 4-frame cross-fades.
- **Audio:** the cut's audio is `voice.mp3` at zero lag, gain 0.997, correlation 0.99985; the residual sits 33-45 dB under the voice in every second (AAC coding noise, no edits, no added sound). Cut: -16.1 LUFS integrated, LRA 2.2 LU, true peak -1.5 dBFS. Voice: -16.1 LUFS, LRA 2.2, peak -1.7. The tail after the voice ends (51.97-52.5) is digital silence. No clicks: nothing in the difference signal stands out, and the only sharp sample steps are the voice's own consonants.
- **Opening question:** "What was 'first sleep'?" is at full strength from 0.00 to about 2.3 s and gone by 2.6 s, over scene 1, with Jane's and the clerk's faces on screen from the first frame and the paint drop already forming at the top edge.
- **Paint near faces and mouths:** no red on or touching any face or mouth in any frame. Nearest approaches:
  - Scene 1: the drop falls (3.0-3.1) and lifts (5.0-5.2) straight up the gap between Jane and the clerk, about 130 px from the edge of her face and about 160 px from his, more than one face-width each side. It does not cross either face. Worth knowing that the lift happens while "her mother was killed." is still on screen; if the lead wants more margin, let it fade in place on the flame.
  - Scene 6: the paint enters at door-handle height (29.55-29.75), about 150 px below the neighbour's mouth, and lands on the lantern at his hand.
  - Scenes 2, 3, 5, 7, 8, 9: window, lower page, window, lamp head, clock, papers; the paths come in from the frame edge away from heads. The historian's page landing is about 250 px below his mouth.
- **Blood:** scene 1's landing is a small calm blob (R 22, no spatter, no drip) sitting exactly on the wick of an unlit candle, and it reads as the flame. Nothing red touches Jane, the clerk, the table or the page while "killed" is on screen. The two spattered landings are on the open book (20.0-20.8, with a short run down the page) and the gas lamp (31.2-35.2); neither beat is about the body. If the lead wants to be strict about "doctors' books", make the book landing calm too.
- **Paint on things that make sense:** candle flame (court), night window (first sleep), the old page (stopped), the open book (two thousand), night window (midnight), lantern (neighbours), gas lamp (lamps), clock (fourteen hours), papers (debate). No colour is called out, so red throughout is right.
- **Drawings:** hand-inked, wobbly, warm; no clean vector or clip-art look. Faces read in scenes 1, 3, 7, 8, 9 and 10. No text anywhere except the captions and the opening question (the historian's page and the researchers' papers carry squiggles, not letters). No photoreal faces.
- **Cover and title:** the title "What was 'first sleep'?" (23 characters, no numbers) and the cover do not answer the question; the cover adds a second puzzle. No AI mention on the cover or anywhere on screen. Brand dot is red, top left. The big splash on the night window is well away from the girl's face. No shock words, nothing about the killing.
- **Victim:** the killing is said once, plainly, with no image of it, no joke, and the film does not return to it. The description closes it ("The crime was never solved."). Not glib.
- **Description:** matches the text passed in the v4 and v5 script reviews. Date given as 13 April 1699 per the BBC with CNN's 1697 noted; Jane Rowth, nine; two men at the window; deposition for an assize court; Public Record Office; "about two thousand references"; change dated to the 1800s with artificial light as the main cause among several; Wehr 1992, 14 hours of darkness, four weeks, no head count; Yetish 2015, Boyce 2023, Ekirch's 2024 reply. All consistent with the research file apart from the stale 1697 note (item 10). Ten sources listed. Footer line "Made with the help of AI tools." is present, once, at the end before the hashtags. 2,993 characters.
- **Length:** 52.5 s, inside the 45-55 s test range.

## Timing table (for the fixer)

| Time (s) | What |
|---|---|
| 0.00-2.6 | opening question, fading from 2.3 |
| 3.13 | landing 1, candle flame |
| 7.53 | landing 2, window |
| 11.97 | landing 3, page |
| 14.23-14.57 | "Then what was" (too short, item 4) |
| 20.07 | landing 4, open book |
| 25.83 | landing 5, window |
| 27.0-30.8 | black blob on the door (item 6) |
| 29.34-29.66 | "or visited" (too short, item 4) |
| 29.93 | landing 6, lantern |
| 31.07-31.17 | splat on the caption (item 1) |
| 37.12-37.60 | "volunteers" spoken, caption late (item 2) |
| 38.17 | landing 8, clock |
| 42.42-42.80 | "Researchers" spoken, no caption (item 2) |
| 42.80-42.87 | paint over the researcher's hand (item 9) |
| 43.23 | landing 9, papers |
| 45.80 | last red pixel; none after (item 3) |

VERDICT: FIX
