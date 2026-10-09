# Channel rules (working name: chain-channel)

Owner: Claude and its agent team. Matthew gives a human eye/ear at the gates below.
Started 2026-10-05.

## What the channel is
Vertical Shorts (60–75 s). Each one answers a real question about an everyday thing with a TRUE chain of cause and effect that lands somewhere nobody expects. Wonder plus dry wit. No morals.

## The groove check (Matthew's rule)
At every key decision (story, angle, hook, title, visual, music, name), ask: **"Is this what most AI would choose?"** If yes, choose something less obvious.
- Keep a running groove list (see `research/STORY_BANK.md`). Stories on it are out.
- The groove is wider than famous stories. Most everyday "why" questions already have near-zero-view AI Shorts. **Our edge is the far end of the chain**, so the script leads toward the surprising link fast.
- Cross-check: if ChatGPT and Claude both give the same story when asked cold, it's taken.

## The thread (Matthew's rule, 2026-10-06)
Every Short's last line teases the next Short, so the Shorts form one continuous thread. Break it only when we really have to.
- **Verify before teasing.** The next story is chosen and deep-verified (central link with two sources) before the current Short's voice is recorded. Short 02 teased purple glass before the research, and the research then found the popular explanation was a myth. The topic survived, but it might not have.
- **Write backward.** Pick the next story first, then plant its object on screen earlier in the current Short, so the tease feels earned (the window tax put glass on screen before the purple-glass tease).
- **Real bridges only.** The link is a shared thing (an object, material, place or person), never a pun. Best when it's also a shared idea (02 to 03: hand-made giving way to machines). Show the shared thing in the last scene, alongside the next story's object (02 ends on a bottle on a windowsill).
- **Each Short stands alone.** The thread lives only in the last line ("And why ...? That's another story."). Never require an earlier video.
- **Two ahead.** Keep two verified candidates for the next link, so a dud or a failed check doesn't break the thread.
- **Make it clickable.** When a Short goes live, set the previous Short's related video to it, and add it to the in-order playlist.
- **Track it** in `research/THREAD.md`.
- **Deliberate exceptions** (same look, feel and purpose): entry-point videos in a slightly different format that welcome new viewers into the thread, and special standalone Shorts. They sit outside the numbered thread.

## Accuracy
- Every claim in a script has a source in that video's fact table. Two independent reliable sources for the central link.
- Hedge causality: "part of the reason," "lined up with." Never "all because."
- If the popular version is a myth, say so or skip it.
- **True, not timid (Matthew, 2026-10-09).** Pick the most interesting phrasing that is still true. Hedge claims of cause ("partly because"), not every noun: "Why was margarine once dyed pink?" beats "Why did some states want margarine dyed pink?", and "Why is old glass purple?" doesn't claim all old glass is. A title or line only needs a hedge when a fair viewer would hear it as false without one.
- Sources go in every description.

