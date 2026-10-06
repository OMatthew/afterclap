#!/usr/bin/env python3
"""Check that every paint landing hits its keyed word in the rendered video.

For each landing, measures the red-lead area around the target in the frames around
the planned impact frame. The splat is many times the drop's area, so the first frame
where the area jumps is the real impact. Reports the offset in frames from the word.
  python3 tools/check_paint.py stories/01-dime [video.mp4]
"""
import json, os, subprocess, sys
import numpy as np

story = sys.argv[1]
out = os.path.join(story, 'out')
vid = sys.argv[2] if len(sys.argv) > 2 else next(os.path.join(out, f) for f in os.listdir(out) if f.endswith('-rough.mp4'))
lands = json.load(open(os.path.join(out, 'landings.json')))
W, H, FPS = 1080, 1920, 30


def frames(f0, n):
    cmd = ['ffmpeg', '-v', 'error', '-ss', f'{f0 / FPS:.4f}', '-i', vid, '-frames:v', str(n), '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-']
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)


worst = 0
print(f"{'word':14s} {'t':>7s} {'plan f':>6s} {'hit f':>6s} {'off':>4s}   area by frame (f-3..f+2)")
for L in lands:
    f = L['frame']
    fr = frames(f - 3, 6)
    r = int(L['R'] * 1.6)
    x0, x1 = max(0, L['x'] - r), min(W, L['x'] + r)
    y0, y1 = max(0, L['y'] - r), min(H, L['y'] + r)
    box = fr[:, y0:y1, x0:x1].astype(int)
    red = ((box[..., 0] > 150) & (box[..., 1] < 120) & (box[..., 2] < 90)).sum(axis=(1, 2))
    # impact = first frame whose red area exceeds 1.8x the drop's (previous frame) and a floor
    hit = None
    for i in range(1, len(red)):
        if red[i] > max(1.8 * red[i - 1], 0.6 * np.pi * (L['R'] * 0.5) ** 2):
            hit = f - 3 + i
            break
    word_f = L['t'] * FPS
    off = (hit - word_f) if hit is not None else float('nan')
    worst = max(worst, abs(off)) if hit is not None else 99
    print(f"{L['word']:14s} {L['t']:7.2f} {f:6d} {str(hit):>6s} {off:4.1f}   {list(red)}")
print(f"\nworst offset: {worst:.1f} frames (target <= 2)")
