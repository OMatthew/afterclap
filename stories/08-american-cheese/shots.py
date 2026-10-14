#!/usr/bin/env python3
"""Short 08 shot list: writes shots.json with every time taken from words.json.

Scene starts and paint times are keyed by word (and which occurrence of it), never typed by
hand: hand-copied times ended up a word early in Short 01.
Usage: python3 stories/08-american-cheese/shots.py
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
    'cheese-pan': "A square slice of cheese melting over a small pan (Short 07's last picture)",
    'cheese-wheel': 'A wheel of Swiss cheese with a wedge cut out (Short 07)',
    'ship': 'A 1910s steamship on simple waves, cheese wheels stacked on deck',
    'hay-pinch': 'Fingers sprinkling a pinch of powder over a wide open vat (Short 07): here, the melted cheese',
    'cheese-tin': 'A small round sealed tin with a portion of soft cheese beside it',
    'greasy-pan': 'A pan of melted cheese that has split: stringy clumps in a puddle of oil',
    'dye-tin': 'An open tin of white powder with a scoop (Short 05): here, the salt',
    'wrapped-slices': 'A stack of individually wrapped cheese slices, the top one half unwrapped',
    'patent-bottle': 'A patent document with a seal, and a small glass bottle (Short 06)',
}
art = lambda *ids: [{'id': i, 'desc': A[i]} for i in ids]

S = []
S.append(('Why', 1, 'Why does a slice of American cheese melt so smoothly?',
          art('cheese-pan'), [('the melting slice', 'melt', 1)], {'beat_note': "Opens on Short 07's last picture (the thread)."}))
S.append(('The', 1, 'The trick behind it was invented in Switzerland, more than a hundred years ago.', art('cheese-wheel'),
          [('a hole in the wheel', 'Switzerland', 1)], {}))
S.append(('Around', 1, 'Around 1911, a cheese company in Switzerland was shipping Swiss cheese overseas. On the long trip, the cheese could spoil.', art('ship'),
          [('the cheese wheels on deck', 'overseas', 1), ('the same cheese, spoiling', 'spoil', 1)], {}))
S.append(('So', 1, 'So they melted it down with a pinch of special salt', art('hay-pinch'),
          [('the pinch', 'pinch', 1)], {}))
S.append(('and', 1, 'and sealed it in tins. Now it could survive the trip.', art('cheese-tin'),
          [('the tin', 'tins', 1)], {}))
S.append(('Heat', 1, 'Heat most cheese, and the fat leaks out as grease.', art('greasy-pan'),
          [('the grease puddle', 'grease', 1)], {}))
S.append(('That', 1, 'That salt keeps the fat mixed in. So when you melt the cheese again, it stays smooth.', art('dye-tin', 'cheese-pan'),
          [('the salt', 'salt', 1), ('the smooth melting slice', 'smooth', 1)], {}))
S.append(('And', 1, "And that's what every slice of American cheese is: cheese that's already been melted once, with a salt like that.", art('wrapped-slices'),
          [('the top slice', 'slice', 1)], {}))
S.append(('In', 1, 'In 1921, an American patent used one of these salts, sodium phosphate, to keep canned cheese from separating. The patent also praised the salt as a mild laxative.', art('patent-bottle'),
          [('the patent seal', 'patent', 1), ('the bottle', 'laxative', 1)], {}))
S.append(('And', 1, 'And why do some slices say "cheese product" on the wrapper? That\'s another story.', art('wrapped-slices'),
          [('the wrapper', 'wrapper', 1)], {'beat_note': 'The tease: Short 09 is the "cheese product" label.'}))

scenes, cursor = [], 0.0
for k, (w0, n0, line, arts, paints, ex) in enumerate(S):
    t0 = 0.0 if k == 0 else at(w0, n0, after=cursor + 0.05)
    start = 0.0 if k == 0 else round(t0 - 0.12, 2)
    cursor = t0
    sc = {'id': k + 1, 'start': start, 'line': line, 'art': arts, 'paint': []}
    for on, word, n in paints:
        sc['paint'].append({'on': on, 'word': word, 't': at(word, n, after=t0)})
    if 'drains' in ex:   # per landing: None or (word, occurrence, start offset s, end offset s)
        for p, d in zip(sc['paint'], ex['drains']):
            if d:
                tw = at(d[0], d[1], after=t0)
                p['drain'] = [round(tw + d[2], 2), round(tw + d[3], 2)]
    if 'beat_note' in ex:
        sc['beat_note'] = ex['beat_note']
    scenes.append(sc)
dur = json.load(open(os.path.join(HERE, 'voice.json')))['duration_sec']
for a, b in zip(scenes, scenes[1:] + [None]):
    a['end'] = b['start'] if b else dur
    for p in a['paint']:
        assert a['start'] <= p['t'] < a['end'], (a['id'], p)

out = {
    'story': '08-american-cheese',
    'question': 'Why does a slice of American cheese melt so smoothly?',
    'audio': 'voice.mp3', 'words': 'words.json', 'duration': dur,
    'notes': ('Narration v4.1. Times are seconds into voice.mp3, computed from words.json by shots.py. '
              'Each scene is one stop on the vertical paper strip. "paint" lists where the paint lands '
              'and the word it lands on.'),
    'scenes': [{k: s[k] for k in ('id', 'start', 'end', 'line', 'art', 'paint', 'beat_note') if k in s} for s in scenes],
}
with open(os.path.join(HERE, 'shots.json'), 'w') as fh:
    json.dump(out, fh, indent=2)
for s in scenes:
    print(f"{s['id']:>2} {s['start']:6.2f}-{s['end']:6.2f}  " + ', '.join(f"{p['word']}@{p['t']}" for p in s['paint']))
