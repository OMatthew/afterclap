#!/usr/bin/env python3
"""Find stray sounds in a voice file: short bursts (< 0.25 s) with silence on both sides,
like a clipped "s" before a word (Short 10, voice v1). Usage: python3 tools/blips.py voice.mp3"""
import re, subprocess, sys
out = subprocess.run(['ffmpeg', '-i', sys.argv[1], '-af', 'silencedetect=n=-45dB:d=0.12', '-f', 'null', '-'],
                     capture_output=True, text=True).stderr
starts = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', out)]
ends = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', out)]
found = 0
for e, s in zip(ends, starts[1:]):          # sound runs from a silence end to the next silence start
    if s - e < 0.25:
        print(f'blip {e:.2f}-{s:.2f} s ({(s - e) * 1000:.0f} ms)'); found += 1
print('blips:', found)
