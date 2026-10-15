"""QA for v10: loop similarity, faces vs text zones, subtitle text rules, frame sheet, uploads."""
import subprocess as sp, numpy as np, re, json, os, imageio_ffmpeg, cv2
F = imageio_ffmpeg.get_ffmpeg_exe(); os.chdir('/tmp/r4'); V = 'wetsuit_v10.mp4'
info = json.load(open('info.json')); d = info['d']; st = [sum(d[:i]) for i in range(10)]
err = sp.run([F, '-i', V, '-map', '0:v', '-f', 'null', '-'], capture_output=True, text=True).stderr
n = int(re.findall(r'frame=\s*(\d+)', err)[-1])
def frame(k, gray=True):
    raw = sp.run([F, '-loglevel', 'error', '-i', V, '-vf', f"select='eq(n,{k})'", '-frames:v', '1', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(1920, 1080, 3)
a, b = frame(0), frame(n - 1)
g = lambda x: cv2.cvtColor(x, cv2.COLOR_BGR2GRAY)[760:, :].astype(float)
print('frames', n, 'LOOP_SIM', round(1 - np.abs(g(a) - g(b)).mean() / 255, 3))
# text zones per beat (y ranges of overlay text/cards + subtitle band), from measured overlay bboxes
ZONES = [[(260, 700), (1290, 1400)], [(260, 1235), (1290, 1400)], *[[(260, 760), (1290, 1400)]] * 2, [(260, 760), (790, 900)], [(260, 760), (790, 900)],
         [(260, 760), (1290, 1400)], [(240, 1190), (1290, 1400)], [(260, 1320), (1335, 1440)], [(260, 560), (1290, 1400)]]
casc = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
prof = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_profileface.xml')
hits = []
for i in range(10):
    for frac in (0.2, 0.5, 0.85):
        k = int((st[i] + d[i] * frac) * 30); im = frame(k); gy = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        faces = list(casc.detectMultiScale(gy, 1.1, 6, minSize=(60, 60))) + list(prof.detectMultiScale(gy, 1.1, 6, minSize=(60, 60)))
        for (x, y, w, h) in faces:
            for z0, z1 in ZONES[i]:
                if y < z1 and y + h > z0 and x < 850:
                    hits.append((i, round(k / 30, 2), (int(x), int(y), int(w), int(h)), (z0, z1)))
print('FACE_TEXT_OVERLAPS', hits if hits else 'none')
subs = [l.split('}', 1)[1] for l in open('subs.ass') if l.startswith('Dialogue')]
badsub = [s for s in subs if re.search(r'[.!]$|[–—]', s)]
print('SUBS', len(subs), 'BAD', badsub, '|', ' / '.join(subs))
sp.run([F, '-loglevel', 'error', '-y', '-i', V, '-vf', 'fps=2,scale=216:384,tile=10x5', '-frames:v', '1', 'review10.jpg'], check=True)
from huggingface_hub import HfApi
for f in (V, 'review10.jpg', 'subs.ass'):
    HfApi().upload_file(path_or_fileobj=f, path_in_repo=f'reels/wetsuit10/{f}', repo_id='dmikonov/surftribe-media', repo_type='dataset')
print('UPLOADED')
