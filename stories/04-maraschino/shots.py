#!/usr/bin/env python3
"""Short 04 shot list: writes shots.json with every time taken from words.json.

Scene starts and paint times are keyed by word (and which occurrence of it), never typed by
hand: hand-copied times ended up a word early in Short 01.
Usage: python3 stories/04-maraschino/shots.py
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
    'cherry-jar': 'An old glass jar of cherries beside a small medicine bottle (from Short 03)',
    'brine-barrel': 'An open barrel of cherries in brine',
    'straw-bottle': 'A straw-wrapped liqueur bottle',
    'marasca-sprig': 'A sprig of small dark cherries',
    'padlock-chain': 'A padlock on a chain (Prohibition)',
    'chemist-bench': 'A lab bench: an opened jar of cherries, test tubes, a magnifying glass',
    'cochineal': 'A prickly-pear pad with three cochineal bugs',
    'sealed-crate': 'A shipping crate tied with string and a wax seal',
    'label-pen': 'A blank label and a dip pen',
    'shopper-hand': 'A hand taking a jar of cherries from a store shelf',
    'dye-bottles': 'Two small dropper bottles',
    'green-orange': 'An orange with a stem and two leaves',
}
art = lambda *ids: [{'id': i, 'desc': A[i]} for i in ids]

S = []  # (first word, occurrence after the previous scene, line, art ids, paint [(on, word, occurrence in scene)], extras)
S.append(('Why', 1, 'Why are maraschino cherries so red? Because the cherry isn\'t. The red is dye. And for nearly thirty years, the government called them imitations. Then the dye became the definition.', art('cherry-jar'),
          [('fills one cherry', 'red', 1), ('fills it again', 'dye', 1)],
          {'drains': [('isn\'t', 1, 0.0, 0.6), ('definition', 1, 0.3, 0.95)],
           'beat_note': "Opens on Short 03's last picture: the thread. The paint is already falling in the first frame. It drains out on \"the cherry isn't\" and comes back on \"dye\"."}))
S.append(('A', 1, 'A brine preserves the cherries and bleaches them pale. Then they\'re dyed red and soaked in almond syrup.', art('brine-barrel'),
          [('the cherries in the brine', 'preserves', 1)], {'soak': ('syrup', 1)}))
S.append(('The', 2, "The name comes from Croatia's coast, where dark marasca cherries were kept in maraschino liqueur. You'll hear that Prohibition killed the liqueur, so America faked it. But the fake came first.", art('straw-bottle', 'marasca-sprig', 'padlock-chain'),
          [('the dark cherries', 'marasca', 1), ('the padlock', 'Prohibition', 1)], {'soak': ('first', 1)}))
S.append(('By', 1, 'By 1911, government chemists were opening jars of "maraschino cherries" and finding no liqueur at all. Just dyed cherries in almond syrup, some colored with insect dye. Shipments were seized, and sellers fined for false labels.', art('chemist-bench', 'cochineal', 'sealed-crate'),
          [('the opened jar', 'opening', 1), ('a test tube', 'liqueur', 1), ('the insects', 'insect', 1), ('the wax seal', 'seized', 1)], {}))
S.append(('In', 2, "In 1912, the rule became: call them imitation, or don't call them maraschino.", art('label-pen'),
          [('the blank label', 'imitation', 1)], {'soak': ('maraschino', 1)}))
S.append(('But', 1, 'But to shoppers, a maraschino cherry was the red one. So in 1940, the government accepted that: a sweet, almond-flavored cherry, dyed red. The fake won the name.', art('shopper-hand'),
          [('a jar on the shelf', 'red', 1), ('the jar in the hand', 'dyed', 1)], {'soak': ('name', 1)}))
S.append(('Most', 1, 'Most jarred maraschinos use Red 40 today. But some cherries shipped in 1910 were dyed with erythrosine, now Red No. 3. After more than a century in our food, it\'s banned from January 2027.', art('dye-bottles'),
          [('the taller bottle', '40', 1), ('fills the smaller bottle', '3', 1)], {'drains': [None, ('banned', 1, 0.0, 1.0)]}))
S.append(('And', 1, "And why can a ripe orange be green? That's another story.", art('cherry-jar', 'green-orange'),
          [('fills the orange', 'green', 1)], {'drains': [('story', 1, 8.0, 9.0)],
          'beat_note': 'The tease: Short 05 is oranges. The paint turns green on the orange and stays to the end.'}))

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
    'story': '04-maraschino',
    'question': "Why are maraschino cherries so red?",
    'audio': 'voice.mp3', 'words': 'words.json', 'duration': dur,
    'notes': ('Narration v2. Times are seconds into voice.mp3, computed from words.json by shots.py. '
              'Each scene is one stop on the vertical paper strip. "paint" lists where the red-lead paint lands '
              'and the word it lands on.'),
    'scenes': [{k: s[k] for k in ('id', 'start', 'end', 'line', 'art', 'paint', 'beat_note') if k in s} for s in scenes],
}
with open(os.path.join(HERE, 'shots.json'), 'w') as fh:
    json.dump(out, fh, indent=2)
for s in scenes:
    print(f"{s['id']:>2} {s['start']:6.2f}-{s['end']:6.2f}  " + ', '.join(f"{p['word']}@{p['t']}" for p in s['paint']))
