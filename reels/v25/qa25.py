"""Numeric QA for reel 25 (checklist items 5, 6, 19, 20, 24, 38, 39)."""
import json, subprocess as sp, numpy as np, cv2, sys
D = '/home/claude/work/series/reels/guess25'; V = sys.argv[1] if len(sys.argv) > 1 else 'E'
TL = json.load(open(D + '/tl.json')); B = json.load(open(D + '/ov/boxes.json'))
def ink(name):
    a = cv2.imread(f'{D}/ov/{name}.png', cv2.IMREAD_UNCHANGED)[..., 3]; ys, xs = np.where(a > 40); return xs.min(), ys.min(), xs.max(), ys.max()
print('== subtitles (pill+text ink bbox, placed at y 1330)')
for k, t0, t1 in TL['subs']:
    x0, y0, x1, y1 = ink('sub_' + k); print(f'  {k}: x {x0}-{x1} centre {(x0 + x1) / 2:.0f} margins L{x0} R{1080 - x1} diff {abs(x0 - (1080 - x1))}  y {1330 + y0}-{1330 + y1}  {t0}-{t1}s')
for n, y in (('hook', 290), ('mark', 232), ('end', 520)):
    x0, y0, x1, y1 = ink(n); print(f'  {n}: x {x0}-{x1} y {y + y0}-{y + y1}')
print('== voice gaps (vo track, -40 dB, >0.12 s)')
r = sp.run(['ffmpeg', '-i', f'{D}/vo_{V}.wav', '-af', 'silencedetect=n=-40dB:d=0.12', '-f', 'null', '-'], capture_output=True, text=True).stderr
st = [float(l.split('silence_start: ')[1]) for l in r.splitlines() if 'silence_start' in l]
en = [float(l.split('silence_end: ')[1].split()[0]) for l in r.splitlines() if 'silence_end' in l]
gaps = [(round(a, 2), round(b, 2), round(b - a, 2)) for a, b in zip(st, en)]
print('  ', gaps); inner = [g for g in gaps if g[0] > 0.2 and g[1] < TL['total'] - 0.05]
print('   longest inner gap', max(g[2] for g in inner), '| tail after last word', round(TL['total'] - st[-1], 2) if st[-1] > en[-1] - 1 else 'n/a')
print('== loop SSIM last vs first frame')
cap = cv2.VideoCapture(f'{D}/v25_silent.mp4'); n = int(cap.get(7)); ok, f0 = cap.read(); cap.set(1, n - 1); ok, fl = cap.read()
from skimage.metrics import structural_similarity as ssim
g0 = cv2.cvtColor(f0, cv2.COLOR_BGR2GRAY); g1 = cv2.cvtColor(fl, cv2.COLOR_BGR2GRAY)
print('   frames', n, 'SSIM full', round(ssim(g0, g1), 3), 'background (rows 1450-1920)', round(ssim(g0[1450:], g1[1450:]), 3))
