"""QA for v10: loop similarity, faces vs text zones, subtitle text rules, frame sheet, uploads."""
import subprocess as sp, numpy as np, re, json, os, imageio_ffmpeg, cv2
F = imageio_ffmpeg.get_ffmpeg_exe(); os.chdir('/tmp/r4'); V = 'wetsuit_v13.mp4'
info = json.load(open('info.json')); d = info['d']; st = [sum(d[:i]) for i in range(10)]
err = sp.run([F, '-i', V, '-map', '0:v', '-f', 'null', '-'], capture_output=True, text=True).stderr
n = int(re.findall(r'frame=\s*(\d+)', err)[-1])
def frame(k, gray=True):
    raw = sp.run([F, '-loglevel', 'error', '-ss', f'{max(0, k / 30 - 1):.3f}', '-i', V, '-vf', f"select='gte(n,{min(k, 30)})'", '-frames:v', '1', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(1920, 1080, 3)
a, b = frame(0), frame(n - 1)
g = lambda x: cv2.cvtColor(x, cv2.COLOR_BGR2GRAY)[760:, :].astype(float)
from skimage.metrics import structural_similarity as ssim
print('frames', n, 'LOOP_SSIM_bg', round(ssim(g(a), g(b), data_range=255), 3), 'full', round(ssim(cv2.cvtColor(a, cv2.COLOR_BGR2GRAY), cv2.cvtColor(b, cv2.COLOR_BGR2GRAY), data_range=255), 3))
# text zones per beat (y ranges of overlay text/cards + subtitle band), from measured overlay bboxes
ZONES = [[(260, 700), (1290, 1400)], [(260, 1235), (1290, 1400)], *[[(260, 760), (1290, 1400)]] * 2, [(260, 760), (790, 900)], [(260, 760), (790, 900)],
         [(260, 760), (790, 900)], [(240, 1190), (1290, 1400)], [(260, 1320), (1335, 1440)], [(260, 560), (1290, 1400)]]
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
sp.run([F, '-loglevel', 'error', '-y', '-i', V, '-vf', 'fps=2,scale=216:384,tile=10x5', '-frames:v', '1', 'review13.jpg'], check=True)
# ---- audio: LUFS / true peak of the final, voice vs music per line
ld = sp.run([F, '-hide_banner', '-i', V, '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
I = re.findall(r'I:\s+(-?[\d.]+) LUFS', ld)[-1]; TP = re.findall(r'Peak:\s+(-?[\d.]+) dBFS', ld)[-1]
print('LUFS', I, 'TRUE_PEAK', TP)
import soundfile as sf
T = info['T']; vs = info['vstart']; vo = info['vo']; ms = info['music_start']
fc = ''.join(f'[{i}:a]aresample=48000,adelay={int(vs[i]*1000)}|{int(vs[i]*1000)}[v{i}];' for i in range(10)) + ''.join(f'[v{i}]' for i in range(10)) + f'amix=inputs=10:normalize=0,apad,atrim=0:{T:.3f}[a]'
sp.run([F, '-loglevel', 'error', '-y', *sum([['-i', f'vt_{i}.wav'] for i in range(10)], []), '-filter_complex', fc, '-map', '[a]', '-ac', '1', 'voice_only.wav'], check=True)
sp.run([F, '-loglevel', 'error', '-y', '-i', 'ride.mp3', '-af', f'atrim={ms:.2f}:{ms + T:.2f},asetpts=PTS-STARTPTS,aresample=48000,volume=0.022', '-ac', '1', 'music_only.wav'], check=True)
va, sr = sf.read('voice_only.wav'); mu, _ = sf.read('music_only.wav')
db = lambda x: 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-12)
rows = []
for i in range(10):
    a0, a1 = int(vs[i] * sr), int((vs[i] + vo[i]) * sr); seg = va[a0:a1]; m = mu[a0:a1]
    w = 2048; frames = [k for k in range(0, len(seg) - w, w) if db(seg[k:k + w]) > -45]
    sv = np.concatenate([seg[k:k + w] for k in frames]) if frames else seg; sm = np.concatenate([m[k:k + w] for k in frames]) if frames else m
    rows.append(round(db(sv) - db(sm), 1))
print('VOICE_OVER_MUSIC_dB per line', rows, 'min', min(rows))
from huggingface_hub import HfApi
for f in (V, 'review13.jpg', 'subs.ass'):
    HfApi().upload_file(path_or_fileobj=f, path_in_repo=f'reels/wetsuit13/{f}', repo_id='dmikonov/surftribe-media', repo_type='dataset')
print('UPLOADED')
