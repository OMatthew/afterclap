#!/usr/bin/env python3
"""Short 02 shot list: writes shots.json with every time taken from words.json.

Scene starts and paint times are keyed by word (and which occurrence of it), never typed by
hand: hand-copied times ended up a word early in Short 01.
Usage: python3 stories/02-ridges/shots.py
"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
words = json.load(open(os.path.join(HERE, 'words.json')))
norm = lambda t: re.sub(r"[^a-z0-9']", '', t.lower())


def at(word, n=1, after=0.0):
    """Start time of the nth occurrence of `word` at or after `after` seconds."""
    hits = [w for w in words if norm(w['w']) == norm(word) and w['s'] >= after - 1e-6]
    if len(hits) < n:
        raise SystemExit(f'"{word}" #{n} after {after}: not in words.json')
    return hits[n - 1]['s']


A = {
    'coins-edge': 'A dime and a nickel on edge, side by side: the dime ridged, the nickel smooth (true size ratio 17.9 : 21.2)',
    'house-bricked': 'A plain Georgian house front with two windows bricked up',
    'hammer-coin': 'Making a coin by hand: hammer, punch, coin on a little anvil',
    'lumpy-coin': 'An old hand-struck coin with a lumpy, uneven edge',
    'shears-clip': 'A hand with shears snipping a sliver off a coin',
    'ladle': 'A little melting ladle over a brazier, slivers inside',
    'rope': 'A coil of rope on a peg (no noose, no figure)',
    'balance': 'A balance: a clipped coin rides high against a full weight',
    'screw-press': 'A 1690s coin screw press',
    'milled-coin': 'A machine-made coin on edge, ridged, with one notch cut in',
    'chest': 'An open, empty Treasury strongbox',
    'house-open': 'The same house, all five windows open',
    'tax-man': 'A 1690s tax assessor from behind, ledger in hand, pointing up',
    'dime-large': 'A dime drawn large, its ridged edge showing (the copper core as a thin band)',
    'glass-panes': 'An old sash window with small panes of wavy old glass',
    'old-bottle': 'An old glass medicine bottle from around 1900, corked (Short 03 leads with old bottles)',
}
art = lambda *ids: [{'id': i, 'desc': A[i]} for i in ids]

S = []  # (first word, occurrence after the previous scene, line, art ids, paint [(on, word, occurrence in scene)], extras)
S.append(('Why', 1, "Why does a dime have ridges, but a nickel doesn't?", art('coins-edge'),
          [('the dime\'s ridges', 'ridges', 1)], {}))
S.append(('Those', 1, 'Those ridges, and some bricked-up windows in England, trace back to the same crime.', art('house-bricked'),
          [('a bricked-up window', 'bricked-up', 1)], {}))
S.append(('Silver', 1, 'Silver coins used to be worth their silver. They were hammered out by hand, with uneven edges,', art('hammer-coin', 'lumpy-coin'),
          [('the coin under the punch', 'silver', 2), ('the lumpy edge', 'uneven', 1)], {}))
S.append(('so', 1, 'so people snipped a little off and melted the clippings down.', art('shears-clip', 'ladle'),
          [('the sliver, as it comes off', 'off', 1), ('the ladle: the paint is the clippings', 'clippings', 1)],
          {'beat_note': 'The paint is the silver here: snipped off, then dropped into the ladle.'}))
S.append(('You', 1, 'You could hang for clipping. People clipped anyway.', art('rope'),
          [('the rope', 'hang', 1)], {'beat_note': 'Calm, a touch grim. No figure.'}))
S.append(('By', 1, "By the 1690s, England's silver coins were missing nearly half their silver.", art('balance'),
          [('the clipped coin in the high pan', 'half', 1)], {}))
S.append(('So', 1, 'So England called them in and struck new coins by machine, with ridged edges. Clip one of those, and anyone can tell.', art('screw-press', 'milled-coin'),
          [('the ridged edge', 'ridged', 1), ('the notch', 'tell', 1)], {}))
S.append(('For', 1, "For months, the old coins were taken back at full value, so their owners didn't lose out. That cost the government millions of pounds.", art('chest'),
          [('the chest, filling it; it drains on "cost"', 'full', 1)], {'drain_from': ('cost', 1), 'drain_to': ('pounds', 1)}))
S.append(('To', 1, 'To help pay for that, Parliament taxed houses by their windows. Windows were easy to count from the street.', art('house-open', 'tax-man'),
          [('an upstairs window', 'windows', 1), ('the next window along (counting)', 'count', 1)], {}))
S.append(('Some', 1, 'Some owners bricked windows up, to pay less tax. A few of those blank windows are still there.', art('house-bricked'),
          [('the bricked window', 'bricked', 1)], {'soak': ('still', 1), 'beat_note': 'Callback to scene 2: the same house.'}))
S.append(("America's", 1, "America's silver coins, dimes included, got ridges too. A nickel is mostly copper, never worth clipping, so it stayed smooth.", art('coins-edge'),
          [('the dime\'s ridges', 'dimes', 1), ('the nickel; it slides off on "smooth"', 'copper', 1)],
          {'slide': ('stayed', 1), 'beat_note': 'Callback to scene 1, now answered. The paint slips off the smooth nickel on "stayed smooth".'}))
S.append(('The', 1, 'The silver left the dime in 1965. The ridges stayed.', art('dime-large'),
          [('the dime, filling it; it drains out', 'silver', 1), ('the ridges, and stays', 'ridges', 1)],
          {'drain_from': ('dime', 1), 'drain_to': ('ridges', 1, -0.5), 'beat_note': 'Echoes Short 01 ("The silver left the dime in 1965. The size stayed.")'}))
S.append(('And', 1, "And why is some old glass purple? That's another story.", art('old-bottle'),
          [('the bottle', 'purple', 1)], {'beat_note': 'The tease: Short 03 is purple glass.'}))

scenes, cursor = [], 0.0
for k, (w0, n0, line, arts, paints, ex) in enumerate(S):
    # each scene starts at its first word, searched from the previous scene's start;
    # its paint words are searched from the scene's own start
    t0 = 0.0 if k == 0 else at(w0, n0, after=cursor + 0.05)
    start = 0.0 if k == 0 else round(t0 - 0.12, 2)
    cursor = t0
    sc = {'id': k + 1, 'start': start, 'line': line, 'art': arts, 'paint': []}
    for on, word, n in paints:
        sc['paint'].append({'on': on, 'word': word, 't': at(word, n, after=t0)})
    if 'drain_from' in ex:
        f, g = ex['drain_from'], ex['drain_to']   # (word, occurrence[, offset s])
        sc['paint'][0]['drain'] = [round(at(f[0], f[1], after=t0) + (f[2] if len(f) > 2 else 0), 2),
                                   round(at(g[0], g[1], after=t0) + (g[2] if len(g) > 2 else 0), 2)]
    if 'soak' in ex:
        sc['paint'][-1]['soak'] = at(*ex['soak'], after=t0)
    if 'slide' in ex:
        sc['paint'][-1]['slide_at'] = at(*ex['slide'], after=t0)
    if 'beat_note' in ex:
        sc['beat_note'] = ex['beat_note']
    scenes.append(sc)
dur = json.load(open(os.path.join(HERE, 'voice.json')))['duration_sec']
for a, b in zip(scenes, scenes[1:] + [None]):
    a['end'] = b['start'] if b else dur
    for p in a['paint']:
        assert a['start'] <= p['t'] < a['end'], (a['id'], p)

out = {
    'story': '02-ridges',
    'question': "Why does a dime have ridges, but a nickel doesn't?",
    'audio': 'voice.mp3', 'words': 'words.json', 'duration': dur,
    'notes': ('Narration v5. Times are seconds into voice.mp3, computed from words.json by shots.py. '
              'Each scene is one stop on the vertical paper strip. "paint" lists where the red-lead paint lands '
              'and the word it lands on. Real US coins: dime 17.9 mm, nickel 21.2 mm.'),
    'scenes': [{k: s[k] for k in ('id', 'start', 'end', 'line', 'art', 'paint', 'beat_note') if k in s} for s in scenes],
}
with open(os.path.join(HERE, 'shots.json'), 'w') as fh:
    json.dump(out, fh, indent=2)
for s in scenes:
    print(f"{s['id']:>2} {s['start']:6.2f}-{s['end']:6.2f}  " + ', '.join(f"{p['word']}@{p['t']}" for p in s['paint']))
