"""22.10: per-line prosody report of a built voice track (Dima: Hebrew intonation must sound Israeli).
usage: python3 prosody_report.py <out/ci/<reel> dir>   (needs vo.wav + tl.json there; pip install praat-parselmouth librosa)
Checks per line: final contour (fall / level / rise) against what Hebrew expects (statements, imperatives and wh-questions fall,
yes/no questions rise), pitch level vs the other lines (even = within 3 st), pitch range (6-15 st)."""
import json, sys, numpy as np, librosa, parselmouth
D = sys.argv[1]; TL = json.load(open(f'{D}/tl.json')); y, sr = librosa.load(f'{D}/vo.wav', sr=16000)
WH = ('למה', 'איך', 'מה', 'מי', 'איפה', 'מתי', 'כמה', 'לאן', 'איזה', 'איזו', 'why', 'how', 'what', 'who', 'where', 'when')
snd = parselmouth.Sound(y.astype(np.float64), sr); pt = snd.to_pitch(time_step=0.01, pitch_floor=70, pitch_ceiling=420)
f0 = pt.selected_array['frequency']; t = pt.xs(); st = lambda hz: 12 * np.log2(hz / 100.0)
rows = []
for l in TL['L']:
    a, b = l['t0'], l['t0'] + l['d']; m = (t >= a) & (t <= b) & (f0 > 0); ff, tt = f0[m], t[m]
    if len(ff) < 10: rows.append((l['k'], l['txt'], None)); continue
    s = st(ff); end = tt[-1]; last = s[tt > end - 0.15]; prev = s[(tt > end - 0.50) & (tt <= end - 0.15)]
    mv = float(last.mean() - prev.mean()) if len(last) > 2 and len(prev) > 2 else 0.0
    fin = 'fall' if mv < -1.5 else ('rise' if mv > 1.5 else 'level')
    txt = l['txt'].strip(); w0 = txt.split()[0].strip('?,.').lower()
    exp = 'rise' if txt.endswith('?') and w0 not in WH else 'fall'
    rows.append((l['k'], txt, dict(med=float(np.median(s)), rng=float(np.percentile(s, 90) - np.percentile(s, 10)), mv=mv, fin=fin, exp=exp)))
G = float(np.median([r[2]['med'] for r in rows if r[2]]))
bad = 0
for k, txt, r in rows:
    if not r: print(k, 'NO PITCH', txt); bad += 1; continue
    ok_f = r['fin'] == r['exp'] or (r['exp'] == 'fall' and r['fin'] == 'level'); ok_l = abs(r['med'] - G) <= 3; ok_r = 6 <= r['rng'] <= 15
    flag = 'OK ' if ok_f and ok_l and ok_r else 'BAD'; bad += flag == 'BAD'
    print(f"{flag} {k} final {r['fin']:5} ({r['mv']:+.1f} st, expected {r['exp']}) | level {r['med'] - G:+.1f} st | range {r['rng']:.1f} st | {txt}")
print('lines flagged:', bad, '| median pitch', f'{100 * 2 ** (G / 12):.0f} Hz')
