#!/usr/bin/env python3
"""Short 10 shot list: writes shots.json with every time taken from words.json.

Scene starts and paint times are keyed by word (and which occurrence of it), never typed by
hand: hand-copied times ended up a word early in Short 01.
Usage: python3 stories/10-trick-or-treat/shots.py
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
    'candy-bucket': "A jack-o'-lantern bucket full of wrapped candy (Short 09's last picture)",
    'wagon-roof': 'A farm wagon hauled up onto a barn roof: a Halloween prank',
    'masked-kids': 'Four kids in paper masks at a front door, seen from behind',
    'coin-hand': 'A hand from a doorway dropping a coin into a child\'s palm',
    'house-open': 'A plain two-storey house, front door shut (Short 02)',
    'apple-blade': 'An apple cut in half on a plate, a razor blade beside it',
    'old-bottle': 'A corked glass bottle (Short 02): the poison',
    'clippings': 'A file box of newspaper clippings with a magnifying glass',
    'candy-straws': 'Three paper candy straws',
    'popcorn-trash': 'A trash can full of homemade cookies and popcorn balls',
    'wrapped-candy': 'One candy bar in a sealed factory wrapper',
    'ragamuffin': 'A kid in baggy grown-up clothes and a mask holding out a hat at a door with a paper turkey',
}
art = lambda *ids: [{'id': i, 'desc': A[i]} for i in ids]

S = []
S.append(('Why', 1, 'Why do we say "trick or treat"?', art('candy-bucket'),
          [('the candy', 'treat', 1)], {'beat_note': "Opens on Short 09's last picture (the thread)."}))
S.append(('Because', 1, 'Because it started as a threat. A hundred years ago, Halloween meant pranks: gates carried off, wagons hauled onto roofs.', art('wagon-roof'),
          [('the barn loft', 'threat', 1), ('the wagon', 'wagons', 1)], {}))
S.append(('In', 1, 'In 1917, an Ontario newspaper printed the earliest known use of "tricks or treats." Gangs of kids called it out at the door.', art('masked-kids'),
          [('the door', 'tricks', 1)], {}))
S.append(('Pay', 1, 'Pay them off, the paper said, and your house was safe.', art('coin-hand', 'house-open'),
          [('the coin', 'Pay', 1), ('the front door', 'safe', 1)], {}))
S.append(('By', 1, 'By the 1970s, the fear flipped. Now the danger was the treat. Parents were warned that strangers hid poison and razor blades in it.', art('apple-blade', 'old-bottle'),
          [('the plate', 'treat', 1), ('the bottle', 'poison', 1)], {}))
S.append(('But', 1, "But a sociologist has tracked these reports all the way back to 1958. He hasn't found one child killed or badly hurt by a stranger's candy.", art('clippings'),
          [('the lens', 'reports', 1)], {}))
S.append(('most', 1, 'The most famous death, in 1974, was a boy poisoned by his own father.', art('candy-straws'),
          [('a straw', 'poisoned', 1)], {}))
S.append(('Still', 1, 'Still, homemade treats got thrown out.', art('popcorn-trash'),
          [('the cookies', 'homemade', 1)], {}))
S.append(('Only', 1, 'Only candy in a factory wrapper counted as safe.', art('wrapped-candy'),
          [('the wrapper', 'wrapper', 1)], {}))
S.append(('Kids', 1, 'Kids once got treats to stop a real threat. Now the treats come sealed, against a danger that was mostly a myth.', art('coin-hand', 'wrapped-candy'),
          [('the coin', 'threat', 1), ('the wrapper', 'sealed', 1)], {}))
S.append(('why', 1, 'And why did New York kids once go door to door in costume on Thanksgiving? That\'s another story.', art('ragamuffin'),
          [('the paper turkey', 'Thanksgiving', 1)], {'beat_note': 'The tease: Short 11 is Ragamuffin Day.'}))

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
    'story': '10-trick-or-treat',
    'question': 'Why do we say "trick or treat"?',
    'audio': 'voice.mp3', 'words': 'words.json', 'duration': dur,
    'notes': ('Narration v3. Times are seconds into voice.mp3, computed from words.json by shots.py. '
              'Each scene is one stop on the vertical paper strip. "paint" lists where the paint lands '
              'and the word it lands on.'),
    'scenes': [{k: s[k] for k in ('id', 'start', 'end', 'line', 'art', 'paint', 'beat_note') if k in s} for s in scenes],
}
with open(os.path.join(HERE, 'shots.json'), 'w') as fh:
    json.dump(out, fh, indent=2)
for s in scenes:
    print(f"{s['id']:>2} {s['start']:6.2f}-{s['end']:6.2f}  " + ', '.join(f"{p['word']}@{p['t']}" for p in s['paint']))
