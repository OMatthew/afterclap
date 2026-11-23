# Short 23 "the Blue Hippo": gate 6 full-cut review

Reviewer: fresh Fable 5.2 agent, 2026-11-23. Reviewed `out/blue-hippo-rough.mp4` (49.81 s, 1494 frames) and `out/blue-hippo-cover.jpg` against `narration.txt`, `words.json`, `description.txt`, `publish.md`, `research/23-blue-hippo.md`, CHANNEL_RULES.md and LEAD.md.

How: stills every 0.5 s across the whole cut (10 contact sheets), every frame at 30 fps around all nine landings, lifts and between-scene moves (35 sheets), full-size crops of every face and of the hippo, ferry, cat and radio scenes; faster-whisper transcript of the cut's audio; ffprobe and ebur128. Frames are in the session scratchpad under `h23-review/` (sheets/, crops/).

Sources re-opened today: Macy's Aug 18, 2026 release (macysinc.com), Fox 13 (Macy's statement, Nov 21), Good Housekeeping via Yahoo (Nov 23), NYT 2017 (Caron) via blimpinfo, Fox 5 NY parade forecast (Nov 19). Not opened: NYT 1931 (paywalled, still second-hand), NYPL, Untapped (read by the script reviewer today).

## Blocking (2)

### B1. Red and dark-red paint on the hippo's body, three times (25.90-26.60, 30.70-31.43, 44.90-45.60)

The paint is only blue while it sits still. It arrives red, and in scene 6 it leaves red:

- **25.90-26.50 (scene 6 landing):** a red drop slides in over the hippo's rump and along its flank, then splats red on its side (26.40-26.50). At 26.53-26.60 the red-to-blue blend passes through a dark maroon disc about a third of the body wide. Blue from about 26.63.
- **30.70-31.43 (scene 6 drain and lift):** the blue pool turns purple (30.70-30.73), then a red-brown smear lying between the hippo's hind legs (30.77-30.83), then a glossy red blob hanging from its underside (30.87-31.23) that stretches into a long red drip and falls (31.27-31.43). This is the worst of the three: about 0.7 s of red pooled under, then dripping from, an animal's belly.
- **44.90-45.60 (scene 9 landing):** same as the first: red drop across the rump, red splat on the flank, maroon disc at 45.57-45.60.

Why it blocks: "red paint must not read as blood" and "paint ... never bodies". The hippo is drawn as a creature with a face, and the Short goes out six days after Fiona died, when a red patch on a hippo's side or a red drip from its belly is the one image this video cannot have. It also contradicts the colour rule in spirit: the narration says "blue hippo" at 26.14 and the paint on it is still red until 26.6.

Fix (the ending at 47.46-49.5 already does it right: the pool stays blue, drains and fades on the hippo with no red):

1. Make the paint blue before it touches the hippo, on both landings. The tint keyframe is `at: 26.38` / `at: 45.38` (the landing); move it to before the drop enters the drawing (about `25.85` and `44.85`, with a short `dur`), so the drop travels and splats blue. If the engine can't tint a drop in flight, bring the drop in from above onto empty paper beside the hippo, or drop the travelling drop for these two landings and let the blue pool well up in place.
2. Scene 6 exit: keep it blue through the whole drain and until it is clear of the body. Either let the blue drain and fade out on the hippo exactly as scene 9 does and start a fresh red drop for the radio room from the paper edge, or let the drip fall blue and turn red only after 31.45, once it is in empty paper below the feet.
3. Re-check with every frame from 25.8-26.7, 30.2-31.5 and 44.8-45.7: no frame with red, maroon or red-brown inside or touching the hippo outline.

### B2. The ferry scene's balloon does not read as a tiger, and the red lands on the boat-hook's tip (15.3-20.9; paint 18.57-20.5)

- While the caption and voice say "the tiger balloon" (18.3-19.3), the drawing shows a smiling, knotted sack: two dot eyes and a smile, no visible ears at size (the one "floppy ear" from fixes.py is a small bump), no tail, and four faint lines on the right that read as folds in cloth, not stripes. A cold viewer sees two sailors hooking a happy laundry bag. It is cute, but it is the one drawing in the cut that fights its own caption.
- The red splat lands exactly where the hook's point meets the knot, on a thing with a face (18.77-20.5). Hook plus face plus red at the point of contact is the blood reading the rule warns about ("blades or anything that could bleed"). It is small (R 32) and calm, so on its own I would have called it minor; together with the first point the scene needs one more pass.

