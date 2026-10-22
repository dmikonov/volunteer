"""21.10: Hebrew voice from F5 takes (Space dmikonov/f5-hebrew, voice 3 = FLEURS he_il 12632262789732552882).
Takes are made beforehand with the MCP tool f5_hebrew_say and listed in the spec: "f5_takes": [[line_index, url], ...]
(several per line = best of). Picks per line the take with the lowest word error (ivrit-ai whisper), ties -> closest
to the median duration of that line's takes. Writes the same files as voice.py: L<i>.wav, vo_raw.wav, vo.wav, tl.json.
usage: python3 voice_f5.py <workdir>"""
import json, re, sys, os, subprocess as sp
import numpy as np, editdistance
W = sys.argv[1]; S = json.load(open(f'{W}/spec.json')); SR = 48000; GAP = S.get('gap', 0.2)
LINES = S['lines']; TAKES = S['f5_takes']
NUM = {'1': 'אחת', '2': 'שתיים', '3': 'שלוש', '10': 'עשר'}
def norm(s):
    out = []
    for w in s.split():
        w = re.sub('[^א-ת0-9]', '', w); w = NUM.get(w, w)
        if w: out.append(w)
    return out
def ld(f, sr=16000):
    return np.frombuffer(sp.run(['ffmpeg', '-v', 'error', '-i', f, '-ac', '1', '-ar', str(sr), '-f', 'f32le', '-'], capture_output=True).stdout, np.float32)
os.makedirs(f'{W}/takes', exist_ok=True)
from faster_whisper import WhisperModel
try:  # 22.10: prosody of each take (Dima: intonation must sound Israeli). Final contour + pitch level between lines.
    import parselmouth
    WH = ('למה', 'איך', 'מה', 'מי', 'איפה', 'מתי', 'כמה', 'לאן', 'איזה', 'איזו')
    def prosody(a16):
        snd = parselmouth.Sound(a16.astype(np.float64), 16000); pt = snd.to_pitch(time_step=0.01, pitch_floor=70, pitch_ceiling=420)
        f0 = pt.selected_array['frequency']; t = pt.xs(); m = f0 > 0; ff, tt = f0[m], t[m]
        if len(ff) < 10: return None
        st = 12 * np.log2(ff / 100.0); end = tt[-1]; last = st[tt > end - 0.15]; prev = st[(tt > end - 0.50) & (tt <= end - 0.15)]
        mv = float(last.mean() - prev.mean()) if len(last) > 2 and len(prev) > 2 else 0.0
        return {'med': float(np.median(st)), 'rng': float(np.percentile(st, 90) - np.percentile(st, 10)), 'mv': mv, 'fin': 'fall' if mv < -1.5 else ('rise' if mv > 1.5 else 'level')}
    def expected(txt, k):
        e = S.get('final', {}).get(k)
        if e: return e
        t = txt.strip()
        if t.endswith('?') and not t.split()[0] in WH: return 'rise'   # yes/no question: Hebrew marks it by a final rise
        return 'fall'  # statements, imperatives, wh-questions: final fall (level tolerated)
except Exception as _e:
    prosody = None; print('prosody check off:', _e)
wm = WhisperModel('ivrit-ai/whisper-large-v3-turbo-ct2', device='cpu', compute_type='int8', cpu_threads=4)
ref_txt = S.get('ref_lines', LINES)  # what the voice should say (SurfTribe spoken as סרף טרייב)
ev = {}
for n, (i, url) in enumerate(TAKES):
    f = f'{W}/takes/t{n}_L{i + 1}.wav'
    r = sp.run(['curl', '-sSfL', '--retry', '3', '-o', f, url])
    if r.returncode or os.path.getsize(f) < 2000: print('download failed', i, url[-40:]); continue
    a = ld(f); seg, _ = wm.transcribe(a, language='he', beam_size=5, word_timestamps=True)
    Wd = [(w.word.strip(), w.start, w.end) for sg in seg for w in sg.words]
    ref = norm(ref_txt[i]); hyp = norm(' '.join(w[0] for w in Wd))
    wer = editdistance.eval(ref, hyp) / max(1, len(ref))
    ev.setdefault(i, []).append({'f': f, 'wer': wer, 'w': Wd, 'dur': len(a) / 16000, 'txt': ' '.join(w[0] for w in Wd), 'pr': prosody(a) if prosody else None})
    print('take', i, n, 'wer', round(wer, 3), 'dur', round(len(a) / 16000, 2), '|', ev[i][-1]['txt'])
