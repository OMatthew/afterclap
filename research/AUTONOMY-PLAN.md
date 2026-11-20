# Afterclap: running autonomously (plan, 2026-11-20)

## Why now
Nothing shipped from Nov 13 to Nov 20: the planned Shorts (sliced bread, turkey pardon, Black Friday) were never made, because work only moved while a chat with Matthew was active. Autonomy means the pipeline moves on a schedule by itself, and quality is guarded by gates, not by Matthew watching.

## What we took from the reference videos (2026-11-20)
- "I Let Claude Run My YouTube Channel" (LanceypooAutomates): one Claude session, a style captured once as a reusable skill (reference analysis, then a 30 s test scene), one video a day rendered overnight, auto title/thumbnail/upload. Useful: capture the style once and reuse it; render unattended. Not useful: its QC is "trust it after the test scene", and its income claims are unverified and sell a paid community.
- The two niche videos (Learn with Lukas, Make Money Matt): little on pipelines. Useful point: YouTube's July 2026 clarification of the "inauthentic content" policy removes monetization from generic, repetitive or template-based channels, AI or not. A recognizable voice or character, a clear audience and real value are what survive.
- Notes and transcripts: ~/Movies/Afterclap/work/reference/autonomy-videos-2026-11-20.md

## The pipeline (state lives in the repo, so any session can pick it up)
`pipeline/QUEUE.md`: one row per story with its stage, owner, next action and due date. Stages and the gate each must pass:

| Stage | Who | Gate to move on |
|---|---|---|
| 1. Topic | lead | Scores on the topic sheet (present-day stakes, familiar anchor, surprise, visual, sources, not over-covered); no two similar topics in a row |
| 2. Research | lead + research subagent | Every claim has 2 independent sources (1 if primary/official), with dates, in `research/<id>.md`; time-sensitive claims flagged |
| 3. Script | lead | Fable fact check: no blocking issues. Viewer panel (5 personas, independent): median "still watching at the end" at least 60% for long-form, no line that 3+ panelists name as their exit point |
| 4. Voice | Mac | words.py match 0.95+, blips 0, duration in range (Shorts 45-60 s; long 8:00-11:00) |
| 5. Art | image helper | Every drawing viewed; tracer faces checked; no red near faces or mouths; no clip-art look |
| 6. Cut | lead | Stills checked; captions vs narration word for word; then a fresh Fable full-cut review: VERDICT SHIP |
| 7. Publish | fresh low-cost helper | Account and channel checks; title and cover don't answer the question; disclosure footer; time-sensitive line re-checked that day |
| 8. Learn | lead, weekly | Studio numbers into `research/ANALYTICS-*.md`; what to keep or change, decided on data from at least 5 uploads, not one |

A failed gate sends the story back one stage with the reason written down. Two fails at the same gate, or reviewers who disagree, goes to Matthew as a short written choice.

## Staying clearly "not mass-produced"
- Cadence capped: about 3 Shorts a week and 1 long video every 2-3 weeks. Quality first; never daily volume.
- Every story is original research with sources in the description; no story is a re-skin of another.
- Variety rule: openings, structures and paint moves rotate; a monthly Fable "template audit" of the last 10 uploads asks whether a viewer could tell they came from a template, and lists fixes.
- The constant parts are the brand (paper, ink, red paint, the narrator), not the story shape.
- Disclosure stays as it is: platform AI labels and the description footer.
- Kill switch: pause publishing and tell Matthew if YouTube flags anything, or if stayed-to-watch falls under 50% on 3 uploads in a row.

## How it runs
- One scheduled task (Mon/Wed/Fri morning) starts a fresh lead session. It reads this plan, `pipeline/QUEUE.md`, CHANNEL_RULES.md and the latest handoff, does the next actions, updates the queue, and ends with a 3-line note to Matthew only if something needs him. It needs the Mac on (voice, Chrome, Studio).
- A long chat like this one is no longer the lead. Matthew can open any fresh chat to talk; it reads the same files.
- Models: Fable for content judgement (facts, panels, full-cut reviews); Sonnet helpers for browser work and uploads; Haiku-level checks for mechanical diffs.

## What Matthew needs to decide (once)
1. Standing OK to download drawings from the image tool for Afterclap (today it's asked per Short).
2. Standing OK to publish Afterclap videos that pass every gate, with a weekly digest instead of a yes per upload (like Busyquiet's 2026-10-24 pre-approval). Deleting videos stays his.
3. OK for the one recurring scheduled task.
4. Image tool while ChatGPT usage is low: wait, or use Gemini for drawings.
