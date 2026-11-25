# Short 23 "the Blue Hippo": gate 6 full-cut review, round 3 (fallback last line)

Reviewer: fresh Fable 5.2 agent, 2026-11-25. Reviewed `out/blue-hippo-rough.mp4` (50.0 s, rendered 2026-11-25 14:11 UTC, commit 704d68f; HEAD 7a41218) against `narration.txt`, `description.txt`, `publish.md`, `words.json`, `out/cues.json`, CHANNEL_RULES.md (Look, captions, gates) and the round-2 review `fable-cut-v2.md`.

Scope: the change since round 2 is the last line ("Macy's is bringing a blue hippo back.", voice take c, chunks 4-5 regenerated) and the re-render that follows from the new timings.

How: audio pulled from the cut and compared sample-wise with `voice.mp3` and with the round-2 `voice.mp3` (git 2ed759f); level trace in 50 ms frames around every pause from 30 s on; faster-whisper (small.en, word timestamps) on the cut's audio against `words.json`; caption strip at every 0.25 s for the whole cut (200 strips, 4 sheets, all read); stills every 0.25 s from 30.0 to 49.75 (8 sheets, all looked at); every frame 31.50-32.27 (radio-room entry) and 48.60-49.63 (final drain); full-size frame at 46.5; per-frame red / blue / purple pixel count with paint position over all 1500 frames; ffprobe and ebur128. Frames are in the session scratchpad under `h23-review3/` (sheets/, q/, col.json).

Not re-done: scenes 1-5 frame by frame (the first 31 s of voice are bit-for-bit the round-2 takes and the landings there fall on the same words at the same times; the paint trace shows the same landings), the cover (unchanged), and the historical fact check (round 1).

## Blocking

None.

## 1. Audio of the regenerated chunks

- **Same takes up to the splice.** New `voice.mp3` vs round-2 `voice.mp3`: correlation 1.000 in every second from 0 to 31 s, unrelated from 31 s on. So chunks 0-3 are untouched and the new audio starts with "So Macy's radioed". The cut's audio matches `voice.mp3` (correlation 0.9996-0.9999 in every 6 s window, zero lag); the render did not re-time it.
- **Splice at 31.0-31.5 is clean.** "going" decays naturally (-10, -15, -24, -31, -42, -55 dB), then 0.4 s of digital silence, then "So" comes up from silence. No click, no cut-off tail, no clipped onset. The other joins (41.4-42.0 before "This year"; the tail after "it") are the same shape. Pauses: 0.50 s at the splice, 0.58 s before "This year", like the 0.50-0.51 s pauses in the old chunks.
- **No clicks or clipping.** Largest sample-to-sample jumps in 31-50 s are the same size as in the untouched part; peak -1.6 dBTP, no clipped samples.
- **Nothing rushed.** Chunk 4 at 172 wpm and chunk 5 at 168 wpm, no stretch (the old chunks run 160-185). "This year, in its hundredth parade," takes 2.0 s, then a 0.68 s breath, "Macy's is bringing a blue hippo back." 2.1 s, 0.56 s pause, "This time, they're holding on to it." 2.0 s. The ending has room.
- **Transcript.** Whisper returns the narration word for word, including "Macy's is bringing a blue hippo back." and "This time, they're holding on to it." (it writes "brand new" for "brand-new"; nothing else differs). Its word times agree with `words.json` within 0.05 s for nearly every word; the worst are "saying" (0.12 s) and "to"/"it" at the very end (0.08-0.12 s), none of which moves a caption or a landing by a visible amount.
- Same voice, level and room tone on both sides of the splice as far as the level trace and transcript can show. I can't listen; nothing measured suggests a change of timbre, but a human ear is the only real test of that.

## 2. Captions vs narration, whole cut

All 39 caption cards read at 0.25 s steps, in order: "In 1931, / a department store / asked ships at sea / to watch the sky for / a blue hippopotamus. / Back then, / Macy's ended / its Thanksgiving / parade by letting / the giant balloons go. / Bring one back, / and you won a prize. / So the city chased them. / A ferry crew fished / the tiger balloon out / of the East River. / The cat drifted / to New Jersey, / hit a power line, / and burned. / But the blue hippo floated / past the brand-new / Empire State Building, / and kept going. / So Macy's radioed / the ocean liners, / and made the reward / four times bigger. / People phoned in, / saying they had / found the hippo. / Nobody ever / brought it back. / This year, / in its hundredth parade, / Macy's is bringing / a blue hippo back. / This time, / they're holding / on to it."

Word for word the same as `narration.txt`, punctuation included. No leftover "flying" or "again" anywhere. No AI mention on screen. Each card is up within about 0.1 s of its first word (new cards: "Macy's is bringing" by 44.75 for 44.70; "a blue hippo back." by 45.50 for 45.46; "This time," fading in at 47.25 for 47.38; "they're holding" by 48.25 for 48.18; "on to it." at 48.75 for 48.80).

## 3. Scene timing, last three scenes

