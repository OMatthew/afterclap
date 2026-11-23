#!/usr/bin/env python3
"""Short 21 shot list: writes shots.json with every time taken from words.json.

Scene starts and paint times are keyed by word (and which occurrence of it), never typed by hand.
Hook test (2026-11-10): opens on the strangest fact under the on-screen question; the cat opens and closes it, so Shorts' loop lands back
on the opening image.
Usage: python3 stories/21-turkey-pardon/shots.py
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
    'podium-turkey': 'An older president at an outdoor lectern, glancing slyly at a live white turkey on a small table',
    'reporters': 'Four 1980s reporters crowding forward with microphones and notepads',
    'president-joke': 'The president laughing at his lectern, one hand open toward the turkey',
    'hand-over-turkey': 'A president holding his hand out over a live turkey on a table, the turkey looking up',
    'row-of-lecterns': 'A row of lecterns receding, each with a turkey on a small table',
    'law-book': 'A turkey peering at a thick open law book',
    'roast-dinner': 'A roast turkey on a platter beside a folded napkin',
    'straw-pen': 'A big white turkey resting in straw in a pen, a barn behind',
}
art = lambda *ids: [{'id': i, 'desc': A[i]} for i in ids]

S = []
S.append(('The', 1, 'The first time a president talked about pardoning a turkey, he was dodging a question about a scandal. So why does every president pardon one now?', art('podium-turkey'), [('the lectern', 'dodging', 1)]))
S.append(('It', 1, "It was 1987. Reporters asked Ronald Reagan if he'd pardon two of his former aides, caught up in a scandal called Iran-Contra. He wouldn't say.", art('reporters'), [('the notepad', 'asked', 1)]))
S.append(('Instead', 1, "Instead, he joked that he would have pardoned the Thanksgiving turkey he'd just been given.", art('president-joke'), [('the lectern', 'joked', 1)]))
S.append(('In', 1, 'In 1989, the next president, George Bush, went ahead and did it. He told the crowd: this turkey is pardoned.', art('hand-over-turkey'), [('the card', 'ahead', 1)]))
S.append(('Every', 1, 'Every president since has done the same.', art('row-of-lecterns'), [('the first lectern', 'since', 1)]))
S.append(('Legally', 1, "Legally, there's nothing to pardon. The turkey hasn't broken any law.", art('law-book'), [('the law book', 'law', 1)]))
S.append(('And', 1, 'And the birds are bred to be eaten,', art('roast-dinner'), [('the napkin', 'eaten', 1)]))
S.append(('so', 1, 'so many have lived only a year or two more.', art('straw-pen'), [('the barn', 'lived', 1)]))

scenes, cursor = [], 0.0
for k, (w0, n0, line, arts, paints) in enumerate(S):
    t0 = 0.0 if k == 0 else at(w0, n0, after=cursor + 0.05)
    start = 0.0 if k == 0 else round(t0 - 0.12, 2)
    cursor = t0
    sc = {'id': k + 1, 'start': start, 'line': line, 'art': arts, 'paint': []}
    for on, word, n in paints:
        sc['paint'].append({'on': on, 'word': word, 't': at(word, n, after=t0)})
    scenes.append(sc)
dur = json.load(open(os.path.join(HERE, 'voice.json')))['duration_sec']
dur = round(dur + 0.5, 3)   # hold the clean last drawing ~0.5 s after the last word before the loop (Fable cut review 2026-11-20)
for a, b in zip(scenes, scenes[1:] + [None]):
    a['end'] = b['start'] if b else dur
    for p in a['paint']:
        assert a['start'] <= p['t'] < a['end'], (a['id'], p)

out = {
    'story': '21-turkey-pardon',
    'question': "Why does the president pardon a turkey?",
    'audio': 'voice.mp3', 'words': 'words.json', 'duration': dur,
    'notes': ('Narration v5 (after Fable rechecks and three panel rounds). Times are seconds into voice.mp3, computed from words.json by shots.py. '
              'Each scene is one stop on the vertical paper strip. "paint" lists where the paint lands '
              'and the word it lands on.'),
    'scenes': [{k: s[k] for k in ('id', 'start', 'end', 'line', 'art', 'paint') if k in s} for s in scenes],
}
with open(os.path.join(HERE, 'shots.json'), 'w') as fh:
    json.dump(out, fh, indent=2)
for s in scenes:
    print(f"{s['id']:>2} {s['start']:6.2f}-{s['end']:6.2f}  " + ', '.join(f"{p['word']}@{p['t']}" for p in s['paint']))