L = []; t = 0.12
for i, disp in enumerate(LINES):
    c = ev[i]; md = float(np.median([x['dur'] for x in c])); bw = min(x['wer'] for x in c)
    cands = [x for x in c if x['wer'] <= bw + 1e-9]
    if prosody and all(x.get('pr') for x in cands):
        if 'GMED' not in globals():
            GMED = float(np.median([x['pr']['med'] for j in ev for x in ev[j] if x.get('pr') and x['wer'] <= min(y['wer'] for y in ev[j]) + 1e-9]))
        exp = expected(ref_txt[i], f'L{i + 1}')
        def score(x):
            pr = x['pr']; ok = pr['fin'] == exp or (exp == 'fall' and pr['fin'] == 'level')
            return abs(pr['med'] - GMED) + (0 if ok else 2.5) + 0.3 * abs(x['dur'] - md) + (1.0 if pr['rng'] > 15 else 0)
        p = sorted(cands, key=score)[0]
        print('PICK', i, 'wer', round(p['wer'], 3), '| final', p['pr']['fin'], f"({p['pr']['mv']:+.1f} st, expected {exp})", '| pitch', f"{100 * 2 ** (p['pr']['med'] / 12):.0f} Hz", f"(level {p['pr']['med'] - GMED:+.1f} st)", '| range', f"{p['pr']['rng']:.1f} st |", p['txt'])
    else:
        p = sorted(cands, key=lambda x: abs(x['dur'] - md))[0]
        print('PICK', i, 'wer', round(p['wer'], 3), p['txt'])
    a = ld(p['f'], SR); env = np.sqrt(np.convolve(a ** 2, np.ones(480) / 480, 'same')); idx = np.where(env > 0.02 * np.abs(a).max())[0]
    s0 = max(0.0, idx[0] / SR - 0.04); e0 = min(len(a) / SR, idx[-1] / SR + 0.10)
    fn = f'{W}/L{i + 1}.wav'
    sp.run(['ffmpeg', '-v', 'error', '-y', '-i', p['f'], '-ar', str(SR), '-ac', '1', fn], check=True)
    toks = disp.split(); ww = [x for x in p['w'] if x[0]]
    if len(ww) == len(toks): tim = [(x[1], x[2]) for x in ww]
    else:  # spread display tokens over the spoken span by character length
        a0 = ww[0][1] if ww else s0; a1 = ww[-1][2] if ww else e0; ln = np.cumsum([0] + [len(x) for x in toks]); tot = ln[-1]
        tim = [(a0 + (a1 - a0) * ln[k] / tot, a0 + (a1 - a0) * ln[k + 1] / tot) for k in range(len(toks))]
    words = [[tok, round(t + max(0, b0 - s0), 3), round(t + min(e0, b1) - s0, 3)] for tok, (b0, b1) in zip(toks, tim)]
    L.append({'k': f'L{i + 1}', 'txt': disp, 'fn': fn, 'words': words, 's0': s0, 'e0': e0, 't0': round(t, 3), 'd': e0 - s0, 'wer': p['wer'], 'asr': p['txt']})
    t += (e0 - s0) + GAP + S.get('gap_after', {}).get(f'L{i + 1}', 0)  # 21.10: silent hold after a line (recap frame)
T = round(L[-1]['t0'] + L[-1]['d'] + 0.9, 3)
inputs, fc, seq, cur = [], [], [], 0.0
for i, l in enumerate(L):
    sil = l['t0'] - cur
    if sil > 0.001: fc.append(f'aevalsrc=0:d={sil:.3f}:s={SR}:c=mono[s{i}]'); seq.append(f'[s{i}]')
    inputs += ['-i', l['fn']]; fc.append(f"[{len(inputs) // 2 - 1}:a]atrim=start={l['s0']:.3f}:end={l['e0']:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.01,afade=t=out:st={max(0, l['d'] - 0.03):.3f}:d=0.03,aformat=channel_layouts=mono[a{i}]"); seq.append(f'[a{i}]')
    cur = l['t0'] + l['d']
fc.append(f"{''.join(seq)}concat=n={len(seq)}:v=0:a=1,apad=whole_dur={T}[vo]")
sp.run(['ffmpeg', '-v', 'error', '-y'] + inputs + ['-filter_complex', ';'.join(fc), '-map', '[vo]', '-t', str(T), f'{W}/vo_raw.wav'], check=True)
r = sp.run(['ffmpeg', '-hide_banner', '-i', f'{W}/vo_raw.wav', '-af', 'loudnorm=I=-15:TP=-2:LRA=9:print_format=json', '-f', 'null', '-'], capture_output=True, text=True).stderr
m = json.loads(r[r.rindex('{'):r.rindex('}') + 1])
ln = f"loudnorm=I=-15:TP=-2:LRA=9:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true"
sp.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{W}/vo_raw.wav', '-af', ln, '-ar', '48000', '-ac', '2', f'{W}/vo.wav'], check=True)
json.dump({'T': T, 'L': L}, open(f'{W}/tl.json', 'w'), ensure_ascii=False)
print('he f5 T', T, [(l['k'], l['t0'], round(l['d'], 2), round(l['wer'], 2)) for l in L])
