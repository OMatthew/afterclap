#!/usr/bin/env python3
"""Short 06 shot list: writes shots.json with every time taken from words.json.

Scene starts and paint times are keyed by word (and which occurrence of it), never typed by
hand: hand-copied times ended up a word early in Short 01.
Usage: python3 stories/06-margarine/shots.py
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
    'green-orange': "An orange with a stem and two leaves (Short 05's last picture)",
    'margarine-block': "A block of margarine on a plate, a corner sliced off, a butter knife (Short 05's last picture)",
    'butter-dye': 'A stick of butter on a dish beside a small dropper bottle',
    'patent-bottle': 'An old document with a wax seal and ribbon, a small corked bottle beside it',
    'cow-hay': 'A cow eating from a hay rack in winter, a milk pail by its legs',
    'butter-churn': 'An old wooden butter churn and a round pat of butter on a board',
    'law-book': 'A thick old book lying open, with a ribbon bookmark (Short 05)',
    'shop-counter': 'A shop counter with a crate of wrapped blocks; a hand pushes one away',
    'court-front': 'The front of a classical courthouse (Short 05)',
    'margarine-package': 'A paper-wrapped one-pound block with a tax stamp across the fold',
    'kneading-bag': 'Two hands squeezing a clear bag of pale margarine with one bead inside',
    'diner-plate': 'A plate with a triangular pat and a butter knife, a blank tent card beside it',
    'dairy-trio': 'A stick of butter, a wedge of Swiss cheese, a scoop of ice cream',
    'swiss-hay': 'A wedge of Swiss cheese with few holes, a few strands of hay in front',
}
art = lambda *ids: [{'id': i, 'desc': A[i]} for i in ids]

S = []  # (first word, occurrence after the previous scene, line, art ids, paint [(on, word, occurrence in scene)], extras)
S.append(('Why', 1, 'Why was margarine once dyed pink? So nobody would buy it.', art('green-orange', 'margarine-block'),
          [('the margarine block, turning pink', 'pink', 1)],
          {'beat_note': "Opens on Short 05's last picture (the thread): the paint turns pink on the block."}))
S.append(('The', 1, "The fight was over yellow, and butter's yellow often came from dye too.", art('butter-dye'),
          [('the butter, yellow', 'yellow', 1), ('the dropper bottle, yellow', 'dye', 1)], {}))
S.append(('Margarine', 1, "Margarine comes out nearly white. Its inventor's 1873 patent says to add the yellow dye that butter already used.", art('margarine-block', 'patent-bottle'),
          [('the wax seal on the patent', 'patent', 1), ('the little bottle, yellow', 'yellow', 1)],
          {'beat_note': 'The margarine block stays bare ink: nearly white.'}))
S.append(('In', 1, 'In winter, cows ate hay instead of grass, and butter came out paler. So dairies dyed it yellow.', art('cow-hay', 'butter-churn'),
          [('the hay', 'hay', 1), ('the pat of butter: pale, then yellow on "yellow"', 'paler', 1)], {}))
S.append(('still', 1, 'Butter makers still called yellow margarine a fake. In 1885, New Hampshire passed a law that margarine had to be pink. A few states copied it.', art('law-book', 'margarine-block'),
          [('the margarine block, yellow (on "fake")', 'fake', 1), ('the open law book', 'law', 1), ('the margarine block, pink', 'pink', 1)], {}))
S.append(('When', 1, 'When stores in one of those states got pink margarine, nobody would buy it.', art('shop-counter'),
          [('the pushed-away block, pink', 'pink', 1)], {}))
S.append(('In', 2, "In 1898, the Supreme Court ruled against New Hampshire's law. The Court said forcing a color that won't sell is really a ban.", art('court-front'),
          [('the courthouse roof', 'Court', 1), ('the whole roof, filled', 'forcing', 1)], {'drains': [None, ('ban', 1, 0.0, 0.7)]}))
S.append(('So', 1, 'So in 1902, Congress taxed yellow margarine instead, at forty times the rate on white.', art('margarine-package'),
          [('the wrapped margarine, yellow; it swells on "forty"', 'yellow', 1)], {}))
S.append(('To', 1, 'To avoid that tax, makers sold margarine white for decades, with a capsule of yellow dye that families mixed in at home.', art('kneading-bag'),
          [('the bead: red, then yellow on "yellow"; it swells through the bag on "mixed"', 'capsule', 1)], {}))
S.append(('The', 1, 'The tax ended in 1950. But one rule from that year is still US law. A restaurant serving yellow margarine has to label each piece, or cut it into a triangle.', art('diner-plate'),
          [('the blank tent card', 'rule', 1), ('the tent card again', 'label', 1), ('the triangle pat, yellow', 'triangle', 1)],
          {'drains': [None, None, ('triangle', 1, 0.8, 1.6)]}))
S.append(('As', 1, 'As for butter, under a 1938 US law, it can be dyed without saying so. The same goes for cheese and ice cream.', art('dairy-trio'),
          [('the butter, yellow', 'dyed', 1), ('the cheese wedge, red again', 'cheese', 1)], {}))
S.append(('And', 2, "And why does Swiss cheese have fewer holes now? That's another story.", art('margarine-block', 'swiss-hay'),
          [('the cheese, by its holes', 'holes', 1)],
          {'beat_note': 'The tease: Short 07 is Swiss cheese. Hay (the winter butter) lies in front of the wedge.'}))

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
    'story': '06-margarine',
    'question': 'Why was margarine once dyed pink?',
    'audio': 'voice.mp3', 'words': 'words.json', 'duration': dur,
    'notes': ('Narration v3.2. Times are seconds into voice.mp3, computed from words.json by shots.py. '
              'Each scene is one stop on the vertical paper strip. "paint" lists where the paint lands '
              'and the word it lands on.'),
    'scenes': [{k: s[k] for k in ('id', 'start', 'end', 'line', 'art', 'paint', 'beat_note') if k in s} for s in scenes],
}
with open(os.path.join(HERE, 'shots.json'), 'w') as fh:
    json.dump(out, fh, indent=2)
for s in scenes:
    print(f"{s['id']:>2} {s['start']:6.2f}-{s['end']:6.2f}  " + ', '.join(f"{p['word']}@{p['t']}" for p in s['paint']))
