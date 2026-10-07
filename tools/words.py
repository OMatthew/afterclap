#!/usr/bin/env python3
"""Word timings for a story: voice.mp3 -> words.json ([{w, s, e}], seconds into voice.mp3).

faster-whisper small.en on CPU (int8, beam 5, word timestamps), as in Short 01. The audio is
decoded with ffmpeg to 16 kHz mono first (the bundled decoder failed on these files).
The transcript is then lined up with narration.txt:
  - a word Whisper heard differently keeps its times and takes the script's spelling
  - a script word Whisper skipped is reported, with the gap it falls in; time it from the
    waveform (ffmpeg silencedetect) and add it by hand
The match printed is Whisper's own transcript against the script, before any renaming
(expect 1.000, or know why not).

Usage: python3 tools/words.py stories/02-ridges [voice.mp3] [--model small.en]
"""
import difflib, json, os, re, subprocess, sys


def norm(t):
    t = t.lower().replace('’', "'")
    return re.sub(r"[^a-z0-9']", '', t)


def script_tokens(path):
    txt = open(path).read()
    txt = re.sub(r'\[\[[^\]]*\]\]', ' ', txt)
    toks = []
    for raw in txt.split():
        clean = raw.strip('.,!?;:"()“”‘').replace('’', "'")
        if norm(clean):
            toks.append(clean)
    return toks


def transcribe(audio, model_name):
    import numpy as np
    from faster_whisper import WhisperModel
    # decode with ffmpeg straight to 16 kHz mono float samples (faster-whisper's own av decoder fails here)
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', audio, '-ac', '1', '-ar', '16000', '-f', 'f32le', '-'],
                         check=True, stdout=subprocess.PIPE).stdout
    samples = np.frombuffer(raw, dtype=np.float32)
    model = WhisperModel(model_name, device='cpu', compute_type='int8')
    segs, _ = model.transcribe(samples, beam_size=5, word_timestamps=True, language='en', vad_filter=False)
    out = []
    for sg in segs:
        for w in sg.words:
            for part in w.word.strip().split():
                out.append({'w': part.strip('.,!?;:"'), 's': round(w.start, 2), 'e': round(w.end, 2)})
    return [w for w in out if norm(w['w'])]


def main():
    args = sys.argv[1:]
    model = 'small.en'
    if '--model' in args:
        i = args.index('--model'); model = args[i + 1]; del args[i:i + 2]
    story = args[0]
    audio = args[1] if len(args) > 1 else os.path.join(story, 'voice.mp3')
    script = script_tokens(os.path.join(story, 'narration.txt'))
    heard = transcribe(audio, model)
    a, b = [norm(w['w']) for w in heard], [norm(t) for t in script]
    sm = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
    print(f'whisper vs script: {sm.ratio():.3f} ({len(heard)} heard, {len(script)} in script)')
    words, issues = [], []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == 'equal':
            for i, j in zip(range(i1, i2), range(j1, j2)):
                words.append(dict(heard[i], w=script[j]))
        elif op == 'replace' and i2 - i1 == j2 - j1:
            for i, j in zip(range(i1, i2), range(j1, j2)):
                issues.append(f'heard "{heard[i]["w"]}" for "{script[j]}" @{heard[i]["s"]}')
                words.append(dict(heard[i], w=script[j]))
        elif op == 'replace':
            # merged or split words ("1690s" vs "sixteen nineties"): spread the script words over the span
            s, e = heard[i1]['s'], heard[i2 - 1]['e']
            n = j2 - j1
            issues.append(f'heard "{" ".join(w["w"] for w in heard[i1:i2])}" for "{" ".join(script[j1:j2])}" @{s}: times spread evenly')
            for k, j in enumerate(range(j1, j2)):
                words.append({'w': script[j], 's': round(s + (e - s) * k / n, 2), 'e': round(s + (e - s) * (k + 1) / n, 2)})
        elif op == 'delete':
            issues.append(f'extra word(s) heard, dropped: "{" ".join(w["w"] for w in heard[i1:i2])}" @{heard[i1]["s"]}')
        elif op == 'insert':
            prev = words[-1]['e'] if words else 0.0
            nxt = heard[i1]['s'] if i1 < len(heard) else None
            issues.append(f'MISSING "{" ".join(script[j1:j2])}" between {prev} and {nxt}: time from the waveform')
    for m in issues:
        print(' -', m)
    out = os.path.join(story, 'words.json')
    with open(out, 'w') as fh:
        json.dump(words, fh, indent=0)
    print(f'wrote {out}: {len(words)} words, last ends {words[-1]["e"]} s')


if __name__ == '__main__':
    main()
