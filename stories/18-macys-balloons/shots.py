#!/usr/bin/env python3
"""Short 18 shot list: writes shots.json with every time taken from words.json.

Scene starts and paint times are keyed by word (and which occurrence of it), never typed by hand.
Hook test (2026-11-10): opens on the strangest fact under the on-screen question; the cat opens and closes it, so Shorts' loop lands back
on the opening image.
Usage: python3 stories/16-red-blue/shots.py
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
    'plane-cat': 'A 1930s biplane flying into a huge striped tabby cat balloon; the young pilot, goggles up, surprised',
    'letting-go': 'Parade handlers letting go of their ropes as a dragon balloon lifts off over rooftops',
    'prize-man': 'A grinning man hauling a saggy balloon with a prize tag',
    'roof-tug': 'Two men on a roof in a tug-of-war over a tiger balloon, tearing it',
    'pilot-warning': 'A man with a megaphone calling up to a biplane',
    'plane-spin': 'A biplane spinning down above rooftops, the deflated cat wrapped round its wing',
    'instructor': 'Two pilots in an open cockpit, the instructor gripping the stick',
    'folding': 'Two workers folding a deflated balloon on the ground',
    'handlers-cat': 'The striped cat balloon held down by a long line of handlers with ropes',
}
art = lambda *ids: [{'id': i, 'desc': A[i]} for i in ids]

S = []
S.append(('A', 1, 'A student pilot once flew her plane straight into a giant balloon cat. Why was a parade balloon up there at all?', art('plane-cat'),
          [('the cat balloon', 'straight', 1)]))
S.append(('Because', 1, "Because after its Thanksgiving parade, Macy's let the balloons go on purpose, as a prize hunt.", art('letting-go'),
          [('the dragon balloon', 'go', 1)]))
S.append(('In', 1, 'In 1928, bringing one back won you a hundred dollars.', art('prize-man'), [('the saggy balloon', 'won', 1)]))
S.append(('So', 1, 'So people fought over them. On a rooftop in Queens, a tug-of-war tore a tiger balloon to pieces.', art('roof-tug'),
          [('the tiger balloon', 'tiger', 1)]))
S.append(('Even', 1, "Even pilots joined the hunt. Macy's warned them: no prize for a balloon knocked down by a plane.", art('pilot-warning'),
          [('the megaphone', 'warned', 1)]))
S.append(('In', 1, 'In 1932, the student steered right into the cat.', art('plane-cat'), [('the cat balloon', 'cat', 1)]))
S.append(('It', 1, 'It wrapped around her wing, and the plane spun down toward the rooftops. Her instructor grabbed the controls and leveled off just above the roofs.', art('plane-spin'),
          [('the balloon on the wing', 'wing', 1), ('the plane, as it levels off', 'leveled', 1)]))   # the instructor drawing traced with blank faces: dropped
S.append(('By', 1, "By the next parade, Macy's had stopped letting the balloons go.", art('folding'), [('the folded balloon', 'stopped', 1)]))
S.append(('Today', 1, 'Today, they stay roped down the whole way. Nobody wants another flying cat.', art('handlers-cat'),
          [('the cat balloon', 'roped', 1)]))

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
for a, b in zip(scenes, scenes[1:] + [None]):
    a['end'] = b['start'] if b else dur
    for p in a['paint']:
        assert a['start'] <= p['t'] < a['end'], (a['id'], p)

out = {
    'story': '18-macys-balloons',
    'question': "Why did Macy's let its parade balloons fly away?",
    'audio': 'voice.mp3', 'words': 'words.json', 'duration': dur,
    'notes': ('Narration v3 (after the Fable pre-draw review). Times are seconds into voice.mp3, computed from words.json by shots.py. '
              'Each scene is one stop on the vertical paper strip. "paint" lists where the paint lands '
              'and the word it lands on.'),
    'scenes': [{k: s[k] for k in ('id', 'start', 'end', 'line', 'art', 'paint') if k in s} for s in scenes],
}
with open(os.path.join(HERE, 'shots.json'), 'w') as fh:
    json.dump(out, fh, indent=2)
for s in scenes:
    print(f"{s['id']:>2} {s['start']:6.2f}-{s['end']:6.2f}  " + ', '.join(f"{p['word']}@{p['t']}" for p in s['paint']))
