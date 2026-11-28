#!/usr/bin/env python3
"""lf01 pre-trace prep: the Gemini drawings have thin, grey lines on a soft gradient,
which the tracer (INK_THRESHOLD 150) mostly drops at 1024 px. Flatten the paper,
stretch the ink to black and thicken lines to ~3 px. Reads art-src/<id>.png, writes art/<id>.png.
Usage: python3 stories/lf01-minefields/prep.py [ids...]"""
import sys, os, glob
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage as ndi
HERE = os.path.dirname(os.path.abspath(__file__))
ZOOM = {'drones', 'four-things', 'defence-belt', 'walk-lane', 'stopped-vehicle', 'plough-shells'}
ids = sys.argv[1:] or [os.path.basename(f)[:-4] for f in glob.glob(os.path.join(HERE, 'art-src', '*.png'))]
for i in ids:
    g = np.asarray(Image.open(os.path.join(HERE, 'art-src', i + '.png')).convert('L')).astype(float)
    bg = ndi.median_filter(g, size=31)            # paper tone, lines removed
    n = np.clip(g / np.maximum(bg, 1) * 255, 0, 255)
    ink = np.clip((248 - n) / 120, 0, 1)        # 0 paper .. 1 full ink
    ink = ndi.grey_dilation(ink, size=(3, 3))
    out = Image.fromarray((255 - ink * 255).astype(np.uint8))
    if i in ZOOM:   # small subject: crop to the ink and scale up so detail survives the tracer
        ys, xs = np.where(ink > 0.5); m = 30
        box = (max(0, xs.min() - m), max(0, ys.min() - m), min(g.shape[1], xs.max() + m), min(g.shape[0], ys.max() + m))
        out = out.crop(box); out = out.resize((1024, round(1024 * out.size[1] / out.size[0])), Image.LANCZOS)
    out.save(os.path.join(HERE, 'art', i + '.png'))
    print(i, 'ink px', int((ink > 0.5).sum()))
