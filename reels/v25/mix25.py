"""Audio for reel 25: VO + quiet constant music bed (Mixkit 623, RMS window) + ocean + SFX, two-pass loudnorm -14 LUFS."""
import json, sys, subprocess as sp, numpy as np
D = '/home/claude/work/series/reels/guess25'; SR = 48000
V = sys.argv[1] if len(sys.argv) > 1 else 'E'
TL = json.load(open(D + '/tl.json')); T = TL['total']; N = int(T * SR)
def load(fn, mono=False):
    a = sp.run(['ffmpeg', '-v', 'error', '-i', fn, '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True).stdout
    return np.frombuffer(a, np.float32).reshape(-1, 2).copy()
def rms(x): return float(np.sqrt(np.mean(x ** 2)) + 1e-9)
def db(g): return 10 ** (g / 20)
def put(buf, x, t, g=0.0):
    i = int(t * SR); n = min(len(x), len(buf) - i)
    if n > 0: buf[i:i + n] += x[:n] * db(g)
vo = load(f'{D}/vo_{V}.wav')[:N]; vo = np.pad(vo, ((0, N - len(vo)), (0, 0)))
act = np.abs(vo).mean(1) > 0.01; vr = rms(vo[act])
mus = load(f'{D}/aud/music.mp3')[:N]; mus = np.pad(mus, ((0, N - len(mus)), (0, 0)))
mus *= vr / rms(mus) * db(-21)                       # constant bed 21 dB under the voice, no ducking pumps
tt = np.arange(N) / SR
mus *= np.clip(tt / 0.25, 0, 1)[:, None] * np.clip((T - tt) / 0.5, 0.15, 1)[:, None]
fz = TL['flash'][0]
mus *= (1 - 0.75 * np.exp(-((tt - (fz + 0.35)) / 0.35) ** 2))[:, None]   # music drops out on the freeze
oc = load(f'{D}/aud/x1195.mp3'); oc = np.tile(oc, (N // len(oc) + 1, 1))[:N]; oc *= vr / rms(oc) * db(-27)
fx = np.zeros((N, 2), np.float32)
def sfx(i, t, g):
    x = load(f'{D}/aud/x{i}.mp3'); x *= vr / max(rms(x[np.abs(x).mean(1) > 1e-3]), 1e-6); put(fx, x, t, g)
sfx(2568, 0.02, -16); sfx(2568, TL['badges']['b2']['on'], -16)
B2 = sum(s['dur'] for s in TL['segs'][:3]); sfx(2626, B2 - 0.05, -17)      # rewind
C0 = sum(s['dur'] for s in TL['segs'][:6]); sfx(3120, C0 - 0.15, -18)
sfx(1143, fz, -12); sfx(3005, TL['end_on'], -19)
mix = vo + mus + oc + fx
sp.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-', f'{D}/mix_raw.wav'], input=mix.astype(np.float32).tobytes(), check=True)
m = sp.run(['ffmpeg', '-hide_banner', '-i', f'{D}/mix_raw.wav', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=9:print_format=json', '-f', 'null', '-'], capture_output=True, text=True).stderr
J = json.loads(m[m.rindex('{'):])
ln = f"loudnorm=I=-14:TP=-1.5:LRA=9:measured_I={J['input_i']}:measured_TP={J['input_tp']}:measured_LRA={J['input_lra']}:measured_thresh={J['input_thresh']}:offset={J['target_offset']}:linear=true"
sp.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{D}/mix_raw.wav', '-af', ln + ',aresample=48000', '-c:a', 'pcm_s16le', f'{D}/mix_{V}.wav'], check=True)
# report: voice vs music level per line, loudness
print('music under voice dB', round(20 * np.log10(rms(mus[act]) / vr), 1), 'ocean', round(20 * np.log10(rms(oc[act]) / vr), 1))
r = sp.run(['ffmpeg', '-hide_banner', '-i', f'{D}/mix_{V}.wav', '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
print([l.strip() for l in r.splitlines() if l.strip().startswith(('I:', 'Peak:', 'LRA:'))][-3:])