| Scene | Drawing starts | First word | Paint lands | Landing word |
|---|---|---|---|---|
| radio room | 31.51 | "So" 31.62 | 32.20 | "radioed" 32.20 |
| phone caller | 36.46 | "People" 36.62 | 37.62-37.63 | "saying" 37.62 |
| handlers and hippo | 41.84 | "This" 42.06 | 45.77-45.80 | "blue" 45.78 |

All three scenes are fully drawn before their first caption is a quarter second old, and all three landings fall on the frame of their word (checked against the paint trace, not only cues.json). In the last scene the drop enters at 45.30 under "bringing" and the blue fill spreads across the body from 45.80 to about 46.3, so the hippo is blue while "blue hippo back" is on screen and stays full until 47.7.

## 4. Paint, 30-50 s

- **Scene 6 exit (30.24-31.70).** Fill drains blue, bead at the knot 30.75-31.1, falls blue. It turns from blue through two dull-plum frames (31.67-31.70) to red at 31.73, in empty paper above the radio set, after the hippo has scrolled off the top. Same as round 2.
- **Radio room (31.73-32.27).** The red bead comes down the left edge onto the lamp of the set and settles on the set's lower panel at (166, 797). It stays left of the headphone the whole way, never over the head, well away from the eye and mouth. Small calm splat on an object.
- **Phone caller (37.17-37.63 in, 41.23-41.57 out).** In and out low on the right at desk height (y 1037-1167), onto the base of the candlestick phone, under the raised arm and far below the open mouth.
- **Last scene (45.30-49.60).** Blue from its first frame at the left paper edge; crosses empty paper to the rump; fills the body, belly and the tops of the legs and stops at the neck, so the head and face stay bare paper. Drains downward blue from 47.68, gathers at the tie-off knot about 49.0, pales and is gone by 49.60. The last 0.4 s is the bare drawing with "on to it."
- **Colour count.** Zero red and zero purple pixels in every frame from 25.33 to 31.70 and from 41.60 to the end, which covers every frame in which either hippo is on screen. No red, maroon or plum inside or touching a hippo anywhere. Red in 30-50 s sits only on the radio set and the phone base.
- The handlers are stick figures with blank heads; no paint goes near them.

## 5. Is the new last line true either way?

- **"This year, in its hundredth parade, Macy's is bringing a blue hippo back."** Macy's announced the Blue Hippo's return for the 100th parade on Aug. 18 (its own release, first source in the description), and the lead's gate-7 check this morning found it still in the lineup. The line says what Macy's is doing; it no longer says the balloon is in the air. If the wind grounds the balloons on Thursday, "is bringing back" still describes the plan and the balloon Macy's made, where "is flying a blue hippo again" would have been false. It would turn untrue only if Macy's pulled the Blue Hippo from the parade altogether, which nothing suggests.
- **"This time, they're holding on to it."** True flown or grounded: Macy's stopped releasing balloons by 1933, and a grounded balloon is held on to all the more.
- **Captions:** same words, same result. **Title:** about 1931. **Cover ("Last seen: / flying"):** about 1931.
- **Picture:** the last drawing shows the hippo in the air on its lines above the handlers. It illustrates how the balloon is meant to travel and is not a claim; I don't count it as depending on Thursday.
- **Description:** "Macy's announced the Blue Hippo's return in August" (true, dated). "Macy's said the balloon's handlers will wear a purple patch" is reported as Macy's statement, so it stays true as a report even if the balloon is grounded. Nothing in the description says the balloon flew or will fly. AI footer line is there; sources are listed.
- I did not re-verify the forecast or the lineup myself beyond a search that showed the same wind headlines the lead logged; I'm relying on the lead's 8 AM gate-7 check for both.

## 6. Specs

H.264 High, yuv420p, 1080x1920, 30 fps, 1500 frames; AAC-LC 48 kHz mono; 50.005 s; 18,322,654 bytes (18.32 MB, under 20 MB). Integrated loudness -16.2 LUFS, LRA 2.1 LU, true peak -1.6 dBFS.

## Minor (lead's call; none blocks)

1. **`publish.md` is stale.** It still gives the status as "gate 6 pending", the file as "~49.8 s, 18.4 MB", the schedule as Wed 10:00 AM, and quotes the old last line as the current one. If the upload helper reads it, update it first (50.0 s, 18.3 MB, new upload rather than LdHCdWmI4QE, fallback already applied).
2. **The blue leaves the hippo while the voice says "they're holding on to it."** The drain starts at 47.68 on "time" and the body is bare by about 49.0, under "on to it." It follows the channel's ending rule (paint fades out) and round 2 passed the same ending, but with the new line the hippo is fully blue for only about 1.4 s. If there is ever another render, start the drain about 0.5 s later.
3. **49.0-49.5, blue bead at the knot between the hind legs**, as in scene 6 (round-2 minor 1). Blue, on the knot, reads as paint running off.
4. Round-2 minors 2-4 stand as they were.

## Gate 7 reminder

The wind no longer matters to the script. What still does, before it goes live: the Blue Hippo is still in the lineup, and the Fiona line still matches Macy's latest statement.

VERDICT: SHIP