Fix (fixes.py, `ferry-tiger` block): give the balloon two clear upright ears on top of the head, three or four bold curved stripes across the whole body (thick enough to survive at 1080), a striped tail trailing in the water, and whiskers or a small nose so the face reads cat-like; keep it limp and half-deflated. Move the paint off the hook point: onto the striped flank well away from the hook and the face (as on the dragon in scene 2), or onto the ferry's rail or porthole. Look at a 19.5 s still before re-rendering the whole cut.

## Minor (lead's call; none blocks on its own)

1. **31.63-31.80, radio room entry.** The red drop comes down past the operator's head on the headphone side while he is still being inked. Measured on full-size frames: about 70 px from the headphone's edge at the closest (31.73), about 290 px from the eye and further from the mouth, never over the head, and it lands on the set's lamp at 31.83 and slides down to the dial by 32.27. It is behind his ear, not beside his face or mouth, so it passes. If B1's fix starts a fresh drop for this scene anyway, bring it in from the left paper edge at dial height and the question goes away.
2. **2.13-2.27, intro.** The falling drop crosses the question's letters ("look", then the "o" of "hippo") for four or five frames. Readable, and the title is fading by 2.33; nudging the drop's x about 60 px right would clear the type.
3. **Blue fill is an oval, not the hippo.** In scene 6 (26.6-30.4) the ellipse covers the belly and the tops of three legs and pokes outside the outline at the lower left (rump/hind leg) and between the legs; in scene 9 it sits better. It reads as "a blue patch on a hippo" rather than "a blue hippo". The hook-test rule asks for whole shapes filled. A polygon that follows the body outline (stopping at the head, as now) would be better; not blocking, since the colour reads at once and stays off the face.
4. **Cover.** Correct on the rules (blue paint, red brand dot, three words), but the blue blob is small (R 46) for a cover whose title says "blue hippo"; at thumbnail size it is a dot on the hind leg. Consider the same body fill as the video, or at least double the radius.
5. **14.07-14.57, prize sack.** The paint lands on "won" and starts to gather 0.5 s later; it is the shortest hold in the cut and barely registers. Scene 3 is only 2.7 s, so this may be the best available.
6. **Cat on the wire (21.0-25.5).** Reads as a real tabby asleep across the wires with a wisp of smoke, more than as a balloon; the dangling string helps. Gentle, no fire, no gore, and the red sits on the pole at the insulator, not on the cat, so it reads as a spark at most. Passes.
7. **Ferry crewman, left.** The V brow gives him a scowl; fine for a man hauling a wet balloon.
8. **Loudness.** -16.2 LUFS integrated, true peak -1.6 dBFS, LRA 2.1 LU. A little under the usual -14 for Shorts; YouTube does not turn quiet uploads up. Fine if this matches Shorts 18-22.
9. **File size.** 18.37 MB, under the 20 MB limit with little room; watch it on the re-render.

## Passes

