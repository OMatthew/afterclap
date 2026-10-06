# Notes for agents working in this repo

- **What this is:** Afterclap (@afterclapstories), a YouTube Shorts channel. Vertical Shorts, 60–75 s. Each one answers a real everyday question with a true, surprising chain of cause and effect. The channel says openly that it's made with AI tools. Every claim is fact-checked, with sources in the description.
- **Groove check (Matthew's rule):** at every key decision, ask "Is this what most AI would choose?" If yes, choose something less obvious. This applies to visuals, captions, motion and sound as much as to stories.
- **Look:** read CHANNEL_RULES.md and reference/motion-test/. Black ink line art on warm paper, one long vertical paper strip, and one accent: red-lead paint #D9431E that behaves like real paint and jumps from scene to scene.
- **Voice:** made outside this repo (ElevenLabs v4, "Darren"). Each story arrives with voice.mp3 and words.json (word timestamps). Never re-time or edit the narration audio.
- **Rendering:** deterministic, frame by frame, with Playwright Chromium (usually preinstalled under /opt/pw-browsers, so don't run `playwright install`) and ffmpeg (H.264 yuv420p, AAC).
- **Big binaries:** mp4s up to about 20 MB each are fine to commit for review. Keep stills as JPG.
- **Quality bar:** calm, readable and charming beats feature count. Render stills and look at them before calling anything done.
- **Roles:** the project lead is Claude (Matthew's main Cowork session), which reviews and merges. Matthew gives the final yes or no on taste.
