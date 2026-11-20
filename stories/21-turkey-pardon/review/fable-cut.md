# Short 21 "Why does the president pardon a turkey?": final cut review (gate 6)

Reviewer: fresh Fable 5.2 agent, 2026-11-20.
Cut: `out/turkey-pardon-rough.mp4` (46.10 s, 1080x1920, 30 fps, H.264 yuv420p + AAC, -16.0 LUFS, peak -1.6 dBTP). Cover: `out/turkey-pardon-cover.jpg`.

How it was checked: frames every 0.5 s for the whole cut, frame-by-frame (30 fps) around every paint landing and lift, the caption band at 30 fps for every caption change, the audio transcribed with faster-whisper (base.en, small.en, medium.en), and the primary sources opened (Reagan Library, Bush Library, NTF, Truman Library, WHHA, NPR/Michigan Public, ABC News, The Counter, WV Governor, WDTV, Herald-Dispatch).

Summary: script, captions, facts, title and cover wording all pass. The cut fails on the red-paint rules: in a Short about a bird that is normally killed, the paint sits on or drips from the turkey in four places and crosses a face once. All are layout fixes (no new drawings, no new voice needed).

## Blocking

1. **44.2-45.9 s (last scene, `straw-pen`, word "lived"): red blob on the breast of the resting turkey.** The bird is lying down with its eye closed, and the line is "so many have lived only a year or two more". A glossy red patch on its chest reads as a wound on a dead or dying turkey. It is also the last image of the Short. Move the landing off the bird (barn door, a fence post, or the straw in front), calm splat as now.

2. **31.2-33.0 s (`hand-over-turkey`, the drain after the fill): red pools under the turkey's belly and drips down between its legs onto the table** for about 1.8 s, on "this turkey is pardoned." This is the clearest blood read in the cut. The big round fill itself (28.6-31.2 s) reads as paint and can stay; change how it leaves (lift or toss off the top, or fade in place) so nothing red runs down and out of the underside of the bird. `fill.drain` and the "drip" lift at 32.87 s are the cause.

3. **40.13-40.23 s and 41.17-41.33 s (`law-book`, word "law"): the drop falls past the tip of the turkey's beak, and lifts back up through it.** At 40.17-40.20 s the red drop is touching the beak, so it looks like something red dripping from the bird's mouth; the same again on the way out. Landing x=661 is directly under the head. Move the landing to the far side of the book (right page edge or the book's corner) so the path is clear of the head both ways.

4. **9.23-9.33 s (`podium-turkey`, lift after "dodging"): the paint crosses the president's face** (cheek and mouth at 9.27-9.30 s, forehead at 9.33 s) as it tosses up to the next scene. Three or four frames, but it is red on a face and over a mouth. The landing on the lectern front sits right below his head; either move it (the turkey's table drape works, as in scene 3) or change the lift so it leaves sideways.

5. **Cover: the red splat sits on the turkey's flank**, under the raised hand and beside "Pardoned." As a still it reads as a wound more than the large fill does in motion. Put it on the tablecloth or on the card in his hand (`cover.at`). The words and the brand dot are fine.

## Minor (fix in the same pass if cheap; none blocks on its own)

