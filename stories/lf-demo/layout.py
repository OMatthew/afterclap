#!/usr/bin/env python3
"""Rebuild the 23.5-second landscape demo layout from Short 18. Audio stays untouched."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / '18-macys-balloons'
shots = json.loads((SOURCE / 'shots.json').read_text())
shots.update(story='lf-demo', duration=23.5,
             notes='First four scenes of Short 18, ending at 23.5 s. Source voice and word timestamps are copied unchanged.')
shots['scenes'] = shots['scenes'][:4]
shots['scenes'][0]['chapter'] = 'The flying cat'
shots['scenes'][2]['chapter'] = 'A reward for bringing them back'
layout = json.loads((SOURCE / 'layout.json').read_text())
layout['scenes'] = layout['scenes'][:4]
style = layout['style']
style.update(frame='landscape', captions=True, loop=False)
style.pop('cap', None)
style.pop('capChars', None)
style['introTitle'].update(words=["Why did Macy's", 'let them fly?'], size=90, top=110)
for scene in layout['scenes']:
    for art in scene['art']:
        trace = json.loads((HERE / 'art/traced' / (art['id'] + '.json')).read_text())
        aspect = trace['size'][0] / trace['size'][1]
        art.update(x=1330 if scene['id'] == 1 else 960, y=490,
                   w=round(min(1000 if scene['id'] == 1 else 1440, 720 * aspect)))
layout['cover'].update(x=1340, y=540, w=940)
for name, value in [('shots.json', shots), ('layout.json', layout)]:
    (HERE / name).write_text(json.dumps(value, indent=1) + '\n')