- **Specs:** H.264 High, yuv420p, 1080x1920, 30 fps, 1494 frames; AAC-LC 48 kHz mono; 49.81 s; 18.37 MB.
- **Audio vs narration:** faster-whisper transcript of the cut matches narration.txt word for word (128 words in words.json, all matching; only "brand new" / capital "Parade" differ, which is the transcriber's spelling). Voice is 49.37 s; nothing re-timed.
- **Captions vs narration:** all 40 caption cards read off the frames match the narration exactly, including punctuation ("brand-new", "hundredth", "they're holding / on to it."). No AI mention, no extra on-screen text.
- **Timing on the word:** landings at asked 2.42, letting 10.28, won 14.08, tiger 18.76, line 23.98, hippo 26.38, radioed 32.22, saying 37.60, blue 45.38, each within a frame or two of the word in words.json and in the transcript. Scene changes fall in the pauses (6.3-6.8, 12.1-12.7, 25.4-25.9, 31.0-31.5, 41.3-41.8).
- **Opening:** the question is on screen in cover-style type from frame 0 to about 2.4 s (fade to 2.6), with the red drop already hanging at the top from frame 0 and landing on the lifebuoy at "asked". A character with a face (the officer with binoculars) is in the first frame. No branding at the start.
- **Ending:** clean and short: the blue drains and fades on the hippo by 49.5, 0.3 s of still drawing, no reel, no sting, no tease. Last drawing shows the handlers on the ropes, which carries "holding on to it".
- **Paint and faces, everything except B1/B2:** lifebuoy (scene 1), dragon's body (2), prize sack (3), pole (5), radio dial (7), telephone base (8) are all objects, all calm splats (no specks, no drips). Entries and exits checked frame by frame: scene 2 exit leaves by the dragon's tail; scene 3 entry and exit travel at sack height to the right, away from the man's face; scene 4 entry and exit run along the rail under the crewmen's hands, well below both faces; scene 5 in and out at the left pole; scene 7 exit to the left edge at dial height; scene 8 in and out low on the right at desk height, well under the caller's open mouth. No red on, across or beside a mouth anywhere.
- **Colour rule:** the paint is blue while it rests on the hippo in both scenes (26.63-30.67, 45.63-49.5) and on the cover; red everywhere else; the cover's brand dot is red. (The arrival and departure colours are B1.)
- **Look:** warm textured paper, wobbly hand-inked line with boil, lots of empty space, one accent. Nothing reads as vector or clip art. Faces read on the officer, the three handlers, the prize man, both crewmen, the radio operator and the caller. The Empire State top has its 1931 mast and no antenna. Nothing garbled apart from the tiger (B2).
- **Facts, narration:** every line still stands against the sources re-opened today. Macy's Aug 18 release: "every balloon was accounted for" except the Blue Hippopotamus, "last seen soaring beyond the Empire State Building", "will make a triumphant return to Macy's Thanksgiving Day Parade 2026". Good Housekeeping: "radiograms have been sent to the captains of all transatlantic liners now at sea", "the reward for its return has been multiplied by four", tiger "salvaged by the crew of the Greenpoint ferry boat Wyoming". NYT 2017: "Calls streamed in from people who claimed to have found the hippo", Felix "floating into a high-tension wire and catching fire", believed "soaring somewhere over the ocean". No dollar figure, no direction of drift, no "replica", no size. Three numbers (1931, four times, hundredth).
- **Facts, description:** dates and claims match (1928-1932 releases; Dec. 2, 1931 NYT; "then only months old"; "thought to be somewhere over the ocean"; stopped by 1933). The Fiona line is accurate and respectful: she died Nov 19; Macy's statement (Fox 13, Nov 21) says "Blue Hippo's handlers will wear a purple Fiona patch during the 100th Macy's Thanksgiving Day Parade". The line says "patch", not "dedicated", makes no joke, and Fiona is absent from the narration, title, cover, captions and tags. Sources listed; footer "Made with the help of AI tools." present. One small honesty note: the NYT 1931 article is listed as a source but was read only through later quotation; that is acceptable since the two outlets quoting it are listed too.
- **Title and cover:** "Why did Macy's ask ships to look for a blue hippo? 🦛" (52 characters, no numbers) with "Last seen: flying" does not answer the question; the cover adds a second puzzle. Neither names the balloon release, the reward or the radiograms.

## Time-sensitive lines, to re-check Wednesday morning before it goes live (gate 7)

- **"This year, in its hundredth parade, Macy's is flying a blue hippo again." (41.8-46.2)** True as of today: Macy's Nov 21 statement ("as Macy's welcomes our own beloved Blue Hippo back to the parade") and Good Housekeeping, Nov 23 ("will be making an appearance in the Parade"). Re-open Macy's newsroom and one news search for "Blue Hippo" on Wednesday.
- **Wind.** The only forecast found is still Fox 5 NY, Nov 19: no wind numbers yet; the early-week storm should clear by Thursday, with a chance of lingering wet conditions. NYC grounds the giant balloons at 23 mph sustained or 34 mph gusts. Check the NWS New York forecast for Thursday 8 AM-noon on Wednesday. If grounding looks likely, hold the upload and use the fallback in publish.md ("Macy's is bringing a blue hippo back." needs a re-voice of the last chunk); "This time, they're holding on to it." survives either way.
- **Fiona line in the description.** Re-read against Macy's latest statement on Wednesday (patch and donation; nothing about dedicating the balloon as of Nov 21-23). If Macy's changes the plan, change the line to match its words.
- **"This year"** dates the Short; fine for a Wednesday post, and the description gives the year through its sources.

VERDICT: FIX
