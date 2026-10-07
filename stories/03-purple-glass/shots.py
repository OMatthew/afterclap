#!/usr/bin/env python3
"""Short 03 shot list: writes shots.json with every time taken from words.json.

Scene starts and paint times are keyed by word (and which occurrence of it), never typed by
hand: hand-copied times ended up a word early in Short 01.
Usage: python3 stories/03-purple-glass/shots.py
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
    'glass-panes': 'An old sash window (from Short 02)',
    'old-bottle': 'An old medicine bottle on the windowsill (from Short 02)',
    'owens-machine': 'An early 1900s automatic bottle machine beside an open-topped furnace tank',
    'open-tank': 'A long, low open tank of molten glass; a machine arm dips in',
    'carry-in-boy': 'A boy of about ten (c. 1900) from behind, carrying hot bottles on a long fork',
    'sand-scoop': 'A heap of sand with a scoop; a few dark specks (iron)',
    'glass-pot': "A glassmaker's clay pot; a hand sprinkles a little powder in",
    'soap-bar': 'A plain bar of soap with a few bubbles',
    'sun-bottle': 'An old bottle on a shelf in the sun',
    'half-buried': 'An old bottle half buried in the ground (cross-section)',
    'ww1-helmet': 'A World War One steel helmet',
    'glassblower': 'A glassblower from the side, blowing a bubble of glass',
    'boy-door': 'The same boy walking out of a factory door into daylight',
    'cherry-jar': 'An old glass jar of cherries beside an old medicine bottle (bridge to Short 04)',
}
art = lambda *ids: [{'id': i, 'desc': A[i]} for i in ids]

S = []  # (first word, occurrence after the previous scene, line, art ids, paint [(on, word, occurrence in scene)], extras)
S.append(('Why', 1, 'Why is some old glass purple? It started out clear. Sunlight turned it purple.', art('glass-panes', 'old-bottle'),
          [('fills the bottle on the windowsill', 'purple', 1), ('back onto the bottle', 'purple', 2)],
          {'drain_from': ('started', 1, 0.0), 'drain_to': ('clear', 1, 0.45), 'soak': ('purple', 2, 0.55),
           'beat_note': "Opens on Short 02's last picture: the thread. The paint drains out on 'started out clear' and comes back on the second 'purple'."}))
S.append(('Newer', 1, "Newer bottles don't, mostly because of a machine that helped get kids out of bottle factories.", art('owens-machine', 'carry-in-boy'),
          [('the machine', 'machine', 1), ('the boy', 'kids', 1)], {}))
S.append(('Iron', 1, 'Iron in sand tints glass green.', art('sand-scoop'),
          [('the iron specks in the sand', 'green', 1)], {}))
S.append(('So', 1, "So glassmakers added a little manganese. Its faint pink cancels the green. They called it glassmaker's soap.", art('glass-pot', 'soap-bar'),
          [('the pinch of powder', 'manganese', 1), ('the soap', 'soap', 1)], {}))
S.append(('But', 1, 'But sunlight slowly changes manganese. Over months and years, the glass can turn lavender, then purple.', art('sun-bottle'),
          [('the bottle in the sun', 'lavender', 1)], {'soak': ('purple', 1)}))
S.append(('A', 1, 'A half-buried bottle turns purple only where the sun could reach it.', art('half-buried'),
          [('fills only the part above the ground', 'purple', 1)], {'drain_from': ('reach', 1, 0.2), 'drain_to': ('it', 1, 0.9)}))
S.append(('Why', 1, 'Why did the purple stop? World War One made manganese scarce.', art('ww1-helmet'),
          [('the helmet', 'scarce', 1)], {}))
S.append(('But', 1, 'But mostly, it was machines. In 1903, Michael Owens got the first fully automatic bottle machine working.', art('owens-machine'),
          [('the machine', 'machines', 1), ('the finished bottles', 'working', 1)], {}))
S.append(('Machines', 2, 'Machines drew their glass straight from huge open tanks, where manganese was hard to control.', art('open-tank'),
          [('fills the open pool of glass', 'tanks', 1)], {'drain_from': ('control', 1, 0.0), 'drain_to': ('control', 1, 0.75)}))
S.append(('Most', 1, 'Most glassmakers switched to selenium. Selenium glass can age to a faint straw color, not purple.', art('glass-pot'),
          [('the pinch of powder', 'selenium', 1)], {}))
S.append(("That's", 1, "That's why purple glass usually means it was made before about 1920, when most bottles were still blown by hand.", art('glassblower'),
          [('the bubble of glass', 'blown', 1)], {}))
S.append(('Owens', 1, 'Owens had been one of those factory kids. He started at ten, shoveling coal and carrying hot bottles.', art('carry-in-boy'),
          [('the hot bottles', 'hot', 1)], {}))
S.append(('His', 1, "His machine took over much of the kids' work, and helped end child labor in bottle factories.", art('owens-machine', 'boy-door'),
          [('the machine', 'work', 1), ('the boy walking out', 'end', 1)], {'soak': ('factories', 1)}))
S.append(('And', 2, "And why are maraschino cherries so red? That's another story.", art('cherry-jar'),
          [('the cherries', 'red', 1)], {'soak': ('story', 1), 'beat_note': 'The tease: Short 04 is maraschino cherries. Old glass beside a jar of cherries: color hiding color.'}))

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
    'story': '03-purple-glass',
    'question': "Why is some old glass purple?",
    'audio': 'voice.mp3', 'words': 'words.json', 'duration': dur,
    'notes': ('Narration v5. Times are seconds into voice.mp3, computed from words.json by shots.py. '
              'Each scene is one stop on the vertical paper strip. "paint" lists where the red-lead paint lands '
              'and the word it lands on.'),
    'scenes': [{k: s[k] for k in ('id', 'start', 'end', 'line', 'art', 'paint', 'beat_note') if k in s} for s in scenes],
}
with open(os.path.join(HERE, 'shots.json'), 'w') as fh:
    json.dump(out, fh, indent=2)
for s in scenes:
    print(f"{s['id']:>2} {s['start']:6.2f}-{s['end']:6.2f}  " + ', '.join(f"{p['word']}@{p['t']}" for p in s['paint']))
