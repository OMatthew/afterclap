#!/usr/bin/env python3
"""Short 16 shot list: writes shots.json with every time taken from words.json.

Scene starts and paint times are keyed by word (and which occurrence of it), never typed by hand.
Loop test (Matthew, 2026-10-28): it opens and ends on the same two TVs, so Shorts' loop lands back
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
    'two-tvs': 'Two old TV sets side by side, each showing a map of the US',
    'remote-tv': 'A hand pointing a remote at an old TV showing a US map',
    'nbc-map': 'A big US map of states with light bulbs; a man in a suit points at it, seen from behind',
    'big-ben': 'Big Ben',
    'three-tvs': 'Three old TV sets in a row, each showing a US map',
    'donkey-elephant': 'A donkey and an elephant standing together',
    'us-map': 'A plain US map with state lines',
    'calendar': 'A desk calendar with pages flying off',
    'courthouse': 'A courthouse with columns and steps',
    'night-tv': 'A TV showing a US map, an empty armchair and a floor lamp at night',
    'newspaper-map': 'A folded newspaper with a US map on the front, a pencil beside it',
    'two-talking': 'Two men chatting over a railing, plants behind',
}
art = lambda *ids: [{'id': i, 'desc': A[i]} for i in ids]

S = []
S.append(('Why', 1, 'Why are Republican states red, and Democratic states blue?', art('two-tvs'),
          [('the left TV map', 'red', 1), ('the right TV map', 'blue', 1)]))
S.append(('Once', 1, 'Once, it depended on which channel you watched.', art('remote-tv'),
          [('the remote', 'channel', 1)]))
S.append(('In', 1, 'In 1976, NBC built a giant lit-up map. Republicans were blue and Democrats were red,', art('nbc-map'),
          [('a light bulb (yellow)', 'lit-up', 1), ('a state (blue)', 'blue', 1), ('Texas (red)', 'red', 1)]))
S.append(('copied', 1, 'copied from Britain, where the conservatives are blue.', art('big-ben'),
          [('the clock face (blue)', 'conservatives', 1)]))
S.append(('Other', 1, 'Other networks picked their own colors.', art('three-tvs'),
          [('the first TV map (blue)', 'picked', 1), ('the third TV map (red)', 'colors', 1)]))
S.append(('Flip', 1, 'Flip channels on election night, and the same state could change color.', art('remote-tv'),
          [('the TV map (red, turns blue on "change")', 'election', 1)]))
S.append(('Gradually', 1, 'Gradually, the networks settled on red for Republicans and blue for Democrats.', art('donkey-elephant'),
          [('the elephant (red)', 'red', 1), ('the donkey (blue)', 'blue', 1)]))
S.append(('Then', 1, 'Then came the 2000 election, Bush against Gore.', art('us-map'),
          [('Texas (red)', 'Bush', 1), ('California (blue)', 'Gore', 1)]))
S.append(('The', 2, 'The result stayed undecided for five weeks', art('calendar'),
          [('a flying page', 'five', 1)]))
S.append(('of', 1, 'of recounts and court cases.', art('courthouse'), []))   # no paint: a red courthouse would take a side
S.append(('Night', 1, 'Night after night, the same red-and-blue map stayed on TV.', art('night-tv'),
          [('the west of the TV map (red)', 'red-and-blue', 1), ('the east (blue)', 'map', 1)]))
S.append(('That', 1, 'That year, the New York Times ran a color election map too. One of its graphics editors picked red for Republicans for a simple reason: both start with R.', art('newspaper-map'),
          [('the newspaper map (red)', 'map', 1), ('the pencil (red)', 'red', 1), ('the R (red)', 'R', 1)]))
S.append(('Within', 1, 'Within a few years, "red state" and "blue state" were everyday words.', art('two-talking'),
          [('the left plant (red)', 'red', 1), ('the right plant (blue)', 'blue', 1)]))
S.append(('Neither', 1, 'Neither party ever made these colors official.', art('donkey-elephant'),
          [('the elephant (red)', 'party', 1), ('the donkey (blue)', 'colors', 1)]))
S.append(('They', 1, 'They came from TV maps, and weeks of coverage likely made them stick.', art('two-tvs'),
          [('the left TV map (red)', 'maps', 1), ('the right TV map (blue)', 'coverage', 1)]))

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
    'story': '16-red-blue',
    'question': 'Why are Republican states red, and Democratic states blue?',
    'audio': 'voice.mp3', 'words': 'words.json', 'duration': dur,
    'notes': ('Narration v7. Times are seconds into voice.mp3, computed from words.json by shots.py. '
              'Each scene is one stop on the vertical paper strip. "paint" lists where the paint lands '
              'and the word it lands on. Red and blue paint stand for the parties only where the narration says so.'),
    'scenes': [{k: s[k] for k in ('id', 'start', 'end', 'line', 'art', 'paint') if k in s} for s in scenes],
}
with open(os.path.join(HERE, 'shots.json'), 'w') as fh:
    json.dump(out, fh, indent=2)
for s in scenes:
    print(f"{s['id']:>2} {s['start']:6.2f}-{s['end']:6.2f}  " + ', '.join(f"{p['word']}@{p['t']}" for p in s['paint']))
