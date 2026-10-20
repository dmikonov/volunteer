"""Kokoro TTS per line with word timings. Runs under Python 3.12 (uv). usage: kokoro_tts.py <workdir> <voice> <speed>
writes <workdir>/L{i}.wav and <workdir>/kokoro.json [{k, txt, fn, words:[[w,start,end],...]}]"""
import sys, json, numpy as np, soundfile as sf
from kokoro import KPipeline
W, V, SP = sys.argv[1], sys.argv[2], float(sys.argv[3])
S = json.load(open(f'{W}/spec.json')); p = KPipeline(lang_code='a' if not V.startswith('b') else 'b', repo_id='hexgrad/Kokoro-82M')
out = []
for i, t in enumerate(S['lines'], 1):
    aud, words, off = [], [], 0.0
    for r in p(t, voice=V, speed=SP):
        a = np.asarray(r.audio, dtype=np.float32); aud.append(a)
        toks = [x for x in (r.tokens or []) if x.text.strip() and any(ch.isalnum() for ch in x.text)]
        if toks and all(x.start_ts is not None and x.end_ts is not None for x in toks):
            words += [[x.text, off + x.start_ts, off + x.end_ts] for x in toks]
        else:  # proportional fallback
            ws = r.graphemes.split(); L = len(a) / 24000; n = sum(len(w) for w in ws) or 1; c = 0
            for w in ws: words.append([w, off + L * c / n, off + L * (c + len(w)) / n]); c += len(w)
        off += len(a) / 24000
    fn = f'{W}/L{i}.wav'; sf.write(fn, np.concatenate(aud), 24000)
    out.append({'k': f'L{i}', 'txt': t, 'fn': fn, 'words': words})
json.dump(out, open(f'{W}/kokoro.json', 'w'), ensure_ascii=False)
print('kokoro ok', V, [(o['k'], round(o['words'][-1][2], 2)) for o in out])