## Openness about AI (Matthew approved 2026-10-05)
About section: researched and made with AI tools, fact-checked, sources in every description. Keep visuals stylized; never a photoreal face of a real person (this also keeps us outside YouTube's AI-label requirement).

## Script clarity check (every draft and every edit)
Added 2026-10-06 after the dime Short's v3 edit cut the line that explained the goblin, and nobody re-checked it.
A fresh reviewer that hasn't seen the research (a separate, cold model call) reads the final script once, as a listener, and must:
1. Explain the whole chain back, ending with the answer to the opening question.
2. For each thing the hook promises, quote the line that pays it off. Every hook item should be part of the answer, not a side tangent.
3. Name what every pronoun points to (it, that, they, he), especially right after a reveal. Rewrite any that could point two ways.
4. Flag any line that could be heard literally the wrong way, or that leaves a "wait, what?" on one listen.
5. Flag repeated punchlines and over-explaining.
If anything is shaky, rewrite and run the check again. Edits made after feedback go through the same check before audio is rendered.

## Written for the ear (Matthew, 2026-10-09)
Viewers hear the script once, at Darren's pace, with an accent. After Short 05's first voice:
- Each new point hooks onto the last one ("Florida's early oranges are often ripe but still green" after "where nights stay warm"), with a pause before a jump. Don't go from a fact to a teaser to a new place inside two sentences.
- No trade jargon ("packers"); use the word a viewer would use ("growers").
- If a word fights what the viewer expects ("fumes" when they expect heat), say why in the line: "Not from the heat, scientists found. From the fumes."
- Read it aloud for accidental rhymes and chimes ("Their case: it's only a trace").
- Matthew reviews the voice before drawings start; cold reads are done as a listener, not a reader.

## Look
- Black-and-white line art on warm paper, lots of empty space.
- One accent color appears as **real paint**. It splashes onto the thing that matters, then lifts off and jumps to the next thing as the scene changes. The paint carries the chain, so the narration never needs to say "chain."
- No on-screen text except the cover frame and captions.
- The paint is red lead #D9431E, the channel's signature.
- **The paint takes the color we call out (Matthew, 2026-10-07; made a firm rule 2026-10-08).** Whenever the narration, the title or the cover draws attention to a thing's color, the paint on that thing turns that color. Red paint on something we call purple reads as a contradiction. In the video it turns the color where it sits ("the glass turns purple" while it fills the bottle), holds it, then turns back to red before or while it jumps on. On the cover, the splash is the color the title or cover names (`cover.color` in layout.json; Short 03's cover went purple on 2026-10-08); the brand dot stays red. When the paint only marks a thing (the iron specks on "green"), it stays red. Stains, footprints and specks keep the color they had. Red stays the signature everywhere else. Colors: `PAINT_COLORS` in engine/plan.cjs (violet is manganese violet, a real manganese pigment; lavender; pale; wine; green); set per landing with `tint` in layout.json. Check before every cut and cover: each color the narration, title or cover calls out has the paint in that color.

## Voice
ElevenLabs v4, "Darren – Calm Irish Storyteller" (9TYDukkUVpJPDSIuv3ir), stability 0.5, no pitch change. Rushed lines get re-rendered, and slow-down is capped at 10%. To quicken a whole read slightly, re-run the voice tool with `--tempo` (Short 03: 1.05, pitch kept, same takes), then re-run words.py and shots.py. The render never edits voice.mp3.

## Sound
No music. The only sounds besides the voice are the film-reel projector at the end and the brand plink: one small water-drop sound as the red drop lands in the "a" (Matthew picked it, 2026-10-08). Both are ours or licensed (the plink is synthesized by tools/brand_plink.py into sfx/brand-splat.wav). Long thread videos end the same way.

## Hook and packaging
- Open on the question itself, asked directly. No "Have you ever wondered."
- Then name the unexpected other end within the first ~10 s (the promise).
- Titles ≤70 chars, no numbers or series names, never give away the payoff.
- Cover frame: 2–4 big words plus a brand mark in a fixed spot.
- **The title and cover never answer the question (Matthew, 2026-10-09).** Seen together, they should make the question bigger, not settle it. "Why are maraschino cherries so red? It's not the cherry" with "Bleached. Then dyed." gives the answer away, so a viewer can skip the Short. Better: a cover that adds a second puzzle (05: "Why are oranges orange? It went to the Supreme Court" with "Ripe. Still green.").

## Gates (Matthew)
1. Visual style
2. Channel name
3. First 3 finished Shorts
4. Then a quick look at each Short before upload, and an OK for each upload.
Matthew creates the YouTube channel itself (Claude doesn't create accounts).

## Cadence and success bar
Daily except Sunday at noon CT (Matthew, 2026-10-08; was 2–3 a week), craft over volume: a Short that isn't ready moves back a day. 90-day bar: one Short past 100K views, or 1,000 subscribers.
