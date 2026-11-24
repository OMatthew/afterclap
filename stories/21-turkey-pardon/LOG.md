# 21-turkey-pardon: log

## 2026-11-20 (scheduled lead run)
- **Research (gate 2): PASS.** research/21-turkey-pardon.md (Fable research agent): every claim sourced; Truman and Lincoln myths noted; Reagan 1987 and Bush 1989 checked against the presidential library transcripts.
- **Script (gate 3): PASS on v5** after four rounds.
  - Fable fact check: v2 FIX (tense of "many live", "aides", "no joke"); v3 FIX (clarity of "Two years later"); v4 PASS; v5 PASS (review/fable-script.md).
  - Viewer panel (5 independent Fable personas, panel/): v2, v3 and v4 each had 3-4 of 5 naming the 1947/backstory line as their exit (failed the gate twice: told Matthew, with the lead's fix). v5 cut the backstory: exits split 2/2/1, no line named by 3+, END% 57/78/68/58/60 (median 60).
  - Taken: Reagan first, "former aides", the joke in plain order, "In 1989, the next president", lifespan in present perfect. Rejected: "That bird was still headed for dinner" (false: it was going to a pet farm).
- **Voice (gate 4): PASS.** Take b, --tempo 0.95 (take a was 43.7 s, under 45). 46.1 s; words.py 0.980; blips 0. Whisper hears "pardoned" for "pardon" at 13.8 s (near-homophone before "two"; caption is right; not blocking).
- **Art (gate 5): PASS.** 10 ChatGPT guides (Sonnet helper), traced; 8 used (crate-steps, farm-truck unused after the backstory cut). Faces checked at full size; the middle reporter's face is blank after tracing (as in 18).
- **Cut (gate 6): FIX** (Fable full-cut review, review/fable-cut.md). Five blocking red-paint items: final landing on the resting turkey read as a wound; the body fill drained like blood; drops/lifts crossed the turkey's beak, the president's face and the cover turkey's flank.
  - Fixed so far: body fill removed; landings moved to lectern, notepad, card, first lectern, far side of the book, napkin, barn; cover splat on the card; description "pet farm", unsupported "university care" clause cut.
  - **Still open:** the paint's travel path between scenes isn't vertical, so on lifts and drops it can still pass close to the presidents' faces (9.3 s beside the first president's head; 28.45 s and 33.1 s near Bush's shoulder and neck). Next run: read how engine/plan.cjs picks the gather/lift path (`tr.mode`) and either move landings so the path clears faces or set the mode; then re-render, look at transit frames, and run a fresh Fable full-cut review.
  - Minor, optional: 0.4-0.6 s hold at the end; first landing could come before the title fades.
- **Publish plan (gate 7):** Tue Nov 24, after the 2026 ceremony (2:00 PM ET) so "Every president since has done the same" is checked that day; e.g. schedule ~2:30 PM CT. Title "Why does the president pardon a turkey? 🦃"; cover "Pardoned. For what?"; description.txt.

## 2026-11-23 (scheduled lead run)
- **Cut (gate 6): SHIP on round 3.** Paint travel: new opt-in engine options (`exit` left/right/up, `enter` side/top) so the paint leaves sideways instead of rising past faces; card landing drops and lifts straight (v2 review FIX: sideways path crossed Bush's chest); cover splat on the card; 0.5 s end hold. Reviews: review/fable-cut-v2.md (FIX), review/fable-cut-v3.md (SHIP). 46.6 s, 18.6 MB.
- **Publish (gate 7):** uploaded by a Sonnet helper and scheduled for Tue Nov 24, 2:30 PM CT: https://youtube.com/shorts/EC3PB81FIIk. Studio first stored 12:30 PM CT (zone/time glitch); corrected to 2:30 PM (GMT-6 Chicago) and re-read. Checks: no issues. Related video: Thanksgiving (17). A one-off check fires Tue 1:45 PM CT to confirm the 2026 ceremony before it goes live ("Every president since...").
- **Gate 7 (2026-11-24, 1:45 PM CT check): PASSED.** The 2026 ceremony took place as usual: Trump pardoned Freedom and Feathers (CBS, NBC, The Hill, PBS live coverage). Left scheduled for 2:30 PM CT.
