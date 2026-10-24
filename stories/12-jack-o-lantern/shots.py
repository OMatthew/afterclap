#!/usr/bin/env python3
"""Short 12 shot list: writes shots.json with every time taken from words.json.

Scene starts and paint times are keyed by word (and which occurrence of it), never typed by
hand: hand-copied times ended up a word early in Short 01.
Usage: python3 stories/12-jack-o-lantern/shots.py
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
    'pumpkin-lit': 'A carved pumpkin with a simple face and a candle glowing inside, on a stone doorstep',
    'jack-devil': 'A grinning man in a flat cap pointing up at a small horned devil stuck in a tree',
    'jack-turnip': 'A lone man walking a night road, holding out a carved turnip with a glowing coal inside',
    'prank-boys': 'Two boys crouched behind a stone wall at night, one holding up a glowing lantern on a stick',
    'skull-turnip': 'A turnip carved like a skull, a candle flame showing through the eyes',
    'hedge-scare': 'A glowing carved turnip on a hedge; a man walking past jumps back, hat flying',
    'farm-boy': 'A boy carrying a huge pumpkin across a field of cut corn stalks',
    'old-book': 'An old children\'s book lying open, a little pumpkin picture on the left page',
    'scoop-hands': 'Two hands scooping seeds out of a pumpkin with a big spoon, the lid beside it',
    'night-carry': 'A boy walking into a dark field, holding a lit pumpkin lantern by a loop of string',
    'party': 'An old-fashioned party: a girl bobbing for apples, paper lanterns strung above',
    'harvest-porch': 'A porch corner with a bundle of corn stalks, pumpkins and gourds',
    'penny-journal': 'An old magazine page with a big printed picture of a man holding up a lantern',
    'lantern-man': 'A man in a long coat holding up an old metal lantern',
    'no-list': 'A lump of coal, a turnip and a pumpkin in a row, each crossed out',
    'marsh-light': 'Reeds and still water at night, a small glow floating above the water',
}
art = lambda *ids: [{'id': i, 'desc': A[i]} for i in ids]

S = []
S.append(('Why', 1, 'Why do we carve pumpkins on Halloween?', art('pumpkin-lit'),
          [('the candle glow', 'pumpkins', 1)], {}))
S.append(('The', 1, 'The usual answer is an Irish tale: a man named Jack tricked the devil,', art('jack-devil'),
          [('the tree', 'Irish', 1)], {'beat_note': 'No paint on the devil or Jack.'}))
S.append(('and', 1, 'and was left to wander the earth with a coal inside a carved turnip.', art('jack-turnip'),
          [('the road', 'wander', 1)], {}))
S.append(('But', 1, 'But the oldest carved lanterns we found were a prank, to scare people in the dark.', art('prank-boys'),
          [('the wall they hide behind', 'oldest', 1)], {}))
S.append(('In', 2, 'In England, a turnip cut like a skull, with a candle inside, already scared people by 1640.', art('skull-turnip'),
          [('the candle flame (not the skull)', 'candle', 1)], {'beat_note': 'Calm paint on the flame only.'}))
S.append(('Around', 1, 'Around 1800, boys in one county set them on hedges to frighten people walking past.', art('hedge-scare'),
          [('the hedge', 'boys', 1)], {}))
S.append(('In', 2, "In America, boys used pumpkins instead, and called them jack-o'-lanterns.", art('farm-boy', 'pumpkin-lit'),
          [('the carved pumpkin\'s candle', "jack-o'-lanterns", 1)], {}))
S.append(('A', 1, "A children's book from 1838 shows how to make one:", art('old-book'),
          [('the book cover', 'book', 1)], {}))
S.append(('dig', 1, 'dig it out,', art('scoop-hands'),
          [], {'beat_note': 'No paint on the cut pumpkin.'}))
S.append(('cut', 1, 'cut a face, put in a candle,', art('pumpkin-lit'),
          [('the candle', 'candle', 1)], {}))
S.append(('and', 1, 'and carry it into the dark.', art('night-carry'),
          [('a corn stalk', 'carry', 1)], {}))
S.append(('But', 1, 'But the book never mentions Halloween.', art('old-book'),
          [('the little pumpkin picture', 'Halloween', 1)], {}))
S.append(('So', 1, 'So how did a prank lantern become a Halloween one?', art('prank-boys'),
          [('the wall', 'prank', 1)], {'beat_note': 'The mid re-hook: back to the prank lantern.'}))
S.append(('Partly', 1, 'Partly, historians say, because after the Civil War, Americans made Halloween a party night.', art('party'),
          [('the paper lanterns', 'Partly', 1)], {}))
S.append(('They', 1, 'They decorated with the harvest, including pumpkins.', art('harvest-porch'),
          [('the biggest pumpkin', 'pumpkins', 1)], {}))
S.append(('As', 1, "As for Jack's tale, the oldest version we found was printed in Dublin in 1836.", art('penny-journal'),
          [('the printed lantern', 'printed', 1)], {}))
S.append(('It', 1, 'It has a lantern, but no coal, no turnip, no pumpkin.', art('lantern-man', 'no-list'),
          [('the lantern', 'lantern', 1)], {'beat_note': 'The X marks draw on coal, turnip, pumpkin.'}))
S.append(('The', 1, "The story explains a ghostly light that floats over marshes at night. People called that light a jack-o'-lantern", art('marsh-light'),
          [('the glow; it swells on "that light"', 'light', 1)], {}))
S.append(('long', 1, 'long before the name was given to a carved face.', art('pumpkin-lit'),
          [('the candle', 'carved', 1)], {}))

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
    'story': '12-jack-o-lantern',
    'question': 'Why do we carve pumpkins on Halloween?',
    'audio': 'voice.mp3', 'words': 'words.json', 'duration': dur,
    'notes': ('Narration v14. Times are seconds into voice.mp3, computed from words.json by shots.py. '
              'Each scene is one stop on the vertical paper strip. "paint" lists where the paint lands '
              'and the word it lands on.'),
    'scenes': [{k: s[k] for k in ('id', 'start', 'end', 'line', 'art', 'paint', 'beat_note') if k in s} for s in scenes],
}
with open(os.path.join(HERE, 'shots.json'), 'w') as fh:
    json.dump(out, fh, indent=2)
for s in scenes:
    print(f"{s['id']:>2} {s['start']:6.2f}-{s['end']:6.2f}  " + ', '.join(f"{p['word']}@{p['t']}" for p in s['paint']))
