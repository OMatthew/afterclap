#!/usr/bin/env python3
"""Short 20 shot list: writes shots.json with every time taken from words.json.

Scene starts and paint times are keyed by word (and which occurrence of it), never typed by hand.
Ends on Jane with no paint: the drop leaves with the researchers' scene (an entry onto the candle crossed the clerk's face).
Opens on the strangest fact (a girl's 1690s court statement about 'first sleep') under the on-screen question,
with a face in the first scene. Ends back on Jane (reuses jane-court).
Usage: python3 stories/20-first-sleep/shots.py
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
    'jane-court': 'A girl in a 1690s dress and cap speaking; a clerk in a wig writes her words with a quill by a candle',
    'bed-window': 'A girl sitting up awake in a 1690s bed beside a sleeping woman, a crescent moon in the window',
    'historian-desk': 'A historian in glasses at a library desk, surprised, holding up an old handwritten page',
    'old-books': 'Old books on a table: a strapped diary, a thin play script, a big open doctor\'s book',
    'midnight-candle': 'A couple in nightcaps sitting up awake in bed, one holding a candle; a crescent moon in the window',
    'midnight-hour': 'Three vignettes: a woman praying by a bed, two people talking by a fire, a neighbour with a lantern at the door',
    'lamps-street': 'An 1800s street at evening with glowing gas lamps and a couple walking past',
    'dark-room': 'A young man lying awake on a bed in a bare room, a wall clock above',
    'two-researchers': 'Two researchers at a table of papers, one pointing, the other raising a hand to object',
}
art = lambda *ids: [{'id': i, 'desc': A[i]} for i in ids]

S = []
S.append(('In', 1, 'In the 1690s, a girl named Jane told a court about the night her mother was killed.', art('jane-court'), [('the paper', 'court', 1)]))
S.append(('She', 1, 'She said they had just woken from their "first sleep."', art('bed-window'), [('the window', 'first', 1)]))
S.append(('Centuries', 1, 'Centuries later, a historian read that, and stopped. First sleep? Then what was the second?', art('historian-desk'), [('the page', 'stopped', 1)]))
S.append(('He', 1, "He found both in diaries, plays and doctors' books. About two thousand times.", art('old-books'), [('the open book', 'thousand', 1)]))
S.append(('Many', 1, 'Many Europeans once slept twice a night, with an hour or so awake around midnight.', art('midnight-candle'), [('the window', 'midnight', 1)]))
S.append(('In', 1, 'In that hour, people prayed, talked, or visited the neighbours.', art('midnight-hour'), [('the lantern', 'neighbours', 1)]))
S.append(('But', 1, 'But as lamps got brighter, the two sleeps became one, and the phrase was forgotten.', art('lamps-street'), [('the lamp', 'brighter', 1)]))
S.append(('In', 1, 'In one experiment, volunteers kept in darkness fourteen hours a night began sleeping in two halves.', art('dark-room'), [('the clock', 'darkness', 1)]))
S.append(('Researchers', 1, 'Researchers still debate how common two sleeps were.', art('two-researchers'), [('the papers', 'debate', 1)]))
S.append(('Jane', 1, 'Jane never explained what "first sleep" meant. She didn\'t need to. Back then, everyone knew.', art('jane-court'), []))

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
    'story': '20-first-sleep',
    'question': "What was 'first sleep'?",
    'audio': 'voice.mp3', 'words': 'words.json', 'duration': dur,
    'notes': ('Narration v6 = v4 with "the 1690s" (Fable v4/v5 facts PASS, panel v4 PASS). Times are seconds into voice.mp3, computed from words.json by shots.py. '
              'Each scene is one stop on the vertical paper strip. "paint" lists where the paint lands and the word it lands on.'),
    'scenes': [{k: s[k] for k in ('id', 'start', 'end', 'line', 'art', 'paint') if k in s} for s in scenes],
}
with open(os.path.join(HERE, 'shots.json'), 'w') as fh:
    json.dump(out, fh, indent=2)
for s in scenes:
    print(f"{s['id']:>2} {s['start']:6.2f}-{s['end']:6.2f}  " + ', '.join(f"{p['word']}@{p['t']}" for p in s['paint']))
