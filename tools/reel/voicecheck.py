"""21.10: voice QA. Whisper re-recognizes each line of vo.wav; prints words/sec and a match score per line.
usage: python3 voicecheck.py <workdir>"""
import json, sys, re, subprocess as sp, numpy as np, difflib
W = sys.argv[1]; S = json.load(open(f'{W}/spec.json')); TL = json.load(open(f'{W}/tl.json')); HE = S['lang'] == 'he'
from faster_whisper import WhisperModel
m = WhisperModel('ivrit-ai/whisper-large-v3-turbo-ct2' if HE else 'small.en', device='cpu', compute_type='int8', cpu_threads=4)
a = np.frombuffer(sp.run(['ffmpeg', '-v', 'error', '-i', f'{W}/vo_raw.wav', '-ac', '1', '-ar', '16000', '-f', 'f32le', '-'], capture_output=True).stdout, np.float32)
norm = (lambda s: re.sub('[^א-ת0-9 ]', '', s).split()) if HE else (lambda s: re.sub("[^a-z0-9' ]", '', s.lower()).split())
bad = 0; tw = 0; td = 0
for l in TL['L']:
    s0, s1 = l['t0'] - 0.05, l['t0'] + l['d'] + 0.05
    seg = a[int(max(0, s0) * 16000):int(s1 * 16000)]
    txt = ' '.join(x.text for x in m.transcribe(seg, language='he' if HE else 'en', beam_size=5)[0])
    ref, hyp = norm(l['txt']), norm(txt); r = difflib.SequenceMatcher(None, ref, hyp).ratio()
    wps = len(ref) / max(0.1, l['d']); tw += len(ref); td += l['d']
    flag = 'OK' if r >= 0.85 else 'CHECK'; bad += flag != 'OK'
    print(f"{l['k']} {flag} match={r:.2f} wps={wps:.2f} dur={l['d']:.2f} | ref: {l['txt']} | asr: {txt.strip()}")
print(f"TOTAL wps={tw / td:.2f} lines_to_check={bad}")
