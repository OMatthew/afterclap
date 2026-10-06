#!/usr/bin/env python3
"""Afterclap brand mark: turn the channel avatar into the end-of-Short "a".

Reads brand/avatar-yt-800.jpg (the YouTube avatar, black ink "a" with red-lead paint in
its bowl) and writes brand/a-mark.json:
  glyph   filled outline of the "a" (SVG path, even-odd), in avatar pixels
  reveal  brush paths along the letter's spine, in writing order, for the brush-on reveal
  paint   where the paint lands (the bowl) and how big the splat is
  box     the glyph's bounding box, so the renderer can place and scale it
Usage: python3 tools/brand_mark.py [avatar.jpg] [out.json] [--order 0,3,1,2r]
  --order  writing order of the spine paths as found (longest first); "r" reverses one.
           For the current avatar: the bowl, then the hook into the stem, the stem, the exit tail.
"""
import json, math, os, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage import measure
from skimage.morphology import skeletonize

sys.path.insert(0, os.path.dirname(__file__))
import trace as T  # noqa: E402  (stroke graph helpers from the art trace step)


def main():
    args = [a for a in sys.argv[1:]]
    order = None
    if '--order' in args:
        i = args.index('--order'); order = args[i + 1].split(','); del args[i:i + 2]
    src = args[0] if len(args) > 0 else 'brand/avatar-yt-800.jpg'
    out = args[1] if len(args) > 1 else 'brand/a-mark.json'
    im = np.asarray(Image.open(src).convert('RGB')).astype(float)
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    black = (r < 90) & (g < 90) & (b < 90)
    black = ndi.binary_opening(ndi.binary_closing(black, iterations=2), iterations=1)
    lab, n = ndi.label(black)
    sizes = ndi.sum(black, lab, range(1, n + 1))
    glyph = lab == (int(np.argmax(sizes)) + 1)            # the letter only, no stray specks
    # outline: keep a little of the brushy edge (that roughness is the brand's look)
    sm = ndi.gaussian_filter(glyph.astype(float), 1.2)
    contours = measure.find_contours(sm, 0.5)
    d = ''
    for c in contours:
        if len(c) < 30:
            continue
        xy = T.rdp(np.c_[c[:, 1], c[:, 0]], 0.7)
        d += 'M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in xy) + 'Z '
    ys, xs = np.nonzero(glyph)
    box = [int(xs.min()), int(ys.min()), int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1)]

    # the bowl (counter): where the paint lands
    filled = ndi.binary_fill_holes(glyph)
    hole = filled & ~glyph
    hl, hn = ndi.label(hole)
    hs = ndi.sum(hole, hl, range(1, hn + 1))
    bowl = hl == (int(np.argmax(hs)) + 1)
    by, bx = ndi.center_of_mass(bowl)
    red = (r > 150) & (g < 110) & (b < 90)
    ry, rx = ndi.center_of_mass(red)
    paint = {'x': round(float(rx), 1), 'y': round(float(ry), 1),
             'R': round(math.sqrt(red.sum() / math.pi) * 0.92, 1),
             'bowl': [round(float(bx), 1), round(float(by), 1), round(math.sqrt(bowl.sum() / math.pi), 1)]}

    # spine for the brush reveal: skeleton strokes, longest first (the bowl, then the stem and tail)
    sk = skeletonize(glyph)
    nodes, edges = T.skeleton_graph(sk)
    strokes = T.prune_and_assemble(nodes, edges)
    rev = []
    for s in strokes:
        xy = T.smooth(T.resample(s['xy'], 3.0), 4.0, s['closed'])
        L = T.plen(xy)
        if L < 60:
            continue
        # the italic "a" is written from its top right: start each spine there
        if not s['closed'] and xy[0][1] > xy[-1][1]:
            xy = xy[::-1]
        rev.append({'pts': [[round(float(x), 1), round(float(y), 1)] for x, y in T.rdp(xy, 1.0)], 'len': round(L, 1), 'closed': bool(s['closed'])})
    rev.sort(key=lambda s: -s['len'])
    if order:
        picked = []
        for tok in order:
            k = int(tok.rstrip('r')); p = dict(rev[k])
            if tok.endswith('r'): p['pts'] = p['pts'][::-1]
            picked.append(p)
        rev = picked
    dist = ndi.distance_transform_edt(glyph)
    width = float(2 * dist[sk].max()) + 16

    res = {'src': os.path.basename(src), 'size': list(glyph.shape[::-1]), 'box': box, 'glyph': d.strip(),
           'reveal': rev, 'brush': round(width, 1), 'paint': paint, 'ink': '#1C1815'}
    with open(out, 'w') as fh:
        json.dump(res, fh, separators=(',', ':'))
    print(f'mark: box {box}, {len(rev)} brush paths (brush {width:.0f}px), paint at ({rx:.0f},{ry:.0f}) R {paint["R"]}')


if __name__ == '__main__':
    main()
