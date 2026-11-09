#!/usr/bin/env python3
"""Short 17 shot list: writes shots.json with every time taken from words.json.

Scene starts and paint times are keyed by word (and which occurrence of it), never typed by hand.
Loop: it opens and ends on the same calendar, so Shorts' loop lands back
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
    'calendar-turkey': 'A November wall calendar (a plain grid, 7 columns x 5 rows) above a roast turkey on a platter',
    'lincoln-quill': 'Abraham Lincoln, from the side, writing with a quill',
    'shop-window': 'A 1930s shop window with toys and gifts; a worried shopkeeper beside it',
    'store-doors': 'Shoppers in 1930s coats waiting at closed store doors with a wreath',
    'empty-wallet': 'An open, nearly empty wallet and two coins',
    'fdr-mic': 'Franklin Roosevelt, from the side, at an old radio microphone',
    'us-map': 'A plain US map with state lines',
    'texas-two': 'An outline of Texas with two little roast turkeys in it',
    'grumpy-man': 'A frowning man in a 1930s hat pointing at a wall calendar',
    'two-houses': 'Two small houses with a signpost between them',
    'cash-register': 'An old brass cash register',
    'capitol': 'The U.S. Capitol dome',
    'turkey-platter': 'A roast turkey on a platter',
}
art = lambda *ids: [{'id': i, 'desc': A[i]} for i in ids]

S = []
S.append(('Why', 1, 'Why is Thanksgiving on the fourth Thursday of November? It used to be the last Thursday.', art('calendar-turkey'),
          [('the fourth Thursday square', 'fourth', 1), ('the last Thursday square', 'last', 1)]))
S.append(('Abraham', 1, 'Abraham Lincoln picked it, and later presidents usually kept it.', art('lincoln-quill'),
          [('the paper he writes on', 'picked', 1)]))
S.append(('Then', 1, 'Then came 1939. That November had five Thursdays, so Thanksgiving would land on the very last day of the month.', art('calendar-turkey'),
          [('the fifth Thursday square', 'five', 1), ('the last square (swells)', 'last', 1)]))
S.append(('Store', 1, 'Store owners were worried.', art('shop-window'), [('a gift box in the window', 'worried', 1)]))
S.append(('Back', 1, 'Back then, most people waited until after Thanksgiving to start their Christmas shopping.', art('store-doors'),
          [('the wreath', 'Christmas', 1)]))
S.append(('A', 1, 'A late Thanksgiving meant a short shopping season, in the middle of the Great Depression.', art('empty-wallet'),
          [('the wallet', 'short', 1)]))
S.append(('So', 1, 'So they asked President Franklin Roosevelt to move Thanksgiving up a week. He did.', art('fdr-mic'),
          [('the microphone', 'move', 1)]))
S.append(('The', 1, 'The country split. Some states followed him. Others kept the old date.', art('us-map'),
          [('a state', 'followed', 1), ('another state', 'Others', 1)]))
S.append(('Texas', 1, 'Texas took both days off.', art('texas-two'), [('the Texas panhandle', 'both', 1)]))
S.append(('Critics', 1, 'Critics called Roosevelt\'s early holiday "Franksgiving."', art('grumpy-man'),
          [('the calendar he points at', 'Franksgiving', 1)]))
S.append(('Families', 1, 'Families in neighboring states sat down to turkey a week apart.', art('two-houses'),
          [('the signpost', 'neighboring', 1), ('the second chimney', 'apart', 1)]))
S.append(('Did', 1, "Did the extra week help the stores? Roosevelt later admitted it didn't work. Most stores said it made little difference.", art('cash-register'),
          [('the cash drawer', 'stores', 1), ('the keys', 'difference', 1)]))
S.append(('In', 1, 'In 1941, Congress made it law: Thanksgiving is the fourth Thursday of November.', art('capitol'),
          [('the dome', 'law', 1)]))
S.append(('Most', 1, 'Most years, the fourth Thursday is also the last. But some Novembers have five.', art('calendar-turkey'),
          [('the fourth Thursday square', 'fourth', 1), ('the fifth Thursday square', 'some', 1)]))   # lands on "some Novembers": the loop fade starts 0.9 s before the end

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
    'story': '17-thanksgiving',
    'question': 'Why is Thanksgiving on the fourth Thursday of November?',
    'audio': 'voice.mp3', 'words': 'words.json', 'duration': dur,
    'notes': ('Narration v3. Times are seconds into voice.mp3, computed from words.json by shots.py. '
              'Each scene is one stop on the vertical paper strip. "paint" lists where the paint lands '
              'and the word it lands on.'),
    'scenes': [{k: s[k] for k in ('id', 'start', 'end', 'line', 'art', 'paint') if k in s} for s in scenes],
}
with open(os.path.join(HERE, 'shots.json'), 'w') as fh:
    json.dump(out, fh, indent=2)
for s in scenes:
    print(f"{s['id']:>2} {s['start']:6.2f}-{s['end']:6.2f}  " + ', '.join(f"{p['word']}@{p['t']}" for p in s['paint']))
