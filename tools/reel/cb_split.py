"""22.10: cut Chatterbox chunk takes (cb_takes.py) into per-line files by ivrit-ai whisper word alignment, write
<spec>.takes.json for voice_f5.py ([[line_index, file://...], ...]). usage: python3 cb_split.py <spec.json> <name>"""
import json, os, re, sys, subprocess as sp
import numpy as np, editdistance, librosa
from faster_whisper import WhisperModel
SP, NAME = sys.argv[1], sys.argv[2]; S = json.load(open(SP)); LINES = S.get('ref_lines', S['lines'])
O = f'/s17/takes/{NAME}'; CH = json.load(open(f'{O}/chunks.json'))
NUM = {'1': 'אחת', '2': 'שתיים', '3': 'שלוש', '10': 'עשר'}
def norm(w): w = re.sub('[^א-ת0-9]', '', w); return NUM.get(w, w)
wm = WhisperModel('ivrit-ai/whisper-large-v3-turbo-ct2', device='cpu', compute_type='int8', cpu_threads=4)
def sim(a, b): return 1 - editdistance.eval(a, b) / max(1, len(a), len(b))
def align(ref, hyp):  # DP alignment of token lists, returns {ref_i: hyp_j} for matched/substituted pairs
    n, m = len(ref), len(hyp); D = np.zeros((n + 1, m + 1)); D[:, 0] = np.arange(n + 1); D[0, :] = np.arange(m + 1); B = np.zeros((n + 1, m + 1), dtype=int)
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            c = [D[i - 1, j - 1] + (1 - sim(ref[i - 1], hyp[j - 1])) * 1.2, D[i - 1, j] + 1, D[i, j - 1] + 1]
            k = int(np.argmin(c)); D[i, j] = c[k]; B[i, j] = k
    i, j, pairs = n, m, {}
    while i > 0 and j > 0:
        if B[i, j] == 0:
            if sim(ref[i - 1], hyp[j - 1]) >= 0.34: pairs[i - 1] = j - 1
            i, j = i - 1, j - 1
        elif B[i, j] == 1: i -= 1
        else: j -= 1
    return pairs
takes = []
for tk in CH:
    y, sr = librosa.load(tk['file'], sr=16000); seg, _ = wm.transcribe(y, language='he', beam_size=5, word_timestamps=True)
    W = [(w.word.strip(), w.start, w.end) for sg in seg for w in sg.words if norm(w.word.strip())]
    hyp = [norm(w[0]) for w in W]; ref, owner = [], []
    for i in tk['lines']:
        for w in LINES[i].split():
            if norm(w): ref.append(norm(w)); owner.append(i)
    P = align(ref, hyp); print(f"C{tk['chunk']} t{tk['take']} {tk['dur']}s | asr: {' '.join(w[0] for w in W)}")
    # per line: first and last aligned hyp word
    spans = {}
    for r, i in enumerate(owner):
        if r in P: spans.setdefault(i, [P[r], P[r]]); spans[i][1] = P[r]
    rms = librosa.feature.rms(y=y, frame_length=400, hop_length=80)[0]; hop = 80 / sr
    def quiet(t0, t1):  # time of minimum energy between t0 and t1
        a, b = int(t0 / hop), max(int(t0 / hop) + 1, int(t1 / hop)); k = a + int(np.argmin(rms[a:b])); return k * hop
    lines = [i for i in tk['lines'] if i in spans]; cuts = []
    for q in range(len(lines)):
        i = lines[q]; st_ = W[spans[i][0]][1]; en_ = W[spans[i][1]][2]
        a = max(0.0, st_ - 0.25) if q == 0 else cuts[-1]
        if q < len(lines) - 1:
            nxt = W[spans[lines[q + 1]][0]][1]; b = quiet(en_, nxt) if nxt - en_ > 0.08 else (en_ + nxt) / 2
        else: b = min(len(y) / sr, en_ + 0.35)
        cuts.append(b); f = f"{O}/L{i + 1}_t{tk['take']}.wav"
        sp.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{a:.3f}', '-to', f'{b:.3f}', '-i', tk['file'], '-ac', '1', f], check=True)
        takes.append([i, 'file://' + f]); print(f"  L{i + 1} {a:.2f}-{b:.2f} | {' '.join(w[0] for w in W[spans[i][0]:spans[i][1] + 1])}")
    for i in tk['lines']:
        if i not in spans: print(f"  L{i + 1} NOT ALIGNED in C{tk['chunk']} t{tk['take']}")
TF = os.path.splitext(SP)[0] + '.takes.json'; json.dump(takes, open(TF, 'w'), ensure_ascii=False); print('line takes', len(takes), '->', TF)
