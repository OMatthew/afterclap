#!/usr/bin/env python3
"""Short 05 shot list: writes shots.json with every time taken from words.json.

Scene starts and paint times are keyed by word (and which occurrence of it), never typed by
hand: hand-copied times ended up a word early in Short 01.
Usage: python3 stories/05-oranges/shots.py
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
    'cherry-jar': 'The cherry jar (Short 04 opened and closed on it)',
    'green-orange': 'An orange with a stem and two leaves (Short 04\'s last picture)',
    'dye-tin': 'An open tin of powdered dye with a scoop',
    'court-front': 'The front of a classical courthouse: steps, columns, a triangular roof',
    'orange-branch': 'An orange hanging from a branch under a crescent moon and two stars',
    'kerosene-stove': 'A small kerosene stove with fumes rising, beside a crate of oranges',
    'dye-tank': 'A shallow tank of dye with oranges floating, a ramp carrying them out',
    'test-flasks': 'A rack of test tubes and a half-full flask',
    'magnifier-peel': 'A magnifying glass over an orange: the peel up close, with a few tiny dots',
    'capitol': 'The Capitol (from Short 01)',
    'law-book': 'A thick old book lying open, with a ribbon bookmark',
    'dusty-bottle': 'A small old bottle with a cork and a cobweb',
    'margarine-block': 'A block of margarine on a plate, a corner sliced off, a butter knife',
}
art = lambda *ids: [{'id': i, 'desc': A[i]} for i in ids]

S = []  # (first word, occurrence after the previous scene, line, art ids, paint [(on, word, occurrence in scene)], extras)
S.append(('Why', 1, 'Why are oranges orange? One reason: cool nights.', art('cherry-jar', 'green-orange'),
          [('fills the orange: green on "oranges", orange on "orange"', 'oranges', 1)],
          {'drains': [('decades', 1, 0.0, 0.5)], 'beat_note': "Opens on Short 04's last picture (the thread). The paint lands on the green orange and turns orange."}))
S.append(('For', 1, 'For decades, some Florida oranges had another: dye. And that dye went all the way to the Supreme Court.', art('dye-tin', 'court-front'),
          [('the open dye tin', 'dye', 1), ('the courthouse', 'Court', 1)], {}))
S.append(('Cool', 1, "Cool nights break down the green in the peel. Where nights stay warm, a ripe orange can stay green, and Florida's early oranges often do.", art('orange-branch'),
          [('the orange under the moon, green', 'green', 1)], {'drains': [('do', 1, 0.25, 0.8)]}))
S.append(('In', 2, 'In the 1920s, growers put them in rooms warmed by kerosene stoves, and the green faded. Not from the heat, scientists found. From a gas in the fumes. That gas is still used today. But the oranges came out pale yellow.', art('kerosene-stove'),
          [('the stove', 'stoves', 1), ('the oranges in the crate, green', 'green', 1), ('the fumes', 'fumes', 1), ('the oranges, pale yellow', 'pale', 1)], {}))
S.append(('So', 1, 'So in the 1930s, Florida started dyeing them orange.', art('dye-tank'),
          [('the oranges in the tank: pale yellow, then orange on "orange"', '1930s', 1)], {}))
S.append(('In', 1, "In the 1950s, that dye failed new government tests, and it was banned. Florida's growers sued. It's just a trace on the peel, they said.", art('test-flasks', 'magnifier-peel'),
          [('the flask', 'tests', 1), ('a speck on the peel in the lens', 'trace', 1)],
          {'drains': [('banned', 1, 0.0, 0.6), None]}))
S.append(('In', 1, "In 1958, the Supreme Court ruled against them, unanimously. If a dye is found harmful, the law says, it can't be used at all. Not even a trace.", art('court-front'),
          [('the courthouse', 'Court', 1)], {'drains': [('trace', 1, 0.0, 0.7)]}))
S.append(('So', 1, 'So Congress allowed a different dye, temporarily, until it could write a new color law with safe limits. That law came in 1960, partly because of oranges.', art('capitol', 'law-book'),
          [('the Capitol dome', 'Congress', 1), ('the open book, turning orange on "oranges"', 'law', 1)], {}))
S.append(('And', 1, 'And that temporary dye? Growers used it for about sixty years, then quietly stopped. It was never banned. Now the FDA wants to retire it.', art('dusty-bottle'),
          [('the dusty bottle', 'dye', 1)], {'drains': [('stopped', 1, 0.0, 1.4)]}))
S.append(('And', 1, "And why was margarine once dyed pink? That's another story.", art('green-orange', 'margarine-block'),
          [('the margarine, turning pink', 'pink', 1)],
          {'beat_note': 'The tease: Short 06 is margarine. The paint turns pink on the block and stays to the end.'}))

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
    if 'drains' in ex:   # per landing: None or (word, occurrence, start offset s, end offset s)
        for p, d in zip(sc['paint'], ex['drains']):
            if d:
                tw = at(d[0], d[1], after=t0)
                p['drain'] = [round(tw + d[2], 2), round(tw + d[3], 2)]
    if 'soak' in ex:   # (word, occurrence[, offset s])
        k_ = ex['soak']
        sc['paint'][-1]['soak'] = round(at(k_[0], k_[1], after=t0) + (k_[2] if len(k_) > 2 else 0), 2)
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
    'story': '05-oranges',
    'question': "Why are oranges orange?",
    'audio': 'voice.mp3', 'words': 'words.json', 'duration': dur,
    'notes': ('Narration v6.1. Times are seconds into voice.mp3, computed from words.json by shots.py. '
              'Each scene is one stop on the vertical paper strip. "paint" lists where the red-lead paint lands '
              'and the word it lands on.'),
    'scenes': [{k: s[k] for k in ('id', 'start', 'end', 'line', 'art', 'paint', 'beat_note') if k in s} for s in scenes],
}
with open(os.path.join(HERE, 'shots.json'), 'w') as fh:
    json.dump(out, fh, indent=2)
for s in scenes:
    print(f"{s['id']:>2} {s['start']:6.2f}-{s['end']:6.2f}  " + ', '.join(f"{p['word']}@{p['t']}" for p in s['paint']))
