#!/usr/bin/env python3
"""Short 23 shot list: writes shots.json with every time taken from words.json.

Scene starts and paint times are keyed by word (and which occurrence of it), never typed by hand.
Hook test (2026-11-10): opens on the strangest fact (ships told to watch the sky for a hippo) under the on-screen question,
with a face in the first scene. Sequel to 18 (Macy's balloons), but stands alone.
Usage: python3 stories/23-blue-hippo/shots.py
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
    'liner-lookout': 'A 1930s ocean-liner officer at the rail, binoculars raised to the sky; a lifebuoy on the rail',
    'letting-go': 'Parade handlers opening their hands as a dragon balloon lifts off over rooftops (from 18)',
    'prize-man': 'A grinning man hauling a saggy balloon over his shoulder, a prize tag on it (from 18)',
    'ferry-tiger': 'Two ferry crewmen hauling a soggy striped balloon out of the river with a boat hook',
    'cat-wire': 'A saggy striped cat balloon caught on power lines between two poles, a wisp of smoke',
    'empire-hippo': 'A round hippo balloon floating past the top of the Empire State Building',
    'radio-room': "A 1930s ship's radio operator in headphones at a telegraph key, a porthole behind",
    'phone-caller': 'A grinning man on a candlestick telephone, finger raised',
    'handlers-hippo': 'The hippo balloon over a city street, held down by a line of handlers with ropes',
}
art = lambda *ids: [{'id': i, 'desc': A[i]} for i in ids]

S = []
S.append(('In', 1, 'In 1931, a department store asked ships at sea to watch the sky for a blue hippopotamus.', art('liner-lookout'), [('the lifebuoy', 'sea', 1)]))
S.append(('Back', 1, "Back then, Macy's ended its Thanksgiving parade by letting the giant balloons go.", art('letting-go'), [('the dragon', 'letting', 1)]))
S.append(('Bring', 1, 'Bring one back, and you won a prize.', art('prize-man'), [('the bag', 'back', 1)]))
S.append(('So', 1, 'So the city chased them. A ferry crew fished the tiger balloon out of the East River.', art('ferry-tiger'), [('the ferry side', 'tiger', 1)]))
S.append(('The', 4, 'The cat drifted to New Jersey, hit a power line, and burned.', art('cat-wire'), [('the pole', 'line', 1)]))
S.append(('But', 1, 'But the blue hippo floated past the brand-new Empire State Building, and kept going.', art('empire-hippo'), [('the hippo', 'hippo', 1)]))
S.append(('So', 1, "So Macy's radioed the ocean liners, and made the reward four times bigger.", art('radio-room'), [('the radio set', 'radioed', 1)]))
S.append(('People', 1, 'People phoned in, saying they had found the hippo. Nobody ever brought it back.', art('phone-caller'), [('the phone base', 'saying', 1)]))
S.append(('This', 1, "This year, in its hundredth parade, Macy's is flying a blue hippo again. This time, they're holding on to it.", art('handlers-hippo'), [('the hippo', 'blue', 1)]))

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
dur = round(dur + 0.5, 3)   # hold the clean last drawing ~0.5 s after the last word
for a, b in zip(scenes, scenes[1:] + [None]):
    a['end'] = b['start'] if b else dur
    for p in a['paint']:
        assert a['start'] <= p['t'] < a['end'], (a['id'], p)

out = {
    'story': '23-blue-hippo',
    'question': "Why did Macy's ask ships to look for a blue hippo?",
    'audio': 'voice.mp3', 'words': 'words.json', 'duration': dur,
    'notes': ('Narration v3 (Fable fact check PASS, panel round 2). Times are seconds into voice.mp3, computed from words.json by shots.py. '
              'Each scene is one stop on the vertical paper strip. "paint" lists where the paint lands and the word it lands on.'),
    'scenes': [{k: s[k] for k in ('id', 'start', 'end', 'line', 'art', 'paint') if k in s} for s in scenes],
}
with open(os.path.join(HERE, 'shots.json'), 'w') as fh:
    json.dump(out, fh, indent=2)
for s in scenes:
    print(f"{s['id']:>2} {s['start']:6.2f}-{s['end']:6.2f}  " + ', '.join(f"{p['word']}@{p['t']}" for p in s['paint']))
