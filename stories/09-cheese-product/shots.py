#!/usr/bin/env python3
"""Short 09 shot list: writes shots.json with every time taken from words.json.

Scene starts and paint times are keyed by word (and which occurrence of it), never typed by
hand: hand-copied times ended up a word early in Short 01.
Usage: python3 stories/09-cheese-product/shots.py
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
    'wrapped-slices': "A stack of individually wrapped cheese slices, the top one half unwrapped (Short 08's last picture)",
    'dye-tin': 'An open tin of white powder with a scoop: the milk protein powder',
    'cow-hay': 'A cow at a hay rack with a milk pail: the dairy farmers',
    'law-book': 'A thick old book lying open: the rules',
    'dairy-trio': 'Butter, a wedge of cheese, a bowl of cream: the allowed dairy ingredients',
    'ship': 'A steamship on simple waves (Short 08): from overseas',
    'rubber-stamp': 'A hand pressing a rubber stamp onto a sheet: the FDA',
    'label-pen': 'A pen on a blank label: the new name',
    'candy-bucket': "A jack-o'-lantern bucket full of wrapped candy",
}
art = lambda *ids: [{'id': i, 'desc': A[i]} for i in ids]

S = []
S.append(('Why', 1, 'Why do some cheese slices say "cheese product" on the wrapper?', art('wrapped-slices'),
          [('the wrapper flap', 'wrapper', 1)], {'beat_note': "Opens on Short 08's last picture (the thread)."}))
S.append(('Because', 1, 'Because of a powder from overseas, some angry dairy farmers, and the FDA.', art('dye-tin', 'cow-hay'),
          [('the powder', 'powder', 1), ('the milk pail', 'farmers', 1)], {}))
S.append(('In', 1, 'In America, some food names come with a recipe set by law.', art('law-book'),
          [('the open page', 'law', 1)], {}))
S.append(('To', 1, 'To be called "cheese food," a product can only use cheese plus things like milk, cream and whey.', art('dairy-trio'),
          [('the cheese', 'cheese', 1), ('the butter', 'cream', 1)], {}))
S.append(('Kraft', 1, 'Kraft Singles were sold as cheese food.', art('wrapped-slices'),
          [('the top slice', 'Singles', 1)], {}))
S.append(('But', 1, 'But Kraft was adding milk protein concentrate, a powder made by filtering milk down to its protein.', art('dye-tin'),
          [('the powder', 'powder', 1)], {}))
S.append(('Much', 1, 'Much of it came from overseas, and American dairy farmers wanted something done about it.', art('ship', 'cow-hay'),
          [('the ship', 'overseas', 1), ('the milk pail', 'farmers', 1)], {}))
S.append(('That', 1, "That powder wasn't in the recipe. In 2002, FDA inspectors found it in Kraft's plants, so the slices couldn't be called cheese food anymore.", art('law-book', 'rubber-stamp'),
          [('the open page', 'recipe', 1), ('the stamp', 'inspectors', 1)], {}))
S.append(('Kraft', 1, 'Kraft didn\'t take the powder out. It changed the name instead, to "cheese product." That name has no recipe at all.', art('label-pen'),
          [('the label', 'name', 1)], {}))
S.append(('So', 1, 'So Kraft kept the powder, and dropped the word "food."', art('wrapped-slices'),
          [('the wrapper flap', 'food', 1)], {}))
S.append(('why', 1, 'And why do we say "trick or treat"? That\'s another story.', art('candy-bucket'),
          [('the candy', 'treat', 1)], {'beat_note': 'The tease: Short 10 is trick or treat.'}))

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
    'story': '09-cheese-product',
    'question': 'Why do some cheese slices say "cheese product"?',
    'audio': 'voice.mp3', 'words': 'words.json', 'duration': dur,
    'notes': ('Narration v2. Times are seconds into voice.mp3, computed from words.json by shots.py. '
              'Each scene is one stop on the vertical paper strip. "paint" lists where the paint lands '
              'and the word it lands on.'),
    'scenes': [{k: s[k] for k in ('id', 'start', 'end', 'line', 'art', 'paint', 'beat_note') if k in s} for s in scenes],
}
with open(os.path.join(HERE, 'shots.json'), 'w') as fh:
    json.dump(out, fh, indent=2)
for s in scenes:
    print(f"{s['id']:>2} {s['start']:6.2f}-{s['end']:6.2f}  " + ', '.join(f"{p['word']}@{p['t']}" for p in s['paint']))
