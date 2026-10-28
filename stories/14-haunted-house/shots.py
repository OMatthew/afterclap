#!/usr/bin/env python3
"""Short 14 shot list: writes shots.json with every time taken from words.json.

Scene starts and paint times are keyed by word (and which occurrence of it), never typed by
hand: hand-copied times ended up a word early in Short 01.
Usage: python3 stories/14-haunted-house/shots.py
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
    'old-house': 'A crooked haunted house: loose shutter, boarded window, one lit window, bare tree, broken fence',
    'soaped-window': 'A kid on tiptoe scribbling on a shop window with a bar of soap',
    'church-manse': 'A small country church and, beside it, the minister\'s house',
    'stair-ghost': 'Two guests climbing narrow stairs side by side; a sheet ghost at the top',
    'dark-hand': 'A hand reaching in the dark toward a plate holding a round sponge',
    'grape-saucer': 'Two peeled grapes on a saucer',
    'tipped-outhouse': 'A wooden outhouse tipped over on its side',
    'wagon-roof': 'A farm wagon sitting on a barn roof (Short 10)',
    'costume-party': 'Five kids in homemade costumes at a table with a punch bowl, streamers above',
    'ticket-coins': 'An old admission ticket and two coins',
    'ticket-line': 'Four people waiting at the arched door of an old building',
    'coin-jar': 'A jar with coins and paper bills',
    'small-haunts': 'Three small houses, each with a paper ghost in the window',
    'ghost-top': 'A sheet ghost at the top of a short staircase, arms raised',
}
art = lambda *ids: [{'id': i, 'desc': A[i]} for i in ids]

S = []
S.append(('Where', 1, 'Where did haunted houses come from?', art('old-house'),
          [('the lit window', 'haunted', 1)], {}))
S.append(('The', 1, 'The usual story: in the 1930s, Halloween pranks got out of hand, so grown-ups made haunted houses to keep kids busy instead.', art('wagon-roof'),
          [('the wagon on the roof', 'pranks', 1)], {}))
S.append(('But', 1, 'But old newspapers say the idea is older.', art('old-house'),
          [('the lit window', 'older', 1)], {}))
S.append(('In', 1, 'In 1915, a church youth class in South Dakota turned their minister\'s house into "A Haunted House."', art('church-manse'),
          [('the minister\'s door', "minister's", 1)], {}))
S.append(('Guests', 1, 'Guests were sent, two at a time, up "the stairway that leads to death." At the top, a ghost pounced.', art('stair-ghost'),
          [('the ghost\'s sheet', 'pounced', 1)], {}))
S.append(('Another', 1, 'Another party plan had guests touch a pretend dead man\'s "brains" in the dark: an ice-cold sponge.', art('dark-hand'),
          [('the sponge', 'sponge', 1)], {'beat_note': 'Matthew OK\'d paint on the sponge (2026-10-27).'}))
S.append(('His', 1, 'His "eyes"? Two peeled grapes.', art('grape-saucer'),
          [('the saucer', 'grapes', 1)], {}))
S.append(('So', 1, 'So why does everyone point to the 1930s? Because the pranks were real. Kids tipped over outhouses', art('tipped-outhouse'),
          [('the outhouse', 'outhouses', 1)], {}))
S.append(('and', 1, 'and covered windows in soap.', art('soaped-window'),
          [('the soap scribble', 'soap', 1)], {}))
S.append(('Some', 1, 'Some towns threw big Halloween parties to keep them busy.', art('costume-party'),
          [('the streamers', 'parties', 1)], {}))
S.append(('Then', 1, 'Then people saw a haunted house could raise money.', art('ticket-coins'),
          [('the ticket', 'money', 1)], {}))
S.append(('In', 1, 'In the 1960s, a volunteer women\'s group in Indianapolis sold tickets to one in an old building,', art('ticket-line'),
          [('the doorway', 'tickets', 1)], {}))
S.append(('and', 1, 'and raised thousands.', art('coin-jar'),
          [('the coins', 'thousands', 1)], {}))
S.append(('Then', 1, 'Then clubs around the country started running their own, for charity.', art('small-haunts'),
          [('a door', 'clubs', 1)], {}))
S.append(('So', 1, 'So decades before that Indianapolis fundraiser, a church party was sending guests upstairs to meet a ghost.', art('ghost-top'),
          [('the ghost\'s sheet', 'ghost', 1)], {}))


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
    'story': '14-haunted-house',
    'question': 'Where did haunted houses come from?',
    'audio': 'voice.mp3', 'words': 'words.json', 'duration': dur,
    'notes': ('Narration v7. Times are seconds into voice.mp3, computed from words.json by shots.py. '
              'Each scene is one stop on the vertical paper strip. "paint" lists where the paint lands '
              'and the word it lands on.'),
    'scenes': [{k: s[k] for k in ('id', 'start', 'end', 'line', 'art', 'paint', 'beat_note') if k in s} for s in scenes],
}
with open(os.path.join(HERE, 'shots.json'), 'w') as fh:
    json.dump(out, fh, indent=2)
for s in scenes:
    print(f"{s['id']:>2} {s['start']:6.2f}-{s['end']:6.2f}  " + ', '.join(f"{p['word']}@{p['t']}" for p in s['paint']))