- **42.6-43.5 s (`roast-dinner`, "eaten"):** the drop falls across the roast's breast (42.60 s) and lands on the platter rim directly under the bird. On a cooked bird it reads more like sauce than blood, but the napkin is a safer landing.
- **Paint in transit over turkeys:** 20.3-20.8 s it arrives across the turkey's body and feet before settling on the drape; 33.67 s it arrives at the first turkey's neck in `row-of-lecterns`; 35.67-35.73 s it lifts across that turkey's head. One to three frames each. They will mostly go away when the landings in items 1-4 move; check them again after the re-render.
- **3.70-3.73 s:** the opening drop falls close beside the president's hair (not on the face). Acceptable.
- **Opening (0-3.8 s):** the question is on screen in big type from frame 0 to about 2.4 s and reads well, with a face in the first scene. The paint is only a drip hanging at the top edge during that time; it lands at 3.84 s, after the title has gone. The test rule says "with the paint already landing". Consider an earlier first landing, or accept as is.
- **13.8 s, "if he'd pardon two":** base.en and medium.en hear "pardoned" (medium at 0.90 confidence); small.en hears "pardon" at 0.49. The d of "he'd pardon" runs into the t of "two", so the two are near-homophones and the audio cannot settle it. Heard as "if he'd pardoned two of his former aides", it becomes a question about the past, which is not what was asked, though it asserts nothing false and "He wouldn't say" still follows. The caption reads "Reagan if he'd pardon" and settles it for anyone reading. Not blocking. If that chunk is ever re-voiced, "if he would pardon two" removes the doubt.
- **`reporters` (9.6-19.5 s):** the right-hand reporter's face is slightly garbled at full size (one large blank lens, a tiny second one, a small "8" mouth, stray crossing lines in the hair). It passes at phone size; re-ink if the drawing is touched.
- **`row-of-lecterns` (33.4-35.6 s):** small and busy, and the far end dissolves into scribbles. It reads as "many lecterns with turkeys" in the 2 s it is up, which is all it needs.
- **Scroll frames:** at 33.40-33.50 s and 43.93-44.03 s the incoming drawing passes through the caption line for 2-4 frames. Not readable as an error at speed.
- **Ending:** the last word ends at about 45.98 s and the file ends at 46.10 s; the paint fades from 45.3 s while "a year or two more" is still being said. It lands, but only just. A hold of about 0.4-0.6 s on the clean drawing after the last word would let the line breathe before the loop (pad the render; don't touch voice.mp3).

## Passes

- **Captions vs narration:** every caption read at 30 fps; all 122 words match narration.txt word for word, in order. Bush line is "He told the crowd:" then "this turkey is pardoned." with no quotation marks. Each caption appears within about 0.1 s of its first word. Shortest holds are "have pardoned" (0.47 s) and "Instead," (0.6 s), which match the speech. Captions sit below the drawings and never cover them.
- **What is said:** all three transcripts match the script apart from the "pardon/pardoned" word above. No blips, no dropped words.
- **Scene timing:** reporters drawn by 10.6 s ("Reporters asked" 11.84); joke scene by 20.9 s ("joked" 21.02); hand over turkey from 24.75 s ("In 1989" 24.3-24.9); lecterns 33.4 s ("Every president since" 33.52); law book 36.1 s ("Legally" 36.34); roast 41.4 s ("bred to be eaten" 42.0); straw pen 43.9 s ("lived" 44.18). All on the word.
- **Faces:** stylized line faces, none photoreal, none a likeness that needs the AI label. No red on any face except the transit in item 4.
- **Colour rule:** nothing in the narration, title or cover names a colour; red throughout is correct.
- **On-screen text:** only the opening question and captions. No AI mention on screen or on the cover.
- **Title and cover:** "Why does the president pardon a turkey?" (39 characters, no numbers) and "Pardoned. For what?" (three words, brand dot in place). Together they add a second puzzle and do not give the answer.
- **Length and numbers:** 46.1 s, 122 words (target 45-55 s, 110-130). Numbers heard: 1987, 1989, "two" aides, "a year or two". Within the limit.

## Facts against sources

- **Reagan, Nov 23, 1987** (Reagan Library transcript, opened): "Q. Are you going to pardon North and Poindexter, sir?" He answers that it is "a question no one can answer at this point, and I'm not going to try", then: "If they'd given me a different answer on Charlie and his future, I would have pardoned him." The aide had just said "He's going to a pet farm." Narration ("He wouldn't say. Instead, he joked that he would have pardoned the Thanksgiving turkey he'd just been given") is accurate. The description's quote "would have pardoned" is exact.
- **Bush, Nov 17, 1989** (Bush Library transcript, opened; date confirmed by the NTF history page): "he will not end up on anyone's dinner table, not this guy -- he's granted a Presidential pardon as of right now". The description's quote "granted a Presidential pardon as of right now" is exact. The narration's "this turkey is pardoned" is a fair paraphrase and is shown without quotation marks.
- **"The first time a president talked about pardoning a turkey"**: NPR/Michigan Public says Reagan "used the word 'pardon' for the first time in reference to sparing a Thanksgiving turkey". The description adds "on record". Fine.
- **"Every president since has done the same"**: NTF: "The custom of 'pardoning' has continued with each president since then"; Herald-Dispatch (2026-11-19): each year since 1989. True through 2025.
- **"Legally, there's nothing to pardon"**: Art. II sec. 2. The UNC page returned 403 to my fetch (likely a bot block); open the link in a browser on upload day.
- **"many have lived only a year or two more"**: ABC News (2013) confirms Cobbler was euthanized in August and Gobbler died in February after the 2012 pardon; The Counter confirms the Virginia Tech birds' short lives and that Courage (2009) "lived over six years". "Many" is right; the description gives the exception.
- **Description, two small things:** (a) "already headed for a petting farm": the transcript says "pet farm" (NPR says "petting zoo"); use "pet farm". (b) "recent university care has helped" is not supported by any source in the list (The Counter reports the university birds dying within about a year; the NC State page is not listed, and the research file found no death dates for 2020-2025 birds). Cut the clause or add the source, since the description says every claim is checked against the list. The disclosure footer and sources are in place.

## Time-sensitive

- **2026 ceremony (Tue Nov 24, 2:00 PM ET):** WV Governor's office (Nov 18) and WDTV confirm this year's two turkeys are going to the White House "next week" for the president to pardon. I could not re-open the pool advisory with the exact time (429). Nothing in the narration or description depends on the time or the outcome.
- **"Every president since has done the same"** holds as of today. Gate 7 must re-check on the morning of Nov 24 that the ceremony has not been cancelled or changed; if the Short goes out before 2 PM ET the line is still true as written.
- No 2026 names, weights or destinations appear anywhere in the Short or description. Good.

## To pass on re-review

Items 1-5 fixed and re-rendered, then a look at the frames around each landing and lift (and the transit frames listed under Minor). The description edits take a minute and should go in the same pass.

VERDICT: FIX
