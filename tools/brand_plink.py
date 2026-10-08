#!/usr/bin/env python3
"""The brand plink: one small water-drop sound as the red drop lands in the "a" at the end
(Matthew picked option A of three, 2026-10-08). Synthesized from scratch, so we own it.

Usage: python3 tools/brand_plink.py      -> writes sfx/brand-splat.wav
The renderer plays sfx/<cue type>.wav at each cue; reel.cjs emits the 'brand-splat' cue at the
drop's impact (gain 1, so this file's own level is the mix level: peak -15 dBFS, well under the voice).
"""
import os, wave
import numpy as np

SR = 48000
rng = np.random.default_rng(7)
t = lambda d: np.arange(int(d * SR)) / SR
env = lambda tt, a, tau: np.minimum(1, tt / a) * np.exp(-tt / tau)


def drop(f0=900, f1=1650, glide=0.045, tau=0.04):
    """A drop into liquid: a short sine whose pitch rises as the bubble closes, plus a tiny impact tick."""
    tt = t(0.35)
    f = f0 + (f1 - f0) * np.minimum(1, tt / glide) ** 0.7
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(tt, 0.0015, tau)
    tick = rng.standard_normal(len(tt)) * env(tt, 0.0002, 0.0012) * 0.25
    return x + np.convolve(tick, np.ones(6) / 6, 'same')


def room(x, dur=0.9, mix=0.10):
    """A small soft room: the dry sound plus a little of it through decaying, smoothed noise."""
    tt = t(dur)
    ir = rng.standard_normal(len(tt)) * np.exp(-tt / 0.22)
    ir = np.convolve(ir, np.ones(24) / 24, 'same')
    ir /= np.abs(ir).sum() / 6
    return x + mix * np.convolve(x, ir)[:len(x)]


x = np.zeros(int(1.2 * SR))
d = drop()
x[:len(d)] += d
x = room(x)
x = x / np.abs(x).max() * 10 ** (-15 / 20)
x[-int(0.15 * SR):] *= np.linspace(1, 0, int(0.15 * SR))
out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'sfx', 'brand-splat.wav')
st = (np.stack([x, x], 1) * 32767).astype('<i2')
with wave.open(out, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(st.tobytes())
print('wrote', out)
