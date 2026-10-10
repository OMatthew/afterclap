#!/usr/bin/env python3
"""Short 07 shot list: writes shots.json with every time taken from words.json.

Scene starts and paint times are keyed by word (and which occurrence of it), never typed by
hand: hand-copied times ended up a word early in Short 01.
Usage: python3 stories/07-swiss-cheese/shots.py
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
    'margarine-block': "A block of margarine on a plate (Short 06's last picture)",
    'swiss-hay': "A wedge of Swiss cheese with few holes, hay in front (Short 06's last picture)",
    'court-front': 'The front of a classical courthouse (Shorts 05 and 06)',
    'cheese-wheel': 'A wheel of Swiss cheese with a wedge cut out, holes on the cut face',
    'hay-stem2': 'A hay stem drawn large, its cut end full of tiny tubes, and a broken-off speck',
    'cow-hay': 'A cow eating from a hay rack, an open milk pail by its legs (Short 06)',
    'milking-machine': 'Milking cups on hoses running into a closed, lidded steel can',
    'blind-wedge': "Scene 1's wedge with its holes and hay taken away",
    'law-book': 'A thick old book lying open (Shorts 05 and 06): the rulebook',
    'hay-pinch': 'Two fingers sprinkling a pinch of powder over an open vat of milk',
    'rubber-stamp': 'A hand pressing a rubber stamp onto a blank sheet',
    'deli-slicer2': 'A simple slicer; a wide holey slice hangs off it, ripped in two',
    'coin-pea2': 'A plain coin about twice the width of a pea',
    'two-slices2': 'Two slices: big holes and one medium; tiny holes and one medium of the same size',
    'cheese-pan': 'A square slice of cheese melting over a small pan',
}
art = lambda *ids: [{'id': i, 'desc': A[i]} for i in ids]

S = []  # (first word, occurrence after the previous scene, line, art ids, paint [(on, word, occurrence in scene)], extras)
S.append(('Why', 1, 'Why does Swiss cheese have fewer holes now? Because milking got too clean.', art('margarine-block', 'swiss-hay'),
          [('the cheese, by its holes', 'holes', 1)],
          {'beat_note': "Opens on Short 06's last picture (the thread)."}))
S.append(('And', 1, 'And Swiss cheesemakers had to take their own government to court to get the holes back.', art('court-front'),
          [('the courthouse roof', 'court', 1)], {}))
S.append(('The', 2, 'The holes are gas, from bacteria in the cheese. But a bubble needs a place to start.', art('cheese-wheel'),
          [('a hole, as the gas; it swells on "start"', 'gas', 1)], {}))
S.append(('Swiss', 1, 'Swiss scientists found it. Specks of hay. Hay is full of tiny tubes, so a speck can carry a little air. The gas gathers there, and a hole grows.', art('hay-stem2'),
          [('the broken-off speck', 'Specks', 1), ('one tube in the cut end; it swells into a hole on "gathers"', 'tubes', 1)], {}))
S.append(('Those', 1, 'Those specks used to fall into open milk buckets.', art('cow-hay'),
          [('the open pail', 'buckets', 1)], {}))
S.append(('But', 1, 'But from about 2005, Swiss farms started switching to closed milking machines. Fewer specks, fewer holes.', art('milking-machine', 'blind-wedge'),
          [('the closed can', 'closed', 1)],
          {'beat_note': "The blind wedge is scene 1's wedge with the holes gone, bare ink: no paint, no holes."}))
S.append(('Emmentaler', 1, 'Emmentaler, the original Swiss cheese, has an official rulebook.', art('law-book'),
          [('the open page', 'rulebook', 1)], {}))
S.append(('So', 1, "So its makers asked to add a pinch of ground hay to the milk. Switzerland's agriculture office said no, because it wasn't traditional.", art('hay-pinch', 'rubber-stamp'),
          [('the pinch', 'pinch', 1), ('the stamp, as ink', 'no', 1)], {}))
S.append(('In', 1, "In 2025, a Swiss court sided with the cheesemakers. The court said the hay powder isn't traditional, but the holes it brings back are.", art('court-front', 'cheese-wheel'),
          [('the courthouse roof', 'court', 1), ('a hole in the wheel; it swells on "back"', 'holes', 1)], {}))
S.append(('In', 1, 'In America, cheesemakers wanted smaller holes. Cheese with big holes can get torn up in slicing machines.', art('deli-slicer2'),
          [('the torn slice', 'torn', 1)], {}))
S.append(('In', 2, 'In 2001, the USDA changed its rules. Good Swiss cheese used to need holes about the size of a dime. Now they can be as small as a pea.', art('coin-pea2'),
          [('the coin', 'dime', 1), ('the pea', 'pea', 1)], {}))
S.append(('So', 1, "So today, Switzerland's smallest holes are about the size of America's biggest.", art('two-slices2'),
          [("the left slice's medium hole", 'smallest', 1), ("the right slice's medium hole, the same size", 'biggest', 1)], {}))
S.append(('And', 1, "And why does a slice of American cheese melt so smoothly? That's another story.", art('cheese-pan'),
          [('the melting slice', 'melt', 1)],
          {'beat_note': 'The tease: Short 08 is American cheese.'}))

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
    'story': '07-swiss-cheese',
    'question': 'Why does Swiss cheese have fewer holes now?',
    'audio': 'voice.mp3', 'words': 'words.json', 'duration': dur,
    'notes': ('Narration v2.3. Times are seconds into voice.mp3, computed from words.json by shots.py. '
              'Each scene is one stop on the vertical paper strip. "paint" lists where the paint lands '
              'and the word it lands on.'),
    'scenes': [{k: s[k] for k in ('id', 'start', 'end', 'line', 'art', 'paint', 'beat_note') if k in s} for s in scenes],
}
with open(os.path.join(HERE, 'shots.json'), 'w') as fh:
    json.dump(out, fh, indent=2)
for s in scenes:
    print(f"{s['id']:>2} {s['start']:6.2f}-{s['end']:6.2f}  " + ', '.join(f"{p['word']}@{p['t']}" for p in s['paint']))
