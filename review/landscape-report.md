Landscape support is implemented locally; browser validation and the requested commit are unfinished.

`style.frame: "landscape"` selects 1920×1080 scene coordinates and horizontal scrolling, reusing the existing easing, paper, ink, paint, downward drips and motion beats. Omit it for portrait. Landscape captions default to one centred 48 px line near the bottom, grouped at about 42 characters. `style.captions: false` hides them; SRT export remains on in both modes. `scene.chapter` in layout.json (including output from layout.py) or shots.json writes `<name>-chapters.txt`, starting at `0:00`. Landscape covers use the existing options and export at 1280×720.

Example layout options:

```json
{"style":{"frame":"landscape","captions":false},"scenes":[{"id":1,"chapter":"The flying cat"}]}
```

Keep the scene's existing art/paint entries. `--workers 1` is the default; 1–3 are accepted (`--par` remains an alias). Workers capture global frame times into lossless FFV1 chunks, join without re-encoding, then encode once. Encoders use at most two threads. Suggested command:

```sh
nice -n 10 ~/.local/bin/node engine/render.cjs stories/lf-demo --workers 3
```

`--from` / `--to` select a range without modifying narration; sidecar times follow that range. FFV1 scratch files can use substantial disk space.

The demo contains the first four Macy's scenes (23.5 s), landscape layouts, traced art, two chapters and SRT. Its voice.mp3 and words.json are byte-identical copies. `python3 stories/lf-demo/layout.py` rebuilds its layout/shots. Requested video, cover and four review JPGs are not generated yet.

Checks on macOS 26.5.2 arm64, Node 22.23.4, FFmpeg 9.0.2:

- `node review/landscape-check.cjs`: passed portrait plan equality against fd89c03, landscape geometry, caption/letter/nudge planning, sidecar ranges and unchanged demo audio/timestamps; page JavaScript parses.
- `node review/worker-check.cjs`: passed the real FFV1/join/encode pipeline using 35 fixed PNGs. Joined pixels equal all source pixels; final silent MP4 bytes match with 1 and 3 workers. This uses a browser stub, so it does not verify Chromium rendering or demo speed.
- Required portrait PNG/JPG comparison at 3, 14 and 30 s: **not run**. The before-change `--stills` attempt could not start Chromium. Plan equality does not establish pixel equality.
- Demo render time: **1 worker unavailable; 3 workers unavailable**. Both attempts fail before capture. No native visual review has been completed.

Chromium headless shell revision 1234 fails with `MachPortRendezvousServer ... Permission denied (1100)`; retries reproduce it. `nice` reports `setpriority: Operation not permitted`. Playwright was found in the installed Codex runtime; its browser cache was selected explicitly. The initial automatic retrace failed for missing scikit-image; existing traced JSON timestamps were refreshed without changing their contents. Failure logs are beside this report.

Git staging also fails: the sandbox cannot create `/Users/matthew/Desktop/Projects/afterclap/.git/worktrees/wt-landscape/index.lock`. No commit was made. No push, deploy, upload or publication occurred.

To finish: use a session allowed to launch Chromium, change process priority and write this worktree's Git metadata. Capture portrait baselines with the original engine from fd89c03, rerun current `--stills 3,14,30` and compare files; render the demo sequentially with 1 and 3 workers, record timings and compare outputs; run `--stills 1,9,15,21`, copy its 1280-wide JPGs to `stories/lf-demo/review/`, inspect the video/cover/stills, then commit locally. Rendering appearance, browser worker determinism, 10-minute performance and scratch-disk usage remain unverified.
