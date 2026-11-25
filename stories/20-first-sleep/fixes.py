#!/usr/bin/env python3
"""Short 20 fixes to the traced art. Run after trace.py, before inksvg.cjs (idempotent).
The skeleton tracer drops solid eye dots and pupils. This finds small, solid, roundish dark blobs in the
source PNG (1024 px) and puts them back as fills, so faces keep their eyes. Optional per-drawing boxes
limit where blobs are taken (faces only), so buttons, knobs and candle wicks are left alone.
Cut review (Fable, 2026-11-25): drop the sleeping mother's faceless head loop in bed-window (it read as a pillow lump and
contradicted "they had just woken"), the stray mouth-to-collar line in midnight-candle, and the solid ink blob at the top of
the door in midnight-hour. Removal is by box (strokes wholly inside it), so a re-trace keeps working.
"""
import json, os
import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
IDS = ['jane-court', 'bed-window', 'historian-desk', 'midnight-candle', 'midnight-hour', 'lamps-street',
       'dark-room', 'two-researchers']
# face boxes (source px, x0,y0,x1,y1); None = whole drawing
BOXES = {
    'jane-court': [(240, 260, 330, 310), (640, 290, 730, 335)],
    'bed-window': [(490, 360, 560, 410)],
    'historian-desk': [(440, 285, 560, 330)],
    'midnight-candle': [(340, 355, 430, 400), (545, 435, 600, 470)],
    'midnight-hour': [(180, 430, 225, 470), (430, 405, 470, 445), (570, 425, 620, 460), (840, 410, 885, 440)],
    'lamps-street': [(480, 515, 530, 545), (595, 540, 640, 565)],
    'dark-room': [(295, 470, 370, 505)],
    'two-researchers': [(300, 300, 390, 350), (670, 320, 760, 360)],
}


DROP = {   # strokes wholly inside these boxes (source px) are removed
    'bed-window': [(125, 475, 262, 548)],
    'midnight-candle': [(350, 475, 390, 605)],
}
DROP_FILLS = {'midnight-hour': [(900, 360, 940, 400)]}   # traced fills (not our eye dots) whose centre is in these boxes


def blobs(png, boxes):
    a = np.asarray(Image.open(png).convert('L').resize((1024, 1024))) < 110
    lab, n = ndimage.label(a)
    out = []
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        ys, xs = sl
        h, w = ys.stop - ys.start, xs.stop - xs.start
        area = int((lab[sl] == i).sum())
        if not (12 <= area <= 160 and 3 <= w <= 16 and 3 <= h <= 18): continue
        if area / (w * h) < 0.55 or max(w, h) / min(w, h) > 2.2: continue
        cy, cx = ndimage.center_of_mass(lab[sl] == i)
        cx, cy = cx + xs.start, cy + ys.start
        if boxes and not any(b[0] <= cx <= b[2] and b[1] <= cy <= b[3] for b in boxes): continue
        out.append((cx, cy, w / 2, h / 2))
    return out


for a in IDS:
    p = os.path.join(HERE, 'art', 'traced', a + '.json')
    d = json.load(open(p))
    x0, y0 = d['crop'][0], d['crop'][1]
    d['fills'] = [f for f in d.get('fills', []) if not f.get('fix')]
    for b in DROP.get(a, []):
        d['strokes'] = [st for st in d['strokes'] if not all(b[0] <= x + x0 <= b[2] and b[1] <= y + y0 <= b[3] for x, y in st['pts'])]
    for b in DROP_FILLS.get(a, []):
        d['fills'] = [f for f in d['fills'] if not (b[0] <= f['cx'] + x0 <= b[2] and b[1] <= f['cy'] + y0 <= b[3])]
    found = blobs(os.path.join(HERE, 'art', a + '.png'), BOXES.get(a))
    for cx, cy, rx, ry in found:
        d['fills'].append({'cx': round(cx - x0, 1), 'cy': round(cy - y0, 1), 'rx': round(max(rx, 3), 1),
                           'ry': round(max(ry, 3.5), 1), 'fix': True})
    json.dump(d, open(p, 'w'))
    print(f'{a:16} eye dots {len(found):2}  ' + ' '.join(f'({cx:.0f},{cy:.0f})' for cx, cy, *_ in found))
