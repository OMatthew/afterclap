#!/usr/bin/env python3
"""Short 11 shot list: writes shots.json with every time taken from words.json.

Scene starts and paint times are keyed by word (and which occurrence of it), never typed by
hand: hand-copied times ended up a word early in Short 01.
Usage: python3 stories/11-ragamuffin-day/shots.py
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
    'ragamuffin': "A kid in baggy grown-up clothes and a mask holding out a hat at a door with a paper turkey (Short 10's last picture)",
    'copycat': 'A small kid in a huge coat and top hat strutting behind a costumed grown man, copying his walk',
    'cop-kid': 'A policeman in a tall helmet wagging his finger at a small kid in an oversized coat and mask',
    'men-parade': 'Grown men in fancy costumes marching with a drum, one in a plumed hat on horseback',
    'big-clothes': 'Three kids in their fathers\' old clothes, sleeves past their hands, trousers rolled up, one in a huge floppy hat',
    'doorbell': 'A small hand pressing an old doorbell beside a front door',
    'hat-treats': 'An upturned old hat holding pennies, an apple and a few candies',
    'boys-banner': 'A line of boys marching in costume behind a long banner',
    'coat-hook': 'A big old coat and a top hat hanging on a wall hook',
    'candy-bucket': "A jack-o'-lantern bucket full of wrapped candy (Short 09)",
    'masked-kids': 'Four kids in paper masks at a front door, seen from behind (Short 10)',
    'window-frown': 'A grown-up frowning out through a lace curtain at a window',
    'big-balloon': 'A giant parade balloon floating above a street, held by ropes',
}
art = lambda *ids: [{'id': i, 'desc': A[i]} for i in ids]

S = []
S.append(('Why', 1, 'Why did New York kids once go door to door in costume on Thanksgiving?', art('ragamuffin'),
          [('the paper turkey', 'Thanksgiving', 1)], {'beat_note': "Opens on Short 10's last picture (the thread)."}))
S.append(('Because', 1, 'Because they were copying the grown-ups.', art('copycat'),
          [('the top hat', 'copying', 1)], {}))
S.append(('Then', 1, 'Then other grown-ups spent decades trying to stop the kids.', art('cop-kid'),
          [], {'beat_note': 'No paint on the people (red must not read as blood).'}))
S.append(('Back', 1, "Back in the 1800s, grown men's clubs paraded through New York in costume on Thanksgiving.", art('men-parade'),
          [('the drum', 'paraded', 1)], {}))
S.append(('So', 1, 'So kids copied them, in old clothes many sizes too large. They looked like ragamuffins, scruffy kids in rags. People called the day Ragamuffin Day.', art('big-clothes'),
          [('the floppy hat brim; it swells on "Ragamuffin"', 'large', 1)], {}))
S.append(('But', 1, "But the men gave up their parades. The kids didn't. They rang doorbells and asked, \"Anything for Thanksgiving?\"", art('men-parade', 'doorbell'),
          [('the doorbell button', 'doorbells', 1)], {}))
S.append(('Pennies', 1, 'Pennies, apples, candy.', art('hat-treats'),
          [('the apple', 'apples', 1)], {}))
S.append(('So', 1, 'So the grown-ups pushed back. A newspaper called the kids a nuisance.', art('window-frown'),
          [('the curtain', 'nuisance', 1)], {'beat_note': 'The same frowning grown-up comes back at "all over again".'}))
S.append(('Police', 1, 'Police were told to stop the begging.', art('cop-kid'),
          [], {}))
S.append(('A', 1, 'A boys\' club held a costume parade instead, with the slogan "American boys do not beg."', art('boys-banner'),
          [('the banner', 'slogan', 1)], {}))
S.append(('By', 1, 'By about 1940, Ragamuffin Day had faded.', art('coat-hook'),
          [('the coat', 'faded', 1)], {}))
S.append(('But', 1, "But the doorbells didn't stay quiet for long. Within ten years, a new custom reached the East Coast from the West.", art('doorbell'),
          [('the doorbell button', 'doorbells', 1)], {}))
S.append(('Kids', 1, 'Kids in costume, ringing doorbells for treats. Only now, on Halloween.', art('masked-kids', 'candy-bucket'),
          [('the door', 'ringing', 1), ('the bucket', 'Halloween', 1)], {}))
S.append(('And', 1, 'And some adults on the East Coast called it begging, all over again.', art('window-frown'),
          [('the curtain', 'begging', 1)], {}))
S.append(('why', 1, "And why does the Macy's parade have giant balloons? That's another story.", art('big-balloon'),
          [('the balloon', 'balloons', 1)], {'beat_note': "The tease: Short 12 is the Macy's balloons."}))

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
    'story': '11-ragamuffin-day',
    'question': 'Why did New York kids once go door to door in costume on Thanksgiving?',
    'audio': 'voice.mp3', 'words': 'words.json', 'duration': dur,
    'notes': ('Narration v3.4. Times are seconds into voice.mp3, computed from words.json by shots.py. '
              'Each scene is one stop on the vertical paper strip. "paint" lists where the paint lands '
              'and the word it lands on.'),
    'scenes': [{k: s[k] for k in ('id', 'start', 'end', 'line', 'art', 'paint', 'beat_note') if k in s} for s in scenes],
}
with open(os.path.join(HERE, 'shots.json'), 'w') as fh:
    json.dump(out, fh, indent=2)
for s in scenes:
    print(f"{s['id']:>2} {s['start']:6.2f}-{s['end']:6.2f}  " + ', '.join(f"{p['word']}@{p['t']}" for p in s['paint']))
